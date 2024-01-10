from django.contrib import admin
from .models import DBPilots, DBAirCompany, DBArrivalPoint, DBDeparturePoint, DBFlight, DBReason, DBManualControlRequest

# Register your models here.
admin.site.register(DBPilots)
admin.site.register(DBAirCompany)
admin.site.register(DBArrivalPoint)
admin.site.register(DBDeparturePoint)
admin.site.register(DBFlight)
admin.site.register(DBReason)
admin.site.register(DBManualControlRequest)
