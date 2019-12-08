import logging
import threading
import time
from random import randint

from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from hidento_project import settings
from secretcrushapp.models import InstagramCrush

from hidento_project.settings import STABLIZATION_PERIOD

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)

def startStablizerThread():
    stablizerThread = threading.Thread(target=runStablizer, daemon=True, name='stablizer thread 78')
    stablizerThread.start()

def runStablizer():
    while True:
        logging.debug('stablizing thread going into sleep at {}. thread name = {}'.format(now(), threading.current_thread().name))
        time.sleep(10)
        stablize()

def stablize():
    logging.debug('starting to stablize the matches at {}'.format(now()))
    for user_instagram in InstagramCrush.objects.only('instagram_username').filter(match_instagram_username__isnull=False).iterator(500):
        with transaction.atomic():
            matched_instagrams = InstagramCrush.objects.select_for_update().filter(Q(instagram_username=user_instagram.instagram_username)
                                                                              | Q(match_instagram_username=user_instagram.instagram_username))
            matched_instagrams_list = list(matched_instagrams)
            if not matched_instagrams_valid(matched_instagrams_list, user_instagram.instagram_username):
                continue
            if match_already_stablized(matched_instagrams_list):
                pass
            if match_has_matured(matched_instagrams_list):
                stablizeMatch(matched_instagrams_list)
                matched_instagrams_list[0].save()
                matched_instagrams_list[1].save()

def matched_instagrams_valid(matched_instagrams_list, instagramUsername):
    match_length = len(matched_instagrams_list)
    if match_length != 2:
        if match_length == 1 and matched_instagrams_list[0].match_instagram_username is not None:
            logging.debug('System in inconsistent state. Match username not none but match not available '
                          'for user_instagram - {}'.format(matched_instagrams_list[0].instagram_username))
        if match_length > 2:
            logging.debug('System in inconsistent state. More than 2 users are there in a match for instagram username '
                          '- {}. Number of instagrams in match - {}'.format(instagramUsername, match_length))
        if match_length == 0:
            logging.debug('Instagram retrieved for stablizing but while getting lock on individual instagram, '
                          'no instagrams were found for instagram username - {}'.format(instagramUsername))
        return False
    if matched_instagrams_list[0].instagram_username == matched_instagrams_list[1].match_instagram_username \
        and matched_instagrams_list[1].instagram_username == matched_instagrams_list[0].match_instagram_username:
        return True
    return False

def match_has_matured(matched_instagrams_list):
    if matched_instagrams_list[0].match_time != matched_instagrams_list[1].match_time:
        logging.debug('System in inconsistent state. Match time of matched users not same for instagram users {} and {}' \
                      .format(matched_instagrams_list[0].instagram_username, matched_instagrams_list[1].instagram_username))
        return False
    time_difference = now() - matched_instagrams_list[0].match_time
    duration_in_days = divmod(time_difference.total_seconds(), 86400)[0]
    if duration_in_days >= STABLIZATION_PERIOD:
        return True
    return False


def stablizeMatch(matched_instagrams_list):
    matched_instagrams_list[0].match_stablized = True
    matched_instagrams_list[1].match_stablized = True
    positionOf1in0 = currentMatchPosition(matched_instagrams_list[0])
    matched_instagrams_list[1].match_nickname = matched_instagrams_list[0].__dict__[getCrushField(positionOf1in0, 'nickname')]
    matched_instagrams_list[1].match_message = matched_instagrams_list[0].__dict__[getCrushField(positionOf1in0, 'message')]
    positionOf0in1 = currentMatchPosition(matched_instagrams_list[0])
    matched_instagrams_list[0].match_nickname = matched_instagrams_list[1].__dict__[getCrushField(positionOf0in1, 'nickname')]
    matched_instagrams_list[0].match_message = matched_instagrams_list[1].__dict__[getCrushField(positionOf0in1, 'message')]
    personToInform = getPersonToInform(matched_instagrams_list)
    matched_instagrams_list[personToInform].inform_this_user = True

def match_already_stablized(matched_instagrams_list):
    if matched_instagrams_list[0].match_stablized == True and matched_instagrams_list[1].match_stablized == True:
        return True
    if matched_instagrams_list[0].match_stablized == True or matched_instagrams_list[1].match_stablized == True:
        logging.debug('Matching stablized for only one user or Matching made with stablized user. User instagram names'
                      ' - {} and {}'.format(matched_instagrams_list[0].instagram_username, matched_instagrams_list[1].instagram_username))
        matched_instagrams_list[0].match_stablized = True
        matched_instagrams_list[1].match_stablized = True
        return True
    return False

def getPersonToInform(matched_instagrams_list):
    positionOf1in0 = currentMatchPosition(matched_instagrams_list[0])
    positionOf0in1 = currentMatchPosition(matched_instagrams_list[1])
    wishOf0 = matched_instagrams_list[0].__dict__[getCrushField(positionOf1in0, 'whomToInform')]
    wishOf1 = matched_instagrams_list[1].__dict__[getCrushField(positionOf0in1, 'whomToInform')]
    if (wishOf0 == 1 and wishOf1 == 1) or (wishOf0 == 2 and wishOf1 == 2):
        return randint(0,1)
    if wishOf0 == 2:
        return 1
    return 0

def currentMatchPosition(user_instagram):
    for position in range(1,6):
        if user_instagram.__dict__[getCrushField(position, 'username')] == user_instagram.match_instagram_username \
                and user_instagram.__dict__[getCrushField(position, 'active')]:
            return position
    return 0

def getCrushField(position, fieldname):
    return 'crush' + str(position) + '_' + fieldname