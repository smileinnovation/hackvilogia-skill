# -*- coding: utf-8 -*-
import traceback
import logging
import paho.mqtt.client as mqtt
import json
from hackVilogiaSkill.intentMessage import IntentMessage


class Dialog:
    def __init__(self, mqtt_client):
        self._mqtt_client = mqtt_client

    def start_session_action(self, site_id = None, text = None, custom_data = None, can_be_enqueued = False, intent_filter = None):
        payload = {
            'init':{
                'type':'action',
                'canBeEnqueued':can_be_enqueued,
            }
        }
        if site_id is not None: payload['siteId'] = site_id
        if text is not None: payload['init']['text'] = text
        if custom_data is not None: payload['customData'] = custom_data
        if intent_filter is not None: payload['init']['intentFilter'] = intent_filter
        self._mqtt_client.publish('hermes/dialogueManager/startSession', json.dumps(payload))

    def continue_session(self, session_id, text, custom_data = None, intent_filter = None):
        payload = {
            'sessionId': session_id,
            'text': text
        }
        if intent_filter is not None: payload['intentFilter'] = intent_filter
        if custom_data is not None: payload['customData'] = custom_data
        self._mqtt_client.publish('hermes/dialogueManager/continueSession', json.dumps(payload))

    def end_session(self, session_id, text = None):
        payload = {
            'sessionId': session_id
        }
        if text is not None: payload['text'] = text
        self._mqtt_client.publish('hermes/dialogueManager/endSession', json.dumps(payload))


class EventBus:

    _SUB_INTENT = 'hermes/intent/{}' # subscription pattern for any intent to subscribe to
    _SUB_ON_ERROR = 'hermes/nlu/intentNotRecognized' # subscription topic for not recognized intent

    def __init__(self, mqtt_host, mqtt_port, state_machine):
        self._logger = logging.getLogger('HackVilogiaSkill')
        self._logger.info('Initializing')
        self._me = 'default'
        self.mqtt_client = None
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_client = self.connect()
        self.state_machine = state_machine
        self.dialog = Dialog(self.mqtt_client)
        self.intents_with_handlers = self.state_machine.intents_with_handlers()
        self.fallback_handler = self.state_machine.fallback_handler()

    def on_connect(self, client, userdata, flags, rc):
        self._logger.info("Connected with result code {0}".format(rc))
        subscriptions = list(map(lambda i: (self._SUB_INTENT.format(i), 0), self.intents_with_handlers.keys()))
        subscriptions.append((self._SUB_ON_ERROR, 0))
        client.subscribe(subscriptions)

    def intent_to_func(self, intent):
        if self.intents_with_handlers is not None and intent in self.intents_with_handlers:
            return self.intents_with_handlers[intent]
        else:
            return self.fallback_handler

    def on_message(self, client, userdata, message):
        if hasattr(message, 'payload') and message.payload:
            try:
                payload = json.loads(message.payload.decode('utf-8'))
                if message.topic == self._SUB_ON_ERROR:
                    # TODO manage unrecognized intent!
                    self._logger.info("HackVilogiaSkill has received an event for unrecognized intent!")
                else:
                    intent_message = IntentMessage.from_payload(payload)
                    self.intent_to_func(intent_message.intent.intentName)(intent_message, self.dialog)

            except Exception:
                print(traceback.format_exc())

    def connect(self):
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = self.on_connect
        mqtt_client.on_message = self.on_message
        return mqtt_client

    def start(self):
        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, 60)
        self.mqtt_client.loop_start()

    def stop(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
