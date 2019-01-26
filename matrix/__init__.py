## Set Initial Variables ##
import os # Miscellaneous operating system interface

import time # Time access and conversions
from random import randint # Random numbers
import sys # System-specific parameters and functions

import zmq # Asynchronous messaging framework
from matrix_io.proto.malos.v1 import driver_pb2 # MATRIX Protocol Buffer driver library
from matrix_io.proto.malos.v1 import io_pb2 # MATRIX Protocol Buffer sensor library
from multiprocessing import Process, Manager, Value # Allow for multiple processes at once
from zmq.eventloop import ioloop, zmqstream# Asynchronous events through ZMQ

matrix_ip = '127.0.0.1' # Local device ip
everloop_port = 20021 # Driver Base port
led_count = 0 # Amount of LEDs on MATRIX device
# Handy function for connecting to the Error port
from matrix.utils import register_error_callback

import paho.mqtt.client as mqtt
import json


class EverLoop:
    def __init__(self):
        print("")

class LedControl:

    _SUB_ON_HOTWORD = 'hermes/hotword/default/detected'
    _SUB_ON_SAY = 'hermes/tts/say'
    _SUB_ON_THINK = 'hermes/asr/textCaptured'
    _SUB_ON_LISTENING = 'hermes/asr/startListening'
    _SUB_ON_HOTWORD_TOGGLE_ON = 'hermes/hotword/toggleOn'
    _SUB_ON_ERROR = 'hermes/nlu/intentNotRecognized'
    _SUB_ON_SUCCESS = 'hermes/nlu/intentParsed'
    _SUB_ON_PLAY_FINISHED = 'hermes/audioServer/default/playFinished'
    _SUB_ON_TTS_FINISHED = 'hermes/tts/sayFinished'

    '''
    _SUB_ON_LEDS_TOGGLE = 'hermes/leds/toggle'
    _SUB_ON_LEDS_TOGGLE_ON = 'hermes/leds/toggleOn'
    _SUB_ON_LEDS_TOGGLE_OFF = 'hermes/leds/toggleOff'
    _SUB_UPDATING = 'hermes/leds/systemUpdate'
    _SUB_ON_CALL = 'hermes/leds/onCall'
    _SUB_SETUP_MODE = 'hermes/leds/setupMode'
    _SUB_CON_ERROR = 'hermes/leds/connectionError'
    _SUB_ON_MESSAGE = 'hermes/leds/onMessage'
    _SUB_ON_DND = 'hermes/leds/doNotDisturb'
    '''

    def __init__(self, mqtt_host, mqtt_port, logger):
        self._logger = logger
        self._logger.info('Initializing')
        self._me = 'default'
        self.mqtt_client = None
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_client = self.connect()

    def on_connect(self, client, userdata, flags, rc):
        self._logger.info("Connected with result code {0}".format(rc))
        client.subscribe([
            (self._SUB_ON_HOTWORD, 0),
            (self._SUB_ON_SAY, 0),
            (self._SUB_ON_THINK, 0),
            (self._SUB_ON_LISTENING, 0),
            (self._SUB_ON_HOTWORD_TOGGLE_ON, 0),
            (self._SUB_ON_ERROR, 0),
            (self._SUB_ON_SUCCESS, 0),
            (self._SUB_ON_PLAY_FINISHED, 0),
            (self._SUB_ON_TTS_FINISHED, 0),
        ])

    def event_to_func(self, event):
        return {
            self._SUB_ON_HOTWORD:self.wakeup_event,
            self._SUB_ON_SAY:self.tts_start_event,
            self._SUB_ON_THINK: self.think_event,
            self._SUB_ON_LISTENING: self.listening_event,
            self._SUB_ON_HOTWORD_TOGGLE_ON: self.backtosleep_event,
            self._SUB_ON_ERROR: self.intent_error_event,
            self._SUB_ON_SUCCESS: self.intent_success_event,
            self._SUB_ON_PLAY_FINISHED: self.play_finished_event,
            self._SUB_ON_TTS_FINISHED: self.tts_finished_event
        }.get(event, self.unmanaged_event)

    def wakeup_event(self, payload):
        self._logger.info("=> wakeup: {}".format(payload))

    def backtosleep_event(self, payload):
        self._logger.info("=> backtosleep: {}".format(payload))

    def listening_event(self, payload):
        self._logger.info("=> listening: {}".format(payload))

    def think_event(self, payload):
        self._logger.info("=> thinking: {}".format(payload))

    def tts_start_event(self, payload):
        self._logger.info("=> tts start: {}".format(payload))

    def tts_finished_event(self, payload):
        self._logger.info("=> tts finished: {}".format(payload))

    def intent_error_event(self, payload):
        self._logger.info("=> intent error: {}".format(payload))

    def intent_success_event(self, payload):
        self._logger.info("=> intent success: {}".format(payload))

    def play_finished_event(self, payload):
        self._logger.info("=> play finished: {}".format(payload))



    def unmanaged_event(self, payload):
        self._logger.info("=> unmanaged: {}".format(payload))

    def on_message(self, client, userdata, message):
        if hasattr(message, 'payload') and message.payload:
            try:
                payload = json.loads(message.payload.decode('utf-8'))
                self._logger.info("LedControl has received {}".format(message.topic))
                self.event_to_func(message.topic)(payload)
            except Exception as e:
                print(e)

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
