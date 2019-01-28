# -*- coding: utf-8 -*-
import sys
import logging
import paho.mqtt.client as mqtt
import json
from hackVilogiaSkill.intentMessage import IntentMessage
from hackVilogiaSkill.message import Message

SKILL_MESSAGES = {
    'fr': {
        'hello': [
            "Salut biloute",
            "Hey copain"
        ],
        'youAreWelcome': [
            "Mais de rien.",
            "Je vous en pris."
        ],
        'bye': [
            "à bientôt"
        ],
        'unknownSmallTalk': [
            "Je ne suis pas sur de vous avoir compris... "
        ]
    }
}

class StateMachine:
    def __init__(self):
        self._logger = logging.getLogger('HackVilogiaSkill')
        self._message = Message(SKILL_MESSAGES)

    def yes_no(self, intent_message, dialog):
        self._logger.info("=> intent yes_no")
        self._logger.info("Custom data: {}".format(intent_message.custom_data))
        dialog.end_session(session_id=intent_message.session_id, text=self._message.get('bye'))

    def how_are_you(self, intent_message, dialog):
        self._logger.info("=> intent how_are_you")

    def small_talk(self, intent_message, dialog):
        self._logger.info("=> intent small_talk")

        if intent_message.slots['hello']:
            #dialog.end_session(session_id=intent_message.session_id, text=self._message.get('hello'))
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('hello'), intent_filter=['smilehack:repondreOuiOuNon'], custom_data="TESTCUSTOM")

    def unmanaged_event(self, intent_message, dialog):
        self._logger.info("=> intent unknown")


'''

https://docs.snips.ai/reference/dialogue

hermes.publish_start_session_action(site_id, session_init_text, session_init_intent_filter, session_init_can_be_enqueued, custom_data)
hermes.publish_continue_session(session_id, text, intent_filter)
hermes.publish_end_session(session_id, text)
	
	hermes/dialogueManager/startSession
	{
        (opts)'siteId: site_id,
	    (opts)'customData': custom_data,
		'init': {
			'type': 'notification',
			'text': text
		}
	}

    hermes/dialogueManager/startSession
    {
	    (opts)'siteId: site_id,
	    (opts)'customData': custom_data,
		'init': {
			'type': 'action',
			'canBeEnqueued': session_init_can_be_enqueued,
			(opts)'intentFilter': 'session_init_intent_filter,
			(opts)'sendIntentNotRecognized': false,
			(opts)'text': session_init_text
		}
	}

    hermes/dialogueManager/continueSession
    {
        sessionId:sessionId,
        text:text,
        (opts)intentFilter:intentfilter,
        (opts)customData:custom
        (opts)sendIntentNotRecognized:false
    }
    
    hermes/dialogueManager/endSession
    {
        sessionId:sessionId
        (opts)text:text
    }

'''


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


class HackVilogiaSkill:

    _SUB_INTENT = 'hermes/intent/{}'
    _SUB_ON_ERROR = 'hermes/nlu/intentNotRecognized'
    _ALL_INTENTS = ['smilehack:smallTalk', 'smilehack:sayHowAreYou', 'smilehack:repondreOuiOuNon']

    def __init__(self, mqtt_host, mqtt_port):
        self._logger = logging.getLogger('HackVilogiaSkill')
        self._logger.info('Initializing')
        self._me = 'default'
        self.mqtt_client = None
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_client = self.connect()
        self.stateMachine = StateMachine()
        self.dialog = Dialog(self.mqtt_client)

    def on_connect(self, client, userdata, flags, rc):
        self._logger.info("Connected with result code {0}".format(rc))

        subscriptions = list(map(lambda i: (self._SUB_INTENT.format(i), 0), self._ALL_INTENTS))
        subscriptions.append((self._SUB_ON_ERROR, 0))
        client.subscribe(subscriptions)

    def intent_to_func(self, intent):
        return {
            'smilehack:smallTalk':self.stateMachine.small_talk,
            'smilehack:sayHowAreYou':self.stateMachine.how_are_you,
            'smilehack:repondreOuiOuNon': self.stateMachine.yes_no,
        }.get(intent, self.stateMachine.unmanaged_event)

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

            except Exception as e:
                print(e)
                type, value, traceback = sys.exc_info()
                print('Error opening %s: %s' % (value.filename, value.strerror))

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



'''
        self._logger.info(intent_message.session_id)
        self._logger.info(intent_message.custom_data)
        self._logger.info(intent_message.site_id)
        self._logger.info(intent_message.input)
        self._logger.info(intent_message.intent)
        self._logger.info(intent_message.intent.probability)
        self._logger.info(intent_message.slots['slotName'].entity)
        self._logger.info(intent_message.slots['slotName'].slotName)
        self._logger.info(intent_message.slots['slotName'].kind)
        self._logger.info(intent_message.slots['slotName'].value)
'''