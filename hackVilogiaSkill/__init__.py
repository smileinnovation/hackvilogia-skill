# -*- coding: utf-8 -*-
import logging
from hackVilogiaSkill.message import Message
from hackVilogiaSkill.clients import ClientMock
from hackVilogiaSkill.incident import Incident, IncidentType, EmergencyLevel

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
        'ask_for_numero_client': [
            'pouvez-vous me communiquer votre numéro de locataire ?'
        ],
        'client_number_mandatory': [
            'Désolé, mais nous ne pouvons pas traiter votre demande sans numéro de locataire'
        ],
        'confirmClientPhoneNumber': [
            'pouvez-vous me confirmer que votre numéro de téléphone se termine par {} ?'
        ],
        'transfer_to_tech_support': [
            'Très bien. Nous transférons votre demande au service technique concerné'
        ],
        'transfer_to_sale_support': [
            'Très bien. Nous transférons votre demande au service commercial concerné'
        ]
    }
}


class HackVilogiaSkill:
    def __init__(self):
        self._logger = logging.getLogger('HackVilogiaSkill')
        self._message = Message(SKILL_MESSAGES)
        self._current_incident = None

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

    def set_new_incident(self, incidentType):
        self._current_incident = Incident(incidentType)

    def clear_incident(self):
        self._current_incident = None

    def send_incident(self):
        print(self._current_incident.to_JSON())

    def how_are_you(self, intent_message, dialog):
        self._logger.info("=> intent how_are_you")
        dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('imfine'))

    def small_talk(self, intent_message, dialog):
        self._logger.info("=> intent small_talk")

        if intent_message.slots['hello']:
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('hello'))

        if intent_message.slots['bye']:
            dialog.end_session(session_id=intent_message.session_id, text=self._message.get('bye'))
            self.clear_incident()

        if intent_message.slots['thanks']:
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('thanks'))

    def unmanaged_event(self, intent_message, dialog):
        self._logger.info("=> intent unknown")
        dialog.end_session(session_id=intent_message.session_id, text=self._message.get('unknownSmallTalk'))
        self.clear_incident()

    def yes_no(self, intent_message, dialog):
        self._logger.info("=> intent yes_no")
        self._logger.info("Custom data: {}".format(intent_message.custom_data))

        custom_data = intent_message.custom_data
        if custom_data is not None:
            if custom_data == 'CONFIRM_CLIENT_PHONE_NUMBER':
                message = self._message.get('transfer_to_tech_support') if self._current_incident.incidentType == IncidentType.Technical else self._message.get('transfer_to_sale_support')
                dialog.end_session(session_id=intent_message.session_id, text=message)
                self.send_incident()
                self.clear_incident()

    def numero_locataire(self, intent_message, dialog):
        self._logger.info("=> intent numero_locataire")
        number = self.reduce_number(intent_message.slots['locataire'])
        print(number)
        client = ClientMock.client_by_id(number)
        if client is not None:
            dialog.end_session(session_id=intent_message.session_id, text='Bonjour {0} {1}'.format(client['firstName'], client['lastName']))
            dialog.start_session_action(site_id='default',
                                        text=self._message.get('confirmClientPhoneNumber').format(client['phone'][-2:]),
                                        custom_data='CONFIRM_CLIENT_PHONE_NUMBER',
                                        intent_filter=['smilehack:repondreOuiOuNon', 'smilehack:smallTalk'],
                                        can_be_enqueued=True
                                        )
        else:
            dialog.end_session(session_id=intent_message.session_id, text='Désolé, mais je ne trouve de client avec le numéro {}'.format(number))
            dialog.start_session_action(site_id='default',
                                        text=self._message.get('ask_for_numero_client'),
                                        custom_data='ASK_FOR_CLIENT_NUMBER',
                                        intent_filter=['smilehack:numeroLocataire', 'smilehack:smallTalk'],
                                        can_be_enqueued=True
                                        )

    def pas_numero_locataire(self, intent_message, dialog):
        # Custom data to be used to know if the client number is mandatory or not
        dialog.end_session(session_id=intent_message.session_id, text=self._message.get('client_number_mandatory'))
        self.clear_incident()

    # Incident #
    ############

    def info_loyer_charge(self, intent_message, dialog):
        self._logger.info("=> intent info_loyer_charge")

        self.set_new_incident(IncidentType.Sales)

        print("++++")
        print(intent_message.input)
        if intent_message.slots is not None:
            print("----")
        for slot in intent_message.slots:
            print('{0} : {1} / {2} / {3}'.format(slot, intent_message.slots[slot].kind, intent_message.slots[slot].value, intent_message.slots[slot].rawValue))
        dialog.continue_session(session_id=intent_message.session_id,
                                text=self._message.get('ask_for_numero_client'),
                                intent_filter=['smilehack:numeroLocataire', 'smilehack:pasNumeroClient',
                                               'smilehack:smallTalk']
                                )

    def plomberie(self, intent_message, dialog):
        self._logger.info("=> intent plomberie")

        self.set_new_incident(IncidentType.Technical)

        print("++++")
        print(intent_message.input)
        if intent_message.slots is not None:
            print("----")
        for slot in intent_message.slots:
            print('{0} : {1} / {2} / {3}'.format(slot, intent_message.slots[slot].kind, intent_message.slots[slot].value, intent_message.slots[slot].rawValue))
        dialog.continue_session(session_id=intent_message.session_id,
                                text=self._message.get('ask_for_numero_client'),
                                intent_filter = ['smilehack:numeroLocataire', 'smilehack:pasNumeroClient',
                                                 'smilehack:smallTalk']
                                )


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

