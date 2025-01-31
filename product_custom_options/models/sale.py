# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_custom_product = fields.Boolean("Have custom options")

    sale_options_ids = fields.One2many(
        'sale.custom.options', 'order_line_id',string="Custom Options")
    sale_options_price = fields.Float(string="Price",
        compute='_compute_options_price',
        digits=dp.get_precision('Product Price'),
        help="Price for the custom option.")
    non_discount_option_price = fields.Float(string="Non Discount Option Price",
        digits=dp.get_precision('Product Price'),
        help="Price for the non discount with custom options product price.")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id.custom_option_ids:
            self.is_custom_product = True
        else:
            self.is_custom_product = False


    def _compute_options_price(self):
        for line in self:
            line.sale_options_price = sum(line.sale_options_ids.mapped('price'))

    def _compute_price_unit(self):
        for line in self:
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                line.price_unit = 0.0
            else:
                price = line.with_company(line.company_id)._get_display_price()
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )
                line.price_unit += sum(line.sale_options_ids.mapped('price'))

    def configure_product(self):
        productObj = self.product_id
        if productObj.custom_option_ids:
            return {
                'name': ("Information"),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'sale.order.line',
                'view_id': self.env.ref('product_custom_options.sale_order_line_custom_options_form').id,
                'res_id': self.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
            }


    def add_option(self):
        productObj = self.product_id
        if productObj.custom_option_ids:
            wizardObj = self.env['sale.option.selection.wizard'].create({'order_line_id': self.id})
            return {
                'name': ("Information"),
                'view_mode': 'form',
                'view_type': 'form',
                'src_model': 'sale.order.line',
                'res_model': 'sale.option.selection.wizard',
                'view_id': self.env.ref('product_custom_options.sale_option_selection_wizard_form').id,
                'res_id': wizardObj.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
            }



        
    
    # def save_option(self):
    #     price_unit = 0.00
    #     product = self.product_id.with_context(
    #         lang=self.order_id.partner_id.lang,
    #         partner=self.order_id.partner_id.id,
    #         quantity=self.product_uom_qty,
    #         date=self.order_id.date_order,
    #         pricelist=self.order_id.pricelist_id.id,
    #         uom=self.product_uom.id
    #     )
    #     name = product.name_get()[0][1]
    #     if product.description_sale:
    #         name += '\n' + product.description_sale
    #     if self.order_id.pricelist_id and self.order_id.partner_id:
    #         price_unit = self.price_unit

    #     if self.sale_options_ids:
    #         from_currency = self.order_id.company_id.currency_id
    #         sale_options_price = self.sale_options_price
    #         sale_options_price = from_currency.compute(
    #         sale_options_price, self.order_id.pricelist_id.currency_id)
    #         price_unit += sale_options_price
    #         description = self.sale_options_ids.mapped(
    #             lambda option: option.custom_option_id.name+': '+option.input_data if option.custom_option_id and option.input_data else '')
    #         if description :
    #             name +='\n'+'\n'.join(description)
    #     self.name = name
    #     self.price_unit = price_unit
    #     if self.discount:
    #         getperem =self.env['ir.config_parameter'].sudo().get_param('account.show_line_subtotals_tax_selection')
    #         if getperem == 'tax_included':
    #             taxes = self.tax_id.compute_all(price_unit, self.order_id.currency_id, self.product_uom_qty, product=self.product_id, partner=self.order_id.partner_shipping_id)
    #             self.non_discount_option_price = taxes['total_included'] / self.product_uom_qty
    #         else:
    #             self.non_discount_option_price = price_unit



    def save_option(self):
        pu = 0.00
        discount = 0.00
        order = self.order_id
        product_context = dict(self.env.context)
        product_context.setdefault('lang', order.partner_id.lang)
        product_context.update({
            'partner': order.partner_id,
            'quantity': self.product_uom_qty,
            'date': order.date_order,
            'pricelist': order.pricelist_id.id,
            'uom': self.product_uom.id,
        })
        product = self.env['product.product'].with_context(product_context).with_company(order.company_id.id).browse(self.product_id.id)
        price, rule_id = self.order_id.pricelist_id.with_context(product_context)._get_product_price_rule(product, self.product_uom_qty or 1.0)
        # if order.pricelist_id.discount_policy == 'without_discount':
        #     pu = self.with_context(product_context)._get_pricelist_price_before_discount()
        #     currency =  self.currency_id

        #     if order.pricelist_id and order.partner_id:
        #         order_line = self
        #         if order_line:
        #             price = self.env['account.tax']._fix_tax_included_price_company(price, product.taxes_id, order_line[0].tax_id, self.company_id)
        #             pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id, order_line[0].tax_id, self.company_id)

        #     if pu != 0:
        #         if order.pricelist_id.currency_id != currency:
        #             date = order.date_order or fields.Date.today()
        #             pu = currency._convert(pu, order.pricelist_id.currency_id, order.company_id, date)
        #         if self.sale_options_ids:
        #             sale_options_price = self.sale_options_price
        #             sale_options_price = self.env['product.product']._get_pricelist_based_price_options(rule_id, self.sale_options_ids)
        #             pu+= self.sale_options_price
        #             price += sale_options_price
        #         discount = (pu - price) / pu * 100

        #         if discount < 0:
        #             discount = 0
        #             pu = price
        # else:
        pu = price

        if order.pricelist_id and order.partner_id:
            order_line = order._cart_find_product_line(product.id)
            if order_line:
                pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id, order_line[0].tax_id, self.company_id)
        if self.sale_options_price:
            sale_options_price = self.sale_options_price
            sale_options_price = self.env['product.product']._get_pricelist_based_price(rule_id, sale_options_price)
            from_currency = self.order_id.company_id.currency_id
            tmp = from_currency._convert(
            sale_options_price, self.order_id.pricelist_id.currency_id, self.env.company, fields.Date.today())
            pu+= tmp
        price_without_pl = (sum(self.sale_options_ids.mapped('price'))+ product.lst_price)      
        
        # name = product.name_get()[0][1]
        name = product.display_name
        if product.description_sale:
            name += '\n' + product.description_sale
                
        if self.sale_options_ids:
            description = []
            for option in self.sale_options_ids:
                if option.input_data:  
                    description.append(option.custom_option_id.name + ': ' + option.input_data)

            if description:
                name += '\n' + '\n'.join(description)

        if self.discount:
            getperem =self.env['ir.config_parameter'].sudo().get_param('account.show_line_subtotals_tax_selection')
            
            if getperem == 'tax_included':
                taxes = self.tax_id.compute_all(pu, self.order_id.currency_id, self.product_uom_qty, product=self.product_id, partner=self.order_id.partner_shipping_id)
                self.non_discount_option_price = taxes['total_included'] / self.product_uom_qty
            else:
                self.non_discount_option_price = pu
        
        self.sudo().write({
            'name': name,
            'price_unit': pu, 
            'discount': discount
        })

