import logging
from django.db import transaction

from hidento_project import settings
from secretcrushapp.models import InstagramCrush

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)
def startMatching(user):
    with transaction.atomic():
        user_instagram = user.instagramDetails.select_for_update().first()
        if currentMatchRemoved(user_instagram):
            firstLoser = breakCurrentMatch(user_instagram)
        newMatchAvailable = tryToMakeNewMatch(user_instagram)
        if newMatchAvailable is not None and user_instagram.match_instagram_username is not None:
            firstLoser = breakCurrentMatch(user_instagram)

def currentMatchRemoved(user_instagram):
    if user_instagram.match_instagram_username is not None and currentMatchPriorityPosition(user_instagram) == 0:
        return True
    return False

def breakCurrentMatch(user_instagram):
    if user_instagram.match_instagram_username is None:
        return None
    matchToBreak = InstagramCrush.objects.select_for_update().get(instagram_username=user_instagram.match_instagram_username)
    if matchToBreak is not None:
        matchToBreak.match_instagram_username = None
        matchToBreak.match_time = None
        matchToBreak.match_nickname = None
        matchToBreak.match_message = None
    user_instagram.match_instagram_username = None
    user_instagram.match_time = None
    user_instagram.match_nickname = None
    user_instagram.match_message = None
    return matchToBreak

def tryToMakeNewMatch(user_instagram):
    if user_instagram is None or user_instagram.match_stablized:
        return None
    for position in range(1,6):
        crushUsername = user_instagram.__dict__[getCrushField(position, 'username')]
        crushIsActive = user_instagram.__dict__[getCrushField(position, 'active')]
        if crushUsername is not None and crushIsActive:
            crushInstagram = InstagramCrush.objects.select_for_update().get(instagram_username=crushUsername)
            if crushIsAvailableForMatch(crushInstagram, user_instagram.instagram_username):
                if user_instagram.match_instagram_username is None or position < currentMatchPriorityPosition(crushInstagram):
                    return crushInstagram
                return None
    return None

def crushIsAvailableForMatch(crushInstagram, user_instagram_username):
    if crushInstagram is None or crushInstagram.match_stablized:
        return False
    for position in range(1,6):
        crushscrushUsername = crushInstagram.__dict__[getCrushField(position, 'username')]
        crushscrushIsActive = crushInstagram.__dict__[getCrushField(position, 'active')]
        if crushscrushUsername is not None and crushscrushIsActive:
            if crushscrushUsername == user_instagram_username:
                if crushInstagram.match_instagram_username is None or position <= currentMatchPriorityPosition(crushInstagram):
                    return True
                return False
    return False

def currentMatchPriorityPosition(user_instagram):
    for position in range(1,6):
        if user_instagram.__dict__[getCrushField(position, 'username')] == user_instagram.match_instagram_username:
            return position
    return 0

def getCrushField(position, fieldname):
    return 'crush' + str(position) + '_' + fieldname