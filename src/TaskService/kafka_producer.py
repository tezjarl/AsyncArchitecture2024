from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
from schema_registry_client import get_schema_from_registry


def get_avro_producer(subject):
    kafka_config = {
        'bootstrap.servers': 'localhost:9092',
        'batch.size': 64000,
        'linger.ms': 300,
        'schema.registry.url': 'http://localhost:8081'
    }
    schema_id, schema_str = get_schema_from_registry(subject)
    value_schema = avro.loads(schema_str)
    producer = AvroProducer(kafka_config, default_value_schema=value_schema)
    return producer
