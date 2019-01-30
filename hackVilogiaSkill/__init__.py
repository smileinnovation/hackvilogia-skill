# -*- coding: utf-8 -*-
import logging
from hackVilogiaSkill.message import Message
from hackVilogiaSkill.clients import ClientMock

SKILL_MESSAGES = {
    'fr': {
        'hello': [
            "Bonjour, Comment puis-je vous aider ?"
        ],
        'imfine': [
            "Je vais bien merci. Comment puis-je vous aider ?",
            "Tout va bien pour moi. Comment puis-je vous aider ? "
        ],
        'thanks': [
            "Mais de rien. A votre service",
            "Je vous en pris."
        ],
        'bye': [
            "au revoir, à bientôt",
            "au revoir, à votre service"
        ],
        'unknownSmallTalk': [
            "Je ne suis pas sur de vous avoir compris... "
        ],
        'confirmClientPhoneNumber': [
            'pouvez-vous me confirmer que votre numéro de téléphone se termine par {} ?'
        ],
        'transfer_to_support': [
            'Très bien. Nous transférons votre demande à la bonne personne'
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
            'smilehack:repondreOuiOuNon': self.yes_no,
            'smilehack:numeroLocataire': self.numero_locataire,
            'smilehack:pasNumeroClient': self.pas_numero_locataire,
            'smilehack:InfoLoyerCharge': self.info_loyer_charge,
            'smilehack:problemePlomberieSanitaire': self.plomberie
        }

    def reduce_number(self, slot):
        if slot:
            # If slot is a list of Number, we concatenate them to build a full number
            # Ex: My number is 34 45 56 => 344556
            if isinstance(slot, list):
                return ''.join(list(map(lambda s: str(abs(int(s.value))), slot)))
            else:
                return str(int(slot.value))

    def how_are_you(self, intent_message, dialog):
        self._logger.info("=> intent how_are_you")
        dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('imfine'))

    def small_talk(self, intent_message, dialog):
        self._logger.info("=> intent small_talk")

        if intent_message.slots['hello']:
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('hello'))

        if intent_message.slots['bye']:
            dialog.end_session(session_id=intent_message.session_id, text=self._message.get('bye'))

        if intent_message.slots['thanks']:
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('thanks'))

    def unmanaged_event(self, intent_message, dialog):
        self._logger.info("=> intent unknown")
        dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('unknownSmallTalk'))

    def yes_no(self, intent_message, dialog):
        self._logger.info("=> intent yes_no")
        self._logger.info("Custom data: {}".format(intent_message.custom_data))

        custom_data = intent_message.custom_data
        if custom_data is not None:
            if custom_data == 'CONFIRM_CLIENT_PHONE_NUMBER':
                dialog.end_session(session_id=intent_message.session_id,
                                   text=self._message.get('transfer_to_support'))

        dialog.end_session(session_id=intent_message.session_id, text=self._message.get('bye'))

    def numero_locataire(self, intent_message, dialog):
        self._logger.info("=> intent numero_locataire")
        number = self.reduce_number(intent_message.slots['locataire'])
        print(number)
        client = ClientMock.client_by_id(number)
        if client is not None:
            dialog.end_session(session_id=intent_message.session_id, text='Bonjour {0} {1}'.format(client['firstName'], client['lastName']))
            dialog.start_session_action(site_id='default', text=self._message.get('confirmClientPhoneNumber').format(client['phone'][-2:]),
                                        custom_data='CONFIRM_CLIENT_PHONE_NUMBER',
                                        intent_filter=['smilehack:repondreOuiOuNon'],
                                        can_be_enqueued=True
                                        )
        else:
            dialog.end_session(session_id=intent_message.session_id, text='Désolé, mais je ne trouve de client avec le numéro {}'.format(number))
            #TODO ... what must be done here ?

    def pas_numero_locataire(self, intent_message, dialog):
        dialog.end_session(session_id=intent_message.session_id, text='Ok nous allons faire sans numéro client...')

    def info_loyer_charge(self, intent_message, dialog):
        print("++++")
        print(intent_message.input)
        if intent_message.slots is not None:
            print("----")
        for slot in intent_message.slots:
            print('{0} : {1} / {2} / {3}'.format(slot, intent_message.slots[slot].kind, intent_message.slots[slot].value, intent_message.slots[slot].rawValue))
        dialog.end_session(session_id=intent_message.session_id, text='Pas de bras pas de chocolat')

    def plomberie(self, intent_message, dialog):
        print("++++")
        print(intent_message.input)
        if intent_message.slots is not None:
            print("----")
        for slot in intent_message.slots:
            print('{0} : {1} / {2} / {3}'.format(slot, intent_message.slots[slot].kind, intent_message.slots[slot].value, intent_message.slots[slot].rawValue))
        dialog.end_session(session_id=intent_message.session_id, text="Ok j'appelle le plombier")


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

