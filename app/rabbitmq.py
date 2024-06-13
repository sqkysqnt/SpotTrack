import pika

def setup_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='test')
    return connection, channel

def publish_message(channel, message):
    channel.basic_publish(exchange='', routing_key='test', body=message)
    print(f" [x] Sent {message}")
