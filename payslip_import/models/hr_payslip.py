# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_imported = fields.Boolean(readonly=True, default=False)

    @api.model
    def _get_payslip_lines(self, contract_ids, payslip_id):
        values = super(Payslip, self)._get_payslip_lines(contract_ids, payslip_id)
        codes = ['TRIP', 'PHILEE', 'SSSEE', 'HDMFEE']
        if any(rec['code'] in codes for rec in values):
            payslip = self.browse(payslip_id)
            trips = self.env['ibas_hris.trip'].search([('date', '>=', payslip.date_from), ('date', '<=', payslip.date_to), ('employee_id', '=', payslip.employee_id.id)])
            for rec in values:
                if rec['code'] == 'TRIP':
                    rec['amount'] = sum(trips.mapped('amount'))
                elif rec['code'] == 'PHILEE':
                    rec['amount'] += sum(trips.mapped('philhealth_share'))
                elif rec['code'] == 'SSSEE':
                    rec['amount'] += sum(trips.mapped('sss_share'))
                elif rec['code'] == 'HDMFEE':
                    rec['amount'] += sum(trips.mapped('hdmf_share'))
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
