
from django.urls import path
from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .api_views import CustomAuthToken, GetExpiryDate, GetAccountNumber, GetPrivateMessages, GetPublicMessages, SendMessageToAdmin, SubmitReportChunk, AssembleReport, GetCurrentDateTime, GetSpecificParameter, SetSpecificParameter
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
	
	path('', views.home, name='home'),
	path('subscribe/', views.subscribe, name='subscribe'),
	path('manage_subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
	path('about/', views.about, name='about'),
	path('contact/', views.contact, name='contact'),
	path('register/', views.register_view, name='register'),
	path('login/', views.login_view, name='login'),
	path('accounts/login/', views.login_view, name='login'),
	path('admin_panel/', views.admin_panel, name='admin_panel'),
	path('set_language/', views.set_language, name='set_language'),
	path('list_of_products/', views.list_of_products, name='list_of_products'),
	path('list_of_customers/', views.list_of_customers, name='list_of_customers'),
	path('list_of_requests/', views.list_of_requests, name='list_of_requests'),
	path('remove_product/<int:id>/', views.remove_product, name='remove_product'),
	path('remove_selected_products/', views.remove_selected_products, name='remove_selected_products'),
	path('remove_request/<int:id>/', views.remove_request, name='remove_request'),
	path('remove_selected_requests/', views.remove_selected_requests, name='remove_selected_requests'),
	path('request_compilation/<int:product_id>/', views.request_compilation, name='request_compilation'),
	path('customer_profile/<int:id>/', views.customer_profile, name='customer_profile'),  # Add this line
	path('customer_panel/', views.customer_panel, name='customer_panel'),
	path('active_licenses/', views.active_licenses, name='active_licenses'),
	path('profile_info/', views.profile_info, name='profile_info'),
	path('settings/', views.settings_view, name='settings'),
	path('reset-last-update/<int:profile_id>/', views.reset_last_update, name='reset_last_update'),
	path('logout/', views.logout_view, name='logout'),
	
]

urlpatterns += [
	path('inbox/remove_inbox_message/', views.remove_inbox_messages, name='remove_inbox_messages'),  # Notice the change here
]
urlpatterns += [
	# Existing paths
	path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),
	path('get-expiry-date/', GetExpiryDate.as_view(), name='get_expiry_date'),
	path('get-account-number/', GetAccountNumber.as_view(), name='get_account_number'),
	path('get-private-message/', GetPrivateMessages.as_view(), name='get_private_message'),
	path('get-public-message/', GetPublicMessages.as_view(), name='get_public_message'),
	path('submit-report-chunk/', SubmitReportChunk.as_view(), name='submit_report_chunk'),
	path('assemble-report/', AssembleReport.as_view(), name='assemble_report'),
	path('get-current-datetime/', GetCurrentDateTime.as_view(), name='get_current_datetime'),
	path('get-specific-parameter/', GetSpecificParameter.as_view(), name='get_specific_parameter'),
	path('set-specific-parameter/', SetSpecificParameter.as_view(), name='set_specific_parameter'),
]


urlpatterns += [
	path('products/', views.product_list, name='product_list'),
	path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]



urlpatterns += [
	path('messaging/', views.messaging, name='messaging'),
	path('messaging/send_public_message/', views.send_public_message, name='send_public_message'),
	path('messaging/send_private_message/', views.send_private_message, name='send_private_message'),
	path('inbox/', views.inbox, name='inbox'),
]


urlpatterns += [
	path('send-message-to-admin/', SendMessageToAdmin.as_view(), name='send_message_to_admin'),
	path('inbox/', views.inbox, name='inbox'),
	path('inbox/remove_inbox_message/<int:message_id>', views.remove_inbox_messages, name='remove_inbox_messages'),
	path('inbox/message/<int:message_id>/', views.view_message, name='view_message'),	
	path('inbox/delete_messages/', views.delete_messages, name='delete_messages'),
]


from django.urls import path
from . import views

urlpatterns += [
	path('list_of_tickets/', views.list_of_tickets, name='list_of_tickets'),
	path('list_of_tickets/new', views.create_new_ticket, name='create_new_ticket'),
	path('ticket_management/', views.ticket_management, name='ticket_management'),
	path('ticket_management/<int:ticket_id>/', views.show_ticket_admin, name='show_ticket_admin'),
	path('list_of_tickets/<int:ticket_id>/', views.show_ticket_customer, name='show_ticket_customer'),
	path('ticket_management/remove/', views.remove_tickets, name='remove_tickets'),
]

urlpatterns += [
	path('list_of_products/', views.list_of_products, name='list_of_products'),
	path('products/add/', views.add_new_product, name='add_new_product'),
	path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
	
]


urlpatterns += [
	path('product/<int:product_id>/payment/', views.upload_receipt, name='upload_receipt'),
	path('shop/', views.shop_view, name='shop'),
	path('success/', views.success_page, name='success_page'),
	path('checkout/<int:product_id>/', views.checkout, name='checkout'),
	path('payment/success/', views.payment_success, name='payment_success'),
	path('payment/fail/', views.payment_fail, name='payment_fail'),
	path('payment/callback/', views.payment_callback, name='payment_callback'),
	path('performance', views.performance_view, name='performance'),
	path('performance/<int:user_id>/report/<str:unique_id>/week_day_winrate', views.week_day_winrate_view, name='week_day_winrate'),
	path('performance/<int:user_id>/report/<str:unique_id>/week_day_pnl', views.week_day_pnl_view, name='week_day_pnl'),
	path('performance/<int:user_id>/report/<str:unique_id>/hourly_pnl', views.hourly_pnl_view, name='hourly_pnl'),
	path('performance/<int:user_id>/report/<str:unique_id>/hourly_winrate', views.hourly_winrate_view, name='hourly_winrate'),
	path('performance/<int:user_id>/report/<str:unique_id>/bubble_chart/<str:timeframe>/', views.bubble_chart_view, name='bubble_chart'),
	path('performance/<int:user_id>/report/<str:unique_id>/bar_chart/<str:timeframe>/', views.bar_chart_view, name='bar_chart'),

]

urlpatterns += [
	path('rial_payment/callback/', views.rial_payment_callback, name='rial_payment_callback'),
	path('rial_checkout/<int:cart_id>/', views.rial_checkout, name='rial_checkout'),
	]
urlpatterns += [
    path('reports/', views.reports, name='reports'),
    path('reports/<str:unique_id>/', views.report_details, name='report_details'),
]

urlpatterns += [
    path('product/<int:product_id>/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/finalize/', views.finalize_cart, name='finalize_cart'),
    path('invoice/<int:cart_id>/', views.invoice, name='invoice'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    ]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
