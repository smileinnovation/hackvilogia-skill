import json
from enum import Enum


class IncidentType(str, Enum):
    Technical = 'technical'
    Sales = 'sales'


class EmergencyLevel(str, Enum):
    Urgent = 'urgent'
    Regular = 'regular'


class Sentiment(str, Enum):
    Neutral = 'neutral'
    Annoyed = 'annoyed'


class Incident:
    def __init__(self, incidentType, user_input):
        self.incidentType = incidentType
        self.emergencyLevel = EmergencyLevel.Regular
        self.sentiment = Sentiment.Neutral
        self.user_input = user_input
        self.client = None
        self.categories = []
        self.places = []
        self.equipments = []

    def to_JSON(self):
        return json.dumps(self.__dict__)

    def setEmergencyLevel(self, emergencyLevel):
        self.emergencyLevel = emergencyLevel

    def setSentiment(self, sentiment):
        self.sentiment = sentiment

    def setInput(self, input):
        self.input = input

    def setCategories(self, categories):
        self.categories = self.categories + categories

    def setPlaces(self, places):
        self.places = self.places + places

    def setEquipments(self, equipments):
        self.equipments = self.equipments + equipments

    def setClient(self, client):
        self.client = client
