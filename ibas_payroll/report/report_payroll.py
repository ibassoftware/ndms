from odoo import models
import logging
from datetime import datetime
_logger = logging.getLogger(__name__)


class PayrollXlsx(models.AbstractModel):
    _name = 'report.ibas_payroll.report_payroll'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):
        date_from = data['form']['date_start']
        date_to = data['form']['date_end']
        company_id = data['form']['company_id']
        status = data['form']['status']
        bank_account = data['form']['bank_account'] and data['form']['bank_account'].upper(
        )

        format1 = workbook.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'})

        title2 = workbook.add_format(
            {'text_wrap': True, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'})

        bg_flesh = workbook.add_format(
            {'bg_color': '#FDE9D9', 'border': 1, 'border_color': '#D9D9D9'})

        bg_gross_title = workbook.add_format(
            {'text_wrap': True, 'bg_color': '#92D050', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'})

        bg_gross = workbook.add_format(
            {'bg_color': '#92D050', 'border': 1, 'border_color': '#D9D9D9'})

        bg_tot_deduct_title = workbook.add_format(
            {'text_wrap': True, 'bg_color': '#FFC000', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'})

        bg_tot_deduct = workbook.add_format(
            {'bg_color': '#FFC000', 'border': 1, 'border_color': '#D9D9D9'})

        bg_net_pay_title = workbook.add_format(
            {'text_wrap': True, 'bg_color': 'yellow', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#D9D9D9'})

        bg_net_pay = workbook.add_format(
            {'bg_color': 'yellow', 'border': 1, 'border_color': '#D9D9D9'})

        sheet = workbook.add_worksheet()

        sheet.set_column('A:A', 2.22)
        sheet.set_column('B:B', 24)
        sheet.set_column('C:L', 9)
        sheet.set_column('M:M', 10)
        sheet.set_column('N:W', 9)
        sheet.set_column('X:Z', 11)

        sheet.set_row(2, 69)

        sheet.write(0, 1, "PAYROLL PERIOD:", format1)

        sheet.write(1, 4, "Rate", format1)
        sheet.merge_range('F2:I2', 'Days', format1)
        sheet.merge_range('J2:M2', 'Pay', format1)
        sheet.merge_range('N2:X2', 'Deductions', format1)

        sheet.write(2, 0, "")
        sheet.write(2, 1, "Name", format1)
        sheet.write(2, 2, "Remarks", title2)
        sheet.write(2, 3, "Department", title2)
        sheet.write(2, 4, "Regular Day rate/day:", title2)
        sheet.write(2, 5, "No. of regular days", title2)
        sheet.write(2, 6, "OT hour(s):", title2)
        sheet.write(2, 7, "Late/Under time (in minutes)", title2)
        sheet.write(2, 8, "Absent", title2)
        sheet.write(2, 9, "Basic Pay", title2)
        sheet.write(2, 10, "OT Pay", title2)
        sheet.write(2, 11, "Allowance", title2)
        sheet.write(2, 12, "Additioanal Allowance", title2)
        sheet.write(2, 13, "Gross Pay", bg_gross_title)
        sheet.write(2, 14, "Late/Undertime", title2)
        sheet.write(2, 15, "Absent/SD", title2)
        sheet.write(2, 16, "Tax", title2)
        sheet.write(2, 17, "SSS", title2)
        sheet.write(2, 18, "SSS Loan", title2)
        sheet.write(2, 19, "Pagibig", title2)
        sheet.write(2, 20, "Pagibig (HDMF)", title2)
        sheet.write(2, 21, "Philhealth", title2)
        sheet.write(2, 22, "Trip", title2)
        sheet.write(2, 23, "Cash Advance", title2)
        sheet.write(2, 24, "Others", title2)
        sheet.write(2, 25, "Total Deductions", bg_tot_deduct_title)
        sheet.write(2, 26, "Adjustment", title2)
        sheet.write(2, 27, "Net Pay", bg_net_pay_title)

        domain = []
        if status:
            domain.append(('state', '=', status))
        if date_from:
            domain.append(('date_from', '>=', date_from))
        if date_to:
            domain.append(('date_from', '<=', date_to))

        if company_id:
            domain.append(('company_id', '=', company_id))

        payslips = self.env['hr.payslip'].search(domain)

        payslip_ids = []
        for payslip in payslips:
            if bank_account:
                if not payslip.employee_id.bank_account_number:
                    continue
                if bank_account != payslip.employee_id.bank_account_number.upper():
                    continue
            payslip_ids.append(payslip.id)

        payslips = self.env['hr.payslip'].browse(payslip_ids)

        date_from_string = datetime.strptime(
            date_from, '%Y-%m-%d').strftime('%B %d')
        date_to_string = datetime.strptime(
            date_to, '%Y-%m-%d').strftime('%B %d %Y')

        range_date = date_from_string + " - " + date_to_string

        sheet.merge_range('C1:Z1', range_date, format1)

        n = 3
        d = 1
        for i, ps in enumerate(payslips):
            row = i + 1
            row = n
            lines = ps.line_ids
            work_lines = ps.worked_days_line_ids
            department = ps.sudo().employee_id.department_id and ps.sudo(
            ).employee_id.department_id.name or False
            sheet.set_row(row, 27)
            sheet.write(row, 0, d)
            sheet.write(row, 1, ps.employee_id.name, format1)
            sheet.write(row, 2, ps.employee_id.bank_account_number, title2)
            sheet.write(row, 3, department, title2)
            #sheet.write(row, 4, ps.employee_id.bank_account_number, bg_flesh)
            # Rate
            sheet.write(row, 4, ps.contract_id.daily_wage, bg_flesh)
            # Days
            sheet.write(row, 5, sum(work_lines.filtered(
                lambda r: r.code == 'WORK100').mapped('number_of_days')))
            sheet.write(row, 6, sum(work_lines.filtered(
                lambda r: r.code == 'OT').mapped('number_of_hours')))
            sheet.write(row, 7, sum(work_lines.filtered(lambda r: r.code == 'LATE').mapped(
                'number_of_hours')) + sum(work_lines.filtered(lambda r: r.code == 'UNDERTIME').mapped('number_of_hours')))
            sheet.write(row, 8, sum(work_lines.filtered(
                lambda r: r.code == 'ABSENT').mapped('number_of_days')))
            # Pay
            sheet.write(row, 9, sum(lines.filtered(
                lambda r: r.code == 'BASICPAY').mapped('total')), bg_flesh)
            sheet.write(row, 10, sum(lines.filtered(
                lambda r: r.code == 'OVERTIME').mapped('total')), bg_flesh)

            sheet.write(row, 11, sum(lines.filtered(
                lambda r: r.code == 'Allowance').mapped('total')))

            sheet.write(row, 12, sum(lines.filtered(
                lambda r: r.code == 'ADDALLOWANCE').mapped('total')))

            sheet.write(row, 13, sum(lines.filtered(
                lambda r: r.code == 'GROSS').mapped('total')), bg_gross)

            # Deductions
            sheet.write(row, 14, sum(lines.filtered(lambda r: r.code == 'LATE').mapped(
                'total')) + sum(lines.filtered(lambda r: r.code == 'UNDERTIME').mapped('total')))

            sheet.write(row, 15, sum(lines.filtered(
                lambda r: r.code == 'ABSENT').mapped('total')))

            sheet.write(row, 16, sum(lines.filtered(
                lambda r: r.code == 'WT').mapped('total')))

            sheet.write(row, 17, sum(lines.filtered(
                lambda r: r.code == 'SSSEE').mapped('total')))

            sheet.write(row, 18, sum(lines.filtered(
                lambda r: r.code == 'SSSLOAN').mapped('total')))
            # pagibig
            sheet.write(row, 19, sum(lines.filtered(
                lambda r: r.code == 'HDMFEE').mapped('total')))

            sheet.write(row, 20, sum(lines.filtered(
                lambda r: r.code == 'HDMFLOAN').mapped('total')))

            sheet.write(row, 21, sum(lines.filtered(
                lambda r: r.code == 'PHILEE').mapped('total')))

            sheet.write(row, 22, sum(lines.filtered(
                lambda r: r.code == 'TRIP').mapped('total')))

            sheet.write(row, 23, sum(lines.filtered(
                lambda r: r.code == 'ADV').mapped('total')))

            sheet.write(row, 24, sum(lines.filtered(
                lambda r: r.code == 'OTHLOAN').mapped('total')))

            sheet.write(row, 25, sum(lines.filtered(lambda r: r.category_id.code in ['DED', 'LOANS', 'ADVANCES', 'TRIP', 'EMP']).mapped('total')), bg_tot_deduct)

            sheet.write(row, 26, sum(lines.filtered(
                lambda r: r.code == 'ADJ').mapped('total')))

            sheet.write(row, 27, sum(lines.filtered(
                lambda r: r.code == 'NETPAY').mapped('total')), bg_net_pay)

            n += 1
            d += 1
