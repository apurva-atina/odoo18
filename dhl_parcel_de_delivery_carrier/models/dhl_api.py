# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    You should have received a copy of the License along with this program.
#    If not, see <https://store.webkul.com/license.html/>
#################################################################################

import requests
import json
import base64
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


dhl_parcel_de_prod_base_url = "https://api-eu.dhl.com/parcel/de/shipping/v2"
dhl_parcel_de_test_base_url = "https://api-sandbox.dhl.com/parcel/de/shipping/v2"

dhl_parcel_de_prod_return_url = "https://api-eu.dhl.com/parcel/de/shipping/returns/v1"
dhl_parcel_de_test_return_url = "https://api-sandbox.dhl.com/parcel/de/shipping/returns/v1"

dhl_parcel_de_tracking_link = "https://www.dhl.com/in-en/home/tracking/tracking-express.html?submit=1&tracking-id="


class DHLParcelDE:

    def __init__(self, *args, **kwargs):
        self.dhl_de_ekp_number  = kwargs.get('dhl_de_ekp_number')
        self.dhl_de_username = kwargs.get('dhl_de_username')
        self.dhl_de_password = kwargs.get('dhl_de_password')
        self.dhl_de_api_key = kwargs.get('dhl_de_api_key')
        self.dhl_de_enviroment = kwargs.get('dhl_de_enviroment', 'test')

    def check_error(self, response, request_for=None):
        status_code = response.status_code
        json_data = response.json()

        if request_for == 'manifests' and status_code in [200, 207]:
            return False

        if status_code in [200, 207, 400]:
            items = json_data.get('items', [])
            
            if items:
                for item in items:
                    if item.get('sstatus', {}).get('statusCode') == 400:
                        return str(items)
            else:
                title = json_data.get('title')
                detail = json_data.get('detail')
                
                if title and detail:
                    return f"{title} : {detail}"
        
        elif status_code in [401, 429, 500, 502, 403, 422]:
            return f"{json_data.get('title')} : {json_data.get('detail')}"

        return False

    @classmethod
    def get_tracking_link(self, tracknum):
        dhl_parcel_de_tracking_url = dhl_parcel_de_tracking_link
        if len(tracknum.split(sep=',')) == 1:
            return dhl_parcel_de_tracking_url + tracknum
        tracking_nums = list(
            map(lambda x: x+"%2C", tracknum.split(sep=',')))
        dhl_parcel_de_tracking_url += ''.join(tracking_nums)
        return dhl_parcel_de_tracking_url


    def get_dhl_parcel_de_header(self):
        auth_string = base64.b64encode("{}:{}".format(self.dhl_de_username, self.dhl_de_password).encode("utf-8")).decode('utf-8')
        header = {
            "content-type": "application/json",
            "Accept-Language": "en-US",
            "dhl-api-key" : self.dhl_de_api_key,
            "Authorization": f"Basic {auth_string}"
        }
        return header


    def send_request(self, request_body, path, request_for):
        try:
            if request_for in ['ship', 'manifests']:
                base_url = dhl_parcel_de_test_base_url if self.dhl_de_enviroment == 'test' else dhl_parcel_de_prod_base_url
                api_end = base_url + path
            else:
                base_url = dhl_parcel_de_test_return_url if self.dhl_de_enviroment == 'test' else dhl_parcel_de_prod_return_url
                # api_end = base_url + path + '?labelType=BOTH'
                api_end = base_url + path
            header = self.get_dhl_parcel_de_header()
            response = requests.post(url=api_end, data=json.dumps(request_body), headers=header)
            error = self.check_error(response, request_for)
            return dict(success=0 if error else 1, error_message=error, root=response.json())
            
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---DHL Parcel DE %r Exception--------------" % (e))
            return dict(success=False, error_message=e)


    def get_today_manifests(self, path):
        try:
            api_end = dhl_parcel_de_test_base_url if self.dhl_de_enviroment == 'test' else dhl_parcel_de_prod_base_url
            header = self.get_dhl_parcel_de_header()
            response = requests.get(url=api_end+path, headers=header)
            error = self.check_error(response)
            return dict(success=0 if error else 1, error_message=error, root=response.json())
            
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---DHL Parcel DE %r Exception--------------" % (e))
            return dict(success=False, error_message=e)


    def get_return_receiver_ids(self, path):
        try:
            base_url = dhl_parcel_de_test_return_url if self.dhl_de_enviroment == 'test' else dhl_parcel_de_prod_return_url
            header = self.get_dhl_parcel_de_header()
            response = requests.get(url=base_url+path, headers=header)
            error = False
            if not response.status_code == 200:
                error = self.check_error(response)
            return dict(success=0 if error else 1, error_message=error, root=response.json())
            
        except Exception as e:
            _logger.warning(
                "#WKDEBUG---DHL Parcel DE %r Exception--------------" % (e))
            return dict(success=False, error_message=e)
