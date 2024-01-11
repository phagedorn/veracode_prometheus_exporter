import os
import logging
import time
import re

from prometheus_client import start_http_server, Gauge
from veracode_api_py import VeracodeAPI

def get_env_variable(var_name, default, cast_type=str):
    return cast_type(os.getenv(var_name, default))

class ProfileCollector:
    def __init__(self):
        log_level = get_env_variable('LOG_LEVEL', 'INFO')
        logging.basicConfig(level=log_level)

        self.api = VeracodeAPI()
        self.custom_field_name = get_env_variable('CUSTOM_FIELD_NAME', 'cinum')
        self.team_member_count_metrics = {}

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
    
    def count_team_members(self, team_name=None):
        teams = self.api.get_teams()
        if team_name:
            team = next((team for team in teams if team["team_name"] == team_name), None)
            if team:
                members = self.api.get_user_by_search(team_id=team["team_id"])
                cleaned_team_name = re.sub(r'[^a-zA-Z0-9_]', '_', team_name)
                if cleaned_team_name not in self.team_member_count_metrics:
                    self.team_member_count_metrics[cleaned_team_name] = Gauge(f'veracode_team_member_count_{cleaned_team_name}', f'Number of members in the team {team_name}')
                self.team_member_count_metrics[cleaned_team_name].set(len(members))
                return len(members)
            return 0
        else:
            team_member_counts = {}
            for team in teams:
                team_name = team["team_name"]
                team_id = team["team_id"]
                members = self.api.get_user_by_search(team_id=team_id)
                cleaned_team_name = re.sub(r'[^a-zA-Z0-9_]', '_', team_name)
                member_count = len(members)
                team_member_counts[cleaned_team_name] = member_count
                if cleaned_team_name not in self.team_member_count_metrics:
                    self.team_member_count_metrics[cleaned_team_name] = Gauge(f'veracode_team_member_count_{cleaned_team_name}', f'Number of members in the team {team_name}')
                self.team_member_count_metrics[cleaned_team_name].set(member_count)
            return team_member_counts       

if __name__ == '__main__':
    team_name = None # Replace with the desired team name or leave it as None to count all teams
    collector = ProfileCollector()
    collector.register_metrics()
    port = get_env_variable('PORT', '8000', int)
    sleep_interval = int(os.getenv('SLEEP_INTERVAL', '300'))  # Get sleep interval from environment variable with a default of 300 seconds (5 minutes)

    start_http_server(port)

    while True:
        collector.get_unique_custom_field_count()
        collector.count_users()
        team_member_counts = collector.count_team_members(team_name)
        time.sleep(sleep_interval)
