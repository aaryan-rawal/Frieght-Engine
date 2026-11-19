"""Common enums used across the OptiFreight domain models.
"""

from enum import Enum

class SourceType(str, Enum):
    synthetic = "synthetic"
    manual = "manual"
    csv_import = "csv_import"
    public_api = "public_api"

class ListingStatus(str, Enum):
    open = "open"
    cancelled = "cancelled"
    expired = "expired"
    unavailable = "unavailable"

class Verdict(str, Enum):
    pass_ = "pass"
    fail = "fail"
    unknown = "unknown"

class ClaimTag(str, Enum):
    fact = "fact"
    calculation = "calculation"
    estimate = "estimate"
    recommendation = "recommendation"
    ml_estimate = "ml_estimate"

class ShipmentStatus(str, Enum):
    accepted = "accepted"
    heading_to_pickup = "heading_to_pickup"
    loaded = "loaded"
    in_transit = "in_transit"
    delivered = "delivered"
    cancelled = "cancelled"

class RouteClass(str, Enum):
    on_route = "on_route"
    off_route = "off_route"
