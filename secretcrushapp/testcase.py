import time

def createTestcases():
    from secretcrushapp.models import HidentoUser
    time.sleep(2)
    user = HidentoUser.objects.create_user('u2','u2@gmail.com','u2','u2', 2, 'hidentoin')
    from secretcrushapp.models import InstagramCrush
    instagram = InstagramCrush(hidento_userid = user)
    instagram.instagram_username = 'b'
    instagram.instagram_userid = '5176176165'
    instagram.crush1_username = 'a'
    instagram.crush1_whomToInform = 2
    instagram.crush2_active = True
    instagram.crush2_username = 'c'
    instagram.crush1_active = True
    instagram.crush1_nickname = 'btoan'
    instagram.crush1_message = 'btoam'
    instagram.crush2_nickname = 'btocn'
    instagram.crush2_message = 'btocm'
    instagram.save()
    time.sleep(2)

    user = HidentoUser.objects.create_user('u3', 'u3@gmail.com', 'u3', 'u3', 2, 'hidentoin')
    time.sleep(2)
    instagram = InstagramCrush(hidento_userid=user)
    instagram.instagram_username = 'c'
    instagram.instagram_userid = '517617616'
    instagram.crush1_username = 'b'
    instagram.crush2_active = True
    instagram.crush2_username = 'd'
    instagram.crush1_active = True
    instagram.crush1_nickname = 'ctobn'
    instagram.crush1_message = 'ctobm'
    instagram.crush2_nickname = 'ctodn'
    instagram.crush2_message = 'ctodm'
    instagram.save()
    time.sleep(2)

    user = HidentoUser.objects.create_user('u4', 'u4@gmail.com', 'u4', 'u4', 2, 'hidentoin')
    time.sleep(2)
    instagram = InstagramCrush(hidento_userid=user)
    instagram.instagram_username = 'd'
    instagram.instagram_userid = '51761761658'
    instagram.crush1_username = 'c'
    instagram.crush2_active = True
    instagram.crush2_username = 'e'
    instagram.crush1_active = True
    instagram.crush1_nickname = 'dtocn'
    instagram.crush1_message = 'dtocm'
    instagram.crush2_nickname = 'dtoen'
    instagram.crush2_message = 'dtoem'
    instagram.save()
    time.sleep(2)

    user = HidentoUser.objects.create_user('u5', 'u5@gmail.com', 'u5', 'u5', 2, 'hidentoin')
    time.sleep(2)
    instagram = InstagramCrush(hidento_userid=user)
    instagram.instagram_username = 'e'
    instagram.instagram_userid = '51761761657'
    instagram.crush1_username = 'd'
    instagram.crush2_active = True
    instagram.crush2_username = 'a'
    instagram.crush1_active = True
    instagram.crush1_nickname = 'etodn'
    instagram.crush1_message = 'etodm'
    instagram.crush2_nickname = 'etoan'
    instagram.crush2_message = 'etoam'
    instagram.save()
    time.sleep(2)