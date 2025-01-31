# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################


from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)


class CustomoptionPrice(http.Controller):
    @http.route(['/update/option/price'], type='json', auth="public", website=True, csrf=False)
    def updateprice(self, combination, qty, **kw):
        optionData = {}
        optionValueData = {}
        pricelist = request.website._get_current_pricelist()
        company = request.env['website'].get_current_website().company_id
        product_id = request.env['product.product'].browse(combination.get('product_id'))
        optionData,optionValueData = product_id.with_context(quantity = qty).get_option_data(pricelist, company, price_with_pricelist=True)
        actual_optionData,actual_optionValueData = product_id.with_context(quantity = qty).get_option_data(pricelist, company, price_with_pricelist=False)

        multi_option_field_html = {}
        dropdown_option_field_html = {}
        if(kw.get('multiple')):
            for multiple_id in kw.get('multiple'):
                multi_option_field_html[multiple_id] = request.env['ir.ui.view']._render_template(
                    'website_custom_options.OptionTemplate', {
                        'option_id': request.env['product.custom.options'].browse(int(multiple_id)),
                        'option_value_price_data': optionValueData
                    })
        if(kw.get('dropdown')):
            for dropdown_id in kw.get('dropdown'):
                dropdown_option_field_html[dropdown_id] = request.env['ir.ui.view']._render_template(
                    'website_custom_options.OptionTemplate', {
                        'option_id': request.env['product.custom.options'].browse(int(dropdown_id)),
                        'option_value_price_data': optionValueData

                    })
               
        result =  {
                'combination_price_info':{
                'option_data':optionData,
                'option_public_data':optionData,
                'option_value_data':optionValueData,
                'option_value_public_data':optionValueData,
                'actual_option_data' : actual_optionData,
                'actual_option_value_data' : actual_optionValueData,
                'multi_option_field_html': multi_option_field_html,
                'dropdown_option_field_html': dropdown_option_field_html
                }
            }
        return result


class WebsiteSaleCustom(WebsiteSale):

    def check_required_custom_options(self, product_id, kw):
        product_id = request.env['product.product'].sudo().browse([product_id])
        if product_id.custom_option_ids:
            required_ids = product_id.custom_option_ids.filtered(lambda opt: opt.is_required)
            msg = ', '.join([option.name for option in required_ids])
            if kw.get('custom_options',False):
                result = self._filter_custom_options(eval(kw.get('custom_options',False)))
                if result.get('file_name',False):
                    del result['file_name']
                selected_options = result.keys()
                selected_option_ids = [eval(i) for i in selected_options]
                if not all(option in selected_option_ids for option in required_ids.ids):
                    raise ValidationError(f'Some Required custom options are not selected for the product "{product_id.name}".\n{msg} are required custom options.')    

    def _filter_custom_options(self, kw):
        custom_options = {
            k.split('-')[2]: v for k,
            v in kw.items() if "custom_options" in k}
        custom_option_checkbox = {
            k: v for k, v in kw.items() if "custom_option_checkbox" in k}
        custom_option_multiple = {
            k: v for k, v in kw.items() if "custom_option_multiple" in k}
        for optionName in custom_option_multiple.keys():
            optionId = optionName.split('-')[2]
            selectedIds = request.httprequest.form.getlist(optionName)
            if isinstance(selectedIds, list) and len(selectedIds) == 0:
                selectedIds = custom_option_multiple[optionName]
            custom_options.update({optionId: selectedIds})
        for optionName, valueId in custom_option_checkbox.items():
            optionId = optionName.split('-')[2]
            inputData = custom_options.get(optionId, [])
            inputData += [valueId]
            custom_options.update({optionId: inputData})
        if kw.get("file_name",False):
            custom_options.update({
            "file_name":kw.get("file_name",False)
            })
        return custom_options

    @http.route(
        ['/shop/cart/update'],
        type='http',
        auth="public",
        methods=['GET', 'POST'],
        website=True,
        csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        self.check_required_custom_options(product_id, kw)
        request.env.context = dict(request.env.context, custom_options=self._filter_custom_options(eval(kw.get('custom_options',False))))
        result =  super(WebsiteSaleCustom, self).cart_update(product_id=product_id, add_qty=add_qty, set_qty=set_qty, **kw)
        return result 

    @http.route()
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        self.check_required_custom_options(product_id, kw)
        if kw.get('custom_options', False):
            request.env.context = dict(request.env.context, custom_options=self._filter_custom_options(eval(kw.get('custom_options',False))))
        result =  super(WebsiteSaleCustom, self).cart_update_json(
            product_id = product_id,
            line_id = line_id,
            add_qty = add_qty,
            set_qty = set_qty,
            display = display, **kw)
        return result 
