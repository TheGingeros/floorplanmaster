# Vrstva 1: Strukturální graf - Detailní specifikace
Tato sekce definuje nízkoúrovňové datové jádro addonu. Vrstva 1 (Strukturální graf) je čistě matematická reprezentace půdorysu postavená na knihovně NetworkX. Nemá ponětí o místnostech ani o 3D geometrii – vnímá prostor pouze jako množinu bodů (uzlů) spojených úsečkami (hranami). Striktní dodržování pravidel v této vrstvě je naprosto kritické, protože na planaritě a validitě tohoto grafu závisí veškeré další výpočty, zejména následná detekce uzavřených prostorů ve Vrstvě 2.

## Model uzlu propojovacího bodu
Model `Junction` reprezentuje vrchol (node) v topologickém grafu. Fyzicky odpovídá místu, kde stěna začíná, končí, nebo kde se setkává s jinými stěnami (roh, T-křižovatka). Aby byla zaručena matematická planarita grafu (2D průmět bez prostorových klamů), jsou souřadnice uzlu striktně dvoudimenzionální (x, y). Slouží také jako primární záchytný bod pro algoritmy přichycování (snapping).

```python
# Propojovací bod (uzel ve vrstvě 1)
Junction:
  - id: UUID                    # Jedinečný identifikátor (např. "j_001")
  - position: (x: float, y: float)
    * Striktní 2D souřadnice pro planární graf
    * Při zápisu do Blender sítě (BMesh) se osa Z implicitně doplňuje jako 0.0
  - snap_priority: int          # Pro prioritu algoritmu přichycování
  - custom_data: dict           # Uživatelem definovaná metadata
    * created_at: timestamp
    * notes: string (nepovinné)
```

**Omezení**:
- Pozice musí být jedinečná (žádné duplicitní propojovací body)
- Souřadnice by měly spadat do hranic scény
- Typ propojovacího bodu (roh, T, křížení) se určuje podle připojených hran

## Model hrany stěny
Model `Wall` reprezentuje hranu (edge) propojující právě dva existující uzly. Zatímco z pohledu grafové logiky jde o abstraktní spojnici, tento datový model v sobě zapouzdřuje klíčové parametrické vlastnosti (tloušťku, výšku, výřezy pro okna a dveře). Tato metadata si stěna nese s sebou, dokud nejsou ve Vrstvě 3 přeložena pro Geometry Nodes. Návrh striktně dodržuje pravidla prostého grafu.

```python
# Stěna (hrana ve vrstvě 1)
Wall:
  - id: UUID                     # Jedinečný identifikátor (např. "w_001")
  - junction_start: UUID         # Odkaz na počáteční uzel propojovacího bodu
  - junction_end: UUID           # Odkaz na koncový uzel propojovacího bodu
  
  # Parametrické vlastnosti stěny
  - thickness: float             # Šířka stěny v aktuální jednotce (výchozí: 0.2m)
  - height: float                # Výška stěny (výchozí: 3.0m)
  - offset: (x: float, y: float) # Posun od střední čáry (pro asymetrické stěny)
  
  # Materiál a vzhled
  - material_id: str             # Identifikátor materiálu
  - color: (r: float, g: float, b: float, a: float)
  
  # Komponenty stěny (otvory)
  - windows: list[Window]        # Okna na této stěně
  - doors: list[Door]            # Dveře na této stěně
  
  # Metadata
  - is_external: bool            # Pravda, pokud je stěna vnějškem
  - is_bearing: bool             # Nosná/zatěžující stěna
  - custom_data: dict
```

**Omezení**:
- `junction_start` != `junction_end`
- `thickness` > 0
- `height` > 0
- Mezi dvěma konkrétními uzly může vést maximálně jedna hrana (odpovídá prostému grafu).

## Operace strukturálního grafu
Třída `StructuralGraph` slouží jako jediné autoritativní API pro manipulaci s topologií podlaží. Bezpečně zapouzdřuje přímá volání knihovny NetworkX. Poskytuje vysokoúrovňové metody pro CRUD operace (vytváření a mazání uzlů/hran) a zajišťuje, že graf po každé změně zůstane validní. Největší přidanou hodnotou této třídy je sekce analýzy topologie, která dokáže na zavolání identifikovat cykly potřebné pro detekci místností.

```python
class StructuralGraph:
  
  # Propojovací body (Vrcholy)
  add_junction(position: (x, y), **kwargs) → Junction
  remove_junction(junction_id: UUID)
  get_junction(junction_id: UUID) → Junction
  get_all_junctions() → list[Junction]
  find_junctions_near(position: (x, y), radius: float) → list[Junction]
  
  # Stěny (Hrany)
  add_wall(junction_start: UUID, junction_end: UUID, **properties) → Wall
  remove_wall(wall_id: UUID)
  get_wall(wall_id: UUID) → Wall
  get_walls_connected_to(junction_id: UUID) → list[Wall]
  get_all_walls() → list[Wall]
  
  # Analýza topologie
  get_cycles() → list[list[UUID]]           # Najít všechny uzavřené prostory
  get_planar_faces() → list[Face]           # Planární vkládací plochy
  is_planar() → bool                        # Validovat planaritu
  validate_topology() → (bool, list[str])   # Validovat a vrátit chyby
  
  # Geometrie
  calculate_wall_length(wall_id: UUID) → float
  calculate_wall_angle(wall_id: UUID) → float  # V radiánech
```