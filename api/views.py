from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .models import Trip
from .serializers import TripSerializer
from .utils import process_trip_routes
import os
import logging
 

logger = logging.getLogger(__name__)
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "trip_id": {
                    "type": "integer",
                    "example": 123
                }
            },
            "required": ["trip_id"]
        }
    },
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "from": {"type": "string", "example": "33.4806,-112.1923"},
                    "to": {"type": "string", "example": "35.2776,-101.7114"},
                    "distance_miles": {"type": "number", "format": "float", "example": 610.12},
                    "refueling_points": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "example": "PILOT #1118"},
                                "lat": {"type": "number", "format": "float", "example": 34.0569},
                                "lon": {"type": "number", "format": "float", "example": -106.8915},
                                "price": {"type": "number", "format": "float", "example": 4.079}
                            }
                        }
                    }
                }
            },
            description="Returns route with estimated distance and list of fuel stops"
        ),
        400: OpenApiResponse(description="trip_id is required"),
        404: OpenApiResponse(description="Trip not found"),
        500: OpenApiResponse(description="Server error while processing route")
    },
    description="Computes the cheapest drivable route for a given trip ID. Includes recommended refueling points using nearby fuel station data from a CSV file."
)
@api_view(['POST'])
def process_routes(request):
    try:
        trip_id = request.data.get("trip_id")
        if not trip_id:
            return Response({"error": "trip_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        csv_path = os.path.join(os.path.dirname(__file__), '..', 'fuelprices.csv')
        csv_path = os.path.abspath(csv_path)

        route_data = process_trip_routes(trip_id, csv_path)

        return Response(route_data, status=status.HTTP_200_OK)

    except Trip.DoesNotExist:
        return Response({'error': 'Trip not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.exception("Route processing failed")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
