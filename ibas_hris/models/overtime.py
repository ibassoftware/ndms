# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class IBASOT(models.Model):
    _name = 'ibas_hris.ot'
    _inherit = ['mail.thread']
    _description = 'Overtime'
    
    overtime_from = fields.Datetime(string='From', required=True)
    overtime_to = fields.Datetime(string='To', required=True)
    reason = fields.Text(string='Reason', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    ot_minutes = fields.Float(compute='_compute_ot_minutes', string='Overtime in Minutes', store=True)
    
    @api.depends('overtime_to')
    def _compute_ot_minutes(self):
        for rec in self:
            if rec.overtime_from is not False and rec.overtime_to is not False:
                td = fields.Datetime.from_string(rec.overtime_to) - fields.Datetime.from_string(rec.overtime_from)
                rec.ot_minutes = td.total_seconds() / 60

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved')
    ], string='State', default='draft', track_visibility='onchange')

    def submit(self):
        for rec in self:
            rec.state = 'submitted'
    
    def approve(self):
        for rec in self:
            rec.state = 'approved'
    
    def deny(self):
        for rec in self:
            rec.state = 'draft'