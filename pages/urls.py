# pages/urls.py
from django.urls import include, path
from django.conf.urls import url

from . import views

urlpatterns = [
    # path('', views.HomePageView.as_view(), name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^success/$',views.success,name='success'),
    url(r'^showinfo/$',views.showinfo,name='showinfo')


]