
from django.db import models

class harshbank(models.Model):
    accountno = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    balance = models.CharField(max_length=40)
    
class signUp(models.Model):
    username = models.CharField(max_length=30)
    phone_no = models.CharField(max_length=10)
    emailid = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    usertype = models.CharField(max_length=30)
    
class transactions(models.Model):
    user_id=models.IntegerField()
    accountno = models.CharField(max_length=40)
    t_type = models.CharField(max_length=30)
    amount = models.CharField(max_length=30)
    balance = models.IntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    
class FD(models.Model):
    accountno = models.IntegerField()
    amount = models.IntegerField()
    time_period = models.IntegerField()
    interest_rate = models.IntegerField()
    date_time = models.DateTimeField(auto_now_add=True)
    maturity_amount = models.IntegerField()
    maturity_date= models.DateTimeField()