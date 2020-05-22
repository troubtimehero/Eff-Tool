from django.conf.urls import url
from my_admin import views

urlpatterns = [
    url(r'^t/$', views.reload_redis),
    url(r'^w/$', views.upload_words),
    url(r'^tips/$', views.tips),
]
