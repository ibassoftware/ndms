# -*- coding: utf-8 -*-
{
    'name': "ibas_payroll",

    'summary': """Complete Payroll""",

    'description': """
        Complete Payroll
    """,

    'author': "Jothimani Rajagopal",
    'website': "https://www.linkedin.com/in/jothimani-r",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['ibas_hris', 'report_xlsx'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'report/report_ibas_payslip.xml',
        'views/views.xml',
        'wizard/payroll_report_wizard_view.xml',
    ],
}
