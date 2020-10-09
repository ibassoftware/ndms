# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
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

    def get_data(self, sheet):
        keys = [c.value for c in sheet.row(0)]
        for i in range(1, sheet.nrows):
            row = (c.value for c in sheet.row(i))
            yield OrderedDict(pycompat.izip(keys, row))

    def payslip_import(self):
        xlDecoded = base64.b64decode(self.file)
        xlsx = xlrd.open_workbook(file_contents=xlDecoded)
        sheet = xlsx.sheet_by_index(0)
        data = self.get_data(sheet)
        HR_PAYSLIP = self.env['hr.payslip']
        workdays_code = self.env['hr.payslip.worked_days.code'].search_read([], ['name', 'code'])
        workdays_code_dict = {}
        for code in workdays_code:
            workdays_code_dict[code['name']] = code['code']
        for rec in data:
            employee = self.env['hr.employee'].search([('name', '=', rec['Employees'])])
            if employee:
                worked_days_entries = []
                for key, value in rec.items():
                    if key == 'Employees':
                        continue
                    worked_days_entries.append((0, 0, {
                        'name': key,
                        'code': workdays_code_dict.get(key, key),
                        'number_of_days': value,
                        'number_of_hours': value*8,
                        'contract_id': employee.contract_id.id
                    }))
                values = {
                    'employee_id': employee.id,
                    'worked_days_line_ids': worked_days_entries,
                    'contract_id': employee.contract_id.id,
                    'struct_id': employee.contract_id.struct_id.id,
                    'is_imported': True,
                    'date_to': self.date_to,
                    'date_from': self.date_from
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
