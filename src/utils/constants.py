from enum import IntEnum

# Wall parameter limits
MIN_THICKNESS = 0.05   # meters
MAX_THICKNESS = 1.0
DEFAULT_THICKNESS = 0.2

MIN_HEIGHT = 1.0       # meters
MAX_HEIGHT = 10.0
DEFAULT_HEIGHT = 3.0

# Room parameter limits
MIN_ROOM_AREA = 1.0          # m^2
MIN_ASPECT_RATIO = 0.1
MAX_ASPECT_RATIO = 10.0
MIN_ROOM_VERTICES = 3

# Snapping
SNAP_JUNCTION_TOLERANCE = 15  # pixels
# Default colours (RGBA, 0-1 range)
# Enumerations

class RoomType(IntEnum):
    GENERIC = 0
    LIVING = 1
    TECHNICAL = 2
    COMMUNICATION = 3
