# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.hr_payroll.models.hr_payslip import HrPayslip


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_imported = fields.Boolean(readonly=True, default=False)

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        if self.is_imported:
            return HrPayslip.get_worked_day_lines(self, contracts, date_from, date_to)
        else:
            return super(Payslip, self).get_worked_day_lines(
                contracts, date_from, date_to)
