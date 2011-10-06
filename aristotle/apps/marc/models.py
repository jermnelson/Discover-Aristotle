# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
__author__ = 'Jeremy Nelson, Cindy Tappan'

from django.db import models

class Notes(models.Model):
    label = models.CharField(max_length=100, blank=True)
    note_value = models.TextField(blank=True)
    record_load_log_id = models.ForeignKey('RecordLoadLog')
    class Meta:
        db_table = u'notes'

class RecordLoadLog(models.Model):
    process_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(max_length=100, blank=True)
    is_processed = models.NullBooleanField(null=True, blank=True)
    load_table = models.IntegerField(null=True, blank=True)
#    modified_file = models.FileField() 
    new_records = models.IntegerField(null=True, blank=True)
#    original_file = models.FileField() 
    overlaid_records = models.IntegerField(null=True, blank=True)
    record_type = models.IntegerField(null=True, blank=True)
    rejected_records = models.IntegerField(null=True, blank=True)
    source_id = models.IntegerField(null=True, blank=True)
    ils_result = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'recordloadlogs'

