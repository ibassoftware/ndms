# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TripTemplate(models.Model):
    _inherit = "ibas_hris.trip_template"

    code = fields.Char(string="Code")


class Trip(models.Model):
    _inherit = "ibas_hris.trip"
    _description = 'TRIPS'

    code = fields.Char(related='trip_template_id.code')
    quantity = fields.Float(string='Quantity', default=1)
    sub_amount = fields.Monetary(string="Subtotal Amount")
    amount = fields.Monetary(string="Amount", required=True, compute='_compute_amount')
    sss_share = fields.Monetary(string='SSS Employee Share')
    hdmf_share = fields.Monetary(string='HDMF Employee Share')
    philhealth_share = fields.Monetary(string='Philhealth Employee Share')
    advances = fields.Monetary()
    adjustment = fields.Monetary()
    shop_rate = fields.Monetary()

    @api.onchange('trip_template_id')
    def _onchange_sub_amount(self):
        if self.trip_template_id:
            self.sub_amount = self.trip_template_id.amount

    @api.depends('quantity', 'sub_amount')
    def _compute_amount(self):
        for rec in self:
            if rec.quantity > 0:
                rec.amount = rec.quantity * rec.sub_amount
            else:
                rec.quantity = 0
