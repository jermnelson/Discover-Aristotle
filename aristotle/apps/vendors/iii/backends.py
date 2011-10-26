__author__ = 'Jeremy Nelson'

import logging,sys
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User 
from vendors.iii.bots.iiibots import PatronBot

class IIIUserBackend(ModelBackend):
    """
    This backend is used with III's Patron API to authenticate a user 
    using a last name and an III identification number.
    """

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
            try:
                user = User.objects.get(username=iii_id)
            except User.DoesNotExist:
                user = User(username=iii_id,last_name=last_name,is_active=True)
                user.save()
        return user

    def get_user(self,user_id):
        """
        Takes ``user_id`` and tries to retrieve existing User
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            
        
        
