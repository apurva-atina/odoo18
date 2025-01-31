# -*- coding: utf-8 -*-
{
    'name': 'Add Product Specifications',
    'summary': 'Add product specifications which can be later seen on product frontend',
    'version': '18.0',
    'website': 'https://www.rescue-digital.de',
    "author": "Nilam - Atinatechnology",
    'sequence': 10,
    'depends': [ 'base', 'product', 'website_sale', 'droggol_theme_common'
    ],
    'description': "",
    'data': [
        'security/ir.model.access.csv',
        'views/product_specification.xml',
        'views/product_image.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
