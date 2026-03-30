# Organizace modulů
Fyzická organizace zdrojového kódu FloorPlanMaster není jen otázkou vizuálního pořádku, ale striktně zrcadlí definovanou třívrstvou architekturu a vzor MVC. Hlavním cílem této adresářové struktury je fyzické oddělení závislostí a zabránění prolínání matematické logiky s uživatelským rozhraním.

Jádro celého systému – čistě datový Model – je izolováno ve složce core/. Tento kód obsahuje Vrstvu 1 a 2, je napsaný v čistém Pythonu a záměrně neobsahuje žádné přímé volání Blender API. Díky tomu je nezávislý a lze jej ověřovat pomocí automatizovaných testů (tests/). Veškerá interakce s prostředím Blenderu je vyčleněna do specializovaných balíčků: uživatelské vstupy a logika nástrojů (Controller) žijí v operators/, vizuální rozhraní v ui/ a most pro překlad dat do 3D sítě (Vrstva 3 a View) zajišťuje balíček geometry/. Univerzální výpočty a pomocné funkce, které nepotřebují znát celkový kontext aplikace, jsou centralizovány v utils/.

Díky této modulární koncepci se přesně ví, kam sáhnout – pokud se mění chování nástroje Tužka, upravuje se operátor, pokud se přidává výpočet objemu střechy, rozšiřuje se jádro, a tyto změny se navzájem nijak neohrožují.

## Reprezentace organizace modulů
```
floorplanmaster/
│
├── __init__.py                       # Registrace addonu a vstupní bod
│
├── core/
│   ├── __init__.py
│   ├── structural_graph.py           # Vrstva 1: Operace grafu NetworkX
│   ├── room_graph.py                 # Vrstva 2: Sémantický graf místností
│   └── parameters.py                 # Definice parametrů a validace
│
├── geometry/
│   ├── __init__.py
│   ├── attribute_sync.py             # Vrstva 3: Synchronizace do pojmenovaných atributů
│   ├── geometry_nodes_setup.py       # Vytvoření stromu uzlů GN
│   └── bmesh_utils.py                # Nízkoúrovňové operace geometrie
│
├── operators/
│   ├── __init__.py
│   ├── pencil_tool.py                # FP1: Modální operátor kreslení
│   ├── finalize_tool.py              # FP4: Finalizace geometrie
│   ├── edit_room.py                  # Operátor úpravy místnosti
│   └── context_menu.py               # FP5: Kontextová nabídka
│
├── ui/
│   ├── __init__.py
│   ├── properties.py                 # Panely vlastností UI
│   ├── menus.py                      # Integrace hlavní nabídky
│   └── manipulators.py               # FP6: 3D manipulátory/rukojeti
│
├── utils/
│   ├── __init__.py
│   ├── snapping.py                   # Systém přichycování (osa, bod, mřížka)
│   ├── validation.py                 # Validace topologie a geometrie
│   ├── calculations.py               # Výpočty plochy, objemu, vzdálenosti
│   ├── constants.py                  # Konstanty a výchozí hodnoty
│   └── serialization.py              # Ukládání/načítání půdorysů
│
└── tests/
    ├── test_structural_graph.py
    ├── test_room_graph.py
    ├── test_operators.py
    └── test_calculations.py
```