from odoo import models, fields, api, _

class ProductSpecification(models.Model):
    _name = 'product_specification.specification'
    _description = 'Product Specification'

    name = fields.Char(string='Name', required=True)
    value = fields.Char(string='Value', required=True)
    product_id = fields.Many2one('product.template', string='Product')
    
    
class ProductImage(models.Model):
    _inherit = 'product.image'

    image_name = fields.Char(string='Name')
    is_featured = fields.Boolean(string='Featured', default=False)
    product_specification = fields.Many2one('product_specification.specification', string='Product Specification')
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    

    specification = fields.One2many('product_specification.specification', 'product_id', string="Specification")
    name_id = fields.Many2one('product.image', string='Customer Name', compute='_compute_image_match',search=True)
    image_id = fields.Image(related='name_id.image_1920',search=True)
    technical_data = fields.Char(default=lambda self: _('Technical Data'),string="Technical Data", translate=True )
    order_no = fields.Char(default=lambda self: _('Order No.:'),string="Order No", translate=True )
    
    def _compute_image_match(self):
        for template in self:
            matching_image = self.env['product.image'].search([('name', '=', template.name)])
            if matching_image:
                lst = []
                for img in matching_image:
                    if img.is_featured == True:
                        lst.append(img.id)
                
                if lst:
                    for set_img in lst:
                        if set_img:
                            template.name_id = set_img
                else:
                    template.name_id = False
                  
            else:
                template.name_id = False
            # matching_image = self.env['product.image'].search([('name', '=', template.name)], limit=1)
            # if matching_image:
            #     template.name_id = matching_image.id
            # else:
            #     template.name_id = False

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    display_checkbox = fields.Boolean(string="More Display")
