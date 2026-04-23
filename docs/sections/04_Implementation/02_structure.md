# 4.2 Organizace modulů

Složková struktura projektu přímo reflektuje třívrstvou hybridní architekturu popsanou v návrhu (3.2) a zároveň prosazuje klíčové omezení: žádná vrstva nesmí záviset na vrstvách nad sebou a vrstvy 1 a 2 nesmí mít přímou vazbu na Blender API.

```
src/
├── __init__.py              # addon entry point: register/unregister, graph store
├── core/
│   ├── structural_graph.py  # Vrstva 1 — junction, wall, opening, topologie
│   ├── room_graph.py        # Vrstva 2 — room, adjacency, lazy synchronizace
│   ├── sync.py              # Vrstva 3 — Python grafy → Blender mesh + atributy
│   └── validators.py        # sdílené validační funkce s chybovými kódy
├── operators/               # Blender modální operátory (FP1–FP7)
├── ui/                      # N-panel, overlay manager, selection state, properties
├── geometry/                # Geometry Nodes tree builder
├── utils/
│   ├── constants.py         # výchozí hodnoty, validační limity, výčty
│   └── math_helpers.py      # 2D geometrie, polygon area, centroid, aspect ratio
├── tests/                   # pytest unit testy pro core/ a utils/
└── wheels/                  # bundlované .whl závislosti (networkx)
```

## Závislostní pravidla

Jasná pravidla závislostí jsou přímým důsledkem rozhodnutí popsaného v návrhu. Moduly ve složkách `core/structural_graph.py`, `core/room_graph.py` a celé `utils/` neimportují Blender API nikde — tato část kódové základny je testovatelná standardním pytestem mimo Blender. Synchronizační modul `core/sync.py` a vše ve složkách `operators/`, `ui/` a `geometry/` na Blender API závisí a je spustitelné výhradně uvnitř Blenderu.

Závislostní tok je jednosměrný: operátory volají metody ze `core/`; UI čte data ze `core/` přes sdílenou cache; `geometry/` se stará výhradně o strukturu Geometry Nodes modifikátoru. Zpětný tok neexistuje — žádný modul ve `core/` neimportuje nic z `operators/`, `ui/` ani `geometry/`. Toto pravidlo zabraňuje vzniku cyklických závislostí a udržuje jádro systému testovatelné a přenositelné.

## Testování

Složka `tests/` obsahuje jednotkové testy pro Vrstvu 1, Vrstvu 2, validátory a matematické utility. Testy jsou spustitelné příkazem `pytest` z adresáře `src/` bez jakékoliv závislosti na Blenderu. Každý testovací soubor pokrývá jak standardní scénáře, tak hraniční podmínky — minimální a maximální hodnoty parametrů, duplicitní entity, neplatné topologie. Celkem je k dispozici 124 testovacích případů, přičemž všechny procházejí.
