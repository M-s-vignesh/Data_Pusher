from celery import shared_task
import requests
from django.utils.timezone import now
from api.models import Log, Destination

@shared_task
def send_data_to_destinations(account_id, event_id, data):
    """Send incoming data to all destinations asynchronously."""
    
    destinations = Destination.objects.filter(account_id=account_id)
    
    for destination in destinations:
        headers = destination.headers
        headers["CL-X-EVENT-ID"] = event_id  
        
        try:
            if destination.http_method == "GET":
                response = requests.get(destination.url, params=data, headers=headers)
            else:  
                response = requests.request(destination.http_method, destination.url, json=data, headers=headers)
            
            status = "success" if response.status_code in [200, 201, 202] else "failed"

        except requests.RequestException:
            status = "failed"

        Log.objects.create(
            account_id=account_id,
            destination=destination,
            event_id=event_id,
            received_data=data,
            processed_timestamp=now(),
            status=status
        )
