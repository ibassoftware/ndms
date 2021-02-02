# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_imported = fields.Boolean(readonly=True, default=False)

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        values = super(Payslip, self)._get_payslip_lines(contract_ids, payslip_id)
        codes = ['TRIP', 'PHILEE', 'SSSEE', 'HDMFEE']
        added_gross = 0
        added_deductions = 0
        added_net = 0
        if any(rec['code'] in codes for rec in values):
            payslip = self.browse(payslip_id)
            trips = self.env['ibas_hris.trip'].search([('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to), ('employee_id', '=', payslip.employee_id.id)])
            for rec in values:
                if rec['code'] == 'TRIP':
                    rec['amount'] += sum(trips.mapped('amount'))
                    added_gross += sum(trips.mapped('amount'))
                elif rec['code'] == 'PHILEE':
                    rec['amount'] += sum(trips.mapped('philhealth_share'))
                    added_deductions += sum(trips.mapped('philhealth_share'))
                elif rec['code'] == 'SSSEE':
                    rec['amount'] += sum(trips.mapped('sss_share'))
                    added_deductions += sum(trips.mapped('sss_share'))
                elif rec['code'] == 'HDMFEE':
                    rec['amount'] += sum(trips.mapped('hdmf_share'))
                    added_deductions += sum(trips.mapped('hdmf_share'))
                elif rec['code'] == 'ADV':
                    rec['amount'] += sum(trips.mapped('advances'))
                    added_deductions += sum(trips.mapped('advances'))
                elif rec['code'] == 'ADJ':
                    rec['amount'] += sum(trips.mapped('adjustment'))
                    added_net += sum(trips.mapped('adjustment'))
                elif rec['code'] == 'SR':
                    rec['amount'] += sum(trips.mapped('shop_rate'))
                    added_net += sum(trips.mapped('shop_rate'))
                elif rec['code'] == 'Allowance':
                    rec['amount'] += sum(trips.mapped('allowance'))
                    added_gross += sum(trips.mapped('allowance'))
                elif rec['code'] == 'RENT':
                    rec['amount'] += sum(trips.mapped('rental'))
                    added_net += sum(trips.mapped('rental'))
                elif rec['code'] == 'GROSS':
                    rec['amount'] += added_gross
                elif rec['code'] == 'NET':
                    additional_net = ((added_gross + added_net) - added_deductions)
                    rec['amount'] += additional_net

        return values


class PayslipWorkedDaysCode(models.Model):
    _name = 'hr.payslip.worked_days.code'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    is_hour = fields.Boolean(string='Hours', help="Make it True if file contains hour for this Work code")


class PayslipOtherInputCode(models.Model):
    _name = 'hr.payslip.other_input.code'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
