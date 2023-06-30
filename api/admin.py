from django.contrib import admin
from .models import User, Message, Content, Button, Section, Product, Deal
# Register your models here.

admin.site.register(User)
admin.site.register(Message)
admin.site.register(Content)
admin.site.register(Button)
admin.site.register(Section)
admin.site.register(Product)
admin.site.register(Deal)