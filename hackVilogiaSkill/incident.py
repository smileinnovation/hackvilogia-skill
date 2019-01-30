import json
from enum import Enum


class IncidentType(str, Enum):
    Technical = 'technical'
    Sales = 'sales'


class EmergencyLevel(str, Enum):
    Urgent = 'urgent'
    Regular = 'regular'


class Incident:
    def __init__(self, incidentType):
        self.incidentType = incidentType
        self.emergencyLevel = None

    def to_JSON(self):
        return json.dumps(self.__dict__)

    def setEmergencyLevel(self, emergencyLevel):
        self.emergencyLevel = emergencyLevel
