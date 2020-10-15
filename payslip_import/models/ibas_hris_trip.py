# -*- coding: utf-8 -*-
from odoo import models, fields


class TripTemplate(models.Model):
    _inherit = "ibas_hris.trip_template"

    code = fields.Char(string="Code")


class Trip(models.Model):
    _inherit = "ibas_hris.trip"
    _description = 'TRIPS'

    code = fields.Char(related='trip_template_id.code')
