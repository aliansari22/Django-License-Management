from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import json
import numpy as np
import pandas as pd
import os
from django_quill.fields import QuillField
from django.db import models
import secrets
import string


class StringItem(models.Model):
	value = models.CharField(max_length=200)
	expiry_date = models.DateTimeField()

	def is_expired(self):
		return self.expiry_date <= timezone.now()

	def __str__(self):
		return self.value

class PublicMessageList(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	string_items = models.ManyToManyField(StringItem)

	def add_string(self, string, expiry_date):
		string_item = StringItem.objects.create(value=string, expiry_date=expiry_date)
		self.string_items.add(string_item)

	def remove_expired_strings(self):
		expired_items = self.string_items.filter(expiry_date__lte=timezone.now())
		self.string_items.remove(*expired_items)
		expired_items.delete()

	def get_valid_strings(self):
		return [item.value for item in self.string_items.filter(expiry_date__gt=timezone.now())]


class PrivateMessageList(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	string_items = models.ManyToManyField(StringItem)

	def add_string(self, string, expiry_date):
		string_item = StringItem.objects.create(value=string, expiry_date=expiry_date)
		self.string_items.add(string_item)

	def remove_expired_strings(self):
		expired_items = self.string_items.filter(expiry_date__lte=timezone.now())
		self.string_items.remove(*expired_items)
		expired_items.delete()

	def get_valid_strings(self):
		return [item.value for item in self.string_items.filter(expiry_date__gt=timezone.now())]
		

class InboxMessage(models.Model):
	sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
	message = models.TextField()
	sent_at = models.DateTimeField(auto_now_add=True)
	is_read = models.BooleanField(default=False)

	def __str__(self):
		return f"From: {self.sender.username} - To: {self.recipient.username}"






from django_ckeditor_5.fields import CKEditor5Field

from django.db.models import JSONField
class Product(models.Model):
	name = models.CharField(max_length=255)
	persian_name = models.CharField(max_length=255, default='')
	executable = models.FileField(upload_to='executables/', null=True, blank=True)
	price = models.IntegerField()
	payment_link = models.URLField(max_length=200)
	description = CKEditor5Field('Text', config_name='extends')
	image = models.ImageField(upload_to='images/', default='images/default.jpg')
	features = JSONField(default=dict)  # Newly added field for features

	def __str__(self):
		return self.name

class PhoneSubscription(models.Model):
    phone = models.CharField(max_length=15, unique=True)  # Adjust max_length as per your requirement

    def __str__(self):
        return self.phone
        
        
        
class Cart(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f'Cart of {self.user.username}'
	def is_empty(self):
		return len(self.items.all())==0
	def get_total_price(self):
		return sum(item.get_total_price() for item in self.items.all())

class CartItem(models.Model):
	cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f'{self.quantity} of {self.product.name}'

	def get_total_price(self):
		return self.product.price * self.quantity


def generate_random_string(length=12):
	"""Generate a random string of fixed length."""
	characters = string.ascii_letters + string.digits
	return ''.join(secrets.choice(characters) for i in range(length))


def generate_random_digits(length=8):
	"""Generate a random string of fixed length."""
	characters = string.digits
	return ''.join(secrets.choice(characters) for i in range(length))



class CustomerProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	account_number = models.CharField(max_length=100, blank=True, null=True,default='')
	ea_username = models.CharField(max_length=100, blank=True, null=True, default=generate_random_digits)
	ea_password = models.CharField(max_length=100, blank=True, null=True, default=generate_random_string)
	referrer = models.CharField(max_length=100, blank=True, null=True)
	referral_link = models.CharField(max_length=100, blank=True, null=True,default='')
	phone_number = models.CharField(max_length=100, blank=True, null=True, default='')
	timezone = models.CharField(default='Asia/Tehran', max_length=100)  # Add this field
	next_allowed_date = models.CharField(max_length=100)	
	
	daily_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	daily_trade_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	daily_profit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monthly_drawdown = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monthly_profit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	trade_delays = models.IntegerField(default=0)
	update_periodic_limit = models.IntegerField(default=7)
	last_update = models.CharField(max_length=100,default='1970-01-01')
	
	daily_trade_limit_remaining_1 = models.IntegerField(default=0)
	daily_profit_limit_remaining_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monthly_drawdown_remaining_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monthly_profit_limit_remaining_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	trade_delays_remaining_1 = models.IntegerField(default=0)
	daily_drawdown_remaining_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	
	daily_trade_limit_remaining_2 = models.IntegerField(default=0)
	daily_profit_limit_remaining_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monthly_drawdown_remaining_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	monthly_profit_limit_remaining_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	trade_delays_remaining_2 = models.IntegerField(default=0)
	daily_drawdown_remaining_2 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	
	def can_update(self):
		from datetime import timedelta, datetime
		return datetime.fromisoformat(self.last_update) + timedelta(days=self.update_periodic_limit) <= datetime.now()

	
	def __str__(self):
		return self.user.username

class CompilationRequest(models.Model):
	customer = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	account_number = models.CharField(max_length=100)
	expiry_date = models.CharField(max_length=255, blank=True, null=True)
	executable = models.FileField(upload_to='executables/', blank=True, null=True)
	fulfilled = models.BooleanField(default=False)

	def __str__(self):
		return f'{self.customer.username} - {self.product.name}'


class ProductActivation(models.Model):
	customer = models.ForeignKey(User, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	activated = models.BooleanField(default=True)
	url = models.CharField(max_length=255)
	expiry_date = models.CharField(max_length=255)





class APIUsage(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	random_token = models.CharField(max_length=200)

	class Meta:
		unique_together = ('user', 'random_token')

  




########## Tickets ###########
from django.db import models
from django.contrib.auth.models import User

class Ticket(models.Model):
	TOPIC_CHOICES = [
		('general', 'General Inquiry'),
		('technical', 'Technical Support'),
		('billing', 'Billing'),
	]

	PRIORITY_CHOICES = [
		('low', 'Low'),
		('medium', 'Medium'),
		('high', 'High'),
	]

	STATUS_CHOICES = [
		('unread', 'Unread'),
		('read', 'Read'),
		('answered', 'Answered'),
		('closed', 'Closed'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
	priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES)
	message = models.TextField()
	attachments = models.FileField(upload_to='attachments/', blank=True, null=True)
	status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unread')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

class TicketMessage(models.Model):
	ticket = models.ForeignKey(Ticket, related_name='messages', on_delete=models.CASCADE)
	sender = models.ForeignKey(User, on_delete=models.CASCADE)
	message = models.TextField()
	attachments = models.FileField(upload_to='attachments/', blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)


class Receipt(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	receipt_image = models.ImageField(upload_to='receipts/')
	uploaded_at = models.DateTimeField(auto_now_add=True)
	verified = models.BooleanField(default=False)



####### Reports ###########

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import hashlib
import uuid
import pandas as pd
import hashlib
import numpy as np
import pandas as pd
import os
import uuid
from django.db import models
from .utils import *

class Report(models.Model):
	user = models.ForeignKey(User, related_name='reportslist', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	datetime = models.DateTimeField(auto_now_add=True)
	chunks = models.JSONField(default=list)  # Storing chunks as a list of strings
	unique_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)

	def add_chunk(self, chunk):
		# Remove duplicate chunks using hashlib
		chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
		if chunk_hash not in [hashlib.md5(c.encode()).hexdigest() for c in self.chunks]:
			self.chunks.append(chunk)
			self.save()

	def assemble_report(self):
		# Reassemble the chunks into the full report
		return ''.join(self.chunks)


	def get_dataframe(self):
		df = from_string(self.assemble_report())
		return df
		
	def __str__(self):
		return f'Report by {self.user.username} for {self.product.name} on {self.datetime}'

	def get_random_name(self):
		name = ''.join(np.random.choice([str(i) for i in range(10)], size=20).astype('str'))+'.csv'
		return name

	def get_filtered_data(self, col_filter, split_str):
		name = self.get_random_name()
		open(name, 'w').write(self.assemble_report().replace(',End', '').replace(self.unique_id + ',', '').replace(',\n', '\n'))
		df = pd.read_csv(name)
		cols = [i for i in df.columns if col_filter in i.lower()]
		df = df[cols]
		cols = [i.lower().split(split_str)[0].title() for i in cols]
		df.columns = cols
		os.remove(name)
		return df.iloc[0].astype(float).to_dict()

	def get_weekday_winrate(self):
		return self.get_filtered_data('day', 'win')

	def get_weekday_pnl(self):
		return self.get_filtered_data('day', 'pnl')

	def get_weekday_numbers(self):
		return self.get_filtered_data('day', 'num')

	def get_hourly_pnl(self):
		return self.get_filtered_data('h', 'pnl')

	def get_hourly_winrate(self):
		return self.get_filtered_data('h', 'winrate')

	def get_hourly_numbers(self):
		return self.get_filtered_data('h', 'numb')

	
class Order(models.Model):
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='orders', null=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
	amount = models.DecimalField(max_digits=40, decimal_places=2)
	trackId = models.IntegerField(default=0)
	status = models.CharField(max_length=20, choices=[
		('pending', 'Pending'),
		('paid', 'Paid'),
		('failed', 'Failed')
	], default='pending')
	created_at = models.DateTimeField(auto_now_add=True)
	payment_url = models.URLField(blank=True, null=True)
	delivery_status = models.CharField(max_length=20, choices=[
		('not_delivered', 'Not Delivered'),
		('delivered', 'Delivered')
	], default='not_delivered')

	def __str__(self):
		return f"Order {self.id} for {self.product.name}"
