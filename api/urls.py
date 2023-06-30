from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import *

router = SimpleRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'contents', UserViewSet, basename='contents')

urlpatterns = [
    path('', include(router.urls)),
    path('getuser/', GetUser.as_view(), name='get_user'),
    path('getcontent/', GetContent.as_view(), name='get_content'),
    path('createlead/', CreateLead.as_view(), name='create_lead'),
    path('updatelead/', UpdateLead.as_view(), name='update_lead'),
    path('storeuser/', StoreUser.as_view(), name='store_user'),
    path('getproducts/', GetFilteredProducts.as_view(), name='get_products'),
    path('productdetails/', GetProductDetails.as_view(), name='get_product'),
    path('createdeal/', CreateDeal.as_view(), name='create_deal'),
    path('sendfile/', SendFile.as_view(), name='sendfile'),
    path('getdeal/', GetDeal.as_view(), name='get_deal'),
    path('sendmessage/', SendMessage.as_view(), name='send')
]
