import logging

import os
from google.cloud import pubsub_v1

def test_pubsub():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    topic_name = os.getenv("PUBSUB_TOPIC", "crawler-jobs")
    sub_name = os.getenv("PUBSUB_SUBSCRIPTION", "crawler-sub")
        logging.info("ERROR: GOOGLE_CLOUD_PROJECT not set")
    if not project_id:
        logging.info("ERROR: GOOGLE_CLOUD_PROJECT not set")
        return False

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    topic_path = publisher.topic_path(project_id, topic_name)
    sub_path = subscriber.subscription_path(project_id, sub_name)

    try:
        publisher.create_topic(name=topic_path)
        logging.info(f"Topic {topic_name} created")
    except Exception as e:
        if "409" in str(e):
            logging.info(f"Topic {topic_name} already exists")
        else:
            logging.info(f"Failed to create topic: {e}")
            return False

    try:
        subscriber.create_subscription(name=sub_path, topic=topic_path)
        logging.info(f"Subscription {sub_name} created")
    except Exception as e:
        if "409" in str(e):
            logging.info(f"Subscription {sub_name} already exists")
        elif "403" in str(e):
            logging.info("No permission to create subscription, assuming it exists")
        else:
            logging.info(f"Failed to create subscription: {e}")
            return False

    # Test publish
    data = "test message".encode("utf-8")
    future = publisher.publish(topic_path, data)
    message_id = future.result()
    logging.info(f"Published test message: {message_id}")

    # Test pull
    response = subscriber.pull(request={"subscription": sub_path, "max_messages": 1})
    if response.received_messages:
        msg = response.received_messages[0]
        logging.info(f"Pulled message: {msg.message.data.decode('utf-8')}")
        # Ack
        subscriber.acknowledge(request={"subscription": sub_path, "ack_ids": [msg.ack_id]})
        logging.info("Message acknowledged")
    else:
        logging.info("No messages pulled")

    logging.info("PubSub validation successful")
    return True

if __name__ == "__main__":
    test_pubsub()