from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
	_inherit = 'account.move'

	def _allow_post(self):
		for record in self:
			allow_post = False
			if record.is_reversal and record.state == 'validate':
				allow_post = True
			if not record.is_reversal and record.state == 'draft':
				allow_post = True
			record.is_allow_post = allow_post

	def _allow_approve(self):
		for record in self:
			allow_approve = False
			company = self.env.user.company_id
			if record.is_reversal and record.state == 'draft' and record.company_id == company and self.env.user.has_group('ndm_ibas.group_reverse_entry_approver'):
				allow_approve = True
			record.is_allow_approve = allow_approve

	state = fields.Selection(selection_add=[('validate','Validated')])
	is_reversal = fields.Boolean()
	is_allow_post = fields.Boolean(compute='_allow_post')
	is_allow_approve = fields.Boolean(compute='_allow_approve')
	validated_by = fields.Many2one('res.users')
	validated_on = fields.Datetime()

	@api.multi
	def _reverse_move(self, date=None, journal_id=None):
		self.ensure_one()
		reversed_move = self.copy(default={
			'date': date,
			'journal_id': journal_id.id if journal_id else self.journal_id.id,
			'ref': _('reversal of: ') + self.name, 
			'is_reversal': True,},)
			
		for acm_line in reversed_move.line_ids.with_context(check_move_validity=False):
			acm_line.write({
				'debit': acm_line.credit,
				'credit': acm_line.debit,
				'amount_currency': -acm_line.amount_currency
			})
		return reversed_move

	@api.multi
	def reverse_moves(self, date=None, journal_id=None):
		date = date or fields.Date.today()
		reversed_moves = self.env['account.move']
		for ac_move in self:
			reversed_move = ac_move._reverse_move(date=date,
												  journal_id=journal_id)
			reversed_moves |= reversed_move
			#unreconcile all lines reversed
			aml = ac_move.line_ids.filtered(lambda x: x.account_id.reconcile or x.account_id.internal_type == 'liquidity')
			aml.remove_move_reconcile()
			#reconcile together the reconciliable (or the liquidity aml) and their newly created counterpart
			for account in list(set([x.account_id for x in aml])):
				to_rec = aml.filtered(lambda y: y.account_id == account)
				to_rec |= reversed_move.line_ids.filtered(lambda y: y.account_id == account)
				#reconciliation will be full, so speed up the computation by using skip_full_reconcile_check in the context
				to_rec.with_context(skip_full_reconcile_check=True).reconcile()
				to_rec.force_full_reconcile()
		if reversed_moves:
			# reversed_moves._post_validate()
			# reversed_moves.post()
			return [x.id for x in reversed_moves]
		return []

	def action_validate(self):
		self.write({
			'state': 'validate',
			'validated_by': self.env.user.id,
			'validated_on': fields.Datetime.now(),
		})