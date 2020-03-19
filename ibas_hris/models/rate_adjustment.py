# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class RateAdjustment(models.Model):
    _name = 'ibas_hris.rate_adjustment'
    _inherit = ['mail.thread']
    _description = 'Rate Adjustment'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)
    appointment = fields.Char('Appointment')
    job_id = fields.Many2one(
        'hr.job', string='Position', required=True)
