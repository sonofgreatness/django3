import logging
from django.shortcuts import render, redirect
from api.models import Trip

# Configure logger
logger = logging.getLogger(__name__)

import logging
import requests
from django.shortcuts import render, redirect
from django.urls import reverse
from api.models import Trip

logger = logging.getLogger(__name__)

def home(request):
    if request.method == 'POST':
        logger.info("Form submitted")

        start = request.POST.get('start_location')  # format: "lat,lng"
        end = request.POST.get('end_location')      # format: "lat,lng"

        if start and end:
            try:
                start_lat, start_lng = map(float, start.split(','))
                end_lat, end_lng = map(float, end.split(','))

                trip = Trip.objects.create(
                    start_location=start,
                    end_location=end,
                    start_lat=start_lat,
                    start_lng=start_lng,
                    end_lat=end_lat,
                    end_lng=end_lng
                )
                logger.info(f"Trip created successfully: {trip}")
                api_url = request.build_absolute_uri('/api/process_routes')
                response = requests.post(api_url, json={"trip_id": trip.id})

                if response.status_code == 200:
                    route_data = response.json()
                    request.session['route_data'] = route_data
                    return redirect('processed_route')
                else:
                    logger.error(f"API call failed: {response.status_code} {response.text}")

            except Exception as e:
                logger.error(f"Error saving trip or calling API: {e}")
    return render(request, 'trip_planner.html')

def processed_route(request):
      route_data = request.session.pop('route_data', None)
      logger.info(f"Processed route data: {route_data}")
      return render(request, 'home.html', {'route_data': route_data})



