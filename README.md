# veracode_prometheus_exporter
exports simple statistics from veracode api

```
# HELP veracode_unique_cinum_count Number of unique CINUMs
# TYPE veracode_unique_cinum_count gauge
veracode_unique_cinum_count 0.0
# HELP veracode_total_app_profiles Total number of app profiles
# TYPE veracode_total_app_profiles gauge
veracode_total_app_profiles 0.0
# HELP veracode_total_user_count Total number of users
# TYPE veracode_total_user_count gauge
veracode_total_user_count 0.0
# HELP veracode_total_empty_cinums Total number of empty cinum custom fields
# TYPE veracode_total_empty_cinums gauge
veracode_total_empty_cinums 0.0
```


# Start standalone script


# Start only prometheus container

$ docker run -p 8000:8000 -e VERACODE_API_KEY_ID=... -e VERACODE_API_KEY_SECRET=... veracode_prometheus_exporter:latest

# Docker Composee 

Starts following services 
- veracode prometheus exporter on port 8000
- Prometheus with on port 9090 with scrape config for veracode prometheus exporter
- Grafana on port 5000 

Start
$ VERACODE_API_KEY_ID=... VERACODE_API_KEY_SECRET=... docker-compose up 

Stop 
$ docker compose stop
