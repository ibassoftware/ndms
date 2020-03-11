from odoo import models, fields, api


class PayrollReportWizard(models.TransientModel):
    _name = 'payroll.report.wizard'

    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')

    @api.multi
    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_from,
                'date_end': self.date_to,
            },
        }
        return self.env.ref('ibas_payroll.report_payroll_xlsx').report_action(self, data=data)
