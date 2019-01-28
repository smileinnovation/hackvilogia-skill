# -*- coding: utf-8 -*-


class Value:
    def __init__(self, kind, value):
        self._kind = kind
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def kind(self):
        return self._kind

    @staticmethod
    def from_payload(payload):
        kind = None
        value = None

        if payload is not None and payload['kind']:
            kind = payload['kind']

        if payload is not None and payload['value']:
            value = payload['value']

        return Value(kind, value)

class Slot:
    def __init__(self, slotName, entity, range, rawValue, value, confidence):
        self._slotName = slotName
        self._entity = entity
        self._range = range
        self._rawValue = rawValue
        self._value = value
        self._confidence = confidence

    def get_intentName(self):
        return self._slotName

    @property
    def entity(self):
        return self._entity

    @property
    def slotName(self):
        return self._slotName

    @property
    def range(self):
        return self._range

    @property
    def rawValue(self):
        return self._rawValue

    @property
    def value(self):
        return self._value.value

    @property
    def kind(self):
        return self._value.kind

    @property
    def confidence(self):
        return self._confidence

    @staticmethod
    def from_payload(payload):
        slotName = None
        entity = None
        range = None
        rawValue = None
        value = None
        confidence = None

        if payload is not None and 'slotName' in payload:
            slotName = payload['slotName']

        if payload is not None and 'entity' in payload:
            entity = payload['entity']

        if payload is not None and 'range' in payload:
            range = payload['range']

        if payload is not None and 'rawValue' in payload:
            rawValue = payload['rawValue']

        if payload is not None and 'value' in payload:
            value = Value.from_payload(payload['value'])

        if payload is not None and 'confidence' in payload:
            confidence = payload['confidence']

        return Slot(slotName, entity, range, rawValue, value, confidence)

class Intent:
    def __init__(self, intentName, probability):
        self._intentName = intentName
        self._probability = probability

    @property
    def intentName(self):
        return self._intentName

    @property
    def probability(self):
        return self._probability

    @staticmethod
    def from_payload(payload):

        intentName = None
        probability = None

        if payload is not None and 'intentName' in payload:
            intentName = payload['intentName']

        if payload is not None and 'probability' in payload:
            probability = payload['probability']

        return Intent(intentName, probability)


class IntentMessage:
    def __init__(self, session_id, custom_data, site_id, input, intent, slots):
        self._session_id = session_id
        self._custom_data = custom_data
        self._site_id = site_id
        self._input = input
        self._intent = intent
        self._slots = slots

    @property
    def session_id(self):
        return self._session_id

    @property
    def custom_data(self):
        return self._custom_data

    @property
    def site_id(self):
        return self._site_id

    @property
    def input(self):
        return self._input

    @property
    def intent(self):
        return self._intent

    @property
    def slots(self):
        return self._slots

    @staticmethod
    def from_payload(payload):

        session_id = None
        custom_data = None
        site_id = None
        input = None
        slots = None
        intent = None

        if payload is not None and 'sessionId' in payload:
            session_id = payload['sessionId']

        if payload is not None and 'custom_data' in payload:
            custom_data = payload['custom_data']

        if payload is not None and 'input' in payload:
            input = payload['input']

        if payload is not None and 'site_id' in payload:
            site_id = payload['site_id']
        else:
            site_id = 'default'

        if payload is not None and 'slots' in payload:
            slots = []
            for index, slot in enumerate(payload['slots']):
                slots.append(Slot.from_payload(slot))

        if payload is not None and 'intent' in payload:
            intent = Intent.from_payload(payload['intent'])

        return IntentMessage(session_id, custom_data, site_id, input, intent, slots)


'''

Parsed intent payload sample:

{
    'input': 'bonjour',
    'id': '021ce50f-0723-4a14-9111-e0eb0e09091c',
    'sessionId': 'c5c1ff05-6281-44ee-9fea-8f90f0c85f00',
    'intent': {
        'intentName': 'smilehack:smallTalk',
        'probability': 1.0
    },
    'slots': [
        {
            'slotName': 'hello',
            'entity': 'bonjour',
            'range': {
                'end': 7,
                'start': 0
            },
            'rawValue': 'bonjour',
            'value': {
                'kind': 'Custom',
                'value': 'bonjour'
            },
            'confidence': 1.0
        }
    ]
}


---

{"id":"ad45375f-b193-4e8b-a218-f4e7e2b75147","input":"what 's the weather in new york tomorrow","intent":{"intentName":"searchWeatherForecast","probability":0.8033236},"slots":[{"confidence":null,"rawValue":"new york","value":{"kind":"Custom","value":"new york"},"range":{"start":23,"end":31},"entity":"locality","slotName":"forecast_locality"},{"confidence":null,"rawValue":"tomorrow","value":{"kind":"InstantTime","value":"2019-01-29 00:00:00 +00:00","grain":"Day","precision":"Exact"},"range":{"start":32,"end":40},"entity":"snips/datetime","slotName":"forecast_start_datetime"}],"sessionId":"48c06334-19a5-4b41-89c8-a037813e92eb"}

'''