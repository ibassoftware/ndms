# -*- coding: utf-8 -*-


import time
import datetime
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta

import babel


from dateutil import rrule
from odoo import models, fields, api, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class Loan(models.Model):
    _name = "hr.loan"
    _description = 'Employee Loans'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True,
                                  states={'draft': [('readonly', False)]})
    date_from = fields.Date('From Date', readonly=True, states={
                            'draft': [('readonly', False)]})
    date_to = fields.Date('To Date', readonly=True, states={
                          'draft': [('readonly', False)]})
    currency_id = fields.Many2one('res.currency', default=_default_currency, string="Currency", readonly=True,
                                  states={'draft': [('readonly', False)]})
    amount_total = fields.Monetary(string="Total Loan Amount", readonly=True, states={
                                   'draft': [('readonly', False)]})
    amount_deduct = fields.Monetary(string="Deduction Amount", readonly=True, states={
                                    'draft': [('readonly', False)]})
    type = fields.Selection([('sss', 'SSS'), ('hdmf', 'HDMF'), ('other', 'OTHER')], string='Type', readonly=True,
                            states={'draft': [('readonly', False)]})
    amount_total_deducted = fields.Monetary(string="Total Deducted Amount", readonly=True,
                                            states={'draft': [('readonly', False)]})
    remarks = fields.Char(string='Remarks')
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'), ('done', 'Done')], string="Status",
                             default="draft", store=True)

    @api.one
    def _compute_state(self):
        if self.amount_total_deducted >= self.amount_total:
            self.state = 'done'

    @api.multi
    def action_open(self):
        self.write({'state': 'open'})

    @api.multi
    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state in ['open', 'done']:
                raise UserError(
                    _('Deleting of open or paid loans is not allowed.'))
        return super(Loan, self).unlink()

    @api.multi
    def name_get(self):
        result = []
        for loan in self:
            amount_str = 0.0
            if loan.currency_id.position == 'before':
                amount_str = loan.currency_id.symbol + \
                    ' ' + str(loan.amount_total)
            if loan.currency_id.position == 'after':
                amount_str = str(loan.amount_total) + ' ' + \
                    loan.currency_id.symbol
            result.append((loan.id, "[%s] %s" %
                           (amount_str, loan.employee_id.name)))
        return result


class TripTemplate(models.Model):
    _name = "ibas_hris.trip_template"
    _description = 'TRIP TEMPLATE'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    name = fields.Char('Name', compute="_compute_name", store=True)
    loc_from = fields.Char('From Location', required=True)
    loc_to = fields.Char('To Location', required=True)
    currency_id = fields.Many2one(
        'res.currency', default=_default_currency, string="Currency")
    amount = fields.Monetary(string="Amount", required=True)

    @api.depends('loc_from', 'loc_to')
    def _compute_name(self):
        self.name = (self.loc_from or '') + ' -> ' + (self.loc_to or '')


class Trip(models.Model):
    _name = "ibas_hris.trip"
    _description = 'TRIPS'

    @api.model
    def _default_currency(self):
        return self.env.user.company_id.currency_id.id

    date = fields.Date('Date', required=True)
    trip_template_id = fields.Many2one(
        'ibas_hris.trip_template', string='Template')
    loc_from = fields.Char('From Location', required=True)
    loc_to = fields.Char('To Location', required=True)
    currency_id = fields.Many2one(
        'res.currency', default=_default_currency, string="Currency")
    amount = fields.Monetary(string="Amount", required=True)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", required=True)
    remarks = fields.Char('Remarks')

    @api.multi
    def name_get(self):
        result = []
        for trip in self:
            result.append((trip.id, "[%s] %s" % (
                trip.employee_id.name, (trip.loc_from or '') + ' -> ' + (trip.loc_to or ''))))
        return result

    @api.onchange('trip_template_id')
    def _onchange_trip_template_id(self):
        if self.trip_template_id:
            self.loc_from = self.trip_template_id.loc_from
            self.loc_to = self.trip_template_id.loc_to
            self.amount = self.trip_template_id.amount


class Employee(models.Model):
    _inherit = 'hr.employee'

    loan_ids = fields.One2many('hr.loan', 'employee_id', string='Loans')
    trip_ids = fields.One2many('ibas_hris.trip', 'employee_id', string='Trips')

    @api.model
    def _current_year_avg_net_pay(self, current_payslip=None):
        date_from = datetime.date.today().strftime('%Y-01-01')
        date_to = datetime.date.today().strftime('%Y-12-31')
        payslips = self.env['hr.payslip'].search(
            [('employee_id', '=', self.id), ('date_from', '>=', date_from), ('date_from', '<=', date_to),
             ('id', '!=', current_payslip.id)])
        lines = payslips.mapped('line_ids').filtered(
            lambda r: r.code == 'NETPAY')
        return sum(lines.mapped('total'))


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    deduct_sss = fields.Boolean('Deduct SSS')
    deduct_philhealth = fields.Boolean('Deduct Philhealth')
    deduct_hdmf = fields.Boolean('Deduct HDMF')
    generate_backpay = fields.Boolean('Generate 13 th Month Pay / BackPay')

    deduct_loans = fields.Boolean('Deduct Loans')
    other_loans = fields.Boolean('Other Loans')
    project_analtc_acct_id = fields.Many2one(
        'account.analytic.account', string="Project")

    refunded = fields.Boolean('Refunded', default=False)
    deduct_tax = fields.Boolean('Deduct Withholding Tax', default=False)

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(Payslip, self).get_worked_day_lines(
            contracts, date_from, date_to)
        att_obj = self.env['hr.attendance']
        contract = self.contract_id
        employee = self.employee_id

        # Added By SDS
        if not contract:
            contract = contracts
        if not employee:
            employee = contracts.employee_id

        resource_calendar_id = employee.work_sched or contract.resource_calendar_id
        attendances = att_obj.search(
            [('employee_id', '=', contract.employee_id.id), ('check_in', '>=', date_from), ('check_in', '<=', date_to)])

        # HR-2, 3, 5, 6, 7, 8, 9, 10
        late_in_float = 0.0
        undertime_minutes = 0.0
        regular_holiday_worked_hours = 0.0
        special_holiday_worked_hours = 0.0
        restday_regular_holiday_worked_hours = 0.0
        restday_special_holiday_worked_hours = 0.0
        actual_worked_hours = 0.0
        restday_hours = 0.0

        # For Overtime
        regular_ot_minutes = 0.0
        restday_ot_minutes = 0.0
        regular_holiday_ot_minutes = 0.0
        special_holiday_ot_minutes = 0.0
        regular_holiday_restday_ot_minutes = 0.0
        special_holiday_restday_ot_minutes = 0.0
        for att in attendances:

            late_in_float += att.late_in_float
            undertime_minutes += att.undertime_minutes

            regular_holiday_worked_hours += att.reg_hol_hrs_wrk  # Regular Holiday
            special_holiday_worked_hours += att.spec_hol_hrs_wrk  # Special Holiday
            restday_hours += att.rest_day_hrs_wrk  # Restday
            # Restday Regular Holiday
            restday_regular_holiday_worked_hours += att.rd_reg_hol_hrs_wrk
            # Restday Special Holiday
            restday_special_holiday_worked_hours += att.rd_spec_hol_hrs_wrk

            # For Overtime
            regular_ot_minutes += att.reg_appr_overtime  # Regular OT
            restday_ot_minutes += att.rest_day_hrs_ot  # Restday OT
            regular_holiday_ot_minutes += att.reg_hol_hrs_ot  # Regular Holiday OT
            special_holiday_ot_minutes += att.spec_hol_hrs_ot  # Special Holiday OT
            # Restday Regular Holiday OT
            regular_holiday_restday_ot_minutes += att.rd_reg_hol_hrs_ot
            # Restday Special Holiday OT
            special_holiday_restday_ot_minutes += att.rd_spec_hol_hrs_ot

            actual_worked_hours += att.worked_hours < 8 and att.worked_hours or 8

        # HR-4
        absences = 0
        for day in rrule.rrule(rrule.DAILY, dtstart=fields.Datetime.from_string(date_from),
                               until=fields.Datetime.from_string(date_to).replace(hour=23, minute=59, second=59,
                                                                                  microsecond=999999)):
            if not attendances.filtered(lambda r: str(day) <= r.check_in <= str(
                    day.replace(hour=23, minute=59, second=59, microsecond=999999)) and r.is_workday):
                work_hours = employee.get_day_work_hours_count(
                    day, calendar=resource_calendar_id)
                if work_hours:
                    holiday = self.env['ibas_hris.holiday'].search(
                        [('date', '=', day.date())])
                    if not holiday:
                        absences += 1

        # HR-5
        # overtimes = self.env['ibas_hris.ot'].search(
        #    [('state', '=', 'approved'), ('overtime_from', '>=', date_from + ' 00:00:00'),
        #     ('overtime_from', '<=', date_to + ' 23:59:59'), ('employee_id', '=', employee.id)])
        #regular_ot_minutes = 0.0
        #restday_ot_minutes = 0.0
        #regular_holiday_ot_minutes = 0.0
        #special_holiday_ot_minutes = 0.0
        #regular_holiday_restday_ot_minutes = 0.0
        #special_holiday_restday_ot_minutes = 0.0
        # for ot in overtimes:
        #    ot_day = fields.Datetime.from_string(date_from).date()
        #    ot_day_work_hours = employee.get_day_work_hours_count(ot_day, calendar=resource_calendar_id)
        #    ot_day_holiday = self.env['ibas_hris.holiday'].search([('date', '=', ot_day)])

        #    if ot_day_work_hours and not ot_day_holiday:  # Regular Overtime
        #        regular_ot_minutes += ot.ot_minutes
        #    elif not ot_day_work_hours and not ot_day_holiday:  # Restday Overtime
        #        restday_ot_minutes += ot.ot_minutes
        #    if ot_day_work_hours and ot_day_holiday and ot_day_holiday.holiday_type == 'regular':  # Regular Holiday Overtime
        #        regular_holiday_ot_minutes += ot.ot_minutes
        #    if ot_day_work_hours and ot_day_holiday and ot_day_holiday.holiday_type == 'special':  # Special Holiday Overtime
        #        special_holiday_ot_minutes += ot.ot_minutes
        #   if not ot_day_work_hours and ot_day_holiday and ot_day_holiday.holiday_type == 'regular':  # Regular Holiday Restday Overtime
        #        regular_holiday_restday_ot_minutes += ot.ot_minutes
        #    if not ot_day_work_hours and ot_day_holiday and ot_day_holiday.holiday_type == 'special':  # Special Holiday Restday Overtime
        #        special_holiday_restday_ot_minutes += ot.ot_minutes

        res.extend([
            {
                'name': _("Lates"),  # HR-2
                'sequence': 1,
                'code': 'LATE',
                'number_of_days': (late_in_float / 60.00) / 8.00,
                'number_of_hours': (late_in_float / 60.00),
                'contract_id': contract.id,
            }, {
                'name': _("UNDERTIME"),  # HR-3
                'sequence': 2,
                'code': 'UNDERTIME',
                'number_of_days': (undertime_minutes / 60.00) / 8.00,
                'number_of_hours': (undertime_minutes / 60.00),
                'contract_id': contract.id,
            }, {
                'name': _("ABSENT"),  # HR-4
                'sequence': 3,
                'code': 'ABSENT',
                'number_of_days': absences,
                'number_of_hours': absences * 8.00,
                'contract_id': contract.id,
            }, {
                'name': _("Overtime"),  # HR-5 (a)
                'sequence': 4,
                'code': 'OT',
                'number_of_days': (regular_ot_minutes / 60) / 8,
                'number_of_hours': regular_ot_minutes / 60,
                'contract_id': contract.id,
            }, {
                'name': _("Restday Overtime"),  # HR-5 (b)
                'sequence': 4,
                'code': 'RDOT',
                'number_of_days': (restday_ot_minutes / 60) / 8,
                'number_of_hours': restday_ot_minutes / 60,
                'contract_id': contract.id,
            }, {
                'name': _("Regular Holiday Overtime"),  # HR-5 (c)
                'sequence': 4,
                'code': 'RHOT',
                'number_of_days': (regular_holiday_ot_minutes / 60) / 8,
                'number_of_hours': regular_holiday_ot_minutes / 60,
                'contract_id': contract.id,
            }, {
                'name': _("Special Holiday Overtime"),  # HR-5 (d)
                'sequence': 4,
                'code': 'SHOT',
                'number_of_days': (special_holiday_ot_minutes / 60) / 8,
                'number_of_hours': special_holiday_ot_minutes / 60,
                'contract_id': contract.id,
            }, {
                'name': _("Restday Regular Holiday Overtime"),  # HR-5 (e)
                'sequence': 4,
                'code': 'RDRHOT',
                'number_of_days': (regular_holiday_restday_ot_minutes / 60) / 8,
                'number_of_hours': regular_holiday_restday_ot_minutes / 60,
                'contract_id': contract.id,
            }, {
                'name': _("Restday Special Holiday Overtime"),  # HR-5 (f)
                'sequence': 4,
                'code': 'RDSHOT',
                'number_of_days': (special_holiday_restday_ot_minutes / 60) / 8,
                'number_of_hours': special_holiday_restday_ot_minutes / 60,
                'contract_id': contract.id,
            }, {
                'name': _("Regular Holiday"),  # HR-6
                'sequence': 5,
                'code': 'RH',
                'number_of_days': regular_holiday_worked_hours / 8,
                'number_of_hours': regular_holiday_worked_hours,
                'contract_id': contract.id,
            }, {
                'name': _("Special Holiday"),  # HR-7
                'sequence': 6,
                'code': 'SH',
                'number_of_days': special_holiday_worked_hours / 8,
                'number_of_hours': special_holiday_worked_hours,
                'contract_id': contract.id,
            }, {
                'name': _("Restday Regular Holiday"),  # HR-8
                'sequence': 7,
                'code': 'RDRH',
                'number_of_days': restday_regular_holiday_worked_hours / 8,
                'number_of_hours': restday_regular_holiday_worked_hours,
                'contract_id': contract.id,
            }, {
                'name': _("Actual Days Worked"),  # HR-9
                'sequence': 8,
                'code': 'NORMWD',
                'number_of_days': actual_worked_hours / 8,
                'number_of_hours': actual_worked_hours,
                'contract_id': contract.id,
            }, {
                'name': _("Restday Special Holiday"),  # HR-10
                'sequence': 9,
                'code': 'RDSH',
                'number_of_days': restday_special_holiday_worked_hours / 8,
                'number_of_hours': restday_special_holiday_worked_hours,
                'contract_id': contract.id,
            }, {
                'name': _("Restday"),  # HR-10
                'sequence': 10,
                'code': 'RD',
                'number_of_days': restday_hours / 8,
                'number_of_hours': restday_hours,
                'contract_id': contract.id,
            }
        ])
        return res

    @api.multi
    def action_payslip_done(self):
        res = super(Payslip, self).action_payslip_done()
        for rec in self:
            for l in rec.line_ids:
                if l.code == 'SSSLOAN':
                    loan = rec.employee_id.loan_ids.filtered(
                        lambda r: r.state == 'open' and r.type == 'sss')
                    loan and loan[0].write(
                        {'amount_total_deducted': loan.amount_total_deducted + l.total})
                    loan and loan._compute_state()
                if l.code == 'HDMFLOAN':
                    loan = rec.employee_id.loan_ids.filtered(
                        lambda r: r.state == 'open' and r.type == 'hdmf')
                    loan and loan[0].write(
                        {'amount_total_deducted': loan.amount_total_deducted + l.total})
                    loan and loan._compute_state()
                if l.code == 'OTHLOAN':
                    # Due to Multiple Loans for OTHER type iterate
                    loans = rec.employee_id.loan_ids.filtered(
                        lambda r: r.state == 'open' and r.type == 'other')
                    #loan_amount_total = l.total
                    for loan in loans:
                        amount_deduct = loan.amount_deduct
                        loan[0].write(
                            {'amount_total_deducted': loan.amount_total_deducted + amount_deduct})
                        loan._compute_state()

                    # loan and loan[0].write(
                    #    {'amount_total_deducted': loan.amount_total_deducted + l.total})
                    #loan and loan._compute_state()
        return res

    @api.model
    def get_inputs_w_selected_struct(self, contracts, struct_id, date_from, date_to):

        res = []

        structure_ids = contracts.get_all_structures()
        structure_ids.append(struct_id)

        rule_ids = self.env['hr.payroll.structure'].browse(
            structure_ids).get_all_rules()
        sorted_rule_ids = [id for id, sequence in sorted(
            rule_ids, key=lambda x:x[1])]

        inputs = self.env['hr.salary.rule'].browse(
            sorted_rule_ids).mapped('input_ids')

        for contract in contracts:
            for input in inputs:
                input_data = {
                    'name': input.name,
                    'code': input.code,
                    'contract_id': contract.id,
                }
            res += [input_data]

        return res

    @api.onchange('employee_id', 'date_from', 'date_to', 'struct_id')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.fromtimestamp(time.mktime(
            time.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(
            babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        #raise Warning(self.struct_id)

        if not self.contract_id.struct_id:
            return

        if not self.struct_id:
            self.struct_id = self.contract_id.struct_id
        elif len(self.struct_id) == 0:
            self.struct_id = self.contract_id.struct_id

        # computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        get_worked_days = True
        if hasattr(self, 'is_imported'):
            get_worked_days = not self.is_imported
        if get_worked_days:
            worked_days_line_ids = self.get_worked_day_lines(
                contracts, date_from, date_to)
            worked_days_lines = self.worked_days_line_ids.browse([])
            for r in worked_days_line_ids:
                worked_days_lines += worked_days_lines.new(r)
            self.worked_days_line_ids = worked_days_lines

            if self.struct_id != self.contract_id.struct_id:
                input_line_ids = self.get_inputs_w_selected_struct(
                    contracts, self.struct_id.id, date_from, date_to)
            else:
                input_line_ids = self.get_inputs(contracts, date_from, date_to)
            input_lines = self.input_line_ids.browse([])

            for r in input_line_ids:
                input_lines += input_lines.new(r)
            self.input_line_ids = input_lines

        ot_line = self.worked_days_line_ids.filtered(lambda line: line.code == 'OT')
        if ot_line:
            trips = self.env['ibas_hris.trip'].search([('date', '>=', date_from), ('date', '<=', date_to), ('employee_id', '=', self.employee_id.id)])
            ot_line.number_of_hours += sum(trips.mapped('overtime'))
            ot_line.number_of_days = ot_line.number_of_hours / 8

        return
        # return super(Payslip, self).onchange_employee()

    @api.multi
    def refund_sheet(self):
        for payslip in self:
            copied_payslip = payslip.copy(
                {'credit_note': True, 'name': _('Refund: ') + payslip.name})
            payslip.refunded = True
            copied_payslip.compute_sheet()
            copied_payslip.action_payslip_done()

        formview_ref = self.env.ref('hr_payroll.view_hr_payslip_form', False)
        treeview_ref = self.env.ref('hr_payroll.view_hr_payslip_tree', False)

        return {
            'name': ("Refund Payslip"),
            'view_mode': 'tree, form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'hr.payslip',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': "[('id', 'in', %s)]" % copied_payslip.ids,
            'views': [(treeview_ref and treeview_ref.id or False, 'tree'), (formview_ref and formview_ref.id or False, 'form')],
            'context': {}
        }

class IBASHrContract(models.Model):
    _inherit = 'hr.contract'

    @api.multi
    def compute_net_pay(self, categories, contract, inputs):
        shop_rate = contract.shop_rate
        rent = contract.rental
        rent += inputs.RENT and inputs.RENT.amount
        result = categories.GROSS - categories.DED + categories.ADJUSTMENTS + shop_rate + rent
        return result

