# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/models/vehicle.py
# Purpose:  A single vehicle with a persistent identity that
#           travels along the Route. Reports a detection each
#           time it passes an RSU and stops at a red light.
#           Designed so many Vehicle instances can run together.
# ============================================================


class Vehicle:
    def __init__(self, vehicle_id, plate_number, route, cruise_speed_kmh):
        self.vehicle_id = vehicle_id
        self.plate_number = plate_number
        self.route = route
        self.cruise_speed_kmh = cruise_speed_kmh
        self.speed_kmh = cruise_speed_kmh
        self.distance_m = 0.0          # distance traveled along the road
        self.next_node_index = 0       # next RSU not yet detected
        self.stopped = False
        self.finished = False

    @property
    def speed_ms(self):
        return self.speed_kmh / 3.6

    def position(self):
        return self.route.position_at(self.distance_m)

    def advance(self, dt_s, sim_time_s, light):
        """
        Move the vehicle for one simulated tick.

        Returns a list of detection tuples (node, crossing_sim_time, speed)
        for every RSU crossed during this tick. The crossing time is
        interpolated so consecutive RSU timestamps reflect real travel time.
        """
        if self.finished:
            return []

        target = self.distance_m + self.speed_ms * dt_s

        # Stop at a red light if the move would cross its position.
        if (light is not None and light.state == "red"
                and self.distance_m <= light.distance_m < target):
            effective_target = light.distance_m
            self.stopped = True
        else:
            effective_target = target
            self.stopped = False

        start = self.distance_m
        detections = []
        while self.next_node_index < len(self.route.nodes):
            node = self.route.nodes[self.next_node_index]
            if node["distance_m"] <= effective_target + 1e-6:
                if self.speed_ms > 0 and node["distance_m"] > start:
                    crossing = sim_time_s + (node["distance_m"] - start) / self.speed_ms
                else:
                    crossing = sim_time_s
                detections.append((node, crossing, self.speed_kmh))
                self.next_node_index += 1
            else:
                break

        self.distance_m = effective_target

        if (self.next_node_index >= len(self.route.nodes)
                and self.distance_m >= self.route.total_distance_m - 1e-6):
            self.finished = True

        return detections