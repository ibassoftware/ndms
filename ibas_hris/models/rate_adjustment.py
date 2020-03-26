# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class RateAdjustment(models.Model):
    _name = 'ibas_hris.rate_adjustment'
    _inherit = ['mail.thread']
    _description = 'Rate Adjustment'

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
    appointment = fields.Char('Appointment')
    job_id = fields.Many2one(
        'hr.job', related="employee_id.job_id", string='Position')
    grade = fields.Float('Grade Level')
    salary = fields.Monetary(related='employee_id.contract_id.wage', string='Monthly Salary', digits=(
        16, 2), track_visibility="onchange")
    department_id = fields.Many2one(
        'hr.department', related='employee_id.department_id', string='Project/Dept.')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(
        string="Currency", related='company_id.currency_id', readonly=True)
    # right
    date_adj = fields.Date('Date')
    employee_to = fields.Many2one('hr.employee', string='To:')
    employee_from = fields.Many2one('hr.employee', string='From:')
    recb = fields.Many2one(
        'hr.employee', domain="[('job_id', '=', recbd)]", string='Recommended by')
    recbd = fields.Many2one(
        'hr.job', compute='_default_designation', string='Recommended by Designation')
    notedby = fields.Many2one(
        'hr.employee', domain="[('job_id','=', notedbyd)]", string='Noted by')
    notedbyd = fields.Many2one('hr.job', compute='_default_designation',
                               string='Noted by Designation')
    appb_one = fields.Many2one(
        'hr.employee', domain="[('job_id','=', appbd_one)]", string='Approved by(1)')
    appbd_one = fields.Many2one('hr.job', compute='_default_designation',
                                string='Approved by (1) Designation')
    appb_two = fields.Many2one(
        'hr.employee', domain="[('job_id','=', appbd_two)]", string='Approved by(2)')
    appbd_two = fields.Many2one(
        'hr.job', compute='_default_designation', string='Approved by (2) Designation')
    # Adjustment tab
    recommendation = fields.Char('Recommendation')
    effect_from = fields.Date('Effectivity From:')
    effect_to = fields.Date('Effectivity To:')
    position = fields.Char('Position')
    grade_adj = fields.Float('Grade Level')
    rate_adjust = fields.Monetary('Rate Adjust', digits=(
        16, 2), track_visibility="onchange")
    difference = fields.Monetary(compute='_compute_difference', digits=(
        16, 2), string='Difference')
    department_adj_id = fields.Many2one(
        'hr.department', string='Project/Dept.')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

    @api.depends('rate_adjust')
    def _compute_difference(self):
        for rec in self:
            if rec.rate_adjust > rec.salary:
                rec.difference = (rec.rate_adjust - rec.salary)
            else:
                rec.difference = (rec.salary - rec.rate_adjust)

    @api.depends('employee_id')
    def _default_designation(self):
        job_obj = self.env['hr.job']

        hr_officer_job_id = job_obj.search([('name', '=', 'HR Officer')])
        general_manager_job_id = job_obj.search(
            [('name', '=', 'General Manager / HR Head')])
        coo_job_id = job_obj.search(
            [('name', '=', 'Chief Operations Officers')])
        ceo_job_id = job_obj.search(
            [('name', '=', 'President & CEO')])

        for rec in self:
            if hr_officer_job_id:
                rec.recbd = hr_officer_job_id[0].id
            else:
                rec.recbd = hr_officer_job_id.id
            if general_manager_job_id:
                rec.notedbyd = general_manager_job_id[0].id
            else:
                rec.notedbyd = general_manager_job_id.id
            if coo_job_id:
                rec.appbd_one = coo_job_id[0].id
            else:
                rec.appbd_one = coo_job_id.id
            if ceo_job_id:
                rec.appbd_two = ceo_job_id[0].id
            else:
                rec.appbd_two = ceo_job_id.id

    # @api.multi
    # def _compute_regular(self):
        #employee_id = self.id
        #contract_obj = self.env['hr.contract']
        #contract_type_obj = self.env['hr.contract.type']

        #hr_contract_type = contract_type_obj.search([('name', '=', 'Regular')])
        # hr_contract = contract_obj.search(
        #    [('employee_id', '=', employee_id), ('state', '=', 'open'), ('type_id', '=', hr_contract_type.id)])

        # for rec in self:
        #    if hr_contract:
        #        rec.regularized = True
