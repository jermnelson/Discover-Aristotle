"""
 signals.py -- module signals classes for inter-application
 communication of catalog specific signals within the Aristotle Framework
"""
from django.template import Context,loader

def catalog_message(sender,
                    message_text,
                    message_creator,
                    **kwargs):
    """Sends out a catalog message"""
    return None
