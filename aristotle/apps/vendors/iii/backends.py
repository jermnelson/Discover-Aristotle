__author__ = 'Jeremy Nelson'

import logging
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.models import User
from vendors.iii.bots.iiibots import PatronBot

class IIIUserBackend(RemoteUserBackend):
    """
    This backend is used with III's Patron API to authenticate a user 
    using a last name and an III identification number.
    """
    create_unknown_user = False    

    def authenticate(self,last_name=None,iii_id=None):
        """
        The ``last_name`` and ``iii_id`` are used to authenticate againest
        the III server using the PatronBot Returns None if ``last_name`` and
         ``iii_id`` fail to authenticate.
        """
        patron_bot = PatronBot(last_name=last_name,
                               iii_id=iii_id)
        user = None
        if patron_bot.is_valid:
            logging.error("Patron is valid")
            user, created = User.objects.get_or_create(username=iii_id)
            logging.error("Patron user is %s" % user)
            if created:
                user = RemoteUserBackend.configure_user(user)
        return user

    def get_user(self,iii_id):
        """
        Takes ``iii_id`` and tries to retrieve existing User
        """
        try:
            return User.objects.get(username=iii_id)
        except User.DoesNotExist:
            return None
            
        
        
