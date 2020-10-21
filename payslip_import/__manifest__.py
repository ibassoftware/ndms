# -*- coding: utf-8 -*-
{
    'name': 'Payslip Import',
    'category': 'Human Resources',
    'depends': ['ibas_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/worked_days_code_data.xml',
        'data/other_input_code_data.xml',
        'views/templates.xml',
        'views/hr_payslip_views.xml',
        'views/ibas_hris_trip_views.xml',
        'views/worked_days_code_views.xml',
        'views/other_input_code_views.xml',
        'wizard/payslip_import_views.xml',
        'wizard/trip_import_views.xml',
    ],
    'qweb': [
        "static/src/xml/payslip_tree_views.xml",
        "static/src/xml/trip_tree_views.xml",
    ],
    'auto_install': True,
}
