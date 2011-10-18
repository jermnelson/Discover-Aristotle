from django.contrib import admin
from vendors.iii.models import IIIStatusCode,Fund,FundProcessLog

admin.site.register(IIIStatusCode)
admin.site.register(Fund)
admin.site.register(FundProcessLog)
