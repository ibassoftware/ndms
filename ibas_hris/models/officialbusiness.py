from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import pytz
from xlrd import open_workbook
import base64
import io

class OfficialBusiness(models.Model):
    _name = 'ibas_hris.official_business'
    _description = 'Official Business'
    
    from_date = fields.Datetime(string='From', required=True)
    to_date = fields.Datetime(string='To', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
         ('submitted', 'Submitted'),
          ('approved', 'Approved'),
    ], string='Status', default='draft')
    Description = fields.Text(string='Description', required=True)

    def submit_ob(self):
        for rec in self:
            rec.state = 'submitted'
    
    def approve_ob(self):
        for rec in self:
            rec.state = 'approved'
            tz = pytz.timezone('Asia/Manila')
            workday = fields.Datetime.from_string(rec.from_date).astimezone(tz).date()

            mywd = self.env['hr.attendance'].search([
                ('workdate','=',workday),
                 ('employee_id','=',rec.employee_id.id)
            ])

            if len(mywd) <= 0:
                self.env['hr.attendance'].create({
                    'employee_id': rec.employee_id.id,
                    'check_in': rec.from_date,
                    'check_out': rec.to_date
                })
                
            else:
                current_ci = fields.Datetime.from_string(mywd[0].check_in)
                current_co = fields.Datetime.from_string(mywd[0].check_out)
                ob_ci = fields.Datetime.from_string(rec.from_date)
                ob_co = fields.Datetime.from_string(rec.to_date)
                if current_ci > ob_ci:
                    mywd[0].write({                  
                        'check_in': ob_ci                       
                    })
                
                if ob_co > current_co:
                    mywd[0].write({          
                        'check_out': ob_co
                    })
                
                # Update attendance
    
    def deny_ob(self):
        for rec in self:
            rec.state = 'draft'


    