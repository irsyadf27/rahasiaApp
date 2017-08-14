from django.conf.urls import url,include
from django.contrib import admin

from auth.api import ObtainAuthToken

urlpatterns = [

    url(r'^$', ObtainAuthToken.as_view(), name='login'),

]