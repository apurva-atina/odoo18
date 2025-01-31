# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
import logging
_logger= logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def check_required_custom_options(self, line):
        if line.product_id.custom_option_ids:
            required_ids = line.product_id.custom_option_ids.filtered(lambda opt: opt.is_required)
            msg = ', '.join([option.name for option in required_ids])
            selected_options = line.sale_options_ids.custom_option_id.ids
            if not all(option in selected_options for option in required_ids.ids):
                raise ValidationError(f'Some Required custom options are not selected for the product "{line.product_id.name}".\n{msg} are required custom options.')

    def action_confirm(self):
        for line in self.order_line:
            self.check_required_custom_options(line)
        return super().action_confirm()    

    def _cart_update(self, product_id=None, line_id=None, add_qty=0,
                     set_qty=0, attributes=None, **kwargs):
        custom_options = request.env.context.get('custom_options', {}) or self._context.get('custom_options', {})
        values = super(SaleOrder, self)._cart_update(
            product_id, line_id, add_qty, set_qty, **kwargs)

        customOptionModel = self.env['product.custom.options']
        customOptionValueModel = self.env['product.custom.options.value']

        lineId = values.get('line_id')

        line = self.env['sale.order.line'].sudo().browse(lineId)
        if line.exists() and line.product_id.custom_option_ids:
            price = float()
            line.is_custom_product = True
            optionIds = []
            for optionId, inputData in custom_options.items():
                if not optionId or not inputData or optionId == "file_name":
                    continue
                file_input = False
                optionIds.append(int(optionId))
                optionObj = customOptionModel.browse(int(optionId))

                optionType = optionObj.input_type
                if optionType not in ['radio', 'drop_down', 'multiple', 'checkbox']:
                    price = optionObj.price

                if optionType in ['radio', 'drop_down']:
                    valueObj = customOptionValueModel.browse(int(inputData))
                    price = valueObj.price
                    inputData = valueObj.name
                elif optionType in ['multiple', 'checkbox']:
                    names = []
                    prices = []
                    for valueId in inputData:
                        valueObj = customOptionValueModel.browse(int(valueId))
                        prices.append(valueObj.price)
                        names.append(valueObj.name)
                    inputData = ', '.join(names)
                    price = sum(prices)
                elif(optionType == 'file'):

                    if custom_options.get("file_name",False):
                        file_input = inputData.split(",")[1].strip()
                        inputData = custom_options.get("file_name",False)
                    else:
                        file_input = base64.encodestring(inputData.read())
                        inputData = inputData.filename

                description_ids = line.sale_options_ids.filtered(
                    lambda r: r.custom_option_id == optionObj)
                if description_ids:
                    description_id = description_ids[0]
                    description_id.update({
                        'input_data': inputData,
                        'file_data': file_input,
                        'price': price,
                    })
                else:
                    newId = line.sale_options_ids.new({
                        'custom_option_id': optionObj.id,
                        'order_line_id': line.id,
                        'input_data': inputData,
                        'price': price,
                        'file_data': file_input,
                    })
                    line.sale_options_ids += newId
            if add_qty:
                line.sale_options_ids.filtered(
                    lambda r: r.custom_option_id.id not in optionIds).unlink()
            line.with_context(wk_source='website').save_option()       
       
        return values


    @api.model
    def get_custom_options_array(self, custom_options):
        updated_custom_options = {}
        customOptionModel = self.env['product.custom.options']
        customOptionValueModel = self.env['product.custom.options.value']
        for optionId, inputData in custom_options.items():
            if not optionId or not inputData or optionId == "file_name":
                continue
            file_input = False
            optionObj = customOptionModel.browse(int(optionId))
            optionType = optionObj.input_type

            if optionType in ['radio', 'drop_down', 'swatch_visual']:
                valueObj = customOptionValueModel.browse(int(inputData))
                inputData = valueObj.name
            elif optionType in ['multiple', 'checkbox']:
                names = []
                prices = []
                for valueId in inputData:
                    valueObj = customOptionValueModel.browse(int(valueId))
                    names.append(valueObj.name)
                inputData = ', '.join(names)
            elif(optionType == 'file'):
                if custom_options.get("file_name"):
                    inputData = custom_options.get("file_name",False)
                else:
                    inputData = inputData.filename

            updated_custom_options.update({optionId:inputData})
        return updated_custom_options


    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        self.ensure_one()
        order_lines = super(SaleOrder, self)._cart_find_product_line(
            product_id, line_id, **kwargs)
        product = self.env['product.product'].browse(product_id)
        if not order_lines or not product.custom_option_ids:
            return order_lines
        custom_options = request.env.context.get('custom_options', {}) or self._context.get('custom_options', {})
        updatedOptions = self.get_custom_options_array(custom_options)
        orderLine = order_lines and order_lines[0]

        if not updatedOptions and line_id:
            return order_lines
        for orderLine in order_lines:
            savedOptions = dict([(str(saleOption.custom_option_id.id), saleOption.input_data) for saleOption in orderLine.sale_options_ids])
            if savedOptions == updatedOptions:
                return orderLine
        return self.env['sale.order.line']

class Website(models.Model):
    _inherit = 'website'


    # def sale_get_order(self, force_create=False, update_pricelist=False):
    #     res = super(Website,self).sale_get_order(force_create, update_pricelist)
    #     partner_sudo = self.env.user.partner_id
    #     pricelist_id = self.pricelist_id.id
    #     if update_pricelist:
    #         request.session['website_sale_current_pl'] = pricelist_id
    #         res.write({'pricelist_id': pricelist_id})
    #         values = {'pricelist_id': pricelist_id}
    #         res.write(values)
    #         res._recompute_prices()
    #         for line in res.order_line:
    #             if line.exists():
    #                 res._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
    #     return res
