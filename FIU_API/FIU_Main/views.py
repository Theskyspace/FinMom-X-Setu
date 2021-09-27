from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests 
import json
from .APIData import *

# Create your views here.


def index(request): 
    return render(request,"Index.html")

def SignupHandle(request):
    if request.method == 'POST':
        # get the post parameters
        print(request.POST)
        username = request.POST['phnno']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        #check for erroneous input

        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname;
        myuser.last_name = lname;
        myuser.save()
        messages.success(request,"Thanks! Your Account is sucessfully created")
        return redirect('index')
    else:
        return HttpResponse('404: Not found')

def Handlelogin(request):
    if request.method == 'POST':
        # get the post parameters
        print(request.POST)
        loginphnno = request.POST['loginphnno']
        loginpass1 = request.POST['loginpass1']
        
        user = authenticate(username = loginphnno,password = loginpass1)
    


    if user is not None:
        login(request,user)
        # Check here if Consent is already signed or not 
        print(headers)
        local_consent_ID = user.consent.Consent_ID;
      
        request.session['value'] = local_consent_ID
        messages.success(request,"Successfully login")
        return redirect("/ConsentFlow")
    else:
        messages.error(request,"Invalid Credential, Please login again or signup")
        return redirect("/ConsentFlow")


def Handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('index')


@login_required(login_url = "index")
def ConsentFlow(request):
    
    if 'value' in request.session:
          simple_variable = request.session['value']

    try:
        CheckConsentURL = base_url + "/Consent/handle/" + simple_variable;
        x = requests.get(CheckConsentURL , headers = headers)
        json_data = json.loads(x.text)
        print("********",x.text)
        

        if(json_data["ConsentStatus"]["status"] == "READY"):
            #Render the dashboard page here
            return render(request,"ConsentFlow.html",{"message":"Your Consent is ready"})
        else:
            return render(request,"ConsentFlow.html",{"message":"<h1>Your Consent is pending <br> Kindly Fill it <a href='https://anumati.setu.co/{}' target='_blank'>here</a>"})

    except Exception as e:
        print(e)
        return HttpResponse("Consent ID not found Try to create a new one")

    return HttpResponse("<h1>This is the consent page</h1>")