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
  "name"                 :  "Website Custom Options",
  "summary"              :  """This module adds support of custom option for product in odoo website.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  "1",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Custom-Options.html",
  "description"          :  """This module adds support of custom option for product in odoo website.""",
  "live_test_url"        :  "https://odoodemo.webkul.com/?module=website_custom_options",
  "depends"              :  [
                             'website_sale',
                             'product_custom_options',
                            ],
  "data"                 :  [
                             'views/templates.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  'assets'               :  {
                                'web.assets_frontend': [
                                    'website_custom_options/static/src/scss/website_custom_option.scss',
                                    'website_custom_options/static/src/js/website_custom_options.js',
                                 ],
                            },
  "application"          :  True,
  "price"                :  80,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}
