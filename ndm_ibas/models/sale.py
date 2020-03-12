# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _ 

import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	total_invoiced = fields.Float(string='Total Invoiced', compute='_compute_total_invoiced', store=True, track_visibility='always')
	total_difference = fields.Float(string='Difference', compute='_compute_total_invoiced', store=True, track_visibility='always')

	@api.multi
	# @api.depends('invoice_ids.state', 'amount_total')
	@api.depends('state', 'order_line.invoice_status', 'amount_total')
	def _compute_total_invoiced(self):
		for sale in self:
			total_invoiced = 0.00
			for invoice in sale.invoice_ids:
				if invoice.state == 'paid':
					total_invoiced += invoice.amount_total
			total_difference = sale.amount_total - total_invoiced
			sale.total_invoiced = total_invoiced
			sale.total_difference = total_difference



	# HIDE/SHOW ACTION MENU
	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(SaleOrder, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		if view_type == 'tree':
			toolbar = res.get('toolbar')
			if toolbar:
				actions = res['toolbar']['action']
				count = 0
				for action in actions:
					if action['xml_id'] == 'ndm_ibas.action_sale_invoice_delivered':
						res['toolbar']['action'][count] = ""
					count += 1

		if view_type == 'form':
			company = self.env.user.company_id.name
			if "KONGKRETO" not in company:
				toolbar = res.get('toolbar')
				if toolbar:
					actions = res['toolbar']['action']
					count = 0
					for action in actions:
						if action['xml_id'] == 'ndm_ibas.action_sale_invoice_delivered':
							res['toolbar']['action'][count] = ""
						count += 1
				
		return res

