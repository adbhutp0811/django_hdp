from django.urls import path
from . import views

app_name = 'predictor'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/predict/', views.api_predict, name='api_predict'),
    path('insights/', views.model_insights, name='insights'),
]
