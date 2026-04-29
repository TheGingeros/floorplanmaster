# GPU overlay manager — single persistent POST_VIEW + POST_PIXEL handler pair.
#
# Rather than each feature registering its own draw_handler_add/remove pair,
# all GPU overlays go through this module.  The manager holds one handler per
# space and dispatches to registered layer callables in insertion order.
#
# Layer contract:
#   fn(context)  — receives bpy.context at draw time (never a stale snapshot).
#   space='3D'   — POST_VIEW  (world-space geometry)
#   space='2D'   — POST_PIXEL (screen-space UI)
#
# Lifecycle:
#   overlay_manager.register()   — called once in addon register()
#   overlay_manager.unregister() — called once in addon unregister()
#
#   overlay_manager.register_layer(fn, space)   — add a layer (idempotent)
#   overlay_manager.unregister_layer(fn, space) — remove a layer (no-op if absent)
#
# Persistent layers (selection highlights) are registered right after
# overlay_manager.register() in the addon register() function.
# Transient layers (modal tool overlays such as the Pencil Tool) are registered
# in their operator invoke() and unregistered in their _finish().

import bpy
import traceback

_3d_layers = []  # POST_VIEW  callables: fn(context)
_2d_layers = []  # POST_PIXEL callables: fn(context)

_handle_3d = None
_handle_2d = None
_reported_failures = set()


def _report_layer_failure(space, fn, exc):
    key = (space, getattr(fn, "__module__", ""), getattr(fn, "__name__", repr(fn)))
    if key in _reported_failures:
        return
    _reported_failures.add(key)
    print(f"[FloorPlanMaster] Overlay layer failed ({space}): {key[1]}.{key[2]}: {exc}")
    traceback.print_exc()


def _dispatch_3d():
    ctx = bpy.context
    if ctx is None:
        return
    for fn in list(_3d_layers):
        try:
            fn(ctx)
        except Exception as exc:
            _report_layer_failure('3D', fn, exc)


def _dispatch_2d():
    ctx = bpy.context
    if ctx is None:
        return
    for fn in list(_2d_layers):
        try:
            fn(ctx)
        except Exception as exc:
            _report_layer_failure('2D', fn, exc)


def register_layer(fn, space='3D'):
    # Register a draw layer.  Duplicate registrations are silently ignored.
    if space == '3D':
        if fn not in _3d_layers:
            _3d_layers.append(fn)
    else:
        if fn not in _2d_layers:
            _2d_layers.append(fn)


def unregister_layer(fn, space='3D'):
    # Remove a previously registered layer.  No-op if fn is not present.
    if space == '3D':
        if fn in _3d_layers:
            _3d_layers.remove(fn)
    else:
        if fn in _2d_layers:
            _2d_layers.remove(fn)


def register():
    # Register the single persistent handler pair.  Safe to call multiple times.
    global _handle_3d, _handle_2d
    if _handle_3d is None:
        _handle_3d = bpy.types.SpaceView3D.draw_handler_add(
            _dispatch_3d, (), 'WINDOW', 'POST_VIEW'
        )
    if _handle_2d is None:
        _handle_2d = bpy.types.SpaceView3D.draw_handler_add(
            _dispatch_2d, (), 'WINDOW', 'POST_PIXEL'
        )


def unregister():
    # Remove all layers and the handler pair.
    global _handle_3d, _handle_2d
    _3d_layers.clear()
    _2d_layers.clear()
    _reported_failures.clear()
    if _handle_3d is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle_3d, 'WINDOW')
        _handle_3d = None
    if _handle_2d is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle_2d, 'WINDOW')
        _handle_2d = None
