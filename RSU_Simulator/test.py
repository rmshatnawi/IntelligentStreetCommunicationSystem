import traci
import json

traci.start(["sumo-gui", "-c", "intersection.sumocfg"])

# تخزين وقت دخول السيارة
vehicle_enter_time = {}

detected_start = set()
detected_end = set()

inbound_edges = ["L_to_C", "R_to_C", "T_to_C", "B_to_C"]

while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    sim_time = traci.simulation.getTime()

    for edge in inbound_edges:
        for lane in [0, 1]:

            start_rsu = f"RSU_{edge}_Start_L{lane}"
            start_data = traci.inductionloop.getVehicleData(start_rsu)

            for d in start_data:
                v_id = d[0]

         
                if v_id not in detected_start:
                    detected_start.add(v_id)

                    vehicle_enter_time[v_id] = sim_time

                    speed = traci.vehicle.getSpeed(v_id) * 3.6   # m/s to km/h

                    event = {
                        "vehicle_id": v_id,
                        "rsu": "RSU_START",
                        "time": sim_time,
                        "lane": f"{edge}_{lane}",
                        "speed_kmh": round(speed, 2)
                    }

                    print("EVENT: START Detected")
                    print(json.dumps(event, indent=2))

            end_rsu = f"RSU_{edge}_End_L{lane}"
            end_data = traci.inductionloop.getVehicleData(end_rsu)

            for d in end_data:
                v_id = d[0]

         
                if v_id not in detected_end:
                    detected_end.add(v_id)

                    t_start = vehicle_enter_time.get(v_id, sim_time)
                    travel_time = sim_time - t_start

                    speed = traci.vehicle.getSpeed(v_id) * 3.6

                    event = {
                        "vehicle_id": v_id,
                        "rsu": "RSU_END",
                        "time": sim_time,
                        "lane": f"{edge}_{lane}",
                        "speed_kmh": round(speed, 2),
                        "travel_time_sec": round(travel_time, 2)
                    }

                    print("EVENT: END Detected")
                    print(json.dumps(event, indent=2))

traci.close()
