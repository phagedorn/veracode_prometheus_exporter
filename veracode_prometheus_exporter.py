import os
import logging
import time
from prometheus_client import start_http_server, Gauge
from veracode_api_py import VeracodeAPI

class ProfileCollector:
    def __init__(self):
        # Enable debug logging for the Veracode API
        logging.basicConfig(level=logging.INFO)

        self.api = VeracodeAPI()
        self.unique_cinum_count_metric = Gauge('veracode_unique_cinum_count', 'Number of unique CINUMs')
        self.total_app_profiles_metric = Gauge('veracode_total_app_profiles', 'Total number of app profiles')
        self.total_user_count_metric = Gauge('veracode_total_user_count', 'Total number of users')
        self.count_empty_cinum_custom_fields_metric = Gauge('veracode_total_empty_cinums', 'Total number of empty cinum custom fields')    
    def get_unique_cinum_count(self):
        apps = self.api.get_apps()
        cinums = set()
        not_cinum = 0

        for app in apps:
            custom_fields = app['profile']['custom_fields']
            if custom_fields is not None:
                for field in custom_fields:
                    if field['name'] == 'cinum':
                        cinums.add(field['value'])
            else:
                not_cinum += 1
        self.unique_cinum_count_metric.set(len(cinums))
        self.total_app_profiles_metric.set(len(apps))
        self.count_empty_cinum_custom_fields_metric.set(not_cinum)
        return len(cinums)

    def count_users(self):
        users = self.api.get_users()
        return len(users)

# Usage example
if __name__ == '__main__':
    collector = ProfileCollector()

    # Get listen address and port from environment variables
    port = int(os.getenv('PORT', '8000'))

    start_http_server(port)
    while True:
        collector.get_unique_cinum_count()
        user_count = collector.count_users()
        collector.total_user_count_metric.set(user_count)
        time.sleep(60)  