import requests
from django.conf import settings
import json
import uuid
import base64

class Bitrix:
    BASE_URL = ''
    
    def call(self, operation, params=None, isPost=False):
        URL = f'{self.BASE_URL}/{operation}.json'
        
        if params and isPost:
            res = requests.post(URL, json=params).json()
            return res
        
        if params and not isPost:
            res = requests.get(URL, params=params).json()
            return res
        
        res = requests.get(URL).json()
        return res
    
    def get_customer_by_deal(self, id):
        
        if not id:
            return None

        reg = None

        deal = self.get_deal(id)

        contact =  self.call('crm.contact.get', params={'ID': deal['CONTACT_ID']})['result']

        data = {
            "result": {
                'bx_id': contact["ID"],
                'first_name': contact["NAME"],
                'last_name': contact["LAST_NAME"],
                'phone': contact["PHONE"][0]["VALUE"],
                'region': reg
            }
        }

        return data

    def get_employee_by_deal(self, id):
        
        if not id:
            return None

        deal = self.get_deal(id)

        employee = self.call('user.get', params={'ID': deal['CREATED_BY_ID']})['result'][0]

        data = {
            "result": {
                'id': employee["ID"],
                'first_name': employee["NAME"],
                'last_name': employee["LAST_NAME"],
                'email': employee["EMAIL"],
                'type': employee["USER_TYPE"],
                'created_date': deal["DATE_CREATE"],
            }
        }

        return data

    def get_deal(self, id):
        
        if not id:
            return None
        data = self.call('crm.deal.get', params={'ID': id})['result']
        return data

    def get_product_id(self, id):
        if not id:
            return None
        
        product = self.call('crm.product.get', params={'ID': id})['result']

        ID = product['PROPERTY_117']['value']

        return ID

    def get_products(self, id):
        if not id:
            return None

        products = self.call('crm.deal.productrows.get', params={'ID': id})['result']
        
        data = {
            'products': [],
        }
        
        total = 0
        
        for product in products:
            
            detail = {
                'id': self.get_product_id(product['PRODUCT_ID']),
                'title': product['PRODUCT_NAME'],
                'description': product['PRODUCT_DESCRIPTION'],
                'price': product['PRICE'],
                'quantity': product['QUANTITY']
            }
            
            total += product['PRICE'] * product['QUANTITY']
            data['products'].append(detail)
        
        data['total'] = total
        
        return data
    
    def get_product(self, id):
        if not id:
            return None

        product = self.call('crm.product.get', params={'ID': id})['result']
        
        return product
    
    def create_customer(self, user):
        if user is None:
            return None
        
        
        fields = {
            'fields': {
                'NAME': user['first_name'],
                'OPENED': 'Y',
                'TYPE_ID': 'CLIENT',
                'ASSIGNED_BY_ID': '90',
                "PHONE": [ { "VALUE": user['phone'], "VALUE_TYPE": "WORK" } ]
            },
            'params': { "REGISTER_SONET_EVENT": "Y" }
        }
        
        if 'last_name' in user:
            fields['fields']['LAST_NAME'] = user['last_name']
        res = self.call("crm.contact.add", fields, True)['result']
        
        return res

    def create_lead(self, user):
        if user is None:
            return None
        
        fields = {
            'fields': {
                'TITLE': f"{user.first_name} {user.last_name}",
                'NAME': user.first_name,
                'LAST_NAME': user.last_name,
                'OPENED': 'Y',
                'STATUS_ID': 'PROCESSED',
                'ASSIGNED_BY_ID': '90',
                'CONTACT_ID': user.bitrix_id,
                "PHONE": [ { "VALUE": user.phone, "VALUE_TYPE": "WORK" } ]
            },
            'params': { "REGISTER_SONET_EVENT": "Y" }
        }
        
        res = self.call("crm.lead.add", fields, True)['result']
        
        return res

    def get_product_list(self, filter):
        
        data = {
            'filter': {
                'SECTION_ID': filter['section']
            }
        }
        
        products = self.call("crm.product.list", data, True)['result']
        
        result = {
            'items': []
        }
        
        for item in products:
            product = self.get_product(item['ID'])
            detail = {
                'name': product['NAME'],
                'description': product['DESCRIPTION'],
                'link': product['PROPERTY_146']['value'],
                'price': int(product['PRICE'].split('.')[0]),
                'id': int(product['ID'])
            }
            
            result['items'].append(detail)
        
        return result
    
    def create_deal(self, data):        
        fields = {
            'fields': {
                'OPENED': 'Y',
                'STAGE_ID': 'NEW',
                'ASSIGNED_BY_ID': '90',
                'CURRENCY_ID': 'UZS'
            },
            'params': { "REGISTER_SONET_EVENT": "Y" }
        }
        
        res = self.call('crm.deal.add', fields, True)['result']
        return res

    def set_customer_to_deal(self, customer_id, deal_id):
        if customer_id is None or deal_id is None:
            return None
        
        fields = {
            'id': deal_id,
            'fields': {
                'CONTACT_ID': customer_id
            }
        }
        
        return self.call('crm.deal.contact.add', fields, True)
        
    def set_product_to_deal(self, products, deal_id):
        if deal_id is None or products is None:
            return None
        
        fields = {
            'id': deal_id,
            'rows': []
        }
        
        for product in products:
            detail = {
                'PRODUCT_ID': product.product_id,
                'PRICE': product.price,
                'QUANTITY': 1
            }
            
            fields['rows'].append(detail)
        
        res = self.call('crm.deal.productrows.set', fields, True)        
        return res
    
    def update_deal(self, data, id, field):
        
        if not id or not data:
            return None
        
        fields = {
            'id': id,
            'fields': {
                field: data
            },
            'params': { "REGISTER_SONET_EVENT": "Y" }
        }
        
        res = self.call("crm.deal.update", fields, True)['result']
        return res
    
    
    
    def __init__(self):
        self.BASE_URL = f'{settings.BITRIX_DOMAIN}/rest/{settings.BITRIX_USER}/{settings.BITRIX_SECRET_KEY}'
