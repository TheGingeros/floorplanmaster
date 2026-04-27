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

# Openings (doors, windows)
MIN_OPENING_WIDTH = 0.3    # meters
MAX_OPENING_WIDTH = 5.0
MIN_OPENING_CLEARANCE = 0.0  # meters between neighboring openings; exact touch is still forbidden
DEFAULT_DOOR_WIDTH = 0.9
DEFAULT_WINDOW_WIDTH = 1.2

MIN_OPENING_HEIGHT = 0.3   # meters
DEFAULT_DOOR_HEIGHT = 2.1
DEFAULT_WINDOW_HEIGHT = 1.2
DEFAULT_WINDOW_SILL = 0.9  # distance from floor to bottom of window

OPENING_CUTTER_OVERSHOOT = 0.05  # extra depth beyond wall surface for boolean
OPENING_CUTTER_Z_OVERSHOOT = 0.01  # vertical overshoot to avoid coplanar faces

# Snapping
SNAP_JUNCTION_TOLERANCE = 15  # pixels
