# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class CustomProductTemplate(models.Model):
    _inherit = 'product.template'

    strength = fields.Char('Strength')
    aggregate = fields.Char('Aggregate')
    slump = fields.Char('Slump')


class CustomStockPicking(models.Model):
    _inherit = 'stock.picking'

    strength = fields.Char(related='product_id.strength', string='Strength')
    aggregate = fields.Char(related='product_id.aggregate', string='Aggregate')
    slump = fields.Char(related='product_id.slump', string='Slump')
    volume = fields.Float(compute='_compute_vol', string='Volume')
    acc_vol = fields.Float(compute='_compute_acc_vol', string='Acc. Vol.')

    @api.depends('move_lines')
    def _compute_vol(self):
        for rec in self:
            if rec.move_lines:
                for move in rec.move_lines:
                    rec.volume = move.quantity_done

    @api.depends('move_lines')
    def _compute_acc_vol(self):
        for rec in self:
            partner_id = rec.partner_id.id
            origin = rec.origin
            picking_obj = rec.env['stock.picking']
            picking = picking_obj.search(
                [('origin', '=', origin), ('partner_id', '=', partner_id), ('state', '=', 'done')])
            if picking:
                for pick in picking:
                    rec.acc_vol += pick.volume
