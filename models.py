from django.db import models
from django.contrib.auth.models import User


# =========================
# PREDICTION MODEL
# =========================
class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Personal Information
    gender = models.CharField(max_length=10)
    married = models.CharField(max_length=10)
    dependents = models.CharField(max_length=10)
    education = models.CharField(max_length=20)
    self_employed = models.CharField(max_length=10)
    
    # Employment Information
    employment_status = models.CharField(max_length=20, default='Employed')
    years_employed = models.FloatField(default=0)
    employment_type = models.CharField(max_length=50, default='Private')

    # Financial Information
    applicant_income = models.FloatField()
    coapplicant_income = models.FloatField()
    total_income = models.FloatField(default=0)
    existing_debt = models.FloatField(default=0)
    annual_expenses = models.FloatField(default=0)
    
    # Loan Details
    loan_amount = models.FloatField()
    loan_term = models.FloatField()
    loan_purpose = models.CharField(max_length=50, default='Home')
    down_payment = models.FloatField(default=0)
    credit_history = models.FloatField()
    property_area = models.CharField(max_length=20)
    loan_type = models.CharField(max_length=20)
    
    # Collateral
    collateral_available = models.CharField(max_length=20, default='No')
    collateral_value = models.FloatField(default=0)

    # Prediction Results
    result = models.CharField(max_length=20)
    confidence = models.FloatField()
    explanation = models.TextField(default='')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(default=0)  # in seconds

    def __str__(self):
        return f"{self.user.username} - {self.result} ({self.created_at.strftime('%Y-%m-%d')})"
    
    class Meta:
        ordering = ['-created_at']


# =========================
# USER ACTIVITY MODEL
# =========================
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    
# predictor/models.py
from django.db import models
from django.contrib.auth.models import User

class LoanPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    applicant_income = models.FloatField()
    loan_amount = models.FloatField()
    credit_history = models.IntegerField()
    result = models.CharField(max_length=20) # Approved or Rejected
    confidence = models.FloatField(default=80.0)
    created_at = models.DateTimeField(auto_now_add=True)