# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/models/traffic_light.py
# Purpose:  Traffic light placed at a fixed distance along the
#           road (between RSU_15 and RSU_16). Holds RED/GREEN
#           state by simulated time. Vehicles stop at its
#           distance while RED and resume on GREEN.
# ============================================================


class TrafficLight:
    def __init__(self, light_id, segment, lat, lng, distance_m,
                 green_seconds, red_seconds):
        self.light_id = light_id
        self.segment = segment
        self.lat = lat
        self.lng = lng
        self.distance_m = distance_m          # position along the road
        self.green_seconds = green_seconds
        self.red_seconds = red_seconds
        self.state = "green"
        self._forced_red_until = None         # set by force_red()

    def force_red(self, sim_time_s):
        """Turn RED now and hold for red_seconds (single-vehicle demo)."""
        self._forced_red_until = sim_time_s + self.red_seconds

    def update(self, sim_time_s):
        """Recompute state for the current simulated time."""
        if self._forced_red_until is not None:
            if sim_time_s < self._forced_red_until:
                self.state = "red"
            else:
                self.state = "green"
                self._forced_red_until = None
        else:
            cycle = self.green_seconds + self.red_seconds
            phase = sim_time_s % cycle
            self.state = "green" if phase < self.green_seconds else "red"
        return self.state

    def as_map_object(self):
        """Serialized form for the map / server."""
        return {
            "type":     "traffic_light",
            "light_id": self.light_id,
            "segment":  self.segment,
            "lat":      self.lat,
            "lng":      self.lng,
            "state":    self.state,
        }