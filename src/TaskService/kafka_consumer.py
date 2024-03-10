from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
import json
from threading import Thread
from models import db, User
from app import app


def create_user_from_message(message):
    with app.app_context():
        user_data = message
        user = User(name=user_data['name'], public_id=user_data['public_id'])
        db.session.add(user)
        db.session.commit()


def start_consumer():
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'my-consumer-group',
        'auto.offset.reset': 'earliest',
        'schema.registry.url': 'http://localhost:8081'
    }

    consumer = AvroConsumer(consumer_config)
    consumer.subscribe(['auth.user.created'])

    try:
        while True:
            message = consumer.poll(timeout=1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(message.error())
                    break
            create_user_from_message(message.value())
    finally:
        consumer.close()


def start_consumer_thread():
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
