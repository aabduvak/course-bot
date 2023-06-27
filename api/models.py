from typing import Any
from django.db import models

# Create your models here.

class BaseModel(models.Model):
	date_created = models.DateTimeField(auto_now_add=True)
	date_updated = models.DateTimeField(auto_now=True)

class User(BaseModel):
	username = models.CharField(max_length=255, null=True, blank=True)
	first_name = models.CharField(max_length=255)
	last_name = models.CharField(max_length=255, null=True, blank=True)
	chat_id = models.BigIntegerField(unique=True)
	photo = models.ImageField(upload_to='users', null=True, blank=True)
	phone = models.CharField(max_length=15, null=True, blank=True)
	link = models.URLField(null=True, blank=True)
	telegram_id = models.CharField(max_length=255, null=True, blank=True)
	bitrix_id = models.CharField(max_length=255, null=True, blank=True)
	
	def full_name(self):
		if self.last_name:
			return f'{self.first_name} {self.last_name}'
		return self.first_name
	
	def __str__(self):
		if self.username:
			return f'{self.first_name} | {self.username}'	
		return f'{self.first_name} | {self.chat_id}'

class Content(BaseModel):
	title = models.CharField(max_length=150)
	description = models.TextField()
	
	def __str__(self):
		return self.title

class Message(BaseModel):
	sender = models.ForeignKey(User, related_name="messages", on_delete=models.CASCADE)
	text = models.TextField()
	

class Button(BaseModel):
	text = models.CharField(max_length=50)
	parent = models.ForeignKey(Content, related_name="buttons", on_delete=models.CASCADE)
	
	def __str__(self):
		return f'{self.text} | {self.parent}'

class Lead(BaseModel):
	contact = models.ForeignKey(User, related_name="lead", on_delete=models.CASCADE)
	lead_id = models.IntegerField()
	state_id = models.CharField(max_length=100, null=True, blank=True)
	link = models.URLField(null=True, blank=True)
	
	def __str__(self):
		return f'{self.contact.first_name} {self.contact.last_name} #{self.lead_id}'

class Section(BaseModel):
	name = models.CharField(max_length=150)
	section_id = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return self.name

class Product(BaseModel):
	price = models.IntegerField()
	name = models.CharField(max_length=200)
	description = models.TextField(null=True, blank=True)
	section_id = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, null=True)
	photo = models.ImageField(null=True, blank=True, upload_to='product')
	product_id = models.IntegerField(null=True, blank=True)
	link = models.URLField(null=True, blank=True)
	
	def __str__(self):
		return f'{self.name} | {self.product_id}'
	

class Deal(BaseModel):
	contact = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deal")
	lead_id = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead', null=True, blank=True)
	stage_id = models.CharField(max_length=100, blank=True, null=True)
	deal_id = models.IntegerField()
	products = models.ForeignKey(Product, related_name="products", on_delete=models.SET_NULL, null=True, blank=True)
	is_paid = models.BooleanField(default=False)
		
	def __str__(self):
		return f'{self.contact.first_name} {self.contact.last_name} #{self.deal_id}'
