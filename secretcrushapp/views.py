import logging
import requests
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, logout_then_login, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from secretcrushapp.models import HidentoUser, InstagramCrush
from secretcrushapp.forms import SignUpForm, HidentoUserChangeFormForUsers

from hidento_project import settings

#logger = logging.getLogger(__name__)
logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)

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
        return HttpResponseRedirect(reverse('index'))
    return LoginView.as_view(template_name='secretcrushapp/login.html')(request)

@login_required
def logoutView(request):
    return LogoutView.as_view(template_name='secretcrushapp/logout.html')(request)

def signupView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
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
    logging.debug("this log is from account view for {}".format(request.user))
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

@login_required
def linkInstagramView(request):
    return HttpResponseRedirect(constructInstagramApiUrl())

def constructInstagramApiUrl():
    queryParams = urlencode({
        'app_id': settings.INSTAGRAM_APP_ID,
        'redirect_uri': settings.INSTAGRAM_AUTHORIZE_REDIRECT_URL,
        'scope': 'user_profile,user_media',
        'response_type': 'code'
    })
    return settings.INSTAGRAM_AUTHORIZE_URL + '?' + queryParams

@login_required
def authInstagramView(request):
    full_code = request.GET.get('code')
    logging.debug("\n\n\n\n\nfull code: {}".format(full_code))
    code = full_code[0:-2] #remove the trailing '#_' in the code
    logging.debug("\n\n\n\n\ntrimmed code: {}".format(code))
    data = {
        'app_id': settings.INSTAGRAM_APP_ID,
        'app_secret': settings.INSTAGRAM_APP_SECRET,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.INSTAGRAM_AUTHORIZE_REDIRECT_URL,
        'code': code
    }
    logging.debug("\n\n\n\n\npost data: {}".format(data))
    token_response = requests.post(url=settings.INSTAGRAM_TOKEN_URL, data=data)
    token_response_data = token_response.json()
    logging.debug("\n\n\n\n\ntoken response from instagram: {}".format(token_response_data))
    #logger.debug('token response from instagram:\n\n\n\n\n', str(token_response_data), '\n\n\n\n')
    user_details_response = getInstagramUserDetails(token_response_data['user_id'], token_response_data['access_token'])
    user_details_response_data = user_details_response.json()
    logging.debug("\n\n\n\n\nuser details response from instagram: {}".format(user_details_response_data))
    #logger.debug('user details response from instagram:\n\n\n', user_details_response_data, '\n\n\n\n')
    user = request.user
    user_instagram = user.instagramDetails.first()
    if user_instagram is None:
        user_instagram = InstagramCrush(hidento_userid=user)
    user_instagram.instagram_userid = user_details_response_data['id']
    user_instagram.instagram_username = user_details_response_data['username']
    user_instagram.save()
    logging.debug("\n\n\n\n\nuser instagramCrush after saving: {}".format(user_instagram))
    return HttpResponseRedirect(reverse('account'))

def getInstagramUserDetails(user_id, access_token):
    url = settings.INSTAGRAM_USERNODE_URL + user_id
    params = {
        'fields': 'id,username',
        'access_token': access_token
    }
    logging.debug("\n\n\n\n\nuser details url: {}".format(url))
    logging.debug("\n\n\n\n\nuser details q params: {}".format(params))
    return requests.get(url=url, params=params)