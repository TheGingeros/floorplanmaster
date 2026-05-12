"""NetworkX dependency bootstrap for FloorPlanMaster.

Handles mounting the bundled ``networkx`` wheel so the library is available
inside Blender without requiring the user to install anything manually.  When
online access is permitted the module can also download and install the wheel
on demand.

``mount_networkx()`` is the sole public entry point called from ``__init__.py``
before any ``import networkx`` statements run.
"""
import json
import os
import sys
import textwrap
import urllib.error
import urllib.request

import bpy

_NETWORKX_VERSION = "3.6.1"
_NETWORKX_WHL_NAME = f"networkx-{_NETWORKX_VERSION}-py3-none-any.whl"

# Set to True after install_networkx() completes; signals register() to reload.
_needs_reload = False

_minimal_classes = []


def _cache_dir() -> str:
    # Blender's own user data directory — standard location for addon cache data.
    user_data = bpy.utils.resource_path('USER')
    path = os.path.join(user_data, "floorplanmaster_cache")
    os.makedirs(path, exist_ok=True)
    return path


def mount_networkx() -> bool:
    # Return True if networkx is already importable (installed in venv / Blender
    # Python) or was previously cached by this addon.
    try:
        import networkx  # noqa: F401
        return True
    except ModuleNotFoundError:
        pass

    try:
        whl = os.path.join(_cache_dir(), _NETWORKX_WHL_NAME)
        if os.path.exists(whl):
            if whl not in sys.path:
                sys.path.insert(0, whl)
            import networkx  # noqa: F401
            return True
    except (ModuleNotFoundError, OSError):
        pass

    return False


def has_online_access() -> bool:
    # bpy.app.online_access was introduced in Blender 4.2.
    if bpy.app.version < (4, 2, 0):
        return True
    return bpy.app.online_access


def install_networkx(online_access_override: bool = False) -> bool:
    # Download the pure-Python NetworkX wheel from PyPI and add it to sys.path.
    # Returns True on success.
    if not online_access_override and not has_online_access():
        return False

    try:
        cache = _cache_dir()
    except OSError:
        return False

    whl_path = os.path.join(cache, _NETWORKX_WHL_NAME)

    if not os.path.exists(whl_path):
        try:
            metadata_url = f"https://pypi.org/pypi/networkx/{_NETWORKX_VERSION}/json"
            with urllib.request.urlopen(metadata_url, timeout=20) as resp:
                metadata = json.load(resp)

            wheel_url = None
            for file_info in metadata.get("urls", []):
                if file_info.get("packagetype") != "bdist_wheel":
                    continue
                fn = file_info.get("filename", "")
                if "none-any" in fn and fn.endswith(".whl"):
                    wheel_url = file_info.get("url")
                    break

            if not wheel_url:
                return False

            with urllib.request.urlopen(wheel_url, timeout=60) as resp:
                with open(whl_path, "wb") as fh:
                    fh.write(resp.read())

        except (urllib.error.URLError, TimeoutError, OSError):
            return False

    if whl_path not in sys.path:
        sys.path.insert(0, whl_path)

    return True


_OFFLINE_MSG = (
    "Internet access is required to download NetworkX but is currently "
    "disabled in Blender Preferences > System. Clicking \"Install\" will "
    "override this setting for this one download."
)


def register_minimal():
    # Register only the install-prompt operator and a minimal N-panel.
    # Called from the addon's register() when networkx is not available.

    class FLOORPLAN_OT_install_dependencies(bpy.types.Operator):
        bl_idname = "floorplanmaster.install_dependencies"
        bl_label = "FloorPlanMaster: Install Dependencies?"
        bl_description = "Download and install NetworkX (required by FloorPlanMaster)"

        def execute(self, context):
            if install_networkx(online_access_override=True):
                if mount_networkx():
                    self.report({'INFO'}, "NetworkX installed. Reloading add-ons...")
                    bpy.ops.script.reload()
                    return {'FINISHED'}
            self.report(
                {'ERROR'},
                "Failed to install NetworkX. Check your internet connection and try again.",
            )
            return {'CANCELLED'}

        def invoke(self, context, event):
            return context.window_manager.invoke_props_dialog(
                self,
                width=450,
                title="FloorPlanMaster: Install Dependencies?",
                confirm_text="Install",
            )

        def draw(self, context):
            layout = self.layout
            col = layout.column()
            col.label(
                text="FloorPlanMaster requires NetworkX to function.",
                icon='ERROR',
            )
            col.separator()
            col.label(text=f"  • networkx  {_NETWORKX_VERSION}", icon='DOT')
            col.label(
                text="    Graph algorithms for automatic room detection.",
                icon='BLANK1',
            )

            if not has_online_access():
                col.separator()
                chars = max(30, int(450 / 7))
                wrapper = textwrap.TextWrapper(width=chars)
                sub = col.column()
                sub.active = False
                for line in wrapper.wrap(_OFFLINE_MSG):
                    sub.label(text=line, icon='INFO')

    class FLOORPLAN_PT_missing_dependencies(bpy.types.Panel):
        bl_label = "Missing Dependencies"
        bl_idname = "FLOORPLAN_PT_missing_dependencies"
        bl_category = "FloorPlanMaster"
        bl_space_type = 'VIEW_3D'
        bl_region_type = 'UI'
        bl_order = 0

        def draw_header(self, context):
            self.layout.label(text="", icon='ERROR')

        def draw(self, context):
            self.layout.operator(
                FLOORPLAN_OT_install_dependencies.bl_idname,
                text="Install Dependencies",
                icon='IMPORT',
            )

    _minimal_classes.extend([
        FLOORPLAN_OT_install_dependencies,
        FLOORPLAN_PT_missing_dependencies,
    ])
    for cls in _minimal_classes:
        bpy.utils.register_class(cls)

    def _show_dialog():
        bpy.ops.floorplanmaster.install_dependencies("INVOKE_DEFAULT")

    bpy.app.timers.register(_show_dialog, first_interval=0.5, persistent=False)


def unregister_minimal():
    for cls in reversed(_minimal_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
    _minimal_classes.clear()
