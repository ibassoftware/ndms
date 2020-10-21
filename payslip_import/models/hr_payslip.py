# -*- coding: utf-8 -*-

from odoo import fields, models


class Payslip(models.Model):
    _inherit = 'hr.payslip'

    is_imported = fields.Boolean(readonly=True, default=False)


class PayslipWorkedDaysCode(models.Model):
    _name = 'hr.payslip.worked_days.code'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    is_hour = fields.Boolean(string='Hours', help="Make it True if file contains hour for this Work code")


class PayslipOtherInputCode(models.Model):
    _name = 'hr.payslip.other_input.code'

    name = fields.Char(string='Description', required=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
