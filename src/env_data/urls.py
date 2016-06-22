from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<vineyard_id>[0-9])/(?P<env_variable>\w+)/$', views.index, name='index')
]
