"""

URL configuration for main app.

"""



from django.urls import path

from . import views



app_name = 'main'



urlpatterns = [

    # Home and static pages

    path('', views.home, name='home'),

    path('about/', views.about, name='about'),

    path('register/', views.register, name='register'),

    path('test-register/', views.test_register, name='test_register'),

    path('login/', views.user_login, name='user_login'),

    path('signup/', views.signup, name='signup'),

    path('faq/', views.faq, name='faq'),

    

    # User dashboard

    path('dashboard/', views.dashboard, name='dashboard'),

    path('logout/', views.logout, name='logout'),

    

    # Admin specific URLs

    path('admin-login/', views.admin_login, name='admin_login'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('user-details/<int:user_id>/', views.user_details, name='user_details'),

    path('export-data/', views.export_data, name='export_data'),

    

    # AJAX endpoints

    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),

    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),

    path('send-email/<int:user_id>/', views.send_email_to_user, name='send_email_to_user'),

    path('generate-id/', views.generate_registration_id, name='generate_registration_id'),

    path('refresh-pending/', views.refresh_pending_verifications, name='refresh_pending'),

    

    # Error handlers

    path('404/', views.custom_404, name='custom_404'),

    path('500/', views.custom_500, name='custom_500'),

]

