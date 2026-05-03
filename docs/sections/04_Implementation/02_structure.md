# 4.2 Organizace modulů

Struktura složek vymáhá jednosměrný závislostní tok: jádro systému (grafy, validátory, utility) nezávisí na Blender API, synchronizační vrstva přidává první vazbu na `bpy` a operátory s UI stojí na vrcholu hierarchie. Díky tomu lze jednotkové testy spouštět standardním pytestem bez přítomnosti Blenderu.

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

<!-- ## Závislosní pravidla

Závislosní pravidlo má přímý praktický důsledek: složka s jednotkovými testy importuje výhradně z čistého Python jádra a může být spuštěna standardním pytestem bez přítomnosti Blenderu. Testovatelnost tedy není vedlejším efektem dobrého návrhu, ale přímým důsledkem vymáhaného závislosního pravidla — porušení pravidla se projeví okamžitě jako selhání testů.

Přenositelnost jádra do jiného kontextu — například do exportního skriptu nebo serverového výpočtu bez Blenderu — je pak přímým důsledkem téhož omezení. Oba moduly grafů ani matematické utility neobsahují nic, co by je vázalo na konkrétní hostitelské prostředí. -->

## Testování

Složka s testy pokrývá celé čisté Python jádro: Vrstvu 1, Vrstvu 2, validátory a matematické utility. Každý testovací soubor ověřuje jak standardní scénáře, tak hraniční podmínky — minimální a maximální hodnoty parametrů, duplicitní entity, topologicky neplatné grafy a výpočetně degenerované situace. Celkem je k dispozici přes 190 testovacích případů, přičemž všechny procházejí. Synchronizační vrstva a operátory nejsou pokryty automatickými testy, neboť vyžadují přítomnost Blenderu — jejich správnost je ověřována manuálně přímo v prostředí Blenderu.

