from rest_framework import views, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.utils import timezone
from pytz import timezone as pytz_timezone
from .models import *
import datetime

LIMIT = 1


def custom_authenticate(username, password):
	cp = CustomerProfile.objects.filter(ea_username=username,ea_password=password)
	if len(cp)==0:
		return None
	else:
		return cp[0].user
		
		
class CustomAuthToken(ObtainAuthToken):
	def post(self, request, *args, **kwargs):
		if not all(key in request.data for key in ('username', 'password', 'random_token')):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

		user = custom_authenticate(username=request.data['username'], password=request.data['password'])
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)


		api_usage = APIUsage.objects.filter(user=user)
		if len(api_usage)>=LIMIT:
			try:
				api_usage = APIUsage.objects.get(user=user, random_token=request.data['random_token'])
			except:
				api_usage[0].delete()
				api_usage = APIUsage(user=user, random_token=request.data['random_token'])
		else:
			api_usage = APIUsage(user=user, random_token=request.data['random_token'])
			api_usage.save()


		
		return Response({'detail': 'Valid'})


class GetExpiryDate(ObtainAuthToken):
	def post(self, request, *args, **kwargs):
		if not all(key in request.data for key in ('username', 'password', 'product','random_token')):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
		user = custom_authenticate(username=request.data['username'], password=request.data['password'])
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		api_usage = APIUsage.objects.get(user=user, random_token=request.data['random_token'])
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=request.data['random_token'])
		except:
			print(APIUsage.objects.all())
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
			
		product = Product.objects.filter(name=request.data['product'])
		if len(product) == 0:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)
		activation = ProductActivation.objects.filter(customer=user, product=product[0])
		if len(activation) == 0:
			return Response({'detail': 'Invalid.'}, status=status.HTTP_400_BAD_REQUEST)
		else:
			return Response({'detail': activation[0].expiry_date.replace('-','.')})
		



class GetAccountNumber(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data['username']
		password = request.data['password']
		product = request.data['product']
		random_token = request.data['random_token']
		
		if not all([username, password, product, random_token]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
		
		product_obj = Product.objects.filter(name=product).first()
		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)
		
		activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
		if activation is None:
			return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)
		customer_profile = CustomerProfile.objects.get(user=user)
		return Response({'detail': customer_profile.account_number})



class GetPublicMessages(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username', 'newuser')
		password = request.data.get('password', 'NewPassword12')
		product = request.data.get('product')
		random_token = request.data.get('random_token')
		
		if not all([username, password, product, random_token]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
		
		product_obj = Product.objects.filter(name=product).first()
		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)
		
		activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
		if activation is None:
			return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user.publicmessagelist.remove_expired_strings()
		valid_strings = '\n----------\n'.join(user.publicmessagelist.get_valid_strings())
		
		return Response({'detail': valid_strings})





class GetPrivateMessages(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username', 'newuser')
		password = request.data.get('password', 'NewPassword12')
		product = request.data.get('product')
		random_token = request.data.get('random_token')
		
		if not all([username, password, product, random_token]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
		
		product_obj = Product.objects.filter(name=product).first()
		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)
		
		activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
		if activation is None:
			return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user.privatemessagelist.remove_expired_strings()
		valid_strings = '\n----------\n'.join(user.privatemessagelist.get_valid_strings())
		
		return Response({'detail': valid_strings})



class SendMessageToAdmin(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')
		product = request.data.get('product')
		random_token = request.data.get('random_token')
		message = request.data.get('message')

		if not all([username, password, product, random_token, message]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)

		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

		product_obj = Product.objects.filter(name=product).first()
		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)

		activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
		if activation is None:
			return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)

		admin_user = User.objects.filter(is_superuser=True).first()
		if admin_user is None:
			return Response({'detail': 'Admin user not found.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		InboxMessage.objects.create(sender=user, recipient=admin_user, message=message)
		return Response({'detail': 'Message sent successfully.'}, status=status.HTTP_200_OK)







class SubmitReportChunk(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')
		product = request.data.get('product')
		chunk = request.data.get('chunk')
		random_token = request.data.get('random_token')
		
		unique_id = request.data.get('unique_id', str(uuid.uuid4()))  # Generate if not provided

		if not all([username, password, product, chunk]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
		
		product_obj = Product.objects.filter(name=product).first()
		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)

		report, created = Report.objects.get_or_create(user=user, product=product_obj, unique_id=unique_id)
		report.add_chunk(chunk)
		
		return Response({'detail': 'Chunk added successfully.', 'unique_id': report.unique_id}, status=status.HTTP_200_OK)

class AssembleReport(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data.get('username')
		password = request.data.get('password')
		product = request.data.get('product')
		unique_id = request.data.get('unique_id')
		random_token = request.data.get('random_token')
		
		if not all([username, password, product, unique_id]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

		product_obj = Product.objects.filter(name=product).first()
		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)

		report = Report.objects.filter(user=user, product=product_obj, unique_id=unique_id).first()
		if report is None:
			return Response({'detail': 'No report found.'}, status=status.HTTP_404_NOT_FOUND)

		full_report = report.assemble_report()
		
		return Response({'report': full_report}, status=status.HTTP_200_OK)





class GetCurrentDateTime(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        product = request.data.get('product')
        random_token = request.data.get('random_token')
        
        if not all([username, password, product, random_token]):
            return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = custom_authenticate(username=username, password=password)
        if user is None:
            return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            api_usage = APIUsage.objects.get(user=user, random_token=random_token)
        except APIUsage.DoesNotExist:
            return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        
        product_obj = Product.objects.filter(name=product).first()
        if product_obj is None:
            return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)
        
        activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
        if activation is None:
            return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)
        
        customer_profile = CustomerProfile.objects.get(user=user)
        user_timezone = pytz_timezone(customer_profile.timezone)
        current_time = datetime.datetime.now(user_timezone)
        
        return Response({'detail': current_time.isoformat().replace('T',' ').split('.')[0]})



# valid parameters are 'daily_drawdown', 'daily_trade_limit', 'daily_profit_limit', 'monthly_drawdown', 'monthly_profit_limit', 'trade_delays', 				  'update_periodic_limit'
# example: username=admin&password=admin&product=embedchain&random_token=12345%parameter=daily_drawdown,daily_trade_limit,daily_profit_limit,monthly_drawdown,monthly_profit_limit,trade_delays,update_periodic_limit
class GetSpecificParameter(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data['username']
		password = request.data['password']
		product = request.data['product']
		random_token = request.data['random_token']
		parameters = request.data['parameters'].split(',')
		
		if not all([username, password, product, random_token]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
		
		product_obj = Product.objects.filter(name=product).first()

		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)
		
		activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
		if activation is None:
			return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)
		customer_profile = CustomerProfile.objects.get(user=user)
		parameters_string = ''
		for parameter in parameters:
			parameter_value = getattr(customer_profile, parameter)
			parameters_string += f'{parameter}:{parameter_value},'
		return Response({'detail': parameters_string})


# example: username=admin&password=admin&product=embedchain&random_token=12345%parameter=daily_drawdown:100,daily_trade_limit:2,daily_profit_limit:2.5

class SetSpecificParameter(APIView):
	def post(self, request, *args, **kwargs):
		username = request.data['username']
		password = request.data['password']
		product = request.data['product']
		random_token = request.data['random_token']
		parameters = request.data['parameters'].split(',')
		
		if not all([username, password, product, random_token]):
			return Response({'detail': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)
		
		user = custom_authenticate(username=username, password=password)
		if user is None:
			return Response({'detail': 'Invalid username or password.'}, status=status.HTTP_400_BAD_REQUEST)
		
		try:
			api_usage = APIUsage.objects.get(user=user, random_token=random_token)
		except APIUsage.DoesNotExist:
			return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
		
		product_obj = Product.objects.filter(name=product).first()

		if product_obj is None:
			return Response({'detail': 'Invalid product.'}, status=status.HTTP_400_BAD_REQUEST)

		activation = ProductActivation.objects.filter(customer=user, product=product_obj).first()
		if activation is None:
			return Response({'detail': 'Invalid product activation.'}, status=status.HTTP_400_BAD_REQUEST)
		customer_profile = CustomerProfile.objects.get(user=user)
		parameters_string = ''
		for parameter in parameters:
			parameter_name, parameter_value = parameter.split(':')
			setattr(customer_profile, parameter_name, parameter_value)
			parameters_string += f'{parameter_name}:{parameter_value},'
		customer_profile.save()
		return Response({'detail': parameters_string})
