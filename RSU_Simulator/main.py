# # ============================================================
# # Project:  Intelligent Street Communication System (ISCS)
# # File:     RSU_Simulator/main.py
# # Author:   Raghad Shatnawi
# # Date:     March 2026
# # Purpose:  Entry point for the RSU Simulator.
# #           Simulates multiple RSUs running simultaneously,
# #           each detecting vehicles and sending signals to
# #           the FastAPI server at a regular interval.
# #           Uses multithreading so all RSUs run in parallel
# #           exactly as they would in a real deployment.
# # Updates (May 2026 - Dana Omar)
# #   - Added simulated vehicle plate numbers.
# #   - Added random plate number generation.
# #   - Added Vehicle Tracking support.
# #   - Added Stolen Car Detection support.
# # ============================================================
# print("main.py is starting...")
# import time
# import random
# import threading

# from config import (
#     SERVER_URL,
#     SIGNAL_INTERVAL,
#     MAX_SIGNALS,
#     RSUS,
#     SPEED_MIN,
#     SPEED_MAX,
#     VEHICLE_COUNT_MIN,
#     VEHICLE_COUNT_MAX,
# )
# from core.publisher import publish_signal
# from models.signal import build_signal


# # ─── simulate_rsu() ─────────────────────────────────────────
# # Simulates a single RSU running continuously.
# # Builds a random signal and sends it to the server
# # every SIGNAL_INTERVAL seconds.
# #
# # Each RSU runs in its own thread so they all operate
# # independently and simultaneously — just like real RSUs
# # installed on different streets across the city.
# #
# # Parameters:
# #   rsu — dictionary with rsu_id, segment, direction

# # Sample vehicle plate numbers used by the simulator
# # to emulate vehicle identification.
# PLATE_NUMBERS = [
#     "12-34567",
#     "15-98234",
#     "18-45678",
#     "21-12345",
#     "24-67891",
#     "27-54321",
#     "31-98765",
#     "34-11223",
#     "37-44556",
#     "42-77889",
#     "45-23456",
#     "48-56789",
#     "52-34567",
#     "55-89012",
#     "58-45612",
#     "61-23489",
#     "64-56734",
#     "67-89123",
#     "71-34598",
#     "74-67845",
#     "77-91234",
#     "81-45673",
#     "84-78912",
#     "87-12398",
#     "91-56743",
#     "94-89067",
#     "97-23415",
#     "101-67824",
#     "104-91256",
#     "108-34579",
# ]

# def simulate_rsu(rsu: dict):
#     rsu_id    = rsu["rsu_id"]
#     segment   = rsu["segment"]
#     direction = rsu["direction"]
#     lat = rsu["lat"]
#     lng = rsu["lng"]
 
#     print(f"[START] {rsu_id} is now active on segment: {segment}")

#     signal_count = 0

#     while True:

#         # ─── Check if we reached the signal limit ─────────
#         if MAX_SIGNALS is not None and signal_count >= MAX_SIGNALS:
#             print(f"[STOP]  {rsu_id} reached max signals ({MAX_SIGNALS})")
#             break

#         # ─── Simulate random vehicle detection ────────────
#         # In a real RSU, these values come from sensors.
#         # Here we generate random realistic values.
#         speed         = round(random.uniform(SPEED_MIN, SPEED_MAX), 1)
#         vehicle_count = random.randint(VEHICLE_COUNT_MIN, VEHICLE_COUNT_MAX)
#         plate_number = random.choice(PLATE_NUMBERS)


#         # ─── Build the signal ─────────────────────────────
#         signal = build_signal(
#             rsu_id=rsu_id,
#             segment=segment,
#             speed=speed,
#             vehicle_count=vehicle_count,
#             direction=direction,
#             plate_number=plate_number,
#             lat=lat,
#             lng=lng
#         )

#         # ─── Send the signal to the server ────────────────
#         publish_signal(SERVER_URL, signal)

#         signal_count += 1

#         # ─── Wait before sending the next signal ──────────
#         time.sleep(SIGNAL_INTERVAL)


# # ─── main() ─────────────────────────────────────────────────
# # Starts all RSUs simultaneously using multithreading.
# # Each RSU gets its own thread so they run in parallel.
# def main():
#     print("=" * 55)
#     print("  Intelligent Street Communication System")
#     print("  RSU Simulator Starting...")
#     print(f"  Server : {SERVER_URL}")
#     print(f"  RSUs   : {len(RSUS)} units active")
#     print(f"  Interval: every {SIGNAL_INTERVAL} seconds")
#     print("=" * 55)

#     threads = []

#     # ─── Create one thread per RSU ────────────────────────
#     for rsu in RSUS:
#         thread = threading.Thread(
#             target=simulate_rsu,
#             args=(rsu,),
#             daemon=True     # thread stops automatically when main program exits
#         )
#         threads.append(thread)
#         thread.start()

#     # ─── Keep main thread alive ───────────────────────────
#     # Without this the program exits immediately
#     # and all RSU threads die with it.
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("\n[STOP]  Simulator stopped by user.")


# if __name__ == "__main__":
#     main()
# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/main.py
# Purpose:  Entry point. Runs one vehicle with a persistent
#           identity along the RSU polyline (RSU_01 -> RSU_16).
#           The vehicle moves continuously, is detected in order
#           by each RSU, and stops at the traffic light between
#           RSU_15 and RSU_16 while it is red.
# Updates (Jun 2026)
#   - Replaced independent random per-RSU generation with a
#     single tracked vehicle moving along the road.
#   - Added continuous movement, travel-time timestamps,
#     traffic light with red stop, light as a map object.
#   - Structured to support multiple vehicles later.
# ============================================================
# print("main.py is starting...")

# import time
# from datetime import UTC, datetime, timedelta

# from config import (
#     SERVER_URL,
#     INGEST_ENDPOINT,
#     LIGHT_ENDPOINT,
#     SEND_LIGHT_EVENTS,
#     SIM_TICK_SECONDS,
#     REAL_TICK_SECONDS,
#     VEHICLE_CRUISE_SPEED,
#     VEHICLE_PLATE,
#     VEHICLE_ID,
#     TRAFFIC_LIGHT,
#     DEMO_FORCE_STOP,
#     RSUS,
# )
# from core.publisher import publish_signal, publish_light_state
# from models.signal import build_signal
# from models.routs import build_route
# from models.traffic_light import TrafficLight
# from models.vehicle import Vehicle


# def build_light(route):
#     cfg = TRAFFIC_LIGHT
#     distance_m = route.distance_after(cfg["between"][0], cfg["lat"], cfg["lng"])
#     return TrafficLight(
#         light_id=cfg["light_id"],
#         segment=cfg["segment"],
#         lat=cfg["lat"],
#         lng=cfg["lng"],
#         distance_m=distance_m,
#         green_seconds=cfg["green_seconds"],
#         red_seconds=cfg["red_seconds"],
#     )


# def run_simulation():
#     route = build_route(RSUS)
#     light = build_light(route)
#     vehicle = Vehicle(VEHICLE_ID, VEHICLE_PLATE, route, VEHICLE_CRUISE_SPEED)

#     print("=" * 55)
#     print("  Intelligent Street Communication System")
#     print("  RSU Simulator — single tracked vehicle")
#     print(f"  Server   : {SERVER_URL}")
#     print(f"  RSUs     : {len(RSUS)} units (RSU_01 -> RSU_16)")
#     print(f"  Vehicle  : {vehicle.plate_number} @ {vehicle.cruise_speed_kmh} km/h")
#     print(f"  Road     : {route.total_distance_m:.0f} m")
#     print(f"  Light    : {light.light_id} at {light.distance_m:.0f} m "
#           f"(between {TRAFFIC_LIGHT['between'][0]} and {TRAFFIC_LIGHT['between'][1]})")
#     print("=" * 55)

#     sim_start = datetime.now(UTC)
#     sim_time = 0.0
#     light_forced = False
#     last_light_state = None

#     if SEND_LIGHT_EVENTS:
#         light.update(sim_time)
#         publish_light_state(SERVER_URL, light.as_map_object(), LIGHT_ENDPOINT)

#     while not vehicle.finished:
#         # Single-vehicle demo: force the light red on arrival.
#         if (DEMO_FORCE_STOP and not light_forced
#                 and vehicle.distance_m < light.distance_m
#                 and vehicle.distance_m + vehicle.speed_ms * SIM_TICK_SECONDS >= light.distance_m):
#             light.force_red(sim_time)
#             light_forced = True

#         light.update(sim_time)
#         if light.state != last_light_state:
#             print(f"[LIGHT] {light.light_id} -> {light.state.upper()}  (t+{sim_time:.0f}s)")
#             if SEND_LIGHT_EVENTS:
#                 publish_light_state(SERVER_URL, light.as_map_object(), LIGHT_ENDPOINT)
#             last_light_state = light.state

#         for node, crossing, speed in vehicle.advance(SIM_TICK_SECONDS, sim_time, light):
#             ts = (sim_start + timedelta(seconds=crossing)).isoformat()
#             signal = build_signal(
#                 rsu_id=node["rsu_id"],
#                 segment=node["segment"],
#                 speed=speed,
#                 vehicle_count=1,
#                 direction=node["direction"],
#                 plate_number=vehicle.plate_number,
#                 lat=node["lat"],
#                 lng=node["lng"],
#                 timestamp=ts,
#             )
#             publish_signal(SERVER_URL, signal, INGEST_ENDPOINT)
#             print(f"[DETECT] {node['rsu_id']} saw {vehicle.plate_number} "
#                   f"@ {speed} km/h  (t+{crossing:.0f}s)")

#         if vehicle.stopped:
#             print(f"[WAIT]  {vehicle.plate_number} stopped at {light.light_id} (RED)  t+{sim_time:.0f}s")

#         sim_time += SIM_TICK_SECONDS
#         time.sleep(REAL_TICK_SECONDS)

#     print(f"[DONE]  {vehicle.plate_number} completed the route "
#           f"({route.total_distance_m:.0f} m, t+{sim_time:.0f}s).")


# def main():
#     try:
#         run_simulation()
#     except KeyboardInterrupt:
#         print("\n[STOP]  Simulator stopped by user.")


# if __name__ == "__main__":
#     main()

# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/main.py
# Purpose:  Entry point. Real-time traffic flow.
#           New vehicles enter at RSU_01 on a fixed interval,
#           each with its own identity and speed, all moving
#           along the road at once. Every RSU detects each
#           vehicle live as it passes. The traffic light
#           between RSU_15 and RSU_16 cycles; vehicles arriving
#           on red stop until green.
# ============================================================
print("main.py is starting...")

import time
import random
import string
from datetime import UTC, datetime, timedelta

from config import (
    SERVER_URL,
    INGEST_ENDPOINT,
    LIGHT_ENDPOINT,
    SEND_LIGHT_EVENTS,
    SIM_TICK_SECONDS,
    REAL_TICK_SECONDS,
    SPAWN_INTERVAL_SECONDS,
    MAX_VEHICLES,
    VEHICLE_SPEED_MIN,
    VEHICLE_SPEED_MAX,
    TRAFFIC_LIGHT,
    RSUS,
)
from core.publisher import publish_signal, publish_light_state
from models.signal import build_signal
from models.routs import build_route
from models.traffic_light import TrafficLight
from models.vehicle import Vehicle


def build_light(route):
    cfg = TRAFFIC_LIGHT
    distance_m = route.distance_after(cfg["between"][0], cfg["lat"], cfg["lng"])
    return TrafficLight(
        light_id=cfg["light_id"],
        segment=cfg["segment"],
        lat=cfg["lat"],
        lng=cfg["lng"],
        distance_m=distance_m,
        green_seconds=cfg["green_seconds"],
        red_seconds=cfg["red_seconds"],
    )


_used_plates = set()

def random_plate():
    while True:
        prefix = "".join(random.choices(string.digits, k=2))   # 2 digits
        number = "".join(random.choices(string.digits, k=5))   # 5 digits
        plate = f"{prefix}-{number}"
        if plate not in _used_plates:
            _used_plates.add(plate)
            return plate


def spawn_vehicle(index, route):
    plate = random_plate()
    speed = round(random.uniform(VEHICLE_SPEED_MIN, VEHICLE_SPEED_MAX), 1)
    return Vehicle(f"VEH_{index:04d}", plate, route, speed)


def run_simulation():
    route = build_route(RSUS)
    light = build_light(route)

    print("=" * 55)
    print("  Intelligent Street Communication System")
    print("  RSU Simulator - real-time traffic")
    print(f"  Server   : {SERVER_URL}")
    print(f"  RSUs     : {len(RSUS)} units (RSU_01 -> RSU_16)")
    print(f"  Road     : {route.total_distance_m:.0f} m")
    print(f"  Spawn    : 1 vehicle every {SPAWN_INTERVAL_SECONDS}s "
          f"(max {MAX_VEHICLES if MAX_VEHICLES is not None else 'unlimited'})")
    print(f"  Speed    : {VEHICLE_SPEED_MIN}-{VEHICLE_SPEED_MAX} km/h")
    print(f"  Light    : {light.light_id} at {light.distance_m:.0f} m "
          f"({TRAFFIC_LIGHT['green_seconds']}s green / {TRAFFIC_LIGHT['red_seconds']}s red)")
    print("=" * 55)

    sim_start = datetime.now(UTC)
    sim_time = 0.0
    vehicles = []
    spawned = 0
    next_spawn = 0.0
    last_light_state = None

    while True:
        # --- release new vehicles at RSU_01 ---------------
        if (MAX_VEHICLES is None or spawned < MAX_VEHICLES) and sim_time >= next_spawn:
            v = spawn_vehicle(spawned + 1, route)
            vehicles.append(v)
            spawned += 1
            next_spawn += SPAWN_INTERVAL_SECONDS
            print(f"[ENTER]  {v.plate_number} entered at RSU_01 @ {v.speed_kmh} km/h "
                  f"(t+{sim_time:.0f}s)")

        # --- update the traffic light ---------------------
        light.update(sim_time)
        if light.state != last_light_state:
            print(f"[LIGHT]  {light.light_id} -> {light.state.upper()}  (t+{sim_time:.0f}s)")
            if SEND_LIGHT_EVENTS:
                publish_light_state(SERVER_URL, light.as_map_object(), LIGHT_ENDPOINT)
            last_light_state = light.state

        # --- advance every active vehicle -----------------
        for v in vehicles:
            if v.finished:
                continue
            for node, crossing, speed in v.advance(SIM_TICK_SECONDS, sim_time, light):
                ts = (sim_start + timedelta(seconds=crossing)).isoformat()
                signal = build_signal(
                    rsu_id=node["rsu_id"],
                    segment=node["segment"],
                    speed=speed,
                    vehicle_count=1,
                    direction=node["direction"],
                    plate_number=v.plate_number,
                    lat=node["lat"],
                    lng=node["lng"],
                    timestamp=ts,
                )
                publish_signal(SERVER_URL, signal, INGEST_ENDPOINT)
                print(f"[DETECT] {node['rsu_id']} <- {v.plate_number} "
                      f"@ {speed} km/h  (t+{crossing:.0f}s)")

        # --- drop vehicles that left the road -------------
        vehicles = [v for v in vehicles if not v.finished]

        # --- stop only in finite mode when everything done ---
        if MAX_VEHICLES is not None and spawned >= MAX_VEHICLES and not vehicles:
            break

        sim_time += SIM_TICK_SECONDS
        time.sleep(REAL_TICK_SECONDS)

    print(f"[DONE]  All vehicles completed the route (t+{sim_time:.0f}s).")


def main():
    try:
        run_simulation()
    except KeyboardInterrupt:
        print("\n[STOP]  Simulator stopped by user.")


if __name__ == "__main__":
    main()