import json

import pika

from app.settings import settings


def send_message(queue_name, data):
    parameters = pika.ConnectionParameters(
        host=settings.broker_path.split(':')[0],
        port=settings.broker_path,
        virtual_host=settings.rabbitmq_vhost,
        credentials=pika.credentials.PlainCredentials(
            username=settings.rabbitmq_user,
            password=settings.rabbitmq_password
        )
    )
    connection = pika.BlockingConnection(parameters=parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=json.dumps(data).encode(),
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        ),
    )
    print(" [x] Sent message")
