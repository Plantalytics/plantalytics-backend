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
    url(r'^reset', views.reset, name='reset'),
    url(r'^password_reset', views.password_reset, name='password_reset'),
    url(r'^change', views.change, name='change')
]
