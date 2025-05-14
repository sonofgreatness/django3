from rest_framework import serializers
from .models import Trip

from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = [           
    'start_location',
    'end_location', 
    'start_lat',
    'start_lng', 
    'end_lat',
    'end_lng',
  
 ]
