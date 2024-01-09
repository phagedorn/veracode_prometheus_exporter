from unittest.mock import MagicMock
from veracode_prometheus_exporter import ProfileCollector

class TestProfileCollector:
    def setup_method(self):
        self.collector = ProfileCollector()
        self.collector.api = MagicMock()

    def test_get_unique_cinum_count(self):
        # Mock the get_apps method to return a predefined list of applications
        self.collector.api.get_apps.return_value = [
            {
                'profile': {
                    'custom_fields': [
                        {'name': 'cinum', 'value': '123'},
                        {'name': 'cinum', 'value': '456'},
                        {'name': 'other_field', 'value': '789'}
                    ]
                }
            },
            {
                'profile': {
                    'custom_fields': [
                        {'name': 'cinum', 'value': '123'},
                        {'name': 'other_field', 'value': '789'}
                    ]
                }
            },
            {
                'profile': {
                    'custom_fields': None
                }
            }
        ]

        # Call the method
        unique_cinum_count = self.collector.get_unique_cinum_count()

        # Assert the expected values
        assert unique_cinum_count == 2
        assert self.collector.unique_cinum_count_metric._value.get() == 2
        assert self.collector.total_app_profiles_metric._value.get() == 3
        assert self.collector.count_empty_cinum_custom_fields_metric._value.get() == 1