from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('AddStatements', views.addStatements.as_view(), name='add-statements'),
    path('Dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('Add Transaction', views.AddTransaction.as_view(), name='add-transaction'),
    path('Finacial-Report', views.FinancialReport.as_view(), name='financial-report'),
    path('AI Receipt', views.AiReceipt.as_view(), name='ai-receipt'),
    path('Profile', views.ProfileSection.as_view(), name='profile'),
    path('Recurring Payment', views.RecurringPayments.as_view(), name='recurring'),
    path("onboarding/", views.OnBoarding, name="onboarding"),
    path("Anamoly Detection", views.Security.as_view(), name="security"),
    path("Investments", views.Investments.as_view(), name="investment"),
    path("Learn", views.Learn.as_view(), name="learn"),
]
