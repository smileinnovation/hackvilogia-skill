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


class HousingType(str, Enum):
    Individual = 'individual'
    Mutual = 'mutual'


class Incident:
    def __init__(self, incidentType, user_input):
        self.incidentType = incidentType
        self.emergencyLevel = EmergencyLevel.Regular
        self.sentiment = Sentiment.Neutral
        self.user_input = user_input
        self.client = None
        self.housingType = HousingType.Individual
        self.incidentCategories = []
        self.incidentPlace = None
        self.incidentKeywords = []
        self.equipments = []

    def to_JSON(self):
        return json.dumps(self.__dict__)

    def setEmergencyLevel(self, emergencyLevel):
        self.emergencyLevel = emergencyLevel

    def setSentiment(self, sentiment):
        self.sentiment = sentiment

    def setInput(self, input):
        self.input = input

    def setHousingType(self, housingType):
        self.housingType = housingType

    def setIncidentCategories(self, incidentCategories):
        self.incidentCategories = incidentCategories

    def setIncidentPlace(self, incidentPlace):
        self.incidentPlace = incidentPlace

    def setIncidentKeywords(self, incidentKeywords):
        self.incidentKeywords = incidentKeywords

    def setEquipments(self, equipments):
        self.equipments = equipments

    def setClient(self, client):
        self.client = client
