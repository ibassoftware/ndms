# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import xlrd

from collections import OrderedDict

from odoo import api, fields, models
from odoo.tools import pycompat

CODE_DICT = {
    'Normal Working Days paid at 100%': 'WORK100',
    'Lates': 'LATE',
    'UNDERTIME': 'UNDERTIME',
    'ABSENT': 'ABSENT',
    'Regular Holiday Overtime': 'RHOT',
    'Special Holiday Overtime': 'SHOT',
    'Restday Special Holiday Overtime': 'RDSHOT',
    'Restday Regular Holiday Overtime': 'RDRHOT',
    'Restday Overtime': 'RDOT',
    'Overtime': 'OT',
    'Regular Holiday': 'RH',
    'Special Holiday': 'SH',
    'Restday Regular Holiday': 'RDRH',
    'Actual Days Worked': 'NORMWD',
    'Restday Special Holiday': 'RDSH',
    'Restday': 'RD',
}


class PayslipImport(models.TransientModel):
    _name = 'payslip.import'
    _description = 'Payslip Import'

    file = fields.Binary('File', required=True)

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
        for rec in data:
            employee = self.env['hr.employee'].search([('name', '=', rec['Employees'])])
            if employee:
                worked_days_entries = []
                for key, value in rec.items():
                    if key == 'Employees':
                        continue
                    worked_days_entries.append((0, 0, {
                        'name': key,
                        'code': CODE_DICT.get(key, key),
                        'number_of_days': value,
                        'number_of_hours': value*8,
                        'contract_id': employee.contract_id.id
                    }))
                values = {
                    'employee_id': employee.id,
                    'worked_days_line_ids': worked_days_entries,
                    'contract_id': employee.contract_id.id,
                    'struct_id': employee.contract_id.struct_id.id
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
