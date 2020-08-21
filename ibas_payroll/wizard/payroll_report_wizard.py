from odoo import models, fields, api


class PayrollReportWizard(models.TransientModel):
    _name = 'payroll.report.wizard'

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    company_id = fields.Many2one('res.company', string='Company')
    #bank_account = fields.Many2one('res.company', string='Company')

    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_from,
                'date_end': self.date_to,
                'company_id':  self.company_id and self.company_id.id or False,
            },
        }
        return self.env.ref('ibas_payroll.report_payroll_xlsx').report_action(self, data=data)
