# Organizace modulů

Fyzická organizace zdrojového kódu FloorPlanMaster není jen otázkou vizuálního pořádku, ale striktně zrcadlí definovanou třívrstvou architekturu a vzor MVC. Hlavním cílem této adresářové struktury je fyzické oddělení závislostí a zabránění prolínání matematické logiky s uživatelským rozhraním.

Jádro celého systému – čistě datový Model – je izolováno ve složce `core/`. Tento kód obsahuje zastřešující hierarchii budovy i samotnou Vrstvu 1 a 2. Je napsaný v čistém Pythonu a záměrně neobsahuje žádné přímé volání Blender API. Díky tomu je nezávislý a lze jej ověřovat pomocí automatizovaných testů (`tests/`). 

Veškerá interakce s prostředím Blenderu je vyčleněna do specializovaných balíčků: uživatelské vstupy a logika nástrojů (Controller) žijí v `operators/`, vizuální rozhraní v `ui/` a most pro překlad dat do 3D sítě (Vrstva 3 a View) zajišťuje balíček `geometry/`. Univerzální výpočty a pomocné funkce, které nepotřebují znát celkový kontext aplikace, jsou centralizovány v `utils/`.

Díky této modulární koncepci se přesně ví, kam sáhnout – pokud se mění chování nástroje Tužka, upravuje se operátor, pokud se mění logika přepínání pater, upravuje se kontejner budovy, a tyto změny se navzájem nijak neohrožují.

## Reprezentace organizace modulů

```text
floorplanmaster/
│
├── __init__.py                       # Registrace addonu a vstupní bod
│
├── core/
│   ├── __init__.py
│   ├── building.py                   # Kontejner projektu (správa podlaží a aktivního kontextu)
│   ├── floor.py                      # Izolovaný 2D vesmír pro konkrétní podlaží
│   ├── structural_graph.py           # Vrstva 1: Operace grafu NetworkX
│   ├── room_graph.py                 # Vrstva 2: Sémantický graf místností
│   └── parameters.py                 # Definice parametrů a validace
│
├── geometry/
│   ├── __init__.py
│   ├── attribute_sync.py             # Vrstva 3: Dávková synchronizace pojmenovaných atributů
│   ├── geometry_nodes_setup.py       # Vytvoření a přiřazení stromů uzlů GN pro podlaží
│   └── bmesh_utils.py                # Nízkoúrovňové zrcadlení Python grafů do sítě
│
├── operators/
│   ├── __init__.py
│   ├── pencil_tool.py                # FP1: Modální operátor kreslení (v aktivním patře)
│   ├── building_ops.py               # FP3: Operátory pro správu pater (přidat, smazat, aktivovat)
│   ├── finalize_tool.py              # FP4: Finalizace geometrie (zapečení celé budovy)
│   ├── edit_room.py                  # Operátor úpravy parametrů místnosti
│   └── context_menu.py               # FP5: Kontextová nabídka (využívající raycast do pater)
│
├── ui/
│   ├── __init__.py
│   ├── properties.py                 # Panely vlastností UI (včetně správce podlaží)
│   ├── menus.py                      # Integrace hlavní nabídky Blenderu
│   ├── manipulators.py               # FP6: 3D manipulátory (uzamčené do roviny XY daného patra)
│   └── hud_dimensions.py             # FP7: Automatické kótování a překryvná grafika ve viewportu
│
├── utils/
│   ├── __init__.py
│   ├── snapping.py                   # Systém přichycování (striktně promítnutý do 2D)
│   ├── validation.py                 # Bezpečnostní validace topologie a geometrie
│   ├── calculations.py               # Výpočty plochy, objemu a vzdáleností
│   ├── constants.py                  # Konstanty a výchozí hodnoty
│   └── serialization.py              # Interní serializace hierarchie budovy do JSON
│
└── tests/
    ├── test_building_hierarchy.py    # Nové: Testování izolace dat mezi patry
    ├── test_structural_graph.py
    ├── test_room_graph.py
    ├── test_operators.py
    └── test_calculations.py
```