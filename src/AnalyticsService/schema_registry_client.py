import requests


def get_schema_from_registry(subject):
    response = requests.get(f'http://localhost:8081/subjects/{subject}/versions/latest')
    response.raise_for_status()
    response_body = response.json()
    schema_id = response_body['id']
    schema_string = response_body['schema']
    return schema_id, schema_string
