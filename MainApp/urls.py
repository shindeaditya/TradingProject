from django.urls import path
from . import views

urlpatterns = [
    path('upload_csv/', views.upload_csv_view, name='upload_csv'),
]
