# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import datetime
import time
import xlrd

from collections import OrderedDict
# from datetime import datetime

from odoo import api, fields, models
from odoo.tools import pycompat


class PayslipImport(models.TransientModel):
    _name = 'trip.import'
    _description = 'Trip Import'

    file = fields.Binary('File', required=True)

    def get_data(self, sheet):
        keys = [c.value for c in sheet.row(0)]
        for i in range(1, sheet.nrows):
            row = (c.value for c in sheet.row(i))
            yield OrderedDict(pycompat.izip(keys, row))

    def trip_import(self):
        xlDecoded = base64.b64decode(self.file)
        xlsx = xlrd.open_workbook(file_contents=xlDecoded)
        sheet = xlsx.sheet_by_index(0)
        data = self.get_data(sheet)
        IBAS_TRIP = self.env['ibas_hris.trip']
        HR_EMPLOYEE = self.env['hr.employee']
        TRIP_TEMPLATE = self.env['ibas_hris.trip_template']
        for rec in data:
            employee = HR_EMPLOYEE.search([('name', '=', rec['Employees'])], limit=1)
            trip_template = TRIP_TEMPLATE.search([('code', '=', rec['Code'])], limit=1)
            if employee and trip_template:
                IBAS_TRIP.create({
                    'employee_id': employee.id,
                    'trip_template_id': trip_template.id,
                    'loc_from': trip_template.loc_from,
                    'loc_to': trip_template.loc_to,
                    'quantity': rec['Quantity'] if rec['Quantity'] > 0 else 1,
                    'sub_amount': trip_template.amount,
                    'remarks': rec['Remarks'],
                    'date': datetime.datetime(*xlrd.xldate_as_tuple(rec['Date'], xlsx.datemode))
                })
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.model
    def action_import_trip(self):
        view_id = self.env.ref('payslip_import.view_trip_import_form').id
        return {
            'name': 'Import Trips',
            'res_model': self._name,
            'type': 'ir.actions.act_window',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
        }
