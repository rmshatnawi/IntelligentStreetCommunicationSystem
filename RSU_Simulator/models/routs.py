# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/models/route.py
# Purpose:  Road geometry. Builds an ordered polyline from the
#           RSU list, computes cumulative distance along the
#           road, and interpolates a lat/lng for any distance.
#           Used to move a vehicle continuously between RSUs
#           instead of jumping from one to the next.
# ============================================================

from math import radians, sin, cos, sqrt, atan2

EARTH_RADIUS_M = 6371000.0


def haversine_m(lat1, lng1, lat2, lng2):
    """Great-circle distance in meters between two coordinates."""
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dl = radians(lng2 - lng1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * atan2(sqrt(a), sqrt(1 - a))


class Route:
    """Ordered list of RSU nodes with cumulative distance."""

    def __init__(self, nodes, total_distance_m):
        self.nodes = nodes                      # each: rsu_id, segment, direction, lat, lng, distance_m
        self.total_distance_m = total_distance_m

    def position_at(self, distance_m):
        """Return (lat, lng) at a given distance along the road."""
        d = max(0.0, min(distance_m, self.total_distance_m))
        nodes = self.nodes
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            if a["distance_m"] <= d <= b["distance_m"]:
                span = b["distance_m"] - a["distance_m"]
                frac = 0.0 if span == 0 else (d - a["distance_m"]) / span
                lat = a["lat"] + (b["lat"] - a["lat"]) * frac
                lng = a["lng"] + (b["lng"] - a["lng"]) * frac
                return (lat, lng)
        last = nodes[-1]
        return (last["lat"], last["lng"])

    def distance_after(self, rsu_id, lat, lng):
        """Distance along the road of a point placed just after rsu_id."""
        for node in self.nodes:
            if node["rsu_id"] == rsu_id:
                return node["distance_m"] + haversine_m(node["lat"], node["lng"], lat, lng)
        return self.total_distance_m


def build_route(rsus):
    """Build a Route from the ordered RSU list in config."""
    nodes = []
    total = 0.0
    prev = None
    for rsu in rsus:
        if prev is not None:
            total += haversine_m(prev["lat"], prev["lng"], rsu["lat"], rsu["lng"])
        nodes.append({
            "rsu_id":     rsu["rsu_id"],
            "segment":    rsu["segment"],
            "direction":  rsu["direction"],
            "lat":        rsu["lat"],
            "lng":        rsu["lng"],
            "distance_m": total,
        })
        prev = rsu
    return Route(nodes, total)