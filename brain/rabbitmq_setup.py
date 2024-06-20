import pika

def setup_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare exchanges
    channel.exchange_declare(exchange='tracking_exchange', exchange_type='direct', durable=True)
    channel.exchange_declare(exchange='config_exchange', exchange_type='direct', durable=True)
    channel.exchange_declare(exchange='status_exchange', exchange_type='direct', durable=True)

    # Declare queues
    channel.queue_declare(queue='status_queue', durable=True)
    channel.queue_declare(queue='anchor_beacon_distance_queue', durable=True)
    channel.queue_declare(queue='anchor_anchor_distance_queue', durable=True)
    channel.queue_declare(queue='anchor_aware_queue', durable=True)
    channel.queue_declare(queue='calculated_positions_queue', durable=True)
    channel.queue_declare(queue='anchor_exists_queue', durable=True)
    channel.queue_declare(queue='system_setup_queue', durable=True)
    channel.queue_declare(queue='camera_position_queue', durable=True)

    # Bind queues to exchanges
    channel.queue_bind(exchange='tracking_exchange', queue='status_queue', routing_key='anchor_alive')
    channel.queue_bind(exchange='status_exchange', queue='status_queue', routing_key='system_alive')
    channel.queue_bind(exchange='tracking_exchange', queue='anchor_beacon_distance_queue', routing_key='anchor_beacon_distance')
    channel.queue_bind(exchange='tracking_exchange', queue='anchor_anchor_distance_queue', routing_key='anchor_anchor_distance')
    channel.queue_bind(exchange='tracking_exchange', queue='anchor_aware_queue', routing_key='anchor_aware')
    channel.queue_bind(exchange='tracking_exchange', queue='calculated_positions_queue', routing_key='calculated_position')
    channel.queue_bind(exchange='config_exchange', queue='anchor_exists_queue', routing_key='anchor_exists')
    channel.queue_bind(exchange='config_exchange', queue='system_setup_queue', routing_key='system_setup')
    channel.queue_bind(exchange='tracking_exchange', queue='camera_position_queue', routing_key='camera_position')

    connection.close()

if __name__ == "__main__":
    setup_rabbitmq()
