# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class LateralTransfer(models.Model):
    _name = 'ibas_hris.lateral_transfer'
    _inherit = ['mail.thread']
    _description = 'Lateral Transfer'

    name = fields.Char('Ref')
    state = fields.Selection([
        ('draft', 'New'),
        ('pending', 'For Approval'),
        ('approved', 'Approved'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled')
    ], string='Status', group_expand='_expand_states', track_visibility='onchange', default='draft')
    # left
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)
    date_hired = fields.Date(
        related='employee_id.date_hired', string='Date Hired')
    job_id = fields.Many2one('hr.job', string='From Position')
    department_id = fields.Many2one('hr.department', string='From Department')
    salary = fields.Monetary(related='employee_id.contract_id.wage', string='From Salary', digits=(
        16, 2), track_visibility="onchange")
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(
        string="Currency", related='company_id.currency_id', readonly=True)
    # right
    appby = fields.Char('Approved by')
    appbyd = fields.Char(string='Approved by Designation')
    notedby_one = fields.Char('Noted by (1)')
    notedby_one_d = fields.Char('Noted by (1) Designation')
    notedby_two = fields.Char('Noted by (2)')
    notedby_two_d = fields.Char('Noted by (2) Designation')
    conformeby = fields.Char('Conforme by:')
    # transfer tab
    new_dept = fields.Char('New Department')
    new_job = fields.Char('New Position')
    new_salary = fields.Monetary(string='New Salary', digits=(
        16, 2), track_visibility="onchange")
    reason_trans = fields.Char('Reason for Transfer')
    training = fields.Boolean('Training')
    period = fields.Float(string='Period')
    difference = fields.Monetary(compute='_compute_difference', digits=(
        16, 2), string='Difference')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.onchange('training', 'period')
    def _onchange_period(self):
        for rec in self:
            if not rec.training:
                rec.period = 0.0

    @api.depends('new_salary')
    def _compute_difference(self):
        for rec in self:
            if rec.new_salary > rec.salary:
                rec.difference = (rec.new_salary - rec.salary)
            else:
                rec.difference = (rec.salary - rec.new_salary)
