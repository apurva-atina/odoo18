# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
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
{
    "name"          :  "DHL Parcel DE Shipping Integration",
    "summary"       :  """Integrate DHL Parcel DE shipping functionality directly within Odoo ERP applications to deliver increased logistical efficiencies.""",
    "category"      :  "Website/Shipping Logistics",
    "version"       :  "1.0.0",
    "author"        :  "Webkul Software Pvt. Ltd.",
    "license"       :  "Other proprietary",
    "website"       :  "https://store.webkul.com/",
    "description"   :  """
                        DHL Parcel DE Shipping API Integration as Odoo DHL Parcel DE Delivery Method .
                        Provide Shipping Label Generation and Shipping Rate Calculator For Website as Well Odoo BackEnd""",
    "depends"       :  ['odoo_shipping_service_apps', 'website_sale'],
    "data"          :  [
        'security/ir.model.access.csv',
        'views/dhl_parcel_de_price_rule_views.xml',
        'views/dhl_parcel_de_delivery.xml',
        'views/stock_picking_views.xml',
        'views/stock_package_type_view.xml',
        'data/data.xml',
        'data/delivery_demo.xml',
        'data/manifest_cron.xml',
        'data/manifest_sequence.xml',
    ],
    "images"        :  [],
    "application"   :  True,
    "installable"   :  True,
    # "price"         :  149,
    # "currency"      :  "USD",
    "pre_init_hook" :  "pre_init_check",
    "external_dependencies": {'python': ['pycountry']}
}
