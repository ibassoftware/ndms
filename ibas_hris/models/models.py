# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from num2words import num2words
import logging
_logger = logging.getLogger(__name__)


class ibas_hris(models.Model):
    _inherit = 'hr.job'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'For Approval'),
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='draft', help="Set whether the recruitment process is open or closed for this job position.")

    @api.multi
    def action_submit(self):
        self.write({
            'state': 'submitted',
        })

    requesition_date = fields.Date(string='Requisition Date')
    date_required = fields.Date(string='Date Required')

    educational_attainment = fields.Selection([
        ('college', 'College'),
        ('collegelevel', 'College Level'),
        ('vocational', 'Vocational'),
        ('hs', 'High School'),
        ('elementary', 'Elementary'),
        ('other', 'Other'),
    ], string='')

    skills_experiences = fields.Text(string='Skills and Experiences Required')

    employment_classification = fields.Selection([
        ('managerial', 'Managerial'),
        ('engineer', 'Engineer'),
        ('staff', 'Staff'),
        ('projectworker', 'Project Workers'),
        ('other', 'Other'),
    ], string='Employment Classification')

    hiring_status = fields.Selection([
        ('regular', 'Regular'),
        ('probationary', 'Probationary'),
        ('contractual', 'Contractual'),
        ('projectbased', 'Project Based'),
    ], string='Hiring Status')

    hiring_justification = fields.Text(string='Hiring Justification')

    if_not_met = fields.Text(string='If Not Met')

    requested_by = fields.Many2one('hr.employee', string='Requested By')


class ibas_applicant(models.Model):
    _inherit = "hr.applicant"

    first_name = fields.Char(string='First Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')

    @api.onchange('first_name', 'last_name')
    def _onchange_first_name(self):
        for rec in self:
            rec.partner_name = rec.first_name
            if rec.last_name:
                rec.partner_name = rec.partner_name + " " + rec.last_name

    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])[
                    'contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            else:
                new_partner_id = self.env['res.partner'].create({
                    'is_company': False,
                    'name': applicant.partner_name,
                    'email': applicant.email_from,
                    'phone': applicant.partner_phone,
                    'mobile': applicant.partner_mobile,
                    'first_name': applicant.first_name,
                    'middle_name': applicant.middle_name,
                    'last_name': applicant.last_name
                })
                address_id = new_partner_id.address_get(['contact'])['contact']
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write(
                    {'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({
                    'name': applicant.partner_name or contact_name,
                    'job_id': applicant.job_id.id,
                    'address_home_id': address_id,
                    'department_id': applicant.department_id.id or False,
                    'address_id': applicant.company_id and applicant.company_id.partner_id
                    and applicant.company_id.partner_id.id or False,
                    'work_email': applicant.department_id and applicant.department_id.company_id
                    and applicant.department_id.company_id.email or False,
                    'work_phone': applicant.department_id and applicant.department_id.company_id
                    and applicant.department_id.company_id.phone or False,
                    'first_name': applicant.first_name,
                    'middle_name': applicant.middle_name,
                    'last_name': applicant.last_name
                })
                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(
                    _('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window


class ibas_employee(models.Model):
    _inherit = "hr.employee"

    first_name = fields.Char(string='First Name')
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')

    @api.onchange('first_name', 'last_name')
    def _onchange_first_name(self):
        for rec in self:
            rec.name = rec.first_name
            if rec.last_name:
                rec.name = rec.name + " " + rec.last_name

    cost_center = fields.Many2one(
        'account.analytic.account', string='Cost Center')
    present_address = fields.Text(string='Present Address')
    permanent_address = fields.Text(string='Permanent Address')

    father = fields.Char(string='Father')
    mother = fields.Char(string='Mother')
    emergency_contact = fields.Char(string='Emergency Contact')
    emergency_contact_number = fields.Char(string='Emergency Contact Number')

    height = fields.Char(string='Height')
    weight = fields.Char(string='Weight')
    religion = fields.Char(string='Religion')
    date_hired = fields.Date(string='Date Hired')
    employee_number = fields.Char(string='Employeee Number')
    bio_number = fields.Integer(string='Biometric Number')

    sss = fields.Char(string='SSS No')
    tin = fields.Char(string='TIN No')
    hdmf = fields.Char(string='HDMF no')
    philhealth = fields.Char(string='Philhealth No')

    bank_account_number = fields.Char(string='Bank Account')

    children_ids = fields.One2many(
        'ibas_hris.employee_children', 'employee_id', string='Children')
    education_ids = fields.One2many(
        'ibas_hris.employee_education', 'employee_id')
    work_ids = fields.One2many('ibas_hris.employee_work', 'employee_id')
    reference_ids = fields.One2many(
        'ibas_hris.employee_reference', 'employee_id')
    requirement_ids = fields.One2many(
        'ibas_hris.employee_requirement', 'employee_id', string='Requirements')

    work_sched = fields.Many2one('resource.calendar', string='Work Shift')

    regularized = fields.Boolean(
        compute='_compute_regular', string="Regularized")

    rate_of_adjustment_ids = fields.One2many(
        'ibas_hris.rate_adjustment', 'employee_id', string="Adjustment")

    lateral_transfer_ids = fields.One2many(
        'ibas_hris.lateral_transfer', 'employee_id', string="Lateral Transfer")

    count_roa = fields.Integer(
        compute='_count_roa', string='Rate of Adjustment')

    count_lt = fields.Integer(
        compute='_count_lt', string='Lateral Transfer')

    @api.depends('rate_of_adjustment_ids')
    def _count_roa(self):
        if not self.ids:
            # Update calculated fields
            self.update({
                'count_roa': 0,
            })
            return True

        for rec in self:
            count = 0
            if rec:
                for roa in rec.rate_of_adjustment_ids:
                    count += 1
            rec.update({
                'count_roa': count,
            })

    @api.depends('lateral_transfer_ids')
    def _count_lt(self):
        if not self.ids:
            # Update calculated fields
            self.update({
                'count_lt': 0,
            })
            return True

        for rec in self:
            count = 0
            if rec:
                for lt in rec.lateral_transfer_ids:
                    count += 1
            rec.update({
                'count_lt': count,
            })

    @api.multi
    def open_roa(self):
        rate_of_adjustment_ids = self.rate_of_adjustment_ids
        rate_of_adjustment_id = []
        for rate_adj in rate_of_adjustment_ids:
            rate_of_adjustment_id += [rate.id for rate in rate_adj]
        # Open Payment Entry Form
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object(
            'ibas_hris.action_ibas_hris_rate_adjustment')
        kanban_view_id = imd.xmlid_to_res_id(
            'ibas_hris.ibas_hris_rate_adjustment_view_kanban')
        form_view_id = imd.xmlid_to_res_id(
            'ibas_hris.ibas_hris_rate_adjustment_view_form')

        tree_view_id = imd.xmlid_to_res_id(
            'ibas_hris.ibas_hris_rate_adjustment_view_tree')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[kanban_view_id, 'kanban'], [form_view_id, 'form'], [tree_view_id, 'tree']],
            'target': action.target,
            # 'context': action.context,
            'res_model': action.res_model,
            'res_id': rate_of_adjustment_id and rate_of_adjustment_id[0] or False,
        }
        result['domain'] = "[('id', 'in', [" + \
            ','.join(map(str, rate_of_adjustment_id)) + "])]"
        # result['domain'] = "[('id','=',[%s])]" % rate_of_adjustment_id
        return result

    @api.multi
    def open_lt(self):
        lateral_transfer_ids = self.lateral_transfer_ids
        lateral_transfer_id = []
        for lt in lateral_transfer_ids:
            lateral_transfer_id += [rec.id for rec in lt]
        # Open Payment Entry Form
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object(
            'ibas_hris.action_ibas_hris_lateral_transfer')

        kanban_view_id = imd.xmlid_to_res_id(
            'ibas_hris.ibas_hris_lateral_transfer_view_kanban')

        form_view_id = imd.xmlid_to_res_id(
            'ibas_hris.ibas_hris_lateral_transfer_view_form')

        tree_view_id = imd.xmlid_to_res_id(
            'ibas_hris.ibas_hris_lateral_transfer_view_tree')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[kanban_view_id, 'kanban'], [form_view_id, 'form'], [tree_view_id, 'tree']],
            'target': action.target,
            # 'context': action.context,
            'res_model': action.res_model,
            'res_id': lateral_transfer_id and lateral_transfer_id[0] or False,
        }
        result['domain'] = "[('id', 'in', [" + \
            ','.join(map(str, lateral_transfer_id)) + "])]"
        # result['domain'] = "[('id','=',[%s])]" % rate_of_adjustment_id
        return result

    @api.multi
    def _compute_regular(self):
        for rec in self:
            employee_id = rec.id
            contract_obj = self.env['hr.contract']
            contract_type_obj = self.env['hr.contract.type']

            hr_contract_type = contract_type_obj.search(
                [('name', '=', 'Regular')])
            hr_contract = contract_obj.search(
                [('employee_id', '=', employee_id), ('state', '=', 'open'), ('type_id', '=', hr_contract_type.id)])
            if hr_contract:
                rec.regularized = True

    @api.model
    def create(self, vals):
        requirements = self.env['ibas_hris.requirement'].search(
            [("is_default", "=", True)])
        res = super().create(vals)
        _logger.debug(res)
        _logger.debug("HEEYYYYYYYYYY")
        for req in requirements:
            _logger.debug("HEEYYYYYYYYYY")
            _logger.debug(req)
            self.env['ibas_hris.employee_requirement'].create({
                'employee_id': res.id,
                'requirement_id': req.id
            })
        return res


class ibas_employee_children(models.Model):
    _name = "ibas_hris.employee_children"
    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')

    employee_id = fields.Many2one('hr.employee', string='Employee')


class ibas_employee_education(models.Model):
    _name = "ibas_hris.employee_education"
    educ_type = fields.Selection([
        ('elementary', 'Elementary'),
        ('hs', 'High School'),
        ('voca', 'Vocational'),
        ('coll', 'College'),
        ('other', 'Others'),
    ], string='Type')
    name = fields.Char(string='Institution Name', required=True)
    course = fields.Char(string='Course or Training')
    address = fields.Char(string='Address')
    year_attended = fields.Char(string='Year')

    employee_id = fields.Many2one('hr.employee', string='Employee')


class ibas_employee_work(models.Model):
    _name = "ibas_hris.employee_work"
    name = fields.Char(string='Company', required=True)
    position = fields.Char(string='Position')
    address = fields.Char(string='Address')
    year_attended = fields.Char(string='Year')

    employee_id = fields.Many2one('hr.employee', string='Employee')


class ibas_employee_reference(models.Model):
    _name = "ibas_hris.employee_reference"
    name = fields.Char(string='Name', required=True)
    occupation = fields.Char(string='Occupation')
    address = fields.Char(string='Address')
    contact = fields.Char(string='Contact Number')

    employee_id = fields.Many2one('hr.employee', string='Employee')


class ibas_employee_contract(models.Model):
    _inherit = "hr.contract"

    schedule_pay = fields.Selection(
        selection_add=[('per-trip', 'Per-Trip'), ('daily', 'Daily')])
    allowance = fields.Float(string='Untaxable Allowance')
    daily_wage = fields.Float(string='Daily Rate')
    work_days = fields.Selection([
        ('six', 'Six Days'),
        ('five', 'Five Days')
    ], string='Work Days')

    def ComputeSSS(self):
        low = 2250
        high = 2750
        er = 200
        ee = 100
        for rec in self:
            while high <= rec.wage:
                low = low + 500
                high = high + 500
                er = er + 40
                ee = ee + 20
                if low < rec.wage and rec.wage < high:
                    rec.sss_ee = ee
                    rec.sss_er = er

                if er >= 1600:
                    rec.sss_ee = 800
                    rec.sss_er = 1600
                    break

    def ComputePhilHealth(self):
        for rec in self:
            if rec.wage <= 10000:
                rec.philhealth_personal = 150
                rec.philhealth_company = 150
            elif 10000 < rec.wage and rec.wage <= 59999.99:
                fshare = (rec.wage * 0.03)
                rec.philhealth_personal = round(fshare / 2, 2)
                rec.philhealth_company = round(fshare / 2, 2)
                total = rec.philhealth_company + rec.philhealth_personal
                if total != fshare:
                    rec.philhealth_personal = rec.philhealth_company - 0.01
            else:
                rec.philhealth_personal = 900
                rec.philhealth_company = 900

    # @api.onchange('daily_wage', 'work_days')
    # def _onchange_daily_wage(self):
    #     for rec in self:
    #         if rec.work_days == "six":
    #             rec.wage = (rec.daily_wage * 313 ) / 12
    #         else:
    #             rec.wage = (rec.daily_wage * 261 ) / 12

    #         self.ComputeSSS()
    #         self.ComputePhilHealth()

    @api.onchange('wage')
    def _onchange_wage(self):
        for rec in self:
            if rec.work_days == "six":
                adr = rec.wage / 26
                if adr != rec.daily_wage:
                    rec.daily_wage = adr
            else:
                adr = (rec.wage * 12) / 261
                if adr != rec.daily_wage:
                    rec.daily_wage = adr
            if rec.wage < 15250:
                rec.sss_ec = 10
            else:
                rec.sss_ec = 30

            self.ComputeSSS()
            self.ComputePhilHealth()

    sss_ec = fields.Float(string='SSS EC')
    sss_er = fields.Float(string='SSS ER')
    sss_ee = fields.Float(string='SSS EE')
    philhealth_personal = fields.Float(string='Philhealth Personal Share')
    philhealth_company = fields.Float(string='Philhealth Company Share')
    hdmf_personal = fields.Float(string='HDMF Personal Share', default=100)
    hdmf_company = fields.Float(string='HDMF Company Share', default=100)
    probationary_period = fields.Float(string='Probationary Period in Months')
    probationary_period_words = fields.Char(
        string='Wage In Words', compute='_compute_proby', store=True)

    amount_in_words = fields.Char(
        string='Wage In Words', compute='_onchange_amount', store=True)

    daily_wage_in_words = fields.Char(
        string='Daily Rate In Words', compute='_onchange_daily_wage', store=True)

    shop_rate = fields.Float(string="Shop Rate")

    @api.depends('daily_wage')
    def _onchange_daily_wage(self):
        for rec in self:
            whole = num2words(int(rec.daily_wage)) + ' Pesos '
            whole = whole.replace(' and ', ' ')
            if "." in str(rec.daily_wage):  # quick check if it is decimal
                decimal_no = str(rec.daily_wage).split(".")[1]
            if decimal_no:
                whole = whole + "and " + decimal_no + '/100'
            whole = whole.replace(',', '')
            rec.daily_wage_in_words = whole.upper() + " ONLY"

    @api.depends('wage')
    @api.multi
    def _onchange_amount(self):
        for rec in self:
            whole = num2words(int(rec.wage)) + ' Pesos '
            whole = whole.replace(' and ', ' ')
            if "." in str(rec.wage):  # quick check if it is decimal
                decimal_no = str(rec.wage).split(".")[1]
            if decimal_no:
                whole = whole + "and " + decimal_no + '/100'
            whole = whole.replace(',', '')
            rec.amount_in_words = whole.upper() + " ONLY"

    @api.depends('probationary_period')
    @api.multi
    def _compute_proby(self):
        for rec in self:
            rec.probationary_period_words = num2words(
                int(rec.probationary_period))


class ibas_requirement(models.Model):
    _name = 'ibas_hris.requirement'

    name = fields.Char(string='Name', required=True)
    is_default = fields.Boolean(string='Applies to All', default=True)


class ibas_employee_requirement(models.Model):
    _name = 'ibas_hris.employee_requirement'
    requirement_id = fields.Many2one(
        'ibas_hris.requirement', string='Requirement', required=True)
    compliance_date = fields.Date(string='Compliance Date')
    complied = fields.Boolean(readonly=True, string='Complied', stored=True)
    file_attachment = fields.Binary(string='Attachment')
    employee_id = fields.Many2one('hr.employee', string='Employee')

    @api.onchange('compliance_date')
    def _onchange_compliance_date(self):
        for rec in self:
            if (rec.compliance_date is not False):
                rec.complied = True
            else:
                rec.complied = False
