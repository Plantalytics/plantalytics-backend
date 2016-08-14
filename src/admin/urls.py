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
    url(r'^user$', views.user_info, name='user_info'),
    url(r'^user/disable$', views.user_disable, name='user_disable'),
    url(r'^user/edit$', views.user_edit, name='user_edit'),
    url(r'^user/new$', views.user_new, name='user_new'),
    url(
        r'^user/subscription$',
        views.user_subscription,
        name='user_subscription'
    ),
    url(r'^vineyard$', views.vineyard_info, name='vineyard_info'),
    url(
        r'^vineyard/disable$',
        views.vineyard_disable,
        name='vineyard_disable'
    ),
    url(r'^vineyard/new$', views.vineyard_new, name='vineyard_new'),

]
