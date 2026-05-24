# -*- coding: utf-8 -*-
{
    'name': "om_odoo_inheritence",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'author': "Eslam Eid",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','sale','sale_stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
}
