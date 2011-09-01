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

class Loadtables(models.Model):
    name = models.CharField(max_length=50, blank=True)
    description= models.TextField(null=True, blank=True)

    class Meta:
        db_table = u'loadtables'

class Notes(models.Model):
    created_by = models.CharField(max_length=100, blank=True)
    created_on = models.TextField(blank=True) # This field type is a guess.
    label = models.CharField(max_length=100, blank=True)
    note_value = models.TextField(blank=True)
    class Meta:
        db_table = u'notes'

class Process(models.Model):
    name = models.CharField(max_length=50, blank=True)
    display = models.CharField(max_length=100, blank=True)
    class Meta:
        db_table = u'process'

class Recordloadlogs(models.Model):
    created_by = models.CharField(max_length=100, blank=True)
    created_on = models.DateTimeField() # This field type is a guess.
    process_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(max_length=100, blank=True)
    is_processed = models.BooleanField(null=True, blank=True)
    load_table_id = models.IntegerField(null=True, blank=True)
    modified_file = models.TextField(blank=True) # This field type is a guess.
    new_records = models.IntegerField(null=True, blank=True)
    notes_id = models.IntegerField(null=True, blank=True)
    original_file = models.TextField(blank=True) # This field type is a guess.
    overlaid_records = models.IntegerField(null=True, blank=True)
    record_type_id = models.IntegerField(null=True, blank=True)
    rejected_records = models.IntegerField(null=True, blank=True)
    source_id = models.IntegerField(null=True, blank=True)
    ils_result = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'recordloadlogs'

class Recordtypes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30, blank=True)
    class Meta:
        db_table = u'recordtypes'

class Sources(models.Model):
    id = models.IntegerField(primary_key=True)
    alt_name = models.CharField(max_length=50, blank=True)
    changed = models.BooleanField(null=True, blank=True)
    created_by = models.CharField(max_length=100, blank=True)
    created_on = models.TextField(blank=True) # This field type is a guess.
    name = models.CharField(max_length=50, blank=True)
    source_type = models.CharField(max_length=20, blank=True)
    class Meta:
        db_table = u'sources'

class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=100, blank=True)
    display = models.CharField(max_length=50, blank=True)
    created_by = models.CharField(max_length=50, blank=True)
    created_on = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = u'users'

