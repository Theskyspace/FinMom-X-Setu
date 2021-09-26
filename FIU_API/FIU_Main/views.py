from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib import messages

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
        messages.success(request,"Successfully login")
        return redirect("index")
    else:
        messages.error(request,"Invalid Credential, Please login again or signup")
        return redirect("index")

    return HttpResponse("login")

def Handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('index')
