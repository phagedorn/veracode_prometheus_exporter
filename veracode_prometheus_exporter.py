import os
from prometheus_client import start_http_server, Gauge
from veracode_api_py import VeracodeAPI

class ProfileCollector:
    def __init__(self):
        self.api = VeracodeAPI()
        self.unique_cinum_count_metric = Gauge('veracode_unique_cinum_count', 'Number of unique CINUMs')
        self.total_app_profiles_metric = Gauge('veracode_total_app_profiles', 'Total number of app profiles')
        self.total_user_count_metric = Gauge('veracode_total_user_count', 'Total number of users')
        self.findings_per_cinum_metric = Gauge('veracode_findings_per_cinum', 'Number of findings per CINUM')

    def get_unique_cinum_count(self):
        apps = self.api.get_apps()
        cinums = set()

        for app in apps:
            custom_fields = app['profile']['custom_fields']
            if custom_fields is not None:
                for field in custom_fields:
                    if field['name'] == 'cinum':
                        cinums.add(field['value'])
        self.unique_cinum_count_metric.set(len(cinums))
        self.total_app_profiles_metric.set(len(apps))
        return len(cinums)

    def count_users(self):
        users = self.api.get_users()
        return len(users)

    def get_findings_per_cinum(self):
        apps = self.api.get_apps()
        findings_per_cinum = {}

        for app in apps:
            cinum = None
            custom_fields = app['profile']['custom_fields']
            if custom_fields is not None:
                for field in custom_fields:
                    if field['name'] == 'cinum':
                        cinum = field['value']
                        break

            if cinum is not None:
                findings = self.api.get_findings(app['guid'])
                findings_count = len(findings)
                if cinum not in findings_per_cinum:
                    findings_per_cinum[cinum] = 0
                findings_per_cinum[cinum] += findings_count

        return findings_per_cinum

    def export_findings_per_cinum_metric(self):
        findings_per_cinum = self.get_findings_per_cinum()

        for cinum, count in findings_per_cinum.items():
            self.findings_per_cinum_metric.labels(cinum=cinum).set(count)

# Usage example
if __name__ == '__main__':
    collector = ProfileCollector()

    # Get listen address and port from environment variables
    listen_address = os.getenv('LISTEN_ADDRESS', 'localhost')
    port = int(os.getenv('PORT', '8000'))

    start_http_server(port, addr=listen_address)
    while True:
        collector.get_unique_cinum_count()
        user_count = collector.count_users()
        collector.total_user_count_metric.set(user_count)
        collector.export_findings_per_cinum_metric()