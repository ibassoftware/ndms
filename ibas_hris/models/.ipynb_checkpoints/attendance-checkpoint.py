
from odoo import models, fields, api, _
import datetime



class ibas_attendance(models.Model):
    _inherit = 'hr.attendance'

    is_workday = fields.Boolean(compute='_compute_is_workday', string='Is Work Day?', store=True)
    
    @api.depends('employee_id', 'check_in')
    def _compute_is_workday(self):
        if (self.employee_id is not False):
            if (self.employee_id.resource_calendar_id is not False):
                dow = self.check_in.to_date().weekday()
                self.employee_id.resource_calendar_id.attendance_ids.search([("dayofweek","=",True)])
        return False