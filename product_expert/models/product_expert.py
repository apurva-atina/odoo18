from odoo import models, fields,_,api
from odoo.exceptions import ValidationError
import base64

class ExpertQuestions(models.Model):
    _name = "expert.questions"
    
    questions = fields.Text(string="Questions", translate=True)
    answers = fields.Text(string="Answers", translate=True)
    product_id = fields.Many2one('product.template', string='Product')


class ExpertDetails(models.Model):
    _name = "product.expert"
    _rec_name = "expert_name"

    
    expert_name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    expert_image = fields.Binary(string='Expert Image')
    expert_background_image = fields.Binary(string='Expert Background')


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    questions = fields.Text(string="Questions", translate=True)
    answers = fields.Text(string="Answers", translate=True)
    back_img_size = fields.Char(default=lambda self: _('244 x 244 px'),string="Background Image Size", readonly=True)
    img_size = fields.Char(default=lambda self: _('150 x 150 px'),string="Image Size", readonly=True)
    expert_tag = fields.Char(default=lambda self: _('Answers from the Expert'),string="Tag Name", translate=True )
    expert_questions_ids = fields.One2many('expert.questions', 'product_id', string="Experts Questions")
    
    product_expert_id = fields.Many2one(
        'product.expert',
        string='Product Expert'
    )
    
    related_expert_image = fields.Binary(
        string='Related Expert Image',
        related='product_expert_id.expert_image',
        readonly=True,
        store=True  
    )

    related_expert_background_image = fields.Binary(
    string='Background Image',
    related='product_expert_id.expert_background_image',
    readonly=True,
    store=True  
    )
      
    related_expert_description = fields.Text(
        string='Expert Description',
        related='product_expert_id.description',
        readonly=True,
        store=True  
    )
     
    related_expert_name = fields.Char(
        string='Expert Name',
        related='product_expert_id.expert_name',
        readonly=True,
        store=True  
    )
          
