from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect

from secretcrushapp.models import HidentoUser


class HidentoUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = self.loginUsingUsername(username, password)
        if user is None:
            user = self.loginUsingEmail(username, password)
        return user

    def loginUsingUsername(self, username, password):
        try:
            user = HidentoUser.objects.get(username = username)
        except HidentoUser.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                #add db check here to equal the timing login using username and email
                return user

    def loginUsingEmail(self, username, password):
        try:
            user = HidentoUser.objects.get(email = username)
        except HidentoUser.DoesNotExist:
            #run password hash here to equal timing of existent and non-existent users
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

def index(request):
    if request.user.is_authenticated:
        return render(request, 'secretcrushapp/user_home.html', {'user':request.user})
    return LoginView.as_view(template_name='secretcrushapp/website_home.html')(request)

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return LoginView.as_view(template_name='secretcrushapp/login.html')(request)