{
    'name': 'Product category',
    'version': '18.0',
    'category': 'App',
    'license': 'AGPL-3',
    'summary': "Product Translation",
    'description': """
            This module create product from website menuitem maybe
                """,
  
    'author': 'Nilam',
    'depends': ['product','website_sale', 'website', 'sale_management'],
    
    'data': [
                'security/ir.model.access.csv',
                'views/products.xml',
               
           
            ],
   
}
