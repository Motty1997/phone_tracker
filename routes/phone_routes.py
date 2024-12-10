from flask import Blueprint, request, jsonify
from db.models.device import Device
from db.models.interaction import Interaction
from db.models.location import Location
from repository.phone_repo import create_devices_and_relationship, get_connected_devices_bluetooth, \
    get_devices_with_strong_signal, count_devices_connected, is_two_devices_connected, last_interaction

phone_blueprint = Blueprint("phone", __name__)

@phone_blueprint.route("/api/phone_tracker", methods=["POST"])
def create_phone_tracker():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data received"}), 400

        devices = data.get("devices", [])
        interaction_data = data.get("interaction", {})

        device_objs = []
        for device in devices:
            location = Location(
                latitude=device["location"]["latitude"],
                longitude=device["location"]["longitude"],
                altitude_meters=device["location"]["altitude_meters"],
                accuracy_meters=device["location"]["accuracy_meters"]
            )
            device_objs.append(Device(
                device_id=device["id"],
                brand=device["brand"],
                model=device["model"],
                os=device["os"],
                location=location
            ))

        interaction = Interaction(**interaction_data)
        result = create_devices_and_relationship(device_objs, interaction)

        if result["status"] == "success":
            return jsonify({"status": "success"}), 200
        else:
            return jsonify({"status": "failure", "message": result["message"]}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phone_blueprint.route("/api/devices/connected", methods=["GET"])
def find_connected_devices():
    try:
        results = get_connected_devices_bluetooth()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phone_blueprint.route("/api/devices/signal_strength", methods=["GET"])
def find_strong_signal_devices():
    try:
        results = get_devices_with_strong_signal()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phone_blueprint.route("/api/devices/count_connected", methods=["GET"])
def count_connected_devices():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    try:
        connected_count = count_devices_connected(device_id)
        return jsonify({"connected_count": connected_count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phone_blueprint.route("/api/devices/direct_connection", methods=["GET"])
def check_direct_connection():
    from_device = request.args.get("from_device")
    to_device = request.args.get("to_device")

    if not from_device or not to_device:
        return jsonify({"error": "Both 'device1' and 'device2' are required"}), 400

    try:
        connected = is_two_devices_connected(from_device, to_device)
        return jsonify({"status": "connected" if connected else "not connected"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@phone_blueprint.route("/api/devices/recent_interaction", methods=["GET"])
def get_recent_interaction():
    device_id = request.args.get("device_id")
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    try:
        recent_interaction = last_interaction(device_id)
        if recent_interaction:
            return jsonify(recent_interaction), 200
        else:
            return jsonify({"error": "No interaction found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
