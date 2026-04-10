# 3.5 Návrh uživatelského rozhraní (UI a UX)
Tato sekce obaluje definované funkce (kapitola 3.4) vizuálním a interaktivním rozhraním — popisuje, kde se addon v Blender prostředí fyzicky vyskytuje, jak uživatel jeho funkce ovládá a jakou vizuální zpětnou vazbu dostává. Návrh se opírá o zavedené vzory z existujících architektonických nástrojů: Archimesh a Archipack (N-panel s parametry, gizmo manipulace), AutoCAD (klávesové zkratky pro kreslení, HUD s rozměry) a SketchUp (okamžitá vizuální zpětná vazba při kreslení). Blender mechanismy nutné k realizaci těchto vzorů — RNA datový most, Gizmo API, draw_handler, kontextová menu — jsou podrobně rozebrány v [technické analýze UI](../02_Analysis/06_ta_ui.md) a [analýze UI vzorů](../02_Analysis/06_ta_ui_patterns.md).

Addon se vyskytuje na čtyřech místech Blender prostředí. Každé místo má odlišnou roli odpovídající přirozenému způsobu, jakým uživatelé Blenderu pracují:

| Oblast | Role v addonu | Sekce |
| :--- | :--- | :--- |
| **Toolbar (T-panel)** | Aktivace modálního nástroje Pencil Tool | [3.5.1 Toolbar](./05_ui_ux_toolbar.md) |
| **N-panel (Sidebar)** | Správa prvků, parametrické úpravy, globální nastavení | [3.5.2 N-panel](./05_ui_ux_npanel.md) |
| **Klávesové zkratky** | Urychlení nejčastějších akcí bez přepnutí pohledu | [3.5.3 Klávesové zkratky](./05_ui_ux_shortcuts.md) |
| **Viewport UI** | Vizuální zpětná vazba: HUD, kóty, gizmos, barevné odlišení místností | [3.5.4 Viewport UI](./05_ui_ux_viewport.md) |
| **Kontextová nabídka** | Rychlý přístup k akcím závislým na vybraném prvku | [3.5.5 Kontextová nabídka](./05_ui_ux_context_menu.md) |

## [Toolbar (T-panel)](./05_ui_ux_toolbar.md)

## [N-panel](./05_ui_ux_npanel.md)

## [Klávesové zkratky](./05_ui_ux_shortcuts.md)

## [Viewport UI](./05_ui_ux_viewport.md)

## [Kontextová nabídka](./05_ui_ux_context_menu.md)
