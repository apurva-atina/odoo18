# Copyright 2023 Rescue Digital Systems GmbH
{
    'name': 'Sales: Order Confirmation mail template',
    'version': '18.0',
    "summary": "Sales: Order Confirmation mail template design",
    'website': 'https://www.rescue-digital.de',
    'author': "Nilam Jadhav - Atinatechnology",
    'depends': ['base','sale_management','mail','sale','website_sale','website'],
    'category': 'Extra Tools',
    
    'data': [
        'data/inherit_mail_template.xml'    
    ],
    
    'assets': {
        'web.assets_frontend': [
            'sale_order_mail_template/static/scss/style.scss',
        ],
    },
    
    'installable': True,
    'application': False,
}