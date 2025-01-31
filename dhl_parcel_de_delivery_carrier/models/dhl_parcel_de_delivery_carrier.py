# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models
import base64
import logging

from . import dhl_api

try:
    import pycountry
except Exception as e:
    raise UserError("Please install pycountry: pip3 install pycountry")



_logger = logging.getLogger(__name__)

receiver_ids = {
    'BE': 'bel',
    'BG': 'bgr',
    'DK': 'dna',
    'DE': 'itg',
    'EE': 'east',
    'FI': 'fin',
    'FR': 'from',
    'GR': 'grc',
    'GB': 'gbr',
    'IE': 'irl',
    'IT': 'ita',
    'HR': 'hrv',
    'LV': 'lion',
    'LT': 'ltu',
    'LU': 'lux',
    'MT': 'mlt',
    'NL': 'nld',
    'AT': 'aut',
    'PL': 'pol',
    'PT': 'prt',
    'RO': 'rou',
    'SE': 'swe',
    'CH': 'that',
    'SK': 'svk',
    'SI': 'svn',
    'ES': 'esp',
    'CZ': 'jun',
    'HU': 'she',
    'CY': 'cyp',
}

# validate length of string
def validate_length(field=None, value=None, flag=False, max_val=None, min_val=None):
    value = value or ''
    flag = True if min_val<=len(value)<=max_val else False
    msg = f'length of {field} should be between {min_val} and {max_val}.\nValue : {value or None}'
    if not flag:
        raise ValidationError(msg)
    else:
        return value


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def _compute_can_generate_return(self):
        for carrier in self:
            carrier.can_generate_return = True
            carrier.return_label_on_delivery = True
            carrier.get_return_label_from_portal = True

    def _get_delivery_amount(self, order):
        delivery_lines = order.order_line.filtered('is_delivery')
        dhl_de_delivery_amount = sum(delivery_lines.mapped('price_total')) if not order.amount_delivery else order.amount_delivery
        return dhl_de_delivery_amount


    def dhl_parcel_de_rate_shipment(self, order):
        self.wk_validate_object_fields(order.partner_id, ['country_id'])
        receiver_country_code = order.partner_id.country_id.code
        delivery_amount = self._get_delivery_amount(order)
        price = 0
        try:
            if self.dhl_de_price_rule_ids:
                for rule in self.dhl_de_price_rule_ids:
                    if rule.country_id and rule.country_id.code == receiver_country_code:
                        if rule.free_over and (order.amount_total - delivery_amount) >= rule.free_over_amount:
                            price = 0
                        else:
                            price = rule.delivery_price*rule.list_price if rule.variable_factor and rule.list_price>0 else rule.delivery_price
                        break
            _logger.info("====delivery price is %r ====" %price)
            return {
                'success': True,
                'price': price,
                'error_message': False,
                'warning_message': False
            }
        except Exception as e:
            _logger.warning("==== DHL Parcel DE Rate Shipment Exception == %r------------ ====" %e)
            raise UserError(e)

    def _remove_words(self, full_string):
        if len(full_string) <= 50:
            return full_string
        new_string_ar = full_string.split(' ')[0:-1]
        new_string=" ".join(new_string_ar)
        return self._remove_words(new_string)
    
    def _format_dhl_parcel_de_name(self, data):
        tempLine1 = data.get('name')
        tempLine2 = ''
        name3 = ''
        if len(tempLine1) >= 50:
            name1 = self._remove_words(tempLine1)
            tempLine2 = tempLine1[len(name1)+1:] + " " + tempLine2
        else:
            name1 = tempLine1
        if len(tempLine2) >= 50:
            name2 = self._remove_words(tempLine2)
            tempLine3 = tempLine2[len(name2)+1:]
            name3 = self._remove_words(tempLine3)
        else:
            name2 = tempLine2

        return (name1, name2, name3)

    def _alpha2_to_alpha3(self, alpha2_code):
        try:
            country = pycountry.countries.get(alpha_2=alpha2_code.upper())
            if country:
                return country.alpha_3
            else:
                raise ValidationError('Invalid alpha2 {0}'.format(alpha2_code))
        except Exception as e:
            return UserError(f"Error to convert alpha2 to alpha3: {e}")
    
    def _construct_dhl_de_address(self, address, type):
        names = self._format_dhl_parcel_de_name(address)
        data = {
            'name1' : names[0],
            'addressStreet' : validate_length(field=f'{names[0]} Street', value=address.get('street'), min_val=1, max_val=50),
            'postalCode' : validate_length(field=f'{names[0]} Postal Code', value=address.get('zip'), min_val=3, max_val=10),
            'city' : validate_length(field=f'{names[0]} City', value=address.get('city'), min_val=1, max_val=40),
        }
        if names[1]:
            data.update({'name2' : names[1]})
        if names[2]:
            data.update({'name3' : names[2]})
        if address.get('state_code') and not type == 'return':
            data.update({'state' : validate_length(field=f'{names[0]} State', value=address.get('state_code'), min_val=1, max_val=20)})
        if address.get('phone'):
            data.update({'phone' : validate_length(field=f'{names[0]} Phone', value=address.get('phone'), min_val=1, max_val=20)})
        if address.get('email'):
            data.update({'email' : validate_length(field=f'{names[0]} Email', value=address.get('email'), min_val=3, max_val=80)})
        if type == "shipment":
            data.update({'country' : self._alpha2_to_alpha3(address.get('country_code'))})
        return data
    
    def _get_dhl_parcel_de_package(self, package):
        package_weight =  package.shipping_weight + package.package_type_id.package_base_weight
        weight = self._get_api_weight(package_weight)
        package = {
            'dim': {
                'uom' : self.dimensions_uom,
                'height': package.height,
                'length': package.length,
                'width': package.width,
            },
            "weight": {
                "uom": self.uom_id.name,
                "value": round(weight, 2) if not self.uom_id.name == 'g' else int(weight)
			}
        }
        return package
    
    def get_item_wt_and_val(self, weight, value, currency_code):
        item_wt = self._get_api_weight(weight)
        data = {
                "itemValue" : { 
                    "currency": currency_code,
                    "value": round(value, 2)
                },
                "itemWeight" : {
                    "uom" : self.uom_id.name,
                    "value" : round(item_wt, 2) if not self.uom_id.name == 'g' else int(item_wt)
                }
            }
        return data

    def _get_product_price(self, sale_id, qty, product_id):
        product_price = next((order_line.price_unit for order_line in sale_id.order_line if order_line.product_id.id == product_id.id), product_id.lst_price * qty)
        return product_price
    
    def _get_return_items_wt_and_val(self, currency_code, picking):
        total_price = 0
        for move_line in picking.move_line_ids:
            total_price += self._get_product_price(picking.sale_id, move_line.quantity, move_line.product_id)
        shipping_weight = sum(picking.package_ids.mapped('shipping_weight'))
        return self.get_item_wt_and_val(shipping_weight, total_price, currency_code)


    def _get_custom_product_data(self, sale_id, product_id, qty, currency_code, product_for):
        product_price = self._get_product_price(sale_id, qty, product_id)
        product_data = dict(
            itemDescription = product_id.name,
            packagedQuantity = int(qty),
            countryOfOrigin = self._alpha2_to_alpha3(product_id.country_of_origin.code),
        )
        if product_id.hs_code:
            product_data.update(hsCode=product_id.hs_code)
        weight = product_id.weight*qty if product_for == 'return' else product_id.weight
        item_wt_and_val = self.get_item_wt_and_val(weight, product_price, currency_code)
        product_data.update(item_wt_and_val)
        return product_data

    def _get_dhl_de_custom_detail(self, picking, currency_code, package):
        customs = {}
        items = []
        for record in package.quant_ids:
            if not record.product_id.country_of_origin:
                raise ValidationError (f"Country of origin not defined for product : {record.product_id.name}.")
            items.append(self._get_custom_product_data(picking.sale_id, record.product_id, record.quantity, currency_code, product_for='ship'))
        customs.update(
            invoiceNo = picking.name,
            exportType=self.export_type,
            hasElectronicExportNotification=True,
            postalCharges={
                'currency' : currency_code,
                'value' : 0.0 if not picking.sale_id else self._get_delivery_amount(picking.sale_id)
            },
            officeOfOrigin=self._alpha2_to_alpha3(picking.company_id.country_id.code),
            items=items
        )
        if self.dhl_de_product_id.code == 'V54EPAK':
            customs.update(shippingConditions=self.shipping_conditions)
        if self.export_type == 'OTHER':
            export_desc = validate_length(field='Export Description', value=self.export_description, min_val=0, max_val=80),
            customs.update(exportDescription=export_desc)
        return customs
    
    def _get_dhl_de_return_custom_detail(self, currency_code, picking):
        return_items = []
        for record in picking.move_line_ids:
            if not record.product_id.country_of_origin:
                raise UserError (f"Country of origin not defined for product : {record.product_id.name}.")
            product_data = self._get_custom_product_data(picking.sale_id, record.product_id, record.quantity, currency_code, product_for='return')
            return_items.append(product_data)
        return return_items


    def dhl_de_construct_ship_request(self, picking, currency_code):
        receiver = picking.partner_id
        self.wk_validate_object_fields(receiver, ['country_id', 'city', 'zip', 'street'])
        shipper = picking.picking_type_id.warehouse_id.partner_id
        self.wk_validate_object_fields(shipper, ['country_id', 'city', 'zip', 'street'])
        shipper_data = self.get_shipment_shipper_address(order=None, picking=picking)
        recipient_data = self.get_shipment_recipient_address(order=None, picking=picking)
        shipments = []
        for package in picking.package_ids:
            contract_procedure = self.dhl_de_product_id.code[1:3] if self.dhl_de_product_id else ''
            contract_participation = self.dhl_de_contract_participation if self.dhl_de_contract_participation else ''
            payload = {
                'product' : self.dhl_de_product_id.code,
                'billingNumber' : self.dhl_de_ekp_number+contract_procedure+contract_participation,
                'refNo' : picking.name,
                'shipDate' : picking.scheduled_date.strftime('%Y-%m-%d'),
                'shipper' : self._construct_dhl_de_address(shipper_data, type="shipment"),
                'consignee' : self._construct_dhl_de_address(recipient_data, type="shipment"),
                'details' : self._get_dhl_parcel_de_package(package),
                'services' : {
                    'endorsement' : self.endorsement,
                }
            }
            if self.is_international:
                custom_detail = self._get_dhl_de_custom_detail(picking, currency_code, package)
                payload.update(customs=custom_detail)
            shipments.append(payload)
        
        return {
            'profile' : 'STANDARD_GRUPPENPROFIL',
            'shipments' : shipments
        }

    @api.model
    def dhl_parcel_de_send_shipping(self, pickings):
        result = {'exact_price': 0, 'weight': 0, "date_delivery": None,
                'tracking_number': '', 'attachments': []}
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name
        config = self.wk_get_carrier_settings(
            ['dhl_de_username', 'dhl_de_password', 'dhl_de_ekp_number', 'dhl_de_api_key', 'prod_environment', 'dhl_de_contract_participation'])
        config['dhl_de_enviroment'] = 'production' if config['prod_environment'] else 'test'
        sdk = dhl_api.DHLParcelDE(**config)
        ship_req = self.dhl_de_construct_ship_request(picking=pickings, currency_code=currency_code)
        path = f"/orders?docFormat={self.docFormat}&printFormat={self.label_size}"
        
        response = sdk.send_request(request_body=ship_req, path=path, request_for="ship")
        if not response.get('success'):
            raise ValidationError(response.get('error_message'))
        res_items = response.get('root').get('items')

        tracking_numbers = []
        attachments = []
        for item in res_items:
            tracking_numbers.append(item.get('shipmentNo'))
            lable_data = item.get('label').get('b64')
            customsDoc = item.get('customsDoc')
            file_ext = item.get('label').get('fileFormat').lower()
            attachments.append(('dhl_parcel_de_' + item.get('shipmentNo')+ '.' + file_ext, base64.b64decode(lable_data)))
            if customsDoc:
                attachments.append(('custom_doc_' + item.get('shipmentNo')+ '.' + file_ext, base64.b64decode(customsDoc.get('b64'))))

        result['tracking_number'] = ','.join(tracking_numbers)
        result['attachments'] = attachments

        order = self.env['dhl.parcel.de.order'].create({
            'name' : pickings.name,
            'shipment_numbers' : ','.join(tracking_numbers),
            'to_be_menifested' : True,
            'carrier_id' : self.id,
            'picking_id' : pickings.id
        })
        pickings.dhl_de_order_id = order.id
        return result

    @api.model
    def dhl_parcel_de_get_tracking_link(self, picking):
        return dhl_api.DHLParcelDE.get_tracking_link(tracknum=picking.carrier_tracking_ref)  


    def _construct_return_request(self, currency_code, sdk, picking):
        shipper_data = self.get_shipment_shipper_address(order=None, picking=picking)
        recipient_data = self.get_shipment_recipient_address(order=None, picking=picking)
        wt_and_val = self._get_return_items_wt_and_val(currency_code, picking)
        receiverId = receiver_ids.get(recipient_data.get("country_code"))
        if self.prod_environment:
            country_code = self._alpha2_to_alpha3(recipient_data.get('country_code')).lower()
            path = f"/locations?countryCode={country_code}&maxResult=1"
            response = sdk.get_return_receiver_ids(path=path)
            if not response.get('success'):
                raise ValidationError(response.get('error_message'))
            root = response.get('root')
            receiverId = root[0].get('receiverId', '')

        payload = {
            "receiverId" : receiverId,
            "customerReference" : picking.name,
            "shipmentReference" : picking.name,
            "shipper" : self._construct_dhl_de_address(recipient_data, type="return"),
            "itemWeight" : wt_and_val.get('itemWeight'),
            "itemValue" : wt_and_val.get('itemValue'),
            "customsDetails" : {
                "items" : self._get_dhl_de_return_custom_detail(currency_code, picking)
            }
        }
        return payload


    @api.model
    def dhl_parcel_de_get_return_label(self, pickings, tracking_number, origin_date):
        result = {'exact_price': 0, 'weight': 0, "date_delivery": None,
                  'tracking_number': '', 'attachments': []}
        currency_id = self.get_shipment_currency_id(pickings=pickings)
        currency_code = currency_id.name
        config = self.wk_get_carrier_settings(
            ['dhl_de_username', 'dhl_de_password', 'dhl_de_ekp_number', 'dhl_de_api_key', 'prod_environment', 'dhl_de_contract_participation'])
        config['dhl_de_enviroment'] = 'production' if config['prod_environment'] else 'test'
        sdk = dhl_api.DHLParcelDE(**config)
        req_body = self._construct_return_request(currency_code, sdk, picking=pickings)
        return_response = sdk.send_request(request_body=req_body, path="/orders", request_for="return")
        if not return_response.get('success'):
            raise ValidationError(return_response.get('error_message'))
        
        res = return_response.get('root')

        pickings.carrier_tracking_ref = res.get('shipmentNo')
        pickings.international_ship_no = res.get('internationalShipmentNo')
        label_data = res.get('label').get('b64')

        msg = ("Return Shipment sent to carrier %s for expedition with tracking number %s") % (
            pickings.carrier_id.delivery_type, pickings.carrier_tracking_ref)

        my_attachments_ids = []
        my_attachment = self.env['ir.attachment'].create({
            'datas': label_data,
            'name': self.get_return_label_prefix() + "-stock_picking_id-" + str(pickings.id) + '.pdf',
            'res_model': 'stock.picking',
            'res_id': pickings.id
        })
        my_attachments_ids.append(my_attachment.id)
        pickings.return_label_ids = my_attachments_ids
        pickings.message_post(
            body=msg,
            subject="Attachments of tracking",
            attachment_ids=my_attachments_ids
        )
        if pickings.carrier_tracking_ref:
            pickings.label_genrated = True
            pickings.state = 'done'


        
