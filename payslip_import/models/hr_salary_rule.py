# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.multi
    def _compute_rule(self, localdict):
        self.ensure_one()
        if self.code == 'TRIP':
            payslip = localdict.get('payslip')
            trips = self.env['ibas_hris.trip'].search([('date', '>=', payslip.date_from.strftime('%Y-%m-%d')), ('date', '<=', payslip.date_to.strftime('%Y-%m-%d')), ('employee_id', '=', payslip.employee_id)])
            amount = sum(trips.mapped(lambda trip: trip.amount + trip.sss_share + trip.hdmf_share + trip.philhealth_share))
            return amount, float(safe_eval(self.quantity, localdict)), 100.0
        return super(HrSalaryRule, self)._compute_rule(localdict)
