import pika
import json

class ApiCallQueuePublisher:
    def __init__(self, pika_param:pika.ConnectionParameters, api_url:str, http_method:HttpMethodType,
                 queue_name:str, is_passive:bool=True):
        self._api_url = api_url
        self._http_method = http_method
        self._connection = pika.BlockingConnection(pika_param)
        self._channel = self._connection.channel()

        try:
            self._channel.queue_declare(queue=queue_name, passive=is_passive)
        # TODO: Replace original exception later
        except pika.exceptions.ChannelClosedByBroker as ex:
            print(ex)

    def publish(self, exchange_name:str, routing_key:str, contents:dict):
        body = {
            "api_url":self._api_url,
            "http_method": self._http_method,
            "contents": contents
        } 
        self._channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=json.dumps(body))

    def close_connection(self):
        self._connection.close()