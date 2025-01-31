# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
import base64
import json
import requests
import logging
from odoo.exceptions import ValidationError, UserError

from . import dhl_api

from datetime import date
_logger = logging.getLogger(__name__)

VARIABLE_SELECTION = [
    ('quantity', "Quantity"),
]


class DHLParcelDEPriceRule(models.Model):
    _name = 'dhl.parcel.de.price.rule'
    _description = 'DHL Parcel DE Price Rules'


    name = fields.Char(compute='_compute_name')
    carrier_id = fields.Many2one('delivery.carrier', 'Carrier', ondelete='cascade')
    variable = fields.Char(string = "Condition", default="Country", readonly=True)
    operator = fields.Char(string = "Operator", default="=", readonly=True)
    country_id = fields.Many2one("res.country", string="Country", required=True)
    delivery_price = fields.Float(string='Delivery Price', required=True, default=0.0)
    free_over = fields.Boolean(string="Free if order amount is above", default=False)
    free_over_amount = fields.Float(string='Free Over Amount', default=1000)
    list_price = fields.Float('Sale Price', digits='Product Price', required=True, default=0.0)
    variable_factor = fields.Selection(selection=VARIABLE_SELECTION)


    @api.depends('country_id', 'delivery_price', 'variable_factor', 'list_price', 'free_over')
    def _compute_name(self):
        for rule in self:
            name = ''
            if rule.country_id:
                name = 'if country == %s then Price %.2f' % (rule.country_id.name, rule.delivery_price)

            if rule.variable_factor:
                name += ' plus %s times %s' % (str(rule.list_price), rule.variable_factor)

            if rule.free_over:
                name += " & if order amount >= %.2f then Price 0.0" % (rule.free_over_amount)

            rule.name = name

