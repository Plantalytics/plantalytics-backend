#
# Plantalytics
#     Copyright (c) 2016 Sapphire Becker, Katy Brimm, Scott Ewing,
#       Matt Fraser, Kelly Ledford, Michael Limb, Steven Ngo, Eric Turley
#     This project is licensed under the MIT License.
#     Please see the file LICENSE in this distribution for license terms.
# Contact: plantalytics.capstone@gmail.com
#

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<vineyard_id>[0-9])/(?P<env_variable>\w+)/$', views.index, name='index')
]