# -*- coding: utf-8 -*-
{
    'name': "NDM",

    'summary': """
        NDM IBAS CUSTOMIZATIONS""",

    'description': """Customizations""",

    'description': """
        Reports:
            - NDMS Invoice
            - Purchase Order
            - Request for Quotation
      
    """,

    'author': "  EXCODE",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Custom',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account', 'account_check_printing', 'l10n_us_check_printing'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/ndm_security.xml',
        # 'templates.xml',
        'data/report_paperformat_data.xml',
        'data/report_data.xml',
        'views/layout_templates.xml',
        'views/res_config_settings_views.xml',
        'views/res_users_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/stock_picking_views.xml',
        'views/account_invoice_views.xml',
        'views/account_payment_views.xml',
        'views/account_move_views.xml',
        'views/cus_product_template_views.xml',
        # 'views/report_actions.xml',
        'wizard/sale_invoice_delivered_views.xml',
        'report/report_invoice_views.xml',
        'report/report_purchaseorder.xml',
        'report/report_purchasequotation.xml',
        'report/report_deliveryslip_views.xml',
        'report/report_payment_checkvoucher_views.xml',
        'report/report_ndm.xml',
        'report/report_print_check_views.xml',
        'report/report_salesorder_views.xml',
        'report/report.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo.xml',
    ],
}
