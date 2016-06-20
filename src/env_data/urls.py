from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(?P<vineyard_id>[0-9])/(?P<variable_id>[0-9])/$', views.index, name='index')
]
