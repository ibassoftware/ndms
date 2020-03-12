# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.models import AbstractModel


class PubWarrantyOverride(AbstractModel):
	_inherit = 'publisher_warranty.contract'

	@api.multi
	def update_notification(self, cron_mode=True):

		set_param = self.env['ir.config_parameter'].sudo().set_param
		set_param('database.expiration_date', '2050-10-10')
		set_param('database.expiration_reason', 'demo')
		set_param('database.enterprise_code', 'exc123abc')



# class r2d2_patch(models.Model):
#     _name = 'r2d2_patch.r2d2_patch'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100