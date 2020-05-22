from django.conf.urls import url
from frequency import views

urlpatterns = [
    url(r'$', views.index),
]
