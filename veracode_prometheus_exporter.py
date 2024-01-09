import os
import logging
import time

from prometheus_client import start_http_server, Gauge
from veracode_api_py import VeracodeAPI

def get_env_variable(var_name, default, cast_type=str):
    return cast_type(os.getenv(var_name, default))

class ProfileCollector:
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

        self.api = VeracodeAPI()
        self.custom_field_name = get_env_variable('CUSTOM_FIELD_NAME', 'cinum')
        self.sleep_interval = get_env_variable('SLEEP_INTERVAL', '60', int)

    def register_metrics(self):
        self.unique_custom_field_count_metric = Gauge('veracode_unique_custom_field_count', f'Number of unique {self.custom_field_name}s')            
        self.total_app_profiles_metric = Gauge('veracode_total_app_profiles', 'Total number of app profiles')
        self.count_empty_custom_fields_metric = Gauge('veracode_total_empty_custom_fields', 'Total number of empty custom fields')
        self.total_user_count_metric = Gauge('veracode_total_user_count', 'Total number of users')

    def get_unique_custom_field_count(self):
        apps = self.api.get_apps()
        custom_fields = {field['value'] for app in apps if (profile := app.get('profile', {})) and (fields := profile.get('custom_fields')) for field in fields if field['name'] == self.custom_field_name}
        not_custom_field = sum(1 for app in apps if not app.get('profile', {}).get('custom_fields'))

        self.unique_custom_field_count_metric.set(len(custom_fields))
        self.total_app_profiles_metric.set(len(apps))
        self.count_empty_custom_fields_metric.set(not_custom_field)
        return len(custom_fields)

    def count_users(self):
        users = self.api.get_users()
        self.total_user_count_metric.set(len(users))
        return len(users)

if __name__ == '__main__':
    collector = ProfileCollector()
    collector.register_metrics()

    port = get_env_variable('PORT', '8000', int)

    start_http_server(port)

    while True:
        collector.get_unique_custom_field_count()
        collector.count_users()
        time.sleep(collector.sleep_interval)
