from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.SignupHandle, name='SignupHandle'),
    path('login', views.Handlelogin, name='Handlelogin'),
    path('logout', views.Handlelogout, name='Handlelogout'),
    path('CheckConsent', views.Handlelogout, name='Handlelogout'),
    path('ConsentFlow', views.ConsentFlow, name='ConsentFlow'),
    path('DashBoard', views.DataDashBoard, name='DataDashBoard'),
    path('data', views.data, name='data'),
    path('profile', views.profile, name='profile'),
    path('consent_obj', views.checked, name='consent_obj'),
    path('Break', views.breakout, name='breakout'),
    path('ProcessingData', views.ProcessingData, name='ProcessingData'),
    path('load' , views.load , name = "load"),
    path('Passbook' , views.Passbook , name = "Passbook"),
    path('goals' , views.goals , name = "goals"),
]