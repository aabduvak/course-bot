from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from bs4 import BeautifulSoup
import requests

from .models import User, Content, Button, Lead, Section, Product, Deal
from .serializers import UserSerializer, ContentSerializer
from .bitrix import Bitrix

bx24 = Bitrix()

class UserViewSet(ModelViewSet):
	serializer_class = UserSerializer
	queryset = User.objects.all()

class ContentViewSet(ModelViewSet):
    serializer_class = ContentSerializer
    queryset = Content.objects.all()

class GetUser(APIView):
    def get(self, request):
        chat_id = request.query_params.get('chat_id')
        
        # Query the User model based on the username
        try:
            user = User.objects.get(chat_id=chat_id)
            return Response({
				'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone
                })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)

class StoreUser(APIView):
    def post(self, request):
        user = request.data.copy()
        
        res = bx24.create_customer(user)
        
        user['bitrix_id'] = res
        current_site = get_current_site(request)
        
        requests.post(f'http://{current_site}/api/users/', data=user)
        
        return Response({'result': 'successfull'}, status=200)

class GetDetail(APIView):
    def post(self, request):
        telegram_id = request.data['telegram_id']
        
        user = User.objects.get(telegram_id=telegram_id)
        
        if Lead.objects.filter(contact__telegram_id=telegram_id).exists():
            return Response({'result': 'already exist'}, status=200) 
               
        res = bx24.create_lead(user)
        
        lead = Lead.objects.create(contact=user, lead_id=res)
        lead.save()
        
        return Response({'result': 'successfull'}, status=200)

class GetContent(APIView):
    def get(self, request):
        title = request.query_params.get('title')
        
        try:
            content = Content.objects.get(title=title)
            buttons = Button.objects.filter(parent=content)
            
            data = {
				'text': content.description,
                'buttons': []
            }
            
            if buttons.count() > 0:
                for button in buttons:
                    data['buttons'].append(button.text)
    
            return Response(data)
        except Content.DoesNotExist:
            return Response({'error': 'Content not found'}, status=404)

class GetFilteredProducts(APIView):
    def get(self, request):
        section = Section.objects.get(name='Courses')
        
        filter = {
            'section': section.section_id,
        }
        
        products = bx24.get_product_list(filter)

        for product in products['items']:
            if not Product.objects.filter(product_id=product['id']).exists():
                Product.objects.create(
                    name=product['name'],
                    price=product['price'],
                    description=remove_html_tags(product['description']),
                    section_id=section,
                    link = product['link']
                ).save()
            else:
                prod = Product.objects.get(product_id=product['id'])
                if prod.name != product['name']:
                    prod.name = product['name']
                if prod.description != remove_html_tags(product['description']):
                    prod.description = remove_html_tags(product['description'])
                if prod.price != product['price']:
                    prod.price = product['price']
                if prod.link != product['link']:
                    prod.link = product['link']
                prod.save()
        return JsonResponse(products, safe=False)

class GetProductDetails(APIView):
    def get(self, request):
        product_id = request.query_params.get('product_id')
        
        try:
            product = Product.objects.get(product_id=product_id)
            return Response({
                'name': product.name,
                'price': product.price,
                'description': product.description,
                'id': product.product_id
            })
        except Product.DoesNotExist:
            return Response({'error': 'product not found'}, status=404)

class CreateDeal(APIView):
    def post(self, request):
        data = request.data
        lead = None
        
        user = User.objects.get(telegram_id=data['telegram_id'])
        product = Product.objects.filter(product_id=data['product_id'])
        
        deal_data = {
            'user': user
        }
        
        if Lead.objects.filter(contact=user).exists():
            lead = Lead.objects.get(contact=user)
            deal_data['lead'] = lead
        
        id = bx24.create_deal(deal_data)
        res = bx24.set_customer_to_deal(user.bitrix_id, id)
        bx24.set_product_to_deal(product, id)
        
        return Response({'result': 'success'}, status=200)

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()