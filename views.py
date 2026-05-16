from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Prediction

import pandas as pd
import joblib
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# =========================
# API PREDICT
# =========================
@csrf_exempt
def api_predict(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'})

    try:
        data = json.loads(request.body)

        applicant_income = float(data.get('applicant_income', 0))
        coapplicant_income = float(data.get('coapplicant_income', 0))
        loan_amount = float(data.get('loan_amount', 0))
        loan_term = float(data.get('loan_term', 360))
        credit_history = float(data.get('credit_history', 1))

        model, encoders = load_model()

        if model is None:
            return JsonResponse({'error': 'Model not loaded'})

        # Prepare data
        input_data = {
            'Gender': data.get('gender', 'Male'),
            'Married': data.get('married', 'Yes'),
            'Dependents': data.get('dependents', '0'),
            'Education': data.get('education', 'Graduate'),
            'Self_Employed': data.get('self_employed', 'No'),
            'ApplicantIncome': applicant_income,
            'CoapplicantIncome': coapplicant_income,
            'LoanAmount': loan_amount,
            'Loan_Amount_Term': loan_term,
            'Credit_History': credit_history,
            'Property_Area': data.get('property_area', 'Urban'),
            'Loan_Type': data.get('loan_type', 'Home'),
        }

        input_data['Total_Income'] = applicant_income + coapplicant_income

        columns = [
            'Gender','Married','Dependents','Education',
            'Self_Employed','ApplicantIncome','CoapplicantIncome',
            'LoanAmount','Loan_Amount_Term','Credit_History',
            'Property_Area','Loan_Type','Total_Income'
        ]

        row = []
        for col in columns:
            val = input_data[col]
            if col in encoders:
                val = encoders[col].transform([val])[0]
            row.append(float(val))

        df = pd.DataFrame([row], columns=columns)

        pred = model.predict(df)[0]
        prob = model.predict_proba(df)[0]

        result = encoders['Loan_Status'].inverse_transform([pred])[0]
        confidence = round(max(prob) * 100, 2)

        return JsonResponse({
            'result': result,
            'confidence': confidence
        })

    except Exception as e:
        return JsonResponse({'error': str(e)})
# =========================
# USER STATS
# =========================
@login_required
def user_stats(request):
    qs = Prediction.objects.all()

    return render(request, 'user_stats.html', {
        'total': qs.count(),
        'approved': qs.filter(result="Approved").count(),
        'rejected': qs.filter(result="Rejected").count()
    })

# =========================
# LOAD MODEL
# =========================
def load_model():
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))
        encoders = joblib.load(os.path.join(BASE_DIR, "encoders.pkl"))
        return model, encoders
    except:
        return None, None


# =========================
# AI EXPLANATION
# =========================
def explain(data):
    reasons = []

    if data['Credit_History'] == 1:
        reasons.append("✔ Good credit history")
    else:
        reasons.append("❌ Poor credit history")

    return reasons


# =========================
# HOME
# =========================
def home(request):
    return redirect('dashboard')


# =========================
# REGISTER
# =========================
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'register.html', {
                'error': 'All fields are required'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'error': 'Username already exists'
            })

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'register.html')


# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )

        if user:
            login(request, user)
            return redirect('dashboard')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect('login')


    logout(request)
    return redirect('login')


# =========================
# DASHBOARD
# =========================
@login_required
def dashboard(request):
    qs = Prediction.objects.filter(user=request.user)

    return render(request, 'dashboard.html', {
        'total': qs.count(),
        'approved': qs.filter(result="Approved").count(),
        'rejected': qs.filter(result="Rejected").count()
    })


# =========================
# HISTORY
# =========================
@login_required
def history(request):
    data = Prediction.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'data': data})

# =========================
# DASHBOARD API
# =========================
@login_required
def dashboard_data(request):

    qs = Prediction.objects.filter(
        user=request.user
    )

    return JsonResponse({

        'total': qs.count(),

        'approved': qs.filter(
            result="Approved"
        ).count(),

        'rejected': qs.filter(
            result="Rejected"
        ).count()

    })
# =========================
# PREDICT
# =========================
@login_required
def predict(request):

    context = {}

    if request.method == 'POST':

        try:

            applicant_income = float(
                request.POST.get('applicant_income', 0)
            )

            coapplicant_income = float(
                request.POST.get('coapplicant_income', 0)
            )

            loan_amount = float(
                request.POST.get('loan_amount', 0)
            )

            loan_term = float(
                request.POST.get('loan_term', 360)
            )

            credit_history = float(
                request.POST.get('credit_history', 0)
            )
            
            # NEW NUMERIC FIELDS
            years_employed = float(request.POST.get('years_employed', 0))
            existing_debt = float(request.POST.get('existing_debt', 0))
            annual_expenses = float(request.POST.get('annual_expenses', 0))
            down_payment = float(request.POST.get('down_payment', 0))
            collateral_value = float(request.POST.get('collateral_value', 0))

            gender = request.POST.get('gender')
            married = request.POST.get('married')
            dependents = request.POST.get('dependents')
            education = request.POST.get('education')
            self_employed = request.POST.get('self_employed')
            property_area = request.POST.get('property_area')
            loan_type = request.POST.get('loan_type')
            
            # NEW FIELDS
            employment_status = request.POST.get('employment_status', 'Employed')
            years_employed = float(request.POST.get('years_employed', 0))
            employment_type = request.POST.get('employment_type', 'Private')
            existing_debt = float(request.POST.get('existing_debt', 0))
            annual_expenses = float(request.POST.get('annual_expenses', 0))
            loan_purpose = request.POST.get('loan_purpose', 'Home')
            down_payment = float(request.POST.get('down_payment', 0))
            collateral_available = request.POST.get('collateral_available', 'No')
            collateral_value = float(request.POST.get('collateral_value', 0))

            # FIX EDUCATION
            if education in ['SSLC', 'PUC', 'Not Graduate']:
                education = 'Not Graduate'

            elif education == 'Graduate':
                education = 'Graduate'

            # LOAD MODEL
            model, encoders = load_model()

            if model is None:

                context['error'] = "Model not loaded"

                return render(
                    request,
                    'predict.html',
                    context
                )

            # DATA
            data = {

                'Gender': gender,
                'Married': married,
                'Dependents': dependents,
                'Education': education,
                'Self_Employed': self_employed,
                'ApplicantIncome': applicant_income,
                'CoapplicantIncome': coapplicant_income,
                'LoanAmount': loan_amount,
                'Loan_Amount_Term': loan_term,
                'Credit_History': credit_history,
                'Property_Area': property_area,
                'Loan_Type': loan_type,

            }

            data['Total_Income'] = (
                applicant_income +
                coapplicant_income
            )

            columns = [

                'Gender',
                'Married',
                'Dependents',
                'Education',
                'Self_Employed',
                'ApplicantIncome',
                'CoapplicantIncome',
                'LoanAmount',
                'Loan_Amount_Term',
                'Credit_History',
                'Property_Area',
                'Loan_Type',
                'Total_Income'

            ]

            input_data = []

            for col in columns:

                val = data[col]

                if col in encoders:
                    val = encoders[col].transform([val])[0]

                input_data.append(float(val))

            input_df = pd.DataFrame(
                [input_data],
                columns=columns
            )

            # PREDICTION
            pred = model.predict(input_df)[0]

            prob = model.predict_proba(input_df)[0]

            result = encoders[
                'Loan_Status'
            ].inverse_transform([pred])[0]

            confidence = round(
                max(prob) * 100,
                2
            )

            # EXPLANATION
            explanation = explain({

                'ApplicantIncome': applicant_income,

                'LoanAmount': loan_amount,

                'Credit_History': credit_history

            })

            # SAVE DATABASE
            Prediction.objects.create(

                user=request.user,

                result=result,

                confidence=confidence,

                gender=gender,

                married=married,

                dependents=dependents,

                education=education,

                self_employed=self_employed,

                applicant_income=applicant_income,

                coapplicant_income=coapplicant_income,
                
                total_income=applicant_income + coapplicant_income,

                loan_amount=loan_amount,

                loan_term=loan_term,

                credit_history=credit_history,

                property_area=property_area,

                loan_type=loan_type,
                
                # NEW FIELDS
                employment_status=employment_status,
                
                years_employed=years_employed,
                
                employment_type=employment_type,
                
                existing_debt=existing_debt,
                
                annual_expenses=annual_expenses,
                
                loan_purpose=loan_purpose,
                
                down_payment=down_payment,
                
                collateral_available=collateral_available,
                
                collateral_value=collateral_value,
                
                explanation=str(explanation)

            )

            return render(request, 'result.html', {
                'result': result,
                'confidence': confidence,
                'explanation': explanation,
                'gender': gender,
                'married': married,
                'dependents': dependents,
                'education': education,
                'employment_status': employment_status,
                'years_employed': years_employed,
                'applicant_income': applicant_income,
                'coapplicant_income': coapplicant_income,
                'loan_amount': loan_amount,
                'loan_term': loan_term,
                'credit_history': credit_history,
                'property_area': property_area,
                'loan_type': loan_type,
                'loan_purpose': loan_purpose,
                'down_payment': down_payment,
                'existing_debt': existing_debt,
                'collateral_available': collateral_available,
                'collateral_value': collateral_value
            })

        except Exception as e:

            context['error'] = str(e)

            return render(
                request,
                'predict.html',
                context
            )

    return render(
        request,
        'predict.html',
        context
    )
    
from django.shortcuts import render

def forgot_password(request):
    return render(request, 'forgot_password.html')

def terms(request):
    return render(request, 'terms.html')

def privacy(request):
    return render(request, 'privacy.html')