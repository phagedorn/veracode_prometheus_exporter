import pytest
from unittest.mock import patch
from veracode_prometheus_exporter import ProfileCollector

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('CUSTOM_FIELD_NAME', 'cinum')
    monkeypatch.setenv('PORT', '8000')

@pytest.fixture
def setup_collector():
    with patch('veracode_prometheus_exporter.VeracodeAPI') as mock_veracode_api:
        collector = ProfileCollector()
        collector.register_metrics()
        yield mock_veracode_api, collector

@pytest.mark.parametrize(
    "test_id, apps, expected_count",
    [
        ("happy_path", [{'profile': {'custom_fields': [{'name': 'cinum', 'value': '123'}]}}, {'profile': {'custom_fields': [{'name': 'cinum', 'value': '456'}]}}], 2),
        ("edge_case_no_custom_fields", [{'profile': {}}, {'profile': {}}], 0),
        ("edge_case_no_profile", [{}, {}], 0),
        ("error_case_null_app", None, 0),
    ]
)
def test_get_unique_custom_field_count(test_id, apps, expected_count, setup_collector):
    mock_veracode_api, collector = setup_collector
    mock_veracode_api.return_value.get_apps.return_value = apps
    actual_count = collector.get_unique_custom_field_count()
    assert actual_count == expected_count

@pytest.mark.parametrize(
    "test_id, users, expected_count",
    [
        ("happy_path", ['user1', 'user2', 'user3'], 3),
        ("edge_case_no_users", [], 0),
        ("error_case_null_users", None, 0),
    ]
)
def test_count_users(test_id, users, expected_count, setup_collector):
    mock_veracode_api, collector = setup_collector
    mock_veracode_api.return_value.get_users.return_value = users
    actual_count = collector.count_users()
    assert actual_count == expected_count
