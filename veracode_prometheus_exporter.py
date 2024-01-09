import os
import logging
import time
from prometheus_client import start_http_server, Gauge
from veracode_api_py import VeracodeAPI

class ProfileCollector:
    def __init__(self):
        # Enable debug logging for the Veracode API
        logging.basicConfig(level=logging.DEBUG)

        self.api = VeracodeAPI()
        self.custom_field_name = os.getenv('CUSTOM_FIELD_NAME', 'cinum')
        self.unique_custom_field_count_metric = Gauge('veracode_unique_custom_field_count', f'Number of unique {self.custom_field_name}s')
        self.total_app_profiles_metric = Gauge('veracode_total_app_profiles', 'Total number of app profiles')
        self.total_user_count_metric = Gauge('veracode_total_user_count', 'Total number of users')
        self.count_empty_custom_fields_metric = Gauge('veracode_total_empty_custom_fields', 'Total number of empty custom fields')

    def get_unique_custom_field_count(self):
        apps = self.api.get_apps()
        custom_fields = set()
        not_custom_field = 0

        for app in apps:
            profile = app['profile']
            if profile is not None and 'custom_fields' in profile and profile['custom_fields'] is not None:
                for field in profile['custom_fields']:
                    if field['name'] == self.custom_field_name:
                        custom_fields.add(field['value'])
            else:
                not_custom_field += 1

        self.unique_custom_field_count_metric.set(len(custom_fields))
        self.total_app_profiles_metric.set(len(apps))
        self.count_empty_custom_fields_metric.set(not_custom_field)
        return len(custom_fields)

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
        collector.get_unique_custom_field_count()
        user_count = collector.count_users()
        collector.total_user_count_metric.set(user_count)
        time.sleep(60)