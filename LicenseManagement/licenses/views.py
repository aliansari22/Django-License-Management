from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import pytz
from .models import Product, Receipt, ProductActivation
from .forms import ReceiptUploadForm
from .forms import UserRegisterForm, ProductForm, CompilationRequestForm, TicketForm, TicketResponseForm, AddToCartForm
from .models import Product, CompilationRequest, CustomerProfile, ProductActivation, PublicMessageList, PrivateMessageList, StringItem, InboxMessage, Ticket, TicketMessage, Report, Cart, CartItem, PhoneSubscription
from django.contrib.auth.decorators import user_passes_test
from .models import CustomerProfile
from .forms import CustomerProfileForm
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .cryptomus import CryptomusPaymentGateway
from .models import Product, Order
from django.conf import settings
from .utils import *
import requests 

def is_admin(user):
	return user.is_superuser



# payments/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import numpy as np
from django.contrib import messages

@login_required
def add_to_cart(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	cart, created = Cart.objects.get_or_create(user=request.user)
	if request.method == 'POST':
		form = AddToCartForm(request.POST)
		if form.is_valid():
			quantity = form.cleaned_data['quantity']
			cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
			if not created:
				cart_item.quantity += quantity
			else:
				cart_item.quantity = quantity
			cart_item.save()
			return redirect('product_list')
	else:
		form = AddToCartForm()
	return render(request, 'add_to_cart.html', {'form': form, 'product': product})

@login_required
def view_cart(request):
	cart, created = Cart.objects.get_or_create(user=request.user)
	return render(request, 'view_cart_summary.html', {'cart': cart})

@login_required
def finalize_cart(request):
	cart, created = Cart.objects.get_or_create(user=request.user)
	if request.method == 'POST':
		# Process payment and create order
		return redirect('invoice', cart_id=cart.id)
	return render(request, 'finalize_cart.html', {'cart': cart})

@login_required
def invoice(request, cart_id):
	cart = get_object_or_404(Cart, id=cart_id)
	return render(request, 'invoice.html', {'cart': cart})
	
@login_required
def create_payment(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	
	# Create an order
	order = Order.objects.create(
		product=product,
		user=request.user,
		amount=product.price,
		status='pending'
	)
	
	success_url = request.build_absolute_uri(reverse('verify_payment', args=[order.id]))
	fail_url = request.build_absolute_uri(reverse('payment_fail'))

	gateway = CryptomusPaymentGateway()
	payment_response = gateway.create_payment(str(order.amount), 'USD', order.id, success_url, fail_url)

	if payment_response['status'] == 'success':
		payment_url = payment_response['payment_url']
		order.payment_url = payment_url
		order.save()
		return redirect(payment_url)
	else:
		return render(request, 'payment_error.html', {'error': payment_response['message']})        
	
@login_required
def verify_payment(request, order_id):
	order = get_object_or_404(Order, pk=order_id)
	gateway = CryptomusPaymentGateway()
	
	# Check payment status with Cryptomus
	payment_status = gateway.verify_payment(order.id)
	
	if payment_status['status'] == 'success':
		order.status = 'paid'
		order.save()
		return HttpResponseRedirect(reverse('payment_success') + f'?order_id={order.id}')
	else:
		order.status = 'failed'
		order.save()
		return HttpResponseRedirect(reverse('payment_fail')) 

	
######## MOCK
@login_required
def create_payment(request, product_id):
	product = get_object_or_404(Product, pk=product_id)
	
	# Create an order
	order = Order.objects.create(
		product=product,
		user=request.user,
		amount=product.price,
		status='pending'
	)
	
	success_url = request.build_absolute_uri(reverse('verify_payment', args=[order.id]))
	fail_url = request.build_absolute_uri(reverse('payment_fail'))

	# Simulate payment creation
	payment_response = simulate_payment(str(order.amount), 'USD', order.id, success_url, fail_url)

	if payment_response['status'] == 'success':
		payment_url = payment_response['payment_url']
		order.payment_url = payment_url
		order.save()
		return redirect(payment_url)
	else:
		return render(request, 'payment_error.html', {'error': 'Payment creation failed'})

@login_required
def verify_payment(request, order_id):
	order = get_object_or_404(Order, pk=order_id)
	activation, created = ProductActivation.objects.get_or_create(customer=order.user, product=order.product)
	activation.activated = True
	activation.save()
	# Simulate payment verification
	
	
	return redirect('payment_success', order_id=order.id)

@login_required
def mock_payment(request, product_id):
	product = get_object_or_404(Product, pk=product_id)

		
	# Create an order
	order = Order.objects.create(
		product=product,
		user=request.user,
		amount=product.price,
		status='pending'
	)
	# Simulate a successful payment for demonstration purposes
	order.status = 'paid'
	order.save()
	
	# Redirect to payment success page
	return redirect('verify_payment', order_id=order.id)  # Replace with your actual success URL


######## END MOCK    
@login_required
def payment_success(request, order_id):
	order = get_object_or_404(Order, pk=order_id)

	
	return render(request, 'payment_success.html')
	
@login_required
def payment_fail(request):
	return render(request, 'payment_fail.html')


from datetime import timedelta, datetime

@login_required
def settings_view(request):
	profile, created = CustomerProfile.objects.get_or_create(user=request.user)
	to_pop = ['account_number', 'referrer', 'referral_link', 'phone_number', 'timezone'] + [i + '_remaining' for i in ['daily_drawdown', 'daily_trade_limit', 'daily_profit_limit', 'monthly_drawdown', 'monthly_profit_limit', 'trade_delays']]
	if request.method == 'POST':
		form = CustomerProfileForm(request.POST, instance=profile, exclude_fields=to_pop)
		if form.is_valid():
			form.save()
			profile.last_update = datetime.now().isoformat()
			profile.save()
			return redirect('settings')
	else:
		
		form = CustomerProfileForm(instance=profile, exclude_fields=to_pop)

	next_allowed_date = (datetime.fromisoformat(profile.last_update) + timedelta(days=profile.update_periodic_limit)).isoformat().replace('T',' ').split('.')[0]
	
	remaining_values_1 = {
		'daily_drawdown': profile.daily_drawdown_remaining_1,
		'daily_trade_limit': profile.daily_trade_limit_remaining_1,
		'daily_profit_limit': profile.daily_profit_limit_remaining_1,
		'monthly_drawdown': profile.monthly_drawdown_remaining_1,
		'monthly_profit_limit': profile.monthly_profit_limit_remaining_1,
		'trade_delays': profile.trade_delays_remaining_1,
	}
	
	remaining_values_2 = {
		'daily_drawdown': profile.daily_drawdown_remaining_2,
		'daily_trade_limit': profile.daily_trade_limit_remaining_2,
		'daily_profit_limit': profile.daily_profit_limit_remaining_2,
		'monthly_drawdown': profile.monthly_drawdown_remaining_2,
		'monthly_profit_limit': profile.monthly_profit_limit_remaining_2,
		'trade_delays': profile.trade_delays_remaining_2,
	}
	
	context = {
		'form': form,
		'readonly': not profile.can_update(),
		'profile': profile,
		'next_allowed_date': datetime.fromisoformat(next_allowed_date),
		'active_page': 'settings',
		'remaining_values_1': remaining_values_1,
		'remaining_values_2': remaining_values_2,
	}
	return render(request, 'settings.html', context)


@user_passes_test(is_admin)
@login_required
def reset_last_update(request, profile_id):
	profile = get_object_or_404(CustomerProfile, user=profile_id)

	
	profile.last_update = timezone.datetime(1970,12,1)
	
	remainings = [i + '_remaining' for i in ['daily_drawdown', 'daily_trade_limit', 'daily_profit_limit', 'monthly_drawdown', 'monthly_profit_limit', 'trade_delays']]
	
	for r in remainings:
		setattr(profile, r, 0)
	
	profile.save()
	
	
	
	return redirect('list_of_customers')  # Redirect to settings page or wherever appropriate

	


@user_passes_test(is_admin)
def inbox(request):
	messages = InboxMessage.objects.filter(recipient=request.user).order_by('-sent_at')
	return render(request, 'inbox.html', {'messages': messages, 'active_page': 'inbox'})

@user_passes_test(is_admin)
def view_message(request, message_id):
	message = get_object_or_404(InboxMessage, id=message_id, recipient=request.user)
	message.is_read = True
	message.save()
	return render(request, 'message.html', {'message': message, 'active_page': 'view_message'})

@user_passes_test(is_admin)
@method_decorator(csrf_exempt, name='dispatch')
def delete_messages(request):
	if request.method == 'POST':
		data = json.loads(request.body)
		message_ids = data.get('message_ids', [])
		if message_ids:
			InboxMessage.objects.filter(id__in=message_ids, recipient=request.user).delete()
			return JsonResponse({'success': True})
		return JsonResponse({'success': False, 'error': 'No message IDs provided.'})

@user_passes_test(is_admin)
def messaging(request):
	return render(request, 'messaging.html', {'active_page': 'messaging'})

@user_passes_test(is_admin)
def send_public_message(request):
	if request.method == 'POST':
		message = request.POST.get('message')
		expiry_date = request.POST.get('expiry_date')
		if message and expiry_date:
			expiry_date = timezone.make_aware(timezone.datetime.fromisoformat(expiry_date), timezone.get_current_timezone())
			users = User.objects.all()
			for user in users:
				public_message_list, created = PublicMessageList.objects.get_or_create(user=user)
				public_message_list.add_string(message, expiry_date)
			messages.success(request, 'Public message sent successfully!')
			return redirect('messaging')
		else:
			messages.error(request, 'Please fill out all fields.')
	return render(request, 'send_public_message.html', {'active_page': 'send_public_message'})

@user_passes_test(is_admin)
def send_private_message(request):
	if request.method == 'POST':
		message = request.POST.get('message')
		expiry_date = request.POST.get('expiry_date')
		recipients = request.POST.get('recipients')
		if message and expiry_date and recipients:
			expiry_date = timezone.make_aware(timezone.datetime.fromisoformat(expiry_date), timezone.get_current_timezone())
			recipient_usernames = [username.strip() for username in recipients.split(',')]
			users = User.objects.filter(username__in=recipient_usernames)
			for user in users:
				private_message_list, created = PrivateMessageList.objects.get_or_create(user=user)
				private_message_list.add_string(message, expiry_date)
			messages.success(request, 'Private message sent successfully!')
			return redirect('messaging')
		else:
			messages.error(request, 'Please fill out all fields.')
	return render(request, 'send_private_message.html', {'active_page': 'send_private_message'})

@login_required
@user_passes_test(is_admin)
def customer_profile(request, id):
	customer = get_object_or_404(User, id=id)
	products = Product.objects.all()
	activations = ProductActivation.objects.filter(customer=customer)
	active_products = [activation.product for activation in activations]
	if request.method == 'POST':
		for product in products:
			
			#activation, created = ProductActivation.objects.get(customer=customer, product=product)
			#if created:
			#	activation.delete()
			#else:
			#	activation.expiry_date = request.POST.get(f'expiry_date_{product.id}')
			#	activation.save()
			if request.POST.get(f'active_{product.id}', 'off') == 'on':
				
				activation, created = ProductActivation.objects.get_or_create(customer=customer, product=product)
				activation.expiry_date = request.POST.get(f'expiry_date_{product.id}')
				activation.save()
				
			else:
				ps = ProductActivation.objects.filter(customer=customer, product=product)
				for p in ps:
					p.delete()
				cr = CompilationRequest.objects.filter(customer=customer, product=product)
				for c in cr:
					c.delete()
		return redirect('customer_profile', id=customer.id)
	context = {
		'customer': customer,
		'products': products,
		'active_products': active_products,
		'activations': activations,
		'active_page': 'customer_profile'
	}
	return render(request, 'customer_profile.html', context)

from django.urls import reverse

from urllib.parse import urlencode

def register_view(request):
	referrer = request.GET.get('referrer', '')  # Get the referrer from the GET parameters
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		
		if form.is_valid():
			user = form.save()
			cp = CustomerProfile.objects.create(
				user=user, 
				referrer=form.cleaned_data['referrer'], 
				phone_number=form.cleaned_data['phone_number'], 
				referral_link='https://tradinglocally.com/register/?referrer=' + user.username
			)
			group = Group.objects.get(name='Customer')
			user.groups.add(group)
			user.save()
			query_string = urlencode({'message': 'Registration successful. Please log in.'})
			url = reverse('login') + '?' + query_string
			return redirect(url)
	else:
		form = UserRegisterForm(initial={'referrer': referrer})  # Pass the referrer to the form initial data
		# Set password widget attributes to hide instructions
		form.fields['password1'].widget.attrs.update({'autocomplete': 'new-password', 'aria-describedby': '', 'onpaste': 'return false'})
		form.fields['password2'].widget.attrs.update({'autocomplete': 'new-password', 'aria-describedby': '', 'onpaste': 'return false'})
	if referrer:  # If referrer is present, set the referrer field as read-only
		form.fields['referrer'].widget.attrs['readonly'] = True
	return render(request, 'register.html', {'form': form, 'active_page': 'register'})
	
def login_view(request):
	message = request.GET.get('message', '')
	if request.method == 'POST':
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			if user.groups.filter(name='Admin').exists():
				return redirect('admin_panel')
			else:
				return redirect('customer_panel')
		else:
			return render(request, 'login.html', {'error': 'Invalid username or password'})
	else:
		return render(request, 'login.html', {'message': message, 'active_page': 'login'})

@user_passes_test(is_admin)
@login_required
def admin_panel(request):
	return render(request, 'admin_panel.html', {'active_page': 'admin_panel'})

@user_passes_test(is_admin)
@login_required
def list_of_products(request):
	if request.method == 'POST':
		form = ProductForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('list_of_products')
	else:
		form = ProductForm()
	products = Product.objects.all()
	return render(request, 'list_of_products.html', {'form': form, 'products': products, 'active_page': 'list_of_products'})

@user_passes_test(is_admin)
@login_required
def list_of_customers(request):
	customers = User.objects.all()[1:]
	return render(request, 'list_of_customers.html', {'customers': customers, 'active_page': 'list_of_customers'})

@user_passes_test(is_admin)
@login_required
def list_of_requests(request):
	open('file','a').write('1111111111')
	requests = CompilationRequest.objects.filter(fulfilled=False)
	if request.method == 'POST':
		open('file','a').write('2222222222')
		form = CompilationRequestForm(request.POST, request.FILES)
		if form.is_valid():
			open('file','a').write('33333333')
			request_id = request.POST.get('request_id')
			request_username = request.POST.get('request_username')
			compilation_request = CompilationRequest.objects.get(id=request_id)
			compilation_request.executable = request.FILES['executable']
			compilation_request.fulfilled = True
			compilation_request.save()
			user = compilation_request.customer
			pa = ProductActivation.objects.get(customer=user, product=compilation_request.product)
			pa.activated = True
			pa.expiry_date = request.POST.get('expiry_date')
			pa.save()
			return redirect('list_of_requests')
	else:
		form = CompilationRequestForm()
	return render(request, 'list_of_requests.html', {'requests': requests, 'form': form, 'active_page': 'list_of_requests'})


@login_required
def customer_panel(request):
	return render(request, 'customer_panel.html', {'active_page': 'customer_panel'})

@login_required
def active_licenses(request):
	customer = request.user
	activations = ProductActivation.objects.filter(customer=customer, activated=True)
	active_licenses = []
	for activation in activations:
		not_requested_yet = True
		try:
			download_link = CompilationRequest.objects.filter(customer=customer, product=Product.objects.filter(id=activation.product_id)[0])[0]
			download_link = CompilationRequest.objects.filter(customer=customer, product=Product.objects.filter(id=activation.product_id)[0])
			download_link = download_link[len(download_link)-1].executable.url
		except IndexError:
			
			download_link = False
			not_requested_yet = False
		except ValueError:
			
			download_link = False
			not_requested_yet = True
		active_licenses.append({
			'name': Product.objects.filter(id=activation.product_id)[0].name,
			'product_id': activation.product_id,
			'download_link': download_link,
			'not_requested_yet': not_requested_yet,
			'expiry_date': activation.expiry_date
		})
	context = {
		'active_licenses': active_licenses,
		'active_page': 'active_licenses'
	}
	return render(request, 'active_licenses.html', context)

@login_required
def profile_info(request):
	if request.method == 'POST':
		profile, created = CustomerProfile.objects.get_or_create(user=request.user)
		profile.account_number = request.POST.get('account_number')
		profile.phone_number = request.POST.get('phone_number')
		profile.ea_password = request.POST.get('ea_password')
		profile.timezone = request.POST.get('timezone')  # Save the timezone
		profile.save()
		return redirect('profile_info')
	else:
		profile, created = CustomerProfile.objects.get_or_create(user=request.user)
		if profile.referral_link=='':
			profile.referral_link = 'https://tradinglocally.com/register/?referrer=' + profile.user.username
			profile.save()
		timezones = pytz.common_timezones  # Get list of common timezones
	return render(request, 'profile_info.html', {'profile': profile, 'active_page': 'profile_info', 'timezones': timezones})
	
	
@user_passes_test(is_admin)
@login_required
def remove_product(request, id):
	product = Product.objects.get(id=id)
	product.delete()
	return redirect('list_of_products')


def remove_selected_products(request):
	if request.method == 'POST':
		selected_products = request.POST.getlist('selected_products')
		Product.objects.filter(id__in=selected_products).delete()
		return redirect('list_of_products')

def remove_selected_requests(request):
	if request.method == 'POST':
		selected_requests = request.POST.getlist('selected_requests')
		CompilationRequest.objects.filter(id__in=selected_requests).delete()
		return redirect('list_of_requests')  # Redirect to the requests management page    
		
def product_list(request):
	products = Product.objects.all()
	return render(request, 'product_list.html', {'products': products, 'active_page': 'product_list'})

@login_required
def remove_from_cart(request, item_id):
	cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
	cart_item.delete()
	return redirect('view_cart')


def product_detail(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	
	if request.method == 'POST':
		try:
			cart, created = Cart.objects.get_or_create(user=request.user)
		except TypeError:
			redirect('login')
		form = AddToCartForm(request.POST)
		if form.is_valid():
			quantity = form.cleaned_data['quantity']
			cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
			if not created:
				cart_item.quantity += quantity
			else:
				cart_item.quantity = quantity
			cart_item.save()
			return redirect('view_cart')
	else:
		form = AddToCartForm()
	return render(request, 'product_detail.html', {'form': form, 'product': product})

	

@login_required
def request_compilation(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	compilation_request = CompilationRequest.objects.create(
		customer=request.user,
		product=product,
		account_number=request.user.customerprofile.account_number,
		fulfilled=False
	)
	return redirect('active_licenses')

def home(request):
	print(request.LANGUAGE_CODE)
	if request.user.is_authenticated:
		if request.user.is_staff:  # Check if user is admin (staff)
			return redirect('admin_panel')
		else:
			return redirect('customer_panel')
	else:
		products = Product.objects.all()
		return render(request, 'home.html', {'active_page': 'home', 'products':products})

def about(request):
	return render(request, 'about.html', {'active_page': 'about'})

def contact(request):
	return render(request, 'contact.html', {'active_page': 'contact'})

def logout_view(request):
	logout(request)
	return redirect('home')

@login_required
def list_of_tickets(request):
	tickets = Ticket.objects.filter(user=request.user)
	return render(request, 'list_of_tickets.html', {'tickets': tickets, 'active_page': 'list_of_tickets'})

@login_required
def create_new_ticket(request):
	if request.method == 'POST':
		form = TicketForm(request.POST, request.FILES)
		if form.is_valid():
			ticket = form.save(commit=False)
			ticket.user = request.user
			ticket.save()
			TicketMessage.objects.create(ticket=ticket, sender=request.user, message=ticket.message, attachments=ticket.attachments)
			return redirect('list_of_tickets')
	else:
		form = TicketForm()
	return render(request, 'create_new_ticket.html', {'form': form, 'active_page': 'create_new_ticket'})

@user_passes_test(is_admin)
@login_required
def ticket_management(request):
	tickets = Ticket.objects.all()
	return render(request, 'ticket_management.html', {'tickets': tickets, 'active_page': 'ticket_management'})

@user_passes_test(is_admin)
@login_required
def show_ticket_admin(request, ticket_id):
	ticket = get_object_or_404(Ticket, id=ticket_id)
	messages_ = TicketMessage.objects.filter(ticket=ticket).order_by('created_at')
	if request.method == 'POST':
		form = TicketResponseForm(request.POST, request.FILES)
		if form.is_valid():
			response = form.save(commit=False)
			response.ticket = ticket
			response.sender = request.user
			response.save()
			ticket.status = 'answered'
			ticket.save()
			return redirect('ticket_management')
	else:
		form = TicketResponseForm()
		if ticket.status == 'unread':
			ticket.status = 'read'
			ticket.save()
	return render(request, 'show_ticket_admin.html', {'ticket': ticket, 'messages_': messages_, 'form': form, 'active_page': 'show_ticket_admin'})

@login_required
def show_ticket_customer(request, ticket_id):
	ticket = get_object_or_404(Ticket, id=ticket_id)
	messages = TicketMessage.objects.filter(ticket=ticket).order_by('created_at')
	if request.method == 'POST':
		form = TicketResponseForm(request.POST, request.FILES)
		if form.is_valid():
			response = form.save(commit=False)
			response.ticket = ticket
			response.sender = request.user
			response.save()
			return redirect('show_ticket_customer', ticket_id=ticket_id)
	else:
		form = TicketResponseForm()
	return render(request, 'show_ticket_customer.html', {'ticket': ticket, 'messages': messages, 'form': form, 'active_page': 'show_ticket_customer'})

@user_passes_test(is_admin)
@login_required
def remove_tickets(request):
	if request.method == 'POST':
		ticket_ids = request.POST.getlist('selected_tickets')
		Ticket.objects.filter(id__in=ticket_ids).delete()
	return redirect('ticket_management')

@user_passes_test(is_admin)
@login_required
def remove_request(request, id):
	
	req = CompilationRequest.objects.get(id=id)
	req.delete()
	return redirect('list_of_requests')


@user_passes_test(is_admin)
@login_required
def remove_inbox_messages(request):
	if request.method == 'POST':
		ticket_ids = request.POST.getlist('selected_messages')
		InboxMessage.objects.filter(id__in=ticket_ids).delete()
	return redirect('inbox')


from django.shortcuts import render, redirect
from .models import Product
from .forms import ProductForm

@user_passes_test(is_admin)
def add_new_product(request):
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			product = form.save(commit=False)

			# Process features
			feature_keys = request.POST.getlist('feature_key')
			feature_values = request.POST.getlist('feature_value')
			features = {key: value for key, value in zip(feature_keys, feature_values)}
			product.features = features

			product.save()
			return redirect('list_of_products')  # Redirect to your product list or detail page
	else:
		form = ProductForm()

	return render(request, 'add_new_product.html', {'form': form})

@user_passes_test(is_admin)
def edit_product(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES, instance=product)
		if form.is_valid():
			form.save()
			return redirect('list_of_products')
	else:
		form = ProductForm(instance=product)
	return render(request, 'edit_product.html', {'form': form, 'active_page': 'edit_product'})



@login_required
def upload_receipt(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	if request.method == 'POST':
		form = ReceiptUploadForm(request.POST, request.FILES)
		if form.is_valid():
			receipt = form.save(commit=False)
			receipt.user = request.user
			receipt.product = product
			receipt.save()
			return redirect('success_page')
	else:
		form = ReceiptUploadForm()
	return render(request, 'upload_receipt.html', {'form': form, 'product': product})



@login_required
@user_passes_test(is_admin)
def shop_view(request):
	receipts = Receipt.objects.filter(verified=False)
	if request.method == 'POST':
		for receipt in receipts:
			if request.POST.get(f'verify_{receipt.id}', 'off') == 'on':
				receipt.verified = True
				receipt.save()
				ProductActivation.objects.get_or_create(customer=receipt.user, product=receipt.product)
				
				
		return redirect('shop')
	return render(request, 'shop.html', {'receipts': receipts, 'active_page':'shop'})

	
	
def success_page(request):
	return render(request, 'success_page.html')



@user_passes_test(is_admin)
@login_required
def remove_inbox_messages(request):
	if request.method == 'POST':
		message_ids = request.POST.getlist('selected_messages')
		InboxMessage.objects.filter(id__in=message_ids).delete()
	return redirect('inbox')


@login_required
def performance_view(request):
	rp = Report.objects.filter(user=request.user)
	if not len(rp):
		return render(request, 'performance/index.html')
	rp = [i.unique_id for i in rp]
	timeframe = 'hourly'
	user = request.user
	user_data = Report.objects.filter(user=user)[0]
	
	if timeframe == 'hourly':
		x_axis_variable = 'Hours'
		y_axis_variables = ['Hourly PNL', 'Hourly Win Rates']
		z_axis_variables = ['Hourly Numbers']
		hours = list(range(24))
		weekdays = []
	elif timeframe == 'weekday':
		x_axis_variable = 'Weekdays'
		y_axis_variables = ['Weekday PNL', 'Weekday Win Rates']
		z_axis_variables = ['Weekday Numbers']
		hours = []
		weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
	else:
		return HttpResponseBadRequest("Invalid timeframe provided")
	
	data = {
		'hours': hours,
		'weekdays': weekdays,
		'hourly_win_rates': list(user_data.get_hourly_winrate().values()),
		'hourly_pnl': list(user_data.get_hourly_pnl().values()),
		'hourly_numbers': (np.array(list(user_data.get_hourly_numbers().values())) ** 1).tolist(),
		'weekday_win_rates': list(user_data.get_weekday_winrate().values()),
		'weekday_pnl': list(user_data.get_weekday_pnl().values()),
		'weekday_numbers': (np.array(list(user_data.get_weekday_numbers().values())) ** 1).tolist(),
	}
	
	
	return render(request, 'performance/index.html', {
		'name_of_reports': rp,
		'user_id': request.user.id,
		'active_page':'performance',
		'x_axis_variable': x_axis_variable,
		'y_axis_variables': y_axis_variables,
		'z_axis_variables': z_axis_variables,
		'data': data,
		'timeframe': timeframe,
	})
	
   
@login_required
def week_day_winrate_view(request, user_id, unique_id):
	user = get_object_or_404(User, id=user_id)
	user_data = get_object_or_404(Report, user=user, unique_id=unique_id)
	weekday_winrate = user_data.get_weekday_winrate()
	return render(request, 'performance/week_day_winrate.html', {'weekday_winrate': weekday_winrate, 'active_page':'performance'})



@login_required
def hourly_pnl_view(request, user_id, unique_id):
	user = get_object_or_404(User, id=user_id)
	user_data = get_object_or_404(Report, user=user, unique_id=unique_id)
	hourly_pnl = user_data.get_hourly_pnl()
	return render(request, 'performance/hourly_pnl.html', {'hourly_pnl': hourly_pnl, 'active_page':'performance'})


@login_required
def hourly_winrate_view(request, user_id, unique_id):
	user = get_object_or_404(User, id=user_id)
	user_data = get_object_or_404(Report, user=user, unique_id=unique_id)
	hourly_winrate = user_data.get_hourly_winrate()
	return render(request, 'performance/hourly_winrate.html', {'hourly_winrate': hourly_winrate, 'active_page':'performance'})

@login_required
def week_day_pnl_view(request, user_id, unique_id):
	user = get_object_or_404(User, id=user_id)
	user_data = get_object_or_404(Report, user=user, unique_id=unique_id)
	weekday_pnl = user_data.get_weekday_pnl()
	return render(request, 'performance/weekday_pnl.html', {'weekday_pnl': weekday_pnl, 'active_page':'performance'})


@login_required
def bubble_chart_view(request, user_id, unique_id, timeframe):
	user = get_object_or_404(User, id=user_id)
	user_data = get_object_or_404(Report, user=user, unique_id=unique_id)
	
	# Depending on the timeframe, select appropriate data
	if timeframe == 'hourly':
		x_axis_variables = ['hours']
		y_axis_variables = ['hourly_win_rates', 'hourly_pnl']
		z_axis_variables = ['hourly_numbers']
		hours = list(range(24))
	elif timeframe == 'weekday':
		x_axis_variables = ['weekdays']
		y_axis_variables = ['weekday_win_rates', 'weekday_pnl']
		z_axis_variables = ['weekday_numbers']
		hours = []  # Empty list for weekdays, adjust as per your data structure
	else:
		# Handle invalid timeframe here or redirect to an error page
		return HttpResponseBadRequest("Invalid timeframe provided")
	
	# Collect data based on the timeframe
	data = {
		'hours': hours,
		'weekdays': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],  # Example weekdays list
		'hourly_win_rates': list(user_data.get_hourly_winrate().values()),
		'hourly_pnl': list(user_data.get_hourly_pnl().values()),
		'hourly_numbers': (np.array(list(user_data.get_hourly_numbers().values())) ** 1).tolist(),  # Example power calculation
		'weekday_win_rates': list(user_data.get_weekday_winrate().values()),
		'weekday_pnl': list(user_data.get_weekday_pnl().values()),
		'weekday_numbers': (np.array(list(user_data.get_weekday_numbers().values())) ** 1).tolist(),  # Example power calculation
	}
	
	return render(request, 'performance/bubble_chart.html', {
		'x_axis_variables': x_axis_variables,
		'y_axis_variables': y_axis_variables,
		'z_axis_variables': z_axis_variables,
		'data': data,
		'timeframe': timeframe,
		'active_page':'performance',
	})


@login_required
def bubble_chart_view(request, user_id, unique_id, timeframe):
	user = get_object_or_404(User, id=user_id)
	user_data = get_object_or_404(Report, user=user, unique_id=unique_id)
	
	if timeframe == 'hourly':
		x_axis_variable = 'Hours'
		y_axis_variables = ['Hourly PNL', 'Hourly Win Rates']
		z_axis_variables = ['Hourly Numbers']
		hours = list(range(24))
		weekdays = []
	elif timeframe == 'weekday':
		x_axis_variable = 'Weekdays'
		y_axis_variables = ['Weekday PNL', 'Weekday Win Rates']
		z_axis_variables = ['Weekday Numbers']
		hours = []
		weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
	else:
		return HttpResponseBadRequest("Invalid timeframe provided")
	
	data = {
		'hours': hours,
		'weekdays': weekdays,
		'hourly_win_rates': list(user_data.get_hourly_winrate().values()),
		'hourly_pnl': list(user_data.get_hourly_pnl().values()),
		'hourly_numbers': (np.array(list(user_data.get_hourly_numbers().values())) ** 1).tolist(),
		'weekday_win_rates': list(user_data.get_weekday_winrate().values()),
		'weekday_pnl': list(user_data.get_weekday_pnl().values()),
		'weekday_numbers': (np.array(list(user_data.get_weekday_numbers().values())) ** 1).tolist(),
	}
	print(data['weekday_win_rates'])
	return render(request, 'performance/bubble_chart.html', {
		'x_axis_variable': x_axis_variable,
		'y_axis_variables': y_axis_variables,
		'z_axis_variables': z_axis_variables,
		'data': data,
		'timeframe': timeframe,
		'active_page': 'performance',
	})



@login_required
def bubble_chart_view(request, user_id, unique_id, timeframe):
	user = get_object_or_404(User, id=user_id)
	report = get_object_or_404(Report, user=user, unique_id=unique_id)

	# Generate DataFrame from report
	df = report.get_dataframe()

	# Calculate metrics
	hourly_metrics, weekday_metrics = calculate_timely_metrics(df)

	# Depending on the timeframe, select appropriate data
	if timeframe == 'hourly':
		x_axis_variable = 'Hours'
		y_axis_variables = ['Hourly PNL', 'Hourly Win Rates']
		z_axis_variables = ['Hourly Numbers', 'Hourly Volume']
		data = {
			'hours': hourly_metrics.index.tolist(),
			'weekdays': [],
			'hourly_win_rates': hourly_metrics['Hourly Win Rate'].tolist(),
			'hourly_pnl': hourly_metrics['Hourly PnL'].tolist(),
			'hourly_numbers': hourly_metrics['Hourly Number of Trades'].tolist(),
			'hourly_volume': hourly_metrics['Hourly Volume'].tolist(),
			'weekday_win_rates': [],
			'weekday_pnl': [],
			'weekday_numbers': [],
			'weekday_volume': [],
		}
	elif timeframe == 'weekday':
		x_axis_variable = 'Weekdays'
		y_axis_variables = ['Weekday PNL', 'Weekday Win Rates']
		z_axis_variables = ['Weekday Numbers', 'Weekday Volume']
		data = {
			'hours': [],
			'weekdays': weekday_metrics.index.tolist(),
			'hourly_win_rates': [],
			'hourly_pnl': [],
			'hourly_numbers': [],
			'hourly_volume': [],
			'weekday_win_rates': weekday_metrics['Week Day Win Rate'].tolist(),
			'weekday_pnl': weekday_metrics['Week Day PnL'].tolist(),
			'weekday_numbers': weekday_metrics['Week Day Number of Trades'].tolist(),
			'weekday_volume': weekday_metrics['Week Day Volume'].tolist(),
		}
	else:
		return HttpResponseBadRequest("Invalid timeframe provided")

	return render(request, 'performance/bubble_chart.html', {
		'x_axis_variable': x_axis_variable,
		'y_axis_variables': y_axis_variables,
		'z_axis_variables': z_axis_variables,
		'data': data,
		'timeframe': timeframe,
		'active_page': 'performance',
	})
	
@login_required
def bar_chart_view(request, user_id, unique_id, timeframe):
	user = get_object_or_404(User, id=user_id)
	report = get_object_or_404(Report, user=user, unique_id=unique_id)

	# Generate DataFrame from report
	df = report.get_dataframe()

	# Calculate metrics
	hourly_metrics, weekday_metrics = calculate_timely_metrics(df)

	# Depending on the timeframe, select appropriate data
	if timeframe == 'hourly':
		x_axis_variable = 'Hours'
		y_axis_variables = ['Hourly Win Rates', 'Hourly PNL', 'Hourly Number of Trades', 'Hourly Volume']
		y_keys = ['hourly_win_rates', 'hourly_pnl', 'hourly_numbers', 'hourly_volume']
		data = {
			'hours': hourly_metrics.index.tolist(),
			'hourly_win_rates': hourly_metrics['Hourly Win Rate'].tolist(),
			'hourly_pnl': hourly_metrics['Hourly PnL'].tolist(),
			'hourly_numbers': hourly_metrics['Hourly Number of Trades'].tolist(),
			'hourly_volume': hourly_metrics['Hourly Volume'].tolist(),
		}
	elif timeframe == 'weekday':
		x_axis_variable = 'Weekdays'
		y_axis_variables = ['Weekday Win Rates', 'Week Day PNL', 'Week Day Number of Trades', 'Week Day Volume']
		y_keys = ['weekday_win_rates', 'weekday_pnl', 'weekday_numbers', 'weekday_volume']
		data = {
			'weekdays': weekday_metrics.index.tolist(),
			'weekday_win_rates': weekday_metrics['Week Day Win Rate'].tolist(),
			'weekday_pnl': weekday_metrics['Week Day PnL'].tolist(),
			'weekday_numbers': weekday_metrics['Week Day Number of Trades'].tolist(),
			'weekday_volume': weekday_metrics['Week Day Volume'].tolist(),
		}
	else:
		# Handle invalid timeframe here or redirect to an error page
		return HttpResponseBadRequest("Invalid timeframe provided")

	return render(request, 'performance/bar_chart.html', {
		'x_axis_variable': x_axis_variable,
		'y_axis_variables': y_axis_variables,
		'y_keys': y_keys,
		'data': data,
		'timeframe': timeframe,
		'active_page': 'performance',
	})

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import translation
from django.shortcuts import redirect

def set_language(request):
	user_language = request.GET.get('language', 'fa')
	translation.activate(user_language)
	response = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
	response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)
	return response




def clean_statistics(stats):
	# Replace spaces with underscores in keys
	return {key.replace(' ', '_'): value for key, value in stats.items()}

@login_required
def reports(request):
	# Fetch all reports for the current user
	rp = Report.objects.filter(user=request.user)
	return render(request, 'performance/reports.html', {'reports': rp})

@login_required
def report_details(request, unique_id):
	rp = Report.objects.filter(user=request.user)
	report = get_object_or_404(Report, user=request.user, unique_id=unique_id)
	df = from_string(report.assemble_report())
	statistics = trading_metrics(df)
	cleaned_statistics = clean_statistics(statistics)
	return render(request, 'performance/reports.html', {'statistics': cleaned_statistics, 'selected_report': report, 'reports':rp})

@login_required
def checkout(request, product_id):
	product = get_object_or_404(Product, pk=product_id)
	if request.method == 'POST':
		crypto = request.POST.get('crypto', 'BTC')
		order = Order.objects.create(
			product=product,
			user=request.user,
			amount=product.price,
			status='pending'
		)

		# Create payment request
		payload = {
			'price_amount': round(float(product.price)/settings.EXCHANGE_RATE,2),
			'price_currency': 'USD',
			'pay_currency': crypto.lower(),
			'ipn_callback_url': 'https://www.tradinglocally.com/payment/callback/',
			'order_id': order.id,
			'order_description': product.name,
		}
		headers = {
			'x-api-key': settings.PAYMENT_API_KEY
		}
		response = requests.post(f"{settings.PAYMENT_API_URL}invoice", json=payload, headers=headers)
		data = response.json()

		order.payment_url = data['invoice_url']
		order.save()

		return redirect(data['invoice_url'])

	return render(request, 'checkout.html', {'product': product, 'price':round(float(product.price)/settings.EXCHANGE_RATE,2), 'currencies': get_currencies()})

def get_currencies():
	l = [
		"btc", "eth", "ltc", "usdt", "ada", "xmr", "zec", "xvg", "bch", "qtum", "dash", "xlm", "xrp", "xem", 
		"dgb", "lsk", "doge", "trx", "kmd", "rep", "bat", "ark", "waves", "bnb", "xzc", "nano", "tusd", 
		"vet", "zen", "grs", "neo", "gas", "pax", "usdc", "rvn", 
		"zil", "bcd", "cro", "dai", "gt", 
		"stpt", "ava", "sxp", "uni", "okb", "btg"
	]
	l = [i.upper() for i in l]
	return l

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def payment_callback(request):
	if request.method == 'POST':
		data = request.POST
		order_id = data.get('order_id')
		order = get_object_or_404(Order, id=order_id)
		
		if data.get('payment_status') == 'completed':
			order.status = 'paid'
			order.save()
			pa = ProductActivation.objects.create(customer=order.user, product=order.product)
			pa.save()
			return redirect('payment_success')
		
	return redirect('payment_fail')


@login_required
def payment_success(request):
	return render(request, 'payment_success.html')

@login_required
def payment_fail(request):
	return render(request, 'payment_fail.html')




@login_required
def rial_checkout(request, cart_id):
	cart = get_object_or_404(Cart, pk=cart_id)

	
	order = Order.objects.create(
		cart=cart,
		user=request.user,
		amount=sum([i.get_total_price() for i in cart.items.all()])*10,
		status='pending'
	)

	# Create payment request
	payload = {
		'merchant':settings.MERCHANT,
		'amount': order.amount,
		'callbackUrl': 'https://tradinglocally.com/rial_payment/callback/',
		'orderId':str(order.id),
	}
	
	response = requests.post("https://gateway.zibal.ir/v1/request", json=payload)
	data = response.json()
	
	
	order.trackId = data['trackId']
	order.save()
	if int(data['result'])==100:
		return redirect(f'https://gateway.zibal.ir/start/{order.trackId}')



@csrf_exempt
def rial_payment_callback(request):
	track_id = request.GET.get('trackId')
	success = request.GET.get('success')
	status = request.GET.get('status')
	order_id = request.GET.get('orderId')
	order = get_object_or_404(Order, id=order_id)
	print(success)
	if int(success) == 1:
		order.status = 'paid'
		order.save()
		for i in order.cart.items.all():
			pa = ProductActivation.objects.create(customer=order.user, product=i.product)
			pa.save()
		order.cart.delete()
		return redirect('payment_success')
	else:
		return redirect('payment_fail')


@csrf_exempt
def subscribe(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        referer = request.META.get('HTTP_REFERER', '/')
        if phone:
            try:
                subscription = PhoneSubscription(phone=phone)
                subscription.save()
                messages.success(request, 'شماره تلفن شما با موفقیت ثبت شد')
            except Exception as e:
                messages.error(request, 'این شماره تلفن قبلا ثبت شده است')
        else:
            messages.error(request, 'لطفا شماره تلفن خود را وارد نمایید')
        return redirect(referer)
    return redirect('/')


import csv
from django.http import HttpResponse
@user_passes_test(is_admin)
@login_required
def manage_subscriptions(request):
    # Fetch the last 25 subscribed phone numbers
    subscriptions = PhoneSubscription.objects.order_by('-id')[:25]

    if 'download' in request.GET:
        # If 'download' parameter is in GET request, generate a CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscriptions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Phone Number'])
        for subscription in subscriptions:
            writer.writerow([subscription.phone])
        
        return response

    return render(request, 'admin_subscriptions.html', {'subscriptions': subscriptions, 'active_page':'manage_subscriptions'})
