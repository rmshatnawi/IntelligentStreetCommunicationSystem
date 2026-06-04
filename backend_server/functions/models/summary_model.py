# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     models/summary_model.py
# Author:   Dana Omar
# Date:     May 2026
# Purpose:  Defines the SegmentTrafficSummary data model used
#           to represent aggregated traffic summaries generated
#           by the backend server.
# ============================================================

from pydantic import BaseModel
from datetime import datetime


class SegmentTrafficSummary(BaseModel):
    segment: str
    window_start: datetime
    window_end: datetime

    signal_count: int
    vehicle_count: int
    avg_speed: float
    flow_rate: float
    density_proxy: float

    traffic_state: str
    computed_at: datetime
