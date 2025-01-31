from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    bullet_point_1 = fields.Char(string="Product 1", translate=True)
    bullet_point_2 = fields.Char(string="Product 2", translate=True)
    bullet_point_3 = fields.Char(string="Product 3", translate=True)
    bullet_point_4 = fields.Char(string="Product 4", translate=True)
    bullet_point_5 = fields.Char(string="Product 5", translate=True)
    subheadline = fields.Char(string="Subheadline", translate=True)



        
