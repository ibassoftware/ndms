from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):
	_inherit = 'res.company'

	purchase_approver_id = fields.Many2one('res.users', string='Purchase Approver')
	purchase_notedby_id = fields.Many2one('res.users', string='Purchase Noted By')
	purchase_preparedby_id = fields.Many2one('res.users', string='Purchase Prepared By')
	invoice_approver_id = fields.Many2one('res.users', string='Invoice Approver')

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	purchase_approver_id = fields.Many2one('res.users', string='Purchase Approver', related='company_id.purchase_approver_id')
	purchase_notedby_id = fields.Many2one('res.users', string='Purchase Noted By', related='company_id.purchase_notedby_id')
	purchase_preparedby_id = fields.Many2one('res.users', string='Purchase Prepared By', related='company_id.purchase_preparedby_id')
	invoice_approver_id = fields.Many2one('res.users', string='Invoice Approver', related='company_id.invoice_approver_id')