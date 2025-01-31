from odoo import models, fields, api


class ProductPublicCategory(models.Model):
    _name = 'product.public.category'
    _inherit = ['product.public.category']
    
    
    description_x = fields.Html('category Description')
    
    
 
