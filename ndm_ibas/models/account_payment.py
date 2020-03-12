from odoo import models, fields, api, _
from num2words import num2words


import logging
_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
	_inherit = 'account.payment'

	# check_voucher_id = fields.Many2one('account.payment.check.voucher', 'Check Voucher')

	check_number = fields.Char(string='Check Number')
	amount_in_words = fields.Char(string='Amount In words', compute='_onchange_amount', store=True)
	notes = fields.Text(string='Notes')

	@api.depends('amount')
	@api.multi
	def _onchange_amount(self):
		for rec in self:
			whole = num2words(int(rec.amount)) + ' Pesos '
			whole = whole.replace(' and ',' ')
			if "." in str(rec.amount): # quick check if it is decimal
				decimal_no = str(rec.amount).split(".")[1]
				if len(decimal_no) == 1:
					decimal_no = decimal_no + "0"
			if decimal_no:
					whole = whole + "and " + decimal_no + '/100'
			whole = whole.replace(',','')
			rec.amount_in_words = whole.upper() + " ONLY"

	@api.multi
	def action_print_check_voucher(self):
		return self.env.ref('ndm_ibas.action_report_check_voucher').report_action(self)

	@api.model
	def compute_check_amount_in_words(self):
		for record in self.search([]):
			if not record.check_amount_in_words:
				check_amount_in_words = record.currency_id.amount_to_text(record.amount)
				_logger.info(check_amount_in_words)
				record.check_amount_in_words = check_amount_in_words

# class AccountPaymentCheckVoucher(models.Model):
# 	_name = 'account.payment.check.voucher'
# 	_description = 'Payment Check Voucher'

# 	name = fields.Char(string='CV #', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
# 	payment_id = fields.Many2one('account.payment', 'Payment')
	
# 	@api.model
# 	def create(self, values):
# 		if values.get('name', 'New') == 'New':
# 			values['name'] = self.env['ir.sequence'].next_by_code('account.payment.check.voucher') or 'New'

# 		result = super(AccountPaymentCheckVoucher, self).create(values)
	
# 		return result