import pika
import json
import requests
from abc import ABCMeta, abstractmethod

class BaseApiCallQueueSubscriber(metaclass=ABCMeta):
    def __init__(self, pika_param:pika.ConnectionParameters, queue_name:str, 
                 exchange_name:str, routing_key:str, is_auto_delete:bool=False, prefetch_count:int=1):
        self._connection = pika.BlockingConnection(pika_param)
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue=queue_name, auto_delete=is_auto_delete)
        self._channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key)
        self._channel.basic_qos(prefetch_count=prefetch_count)
        self._channel.basic_consume(queue_name, on_message_callback=self._callback)

    @abstractmethod
    def core(self, api_url:str, contents:dict, response:requests.Session):
        pass

    def _callback(self, channel, method, properties, body):
        message = json.loads(body)
        api_url = message["api_url"]
        http_method = message["http_method"]
        contents = message["contents"]

        if http_method == "get":
            response = requests.get(api_url)
        else:
            response = requests.post(api_url, data=contents)

        self.core(api_url, contents, response)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self._channel.start_consuming()

class SampleApiCallQueueSubscriber(BaseApiCallQueueSubscriber):
    def core(self, api_url:str, contents:dict, response:requests.Session):
        print(api_url, contents, response)