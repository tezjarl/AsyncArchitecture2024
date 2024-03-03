from confluent_kafka import Producer

kafka_config = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(**kafka_config)
