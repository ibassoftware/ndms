from odoo import models, fields, api, _ 
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class SaleInvoiceDelivered(models.TransientModel):
	_name = 'sale.invoice.delivered'

	def invoice_line_create(self, invoice_id, qty, line):
		invoice_lines = self.env['account.invoice.line']
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

		for delivery in line.mapped('move_ids'):
			if delivery.state == "done":
				dr_no = delivery.picking_id.name
				# location = delivery.picking_id.project_name
				location = delivery.picking_id.project_address
				plate_no = delivery.picking_id.plate_no
				# location_no = delivery.location_no
				qty = delivery.quantity_done

		# dr_no = line.mapped('move_ids').mapped('dr_no')[0]
		# location = line.mapped('move_ids').mapped('location')[0]
		# plate_no = line.mapped('move_ids').mapped('plate_no')[0]
		# location_no = line.mapped('move_ids').mapped('location_no')[0]
				if not float_is_zero(qty, precision_digits=precision):
					vals = line._prepare_invoice_line(qty=qty)
					vals.update({'invoice_id': invoice_id, 'sale_line_ids': [(6, 0, [line.id])], 'dr_no': dr_no, 'location': location, 'plate_no': plate_no})
					invoice_lines |= self.env['account.invoice.line'].create(vals)
		return invoice_lines

	@api.multi
	def create_invoice(self):
		order = self.env['sale.order'].browse(self._context.get('active_ids', []))
		order_line = order.mapped('order_line')
		if order.state != 'sale':
			raise UserError(_('This order should be confirmed first before invoicing.'))

		if not any(line.qty_delivered > 0 for line in order_line):
			raise UserError(_('This order have no delivered quantities.'))

		inv_obj = self.env['account.invoice']
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		invoices = {}
		references = {}

		group_key = order.id or (order.partner_invoice_id.id, order.currency_id.id)
		for line in order_line.sorted(key=lambda l: l.qty_delivered < 0):
			if float_is_zero(line.qty_delivered, precision_digits=precision):
				continue
			if group_key not in invoices:
				inv_data = order._prepare_invoice()
				invoice = inv_obj.create(inv_data)
				references[invoice] = order
				invoices[group_key] = invoice
			elif group_key in invoices:
				vals = {}
				if order.name not in invoices[group_key].origin.split(', '):
					vals['origin'] = invoices[group_key].origin + ', ' + order.name
				if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', ') and order.client_order_ref != invoices[group_key].name:
					vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
				invoices[group_key].write(vals)
			if line.qty_delivered > 0 and line.qty_delivered != line.qty_invoiced:
				quantity = line.qty_delivered - line.qty_invoiced
				# line.invoice_line_create(invoices[group_key].id, quantity)
				self.invoice_line_create(invoices[group_key].id, quantity, line)

		if references.get(invoices.get(group_key)):
			if order not in references[invoices[group_key]]:
				references[invoice] = references[invoice] | order

		if not invoices:
			raise UserError(_('There is no invoicable line.'))

		for invoice in invoices.values():
			if not invoice.invoice_line_ids:
				raise UserError(_('There is no invoicable line.'))
			# If invoice is negative, do a refund invoice instead
			if invoice.amount_untaxed < 0:
				invoice.type = 'out_refund'
				for line in invoice.invoice_line_ids:
					line.quantity = -line.quantity
			# Use additional field helper function (for account extensions)
			for line in invoice.invoice_line_ids:
				line._set_additional_fields(invoice)
			# Necessary to force computation of taxes. In account_invoice, they are triggered
			# by onchanges, which are not triggered when doing a create.
			invoice.compute_taxes()
			invoice.message_post_with_view('mail.message_origin_link',
				values={'self': invoice, 'origin': references[invoice]},
				subtype_id=self.env.ref('mail.mt_note').id)
		
		return {'type': 'ir.actions.act_window_close'}