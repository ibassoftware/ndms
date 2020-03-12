# -*- coding: utf-8 -*-
{
    'name': "r2d2_patch",

    'summary': """
        R2D2 Customization Patch""",

    'description': """
        R2D2 Customization Patch
    """,

    'author': "Excode Innovations",
    'website': "http://www.odoo.world",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail','web', 'web_enterprise'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
       
    ],
    'qweb': [
        "static/src/xml/base.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ]

    
}