from odoo import models, fields, api, _ 
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

class hrAttendanceBatchComputation(models.TransientModel):
	_name = 'hr.attendance.compute.wiz'

	@api.multi
	def action_computeAttendance(self):
		hr_attendance_obj = self.env['hr.attendance'].browse(self._context.get('active_ids', []))
		if hr_attendance_obj:
			for attendance in hr_attendance_obj:
				attendance.action_computeAttendance()