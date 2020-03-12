# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _ 

class PurchaseOrder(models.Model):
	_inherit = 'purchase.order'
	_description = 'Inherit Purchase Order'

	@api.multi
	def _get_approver(self):
		for record in self:
			record.purchase_approver_id = record.company_id.purchase_approver_id
			record.purchase_notedby_id = record.company_id.purchase_notedby_id
			record.purchase_preparedby_id = record.company_id.purchase_preparedby_id

	@api.multi
	def _get_pruchase_group(self):
		for record in self:
			is_purchase_manager = False
			user_rec = self.env['res.users'].browse(record.create_uid)
			if user_rec.has_group('purchase.group_purchase_manager'):
				is_purchase_manager = True
			record.is_purchase_manager = is_purchase_manager

	project_name = fields.Char()
	attention = fields.Char()
	is_purchase_manager = fields.Boolean(compute='_get_pruchase_group')
	purchase_approver_id = fields.Many2one('res.users', string='Purchase Approver', compute='_get_approver')
	purchase_notedby_id = fields.Many2one('res.users', string='Purchase Noted By', compute='_get_approver')
	purchase_preparedby_id = fields.Many2one('res.users', string='Purchase Prepared By', compute='_get_approver')

	@api.multi
	def print_quotation(self):
		# return self.env.ref('ndm_ibas.report_purchase_quotation').report_action(self)
		if 'KONGKRETO' in self.company_id.name:
			return self.env.ref('ndm_ibas.ndm_purchase_quotation_kongkreto').report_action(self)
		else:
			return self.env.ref('ndm_ibas.ndm_purchase_quotation').report_action(self)

	@api.multi
	def print_order(self):
		# return self.env.ref('ndm_ibas.report_purchase_quotation').report_action(self)
		if 'KONGKRETO' in self.company_id.name:
			return self.env.ref('ndm_ibas.ndm_purchase_order_kongkreto').report_action(self)
		else:
			return self.env.ref('ndm_ibas.ndm_purchase_order').report_action(self)