# FloorPlanMaster — Installation and Usage Guide

FloorPlanMaster is a Blender addon for drawing and editing architectural floor plans directly inside the 3D Viewport. It provides a dedicated drawing mode, a pencil tool for placing walls, and parametric controls for room and opening management.

**Requirements:** Blender 5.1.0 or newer.

---

## Installation

### . Install inside Blender

1. Open Blender and go to **Edit > Preferences > Add-ons**.
2. Click **Install from Disk** and select the .zip file with the src folder.
3. Enable the addon by ticking the checkbox next to **FloorPlanMaster**.
4. On first activation Blender installs the bundled NetworkX wheel automatically.

The addon panel is accessible at **View3D > Sidebar (N-panel) > FloorPlanMaster**.

---

## Basic Tools and Controls

### Entering and Exiting FloorPlan Mode

| Action | Key / Location |
| :--- | :--- |
| Enter FloorPlan mode | **Shift+Q** in the 3D Viewport (Object Mode) |
| Exit FloorPlan mode | **Shift+Q** again, or the **Exit FloorPlan Mode** button in the N-panel |

FloorPlan mode is required for all drawing and editing operations. Entering it on an existing mesh object prompts a warning if the object has unsaved edits from Edit Mode.

### Pencil Tool — Drawing Walls

Activate the pencil tool from the Toolbar (T-panel) or press **D** in the 3D Viewport while in FloorPlan mode.

| Action | Input |
| :--- | :--- |
| Place junction / extend wall | Left Mouse Button (click) |
| Finish current wall chain | Right Mouse Button or **Esc** |
| Undo last junction | **Ctrl+Z** |
| Redo | **Ctrl+Shift+Z** or **Ctrl+Y** |
| Toggle N-panel while drawing | **N** |
| Pan / orbit / zoom | Middle Mouse Button, scroll wheel, numpad (pass-through) |

Each click places a junction and connects it to the previous one with a wall segment. Clicking on an existing junction closes a loop.

### Wall Selection and Removal

| Action | Key / Location |
| :--- | :--- |
| Select a wall | Click on it in the viewport |
| Delete selected wall | **X** (only when a wall is selected; otherwise Blender's native delete runs) |

### Room Operations

All room operations are available in the **N-panel** under the FloorPlanMaster tab:

- **Insert Room** — inserts a rectangular room from parameters (width, depth, wall thickness).
- **Remove Room** — removes the currently selected room and its boundary walls.
- **Add Opening** — adds a door or window opening to the selected wall.
- **Remove Opening** — removes an existing opening from the selected wall.

### Edit Mode and Finalization

| Action | Key / Location |
| :--- | :--- |
| Enter Edit Mode | **Tab** (shows a detach-warning dialog for FloorPlan objects) |
| Finalize floor plan | **Finalize** button in the N-panel |

Finalization applies all Geometry Nodes modifiers, converts the floor plan mesh to a standard Blender mesh with UV maps, and removes FloorPlanMaster attributes from the object. This operation is irreversible.

---

## Running the Test Suite

The unit tests cover Layers 1 and 2 (the pure-Python graph core) and do not require a running Blender instance.

### 1. Set up the development environment

```bash
# From the repository root
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r src/requirements-dev.txt
```

`requirements-dev.txt` installs `networkx` and `pytest`.

### 2. Run all tests

```bash
pytest src/tests/
```

### 3. Run with verbose output

```bash
pytest src/tests/ -v
```

### 4. Run a specific test module

```bash
pytest src/tests/test_structural_graph.py
pytest src/tests/test_room_graph.py
pytest src/tests/test_validators.py
pytest src/tests/test_math_helpers.py
```

All tests should pass without any Blender installation. The `bpy` dependency is guarded with `try/except ImportError` in every module that uses it, so the core and utility layers load cleanly under standard Python.

---

## Project Structure (src/)

```
src/
├── __init__.py              # Addon entry point (register / unregister)
├── blender_manifest.toml    # Blender Extensions manifest
├── requirements-dev.txt     # Development dependencies (networkx, pytest)
├── wheels/                  # Bundled NetworkX wheel for distribution
├── core/
│   ├── structural_graph.py  # Layer 1: junctions, walls, planar graph
│   ├── room_graph.py        # Layer 2: rooms, adjacency, cycle detection
│   ├── sync.py              # Layer 3: Python graph -> Blender mesh sync
│   ├── junction_solver.py   # Miter / intersection geometry solver
│   ├── final_mesh_builder.py# Finalization pipeline
│   └── validators.py        # Shared validation rules
├── operators/               # Blender modal operators (FP1–FP7)
├── ui/                      # N-panel sidebar, GPU overlay, properties
├── geometry/                # Geometry Nodes tree builder
├── utils/
│   ├── constants.py         # Default values, limits, enumerations
│   ├── math_helpers.py      # 2D geometry utilities
│   └── unit_format.py       # Display unit formatting
├── tests/                   # pytest unit tests (no Blender required)
└── demo/                    # Standalone demo scripts
```
