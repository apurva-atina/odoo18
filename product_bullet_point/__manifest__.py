# Copyright 2023 Rescue Digital Systems GmbH
{
    'name': 'Add Bullet Points',
    "summary": "Adds Bullet Points to the product, which can be displayed on product frontend",
    'version': '18.0',
    'website': 'https://www.rescue-digital.de',
    "author": "Nilam - Atinatechnology",
    'category': 'Extra Tools',
    'sequence': 10,
    'depends': [ 'base', 'product'
    ],
    
    'description': "",
    'data': [
        'views/product.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
