from odoo import models, fields, _

class ProductTemplateCustomize(models.Model):
    _inherit = 'product.template'
   
    product_description = fields.Html(string='Product Description', translate=True)
    products_information = fields.Char(default=lambda self: _('Product information'), string="Product information", translate=True)
