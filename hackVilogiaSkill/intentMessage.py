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

        if payload is not None and 'kind' in payload:
            kind = payload['kind']

        if payload is not None and 'value' in payload:
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

        if payload is not None and 'customData' in payload:
            custom_data = payload['customData']

        if payload is not None and 'input' in payload:
            input = payload['input']

        if payload is not None and 'siteId' in payload:
            site_id = payload['siteId']
        else:
            site_id = 'default'

        if payload is not None and 'slots' in payload:
            slots = {}
            for i, s in enumerate(payload['slots']):
                slot = Slot.from_payload(s)

                if slot.slotName in slots:
                    if isinstance(slots[slot.slotName], list):
                        slots[slot.slotName].append(slot)
                    else:
                        tmp = slots[slot.slotName]
                        slots[slot.slotName] = list()
                        slots[slot.slotName].append(tmp)
                        slots[slot.slotName].append(slot)
                else:
                    slots[slot.slotName] = slot

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

{
    'id': '7340053d-3602-4d62-9595-bb741a916f1b', 
    'input': 'mon num\xe9ro est le quatorze z\xe9ro quatre', 
    'slots': [
        {
            'range': {'end': 26, 'start': 18}, 
            'confidence': 1.0, 
            'entity': 'snips/number', 
            'rawValue': 'quatorze', 
            'slotName': 'locataire', 
            'value': {'kind': 'Number', 'value': 14.0}
        }, 
        {
            'range': {'end': 31, 'start': 27}, 
            'confidence': 1.0, 
            'entity': 'snips/number', 
            'rawValue': 'z\xe9ro', 
            'slotName': 'locataire', 
            'value': {'kind': 'Number', 'value': 0.0}
        }, 
        {
            'range': {'end': 38, 'start': 32}, 
            'confidence': 1.0, 
            'entity': 'snips/number', 
            'rawValue': 'quatre', 
            'slotName': 'locataire', 
            'value': {'kind': 'Number', 'value': 4.0}
        }
    ], 
    'sessionId': 'fda22bcf-9f8d-4d9d-9dae-9145cab0bd82', 
    'intent': {
        'intentName': 'smilehack:numeroLocataire', 
        'probability': 0.98502237
    }
}


---

{"id":"ad45375f-b193-4e8b-a218-f4e7e2b75147","input":"what 's the weather in new york tomorrow","intent":{"intentName":"searchWeatherForecast","probability":0.8033236},"slots":[{"confidence":null,"rawValue":"new york","value":{"kind":"Custom","value":"new york"},"range":{"start":23,"end":31},"entity":"locality","slotName":"forecast_locality"},{"confidence":null,"rawValue":"tomorrow","value":{"kind":"InstantTime","value":"2019-01-29 00:00:00 +00:00","grain":"Day","precision":"Exact"},"range":{"start":32,"end":40},"entity":"snips/datetime","slotName":"forecast_start_datetime"}],"sessionId":"48c06334-19a5-4b41-89c8-a037813e92eb"}

'''