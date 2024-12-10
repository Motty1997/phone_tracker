from typing import List
from CRUD.crud import data_query, single_query
from db.database import driver
from db.models.device import Device
from db.models.interaction import Interaction


def create_devices_and_relationship(devices: List[Device], interaction: Interaction):
    with driver.session() as session:
        try:
            device_id = 0
            for device in devices:
                query = """
                
                    MERGE (d:Device {id: $id})
                    SET d.brand = $brand, d.model = $model, d.os = $os, 
                        d.latitude = $latitude, d.longitude = $longitude, 
                        d.altitude_meters = $altitude_meters, d.accuracy_meters = $accuracy_meters
                """
                parameters = {
                    "id": device.device_id,
                    "brand": device.brand,
                    "model": device.model,
                    "os": device.os,
                    "latitude": device.location.latitude,
                    "longitude": device.location.longitude,
                    "altitude_meters": device.location.altitude_meters,
                    "accuracy_meters": device.location.accuracy_meters
                }
                if device_id == device.device_id:
                    return {"status": "You tried to connect yourself."}
                device_id =device.device_id
                session.run(query, parameters)

            query = """
                MATCH (d1:Device {id: $from_device}), (d2:Device {id: $to_device})
                MERGE (d1)-[r:CONNECTED {method: $method, signal_strength: $signal_strength, 
                                         distance: $distance, duration: $duration, timestamp: $timestamp}]->(d2)
            """
            parameters={
                "from_device": interaction.from_device,
                "to_device": interaction.to_device,
                "method": interaction.method,
                "signal_strength": interaction.signal_strength_dbm,
                "distance": interaction.distance_meters,
                "duration": interaction.duration_seconds,
                "timestamp": interaction.timestamp
            }
            session.run(query, parameters)
        except Exception as e:
            print(f"Error: {e}")
            return {"status": "failure", "message": str(e)}
        return {"status": "success"}


def get_connected_devices_bluetooth() -> List[dict]:
    query = """
        MATCH (start:Device)
        MATCH (end:Device)
        WHERE start <> end
        MATCH path = shortestPath((start)-[:CONNECTED*]->(end))
        WHERE ALL(r IN relationships(path) WHERE r.method = 'Bluetooth')
        WITH path, length(path) as pathLength
        ORDER BY pathLength DESC
        LIMIT 1
        RETURN path
    """
    return data_query(query)


def get_devices_with_strong_signal():
    query = """
        MATCH (d1:Device)-[r:CONNECTED]->(d2:Device)
        WHERE r.signal_strength > -60
        RETURN d1.id AS device1, d2.id AS device2, r.signal_strength AS signal_strength
    """
    return data_query(query)


def count_devices_connected(device_id: str) -> int:
    query = """
        MATCH (d:Device {id: $device_id})-[:CONNECTED]->(other)
        RETURN COUNT(other) AS connected_count
    """
    result = single_query(query, params={"device_id": device_id})
    return result["connected_count"] if result else 0


def is_two_devices_connected(device1: str, device2: str) -> bool:
    query = """
        MATCH (d1:Device {id: $from_device})-[:CONNECTED]->(d2:Device {id: $to_device})
        RETURN d1.id AS device1, d2.id AS device2
    """
    result = single_query(query, params={"device1": device1, "device2": device2})
    return bool(result)


def last_interaction(device_id: str):
    query = """
        MATCH (d:Device {id: $device_id})-[r:CONNECTED]->(d2:Device)
        RETURN d.id AS device, d2.id AS other_device, r.timestamp AS timestamp
        ORDER BY r.timestamp DESC
        LIMIT 1
    """
    return single_query(query, params={"device_id": device_id})
