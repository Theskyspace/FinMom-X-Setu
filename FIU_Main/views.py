from django.shortcuts import render, HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
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

def ProcessingData(request):
    user = request.user
    loc_Consent_ID = Consent.objects.get(user = user).ConsentID
    print('***************' , loc_Consent_ID) 
    
    # 3rd step of the postman thing
    UrlSigned = base_url + "/Consent/" + loc_Consent_ID
    Fetch_Signed_Consent = requests.get(UrlSigned , headers = headers)
    json_data = json.loads(Fetch_Signed_Consent.text)
    signedConsent = json_data["signedConsent"]


    # Generate Key material
    KeyMaterialURL = setu_rahasya_url + "/ecc/v1/generateKey"
    KeyMaterialData = requests.get(KeyMaterialURL)
    print("****************KeyMaterialData********************    " , KeyMaterialData )
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
    
    base64YourNonce = KeyMaterialData_JSON["KeyMaterial"]["Nonce"]
    ourPrivateKey = KeyMaterialData_JSON["privateKey"]

    print('\n\n\n')

    Assets_Amount = 0;
    Liability_Amount = 0; 
    investment = 0;
    for elements in Fetch_Data_JSON["FI"]:
        base64RemoteNonce = elements["KeyMaterial"]["Nonce"]
        print(elements["fipId"])
        remoteKeyMaterial = elements["KeyMaterial"]
        for data in elements["data"]:
            base64Data = data["encryptedFI"]
                       
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
            type = Decoded_Data_JSON["account"]["type"] 
            
            print(type)

            if(type == "deposit"):       
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentBalance"])
                
            elif(type in ["term_deposit" , "recurring_deposit" , "cd" , "idr" , "mutual_funds" , "bonds" , "debentures" , "etf" , "nps", "govt_securities" , "cp" , "reit" , "invit" , "aif" , "sip" , "equities" , "cis"]):
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentValue"])
                investment += float(Decoded_Data_JSON["account"]["summary"]["currentValue"])
            elif(type in ["credit_card"]):
                Liability_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentDue"])

            elif(type in ["insurance_policies"]):
                # Insurance ammount
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["coverAmount"])
            elif(type in ["ulip",]):
                # Insurance ammount
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["sumAssured"])
            elif(type in ["ppf" , "epf"]):
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentBalance"])
                investment += float(Decoded_Data_JSON["account"]["summary"]["currentBalance"])
   
    Networth = Assets_Amount - Liability_Amount
    # Feeding things into the database.
    database_instance = Consent.objects.get(user = user)
    database_instance.Investments = investment
    database_instance.Networth = Networth
    # database_instance.Last_Updated =  timezone.now()
    database_instance.save()

    return redirect("/DashBoard")

# Loading screen view
def load(request):
    return render(request , "Firsttime.html")

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
            print("\n\n\nLocal Consent : " , local_Consent_Handle , "\n\n")
       
    except Exception as e:
        print("\n\nConsent Flow 1st Try\n" , e , "\n\n\n")
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
            
            # To check if the investments are made or not
            if(a.Investments == -1):
                return redirect("load")

            a.save()

            #Add here if the data of investment and networth is not available
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
        print("\n\nConsent Flow 2st Try\n" , e , "\n\n\n")

        context = {
                'message': 'Please make the Consent to do Go further',
                'img': 'none.jpg',
               
        }
        return render(request,"ConsentFlow.html",context)

    return HttpResponse("<h1>This is the consent page</h1>")

# Dashboard view 
@login_required(login_url = "index")
def DataDashBoard(request):
    print("\n\n\nRendering Dashboard\n\n\n")

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

    print("**************\n\n\n" , KeyMaterialData.text)
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


    print("\n\n\nFetch Data Json : ", Fetch_Data_JSON , "\n\n\n")
    for elements in Fetch_Data_JSON["FI"]:
            base64RemoteNonce = elements["KeyMaterial"]["Nonce"]
            print(elements["fipId"])
            remoteKeyMaterial = elements["KeyMaterial"]
            for data in elements["data"]:
                base64Data = data["encryptedFI"]
                        
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
                type = Decoded_Data_JSON["account"]["type"] 
                

                if(type == "deposit"):      
                    '''
                    Informaion sent through the content is 
                    content = {"month_expense" : "{:,}".format(month_expense), "balance" : currentBalance , Transation : [{naration , date , amount , nature},{naration , data , amount , nature},...] }
                    '''

                    Bank_info_rel = Bank(request,  Decoded_Data_JSON , 4 , "dashboard")
                    content = Bank_info_rel
                    content["investments"] = Consent.objects.get(user = user).Investments
                    content["networth"] = Consent.objects.get(user = user).Networth
                    # content["lastupdated"] = Consent.objects.get(user = user).Last_Updated

                    print("\n\n\nContent : \n" ,  content)

                    print('\n' ,Bank_info_rel,'\n' )
                    print("\n\nRendering DashBoard\n\n")
                    return render(request,"DashBoard2.html",content)

# Passbook
@login_required(login_url = "index")
def Passbook(request):
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

    print("**************\n\n\n" , KeyMaterialData.text)
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


    print("\n\n\nFetch Data Json : ", Fetch_Data_JSON , "\n\n\n")
    for elements in Fetch_Data_JSON["FI"]:
            base64RemoteNonce = elements["KeyMaterial"]["Nonce"]
            print(elements["fipId"])
            remoteKeyMaterial = elements["KeyMaterial"]
            for data in elements["data"]:
                base64Data = data["encryptedFI"]
                        
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
                type = Decoded_Data_JSON["account"]["type"] 
                

                if(type == "deposit"):      
                    '''
                    Informaion sent through the content is 
                    content = {"month_expense" : "{:,}".format(month_expense), "balance" : currentBalance , Transation : [{naration , date , amount , nature},{naration , data , amount , nature},...] }
                    '''

                    Bank_info_rel = Bank(request,  Decoded_Data_JSON , 30 , "Passbook")
                    content = Bank_info_rel

                    print("\n\n\nContent : \n" ,  content)

                    return render(request , "Passbook.html" , content)

# This is a testing fuction for the data fuctionality
@login_required(login_url = "index")
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
    base64Data = Fetch_Data_JSON["FI"][1]["data"][2]["encryptedFI"]
    base64RemoteNonce = Fetch_Data_JSON["FI"][1]["KeyMaterial"]["Nonce"]
    #base64YourNonce = Defined from the above Generating Key material step
    #ourPrivateKey = Generated above Generating Key material step
    remoteKeyMaterial = Fetch_Data_JSON["FI"][1]["KeyMaterial"]

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

    return render(request,"data.html",{"DataJson":Fetch_Data_JSON , "Heading" : Fetch_Data_JSON["FI"][0]["fipId"]})

# Networth breakdown fuction
@login_required(login_url = "index")
def breakout(request):
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
    print("****************KeyMaterialData********************    " , KeyMaterialData )
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
    
    base64YourNonce = KeyMaterialData_JSON["KeyMaterial"]["Nonce"]
    ourPrivateKey = KeyMaterialData_JSON["privateKey"]

    print('\n\n\n')

    Assets = []
    Liability = []
    Assets_Amount = 0;
    Liability_Amount = 0; 
    for elements in Fetch_Data_JSON["FI"]:
        base64RemoteNonce = elements["KeyMaterial"]["Nonce"]
        print(elements["fipId"])
        remoteKeyMaterial = elements["KeyMaterial"]
        for data in elements["data"]:
            base64Data = data["encryptedFI"]
                       
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
            type = Decoded_Data_JSON["account"]["type"] 
            
            print(type)

            if(type == "deposit"):       
                a = {
                    "type" : type,
                    "value" : "+" + str(Decoded_Data_JSON["account"]["summary"]["currentBalance"]),
                }
                Assets.append(a)
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentBalance"])
                
            elif(type in ["term_deposit" , "recurring_deposit" , "cd" , "idr" , "mutual_funds" , "bonds" , "debentures" , "etf" , "nps", "govt_securities" , "cp" , "reit" , "invit" , "aif" , "sip" , "equities" , "cis"]):
                a = {
                    "type" : type,
                    "value" :  "+" + str(Decoded_Data_JSON["account"]["summary"]["currentValue"]),
                 
                }
                Assets.append(a)
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentValue"])
            elif(type in ["credit_card"]):
                a = {
                "type" : type,
                "value" :  "-" + str(Decoded_Data_JSON["account"]["summary"]["currentDue"]),
                }
                Liability.append(a)
                Liability_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentDue"])

            elif(type in ["insurance_policies"]):
            # Insurance ammount
                a = {
                        "type" : type,
                        "value" : "+" + str(Decoded_Data_JSON["account"]["summary"]["coverAmount"]),
                      
                    }
                Assets.append(a)
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["coverAmount"])
            elif(type in ["ulip",]):
                # Insurance ammount
                a = {
                    "type" : type,
                    "value" : "+" + str(Decoded_Data_JSON["account"]["summary"]["sumAssured"]),
        
                }
                Assets.append(a)
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["sumAssured"])
            elif(type in ["ppf" , "epf"]):
                Assets_Amount += float(Decoded_Data_JSON["account"]["summary"]["currentBalance"])


        print("--------------------------------------------")
    print('\n\n\n')


   
    Networth = Assets_Amount - Liability_Amount
    return render(request,"breakout.html",{"Assets" : Assets , "Liability" : Liability , "Assets_Amount" : Assets_Amount , "Liability_Amount" : Liability_Amount , "Networth" : Networth})

# Information managment Fuctions
@login_required(login_url = "index")
def Bank(request,bank_data,range_no , purpose):
    elements = len(bank_data["account"]["transactions"]["transaction"])
    month_expense = 0
    currentBalance = bank_data["account"]["summary"]["currentBalance"]
    currentmonth = 13
    cnt = 0
    transactions = []
    
    for i in range(elements-1 , -1 , -1):
        month = int(bank_data["account"]["transactions"]["transaction"][i]["valueDate"].split('-')[1])
        if(currentmonth == 13):
            currentmonth = month
        
        if(currentmonth != month and purpose != "Passbook"):
            break
        #Add the transation details to the screen to make user understand the recent passbook history.
        
        if(cnt <= range_no):
            if(type == "DEBIT"):
                amount = "-" + u"\u20B9 " + bank_data["account"]["transactions"]["transaction"][i]["amount"]
            else:
                amount = "+" + u"\u20B9 " + bank_data["account"]["transactions"]["transaction"][i]["amount"]

            if(purpose ==  "Passbook"):
                a = [(bank_data["account"]["transactions"]["transaction"][i]["mode"]),(bank_data["account"]["transactions"]["transaction"][i]["narration"]), bank_data["account"]["transactions"]["transaction"][i]["valueDate"] , amount]
            else:
                a = [(bank_data["account"]["transactions"]["transaction"][i]["narration"]) , bank_data["account"]["transactions"]["transaction"][i]["valueDate"] , amount]
            print("\n A data \n" , a , '\n')
            print("\n\nAmount of transation\n\n" , len(bank_data["account"]["transactions"]["transaction"]) , "\n\n\n")
            transactions.append(a)
            cnt += 1

        if(bank_data["account"]["transactions"]["transaction"][i]["type"] == "DEBIT"):
            spending = float(bank_data["account"]["transactions"]["transaction"][i]["amount"])
            month_expense += spending
            
    
    
    information_exchange = {"month_expense" : "{:,}".format(month_expense), "balance" : currentBalance , "transaction" : transactions}
    return information_exchange

@login_required(login_url = "index")
def profile(request):
    return render(request,"Profile.html")

def goals(request):
    return render(request,"goals.html")

@login_required(login_url = "index")
def checked(request):
    print('\n' , request.GET , '\n')
    user_consent_obj = list(request.GET.values())
    user = request.user
    try:
        b = Consent(user = user , consent_obj = user_consent_obj)
        b.save()
    except:
        a = Consent.objects.get(user = user)
        a.ConsentHandle = ""
        a.ConsentID = ""
        a.consent_obj = user_consent_obj
        a.save()

    print(" all values in dictionary are:",user_consent_obj)
    return redirect("/ConsentFlow")