from django.urls import path, include

from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(template_name='secretcrushapp/logout.html'), name='logout'),
]