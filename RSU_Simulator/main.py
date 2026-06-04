# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/main.py
# Author:   Raghad Shatnawi
# Date:     March 2026
# Purpose:  Entry point for the RSU Simulator.
#           Simulates multiple RSUs running simultaneously,
#           each detecting vehicles and sending signals to
#           the FastAPI server at a regular interval.
#           Uses multithreading so all RSUs run in parallel
#           exactly as they would in a real deployment.
# Updates (May 2026 - Dana Omar)
#   - Added simulated vehicle plate numbers.
#   - Added random plate number generation.
#   - Added Vehicle Tracking support.
#   - Added Stolen Car Detection support.
# ============================================================
print("main.py is starting...")
import time
import random
import threading

from config import (
    SERVER_URL,
    SIGNAL_INTERVAL,
    MAX_SIGNALS,
    RSUS,
    SPEED_MIN,
    SPEED_MAX,
    VEHICLE_COUNT_MIN,
    VEHICLE_COUNT_MAX,
)
from core.publisher import publish_signal
from models.signal import build_signal


# ─── simulate_rsu() ─────────────────────────────────────────
# Simulates a single RSU running continuously.
# Builds a random signal and sends it to the server
# every SIGNAL_INTERVAL seconds.
#
# Each RSU runs in its own thread so they all operate
# independently and simultaneously — just like real RSUs
# installed on different streets across the city.
#
# Parameters:
#   rsu — dictionary with rsu_id, segment, direction

# Sample vehicle plate numbers used by the simulator
# to emulate vehicle identification.
PLATE_NUMBERS = [
    "ABC-123",
    "XYZ-555",
    "DEF-202",
    "JKL-777",
    "MNO-888",
    "PQR-111",
    "TUV-222",
    "WXY-333",
    "AAA-444",
    "BBB-555",
    "CCC-666",
    "DDD-777",
    "EEE-888",
    "FFF-999",
    "GGG-101",
    "HHH-202",
    "III-303",
    "JJJ-404",
    "STL-999",
    "STL-555",
]

def simulate_rsu(rsu: dict):
    rsu_id    = rsu["rsu_id"]
    segment   = rsu["segment"]
    direction = rsu["direction"]
 
    print(f"[START] {rsu_id} is now active on segment: {segment}")

    signal_count = 0

    while True:

        # ─── Check if we reached the signal limit ─────────
        if MAX_SIGNALS is not None and signal_count >= MAX_SIGNALS:
            print(f"[STOP]  {rsu_id} reached max signals ({MAX_SIGNALS})")
            break

        # ─── Simulate random vehicle detection ────────────
        # In a real RSU, these values come from sensors.
        # Here we generate random realistic values.
        speed         = round(random.uniform(SPEED_MIN, SPEED_MAX), 1)
        vehicle_count = random.randint(VEHICLE_COUNT_MIN, VEHICLE_COUNT_MAX)
        plate_number = random.choice(PLATE_NUMBERS)


        # ─── Build the signal ─────────────────────────────
        signal = build_signal(
            rsu_id=rsu_id,
            segment=segment,
            speed=speed,
            vehicle_count=vehicle_count,
            direction=direction,
            plate_number=plate_number,
        )

        # ─── Send the signal to the server ────────────────
        publish_signal(SERVER_URL, signal)

        signal_count += 1

        # ─── Wait before sending the next signal ──────────
        time.sleep(SIGNAL_INTERVAL)


# ─── main() ─────────────────────────────────────────────────
# Starts all RSUs simultaneously using multithreading.
# Each RSU gets its own thread so they run in parallel.
def main():
    print("=" * 55)
    print("  Intelligent Street Communication System")
    print("  RSU Simulator Starting...")
    print(f"  Server : {SERVER_URL}")
    print(f"  RSUs   : {len(RSUS)} units active")
    print(f"  Interval: every {SIGNAL_INTERVAL} seconds")
    print("=" * 55)

    threads = []

    # ─── Create one thread per RSU ────────────────────────
    for rsu in RSUS:
        thread = threading.Thread(
            target=simulate_rsu,
            args=(rsu,),
            daemon=True     # thread stops automatically when main program exits
        )
        threads.append(thread)
        thread.start()

    # ─── Keep main thread alive ───────────────────────────
    # Without this the program exits immediately
    # and all RSU threads die with it.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP]  Simulator stopped by user.")


if __name__ == "__main__":
    main()
