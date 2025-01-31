from odoo import fields, models, api


class Menu(models.Model):
    _inherit = "website.menu"
    
    checkbox_field = fields.Boolean(string='Menu Feature')
        
    @api.model
    def get_tree(self, website_id, menu_id=None):
        website = self.env['website'].browse(website_id)
       
        def make_tree(node):            
            menu_url = node.page_id.url if node.page_id else node.url
            menu_node = {
                'fields': {
                    'id': node.id,
                    'name': node.name,
                    'url': menu_url,
                    'new_window': node.new_window,
                    'is_mega_menu': node.is_mega_menu,
                    'sequence': node.sequence,
                    'checkbox_field': node.checkbox_field,
                    'parent_id': node.parent_id.id,
                },
                'children': [],
                'is_homepage': menu_url == (website.homepage_url or '/'),
            }
            
            for child in node.child_id:
                menu_node['children'].append(make_tree(child))
            return menu_node
        

        menu = menu_id and self.browse(menu_id) or website.menu_id
        return make_tree(menu)
    
