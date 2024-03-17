import datetime
import random
from datetime import datetime
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
from django.shortcuts import render, redirect
from flight.models import DBFlight, DBPilots, DBReason, DBArrivalPoint, DBDeparturePoint, DBAirCompany, DBManualControlRequest
import googlemaps
import polyline
from flight.config import api_key_points, OPENWEATHER_API, NOFLYZONE, access_code_conf
import math
import requests
import cv2
import face_recognition
import pickle


def airflight(request):
    if not request.user.is_authenticated:
        return redirect('/user/login')
    pilot_id = request.user.id
    pilot = DBPilots.objects.filter(id=pilot_id).first()
    if request.method == 'POST':
        pilots_email = request.POST.get('email')
        pilots_address_registration = request.POST.get('address')
        company_name = request.POST.get('company_name')
        flight_number = request.POST.get('flight_number')
        company_address = request.POST.get('company_address')
        departure_point = request.POST.get('departure_point')
        arrival_point = request.POST.get('arrival_point')
        flight_time = request.POST.get('flight_time')
        departure_time = request.POST.get('departure_time')
        departure_date = request.POST.get('departure_date')
        arrival_time = request.POST.get('arrival_time')
        arrival_date = request.POST.get('arrival_date')
        number_of_passengers = request.POST.get('number_of_passengers')

        res_pilots = DBPilots.objects.filter(id_users=pilot.id_users)
        for itemPilot in res_pilots:
            itemPilot.username = request.user.username
            itemPilot.password = request.user.password
            itemPilot.email = pilots_email
            itemPilot.address_registration = pilots_address_registration
            itemPilot.company_name = company_name
            itemPilot.flight_number = flight_number
            itemPilot.departure_point = departure_point
            itemPilot.arrival_point = arrival_point
            itemPilot.pilot_registration_date = datetime.now()
            itemPilot.save()

        company_obj = DBAirCompany(
            id_users=pilot.id_users,
            name=company_name,
            pilot=request.user.username,
            company_address=company_address
        )
        company_obj.save()

        geolocator = Nominatim(user_agent="flight")
        location_departure_point = geolocator.geocode(departure_point)
        departure_latitude = location_departure_point.latitude
        departure_longitude = location_departure_point.longitude
        departure_point_address = geolocator.reverse((departure_latitude,
                                                      departure_longitude))
        departure_obj = DBDeparturePoint(
            id_users=pilot.id_users,
            point=departure_point,
            airport_address=departure_point_address,
            latitude=departure_latitude,
            longitude=departure_longitude
        )
        departure_obj.save()

        geolocator = Nominatim(user_agent="flight")
        location_arrival_point = geolocator.geocode(arrival_point)
        arrival_latitude = location_arrival_point.latitude
        arrival_longitude = location_arrival_point.longitude
        arrival_point_address = geolocator.reverse((arrival_latitude,
                                                    arrival_longitude))
        arrival_obj = DBArrivalPoint(
            id_users=pilot.id_users,
            point=arrival_point,
            airport_address=arrival_point_address,
            latitude=arrival_latitude,
            longitude=arrival_longitude
        )
        arrival_obj.save()

        distance_km = haversine((departure_latitude,
                                 departure_longitude),
                                (arrival_latitude,
                                 arrival_longitude),
                                unit=Unit.KILOMETERS)
        flight_obj = DBFlight(
            id_users=pilot.id_users,
            flight_number=flight_number,
            pilot=request.user.username,
            aircompany=company_name,
            airflight_route=(departure_point, arrival_point),
            departure_point=departure_point,
            departure_point_address_airport=departure_point_address,
            departure_point_latitude=departure_latitude,
            departure_point_longitude=departure_longitude,
            arrival_point=arrival_point,
            arrival_point_address_airport=arrival_point_address,
            arrival_point_latitude=arrival_latitude,
            arrival_point_longitude=arrival_longitude,
            distance_km=distance_km,
            flight_time=flight_time,
            departure_date=departure_date,
            departure_time=departure_time,
            arrival_date=arrival_date,
            arrival_time=arrival_time,
            number_of_passengers=number_of_passengers
        )
        flight_obj.save()

        now = datetime.now()
        gmaps = googlemaps.Client(key=api_key_points)
        result_gmaps = gmaps.directions(departure_point,
                                        arrival_point,
                                        mode="transit",
                                        departure_time=now)
        raw = result_gmaps[0]['overview_polyline']['points']
        points = polyline.decode(raw)
        for item in points:
            url_v1 = requests.get(
                "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                (float(item[0]), float(item[1]), str(OPENWEATHER_API))
            )
            data_v1 = url_v1.json()

            no_fly_zone = NOFLYZONE
            if no_fly_zone == item:
                object_rotation_angel = 10 * (3.14 / 180)
                x_latitude_zone = (item[0] * math.cos(object_rotation_angel)) - \
                                  (item[1] * math.sin(object_rotation_angel))
                y_longitude_zone = (item[0] * math.sin(object_rotation_angel)) + \
                                   (item[1] * math.cos(object_rotation_angel))

                url_v1_2 = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                    (float(x_latitude_zone), float(y_longitude_zone), str(OPENWEATHER_API))
                )
                data_v1_2 = url_v1_2.json()
                if data_v1_2['weather'][0]['description'] == 'thunderstorm':
                    object_rotation_angel_v1_2 = 10 * (3.14 / 180)
                    x_latitude_v1_2 = (x_latitude_zone * math.cos(object_rotation_angel_v1_2)) - \
                                      (y_longitude_zone * math.sin(object_rotation_angel_v1_2))
                    y_longitude_v1_2 = (x_latitude_zone * math.sin(object_rotation_angel_v1_2)) + \
                                       (y_longitude_zone * math.cos(object_rotation_angel_v1_2))

                    url_v1_3 = requests.get(
                        "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                        (float(x_latitude_v1_2), float(y_longitude_v1_2), str(OPENWEATHER_API))
                    )
                    data_v1_3 = url_v1_3.json()
                    temp_v1_3 = float(data_v1_3['main']['temp']) - 273.15
                    temp_min_v1_3 = float(data_v1_3['main']['temp_min']) - 273.15
                    temp_max_v1_3 = float(data_v1_3['main']['temp_max']) - 273.15
                    dict_v1_3 = {
                        "temp": round(temp_v1_3, 2),
                        "temp_min": round(temp_min_v1_3, 2),
                        "temp_max": round(temp_max_v1_3, 2),
                        "wind and speed": data_v1_3['wind']['speed']
                    }
                    reason_obj_v1_3 = DBReason(
                        id_users=pilot.id_users,
                        first_reason='No fly zone and:',
                        second_reason=data_v1_2['weather'][0]['description'],
                        old_departure_point=departure_point,
                        old_arrival_point=arrival_point,
                        new_departure_point=departure_point,
                        original_latitude=item[0],
                        original_longitude=item[1],
                        changed_arrival_point=arrival_point,
                        corrected_latitude=(x_latitude_zone, x_latitude_v1_2),
                        corrected_longitude=(y_longitude_zone, y_longitude_v1_2),
                        weather_new_location=(data_v1_3['weather'][0]['description']),
                        description_weather=dict_v1_3
                    )
                    reason_obj_v1_3.save()

                    weather_departure_point_v1_3 = (departure_latitude,
                                                    departure_longitude)
                    weather_arrival_point_v1_3 = (arrival_latitude,
                                                  arrival_longitude)

                    url_Departure_v1_3 = requests.get(
                        "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                        (float(weather_departure_point_v1_3[0]), float(weather_departure_point_v1_3[1]),
                         str(OPENWEATHER_API))
                    )
                    data_Departure_v1_3 = url_Departure_v1_3.json()
                    temp_Departure_v1_3 = float(data_Departure_v1_3['main']['temp']) - 273.15
                    temp_min_Departure_v1_3 = float(data_Departure_v1_3['main']['temp_min']) - 273.15
                    temp_max_Departure_v1_3 = float(data_Departure_v1_3['main']['temp_max']) - 273.15
                    dict_original_weatherDeparture_v1_3 = {
                        "conditions": data_Departure_v1_3['weather'][0]['description'],
                        "temp": round(temp_Departure_v1_3, 2),
                        "temp_min": round(temp_min_Departure_v1_3, 2),
                        "temp_max": round(temp_max_Departure_v1_3, 2),
                        "wind and speed": data_Departure_v1_3['wind']['speed']
                    }

                    url_Arrival_v1_3 = requests.get(
                        "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                        (float(weather_arrival_point_v1_3[0]), float(weather_arrival_point_v1_3[1]),
                         str(OPENWEATHER_API))
                    )
                    data_Arrival_v1_3 = url_Arrival_v1_3.json()
                    temp_Arrival_v1_3 = float(data_Arrival_v1_3['main']['temp']) - 273.15
                    temp_min_Arrival_v1_3 = float(data_Arrival_v1_3['main']['temp_min']) - 273.15
                    temp_max_Arrival_v1_3 = float(data_Arrival_v1_3['main']['temp_max']) - 273.15
                    dict_original_weatherArrival_v1_3 = {
                        "conditions": data_Arrival_v1_3['weather'][0]['description'],
                        "temp": round(temp_Arrival_v1_3, 2),
                        "temp_min": round(temp_min_Arrival_v1_3, 2),
                        "temp_max": round(temp_max_Arrival_v1_3, 2),
                        "wind and speed": data_Arrival_v1_3['wind']['speed']
                    }
                    res_flight_v1_3 = DBFlight.objects.filter(id_users=pilot.id_users)
                    for item_v1_3 in res_flight_v1_3:
                        item_v1_3.flight_condition = 'with correction'
                        item_v1_3.reason_of_correction = ('No fly zone and:',
                                                          data_v1_2['weather'][0]['description'])
                        item_v1_3.departure_point_weather = dict_original_weatherDeparture_v1_3
                        item_v1_3.arrival_point_weather = dict_original_weatherArrival_v1_3
                        item_v1_3.save()
                else:
                    weather_departure_point_v1_4 = (departure_latitude,
                                                    departure_longitude)
                    weather_arrival_point_v1_4 = (arrival_latitude,
                                                  arrival_longitude)

                    url_Departure_v1_4 = requests.get(
                        "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                        (float(weather_departure_point_v1_4[0]), float(weather_departure_point_v1_4[1]),
                         str(OPENWEATHER_API))
                    )
                    data_Departure_v1_4 = url_Departure_v1_4.json()
                    temp_Departure_v1_4 = float(data_Departure_v1_4['main']['temp']) - 273.15
                    temp_min_Departure_v1_4 = float(data_Departure_v1_4['main']['temp_min']) - 273.15
                    temp_max_Departure_v1_4 = float(data_Departure_v1_4['main']['temp_max']) - 273.15
                    dict_normal_weatherDeparture_v1_4 = {
                        "conditions": data_Departure_v1_4['weather'][0]['description'],
                        "temp": round(temp_Departure_v1_4, 2),
                        "temp_min": round(temp_min_Departure_v1_4, 2),
                        "temp_max": round(temp_max_Departure_v1_4, 2),
                        "wind and speed": data_Departure_v1_4['wind']['speed']
                    }

                    url_Arrival_v1_4 = requests.get(
                        "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                        (float(weather_arrival_point_v1_4[0]), float(weather_arrival_point_v1_4[1]),
                         str(OPENWEATHER_API))
                    )
                    data_Arrival_v1_4 = url_Arrival_v1_4.json()
                    temp_Arrival_v1_4 = float(data_Arrival_v1_4['main']['temp']) - 273.15
                    temp_min_Arrival_v1_4 = float(data_Arrival_v1_4['main']['temp_min']) - 273.15
                    temp_max_Arrival_v1_4 = float(data_Arrival_v1_4['main']['temp_max']) - 273.15
                    dict_original_weatherArrival_v1_4 = {
                        "conditions": data_Arrival_v1_4['weather'][0]['description'],
                        "temp": round(temp_Arrival_v1_4, 2),
                        "temp_min": round(temp_min_Arrival_v1_4, 2),
                        "temp_max": round(temp_max_Arrival_v1_4, 2),
                        "wind and speed": data_Arrival_v1_4['wind']['speed']
                    }
                    res_flight_v1_4 = DBFlight.objects.filter(id_users=pilot.id_users)
                    for item_v1_4 in res_flight_v1_4:
                        item_v1_4.reason_of_correction = 'No fly zone',
                        item_v1_4.departure_point_weather = dict_normal_weatherDeparture_v1_4
                        item_v1_4.arrival_point_weather = dict_original_weatherArrival_v1_4
                        item_v1_4.save()
            elif data_v1['weather'][0]['description'] == 'thunderstorm':
                object_rotation_angel_v2 = 10 * (3.14 / 180)
                x_latitude_v2 = (item[0] * math.cos(object_rotation_angel_v2)) - \
                                (item[1] * math.sin(object_rotation_angel_v2))
                y_longitude_v2 = (item[0] * math.sin(object_rotation_angel_v2)) + \
                                 (item[1] * math.cos(object_rotation_angel_v2))

                url_v2 = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                    (float(x_latitude_v2), float(y_longitude_v2), str(OPENWEATHER_API))
                )
                data_v2 = url_v2.json()
                temp_v2 = float(data_v2['main']['temp']) - 273.15
                temp_min_v2 = float(data_v2['main']['temp_min']) - 273.15
                temp_max_v2 = float(data_v2['main']['temp_max']) - 273.15
                dict_v2 = {
                    "temp": round(temp_v2, 2),
                    "temp_min": round(temp_min_v2, 2),
                    "temp_max": round(temp_max_v2, 2),
                    "wind and speed": data_v2['wind']['speed']
                }
                reason_obj_v2 = DBReason(
                    id_users=pilot.id_users,
                    first_reason=data_v1['weather'][0]['description'],
                    second_reason='absent',
                    old_departure_point=departure_point,
                    old_arrival_point=arrival_point,
                    new_departure_point=departure_point,
                    original_latitude=item[0],
                    original_longitude=item[1],
                    changed_arrival_point=arrival_point,
                    corrected_latitude=x_latitude_v2,
                    corrected_longitude=y_longitude_v2,
                    weather_new_location=data_v2['weather'][0]['description'],
                    description_weather=dict_v2
                )
                reason_obj_v2.save()

                weather_departure_point_v2 = (departure_latitude,
                                              departure_longitude)
                weather_arrival_point_v2 = (arrival_latitude,
                                            arrival_longitude)

                url_Departure_v2 = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                    (float(weather_departure_point_v2[0]), float(weather_departure_point_v2[1]),
                     str(OPENWEATHER_API))
                )
                data_Departure_v2 = url_Departure_v2.json()
                temp_Departure_v2 = float(data_Departure_v2['main']['temp']) - 273.15
                temp_min_Departure_v2 = float(data_Departure_v2['main']['temp_min']) - 273.15
                temp_max_Departure_v2 = float(data_Departure_v2['main']['temp_max']) - 273.15
                dict_original_weatherDeparture_v2 = {
                    "conditions": data_Departure_v2['weather'][0]['description'],
                    "temp": round(temp_Departure_v2, 2),
                    "temp_min": round(temp_min_Departure_v2, 2),
                    "temp_max": round(temp_max_Departure_v2, 2),
                    "wind and speed": data_Departure_v2['wind']['speed']
                }

                url_Arrival_v2 = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                    (float(weather_arrival_point_v2[0]), float(weather_arrival_point_v2[1]),
                     str(OPENWEATHER_API))
                )
                data_Arrival_v2 = url_Arrival_v2.json()
                temp_Arrival_v2 = float(data_Arrival_v2['main']['temp']) - 273.15
                temp_min_Arrival_v2 = float(data_Arrival_v2['main']['temp_min']) - 273.15
                temp_max_Arrival_v2 = float(data_Arrival_v2['main']['temp_max']) - 273.15
                dict_original_weatherArrival_v2 = {
                    "conditions": data_Arrival_v2['weather'][0]['description'],
                    "temp": round(temp_Arrival_v2, 2),
                    "temp_min": round(temp_min_Arrival_v2, 2),
                    "temp_max": round(temp_max_Arrival_v2, 2),
                    "wind and speed": data_Arrival_v2['wind']['speed']
                }
                res_flight_v2 = DBFlight.objects.filter(id_users=pilot.id_users)
                for item_v2 in res_flight_v2:
                    item_v2.flight_condition = 'with correction'
                    item_v2.reason_of_correction = data_v1['weather'][0]['description']
                    item_v2.weather_departure_point = dict_original_weatherDeparture_v2
                    item_v2.weather_arrival_point = dict_original_weatherArrival_v2
                    item_v2.save()
            else:
                weather_departure_point_v3 = (departure_latitude,
                                              departure_longitude)
                weather_arrival_point_v3 = (arrival_latitude,
                                            arrival_longitude)

                url_Departure_v3 = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                    (float(weather_departure_point_v3[0]), float(weather_departure_point_v3[1]),
                     str(OPENWEATHER_API))
                )
                data_Departure_v3 = url_Departure_v3.json()
                temp_Departure_v3 = float(data_Departure_v3['main']['temp']) - 273.15
                temp_min_Departure_v3 = float(data_Departure_v3['main']['temp_min']) - 273.15
                temp_max_Departure_v3 = float(data_Departure_v3['main']['temp_max']) - 273.15
                dict_original_weatherDeparture_v3 = {
                    "conditions": data_Departure_v3['weather'][0]['description'],
                    "temp": round(temp_Departure_v3, 2),
                    "temp_min": round(temp_min_Departure_v3, 2),
                    "temp_max": round(temp_max_Departure_v3, 2),
                    "wind and speed": data_Departure_v3['wind']['speed']
                }

                url_Arrival_v3 = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                    (float(weather_arrival_point_v3[0]), float(weather_arrival_point_v3[1]),
                     str(OPENWEATHER_API))
                )
                data_Arrival_v3 = url_Arrival_v3.json()
                temp_Arrival_v3 = float(data_Arrival_v3['main']['temp']) - 273.15
                temp_min_Arrival_v3 = float(data_Arrival_v3['main']['temp_min']) - 273.15
                temp_max_Arrival_v3 = float(data_Arrival_v3['main']['temp_max']) - 273.15
                dict_original_weatherArrival_v3 = {
                    "conditions": data_Arrival_v3['weather'][0]['description'],
                    "temp": round(temp_Arrival_v3, 2),
                    "temp_min": round(temp_min_Arrival_v3, 2),
                    "temp_max": round(temp_max_Arrival_v3, 2),
                    "wind and speed": data_Arrival_v3['wind']['speed']
                }
                res_flight_v3 = DBFlight.objects.filter(id_users=pilot.id_users)
                for item_v3 in res_flight_v3:
                    item_v3.reason_of_correction = 'absent'
                    item_v3.departure_point_weather = dict_original_weatherDeparture_v3
                    item_v3.arrival_point_weather = dict_original_weatherArrival_v3
                    item_v3.save()

    result_one = DBFlight.objects.filter(id_users=pilot.id_users)
    return render(request, 'airlineflight.html', {'airlineflight_res': result_one})


def manual_control_request(request):
    if not request.user.is_authenticated:
        return redirect('/user/login')
    pilot_id = request.user.id
    pilot = DBPilots.objects.filter(id=pilot_id).first()
    pilot_id = int(DBPilots.objects.order_by('-id').first().id)
    unique_id = int(DBFlight.objects.order_by('-id').first().id)
    access_code = request.POST.get('access_code')
    old_departure_point = DBDeparturePoint.objects.values_list('point', flat=True).get(pk=unique_id)
    old_arrival_point = DBArrivalPoint.objects.values_list('point', flat=True).get(pk=unique_id)
    changed_arrival_point = request.POST.get('changed_arrival_point')
    reason = request.POST.get('reason_for_route_correction')
    confirm_request = request.POST.get('confirm_the_request')
    date_week = datetime.today().isoweekday()
    data = pickle.loads(open('face_enc_terrorist', 'rb').read())
    video_cap = cv2.VideoCapture(0)
    if request.method == 'POST':
        while True:
            ret, frame = video_cap.read()
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb)
            for encoding in encodings:
                matches = face_recognition.compare_faces(data['encodings'], encoding)
                if True in matches:
                    if access_code == access_code_conf[str(date_week)]:
                        reason_obj_terrorist = DBReason(
                            id_users=pilot.id_users,
                            first_reason='MANUAL CONTROL REQUEST',
                            second_reason='We found the Terrorist`s person',
                            old_departure_point=DBFlight.objects.values_list('departure_point', flat=True).get(pk=unique_id),
                            old_arrival_point=DBFlight.objects.values_list('arrival_point', flat=True).get(pk=unique_id),
                            new_departure_point=DBFlight.objects.values_list('departure_point', flat=True).get(pk=unique_id),
                            original_latitude=DBFlight.objects.values_list('departure_point_latitude', flat=True).get(pk=unique_id),
                            original_longitude=DBFlight.objects.values_list('departure_point_longitude',flat=True).get(pk=unique_id),
                            changed_arrival_point=DBFlight.objects.values_list('arrival_point', flat=True).get(pk=unique_id),
                            corrected_latitude=DBFlight.objects.values_list('arrival_point_latitude',flat=True).get(pk=unique_id),
                            corrected_longitude=DBFlight.objects.values_list('arrival_point_longitude',flat=True).get(pk=unique_id),
                            weather_new_location=DBFlight.objects.values_list('arrival_point_weather', flat=True).get(pk=unique_id),
                            description_weather=DBFlight.objects.values_list('arrival_point_weather', flat=True).get(pk=unique_id),
                        )
                        reason_obj_terrorist.save()

                        MCR_obj_terr = DBManualControlRequest(
                            id_users=pilot.id_users,
                            reason=(f'MANUAL CONTROL REQUEST, '
                                    f'The reason indicated by the pilot: {reason},'
                                    f'The main reason: We fond the terrorist`s person'),
                            day_of_the_week=date_week,
                            confirm_request=confirm_request,
                            old_departure_point=old_departure_point,
                            old_arrival_point=old_arrival_point,
                            new_departure_point=old_departure_point,
                            new_departure_latitude=DBFlight.objects.values_list('departure_point_latitude', flat=True).get(pk=unique_id),
                            new_departure_longitude=DBFlight.objects.values_list('departure_point_longitude', flat=True).get(pk=unique_id),
                            changed_arrival_point=DBFlight.objects.values_list('arrival_point', flat=True).get(pk=unique_id),
                            changed_arrival_latitude=DBFlight.objects.values_list('arrival_point_latitude', flat=True).get(pk=unique_id),
                            changed_arrival_longitude=DBFlight.objects.values_list('arrival_point_longitude', flat=True).get(pk=unique_id),
                            distance_km=DBFlight.objects.values_list('distance_km', flat=True).get(pk=unique_id),

                        )
                        MCR_obj_terr.save()

                        res_flight_ter = DBFlight.objects.filter(id_users=pilot.id_users)
                        for itemFlight_terr in res_flight_ter:
                            itemFlight_terr.flight_condition = 'with correction'
                            itemFlight_terr.reason_of_correction = (f'The main reason:A threat to safe air travel has '
                                                                    f'been detected.Found among passengers Terrorist '
                                                                    f'person; Mode activation: MANUAL CONTROL REQUEST; '
                                                                    f'Entered pilot`s reason: {reason}')
                            itemFlight_terr.save()
                    else:
                        error_result = DBFlight.objects.filter(id_users=pilot.id_users)
                        return render(request, 'airlineflight_blocked.html', {'airlineflight_res_error': error_result})
                    result_terrorist = DBFlight.objects.filter(id_users=pilot.id_users)
                    return render(request, 'airlineflight_blocked.html', {'airlineflight_res_v1': result_terrorist})

                elif False in matches:
                    if access_code == access_code_conf[str(date_week)]: #A dictionary of unique pairs in key-value format,
                                                                        # where the key is the day of the week in integer
                                                                        # format, and the value is a random word that will
                                                                        # be active for 7 days, after which the dispatcher
                                                                        # will need to update the values and upload the
                                                                        # updated file to the system (to avoid leakage
                                                                        # information to interested parties)
                        now = datetime.now()
                        gmaps = googlemaps.Client(key=api_key_points)
                        result_gmaps = gmaps.directions(old_departure_point,
                                                        old_arrival_point,
                                                        mode="transit",
                                                        departure_time=now)
                        raw = result_gmaps[0]['overview_polyline']['points']
                        points = polyline.decode(raw)
                        starting_point = random.choice(points)
                        x_latitude_sp = starting_point[0]
                        y_longitude_sp = starting_point[1]
                        if x_latitude_sp < 0:                           # If the system crashes
                            geolocator = Nominatim(user_agent="flight")
                            starting_point_address_v1 = geolocator.reverse((y_longitude_sp,
                                                                            x_latitude_sp))
                            geolocator = Nominatim(user_agent="flight")
                            location_changed_arrival_point_v1 = geolocator.geocode(changed_arrival_point)
                            changed_arrival_latitude_v1 = location_changed_arrival_point_v1.latitude
                            changed_arrival_longitude_v1 = location_changed_arrival_point_v1.longitude
                            new_arrival_point_address_v1 = geolocator.reverse((changed_arrival_latitude_v1,
                                                                              changed_arrival_longitude_v1))
                            distance_km_v1 = haversine((y_longitude_sp,
                                                        x_latitude_sp),
                                                       (changed_arrival_latitude_v1,
                                                        changed_arrival_longitude_v1),
                                                       unit=Unit.KILOMETERS)
                            MCR_v1 = DBManualControlRequest(
                                id_users=pilot.id_users,
                                reason=(f'MANUAL CONTROL REQUEST, '
                                        f'The reason indicated by the pilot: {reason}'),
                                day_of_the_week=date_week,
                                confirm_request=confirm_request,
                                old_departure_point=old_departure_point,
                                old_arrival_point=old_arrival_point,
                                new_departure_point=starting_point_address_v1,
                                new_departure_latitude=y_longitude_sp,
                                new_departure_longitude=x_latitude_sp,
                                changed_arrival_point=changed_arrival_point,
                                changed_arrival_latitude=changed_arrival_latitude_v1,
                                changed_arrival_longitude=changed_arrival_longitude_v1,
                                distance_km=distance_km_v1
                            )
                            MCR_v1.save()

                            pilot_obj_v1 = DBPilots(
                                id_users=pilot.id_users,
                                username=request.user.username,
                                password=request.user.password,
                                email=DBPilots.objects.values_list('email', flat=True).get(pk=pilot_id),
                                address_registration=DBPilots.objects.values_list('address_registration', flat=True).get(pk=pilot_id),
                                company_name=DBPilots.objects.values_list('company_name', flat=True).get(pk=pilot_id),
                                flight_number=DBPilots.objects.values_list('flight_number', flat=True).get(pk=pilot_id),
                                departure_point=starting_point_address_v1,
                                arrival_point=changed_arrival_point,
                                pilot_registration_date=datetime.now()
                            )
                            pilot_obj_v1.save()

                            company_obj_v1 = DBAirCompany(
                                id_users=pilot.id_users,
                                name=DBAirCompany.objects.values_list('name', flat=True).get(pk=unique_id),
                                pilot=DBAirCompany.objects.values_list('pilot', flat=True).get(pk=unique_id),
                                company_address=DBAirCompany.objects.values_list('company_address', flat=True).get(pk=unique_id)
                            )
                            company_obj_v1.save()

                            departure_point_obj_v1 = DBDeparturePoint(
                                id_users=pilot.id_users,
                                point=starting_point_address_v1,
                                airport_address=starting_point_address_v1,
                                latitude=y_longitude_sp,
                                longitude=x_latitude_sp
                            )
                            departure_point_obj_v1.save()

                            arrival_point_obj_v1 = DBArrivalPoint(
                                id_users=pilot.id_users,
                                point=changed_arrival_point,
                                airport_address=new_arrival_point_address_v1,
                                latitude=changed_arrival_latitude_v1,
                                longitude=changed_arrival_longitude_v1
                            )
                            arrival_point_obj_v1.save()

                            weather_new_arrival_point_v1 = (changed_arrival_latitude_v1,
                                                            changed_arrival_longitude_v1)

                            url_Arrival_v1 = requests.get(
                                "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                                (float(weather_new_arrival_point_v1[0]), float(weather_new_arrival_point_v1[1]),
                                 str(OPENWEATHER_API))
                            )
                            data_Arrival_v1 = url_Arrival_v1.json()
                            temp_Arrival_v1 = float(data_Arrival_v1['main']['temp']) - 273.15
                            temp_min_Arrival_v1 = float(data_Arrival_v1['main']['temp_min']) - 273.15
                            temp_max_Arrival_v1 = float(data_Arrival_v1['main']['temp_max']) - 273.15
                            dict_weatherArrival_v1 = {
                                "conditions": data_Arrival_v1['weather'][0]['description'],
                                "temp": round(temp_Arrival_v1, 2),
                                "temp_min": round(temp_min_Arrival_v1, 2),
                                "temp_max": round(temp_max_Arrival_v1, 2),
                                "wind and speed": data_Arrival_v1['wind']['speed']
                            }
                            reason_obj_v1 = DBReason(
                                id_users=pilot.id_users,
                                first_reason='Manual Control Request',
                                second_reason=reason,
                                old_departure_point=old_departure_point,
                                old_arrival_point=old_arrival_point,
                                new_departure_point=starting_point_address_v1,
                                original_latitude=y_longitude_sp,
                                original_longitude=x_latitude_sp,
                                changed_arrival_point=changed_arrival_point,
                                corrected_latitude=changed_arrival_latitude_v1,
                                corrected_longitude=changed_arrival_longitude_v1,
                                weather_new_location=data_Arrival_v1['weather'][0]['description'],
                                description_weather=dict_weatherArrival_v1,
                            )
                            reason_obj_v1.save()

                            weather_new_departure_point_v1 = (y_longitude_sp, x_latitude_sp)
                            url_Departure_v1 = requests.get(
                                "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                                (float(weather_new_departure_point_v1[0]), float(weather_new_departure_point_v1[1]),
                                 str(OPENWEATHER_API))
                            )
                            data_Departure_v1 = url_Departure_v1.json()
                            temp_Departure_v1 = float(data_Departure_v1['main']['temp']) - 273.15
                            temp_min_Departure_v1 = float(data_Departure_v1['main']['temp_min']) - 273.15
                            temp_max_Departure_v1 = float(data_Departure_v1['main']['temp_max']) - 273.15
                            dict_weatherDeparture_v1 = {
                                "conditions": data_Departure_v1['weather'][0]['description'],
                                "temp": round(temp_Departure_v1, 2),
                                "temp_min": round(temp_min_Departure_v1, 2),
                                "temp_max": round(temp_max_Departure_v1, 2),
                                "wind and speed": data_Departure_v1['wind']['speed']
                            }
                            flight_obj_v1 = DBFlight(
                                id_users=pilot.id_users,
                                flight_number=DBFlight.objects.values_list('flight_number', flat=True).get(pk=unique_id),
                                pilot=DBFlight.objects.values_list('pilot', flat=True).get(pk=unique_id),
                                aircompany=DBFlight.objects.values_list('aircompany', flat=True).get(pk=unique_id),
                                airflight_route=(starting_point_address_v1, changed_arrival_point),
                                departure_point=starting_point_address_v1,
                                departure_point_address_airport=starting_point_address_v1,
                                departure_point_latitude=y_longitude_sp,
                                departure_point_longitude=x_latitude_sp,
                                arrival_point=changed_arrival_point,
                                arrival_point_address_airport=new_arrival_point_address_v1,
                                arrival_point_latitude=changed_arrival_latitude_v1,
                                arrival_point_longitude=changed_arrival_longitude_v1,
                                distance_km=distance_km_v1,
                                departure_date=datetime.now(),
                                number_of_passengers=DBFlight.objects.values_list('number_of_passengers', flat=True).get(pk=unique_id),
                                flight_condition='with correction',
                                reason_of_correction=(f'MANUAL CONTROL REQUEST, '
                                                      f'The reason indicated by the pilot: {reason}'),
                                departure_point_weather=dict_weatherDeparture_v1,
                                arrival_point_weather=dict_weatherArrival_v1
                            )
                            flight_obj_v1.save()

                        else:
                            geolocator = Nominatim(user_agent="flight")
                            starting_point_address_v2 = geolocator.reverse((x_latitude_sp, y_longitude_sp))
                            geolocator = Nominatim(user_agent="flight")
                            location_changed_arrival_point_v2 = geolocator.geocode(changed_arrival_point)
                            changed_arrival_latitude_v2 = location_changed_arrival_point_v2.latitude
                            changed_arrival_longitude_v2 = location_changed_arrival_point_v2.longitude
                            new_arrival_point_address_v2 = geolocator.reverse((changed_arrival_latitude_v2,
                                                                               changed_arrival_longitude_v2))
                            distance_km_v2 = haversine((x_latitude_sp,
                                                        y_longitude_sp),
                                                       (changed_arrival_latitude_v2,
                                                        changed_arrival_longitude_v2),
                                                       unit=Unit.KILOMETERS)
                            MCR_v2 = DBManualControlRequest(
                                id_users=pilot.id_users,
                                reason=(f'MANUAL CONTROL REQUEST, '
                                        f'The reason indicated by the pilot: {reason}'),
                                day_of_the_week=date_week,
                                confirm_request=confirm_request,
                                old_departure_point=old_departure_point,
                                old_arrival_point=old_arrival_point,
                                new_departure_point=starting_point_address_v2,
                                new_departure_latitude=x_latitude_sp,
                                new_departure_longitude=y_longitude_sp,
                                changed_arrival_point=changed_arrival_point,
                                changed_arrival_latitude=changed_arrival_latitude_v2,
                                changed_arrival_longitude=changed_arrival_longitude_v2,
                                distance_km=distance_km_v2
                            )
                            MCR_v2.save()

                            pilot_obj_v2 = DBPilots(
                                id_users=pilot.id_users,
                                username=request.user.username,
                                password=request.user.password,
                                email=DBPilots.objects.values_list('email', flat=True).get(pk=pilot_id),
                                address_registration=DBPilots.objects.values_list('address_registration', flat=True).get(pk=pilot_id),
                                company_name=DBPilots.objects.values_list('company_name', flat=True).get(pk=pilot_id),
                                flight_number=DBPilots.objects.values_list('flight_number', flat=True).get(pk=pilot_id),
                                departure_point=starting_point_address_v2,
                                arrival_point=changed_arrival_point,
                                pilot_registration_date=datetime.now()
                            )
                            pilot_obj_v2.save()

                            company_obj_v2 = DBAirCompany(
                                id_users=pilot.id_users,
                                name=DBAirCompany.objects.values_list('name', flat=True).get(pk=unique_id),
                                pilot=DBAirCompany.objects.values_list('pilot', flat=True).get(pk=unique_id),
                                company_address=DBAirCompany.objects.values_list('company_address', flat=True).get(pk=unique_id)
                            )
                            company_obj_v2.save()

                            departure_point_obj_v2 = DBDeparturePoint(
                                id_users=pilot.id_users,
                                point=starting_point_address_v2,
                                airport_address=starting_point_address_v2,
                                latitude=x_latitude_sp,
                                longitude=y_longitude_sp
                            )
                            departure_point_obj_v2.save()

                            arrival_point_obj_v2 = DBArrivalPoint(
                                id_users=pilot.id_users,
                                point=changed_arrival_point,
                                airport_address=new_arrival_point_address_v2,
                                latitude=changed_arrival_latitude_v2,
                                longitude=changed_arrival_longitude_v2
                            )
                            arrival_point_obj_v2.save()

                            weather_new_arrival_point_v2 = (changed_arrival_latitude_v2,
                                                            changed_arrival_longitude_v2)

                            url_Arrival_v2 = requests.get(
                                "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                                (float(weather_new_arrival_point_v2[0]), float(weather_new_arrival_point_v2[1]),
                                 str(OPENWEATHER_API))
                            )
                            data_Arrival_v2 = url_Arrival_v2.json()
                            temp_Arrival_v2 = float(data_Arrival_v2['main']['temp']) - 273.15
                            temp_min_Arrival_v2 = float(data_Arrival_v2['main']['temp_min']) - 273.15
                            temp_max_Arrival_v2 = float(data_Arrival_v2['main']['temp_max']) - 273.15
                            dict_weatherArrival_v2 = {
                                "conditions": data_Arrival_v2['weather'][0]['description'],
                                "temp": round(temp_Arrival_v2, 2),
                                "temp_min": round(temp_min_Arrival_v2, 2),
                                "temp_max": round(temp_max_Arrival_v2, 2),
                                "wind and speed": data_Arrival_v2['wind']['speed']
                            }
                            reason_obj_v2 = DBReason(
                                id_users=pilot.id_users,
                                first_reason='Manual Control Request',
                                second_reason=reason,
                                old_departure_point=old_departure_point,
                                old_arrival_point=old_arrival_point,
                                new_departure_point=starting_point_address_v2,
                                original_latitude=x_latitude_sp,
                                original_longitude=y_longitude_sp,
                                changed_arrival_point=changed_arrival_point,
                                corrected_latitude=changed_arrival_latitude_v2,
                                corrected_longitude=changed_arrival_longitude_v2,
                                weather_new_location=data_Arrival_v2['weather'][0]['description'],
                                description_weather=dict_weatherArrival_v2,
                            )
                            reason_obj_v2.save()

                            weather_new_departure_point_v2 = (x_latitude_sp, y_longitude_sp,)
                            url_Departure_v2 = requests.get(
                                "http://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s" %
                                (float(weather_new_departure_point_v2[0]), float(weather_new_departure_point_v2[1]),
                                 str(OPENWEATHER_API))
                            )
                            data_Departure_v2 = url_Departure_v2.json()
                            temp_Departure_v2 = float(data_Departure_v2['main']['temp']) - 273.15
                            temp_min_Departure_v2 = float(data_Departure_v2['main']['temp_min']) - 273.15
                            temp_max_Departure_v2 = float(data_Departure_v2['main']['temp_max']) - 273.15
                            dict_weatherDeparture_v2 = {
                                "conditions": data_Departure_v2['weather'][0]['description'],
                                "temp": round(temp_Departure_v2, 2),
                                "temp_min": round(temp_min_Departure_v2, 2),
                                "temp_max": round(temp_max_Departure_v2, 2),
                                "wind and speed": data_Departure_v2['wind']['speed']
                            }
                            flight_obj_v2 = DBFlight(
                                id_users=pilot.id_users,
                                flight_number=DBFlight.objects.values_list('flight_number', flat=True).get(pk=unique_id),
                                pilot=DBFlight.objects.values_list('pilot', flat=True).get(pk=unique_id),
                                aircompany=DBFlight.objects.values_list('aircompany', flat=True).get(pk=unique_id),
                                airflight_route=(starting_point_address_v2, changed_arrival_point),
                                departure_point=starting_point_address_v2,
                                departure_point_address_airport=starting_point_address_v2,
                                departure_point_latitude=x_latitude_sp,
                                departure_point_longitude=y_longitude_sp,
                                arrival_point=changed_arrival_point,
                                arrival_point_address_airport=new_arrival_point_address_v2,
                                arrival_point_latitude=changed_arrival_latitude_v2,
                                arrival_point_longitude=changed_arrival_longitude_v2,
                                distance_km=distance_km_v2,
                                departure_date=datetime.now(),
                                number_of_passengers=DBFlight.objects.values_list('number_of_passengers', flat=True).get(pk=unique_id),
                                flight_condition='with correction',
                                reason_of_correction=(f'MANUAL CONTROL REQUEST, '
                                                      f'The reason indicated by the pilot: {reason}'),
                                departure_point_weather=dict_weatherDeparture_v2,
                                arrival_point_weather=dict_weatherArrival_v2
                            )
                            flight_obj_v2.save()
                    else:
                        error_result = DBFlight.objects.filter(id_users=pilot.id_users)
                        return render(request, 'airlineflight.html', {'airlineflight_res_error': error_result})
            break
    result_second = DBFlight.objects.filter(id_users=pilot.id_users)
    return render(request, 'airlineflight.html', {'airlineflight_res_v1': result_second})


def state_of_emergency(request):
    if not request.user.is_authenticated:
        return redirect('/user/login')
    pilot_id = request.user.id
    pilot = DBPilots.objects.filter(id=pilot_id).first()
    uniq_id = int(DBFlight.objects.order_by('-id').first().id)
    if request.method == 'POST':
        reason_obj = DBReason(
            id_users=pilot.id_users,
            first_reason='Activation of the air travel mode "State of Emergency"',
            old_departure_point=DBFlight.objects.values_list('departure_point', flat=True).get(pk=uniq_id),
            old_arrival_point=DBFlight.objects.values_list('arrival_point', flat=True).get(pk=uniq_id),
            new_departure_point=DBFlight.objects.values_list('departure_point', flat=True).get(pk=uniq_id),
            original_latitude=DBFlight.objects.values_list('departure_point_latitude', flat=True).get(pk=uniq_id),
            original_longitude=DBFlight.objects.values_list('departure_point_longitude', flat=True).get(pk=uniq_id),
            changed_arrival_point=DBFlight.objects.values_list('arrival_point', flat=True).get(pk=uniq_id),
            corrected_latitude=DBFlight.objects.values_list('arrival_point_latitude', flat=True).get(pk=uniq_id),
            corrected_longitude=DBFlight.objects.values_list('arrival_point_longitude', flat=True).get(pk=uniq_id),
            weather_new_location=DBFlight.objects.values_list('arrival_point_weather', flat=True).get(pk=uniq_id),
            description_weather=DBFlight.objects.values_list('arrival_point_weather', flat=True).get(pk=uniq_id),
        )
        reason_obj.save()
        res_flight = DBFlight.objects.filter(id_users=pilot.id_users)
        for itemFlight in res_flight:
            itemFlight.flight_condition = 'with correction'
            itemFlight.reason_of_correction = 'Activation of the air travel mode "State of Emergency"'
            itemFlight.save()
    result_three = DBFlight.objects.filter(id_users=pilot.id_users)
    return render(request, 'airlineflight_blocked.html', {'airlineflight_res_v2': result_three})





















