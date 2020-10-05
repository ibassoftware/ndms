# -*- coding: utf-8 -*-
{
    'name': 'Payslip Import',
    'category': 'Human Resources',
    'depends': ['ibas_payroll'],
    'data': [
        'views/templates.xml',
        'views/hr_payslip_views.xml',
        'wizard/payslip_import_views.xml',
    ],
    'qweb': [
        "static/src/xml/payslip_tree_views.xml",
    ],
    'auto_install': True,
}
