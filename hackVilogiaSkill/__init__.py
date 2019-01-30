# -*- coding: utf-8 -*-
import logging
from hackVilogiaSkill.message import Message
from hackVilogiaSkill.clients import ClientMock
from hackVilogiaSkill.incident import Incident, IncidentType, EmergencyLevel, Sentiment

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
        'mission': [
            "Je suis l'assistant Vilogia. Pouvez-vous me décrire vous problème ?",
            "Je suis l'assistant Vilogia. Vous pouvez me décrire votre problème et je vous transfèrerai au service concerné"
        ],
        'unknownSmallTalk': [
            "Je ne suis pas sur de vous avoir compris... "
        ],
        'ask_for_numero_client': [
            "pouvez-vous me communiquer votre numéro de locataire s'il vous plait ?"
        ],
        'client_number_mandatory': [
            'Désolé, mais nous ne pouvons pas traiter votre demande sans numéro de locataire'
        ],
        'confirmClientPhoneNumber': [
            'pouvez-vous me confirmer que votre numéro de téléphone se termine par {} ?'
        ],
        'client_not_found': [
            'Désolé, mais je ne trouve pas de client avec le numéro {}'
        ],
        'transfer_to_tech_support': [
            'Très bien. Nous transférons votre demande au service technique concerné'
        ],
        'transfer_to_sale_support': [
            'Très bien. Nous transférons votre demande au service commercial concerné'
        ]
    }
}

INTENT_YES = 'smilehack:Yes'
INTENT_NO = 'smilehack:No'


class HackVilogiaSkill:
    def __init__(self):
        self._logger = logging.getLogger('HackVilogiaSkill')
        self._message = Message(SKILL_MESSAGES)
        self._current_incident = None
        self._current_client = None

    def fallback_handler(self):
        return self.unmanaged_event

    def intents_with_handlers(self):
        return {
            'smilehack:smallTalk': self.small_talk,
            'smilehack:sayHowAreYou': self.how_are_you,
            INTENT_YES: self.yes_no,
            INTENT_NO: self.yes_no,
            'smilehack:numeroLocataire': self.numero_locataire,
            'smilehack:pasNumeroClient': self.pas_numero_locataire,
            'smilehack:InfoLoyerCharge': self.info_loyer_charge,
            'smilehack:MultiService': self.multiservice
        }

    def reduce_number(self, slot):
        if slot:
            # If slot is a list of Number, we concatenate them to build a full number
            # Ex: My number is 34 45 56 => 344556
            if isinstance(slot, list):
                return ''.join(list(map(lambda s: str(abs(int(s.value))), slot)))
            else:
                return str(int(slot.value))

    def set_new_incident(self, intent_message, incidentType):
        self._current_incident = Incident(intent_message.intent.intentName, incidentType, intent_message.input)

        if 'Sentiment' in intent_message.slots:
            s = ''
            if isinstance(intent_message.slots['Sentiment'], list):
                s = intent_message.slots['Sentiment'][0].value
            else:
                s = intent_message.slots['Sentiment'].value

            if s == 'énervé':
                self._current_incident.setSentiment(Sentiment.Annoyed)

    def set_incident_client(self):
        self._current_incident.setClient(self._current_client)

    def clear_incident(self):
        self._current_incident = None
        self._current_client = None

    def send_incident(self):
        print(self._current_incident.to_JSON())

    def how_are_you(self, intent_message, dialog):
        self._logger.info("=> intent how_are_you")
        dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('imfine'))

    def small_talk(self, intent_message, dialog):
        self._logger.info("=> intent small_talk")

        if 'hello' in intent_message.slots:
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('hello'))

        if 'bye' in intent_message.slots:
            dialog.end_session(session_id=intent_message.session_id, text=self._message.get('bye'))
            self.clear_incident()

        if 'thanks' in intent_message.slots:
            dialog.continue_session(session_id=intent_message.session_id, text=self._message.get('thanks'))

        return self.unmanaged_event(intent_message, dialog)

    def unmanaged_event(self, intent_message, dialog):
        self._logger.info("=> intent unknown")
        dialog.continue_session(session_id=intent_message.session_id,
                                text='{0} {1}'.format(self._message.get('unknownSmallTalk'), self._message.get('mission')),
                                intent_filter=[
                                                'smilehack:InfoLoyerCharge',
                                                'smilehack:MultiService',
                                                'smilehack:smallTalk'
                                ])
        self.clear_incident()

    def yes_no(self, intent_message, dialog):
        self._logger.info("=> intent yes_no")
        self._logger.info("Custom data: {}".format(intent_message.custom_data))
        custom_data = intent_message.custom_data

        if self._current_incident is None:
            return self.unmanaged_event(intent_message, dialog)

        if intent_message.intent.intentName == INTENT_YES:
            if custom_data is not None:
                if custom_data == 'CONFIRM_CLIENT_PHONE_NUMBER':
                    message = self._message.get(
                        'transfer_to_tech_support') if self._current_incident.incidentType == IncidentType.Technical else self._message.get(
                        'transfer_to_sale_support')
                    dialog.end_session(session_id=intent_message.session_id, text=message)
                    self.set_incident_client()
                    self.send_incident()
                    self.clear_incident()
        else:
            if custom_data is None:
                dialog.end_session(session_id=intent_message.session_id, text=self._message.get('client_number_mandatory'))

            if custom_data is not None:
                if custom_data == 'CONFIRM_CLIENT_PHONE_NUMBER':
                    dialog.continue_session(session_id=intent_message.session_id,
                                                        text=self._message.get('ask_for_numero_client'),
                                                        intent_filter=['smilehack:numeroLocataire', 'smilehack:pasNumeroClient',
                                                                       'smilehack:smallTalk', INTENT_NO]
                                                        )

    def numero_locataire(self, intent_message, dialog):

        if self._current_incident is None:
            return self.unmanaged_event(intent_message, dialog)

        self._logger.info("=> intent numero_locataire")
        number = self.reduce_number(intent_message.slots['Locataire'])
        print(number)
        client = ClientMock.client_by_id(number)
        if client is not None:
            self._current_client = client
            dialog.end_session(session_id=intent_message.session_id, text='Bonjour {0} {1}'.format(client['firstName'], client['lastName']))
            dialog.start_session_action(site_id='default',
                                        text=self._message.get('confirmClientPhoneNumber').format(client['phone'][-2:]),
                                        custom_data='CONFIRM_CLIENT_PHONE_NUMBER',
                                        intent_filter=[INTENT_YES, INTENT_NO, 'smilehack:smallTalk'],
                                        can_be_enqueued=True
                                        )
        else:
            dialog.end_session(session_id=intent_message.session_id, text=self._message.get('client_not_found').format(number))
            dialog.start_session_action(site_id='default',
                                        text=self._message.get('ask_for_numero_client'),
                                        custom_data='ASK_FOR_CLIENT_NUMBER',
                                        intent_filter=['smilehack:numeroLocataire', INTENT_NO, 'smilehack:smallTalk'],
                                        can_be_enqueued=True
                                        )

    def pas_numero_locataire(self, intent_message, dialog):
        # Custom data to be used to know if the client number is mandatory or not
        dialog.end_session(session_id=intent_message.session_id, text=self._message.get('client_number_mandatory'))
        self.clear_incident()

    # Incident #
    ############

    def display_slots(self, slots):
        if slots is not None:
            print("----")
        for slot in slots:
            v = slots[slot]
            if isinstance(v, list):
                print("{} :".format(slot))
                for i in v:
                    print('  - {0} / {1} / {2}'.format(i.kind,
                                                     i.value,
                                                     i.rawValue))
            else:
                print('{0} : {1} / {2} / {3}'.format(slot, v.kind,
                                                     v.value,
                                                     v.rawValue))

    def fillArrayValueInIncident(self, slots, slotName, func):
        if slotName in slots:
            if isinstance(slots[slotName], list):
                func(list(map(lambda e: e.value, slots[slotName])))
            else:
                func([slots[slotName].value])

    def info_loyer_charge(self, intent_message, dialog):
        self._logger.info("=> intent info_loyer_charge")

        self.set_new_incident(intent_message, IncidentType.Sales)

        if intent_message.slots is not None:
            print("----")
            self.display_slots(intent_message.slots)

        dialog.continue_session(session_id=intent_message.session_id,
                                text=self._message.get('ask_for_numero_client'),
                                intent_filter=['smilehack:numeroLocataire', 'smilehack:pasNumeroClient',
                                               INTENT_NO, 'smilehack:smallTalk']
                                )

    def multiservice(self, intent_message, dialog):
        self._logger.info("=> intent multiservice")

        self.set_new_incident(intent_message, IncidentType.Technical)
        self.fillArrayValueInIncident(intent_message.slots, 'Equipement', self._current_incident.setEquipments)

        if intent_message.slots is not None:
            print("----")
            self.display_slots(intent_message.slots)
        dialog.continue_session(session_id=intent_message.session_id,
                                text=self._message.get('ask_for_numero_client'),
                                intent_filter = ['smilehack:numeroLocataire', 'smilehack:pasNumeroClient',
                                                 INTENT_NO, 'smilehack:smallTalk']
                                )


'''

2019-01-30 19:42:18,353 [Thread-1] - [INFO] - => intent numero_locataire
-100


Equipement : Custom / ma baignoire / ma baignoire
ProblemeEmplacement : Custom / logement / logement
PlomberieSanitaireRobinetterie :
  - Custom / robinetterie / robinetterie
  - Custom / tuyau / tuyau


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
