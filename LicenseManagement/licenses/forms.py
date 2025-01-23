from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, CompilationRequest, Ticket, TicketMessage, Receipt, CustomerProfile, CartItem
from django.utils import timezone
from django.forms import inlineformset_factory
from .models import Product


from .models import CartItem

class AddToCartForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']

from django_ckeditor_5.widgets import CKEditor5Widget

class CustomerProfileForm(forms.ModelForm):
	class Meta:
		model = CustomerProfile
		fields = [
			'account_number', 'referrer', 'referral_link', 'phone_number', 
			'daily_drawdown', 'daily_trade_limit', 'daily_profit_limit', 
			'monthly_drawdown', 'monthly_profit_limit', 'trade_delays', 
			'update_periodic_limit', 'timezone'
		]
		'''
		fields += [i + '_remaining_1' for i in [
			'daily_drawdown', 'daily_trade_limit', 'daily_profit_limit', 
			'monthly_drawdown', 'monthly_profit_limit', 'trade_delays'
		]]
		fields += [i + '_remaining_2' for i in [
			'daily_drawdown', 'daily_trade_limit', 'daily_profit_limit', 
			'monthly_drawdown', 'monthly_profit_limit', 'trade_delays'
		]]
		'''
	def __init__(self, *args, **kwargs):
		exclude_fields = kwargs.pop('exclude_fields', [])
		super(CustomerProfileForm, self).__init__(*args, **kwargs)
		for field in exclude_fields:
			if field in self.fields:
				del self.fields[field]

	def save(self, commit=True):
		instance = super(CustomerProfileForm, self).save(commit=False)
		
		# Update remaining values
		if commit:
			instance.daily_drawdown_remaining_1 = self.cleaned_data['daily_drawdown']
			instance.daily_trade_limit_remaining_1 = self.cleaned_data['daily_trade_limit']
			instance.daily_profit_limit_remaining_1 = self.cleaned_data['daily_profit_limit']
			instance.monthly_drawdown_remaining_1 = self.cleaned_data['monthly_drawdown']
			instance.monthly_profit_limit_remaining_1 = self.cleaned_data['monthly_profit_limit']
			instance.trade_delays_remaining_1 = self.cleaned_data['trade_delays']
			instance.save()
		
		return instance

class UserRegisterForm(UserCreationForm):
	email = forms.EmailField()
	referrer = forms.CharField(max_length=100, required=False)
	account_number = forms.CharField(max_length=100, required=False)
	phone_number = forms.CharField(max_length=100, required=True)
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2', 'referrer', 'phone_number']

class ProductForm(forms.ModelForm):
    features = forms.JSONField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Product
        fields = ['name', 'persian_name', 'image', 'description', 'price', 'payment_link', 'features']
        widgets = {
            "description": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="extends"
            )
        }




class CompilationRequestForm(forms.ModelForm):
	class Meta:
		model = CompilationRequest
		fields = ['executable', 'expiry_date']




class TicketForm(forms.ModelForm):
	class Meta:
		model = Ticket
		fields = ['topic', 'priority', 'message', 'attachments']
		

class TicketResponseForm(forms.ModelForm):
	class Meta:
		model = TicketMessage
		fields = ['message', 'attachments']
		
class ReceiptUploadForm(forms.ModelForm):
	class Meta:
		model = Receipt
		fields = ['receipt_image']


