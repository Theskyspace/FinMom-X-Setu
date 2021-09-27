from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.SignupHandle, name='SignupHandle'),
    path('login', views.Handlelogin, name='Handlelogin'),
    path('logout', views.Handlelogout, name='Handlelogout'),
    path('CheckConsent', views.Handlelogout, name='Handlelogout'),
    path('ConsentFlow', views.ConsentFlow, name='ConsentFlow'),


]