from django.db import models

class Trip(models.Model):
   
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_lat = models.FloatField()
    start_lng = models.FloatField()
    end_lat = models.FloatField()
    end_lng = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" Trip: {self.start_location} to {self.end_location}"
