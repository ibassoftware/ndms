from odoo import models, fields, api, _ 

class StockPicking(models.Model):
	_inherit = 'stock.picking'

	is_company_konkreto = fields.Boolean(compute='_compute_company')
	is_batching_delivery = fields.Boolean(related='picking_type_id.is_batching_delivery')
	project_name = fields.Char(string='Project Name')
	project_address = fields.Char(string='Address')
	driver_name = fields.Char(string='Driver')
	volume = fields.Char(string='Volume')
	strength = fields.Char(string='Strength')
	aggregate = fields.Char(string='Aggregate')
	gross_weight = fields.Char(string='Gross WT')
	tare_wt = fields.Char(string='Tare WT')
	net_wt = fields.Char(string='NET WT')
	slump = fields.Char(string='Slump')
	plate_no = fields.Char(string='Plate #')
	acc_vol = fields.Char(string='Acc. Vol.')
	timeout_p = fields.Char(string='Time Out')

	@api.multi
	@api.depends('company_id')
	def _compute_company(self):
		context = self._context or {}
		for record in self:
			company = self.env.user.company_id.name
			if "KONGKRETO" in company:
				record.is_company_konkreto = True

class StockMove(models.Model):
	_inherit = 'stock.move'

	dr_no = fields.Char(string='DR No.')
	location = fields.Char(string='Location')
	plate_no = fields.Char(string='Plate #')
	location_no = fields.Char(string='Location #')

class StockPickingType(models.Model):
	_inherit = 'stock.picking.type'

	is_batching_delivery = fields.Boolean()