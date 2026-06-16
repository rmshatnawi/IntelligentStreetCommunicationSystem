# =============================================================
# Intelligent Street Communication System (ISCS)
# SUMO Simulation - DB-driven RSUs, RSU-to-RSU traffic
# Author: Raghad Shatnawi
# Last Modified: 16 June 2026
# =============================================================
#
# RSUs are loaded from the database via GET /rsus (no hardcoding).
# Each RSU marker is snapped onto the actual road it maps to, so
# the dot sits on the street the cars drive. Every car is spawned
# to travel RSU-to-RSU, so every car passes RSUs and emits signals.

import math
import uuid
import random
import requests
import traci
from datetime import datetime, timezone

BACKEND = "http://192.168.1.21:8000"     # update post-Render-deploy
SERVER_URL = BACKEND + "/ingest"
RSU_URL = BACKEND + "/rsus"

SUMO_CONFIG = "iscs.sumocfg"
DETECTION_RADIUS_M = 25.0     # RSU coverage radius (meters)
TOTAL_VEHICLES = 20           # how many cars to spawn over the run
SPAWN_EVERY_STEPS = 3         # one new car every N simulation steps
VTYPE = "car"                 # must match the vType id in iscs.rou.xml


def fetch_rsus():
    r = requests.get(RSU_URL, timeout=10)
    r.raise_for_status()
    data = r.json()
    rsus = data["rsus"] if isinstance(data, dict) else data
    for x in rsus:
        x["latitude"] = x["lat"]
        x["longitude"] = x["lng"]
    return rsus


def compass(angle_deg):
    # SUMO angle: 0 = north, increases clockwise.
    return ["Northbound", "Eastbound", "Southbound", "Westbound"][round(angle_deg / 90.0) % 4]


def make_plate(used):
    # Unique plate in the format ##-##### (e.g. 23-45187).
    while True:
        plate = f"{random.randint(10, 99)}-{random.randint(10000, 99999)}"
        if plate not in used:
            used.add(plate)
            return plate


def road_xy(edge, pos, lane_index):
    # Return the (x, y) point that is `pos` meters along the given lane.
    lane_id = f"{edge}_{lane_index}"
    shape = traci.lane.getShape(lane_id)
    d = 0.0
    for i in range(len(shape) - 1):
        x1, y1 = shape[i]
        x2, y2 = shape[i + 1]
        seg = math.hypot(x2 - x1, y2 - y1)
        if seg > 0 and d + seg >= pos:
            t = (pos - d) / seg
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        d += seg
    return shape[-1]


def circle_points(cx, cy, r, n=24):
    return [(cx + r * math.cos(2 * math.pi * i / n),
             cy + r * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]


def send_signal(signal):
    try:
        resp = requests.post(SERVER_URL, json=signal, timeout=5)
        print(f"[SENT] {signal['rsu_id']} | {signal['plate_number']} | "
              f"Speed={signal['speed']} | ({signal['latitude']},{signal['longitude']}) | "
              f"Status={resp.status_code}")
        if resp.status_code != 200:
            print("Server error:", resp.text)
    except Exception as e:
        print("Failed to send signal:", e)


# --- Load RSUs from the database -----------------------------
rsus = fetch_rsus()
if len(rsus) < 2:
    raise SystemExit("Need at least 2 RSUs in the database to route cars between them.")

# Use sumo-gui to watch the demo; change to "sumo" for headless.
traci.start(["sumo-gui", "-c", SUMO_CONFIG])

# Map each RSU to its road edge, then snap its marker onto that road.
for rsu in rsus:
    lon, lat = rsu["longitude"], rsu["latitude"]
    edge, pos, lane = traci.simulation.convertRoad(lon, lat, isGeo=True)
    raw_x, raw_y = traci.simulation.convertGeo(lon, lat, fromGeo=True)
    rsu["edge"] = edge
    if edge:
        sx, sy = road_xy(edge, pos, lane)          # snapped point ON the road
        rsu["x"], rsu["y"] = sx, sy
        off = math.hypot(sx - raw_x, sy - raw_y)    # how far the DB point was off
        print(f"{rsu['rsu_id']}: snapped to {edge}, was {off:.1f} m off the road")
    else:
        rsu["x"], rsu["y"] = raw_x, raw_y
        print(f"{rsu['rsu_id']}: NO road found near it (off the imported map)")

rsu_edges = [r["edge"] for r in rsus if r["edge"]]
if len(rsu_edges) < 2:
    raise SystemExit("Could not map RSUs onto roads. Check the coordinates are on the network.")

# --- Draw RSUs on the map: red marker (ID = label) + coverage circle ---
for rsu in rsus:
    if not rsu["edge"]:
        continue
    rid = rsu["rsu_id"]
    traci.poi.add(rid, rsu["x"], rsu["y"], color=(0, 90, 255, 255), layer=10, width=40, height=40)
    traci.polygon.add("zone_" + rid,
                      circle_points(rsu["x"], rsu["y"], DETECTION_RADIUS_M),
                      color=(255, 0, 0, 70), fill=True, layer=5)

inside = {r["rsu_id"]: set() for r in rsus}
used_plates = set()
spawned = 0
step = 0

# Loop until every car is spawned AND the network has drained.
while spawned < TOTAL_VEHICLES or traci.simulation.getMinExpectedNumber() > 0:

    # Spawn an RSU-to-RSU car on schedule.
    if spawned < TOTAL_VEHICLES and step % SPAWN_EVERY_STEPS == 0:
        a, b = random.sample(rsu_edges, 2)
        route = traci.simulation.findRoute(a, b)
        if route.edges:
            rid = f"route_{spawned}"
            vid = make_plate(used_plates)
            traci.route.add(rid, route.edges)
            traci.vehicle.add(vid, rid, typeID=VTYPE, depart="now")
            spawned += 1

    traci.simulationStep()
    step += 1

    vehicles = traci.vehicle.getIDList()
    positions = {v: traci.vehicle.getPosition(v) for v in vehicles}

    for rsu in rsus:
        rx, ry = rsu["x"], rsu["y"]
        now_inside = {v for v in vehicles
                      if math.hypot(positions[v][0] - rx, positions[v][1] - ry) <= DETECTION_RADIUS_M}

        # Vehicles that just entered this RSU's range -> fire once.
        entered = now_inside - inside[rsu["rsu_id"]]
        inside[rsu["rsu_id"]] = now_inside

        for v in entered:
            vx, vy = positions[v]
            lon, lat = traci.simulation.convertGeo(vx, vy)   # SUMO -> (lon, lat)
            signal = {
                "event_id": str(uuid.uuid4()),
                "rsu_id": rsu["rsu_id"],
                "segment": rsu["segment"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "speed": round(traci.vehicle.getSpeed(v) * 3.6, 1),
                "direction": compass(traci.vehicle.getAngle(v)),
                "vehicle_count": 1,
                "plate_number": v,
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
            }
            send_signal(signal)

traci.close()
print("Simulation finished.")