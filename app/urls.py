from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('AddStatements', views.addStatements.as_view(), name='add-statements'),
    path('Dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('Add Transaction', views.AddTransaction.as_view(), name='add-transaction'),
    path('Finacial Report', views.FinancialReport.as_view(), name='financial-report'),
    path('AI Receipt', views.AiReceipt.as_view(), name='ai-receipt'),
    path('Profile', views.ProfileSection.as_view(), name='profile'),
    path("onboarding/", views.OnBoarding, name="onboarding"),
]
