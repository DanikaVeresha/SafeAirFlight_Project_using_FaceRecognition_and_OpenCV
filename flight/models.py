from django.db import models


class DBPilots(models.Model):
    id_users = models.UUIDField()
    id_pilot = models.IntegerField
    username = models.CharField(max_length=10000)
    password = models.CharField(max_length=10000)
    email = models.EmailField(null=True)
    address_registration = models.CharField(max_length=10000, null=True)
    company_name = models.CharField(max_length=10000, null=True)
    flight_number = models.IntegerField(null=True)
    departure_point = models.CharField(max_length=10000, null=True)
    arrival_point = models.CharField(max_length=10000, null=True)
    pilot_registration_date = models.DateTimeField(null=True)


class DBAirCompany(models.Model):
    id_users = models.UUIDField()
    id_DBAirCompany = models.IntegerField
    name = models.CharField(max_length=10000, null=True)
    pilot = models.CharField(max_length=10000)
    company_address = models.CharField(max_length=10000, null=True)


class DBDeparturePoint(models.Model):
    id_users = models.UUIDField()
    id_DBDeparturePoint = models.IntegerField
    point = models.CharField(max_length=10000, null=True)
    airport_address = models.CharField(max_length=10000, null=True)
    latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)


class DBArrivalPoint(models.Model):
    id_users = models.UUIDField()
    id_DBArrivalPoint = models.IntegerField
    point = models.CharField(max_length=10000, null=True)
    airport_address = models.CharField(max_length=10000, null=True)
    latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)


class DBReason(models.Model):
    id_users = models.UUIDField()
    id_DBReason = models.IntegerField
    first_reason = models.CharField(max_length=10000, null=True)
    second_reason = models.CharField(max_length=10000, default='absent')
    old_departure_point = models.CharField(max_length=10000, null=True)
    old_arrival_point = models.CharField(max_length=10000, null=True)
    new_departure_point = models.CharField(max_length=10000, null=True)
    original_latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    original_longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    changed_arrival_point = models.CharField(max_length=10000, null=True)
    corrected_latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    corrected_longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    weather_new_location = models.CharField(max_length=10000, null=True)
    description_weather = models.CharField(max_length=10000, null=True)


class DBFlight(models.Model):
    id_users = models.UUIDField()
    id_DBFlight = models.IntegerField
    flight_number = models.IntegerField(null=True)
    pilot = models.CharField(max_length=10000)
    aircompany = models.CharField(max_length=10000, null=True)
    airflight_route = models.CharField(max_length=10000, null=True)
    departure_point = models.CharField(max_length=10000, null=True)
    departure_point_address_airport = models.CharField(max_length=10000, null=True)
    departure_point_latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    departure_point_longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    arrival_point = models.CharField(max_length=10000, null=True)
    arrival_point_address_airport = models.CharField(max_length=10000, null=True)
    arrival_point_latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    arrival_point_longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    distance_km = models.FloatField(null=True)
    flight_time = models.TimeField(null=True)
    departure_date = models.DateTimeField(null=True)
    departure_time = models.TimeField(null=True)
    arrival_date = models.DateField(null=True)
    arrival_time = models.TimeField(null=True)
    number_of_passengers = models.IntegerField(null=True)
    flight_condition = models.CharField(max_length=10000, default='without correction')
    reason_of_correction = models.CharField(max_length=10000, null=True)
    departure_point_weather = models.CharField(max_length=10000, null=True)
    arrival_point_weather = models.CharField(max_length=10000, null=True)


class DBManualControlRequest(models.Model):
    id_users = models.UUIDField()
    id_DBManualControlRequest = models.IntegerField
    reason = models.CharField(max_length=10000, null=True)
    day_of_the_week = models.IntegerField(null=True)
    confirm_request = models.CharField(max_length=10000, null=True)
    old_departure_point = models.CharField(max_length=10000, null=True)
    old_arrival_point = models.CharField(max_length=10000, null=True)
    new_departure_point = models.CharField(max_length=10000, null=True)
    new_departure_latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    new_departure_longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    changed_arrival_point = models.CharField(max_length=10000, null=True)
    changed_arrival_latitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    changed_arrival_longitude = models.DecimalField(decimal_places=4, max_digits=10, null=True)
    distance_km = models.FloatField(null=True)









