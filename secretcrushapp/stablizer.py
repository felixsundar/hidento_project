import logging
import threading
import time

from django.db import transaction
from django.db.models import Q
from django.utils.timezone import now

from hidento_project import settings
from secretcrushapp.models import InstagramCrush

logging.basicConfig(filename=settings.LOG_FILE_PATH, level=logging.DEBUG)

def startStablizerThread():
    stablizerThread = threading.Thread(target=runStablizer, daemon=True)
    stablizerThread.start()

def runStablizer():
    while True:
        logging.debug('stablizing thread going into sleep at {}'.format(now()))
        time.sleep(10)
        stablize()

def stablize():
    logging.debug('starting to stablize the matches at {}'.format(now()))
    for user_instagram in InstagramCrush.objects.only('instagram_username').filter(match_instagram_username__isnull=False).iterator(500):
        with transaction.atomic():
            matched_instagrams = InstagramCrush.objects.select_for_update().filter(Q(intagram_username=user_instagram.instagram_username)
                                                                              | Q(match_instagram_username=user_instagram.instagram_username))
            matched_instagrams_list = list(matched_instagrams)
            if not matched_instagrams_valid(matched_instagrams_list) or match_already_stablized(matched_instagrams_list):
                continue
            if match_has_matured(matched_instagrams_list):
                stablizeMatch(matched_instagrams_list)
                matched_instagrams_list[0].save()
                matched_instagrams_list[1].save()

def matched_instagrams_valid(matched_instagrams_list):
    if len(matched_instagrams_list) != 2:
        return False

def match_has_matured(matched_instagrams_list):
    pass


def stablizeMatch(matched_instagrams_list):
    pass


def match_already_stablized(matched_instagrams_list):
    pass
