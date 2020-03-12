# from odoo import models, fields, api, _

# class AccountPayment(models.Model):
# 	_name = 'account.payment'

# 	check_voucher_id = fields.Many2one('account.payment.check.voucher', 'Check Voucher')

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