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


class DHLParcelDEOrders(models.Model):
    _name = 'dhl.parcel.de.order'
    _description = 'DHL Parcel DE Orders'

    name = fields.Char(string="Order Reference")
    shipment_numbers = fields.Char(string="Shipment Numbers")
    to_be_menifested = fields.Boolean(string="Is Manifest", default=False)
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    picking_id = fields.Many2one("stock.picking", string="Picking")


class DHLParcelDEOrders(models.Model):
    _name = 'dhl.parcel.de.manifest'
    _description = 'DHL Parcel DE Manifests'

    _inherit = ['mail.thread']

    name = fields.Char(
        'Manifest Reference',
        default=lambda self: self.env['ir.sequence'].next_by_code('dhl.parcel.de.manifest') or _('New'),
        )

    picking_ids = fields.One2many('stock.picking', 'dhl_de_manifest_id', string='Pickings')
    manifest_tracking_ref = fields.Text('Tracking Reference')

    def _get_menifest_payload(self, orders):
        ship_no = [] 
        for order in orders:
            ship_no.extend(order.shipment_numbers.split(","))
        return {
            'profile' : 'STANDARD_GRUPPENPROFIL',
            'shipmentNumbers' : ship_no
        }
    
    def map_pickings(self, orders, manifest_id):
        for order in orders:
            picking_id = order.picking_id
            picking_id.dhl_de_manifest_id = manifest_id.id
        return True
    
    
    def save_manifests(self, items, orders):
        shipment_numbers = [rec.get('shipmentNo') for rec in items if rec.get('sstatus', {}).get('statusCode') == 200]

        vals = {
            'manifest_tracking_ref' : ",".join(shipment_numbers)
        }
        manifest_id = self.create(vals)
        self.map_pickings(orders, manifest_id)
        orders.write({'to_be_menifested' : False})
        return {'manifest_id' : manifest_id}

    def cron_create_dhl_de_manifest(self):
        delivery_ids = self.env['delivery.carrier'].search([('delivery_type', '=', 'dhl_parcel_de')])

        all_orders = self.env['dhl.parcel.de.order'].search([
            ('to_be_menifested', '=', True),
            ('carrier_id', 'in', delivery_ids.ids)
        ])

        if not all_orders:
            raise UserError("No Order found to Create Manifest !!")

        for rec in delivery_ids:

            orders = all_orders.filtered(lambda order: order.carrier_id == rec)
            if orders:
                config = rec.wk_get_carrier_settings(['dhl_de_username', 'dhl_de_password', 'dhl_de_api_key', 'dhl_de_ekp_number', 'prod_environment', 'dhl_de_contract_participation'])
                config['dhl_de_enviroment'] = 'production' if config['prod_environment'] else 'test'
                sdk = dhl_api.DHLParcelDE(**config)

                payload = self._get_menifest_payload(orders)
                path = "/manifests"
                response = sdk.send_request(request_body=payload, path=path, request_for="manifests")
                if response.get('success'):
                    create_manifest_rec = self.save_manifests(response.get('root').get('items'), orders)
                    taday_date = date.today().strftime("%Y-%m-%d")
                    all_manifests_res = sdk.get_today_manifests(path='/manifests?date=' + str(taday_date))

                    if not all_manifests_res.get('success'):
                        _logger.info(f"#WKERROR ---DHL Parcel DE Exception Get today manifests----- {all_manifests_res.get('error_message')} ------")
                    
                    if all_manifests_res.get('success'):
                        manifest_b64_lst = all_manifests_res.get('root').get('manifest')

                        my_attachments_ids = []
                        for i, data in enumerate(manifest_b64_lst):
                            b64_val = data.get('b64')
                            fileFormat = data.get("fileFormat").lower()
                            my_attachment = self.env['ir.attachment'].create({
                                'datas': b64_val,
                                'name' : 'dhl-de-manifest--' + str(i) + '.' + fileFormat,
                                'res_model': 'dhl.parcel.de.manifest',
                                'res_id': create_manifest_rec['manifest_id'].id,
                            })
                            my_attachments_ids.append(my_attachment.id)

                        items = all_manifests_res.get('root').get('items')

                        shipmentNos = []

                        for item in items:
                            shipmentNos.append(item.get('shipmentNo'))

                        create_manifest_rec['manifest_id'].message_post(    
                            body=f'Order Finalized for DHL Parcel DE with Shipment Numbers {",".join(shipmentNos)}',
                            subject="Attachments",
                            attachment_ids=my_attachments_ids
                        )
