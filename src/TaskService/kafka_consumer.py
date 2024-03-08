from confluent_kafka import Consumer, KafkaError
import json
from threading import Thread
from models import db, User


def create_user_from_message(message):
    user_data = json.loads(message)
    user = User(name=user_data['name'], role=user_data['roles'])
    db.session.add(user)
    db.session.commit()


def start_consumer():
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'my-consumer-group',
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(**consumer_config)
    consumer.subscribe(['cud.auth'])

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
            create_user_from_message(message.value().decode('utf-8'))
    finally:
        consumer.close()


def start_consumer_thread():
    consumer_thread = Thread(target=start_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
