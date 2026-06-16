import traci
import json
import requests
import uuid
from datetime import datetime, timezone

SERVER_URL = "http://192.168.1.21:8000/ingest"

traci.start([
    "sumo",
    "-c",
    "intersection.sumocfg"
])

detected = set()

RSU_CONFIG = {
    "RSU_01_START": {"segment": "street1 St", "direction": "Westbound"},
    "RSU_01_END":   {"segment": "street1 St", "direction": "Westbound"},
    "RSU_02_START": {"segment": "street2 St", "direction": "Eastbound"},
    "RSU_02_END":   {"segment": "street2 St", "direction": "Eastbound"},
    "RSU_03_START": {"segment": "street3 St", "direction": "Southbound"},
    "RSU_03_END":   {"segment": "street3 St", "direction": "Southbound"},
    "RSU_04_START": {"segment": "street4 St", "direction": "Northbound"},
    "RSU_04_END":   {"segment": "street4 St", "direction": "Northbound"},
}

def send_signal(signal):
    try:
        response = requests.post(
            SERVER_URL,
            json=signal,
            timeout=5
        )

        print(
            f"[SENT] {signal['rsu_id']} | "
            f"{signal['plate_number']} | "
            f"Speed={signal['speed']} | "
            f"Status={response.status_code}"
        )

        if response.status_code != 200:
            print("Server error:", response.text)

    except Exception as e:
        print("Failed to send signal:", e)


while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()
    sim_time = traci.simulation.getTime()

    for rsu_id, rsu_info in RSU_CONFIG.items():

        rsu_data = traci.inductionloop.getVehicleData(rsu_id)

        for data in rsu_data:

            vehicle_id = data[0]
            event_key = f"{rsu_id}_{vehicle_id}"

            if event_key in detected:
                continue

            detected.add(event_key)

            plate_number = vehicle_id
            speed = traci.vehicle.getSpeed(vehicle_id) * 3.6
            vehicle_count = 1

            signal = {
                "event_id": str(uuid.uuid4()),
                "rsu_id": rsu_id,
                "segment": rsu_info["segment"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "speed": round(speed, 1),
                "direction": rsu_info["direction"],
                "vehicle_count": vehicle_count,
                "plate_number": plate_number,
            }

            send_signal(signal)

traci.close()

print("Simulation finished.")