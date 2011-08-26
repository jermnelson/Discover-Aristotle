""" 
 models.py -- Django model classes for supporting Aristotle 
 catalog
"""
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright: Currently copyrighted by Colorado College
#
__author__ = 'Jeremy Nelson'

from django.db import models

class Comment(models.Model):
    """`Comment` model stores comments made by users of 
    Aristotle's catalog application.
    """
    created_by = models.CharField(max_length=150) # Store identification text (email, TIGER number, etc.)
    created_on = models.DateTimeField('last updated',
                                      auto_now_add=True)
    text = models.TextField()
