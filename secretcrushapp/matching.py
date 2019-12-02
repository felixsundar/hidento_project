import logging
import threading

from django.db import transaction
from django.utils.timezone import now

from hidento_project import settings

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)
def startMatching(user):
    if user is None:
        return
    with transaction.atomic():
        user_instagram = user.instagramDetails.select_for_update().first()
        if user_instagram is None:
            return
        firstLoser = None
        if currentMatchRemoved(user_instagram):
            firstLoser = breakCurrentMatch(user_instagram)
        newMatchAvailable = tryToMakeNewMatch(user_instagram)
        if newMatchAvailable is not None:
            if user_instagram.match_instagram_username is not None:
                firstLoser = breakCurrentMatch(user_instagram)
            secondLoser = makeMatch(user_instagram, newMatchAvailable)
            newMatchAvailable.save()
            if secondLoser is not None:
                secondLoser.save()
                secondLoserThread = threading.Thread(target=startMatching, args=(secondLoser.hidento_userid,))
                secondLoserThread.start()
        user_instagram.save()
        if firstLoser is not None:
            firstLoser.save()
            firstLoserThread = threading.Thread(target=startMatching, args=(firstLoser.hidento_userid,))
            firstLoserThread.start()


def makeMatch(user_instagram, availableCrush):
    loser = breakCurrentMatch(availableCrush)
    match_time = now()
    positionInFirst = getCrushPosition(user_instagram, availableCrush.instagram_username)
    availableCrush.match_instagram_username = user_instagram.instagram_username
    availableCrush.match_nickname = user_instagram.__dict__[getCrushField(positionInFirst, 'nickname')]
    availableCrush.match_message = user_instagram.__dict__[getCrushField(positionInFirst, 'message')]
    availableCrush.match_time = match_time
    positionInSecond = getCrushPosition(availableCrush, user_instagram.instagram_username)
    user_instagram.match_instagram_username = availableCrush.instagram_username
    user_instagram.match_nickname = availableCrush.__dict__[getCrushField(positionInFirst, 'nickname')]
    user_instagram.match_message = availableCrush.__dict__[getCrushField(positionInFirst, 'message')]
    user_instagram.match_time = match_time
    return loser

def getCrushPosition(user_instagram, crushUsername):
    for position in range(1,6):
        if user_instagram.__dict__[getCrushField(position, 'username')] == crushUsername:
            return position
    return 0

def currentMatchRemoved(user_instagram):
    if user_instagram.match_instagram_username is not None and currentMatchPriorityPosition(user_instagram) == 0:
        return True
    return False

def breakCurrentMatch(user_instagram):
    if user_instagram.match_instagram_username is None:
        return None
    from secretcrushapp.models import InstagramCrush
    try:
        matchToBreak = InstagramCrush.objects.select_for_update().get(instagram_username=user_instagram.match_instagram_username)
    except InstagramCrush.DoesNotExist:
        matchToBreak = None
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
            from secretcrushapp.models import InstagramCrush
            try:
                crushInstagram = InstagramCrush.objects.select_for_update().get(instagram_username=crushUsername)
            except InstagramCrush.DoesNotExist:
                continue
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
        if user_instagram.__dict__[getCrushField(position, 'username')] == user_instagram.match_instagram_username \
                and user_instagram.__dict__[getCrushField(position, 'active')]:
            return position
    return 0

def getCrushField(position, fieldname):
    return 'crush' + str(position) + '_' + fieldname