# pages/urls.py
from django.urls import include, path
from django.conf.urls import url

from . import views

urlpatterns = [
    # path('', views.HomePageView.as_view(), name='home'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^success/$',views.success,name='success'),
    path('showinfo/<str:artist>/',views.showinfo,name='showinfo'),
    url(r'^profile/$',views.profile,name='profile'),
    url(r'^logout/$',views.logout_view,name='logout'),
    url(r'^home/$',views.home_view,name='home')
]