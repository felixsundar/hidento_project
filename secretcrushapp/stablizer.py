import logging
import threading
import time
from random import randint

from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from hidento_project import settings
from secretcrushapp.models import InstagramCrush, Controls

from hidento_project.settings import STABLIZATION_PERIOD, STABLE_PERIOD, CONTROLS_RECORD_ID

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)

def startStablizerThread():
    stablizerThread = threading.Thread(target=runStablizer, daemon=True, name='stablizer_thread')
    stablizerThread.start()

def runStablizer():
    logging.debug('Stablizer thread activated.')
    while True:
        logging.debug('stablizing thread going into sleep at {}'.format(now()))
        time.sleep(10)
        try:
            controls = Controls.objects.get(control_id=CONTROLS_RECORD_ID)
        except Controls.DoesNotExist:
            stablization_days = STABLIZATION_PERIOD
            stable_days = STABLE_PERIOD
        else:
            stablization_days = controls.stablization_days
            stable_days = controls.stable_days
        try:
            stablize(stablization_days, stable_days)
        except Exception as e:
            pass

def stablize(stablization_days, stable_days):
    logging.debug('starting to stablize the matches at {}'.format(now()))
    for user_instagram in InstagramCrush.objects.only('instagram_username').filter(match_instagram_username__isnull=False).iterator(500):
        try:
            stablizeOrDestablize(user_instagram.instagram_username, stablization_days, stable_days)
        except Exception:
            pass

@transaction.atomic
def stablizeOrDestablize(instagram_username, stablization_days, stable_days):
    matched_instagrams = InstagramCrush.objects.select_for_update().filter(
        Q(instagram_username=instagram_username)
        | Q(match_instagram_username=instagram_username))
    matched_instagrams_list = list(matched_instagrams)
    if not matched_instagrams_valid(matched_instagrams_list, instagram_username):
        return
    if match_already_stablized(matched_instagrams_list):
        if stable_period_is_over(matched_instagrams_list, stable_days):
            destablizeMatch(matched_instagrams_list)
            save_matched_instagrams(matched_instagrams_list)
            rematch(matched_instagrams_list)
        return
    if match_has_matured(matched_instagrams_list, stablization_days):
        stablizeMatch(matched_instagrams_list)
        save_matched_instagrams(matched_instagrams_list)

def save_matched_instagrams(matched_instagrams_list):
    matched_instagrams_list[0].save()
    matched_instagrams_list[1].save()

def stable_period_is_over(matched_instagrams_list, stable_days):
    if time_difference_in_days(matched_instagrams_list[0].match_stablized_time, now()) > stable_days:
        return True
    return False

def rematch(matched_instagrams_list):
    match_starter_thread = threading.Thread(target=startMatchingThreadsWithInterval, daemon=True, args=(matched_instagrams_list,))
    match_starter_thread.start()

def startMatchingThreadsWithInterval(matched_instagrams_list):
    from secretcrushapp import matching
    matching_thread1 = threading.Thread(target=matching.startMatching, daemon=True,
                                        args=(matched_instagrams_list[0].hidento_userid,))
    matching_thread1.start()
    time.sleep(4)
    matching_thread2 = threading.Thread(target=matching.startMatching, daemon=True,
                                        args=(matched_instagrams_list[1].hidento_userid,))
    matching_thread2.start()

def matched_instagrams_valid(matched_instagrams_list, instagramUsername):
    match_length = len(matched_instagrams_list)
    if match_length ==2 and matched_instagrams_list[0].instagram_username == matched_instagrams_list[1].match_instagram_username \
        and matched_instagrams_list[1].instagram_username == matched_instagrams_list[0].match_instagram_username:
        return True

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

def match_has_matured(matched_instagrams_list, stablization_days):
    if matched_instagrams_list[0].match_time != matched_instagrams_list[1].match_time:
        logging.debug('System in inconsistent state. Match time of matched users not same for instagram users {} and {}' \
                      .format(matched_instagrams_list[0].instagram_username, matched_instagrams_list[1].instagram_username))
        return False
    if time_difference_in_days(matched_instagrams_list[0].match_time, now()) >= stablization_days:
        return True
    return False

def time_difference_in_days(initial_time, final_time):
    if initial_time is None or final_time is None:
        return -2
    time_difference = final_time - initial_time
    return divmod(time_difference.total_seconds(), 86400)[0]

def stablizeMatch(matched_instagrams_list):
    matched_instagrams_list[0].match_stablized = True
    matched_instagrams_list[1].match_stablized = True
    positionOf1in0 = currentMatchPosition(matched_instagrams_list[0])
    matched_instagrams_list[1].match_nickname = matched_instagrams_list[0].__dict__[getCrushField(positionOf1in0, 'nickname')]
    matched_instagrams_list[1].match_message = matched_instagrams_list[0].__dict__[getCrushField(positionOf1in0, 'message')]
    positionOf0in1 = currentMatchPosition(matched_instagrams_list[1])
    matched_instagrams_list[0].match_nickname = matched_instagrams_list[1].__dict__[getCrushField(positionOf0in1, 'nickname')]
    matched_instagrams_list[0].match_message = matched_instagrams_list[1].__dict__[getCrushField(positionOf0in1, 'message')]
    stablizing_time = now()
    matched_instagrams_list[0].match_stablized_time = stablizing_time
    matched_instagrams_list[1].match_stablized_time = stablizing_time
    personToInform = getPersonToInform(matched_instagrams_list)
    matched_instagrams_list[personToInform].inform_this_user = True

def match_already_stablized(matched_instagrams_list):
    if matched_instagrams_list[0].match_stablized == True and matched_instagrams_list[1].match_stablized == True:
        return True
    if matched_instagrams_list[0].match_stablized == True or matched_instagrams_list[1].match_stablized == True:
        logging.debug('Matching stablized for only one user or Matching made with stablized user. User instagram names'
                      ' - {} and {}'.format(matched_instagrams_list[0].instagram_username, matched_instagrams_list[1].instagram_username))
        destablizeMatch(matched_instagrams_list[0])
        destablizeMatch(matched_instagrams_list[1])
    return False

def destablizeMatch(matched_instagrams_list):
    matched_instagrams_list[0].match_stablized = False
    matched_instagrams_list[0].match_stablized_time = None
    matched_instagrams_list[0].inform_this_user = False
    matched_instagrams_list[0].match_nickname = None
    matched_instagrams_list[0].match_message = None
    matched_instagrams_list[1].match_stablized = False
    matched_instagrams_list[1].match_stablized_time = None
    matched_instagrams_list[1].inform_this_user = False
    matched_instagrams_list[1].match_nickname = None
    matched_instagrams_list[1].match_message = None
    reset_match_time = now()
    matched_instagrams_list[0].match_time = reset_match_time
    matched_instagrams_list[1].match_time = reset_match_time

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