# Copyright 2023 Rescue Digital Systems GmbH
{
    'name': 'Add Product Expert ',
    'version': '18.0',
    "summary": "Adds a product expert in backend which is visible in product frontend",
    'website': 'https://www.rescue-digital.de',
    'author': "Nilam Jadhav - Atinatechnology",
    'depends': ['base', 'product','website_sale'],
    'category': 'Extra Tools',
    'data': [
        'security/ir.model.access.csv',
        'views/product_expert_template.xml',
        'views/product_expert_menu.xml'
        
    ],
    'installable': True,
    'application': False,
}