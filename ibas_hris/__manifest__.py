# -*- coding: utf-8 -*-
{
    'name': "ibas_hris",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_recruitment', 'analytic', 'hr_contract', 'web', 'hr_attendance',
                'resource', 'hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/customviews.xml',
        'views/overtime.xml',
<<<<<<< HEAD
        'views/.ipynb_checkpoints/views-checkpoint.xml',
        'views/.ipynb_checkpoints/templates-checkpoint.xml',
=======
        'views/rate_adjustment_view.xml',
        'views/lateral_transfer_view.xml',
        'views/.ipynb_checkpoints/views-checkpoint.xml',
        'views/.ipynb_checkpoints/templates-checkpoint.xml',
        'wizard/hr_attendance_compute_wiz.xml',
>>>>>>> dd56d33fd7171303517f39951788ebd525b2c177
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
