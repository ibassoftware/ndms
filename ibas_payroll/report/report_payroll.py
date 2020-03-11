from odoo import models


class PayrollXlsx(models.AbstractModel):
    _name = 'report.ibas_payroll.report_payroll'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        date_from = data['form']['date_start']
        date_to = data['form']['date_end']
        sheet = workbook.add_worksheet()
        sheet.write(0, 0, "First Name")
        sheet.write(0, 1, "Middle Name")
        sheet.write(0, 2, "Last Name")
        sheet.write(0, 3, "Department")
        sheet.write(0, 4, "Account Number")
        sheet.write(0, 5, "Gross Income")
        sheet.write(0, 6, "Net Income")
        sheet.write(0, 7, "Net Pay")
        sheet.write(0, 8, "SSS ER")
        sheet.write(0, 9, "SSS EE")
        sheet.write(0, 10, "SSS EC")
        sheet.write(0, 11, "Philhealth Personal")
        sheet.write(0, 12, "Philhealth Company Share")
        sheet.write(0, 13, "HDMF Personal")
        sheet.write(0, 14, "HDMF Company Share")
        sheet.write(0, 15, "Witholding Tax")
        sheet.write(0, 16, "Total Deductions")
        sheet.write(0, 17, "Adjustments")
        sheet.write(0, 18, "Advances")

        domain = [('state', '=', 'done')]
        if date_from:
            domain.append(('date_from', '>=', date_from))
        if date_to:
            domain.append(('date_from', '<=', date_to))

        payslips = self.env['hr.payslip'].search(domain)

        for i, ps in enumerate(payslips):
            row = i + 1
            lines = ps.line_ids
            sheet.write(row, 0, ps.employee_id.first_name)
            sheet.write(row, 1, ps.employee_id.middle_name)
            sheet.write(row, 2, ps.employee_id.last_name)
            sheet.write(row, 3, ps.employee_id.department_id and ps.employee_id.department_id.name)
            sheet.write(row, 4, ps.employee_id.bank_account_number)
            sheet.write(row, 5, sum(lines.filtered(lambda r: r.code == 'GROSS').mapped('total')))
            sheet.write(row, 6, sum(lines.filtered(lambda r: r.code == 'NET').mapped('total')))
            sheet.write(row, 7, sum(lines.filtered(lambda r: r.code == 'NETPAY').mapped('total')))
            # SSS
            sheet.write(row, 8, sum(lines.filtered(lambda r: r.code == 'SSSER').mapped('total')))
            sheet.write(row, 9, sum(lines.filtered(lambda r: r.code == 'SSSEE').mapped('total')))
            sheet.write(row, 10, sum(lines.filtered(lambda r: r.code == 'SSSEC').mapped('total')))
            # PHILHEALTH
            sheet.write(row, 11, sum(lines.filtered(lambda r: r.code == 'PHILEE').mapped('total')))
            sheet.write(row, 12, sum(lines.filtered(lambda r: r.code == 'PHILER').mapped('total')))
            # HDMF
            sheet.write(row, 13, sum(lines.filtered(lambda r: r.code == 'HDMFEE').mapped('total')))
            sheet.write(row, 14, sum(lines.filtered(lambda r: r.code == 'HDMFER').mapped('total')))

            sheet.write(row, 15, sum(lines.filtered(lambda r: r.code == 'WT').mapped('total')))
            sheet.write(row, 16, sum(lines.filtered(lambda r: r.category_id.code == 'DED').mapped('total')))
            sheet.write(row, 17, sum(lines.filtered(lambda r: r.code == 'ADJ').mapped('total')))
            sheet.write(row, 18, sum(lines.filtered(lambda r: r.code == 'ADV').mapped('total')))
