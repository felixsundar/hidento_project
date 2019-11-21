from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, logout_then_login, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.urls import reverse
from secretcrushapp.models import HidentoUser, InstagramCrush
from secretcrushapp.forms import SignUpForm, HidentoUserChangeFormForUsers


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
        return getUserHome(request)
    return LoginView.as_view(template_name='secretcrushapp/website_home.html')(request)

def getUserHome(request):
    user_instagram = request.user.instagramDetails.first()
    context = {
        'user':request.user,
        'user_crush':user_instagram
    }
    return render(request, 'secretcrushapp/user_home.html', context=context)

def loginView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return LoginView.as_view(template_name='secretcrushapp/login.html')(request)

def logoutView(request):
    return LogoutView.as_view(template_name='secretcrushapp/logout.html')(request)

def signupView(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/login/')
    else:
        form = SignUpForm()
    return render(request, 'secretcrushapp/signup.html', {'form': form})

@login_required
def accountView(request):
    user_instagram = request.user.instagramDetails.first()
    instagram_username = None
    if user_instagram is not None:
        instagram_username = user_instagram.instagram_username
    context = {
        'user':request.user,
        'instagram_username':instagram_username
    }
    return render(request, 'secretcrushapp/account.html', context=context)

@login_required
def accountEditView(request):
    user = request.user
    if request.method == 'POST':
        form = HidentoUserChangeFormForUsers(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/account')
    else:
        form = HidentoUserChangeFormForUsers(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'secretcrushapp/account_edit.html', context)

@login_required
def changePasswordView(request):
    return PasswordChangeView.as_view(template_name='secretcrushapp/changePassword.html', success_url=reverse('changePasswordDone'))(request)

@login_required
def changePasswordDoneView(request):
    return logout_then_login(request)


def resetPasswordView(request):
    return PasswordResetView.as_view(template_name='secretcrushapp/resetPassword.html',
                                     email_template_name='secretcrushapp/resetPasswordEmail.html',
                                     subject_template_name='secretcrushapp/resetPasswordSubject.txt',
                                     success_url=reverse('resetPasswordDone')
                                     )(request)


def resetPasswordDoneView(request):
    return PasswordResetDoneView.as_view(template_name='secretcrushapp/resetPasswordDone.html')(request)


def confirmResetPasswordView(request, uidb64, token):
    return PasswordResetConfirmView.as_view(template_name='secretcrushapp/confirmResetPassword.html',
                                            success_url=reverse('completeResetPassword'),
                                            )(request, uidb64=uidb64, token=token)


def completeResetPasswordView(request):
    return PasswordResetCompleteView.as_view(template_name='secretcrushapp/completeResetPassword.html')(request)