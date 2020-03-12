# -*- coding: utf-8 -*-
# Copyright YEAR(S), AUTHOR(S)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
	_inherit = 'account.invoice'

	@api.multi
	def _get_approver(self):
		for record in self:
			record.invoice_approver_id = record.company_id.invoice_approver_id

	is_company_konkreto = fields.Boolean(compute='_compute_company')
	invoice_approver_id = fields.Many2one('res.users', string='Invoice Approver', compute='_get_approver')

	@api.multi
	@api.depends('company_id')
	def _compute_company(self):
		context = self._context or {}
		for record in self:
			company = self.env.user.company_id.name
			if "KONGKRETO" in company:
				record.is_company_konkreto = True

	# CHANGE DESCRIPTION LABEL IN INVOICE LINE / TREE VIEW
	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AccountInvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		if view_type == 'form':
			company = self.env.user.company_id.name
			if "KONGKRETO" in company:
				fields = res.get('fields')
				if fields:
					if fields.get('invoice_line_ids'):
						res['fields']['invoice_line_ids']['views']['tree']['fields']['name']['string'] = _('Design/Description')
		return res

	@api.multi
	def invoice_print(self):
		self.ensure_one()
		self.sent = True
		if 'KONGKRETO' in self.company_id.name:
			return self.env.ref('ndm_ibas.ndm_account_invoice_kongkreto').report_action(self)
		else:
			return self.env.ref('ndm_ibas.ndm_account_invoice').report_action(self)

	@api.multi
	def invoice_print_draft(self):
		self.ensure_one()
		if 'KONGKRETO' in self.company_id.name:
			return self.env.ref('ndm_ibas.ndm_account_invoice_kongkreto').report_action(self)
		else:
			return self.env.ref('ndm_ibas.ndm_account_invoice').report_action(self)

class AccountInvoiceLine(models.Model):
	_inherit = 'account.invoice.line'

	delivery_date = fields.Date(string='Delivery Date')
	dr_no = fields.Char(string='DR No.')
	location = fields.Char(string='Location')
	plate_no = fields.Char(string='Plate #')
	location_no = fields.Char(string='Location #')

	# CHANGE DESCRIPTION LABEL IN INVOICE LINE / FORM VIEW
	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(AccountInvoiceLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		if self._context.get('is_company_konkreto'):
			fields = res.get('fields')
			if fields:
				if fields.get('name'):
					res['fields']['name']['string'] = _('Design/Description')
		return res
