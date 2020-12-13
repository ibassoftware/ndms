# -*- coding: utf-8 -*-
import base64
import time
import xlrd

from collections import OrderedDict
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import pycompat


class PayslipImport(models.TransientModel):
    _name = 'payslip.import'
    _description = 'Payslip Import'

    file = fields.Binary('File', required=True)
    date_from = fields.Date(string='Date From', required=True, default=time.strftime('%Y-%m-01'))
    date_to = fields.Date(string='Date To', required=True, default=datetime.now())

    def get_data(self, sheet, keys):
        for i in range(1, sheet.nrows):
            row = (c.value for c in sheet.row(i))
            yield OrderedDict(pycompat.izip(keys, row))

    def payslip_import(self):
        xlDecoded = base64.b64decode(self.file)
        xlsx = xlrd.open_workbook(file_contents=xlDecoded)
        sheet = xlsx.sheet_by_index(0)
        keys = [c.value for c in sheet.row(0)]
        data = self.get_data(sheet, keys)
        HR_PAYSLIP = self.env['hr.payslip']
        HR_EMPLOYEE = self.env['hr.employee']
        workdays_code = self.env['hr.payslip.worked_days.code'].search_read([('name', 'in', keys)], ['name', 'code', 'is_hour'])
        other_input_code = self.env['hr.payslip.other_input.code'].search_read([('name', 'in', keys)], ['name', 'code'])

        workdays_code_dict = {}
        input_line_dict = {}
        for code in workdays_code:
            workdays_code_dict[code['name']] = [code['code'], code['is_hour']]
        for input_line in other_input_code:
            input_line_dict[input_line['name']] = input_line['code']
        for rec in data:
            employee = HR_EMPLOYEE.search([('name', '=', rec['Employees'])], limit=1)
            if employee:
                worked_days_entries = []
                other_input_entries = []
                for key, val in rec.items():
                    if key == 'Employees':
                        continue
                    if workdays_code_dict.get(key):
                        entry = {
                            'name': key,
                            'code': workdays_code_dict[key][0],
                            'number_of_days': val if not workdays_code_dict[key][1] else val/8,
                            'number_of_hours': val*8 if not workdays_code_dict[key][1] else val,
                            'contract_id': employee.contract_id.id
                        }
                        if key == 'Overtime':
                            trips = self.env['ibas_hris.trip'].search([('date', '>=', self.date_from), ('date', '<=', self.date_to), ('employee_id', '=', employee.id)])
                            entry['number_of_hours'] += sum(trips.mapped('overtime'))
                            entry['number_of_days'] = entry['number_of_hours'] / 8
                        worked_days_entries.append((0, 0, entry))
                    elif input_line_dict.get(key):
                        other_input_entries.append((0, 0, {
                            'name': key,
                            'code': input_line_dict[key],
                            'amount': val or 0,
                            'contract_id': employee.contract_id.id
                        }))
                values = {
                    'employee_id': employee.id,
                    'worked_days_line_ids': worked_days_entries,
                    'input_line_ids': other_input_entries,
                    'contract_id': employee.contract_id.id,
                    'struct_id': employee.contract_id.struct_id.id,
                    'is_imported': True,
                    'date_to': self.date_to,
                    'date_from': self.date_from,
                    'deduct_tax': rec.get('Deduct Withholding Tax', False),
                    'deduct_sss': rec.get('Deduct SSS', False),
                    'deduct_philhealth': rec.get('Deduct Philhealth', False),
                    'deduct_hdmf': rec.get('Deduct HDMF', False),
                    'other_loans': rec.get('Other Loans', False),
                }

                record = HR_PAYSLIP.create(values)
                record.onchange_employee()
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def action_import_payslip(self):
        view_id = self.env.ref('payslip_import.view_payslip_import_form').id
        return {
            'name': 'Import Payslips',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }
