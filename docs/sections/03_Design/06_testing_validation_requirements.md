# Pokrytí požadavků

Kontrolní seznam ověřující pokrytí každého must-have i should-have funkčního prvku návrhem funkce (kapitola 3.4), datovým modelem (kapitola 3.3) a architekturou (kapitola 3.2), včetně pokrytí nefunkčních požadavků.

## Pokrytí must-have prvků

Následující seznam ověřuje, že každý must-have prvek MVP (kapitola 3.1) je plně pokryt návrhem funkce (kapitola 3.4), datovým modelem (kapitola 3.3) a architekturou (kapitola 3.2).

| Požadavek | Must-have prvek | Navrhující sekce | Datový model | Vrstva |
| :--- | :--- | :--- | :--- | :--- |
| FP1 | Modální operátor pro kreslení bodů | FP1 — stavový automat | Junction, Wall (L1) | Controller → L1 → L2 → L3 |
| FP1 | Snap na existující junction | FP1 — snapping | Junction.position (L1) | Controller |
| FP1 | Zápis do L1 až po potvrzení | FP1 — interakce s modelem | — | Controller → L1 |
| FP2 | Dynamická parametrická stěna | FP2 — parametry stěny | Wall.thickness/height (L1) | L1 → L3 → GN |
| FP2 | Vložení pravoúhlé místnosti | FP2 — vložení místnosti | Junction × 4, Wall × 4 (L1) | Controller → L1 → L2 → L3 |
| FP2 | Vazba otvoru na stěnu | FP2 — vazba otvorů | Wall.openings (L1) | L1 → L3 → GN |
| FP2 | GN Mesh Boolean — vizuální výřez otvorů | FP2 — otvory GN Mesh Boolean | Wall.openings, poziční atributy (L3) | L1 → L3 → GN |
| FP3 | Automatická detekce místností | FP3 — detekce cyklů | Room (L2) z cyklu (L1) | L1 → L2 |
| FP3 | Zobrazení plochy místnosti | FP3 — prostorová data | Room.area (L2) | L2 → L3 → GN |
| FP4 | Aplikace GN modifikátoru | FP4 — stavový automat | L3 → statická mesh | View |

Každý must-have prvek je pokryt jednou návrhovou sekcí, má definovaný datový model a průchoditelný tok dat napříč vrstvami.

## Pokrytí should-have prvků

| Požadavek | Should-have prvek | Navrhující sekce | Datový model | Vrstva |
| :--- | :--- | :--- | :--- | :--- |
| FP5 | Kontextová nabídka s akcemi | FP5 — raycast + akce | L3 raycast → L1/L2 | Controller |
| FP6 | Gizmo pro tloušťku/výšku/posun | FP6 — typy manipulátorů | Wall.thickness/height, Junction.position | Controller → L1 → L3 |
| FP7 | GPU overlay kóty | FP7 — datový pipeline | L1 délky, L2 area + centroid | View (BLF) |

## Pokrytí nefunkčních požadavků

| Požadavek | Jak je pokryt návrhem |
| :--- | :--- |
| NP1 — Architektura a technologie | Geometry Nodes jako výpočetní jádro (L3 → GN); Python jako manažer (L1, L2); oddělení vizuální a aplikační logiky (třívrstvá architektura, kapitola 3.2); NetworkX jako deklarovaná wheel závislost |
| NP2 — Výkon a nedestruktivnost | Jednosměrný tok dat bez cyklických přepočtů; změna atributu nevyvolá detekci cyklů (pouze L3 fáze 2); dvoufázová synchronizace minimalizuje overhead; Undo přes Blender snapshot |
| NP3 — Použitelnost a UX | N-panel se standardními UILayout komponentami; klávesové zkratky z Blender/AutoCAD konvencí; GPU overlay s barevnou sémantikou nativních nástrojů; validační chyby hlášeny pop-overem |
