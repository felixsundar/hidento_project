import logging
import threading

import requests
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, logout_then_login, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.timezone import now
from secretcrushapp.models import HidentoUser, InstagramCrush, HowItWorks, FAQ, ContactHidento, Controls, InstagramDetails
from secretcrushapp.forms import SignUpForm, HidentoUserChangeFormForUsers, AddCrushForm, EditCrushForm, ContactForm

from hidento_project import settings

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)
INSTAGRAM_NOT_LINKED = 'Instagram account not linked. Link Instagram account to add secret crush.'
CRUSH_LIST_FULL = 'You already have 5 secret crushes. Remove one of them to add a new crush.'
CRUSH_LIST_EMPTY = 'There is no crush to edit. Your crush list is empty.'
CRUSH_ALREADY_PRESENT = 'This Instagram username is already present in your crush list.'
CRUSH_NOT_PRESENT = 'This instagram username is not present in your crush list. Select one from your crush list.'
PRIORITY_EXCEEDS_LIMIT = 'Priority Position should be within the total number of crushes in the crushlist.'
CRUSH_AND_YOURNAME_SAME = 'You can\'t enter your own Instagram username as a crush.'


class HidentoUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = self.loginUsingUsername(username, password)
        if user is None:
            user = self.loginUsingEmail(username, password)
        return user

    def loginUsingUsername(self, username, password):
        try:
            user = HidentoUser.objects.get(username=username)
        except HidentoUser.DoesNotExist:
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                # add db check here to equal the timing login using username and email
                return user

    def loginUsingEmail(self, username, password):
        try:
            user = HidentoUser.objects.get(email=username)
        except HidentoUser.DoesNotExist:
            # run password hash here to equal timing of existent and non-existent users
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user


def index(request):
    if request.user.is_authenticated:
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/user_home_m.html')
        return render(request, 'secretcrushapp/user_home.html')
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/website_home_m.html')
    return render(request, 'secretcrushapp/website_home.html')


@login_required
def crushListView(request):
    user_instagram = request.user.instagramDetails.first()
    context = {
        'user_firstname': request.user.firstname,
        'instagram_crushes': getInstagramCrushes(user_instagram)
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/crush_list_m.html', context=context)
    return render(request, 'secretcrushapp/crush_list.html', context=context)


def getInstagramCrushes(user_instagram):
    if user_instagram is None:
        return None
    instagramCrushes = []
    for position in range(1, 6):
        crushUsername = user_instagram.__dict__[getCrushField(position, 'username')]
        if crushUsername is not None:
            instagramCrushes.append({
                'crushUsername': crushUsername,
                'crushNickname': user_instagram.__dict__[getCrushField(position, 'nickname')],
                'is_active': user_instagram.__dict__[getCrushField(position, 'active')]
            })
    return instagramCrushes


@login_required
@transaction.atomic
def matchView(request):
    user_instagram = request.user.instagramDetails.first()
    if user_instagram is None or not (user_instagram.match_stablized and user_instagram.inform_this_user):
        matchDetails = None
    else:
        try:
            controls = Controls.objects.get(control_id=settings.CONTROLS_RECORD_ID)
        except Controls.DoesNotExist:
            stable_days = settings.STABLE_PERIOD
        else:
            stable_days = controls.stable_days
        matchDetails = {
            'match_instagram_username': user_instagram.match_instagram_username,
            'user_nickname_for_match': getMatchNickname(user_instagram),
            'match_nickname_for_user': user_instagram.match_nickname,
            'match_message_for_user': user_instagram.match_message,
            'instagramProfileLink': 'https://www.instagram.com/' + user_instagram.match_instagram_username,
            'remaining_stable_days': int(
                stable_days - time_difference_in_days(user_instagram.match_stablized_time, now()))
        }
    context = {
        'matchDetails': matchDetails,
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/match_m.html', context=context)
    return render(request, 'secretcrushapp/match.html', context=context)


def time_difference_in_days(initial_time, final_time):
    if initial_time is None or final_time is None:
        return -2
    time_difference = final_time - initial_time
    return divmod(time_difference.total_seconds(), 86400)[0]


def getMatchNickname(user_instagram):
    matchPosition = getCrushPosition(user_instagram, user_instagram.match_instagram_username)
    return user_instagram.__dict__[getCrushField(matchPosition, 'nickname')]


def loginView(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    if request.user_agent.is_mobile:
        return LoginView.as_view(template_name='secretcrushapp/login_m.html')(request)
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
            messages.success(request, 'Account created successfully.')
            return HttpResponseRedirect(reverse('login'))
    else:
        form = SignUpForm()
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/signup_m.html', {'form': form})
    return render(request, 'secretcrushapp/signup.html', {'form': form})


@login_required
def accountView(request):
    context = {
        'user': request.user,
        'instagram_username': getInstagramUsername(request.user)
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/account_m.html', context=context)
    return render(request, 'secretcrushapp/account.html', context=context)


def getInstagramUsername(user):
    user_instagram = user.instagramDetails.first()
    if user_instagram is not None:
        return user_instagram.instagram_username
    return None


@login_required
@transaction.atomic
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
        'instagram_username': getInstagramUsername(user)
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/account_edit_m.html', context)
    return render(request, 'secretcrushapp/account_edit.html', context)


@login_required
@transaction.atomic
def accountDeleteView(request):
    if request.method == 'POST':
        request.user.delete()
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/account_deleted_m.html')
        return render(request, 'secretcrushapp/account_deleted.html')
    else:
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/account_delete_m.html')
        return render(request, 'secretcrushapp/account_delete.html')


@login_required
def changePasswordView(request):
    if request.user_agent.is_mobile:
        return PasswordChangeView.as_view(template_name='secretcrushapp/changePassword_m.html',
                                          success_url=reverse('changePasswordDone'))(request)
    return PasswordChangeView.as_view(template_name='secretcrushapp/changePassword.html',
                                      success_url=reverse('changePasswordDone'))(request)


@login_required
def changePasswordDoneView(request):
    if request.META.get('HTTP_REFERER') is None:
        return HttpResponseRedirect(reverse('changePassword'))
    logout(request)
    messages.success(request, 'Password changed successfully. Login with your new Password.')
    return HttpResponseRedirect(reverse('login'))


def resetPasswordView(request):
    if request.user_agent.is_mobile:
        return PasswordResetView.as_view(template_name='secretcrushapp/resetPassword_m.html',
                                         email_template_name='secretcrushapp/resetPasswordEmail.html',
                                         subject_template_name='secretcrushapp/resetPasswordSubject.txt',
                                         success_url=reverse('resetPasswordDone')
                                         )(request)
    return PasswordResetView.as_view(template_name='secretcrushapp/resetPassword.html',
                                     email_template_name='secretcrushapp/resetPasswordEmail.html',
                                     subject_template_name='secretcrushapp/resetPasswordSubject.txt',
                                     success_url=reverse('resetPasswordDone')
                                     )(request)


def resetPasswordDoneView(request):
    if request.META.get('HTTP_REFERER') is None:
        return HttpResponseRedirect(reverse('resetPassword'))
    if request.user_agent.is_mobile:
        return PasswordResetDoneView.as_view(template_name='secretcrushapp/resetPasswordDone_m.html')(request)
    return PasswordResetDoneView.as_view(template_name='secretcrushapp/resetPasswordDone.html')(request)


def confirmResetPasswordView(request, uidb64, token):
    if request.user_agent.is_mobile:
        return PasswordResetConfirmView.as_view(template_name='secretcrushapp/confirmResetPassword_m.html',
                                                success_url=reverse('completeResetPassword'),
                                                )(request, uidb64=uidb64, token=token)
    return PasswordResetConfirmView.as_view(template_name='secretcrushapp/confirmResetPassword.html',
                                            success_url=reverse('completeResetPassword'),
                                            )(request, uidb64=uidb64, token=token)


def completeResetPasswordView(request):
    if request.META.get('HTTP_REFERER') is None:
        return HttpResponseRedirect(reverse('resetPassword'))
    messages.success(request, 'Password reset complete. Login with your new Password.')
    return HttpResponseRedirect(reverse('login'))


@login_required
def linkInstagramView(request):
    user_instagram = request.user.instagramDetails.first()
    if user_instagram is not None:
        context = {
            'code': 1,
        }
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/link_instagram_m.html', context)
        return render(request, 'secretcrushapp/link_instagram.html', context)
    if request.GET.get('mode') == 'forceLink':
        request.session['mode'] = 'forceLink'
    return HttpResponseRedirect(constructInstagramApiUrl())


def constructInstagramApiUrl():
    queryParams = urlencode({
        'app_id': settings.INSTAGRAM_APP_ID,
        'redirect_uri': settings.INSTAGRAM_AUTHORIZE_REDIRECT_URL,
        'scope': 'user_profile',
        'response_type': 'code'
    })
    return settings.INSTAGRAM_AUTHORIZE_URL + '?' + queryParams


@login_required
def authInstagramView(request):
    user = request.user
    user_instagram = user.instagramDetails.first()
    if user_instagram is not None:
        context = {
            'code': 1,
        }
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/link_instagram_m.html', context)
        return render(request, 'secretcrushapp/link_instagram.html', context)
    try:
        code = request.GET.get('code')
        data = {
            'app_id': settings.INSTAGRAM_APP_ID,
            'app_secret': settings.INSTAGRAM_APP_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': settings.INSTAGRAM_AUTHORIZE_REDIRECT_URL,
            'code': code
        }
        token_response = requests.post(url=settings.INSTAGRAM_TOKEN_URL, data=data)
        token_response_data = token_response.json()
        user_details_response = getInstagramUserDetails(token_response_data['user_id'],
                                                        token_response_data['access_token'])
        user_details_response_data = user_details_response.json()
        if checkInstagramUsername(request, user_details_response_data['username']):
            context = {
                'code': 2,
                'instagram_username': user_details_response_data['username'],
            }
            if request.user_agent.is_mobile:
                return render(request, 'secretcrushapp/link_instagram_m.html', context)
            return render(request, 'secretcrushapp/link_instagram.html', context)
        user_instagram = InstagramCrush(hidento_userid=user)
        user_instagram.instagram_username = user_details_response_data['username']
        user_instagram.save()
        user_instagram_details = InstagramDetails(hidento_userid=user)
        user_instagram_details.instagram_userid = user_details_response_data['id']
        user_instagram_details.instagram_username = user_details_response_data['username']
        getInstagramLongLivedToken(token_response_data['access_token'], user_instagram_details)
        user_instagram_details.save()
        messages.success(request, 'Instagram account linked successfully. You can add secret crushes now.')
        return HttpResponseRedirect(reverse('crushList'))
    except:
        messages.warning(request, 'Linking Instagram account failed.')
        return HttpResponseRedirect(reverse('crushList'))


def getInstagramLongLivedToken(access_token, user_instagram_details):
    try:
        params = {
            'client_secret': settings.INSTAGRAM_APP_SECRET,
            'grant_type': 'ig_exchange_token',
            'access_token': access_token
        }
        long_lived_token_response = requests.get(url=settings.INSTAGRAM_LONG_LIVED_TOKEN_URL, params=params)
        long_lived_token_response_data = long_lived_token_response.json()
        user_instagram_details.ll_access_token = long_lived_token_response_data['access_token']
        user_instagram_details.expires_in = long_lived_token_response_data['expires_in']
        user_instagram_details.token_time = now()
    except Exception as e:
        logging.debug("ll token exception. username - {}\n exception - {}".format(user_instagram_details.instagram_username, str(e)))


def checkInstagramUsername(request, instagramUsername):
    user_instagram = checkUsernameInInstagramCrush(instagramUsername)
    user_instagramDetails = checkUsernameInInstagramDetails(instagramUsername)
    if user_instagram is None and user_instagramDetails is None:
        return False
    if user_instagram is not None and user_instagramDetails is not None:
        if request.session.pop('mode', None) == 'forceLink':
            user_instagram.delete()
            user_instagramDetails.delete()
            return False
        return True
    if user_instagram is not None:
        user_instagram.delete()
    if user_instagramDetails is not None:
        user_instagramDetails.delete()
    return False

def checkUsernameInInstagramCrush(instagramUsername):
    try:
        return InstagramCrush.objects.get(instagram_username=instagramUsername)
    except InstagramCrush.DoesNotExist:
        return None

def checkUsernameInInstagramDetails(instagramUsername):
    try:
        return InstagramDetails.objects.get(instagram_username=instagramUsername)
    except InstagramDetails.DoesNotExist:
        return None

def getInstagramUserDetails(user_id, access_token):
    url = settings.INSTAGRAM_USERNODE_URL + str(user_id)
    params = {
        'fields': 'id,username',
        'access_token': access_token
    }
    return requests.get(url=url, params=params)


@login_required
def removeInstagramConfirmview(request):
    user_instagram = request.user.instagramDetails.first()
    context = {
        'user_instagram': user_instagram,
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/removeInstagramConfirm_m.html', context=context)
    return render(request, 'secretcrushapp/removeInstagramConfirm.html', context=context)


@login_required
@transaction.atomic
def removeInstagramView(request):
    if request.method != 'POST':
        raise PermissionDenied
    user_instagram = request.user.instagramDetails.first()
    user_instagramDetails = request.user.user_instagramDetails.first()
    if user_instagram is None and user_instagramDetails is None:
        return HttpResponseRedirect(reverse('account'))
    if user_instagramDetails is not None:
        user_instagramDetails.delete()
    elif user_instagram is not None:
        user_instagram.delete()
    messages.success(request, 'Your Instagram has been removed successfully and your crush list has been cleared.')
    return HttpResponseRedirect(reverse('crushList'))


@login_required
@transaction.atomic
def addCrushView(request):
    user_instagram = request.user.instagramDetails.select_for_update().first()
    error_or_lowestPriority = validateUserInstagramForAdd(user_instagram)
    if isinstance(error_or_lowestPriority, dict):
        context = {
            'error': error_or_lowestPriority
        }
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/add_crush_m.html', context)
        return render(request, 'secretcrushapp/add_crush.html', context)

    if request.method == 'POST':
        form = AddCrushForm(error_or_lowestPriority, request.POST)
        if form.is_valid() and validateAndAddCrush(form, user_instagram, error_or_lowestPriority):
            messages.success(request, 'New secret crush has been added successfully')
            return HttpResponseRedirect(reverse('crushList'))
    else:
        form = AddCrushForm(error_or_lowestPriority)
    context = {
        'form': form,
        'lowest_priority': error_or_lowestPriority,
        'priorities': [(getPosition(position)) for position in range(1, error_or_lowestPriority + 1)]
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/add_crush_m.html', context)
    return render(request, 'secretcrushapp/add_crush.html', context)


def getPosition(position):
    return (str(position), str(position) + ' - Highest' if position == 1 else str(position))


def validateUserInstagramForAdd(user_instagram):
    if user_instagram is None:
        return {
            'code': 1,
            'message': INSTAGRAM_NOT_LINKED
        }
    lowest_priority = findVacantPosition(user_instagram)
    if lowest_priority == 0:
        return {
            'code': 2,
            'message': CRUSH_LIST_FULL
        }
    return lowest_priority


def validateAndAddCrush(form, user_instagram, vacant_position):
    if not validateCrushForAdd(form, user_instagram, form.cleaned_data['crushUsername'], vacant_position):
        return False
    user_instagram.__dict__[getCrushField(vacant_position, 'username')] = form.cleaned_data['crushUsername']
    user_instagram.__dict__[getCrushField(vacant_position, 'nickname')] = form.cleaned_data['crushNickname']
    user_instagram.__dict__[getCrushField(vacant_position, 'message')] = form.cleaned_data['crushMessage']
    user_instagram.__dict__[getCrushField(vacant_position, 'whomToInform')] = form.cleaned_data['whomToInform']
    user_instagram.__dict__[getCrushField(vacant_position, 'active')] = True
    user_instagram.__dict__[getCrushField(vacant_position, 'time')] = now()
    moveAccordingToPriority(user_instagram, vacant_position, int(form.cleaned_data['priorityPosition']))
    user_instagram.save()
    return True


def validateCrushForAdd(form, user_instagram, crushUsername, lowest_priority):
    if user_instagram is None:  # this check is already done in validateUserInstagram. it is redundant but for safety
        form.add_error('__all__', INSTAGRAM_NOT_LINKED)
        return False
    if findVacantPosition(
            user_instagram) == 0:  # this check is already done in validateUserInstagram. it is redundant but for safety
        form.add_error('__all__', CRUSH_LIST_FULL)
        return False
    if crushAlreadyPresent(user_instagram, crushUsername):
        form.add_error('crushUsername', CRUSH_ALREADY_PRESENT)
    if user_instagram.instagram_username == crushUsername:
        form.add_error('crushUsername', CRUSH_AND_YOURNAME_SAME)
    if int(form.cleaned_data['priorityPosition']) > lowest_priority:
        form.add_error('priorityPosition', PRIORITY_EXCEEDS_LIMIT)
    return False if form.errors else True


def findVacantPosition(user_instagram):
    for position in range(1, 6):
        if user_instagram.__dict__['crush' + str(position) + '_username'] is None:
            return position
    return 0  # return 0 if all positions are filled


def crushAlreadyPresent(user_instagram, crushUsername):
    for position in range(1, 6):
        if user_instagram.__dict__['crush' + str(position) + '_username'] == crushUsername:
            return True
    return False


def moveAccordingToPriority(user_instagram, initial_position, final_position):
    if initial_position == final_position:
        return
    if initial_position < final_position:
        for position in range(initial_position, final_position):
            swapCrushPositions(user_instagram, position, position + 1)
    else:
        for position in reversed(range(final_position + 1, initial_position + 1)):
            swapCrushPositions(user_instagram, position, position - 1)


def swapCrushPositions(user_instagram, position1, position2):
    temp_username = user_instagram.__dict__[getCrushField(position1, 'username')]
    temp_nickname = user_instagram.__dict__[getCrushField(position1, 'nickname')]
    temp_message = user_instagram.__dict__[getCrushField(position1, 'message')]
    temp_whomToInform = user_instagram.__dict__[getCrushField(position1, 'whomToInform')]
    temp_active = user_instagram.__dict__[getCrushField(position1, 'active')]
    temp_time = user_instagram.__dict__[getCrushField(position1, 'time')]

    user_instagram.__dict__[getCrushField(position1, 'username')] = user_instagram.__dict__[
        getCrushField(position2, 'username')]
    user_instagram.__dict__[getCrushField(position1, 'nickname')] = user_instagram.__dict__[
        getCrushField(position2, 'nickname')]
    user_instagram.__dict__[getCrushField(position1, 'message')] = user_instagram.__dict__[
        getCrushField(position2, 'message')]
    user_instagram.__dict__[getCrushField(position1, 'whomToInform')] = user_instagram.__dict__[
        getCrushField(position2, 'whomToInform')]
    user_instagram.__dict__[getCrushField(position1, 'active')] = user_instagram.__dict__[
        getCrushField(position2, 'active')]
    user_instagram.__dict__[getCrushField(position1, 'time')] = user_instagram.__dict__[
        getCrushField(position2, 'time')]

    user_instagram.__dict__[getCrushField(position2, 'username')] = temp_username
    user_instagram.__dict__[getCrushField(position2, 'nickname')] = temp_nickname
    user_instagram.__dict__[getCrushField(position2, 'message')] = temp_message
    user_instagram.__dict__[getCrushField(position2, 'whomToInform')] = temp_whomToInform
    user_instagram.__dict__[getCrushField(position2, 'active')] = temp_active
    user_instagram.__dict__[getCrushField(position2, 'time')] = temp_time


def getCrushField(position, fieldname):
    return 'crush' + str(position) + '_' + fieldname


@login_required
@transaction.atomic
def editCrushView(request, crushUsername):
    user_instagram = request.user.instagramDetails.select_for_update().first()
    error_or_lowestPriority = validateUserInstagramForEdit(user_instagram, crushUsername)
    if isinstance(error_or_lowestPriority, dict):
        context = {
            'error': error_or_lowestPriority,
            'crushUsername': crushUsername,
        }
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/edit_crush_m.html', context)
        return render(request, 'secretcrushapp/edit_crush.html', context)
    data = getCrushData(user_instagram, crushUsername)
    form = EditCrushForm(error_or_lowestPriority, data)
    if request.method == 'POST':
        form = EditCrushForm(error_or_lowestPriority, request.POST)
        if form.is_valid() and validateAndEditCrush(user_instagram, crushUsername, form, error_or_lowestPriority):
            return HttpResponseRedirect(reverse('crushList'))
    elif request.method == 'DELETE':
        deleteCrush(user_instagram, crushUsername)
        return HttpResponseRedirect(reverse('index'))
    context = {
        'form': form,
        'crushUsername': crushUsername,
        'priorities': [(getPosition(position)) for position in range(1, error_or_lowestPriority + 1)],
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/edit_crush_m.html', context)
    return render(request, 'secretcrushapp/edit_crush.html', context)


def validateUserInstagramForEdit(user_instagram, crushUsername):
    if user_instagram is None:
        return {
            'code': 1,
            'message': INSTAGRAM_NOT_LINKED
        }
    vacant_position = findVacantPosition(user_instagram)
    if vacant_position == 1:
        return {
            'code': 2,
            'message': CRUSH_LIST_EMPTY
        }
    if not crushAlreadyPresent(user_instagram, crushUsername):
        return {
            'code': 3,
            'message': CRUSH_NOT_PRESENT
        }
    return 5 if vacant_position == 0 else vacant_position - 1


def validateAndEditCrush(user_instagram, crushUsername, form, lowest_priority):
    if not validateCrushForEdit(user_instagram, crushUsername, form, lowest_priority):
        return False
    crushPosition = getCrushPosition(user_instagram, crushUsername)

    user_instagram.__dict__[getCrushField(crushPosition, 'nickname')] = form.cleaned_data['crushNickname']
    user_instagram.__dict__[getCrushField(crushPosition, 'message')] = form.cleaned_data['crushMessage']
    user_instagram.__dict__[getCrushField(crushPosition, 'active')] = form.cleaned_data['active']
    user_instagram.__dict__[getCrushField(crushPosition, 'whomToInform')] = form.cleaned_data['whomToInform']
    moveAccordingToPriority(user_instagram, crushPosition, int(form.cleaned_data['priorityPosition']))
    user_instagram.save()
    return True


def validateCrushForEdit(user_instagram, crushUsername, form, lowest_priority):
    if not crushAlreadyPresent(user_instagram,
                               crushUsername):  # this check already done in validateUserInstagramForEdit. it is redundant but for safety
        form.add_error('__all__', CRUSH_NOT_PRESENT)
        return False
    if int(form.cleaned_data['priorityPosition']) > lowest_priority:
        form.add_error('priorityPosition', PRIORITY_EXCEEDS_LIMIT)
        return False
    return True


def getCrushData(user_instagram, crushUsername):
    position = getCrushPosition(user_instagram, crushUsername)
    return {
        'crushNickname': user_instagram.__dict__[getCrushField(position, 'nickname')],
        'crushMessage': user_instagram.__dict__[getCrushField(position, 'message')],
        'whomToInform': user_instagram.__dict__[getCrushField(position, 'whomToInform')],
        'active': user_instagram.__dict__[getCrushField(position, 'active')],
        'priorityPosition': str(position),
    }


def getCrushPosition(user_instagram, crushUsername):
    for position in range(1, 6):
        if user_instagram.__dict__[getCrushField(position, 'username')] == crushUsername:
            return position
    return 0


def deleteCrush(user_instagram, crushUsername):
    position = getCrushPosition(user_instagram, crushUsername)
    user_instagram.__dict__[getCrushField(position, 'username')] = None
    user_instagram.__dict__[getCrushField(position, 'nickname')] = None
    user_instagram.__dict__[getCrushField(position, 'message')] = None
    user_instagram.__dict__[getCrushField(position, 'active')] = False
    user_instagram.__dict__[getCrushField(position, 'time')] = None
    user_instagram.__dict__[getCrushField(position, 'whomToInform')] = 1
    moveAccordingToPriority(user_instagram, position, 5)
    user_instagram.save()


@login_required
@transaction.atomic
def deleteCrushView(request, crushUsername):
    if request.method != 'POST':
        raise PermissionDenied
    user_instagram = request.user.instagramDetails.select_for_update().first()
    error_or_lowestPriority = validateUserInstagramForEdit(user_instagram, crushUsername)
    if isinstance(error_or_lowestPriority, dict):
        context = {
            'error': error_or_lowestPriority,
            'crushUsername': crushUsername,
        }
        if request.user_agent.is_mobile:
            return render(request, 'secretcrushapp/edit_crush_m.html', context)
        return render(request, 'secretcrushapp/edit_crush.html', context)
    deleteCrush(user_instagram, crushUsername)
    messages.success(request, 'Secret crush deleted successfully')
    return HttpResponseRedirect(reverse('crushList'))


def privacyView(request):
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/privacy_m.html')
    return render(request, 'secretcrushapp/privacy.html')


def termsView(request):
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/terms_m.html')
    return render(request, 'secretcrushapp/terms.html')


def howitworksView(request):
    howitworkspoints = HowItWorks.objects.filter(is_enabled=True).order_by('-priority_value')
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/howitworks_m.html', context={'howitworkspoints': howitworkspoints})
    return render(request, 'secretcrushapp/howitworks.html', context={'howitworkspoints': howitworkspoints})


def faqView(request):
    faqs = FAQ.objects.filter(is_enabled=True).order_by('-priority_value')
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/faq_m.html', context={'faqs': faqs})
    return render(request, 'secretcrushapp/faq.html', context={'faqs': faqs})


def contactusView(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Query submitted successfully')
            return HttpResponseRedirect(reverse('contactUs'))
    else:
        form = ContactForm()
    context = {
        'form': form,
    }
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/contact_form_m.html', context)
    return render(request, 'secretcrushapp/contact_form.html', context)


def aboutView(request):
    if request.user_agent.is_mobile:
        return render(request, 'secretcrushapp/about_m.html')
    return render(request, 'secretcrushapp/about.html')


def handler404(request, exception):
    if request.user_agent.is_mobile:
        return render(request, '404_m.html', status=404)
    return render(request, '404.html', status=404)


def handler403(request, exception):
    if request.user_agent.is_mobile:
        return render(request, '403_m.html', status=403)
    return render(request, '403.html', status=403)


def handler500(request):
    if request.user_agent.is_mobile:
        return render(request, '500_m.html', status=500)
    return render(request, '500.html', status=500)


def handler400(request, exception):
    if request.user_agent.is_mobile:
        return render(request, '400_m.html', status=400)
    return render(request, '400.html', status=400)


def csrf_failure(request, reason=""):
    if request.user_agent.is_mobile:
        return render(request, '403_csrf_m.html', status=403)
    return render(request, '403_csrf.html', status=403)
