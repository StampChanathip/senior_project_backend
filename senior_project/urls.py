
from django.contrib import admin
from django.urls import path, include
from mapApp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', car_detail),
    path('chargeHistory', chargeHistory_detail),
    path('route', route_detail),
    path('link', link_detail),
    path('demand', demand_detail),
    path('dashboard', dashboard),
    path('passenger_check', passenger_check),
    path("stationTime", station_time),
    path("__debug__/", include("debug_toolbar.urls")),
]
