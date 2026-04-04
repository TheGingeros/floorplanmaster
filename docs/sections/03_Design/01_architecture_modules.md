# Organizace modulů
Adresářová struktura addonu přímo odráží architektonické vrstvy a vzor MVC. Každý modul má jasně definovanou odpovědnost a minimální závislosti na ostatních.

## Struktura projektu

```
floorplan_master/
├── core/          # MODEL — grafová logika (čistý Python, bez Blender API)
│   ├── ...        # Vrstva 1: planární graf stěn a junctions
│   ├── ...        # Vrstva 2: sémantický graf místností
│   ├── ...        # Vrstva 3: synchronizační modul (topologie mesh + atributy)
│   └── ...        # validační pravidla parametrů
├── operators/     # CONTROLLER — jeden modul na každý funkční požadavek (FP1–FP5)
├── ui/            # VIEW — sidebar panely, GPU overlay, 3D manipulátory, kontextová menu
├── geometry/      # setup Geometry Nodes stromu
├── vendor/        # bundled třetí strany (grafová knihovna, splnění NP1)
└── utils/         # pomocné utility: matematika, konstanty, enumerace
```

## Mapování na MVC

| Složka | MVC role | Architektonická vrstva | Závislost na `bpy` |
| :--- | :--- | :--- | :--- |
| `core/` | Model | Vrstva 1 + 2 | Ne |
| `core/` (sync modul) | Model → View bridge | Vrstva 3 | Ano |
| `operators/` | Controller | — | Ano |
| `ui/` | View (doplňky) | — | Ano |
| `geometry/` | View (setup) | Vrstva 3 | Ano |
| `vendor/` | — | — | Ne |
| `utils/` | — | — | Ne |

- složka `core/` je testovatelná bez Blenderu — záměrně neimportuje `bpy`
- složka `vendor/` obsahuje NetworkX distribuovaný přímo s addonem, uživatel nemusí nic doinstalovat (NP1)
- každý operátor v `operators/` je tenká vrstva volající metody `core/` — logika interakce je striktně oddělena od datového modelu ([2.6 - Modální operátory](../02_Analysis/06_ta_modal_operators.md))
