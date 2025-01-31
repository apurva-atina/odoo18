# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models
from odoo.http import request
from odoo.addons import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def get_option_value_data(self, price_with_pricelist=True):
        self.ensure_one()
        pricelist = request.website._get_current_pricelist()
        company = self.env['website'].get_current_website().company_id
        optionData,optionValueData = self.get_option_data(pricelist, company, price_with_pricelist)
        return [optionData,optionValueData]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    custom_option_ids = fields.One2many(
        'product.custom.options', 'prod_tmpl_id',
        string='Custom Options')
    website_custom_price = fields.Float('Website price (Including Options)', compute='_website_custom_price', digits=dp.get_precision('Product Price'))
    website_custom_public_price = fields.Float('Website public price (Including Options)', compute='_website_custom_price', digits=dp.get_precision('Product Price'))


    def get_option_value_data(self, price_with_pricelist=True):
        self.ensure_one()
        pricelist = request.website._get_current_pricelist()
        company = self.env['website'].get_current_website().company_id
        optionData,optionValueData = self.get_option_data(pricelist, company, price_with_pricelist)
        return [optionData,optionValueData]


    def _website_custom_price(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website._get_current_pricelist()
        for product in self:
            if product.custom_option_ids:

                optionData,optionValueData = product.get_option_value_data()
                optionPublicData,optionValuePublicData = product.get_option_value_data(price_with_pricelist=False)
                defaultOptions = product.custom_option_ids.mapped('custom_options_value_ids').filtered('is_default')
                optionsPrice = sum([optionValueData.get(value.id, 0.0) for value in defaultOptions])
                optionsPublicPrice = sum([optionValuePublicData.get(value.id, 0.0) for value in defaultOptions])

                context = dict(self._context, pricelist=pricelist.id, partner=partner)
                self2 = self.with_context(context) if self._context != context else self

                ret = self.env.user.has_group('sale.group_show_price_subtotal') and 'total_excluded' or 'total_included'
                product.website_custom_price = product.website_price + optionsPrice
                product.website_custom_public_price = product.website_public_price + optionsPublicPrice
            else:
                product.website_custom_price = product.website_price
                product.website_custom_public_price = product.website_public_price

    def is_required_custom_options(self):
        for rec in self:
            if rec.custom_option_ids.ids:
                required_custom_options = any(rec.custom_option_ids.mapped('is_required'))
                return required_custom_options
        return False
