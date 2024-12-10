from dataclasses import dataclass


@dataclass
class Location:
    latitude: float
    longitude: float
    altitude_meters: float
    accuracy_meters: float
