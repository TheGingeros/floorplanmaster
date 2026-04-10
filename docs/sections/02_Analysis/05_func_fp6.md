# FP6 - Interaktivní 3D manipulátory
Interaktivní 3D manipulátory nahrazují ruční zadávání hodnot přímou geometrickou manipulací v prostoru: uživatel chytí barevné táhlo přímo u prvku a tažením myši mění jeho rozměry nebo výšku. Implementace využívá rozhraní `bpy.types.Gizmo` a `GizmoGroup`.
## Základ požadavku - should have:
- **Interaktivní manipulátor** - místo zadávání úpravy do panelu může uživatel chytit barevnouo šipku přímo u zdi a táhnout s ní hahoru
- využití rozhraní bpy.types.Gizmo a GizmoGroup 