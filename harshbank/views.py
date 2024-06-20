from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from .models import harshbank, signUp, transactions, FD
from django.utils import timezone
from datetime import datetime
import sqlite3

def index(request):
    template = loader.get_template('00index.html')
    return HttpResponse(template.render())

def signup(request):
    template = loader.get_template('00signup.html')
    return HttpResponse(template.render())

def cust_storedetails(request):
    deets = signUp(username=request.GET['t1'],phone_no = request.GET['t2'], emailid = request.GET['t3'], password = request.GET['t4'] )
    confpassword = request.GET['t5']
    if(deets.username == '' or deets.emailid == '' or deets.password == '' or deets.phone_no == ''):
        return HttpResponse("fields can not be blank")
    
    elif(deets.password != confpassword):
        return HttpResponse("Passwords don't match")    
    
    else:
        deets.usertype = "Customer"
        deets.save()
        template = loader.get_template('01login.html')
        return HttpResponse(template.render()) 

def login(request):
    template = loader.get_template('01login.html')
    return HttpResponse(template.render())

def login_check_details(request):
    if request.method == 'GET':
        a = request.GET['t2']       #email
        b = request.GET['t3']       #password 
        
        if(a == '' or b== '' ):
            return HttpResponse("fields can not be blank")
        
        else:
            try:
                user = signUp.objects.get(emailid = a, password = b)
                
                if user.usertype == 'Admin':
                    request.session['id'] = user.id
                    # Get a list of all IDs present in the Bank model
                    bank_acc_holder_ids = harshbank.objects.values_list('id', flat=True)

                    # Get all signUP objects
                    all_customer_ids = signUp.objects.values_list('id', flat=True)

                    # Convert bank_acc_holder_ids to a list
                    bank_acc_holder_ids_list = list(bank_acc_holder_ids)

                    # Get the remaining IDs that are not in bank_acc_holder_ids
                    remaining_customer_ids = set(all_customer_ids) - set(bank_acc_holder_ids_list)

                    # Retrieve the signUP objects corresponding to the remaining IDs
                    remaining_customers = signUp.objects.filter(id__in=remaining_customer_ids)
                    bank = harshbank.objects.all()
                    total_balance = sum(item.balance for item in bank)
                    return render(request, '10dashboard.html',{'remaining_customers': remaining_customers, "user":user, "bank":bank, "total_balance":total_balance}) 
                
                elif user.usertype == 'Customer':
                    request.session['id'] = user.id
                    user1 = harshbank.objects.get(id=user.id)
                    return render(request, '02login_success_customer.html', {'user': user,'user1': user1})
                
                else:
                    return HttpResponse("Invalid user type")
                
            except signUp.DoesNotExist:
                return HttpResponse("The details you have entered is incorrrect")
            
    else:
        return HttpResponse("Invalid request method")
    
def logout(request):
        request.session.flush()
        return redirect('index')

def profile(request):
    user_id = request.session.get('id')
    user1 = harshbank.objects.get(id=user_id)
    user = signUp.objects.get(id=user_id)
    return render(request, '02login_success_customer.html', {'user': user,'user1': user1})
      
def editprofile(request):
    user_id = request.session.get('id')
    
    if user_id is not None:
        user = signUp.objects.get(id=user_id)
        user2 = harshbank.objects.get(id=user_id)
        return render(request, '04editprofile.html', {'user': user, 'user2': user2})

def update_editprofile(request):
    user_id = request.session.get('id')
    
    if user_id is not None:
        a = request.GET.get('t1')
        b = request.GET.get('t2')
        c = request.GET.get('t3')
        
        try:
            u = signUp.objects.get(id=user_id)
            u.username = a
            u.emailid = b
            u.phone_no = c
            u.save()
            
            bankDetails = harshbank.objects.get(id = user_id)
            bankDetails.name = a
            bankDetails.save()
            return redirect('/profile/')
        except signUp.DoesNotExist:  
            return HttpResponse("User Profile Does Not Exist")
        
    else:
        return HttpResponse("User ID Not Found in Session")

def transaction(request):
    user_id = request.session.get('id')
    
    if user_id:
        user = harshbank.objects.get(id=user_id)
        account = user.accountno
    data = transactions.objects.filter(accountno=account)
    
    total_credit_amount = sum(transaction.amount for transaction in data.filter(t_type='Credit'))
    total_debit_amount = sum(transaction.amount for transaction in data.filter(t_type='Debit'))
    
    return render(request, '05transactions.html', 
                    {   'data': data, 
                        'user': user , 
                        'total_credit_amount':total_credit_amount,  
                        'total_debit_amount':total_debit_amount 
                    })
   
def deposits(request):
    template = loader.get_template('06deposits.html')
    return HttpResponse(template.render())  

def savings(request):
    user_id = request.session.get('id')
    
    if user_id is not None:
        user = harshbank.objects.get(id=user_id) 
    return render(request, '07savings.html', {'user': user})

def fd(request):
    user_id = request.session.get('id')
    date_time = timezone.now()
    
    if user_id is not None:
        user = harshbank.objects.get(id=user_id) 
    return render(request, '08fd.html', {'user': user, 'date_time':date_time})

def fd_details(request):
    user_id = request.session.get('id')
    
    if user_id is not None:
        user = harshbank.objects.get(id=user_id)
        account = user.accountno

    b = int(request.GET.get('t2'))   #fd amount
    start_date_str  = request.GET['t3']   #start date
    end_date_str = request.GET['t6']   #end date
    d = int(request.GET.get('t4'))   #interest rate
    e = request.GET.get('t5')        #date and time
    
    # Convert string dates to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    # Calculate the time period in days
    time_period = (end_date - start_date).days
    
    # Convert time_period to years
    time_in_years = float(time_period / 365.0)
    print(time_in_years)
 
    principal = b   # fd amount
    rate = d      # rate of interest
    n = 1           #number of times interest rate applied in a year
    maturity_amount = (principal * (1 + (rate/100)/n) ** (n * time_in_years))
    
    if b<user.balance:        
        fd = FD(accountno = account, 
                amount= b, 
                time_period = time_period, 
                interest_rate = rate, 
                date_time = e, 
                maturity_amount = maturity_amount,
                maturity_date = end_date_str)
        fd.save()
        
        user.balance -= int(b)
        user.save()
        t = transactions(user_id=user_id, 
                        accountno = account, 
                        t_type="Debit", 
                        amount = b, 
                        balance = user.balance,
                        date_time=timezone.now())
        t.save()
        return HttpResponse("A FD in your account has been added")
    else:
        return HttpResponse("Balance is low")
 
    

def showfd(request):
    user_id = request.session.get('id')
    
    if user_id:
        user = harshbank.objects.get(id=user_id)
        account = user.accountno
        
        if FD.objects.filter(accountno=account).exists():
            data = FD.objects.filter(accountno=account)
            
        else:
            return HttpResponse("You have no FD right now")
    return render(request, '09showfd.html', {'data':data})
    
def dashboard(request):
    
    # Get a list of all IDs present in the Bank model
    bank_acc_holder_ids = harshbank.objects.values_list('id', flat=True)

    # Get all signUP objects
    all_customer_ids = signUp.objects.values_list('id', flat=True)

    # Convert bank_acc_holder_ids to a list
    bank_acc_holder_ids_list = list(bank_acc_holder_ids)

    # Get the remaining IDs that are not in bank_acc_holder_ids
    remaining_customer_ids = set(all_customer_ids) - set(bank_acc_holder_ids_list)

    # Retrieve the signUP objects corresponding to the remaining IDs
    remaining_customers = signUp.objects.filter(id__in=remaining_customer_ids)

    bank = harshbank.objects.all()
    total_balance = sum(item.balance for item in bank)
    
    # if(data.id!=bank.id):
    #     signup_data = {'data': data}
    return render(request, '10dashboard.html',{'total_balance':total_balance, 'remaining_customers':remaining_customers})
        
def addaccounts(request, user_id):
    if harshbank.objects.filter(id=user_id).exists():
        return HttpResponse("Account already exists")
    else:
        user = signUp.objects.get(id=user_id)
        return render(request, '11createaccount.html', {'user': user})

def storedetails(request):
    
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        account_number = request.GET.get('account_number')
        user_name = request.GET.get('user_name')
        balance = request.GET.get('balance')
        
        # Check if the account number already exists
        if harshbank.objects.filter(id=user_id).exists():
            return HttpResponse("Account already exists")
        
        else:    
        # Create and save the new account
            bank = harshbank(
                id=user_id,
                accountno=account_number,
                name=user_name,
                balance=balance,
            )
            bank.save()
            return HttpResponse("Account added successfully!")
        
    else:
        return HttpResponse("Invalid request method")

  
def listaccounts(request):
    products = harshbank.objects.all()
    products2 = signUp.objects.all()
    return render(request, 'admin-templates/tables.html', {'products': products , 'products2': products2})  

def users(request):
    products = harshbank.objects.all()
    context = {'products': products}
    return render(request, 'admin-templates/users.html',context) 
  
def withdraw(request):
    template = loader.get_template('12withdraw.html')
    return HttpResponse(template.render())

def myWithdraw(request):
    a = request.GET['t1']       #account no
    b = request.GET['t2']       #amount
    
    try:
            account = harshbank.objects.get(accountno=a)
            user_id=account.id
            account.balance -= int(b)
            account.save()
            t = transactions(user_id=user_id, accountno = a, t_type="Debit", amount = b, balance = account.balance ,date_time=timezone.now())
            t.save()
            return HttpResponse("Money withdrawn successfully!")
        
    except harshbank.DoesNotExist:
            return HttpResponse("Account not found.") 

def deposit(request):
    template = loader.get_template('13deposit.html')
    return HttpResponse(template.render())

def myDeposit(request):
    a = request.GET['t1']
    b = request.GET['t2']
    
    try:
            m = harshbank.objects.get(accountno=a)
            user_id= m.id
            m.balance = int(m.balance) + int(b)
            m.save()
            t = transactions(user_id = user_id, accountno = a, t_type="Credit", amount = b, balance = m.balance, date_time=timezone.now())
            t.save()
            return HttpResponse("Money deposited successfully!")
        
    except harshbank.DoesNotExist:
            return HttpResponse("Account number not provided.")
    
def delete(request, user_id):
    user = harshbank.objects.filter(id=user_id)
    
    if user.exists():
        user1 = user.first()
        user1.delete()
        return HttpResponse("Account deleted successfully!")
    
    else:
        return HttpResponse("Account number not provided.")

def update(request, user_id):
    user = signUp.objects.get(id=user_id)
    details = harshbank.objects.get(id = user_id)
    return render(request, '14update.html', {'user': user, 'details':details})

def myUpdate_store(request, user_id):
    a =request.GET['t1']      # username
    b =request.GET['t2']      # emailid
    c =request.GET['t3']      # phone number
    d = request.GET['t4']     #id
    
    try:
        details = signUp.objects.get(id = d)
        details.username = a
        details.emailid = b
        details.phone_no = c
        details.save()
        
        bankDetails = harshbank.objects.get(id = d)
        bankDetails.name = a
        bankDetails.save()
        return HttpResponse("The details have been updated successfully")

    except signUp.DoesNotExist:  
            return HttpResponse("User Profile Does Not Exist")
        