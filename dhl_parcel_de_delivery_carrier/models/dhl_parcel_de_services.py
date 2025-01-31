# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


# VISUAL_CHECK_OF_AGE = [
#     ('A16', 'A16'),
#     ('A18', 'A18'),]

ENDORSEMENT = [
    ('RETURN', 'RETURN'),
    ('ABANDON', 'ABANDON')
]

EXPORT_TYPE = [
    ('OTHER', 'OTHER'),
    ('PRESENT', 'PRESENT'),
    ('COMMERCIAL_SAMPLE', 'COMMERCIAL_SAMPLE'),
    ('DOCUMENT', 'DOCUMENT'),
    ('RETURN_OF_GOODS', 'RETURN_OF_GOODS'),
    ('COMMERCIAL_GOODS', 'COMMERCIAL_GOODS'),
]

SHIPPING_CONDITIONS = [
    ('DAP', 'DAP'),
    ('DDP', 'DDP'),
    ('DDX', 'DDX'),
    ('DXV', 'DXV'),
]


DIMENSION_UOM = [
    ('cm', 'CM'),
    ('mm', 'MM'),
]

LABEL_FORMAT = [
    ('PDF', 'PDF'),
    ('ZPL2', 'ZPL2'),
]

LABEL_SIZE = [
    ('A4', 'A4'),
    ('910-300-700', '(sheet A5) 105x208mm (910-300-700)'),
    ('910-300-700-oz', '(sheet A5) 105x208mm, without additional labels (910-300-700)'),
    ('910-300-710', '105x209mm (910-300-710)'),
    ('910-300-600', '(folding tape labels) 103x199mm (910-300-600)'),
    ('910-300-610', '(roll) 103x199mm (910-300-600)'),
    ('910-300-400', '(folding tape labels) 103x150mm (910-300-400)'),
    ('910-300-410', '(roll) 103x150mm (910-300-410)'),
    ('910-300-300', '(sheet A5) 105x148mm (910-300-300)'),
    ('910-300-300-oz', '(sheet A5) 105x148mm, without additional labels (910-300-300)'),
]


class ProductPackage(models.Model):
    _inherit = 'product.package'
    delivery_type = fields.Selection(
        selection_add=[('dhl_parcel_de', 'DHL Parcel DE')], ondelete={'dhl_parcel_de': 'cascade'}
    )

class ProductPackaging(models.Model):
    _inherit = 'stock.package.type'
    package_carrier_type = fields.Selection(
        selection_add=[('dhl_parcel_de', 'DHL Parcel DE')], ondelete={'dhl_parcel_de': 'cascade'})

    package_base_weight = fields.Float(
        string='Base Package Weight(Kg)',
        default=0.01,
        help="Extra Base Package Weight is added in shipping weight"
    )
    

class ShippingDHLParcelDE(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[('dhl_parcel_de', 'DHL Parcel DE')], ondelete={'dhl_parcel_de': 'set default'})
    dhl_de_ekp_number = fields.Char(string = "EKP Number")
    dhl_de_username = fields.Char(string = "Username")
    dhl_de_password = fields.Char(string = "Password")
    dhl_de_api_key = fields.Char(string = "DHL API Key")
    dhl_de_contract_participation = fields.Char(string = "DHL Contract Participation Number", default="01")
    dhl_de_price_rule_ids = fields.One2many('dhl.parcel.de.price.rule', 'carrier_id', string='DHL Pricing Rules', copy=True)
    dhl_de_product_id = fields.Many2one('dhl.parcel.de.product', string='DHL Parcel-DE Product')
    endorsement = fields.Selection(selection = ENDORSEMENT, string = "Endorsement", default="RETURN")
    is_cod = fields.Boolean(string="Is COD", default=False)
    dhl_de_accountRef = fields.Char(string = "Account Reference")
    is_international = fields.Boolean(string = 'Is International')
    export_type = fields.Selection(selection = EXPORT_TYPE, string = "Export Type", default="COMMERCIAL_GOODS")
    export_description = fields.Char(string = "Export Description")
    shipping_conditions = fields.Selection(selection = SHIPPING_CONDITIONS, string = "Shipping Conditions", default="DAP", required=True)

    dimensions_uom = fields.Selection(selection = DIMENSION_UOM, string = "Dimensions UOM", default="cm")
    docFormat = fields.Selection(selection = LABEL_FORMAT, string = "Doc Format", required=True, default="PDF")
    label_size = fields.Selection(selection = LABEL_SIZE, string = "Label Size", required=True, default="910-300-710")


class DHLParcelDEProduct(models.Model):
    _name = "dhl.parcel.de.product"
    _description = 'DHL Parcel DE Products'

    name = fields.Char(string = 'Name', required=True)
    code = fields.Char(string = 'Code', required=True)
    # contract_procedure = fields.Char(string = 'Contract Procedure', required=True)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dhl_de_order_id = fields.Many2one("dhl.parcel.de.order", string="DHL DE Orders", copy= False)
    dhl_de_manifest_id = fields.Many2one('dhl.parcel.de.manifest' , string="DHL DE Manifest", copy= False)
    international_ship_no = fields.Char(string="International Shipment Number", copy= False)


    def get_all_wk_carriers(self):
        res = super(StockPicking, self).get_all_wk_carriers()
        res.append('dhl_parcel_de')
        return res
    
