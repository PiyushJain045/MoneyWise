from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('AddStatements', views.addStatements.as_view(), name='add-statements'),
    path('Dashboard', views.Dashboard.as_view(), name='dashboard'),
    path('Add Transaction', views.AddTransaction.as_view(), name='add-transaction'),
]
