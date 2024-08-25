import pika
import json
import os
import time
from multiprocessing import Process, cpu_count

# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catalyst_count.settings')

import django
django.setup()  # This sets up Django and allows you to use its ORM

from base.tasks import process_csv_chunk  # Import the function for processing chunks

def establish_connection():
    """Establishes a connection to RabbitMQ with retries and heartbeat."""
    while True:
        try:
            parameters = pika.ConnectionParameters(
                'localhost',
                heartbeat=600,
                blocked_connection_timeout=300
            )
            connection = pika.BlockingConnection(parameters)
            return connection
        except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
            print(f"Connection error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def callback(ch, method, properties, body):
    """Callback function to handle messages from RabbitMQ."""
    try:
        task_data = json.loads(body)
        chunk = task_data.get('chunk')

        if chunk:
            process_csv_chunk(chunk)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error in processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_consumer():
    """Starts the RabbitMQ consumer to process tasks with reconnection logic."""
    connection = establish_connection()
    channel = connection.channel()
    channel.queue_declare(queue='file_processing', durable=True)
    channel.basic_qos(prefetch_count=1)  # Limit the number of unacknowledged messages to 1

    channel.basic_consume(
        queue='file_processing',
        on_message_callback=callback,
        auto_ack=False
    )

    print(f' [*] Waiting for messages in process: {os.getpid()}. To exit press CTRL+C')
    channel.start_consuming()

def spawn_consumers(num_consumers):
    """Spawns multiple consumer processes."""
    processes = []
    for _ in range(num_consumers):
        process = Process(target=start_consumer)
        process.start()
        processes.append(process)
    
    for process in processes:
        process.join()

if __name__ == '__main__':
    num_consumers = cpu_count()  # Adjust this number based on your CPU cores and RabbitMQ capacity
    spawn_consumers(num_consumers)
