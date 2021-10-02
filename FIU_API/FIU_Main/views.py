from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Consent
import requests 
import json
from .APIData import *
import uuid
import base64

# Create your views here.


signedConsent = None

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
            # Here I ask for the Consent ID and I add the entry to the data base
        messages.success(request,"Successfully login")
        return redirect("/ConsentFlow")

    else:
        messages.error(request,"Invalid Credential, Please login again or signup")
        return redirect("/")


def Handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('index')


@login_required(login_url = "index")
def ConsentFlow(request):
    user = request.user
     # Check here if Consent is already signed or not 
    try:
        user_consent_obj = user.consent.ConsentHandle
        if(user_consent_obj == ""):
            url = base_url + "/Consent";
            consent_obj["txnid"] = str(uuid.uuid1());
            consent_obj["ConsentDetail"]["fiTypes"] = eval(user.consent.consent_obj)

            print("Consent Object \n",consent_obj)
            x = requests.post(url, headers = headers, json = consent_obj)
            print(x.text)
            xjson = json.loads(x.text)
            Consent_Handle = xjson["ConsentHandle"]
            print("****Status Code", x.status_code)
            print("\n","\n","\n",Consent_Handle,"\n","\n","\n")
            #Saving it to the database
            a = Consent.objects.get(user = user)
            a.ConsentHandle = Consent_Handle
            a.save()
            #Setting the local Consent varible for future ref
            
            local_Consent_Handle = user.consent.ConsentHandle;
            pritn("klansdknajksdaksdb    " , local_Consent_Handle)
       
    except:
        try:
            user_consent_obj = user.consent.consent_obj
        except:
            return redirect("/profile")
        
        #Setting the local Consent varible for future ref
    
    local_Consent_Handle = user.consent.ConsentHandle;

    
    
    
    try:
        CheckConsentURL = base_url + "/Consent/handle/" + local_Consent_Handle;
        x = requests.get(CheckConsentURL , headers = headers)
        json_data = json.loads(x.text)
        print(json_data)
        print("********",json_data["ConsentStatus"]["status"] == "READY")
        
        #If consent is accepted
        if(json_data["ConsentStatus"]["status"] == "READY"):
            #Render the dashboard page here
            context = {
            'urldone' : "DashBoard",
            'message': 'Your consent is Approved you are good to go.',
            'img': 'Approved.jpg',
            'consent' : 'Ready'
            }
            user = request.user
            a = Consent.objects.get(user = user)
            a.ConsentID = json_data["ConsentStatus"]["id"]
            a.save()
           
            return redirect("DataDashBoard")
        else: 
            urlapprove = "https://anumati.setu.co/" + local_Consent_Handle;
            context = {
                'message': 'Your Consent is pending Kindly make the Approval and then click on done',
                'img': 'Siging.jpg',
                'consent' : 'pending',
                'urlapprove' : urlapprove,
            }
            return render(request,"ConsentFlow.html",context)

    except Exception as e:
        print(e)

        context = {
                'message': 'Please make the Consent to do Go further',
                'img': 'none.jpg',
               
        }
        return render(request,"ConsentFlow.html",context)

    return HttpResponse("<h1>This is the consent page</h1>")


@login_required(login_url = "index")
def DataDashBoard(request):
    user = request.user
    loc_Consent_ID = Consent.objects.get(user = user).ConsentID
    # print('***************' , loc_Consent_ID) 

    UrlSigned = base_url + "/Consent/" + loc_Consent_ID
    Fetch_Signed_Consent = requests.get(UrlSigned , headers = headers)
    json_data = json.loads(Fetch_Signed_Consent.text)
    signedConsent = json_data["signedConsent"]

    # Generate Key material
    KeyMaterialURL = setu_rahasya_url + "/ecc/v1/generateKey"
    KeyMaterialData = requests.get(KeyMaterialURL)

    # print("**************" , KeyMaterialData.text)
    KeyMaterialData_JSON = json.loads(KeyMaterialData.text)
    base64YourNonce = KeyMaterialData_JSON["KeyMaterial"]["Nonce"]
    ourPrivateKey = KeyMaterialData_JSON["privateKey"]


    #Request FI DATA
    UrlFIdata = base_url + "/FI/request"
    Request_FI_Data["KeyMaterial"] = KeyMaterialData_JSON["KeyMaterial"]
    Request_FI_Data["txnid"] = str(uuid.uuid1())
    Request_FI_Data["Consent"]["id"] = loc_Consent_ID
    Request_FI_Data["Consent"]["digitalSignature"] = signedConsent.split(".")[2]
    Request_FI_Data_post = requests.post(UrlFIdata, headers = headers , json = Request_FI_Data)
    print("************",Request_FI_Data_post.text)

    Request_FI_Data_post_json = json.loads(Request_FI_Data_post.text)
    aa_session_id = Request_FI_Data_post_json["sessionId"]
    
    # Fetch The data
    Fetch_Data_URL = base_url + "/FI/fetch/" + aa_session_id
    Fetch_Data = requests.get(Fetch_Data_URL , headers = headers)
    Fetch_Data_JSON = json.loads(Fetch_Data.text)
    

    #Decrypt Data
    base64Data_bank = Fetch_Data_JSON["FI"][1]["data"][0]["encryptedFI"]
    base64RemoteNonce_bank = Fetch_Data_JSON["FI"][1]["KeyMaterial"]["Nonce"]
    #base64YourNonce = Defined from the above Generating Key material step
    #ourPrivateKey = Generated above Generating Key material step
    remoteKeyMaterial_bank = Fetch_Data_JSON["FI"][1]["KeyMaterial"]

    Decrpyt_Body["base64Data"] = base64Data_bank;
    Decrpyt_Body["base64RemoteNonce"] = base64RemoteNonce_bank;
    Decrpyt_Body["base64YourNonce"] = base64YourNonce;
    Decrpyt_Body["ourPrivateKey"] = ourPrivateKey;
    Decrpyt_Body["remoteKeyMaterial"] = remoteKeyMaterial_bank;
    
    url_Decrypt = setu_rahasya_url + "/ecc/v1/decrypt"
    Data_Decrypt = requests.post(url_Decrypt,headers = headers , json = Decrpyt_Body)
    Data_Decrypt_JSON = json.loads(Data_Decrypt.text)

    Base64_Data_bank = Data_Decrypt_JSON["base64Data"]
    Decoded_Data_bank = base64.b64decode(Base64_Data_bank)  
    Decoded_Data_Bank_JSON = json.loads(Decoded_Data_bank)  
    
    '''
    Informaion sent through the content is 
    content = {"month_expense" : "{:,}".format(month_expense), "balance" : currentBalance , Transation : [{naration , date , amount , nature},{naration , data , amount , nature},...] }
    '''

    Bank_info_rel = Bank(request, Decoded_Data_Bank_JSON)
    content = Bank_info_rel
    print("&&&&&&&&&&&&&&&&&&&&&&" ,  content)

    print('\n' ,Bank_info_rel,'\n' )
    return render(request,"DashBoard2.html",content)



def data(request):
    user = request.user
    loc_Consent_ID = Consent.objects.get(user = user).ConsentID
    print('***************' , loc_Consent_ID) 

    UrlSigned = base_url + "/Consent/" + loc_Consent_ID
    Fetch_Signed_Consent = requests.get(UrlSigned , headers = headers)
    json_data = json.loads(Fetch_Signed_Consent.text)
    signedConsent = json_data["signedConsent"]


    # Generate Key material
    KeyMaterialURL = setu_rahasya_url + "/ecc/v1/generateKey"
    KeyMaterialData = requests.get(KeyMaterialURL)
    KeyMaterialData_JSON = json.loads(KeyMaterialData.text)
    base64YourNonce = KeyMaterialData_JSON["KeyMaterial"]["Nonce"]
    ourPrivateKey = KeyMaterialData_JSON["privateKey"]


    #Request FI DATA
    UrlFIdata = base_url + "/FI/request"
    Request_FI_Data["KeyMaterial"] = KeyMaterialData_JSON["KeyMaterial"]
    Request_FI_Data["txnid"] = str(uuid.uuid1())
    Request_FI_Data["Consent"]["id"] = loc_Consent_ID
    Request_FI_Data["Consent"]["digitalSignature"] = signedConsent.split(".")[2]
    Request_FI_Data_post = requests.post(UrlFIdata, headers = headers , json = Request_FI_Data)
    # print(Request_FI_Data)

    Request_FI_Data_post_json = json.loads(Request_FI_Data_post.text)
    aa_session_id = Request_FI_Data_post_json["sessionId"]
    
    # Fetch The data
    Fetch_Data_URL = base_url + "/FI/fetch/" + aa_session_id
    Fetch_Data = requests.get(Fetch_Data_URL , headers = headers)
    Fetch_Data_JSON = json.loads(Fetch_Data.text)
    

    #Decrypt Data
    base64Data = Fetch_Data_JSON["FI"][0]["data"][0]["encryptedFI"]
    base64RemoteNonce = Fetch_Data_JSON["FI"][0]["KeyMaterial"]["Nonce"]
    #base64YourNonce = Defined from the above Generating Key material step
    #ourPrivateKey = Generated above Generating Key material step
    remoteKeyMaterial = Fetch_Data_JSON["FI"][0]["KeyMaterial"]

    Decrpyt_Body["base64Data"] = base64Data;
    Decrpyt_Body["base64RemoteNonce"] = base64RemoteNonce;
    Decrpyt_Body["base64YourNonce"] = base64YourNonce;
    Decrpyt_Body["ourPrivateKey"] = ourPrivateKey;
    Decrpyt_Body["remoteKeyMaterial"] = remoteKeyMaterial;
    
    url_Decrypt = setu_rahasya_url + "/ecc/v1/decrypt"
    Data_Decrypt = requests.post(url_Decrypt,headers = headers , json = Decrpyt_Body)
    Data_Decrypt_JSON = json.loads(Data_Decrypt.text)

    Base64_Data = Data_Decrypt_JSON["base64Data"]
    Decoded_Data = base64.b64decode(Base64_Data)  
    Decoded_Data_JSON = json.loads(Decoded_Data)  

    return render(request,"data.html",{"DataJson":Decoded_Data_JSON , "Heading" : Fetch_Data_JSON["FI"][0]["fipId"]})



def Bank(request,bank_data):
    elements = len(bank_data["account"]["transactions"]["transaction"])
    month_expense = 0
    currentBalance = bank_data["account"]["summary"]["currentBalance"]
    currentmonth = 13
    cnt = 0
    transactions = []
    
    for i in range(elements-1 , 0 , -1):
        month = int(bank_data["account"]["transactions"]["transaction"][i]["valueDate"].split('-')[1])
        if(currentmonth == 13):
            currentmonth = month
        
        if(currentmonth != month):
            break
        #Add the transation details to the screen to make user understand the recent passbook history.
        
        if(cnt < 4):
            a = [(bank_data["account"]["transactions"]["transaction"][i]["narration"]) , bank_data["account"]["transactions"]["transaction"][i]["valueDate"] , bank_data["account"]["transactions"]["transaction"][i]["amount"]]
            print("\n A data \n" , a , '\n')
            transactions.append(a)
            cnt += 1

        if(bank_data["account"]["transactions"]["transaction"][i]["type"] == "DEBIT"):
            spending = float(bank_data["account"]["transactions"]["transaction"][i]["amount"])
            month_expense += spending
            
         
    
    information_exchange = {"month_expense" : "{:,}".format(month_expense), "balance" : currentBalance , "transaction" : transactions}
    return information_exchange


def profile(request):
    return render(request,"profile.html")

def checked(request):
    print('\n' , request.GET , '\n')
    user_consent_obj = list(request.GET.values())
    user = request.user
    b = Consent(user = user , consent_obj = user_consent_obj)
    b.save()
    print(" all values in dictionary are:",user_consent_obj)
    return redirect("/ConsentFlow")