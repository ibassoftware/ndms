# -*- coding: utf-8 -*-

from odoo import fields, models


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_imported = fields.Boolean(readonly=True, default=False)

    def get_worked_day_lines(self, contracts, date_from, date_to):
        if self.is_imported:
            return self.worked_days_line_ids.read(['name', 'sequence', 'code', 'number_of_days', 'number_of_hours', 'contract_id'])
        else:
            return super(Payslip, self).get_worked_day_lines(
                contracts, date_from, date_to)


class PayslipWorkedDaysCode(models.Model):
    _name = 'hr.payslip.worked_days.code'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
