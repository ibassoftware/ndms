from odoo import models, fields, api, _ 

class ResUsers(models.Model):
	_inherit = 'res.users'

	e_signature = fields.Binary(string='E-Signature')