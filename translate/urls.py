from django.conf.urls import url
from translate import views

urlpatterns = [
    url(r'$', views.index),
]
