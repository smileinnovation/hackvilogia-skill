# -*- coding: utf-8 -*-
import logging
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


class HackVilogiaSkill:
    def __init__(self):
        self._logger = logging.getLogger('HackVilogiaSkill')
        self._message = Message(SKILL_MESSAGES)

    def fallback_handler(self):
        return self.unmanaged_event

    def intents_with_handlers(self):
        return {
            'smilehack:smallTalk': self.small_talk,
            'smilehack:sayHowAreYou': self.how_are_you,
            'smilehack:repondreOuiOuNon': self.yes_no
        }

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

