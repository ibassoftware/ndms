# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_imported = fields.Boolean(readonly=True, default=False)

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        if self.is_imported:
            return self.worked_days_line_ids.read(['name', 'sequence', 'code', 'number_of_days', 'number_of_hours', 'contract_id'])
        else:
            return super(Payslip, self).get_worked_day_lines(
                contracts, date_from, date_to)
