import json
from confluent_kafka.avro import AvroConsumer
from event_processors import process_task_created, process_task_assigned, process_task_completed, process_user_created
from threading import Thread


def get_avro_consumer(topic):
    consumer_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'task-created-consumer',
        'auto.offset.reset': 'earliest',
        'schema.registry.url': 'http://localhost:8081'
    }
    consumer = AvroConsumer(consumer_config)
    consumer.subscribe([topic])
    return consumer


def task_created_consumer():
    consumer = get_avro_consumer('task.created')

    try:
        while True:
            message = consumer.poll(1.0)

            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')

            message_data = message.value()
            process_task_created(message_data)
    finally:
        consumer.close()


def task_assigned_consumer():
    consumer = get_avro_consumer('task.assigned')

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')
            process_task_assigned(message.value())
    finally:
        consumer.close()


def task_completed_consumer():
    consumer = get_avro_consumer('task.completed')

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')
                continue
            message_data = message.value()
            process_task_completed(message_data)
    finally:
        consumer.close()


def user_created_consumer():
    consumer = get_avro_consumer('auth.user.created')

    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                print(f'Consumer error: {message.error()}')
                continue
            message_data = message.value()
            process_user_created(message_data)
    finally:
        consumer.close()


def start_task_created_consumer():
    consumer_thread = Thread(target=task_created_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()


def start_task_assigned_consumer():
    consumer_thread = Thread(target=task_assigned_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()


def start_task_completed_consumer():
    consumer_thread = Thread(target=task_completed_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()


def start_user_created_consumer():
    consumer_thread = Thread(target=user_created_consumer)
    consumer_thread.daemon = True
    consumer_thread.start()
