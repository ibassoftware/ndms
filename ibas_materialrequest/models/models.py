# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MaterialRequest(models.Model):
    _name = 'ibas_materialrequest.material_request'
    _description = 'Material Request IBAS'
    _inherit = 'mail.thread'
    
    request_date = fields.Date(string='Request Date', required=True, track_visibility='onchange')
    required_date = fields.Datetime(string='Required Date', required=True, track_visibility='onchange')
    requested_by = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user, track_visibility='onchange')
    reason = fields.Text(string='Reason', required=True, track_visibility='onchange')
    operation_id = fields.Many2one('stock.picking.type', string='Operation', required=True)
    from_location = fields.Many2one('stock.location', string='From Location', required=True, track_visibility='onchange')
    to_location = fields.Many2one('stock.location', string='To Location', required=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('fulfilled', 'Fulfilled')
    ], string='Status', default='draft', track_visibility='onchange')

    transfer_id = fields.Many2one('stock.picking', string='Transfer', readonly=True)

    material_request_line_ids = fields.One2many('ibas_materialrequest.material_request_line', 'material_request_id', 
    string='Request Lines')

    def submit(self):
        for rec in self:
            rec.state = 'submitted'

    def approve(self):
        for rec in self:
            rec.state = 'approved'
            
            tid= self.env['stock.picking'].create({
                'picking_type_id': rec.operation_id.id,
                'location_id': rec.from_location.id,
                'location_dest_id': rec.to_location.id,
                'scheduled_date': rec.required_date
            })

            for pid in rec.material_request_line_ids:
                self.env['stock.move'].create({
                    'picking_id': tid.id,
                    'product_id': pid.product_id.id,
                    'product_uom_qty': pid.quantity,
                    'name': pid.product_id.name,
                    'product_uom': pid.product_id.uom_id.id,
                    'location_id': rec.from_location.id,
                    'location_dest_id': rec.to_location.id
                })
            
            rec.transfer_id = tid.id
            

    def deny(self):
        for rec in self:
            rec.state = 'draft'

    def fulfilled(self):
        for rec in self:
            rec.state = 'fulfilled'


class MaterialRequestLine(models.Model):
    _name = 'ibas_materialrequest.material_request_line'
    
    material_request_id = fields.Many2one('ibas_materialrequest.material_request', string='Material Request')
    product_id = fields.Many2one('product.product', string='Product')
    uom_id = fields.Many2one('product.uom', string='Unit of Measure')
    quantity = fields.Float(string='Quantity')
    quantity_available = fields.Float(string='QTY Available', compute="_compute_available")

    @api.depends('product_id')
    def _compute_available(self):
        for rec in self:
            if rec.product_id:
                rec.quantity_available = rec.product_id.qty_available
                rec.uom_id = rec.product_id.uom_id








# class ibas_materialrequest(models.Model):
#     _name = 'ibas_materialrequest.ibas_materialrequest'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100