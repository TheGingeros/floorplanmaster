# 3.2 Specifikace datových modelů
Zatímco předchozí kapitola definovala procesy a tok dat (architekturu MVC), tato sekce představuje exaktní „slovník“ celého addonu. Definuje fyzické struktury, pravidla a hranice, ve kterých se data mohou pohybovat. Slouží jako striktní programátorský kontrakt mezi matematickým jádrem v Pythonu a 3D prostředím Blenderu.

Abychom předešli zhroucení planárních algoritmů při navrhování komplexních objektů, neukládají se data do jedné ploché struktury, ale podléhají přísné hierarchii podlaží. Na samém vrcholu stojí zastřešující model Budovy (Správce podlaží), který izoluje jednotlivá patra do zcela nezávislých 2D vesmírů. Teprve uvnitř těchto pater žijí naše tři známé vrstvy: Strukturální graf uchovávající 2D topologii (Vrstva 1), Graf místností definující sémantiku a sousedství (Vrstva 2) a Pojmenované atributy sloužící jako optimalizovaný číselný most pro grafickou kartu (Vrstva 3).

Následující specifikace neslouží jen jako přehled proměnných. Detailně definuje povolené datové typy, API metody, a především tvrdá validační omezení, která garantují, že uživatel nemůže vytvořit architektonicky neplatný stav.

## Hierarchie budovy (Zastřešující modely)

Tato nejvyšší úroveň organizuje jednotlivé grafy tak, aby byla zachována 2D planarita.

### Model budovy
```python
Building:
  - id: UUID
  - name: str                    # Název projektu
  - floors: list[Floor]          # Seznam podlaží (seřazený odspodu nahoru)
  - active_floor_index: int      # Index patra, které uživatel aktuálně upravuje
  - project_settings: dict       # Globální nastavení (např. výchozí výška stěn)
```

### Model podlaží
```python
Floor:
  - id: UUID
  - name: str                    # např. "Přízemí", "1. Patro"
  - elevation: float             # Z-výška, na které podlaží začíná (např. 0.0m, 3.2m)
  - is_visible: bool             # Stav zobrazení v UI/Viewportu
  
  # Datové jádro podlaží (izolované instance)
  - structural_graph: StructuralGraph  # Vlastní Vrstva 1
  - room_graph: RoomGraph              # Vlastní Vrstva 2
```

## Vrstva 1: Strukturální graf - Detailní specifikace

### Model uzlu propojovacího bodu

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

### Model hrany stěny

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

### Operace strukturálního grafu

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

---

## Vrstva 2: Graf místností - Detailní specifikace

### Model uzlu místnosti

```python
# Místnost (uzel ve vrstvě 2)
Room:
  - id: UUID                     # Perzistentní identifikátor místnosti (např. "r_001")
  - cycle_id: UUID               # Odkaz na cyklus z vrstvy 1
    * Mapuje tuto místnost na její ohraničující cyklus stěn
    * Změny geometrie nezmění room_id
  
  # Identita místnosti
  - name: str                    # Uživatelsky přívětivé jméno (např. "Obývací pokoj")
  - type: str                    # Klasifikace typu místnosti
    * "residential", "commercial", "circulation", atd.
  
  # Geometrie (vypočítaná)
  - area: float                  # Čtvereční metry (automaticky vypočítáno)
  - perimeter: float             # Metry (automaticky vypočítáno)
  - centroid: (x: float, y: float)  # Střed místnosti (automaticky vypočítáno)
  - vertices: list[(x, y)]       # Hraniční vrcholy v pořadí
  
  # 3D vlastnosti
  - height: float                # Výška místnosti
  - floor_level: float           # z-souřadnice podlahy
  
  # Materiály a vzhled
  - wall_color: (r, g, b, a)     # Výchozí barva stěny
  - floor_material: str          # Identifikátor materiálu
  - floor_color: (r, g, b, a)    # Barva podlahy
  - ceiling_material: str        # Identifikátor materiálu stropu
  - ceiling_color: (r, g, b, a)  # Barva stropu
  
  # Analýza a metadata
  - is_enclosed: bool            # Pravda, pokud je zcela uzavřena
  - perimeter_walls: list[UUID]  # ID stěn tvořících hranici
  - adjacent_rooms: list[UUID]   # ID připojených místností
  - custom_data: dict            # Uživatelem definované vlastnosti
    * occupancy_class: str
    * fire_rating: str
    * accessibility_type: str
    * atd.
```

**Omezení**:
- `id` je perzistentní (nikdy se nemění během úpravy)
- `cycle_id` odkazuje na platný cyklus z vrstvy 1
- `area` se vypočítá z hraničních vrcholů
- `height` > 0
- Minimálně 3 vrcholy (minimální trojúhelník)

### Model hrany sousedství

```python
# Sousedství (hrana v grafu místností)
Adjacency:
  - room_a: UUID                 # První místnost
  - room_b: UUID                 # Druhá místnost
  - shared_wall: UUID            # ID stěny z vrstvy 1 (sdílená hranice)
  
  # Typ připojení
  - connection_type: str
    * "closed": stěna bez otvorů
    * "door": průchod dveřmi
    * "window": vizuální připojení oknem
    * "passage": otevřený průchod
    * "stairs": vertikální logické propojení do jiného podlaží
  
  # Otvory na tomto připojení
  - openings: list[UUID]         # ID dveří/oken
  - total_opening_width: float   # Celková šířka otvorů
```

### Operace grafu místností

```python
class RoomGraph:
  
  # Místnosti (Vrcholy)
  add_room(cycle_id: UUID, **properties) → Room
  remove_room(room_id: UUID)
  get_room(room_id: UUID) → Room
  get_all_rooms() → list[Room]
  
  # Vlastnosti místnosti (Aktualizace)
  update_room_properties(room_id: UUID, **properties)
    # Přepočítá plochu, obvod, pokud se geometrie změnila
  
  # Sousedství (Hrany)
  add_adjacency(room_a: UUID, room_b: UUID, shared_wall: UUID) → Adjacency
  get_adjacent_rooms(room_id: UUID) → list[Adjacency]
  get_adjacency(room_a: UUID, room_b: UUID) → Adjacency or None
  
  # Analýza a dotazy
  get_rooms_of_type(type: str) → list[Room]
  calculate_total_area() → float       # Suma všech oblastí místností
  get_circulation_path(room_a: UUID, room_b: UUID) → list[UUID]
    # Použije Dijkstru k nalezení nejkratší cesty cirkulace
  
  # Konektivita
  get_external_rooms() → list[Room]    # Místnosti dotýkající se exteriéru
  get_interior_rooms() → list[Room]    # Místnosti, které se nedotýkají exteriéru
  get_rooms_by_aspect_ratio() → dict   # Analyzovat tvary místností
```

---

## Vztah: Vrstva 1 ↔ Vrstva 2

### Mapování

```
Vrstva 1 (Strukturální)          Vrstva 2 (Místnost)
┌─────────────────┐           ┌──────────────┐
│  Junction (v)   │ ──────┐   │              │
│  Junction (v)   │       ├──→│   Místnost   │
│  Junction (v)   │ ──┐   │   │              │
│  Stěna (e)      │───┼───→│   (cyklus + ID) │
│  Stěna (e)      │   │   │   │              │
│  ...            │───┼───┘   └──────────────┘
│  (cykly)        │───┘       │  Sousedství  │
│                 │           │  (sdílená    │
│                 │           │   stěna)     │
└─────────────────┘           └──────────────┘
```

### Pravidla synchronizace

1. **Detekce cyklu** (automatické)
   - Když je stěna přidána do vrstvy 1 → NetworkX detekuje nové cykly
   - Nové cykly → Vytvoří nové místnosti ve vrstvě 2
   - Cyklus odstraněn → Odstraní odpovídající místnost (varování uživateli)

2. **Propagace vlastností** (jednosměrná z 1 na 2)
   - Tloušťka stěny vrstva 1 → Použita Geometry Nodes pro 3D šířku
   - Výška stěny vrstva 1 → Použita pro 3D extrusi
   - Materiál stěny vrstva 1 → Výchozí pro hranici místnosti

3. **Aktualizace geometrie** (jednosměrná z 1 na 2)
   - Stěna přesunuta → Cyklus se změní → Plocha místnosti se přepočítá
   - Propojovací bod přidán/odstraněn → Topologie se změní → Místnosti se mohou rozdělit/sloučit
   - ID místnosti přetrvá po celou dobu

---

## Vrstva 3: Pojmenované atributy - Kompletní specifikace

### Tabulka atributů

| Název atributu | Doména | Typ | Výchozí | Použití | Spouštěč aktualizace |
|---|---|---|---|---|---|
| `junction_id` | Vertex | Integer | 0 | Unikátní číselný index propojovacího bodu | Vytvoření propojovacího bodu |
| `wall_id` | Edge | Integer | 0 | Unikátní číselný index stěny | Vytvoření stěny |
| `wall_thickness` | Edge | Float | 0.2 | Šířka stěny (m) | Změna tloušťky stěny |
| `wall_height` | Edge | Float | 3.0 | Výška stěny (m) | Změna výšky stěny |
| `wall_material_id` | Edge | Integer | 0 | Číselný index materiálu | Změna materiálu |
| `wall_offset_x` | Edge | Float | 0.0 | Asymetrický posun | Změna posunu |
| `wall_offset_y` | Edge | Float | 0.0 | Asymetrický posun | Změna posunu |
| `room_id` | Face | Integer | 0 | Unikátní číselný index místnosti | Vytvoření místnosti |
| `room_area` | Face | Float | 0.0 | Vypočítaná plocha (m²) | Změna geometrie místnosti |
| `room_perimeter` | Face | Float | 0.0 | Vypočítaný obvod | Změna geometrie místnosti |
| `room_type` | Face | Integer | 0 | Číselný index klasifikace místnosti | Změna typu |
| `floor_material_id` | Face | Integer | 0 | Číselný index materiálu podlahy | Změna materiálu podlahy |
| `floor_color` | Face | Color | (0.8, 0.8, 0.8, 1) | RGBA barva podlahy | Změna barvy |
| `ceiling_material_id` | Face | Integer | 0 | Číselný index materiálu stropu | Změna materiálu stropu |
| `is_room_enclosed` | Face | Boolean| True | Stav místnosti | Změna geometrie místnosti |

*(Poznámka k ID: Zatímco Vrstva 1 a 2 v Pythonu používají UUID stringy pro spolehlivou identifikaci, před zápisem do Vrstvy 3 se tato UUID mapují na unikátní Integery, protože Geometry Nodes jsou optimalizovány pro rychlé výpočty nad celými čísly).*

**Vlastní vlastnosti objektu (Custom Properties)**:
Celoobjektová metadata se neukládají jako pojmenované atributy sítě, ale jako standardní Custom Properties na samotném Blender objektu.
- `unit_system` (String): "m", "cm", "ft" - Systém měření
- `addon_version` (String): "1.0" - Pro kompatibilitu souboru
- `structure_version` (Int): Čítač pro zneplatnění mezipaměti GN

### Formát serializace

```python
# Slovník Pythonu (reprezentace dat připravených pro síť)
attributes_dict = {
    "vertex": {
        "junction_id": [idx_v0, idx_v1, ...],
    },
    "edge": {
        "wall_id": [idx_e0, idx_e1, ...],
        "wall_thickness": [thick_e0, thick_e1, ...],
        # ...
    },
    "face": {
        "room_id": [idx_f0, idx_f1, ...],
        "room_area": [area_f0, area_f1, ...],
        "floor_color": [(r,g,b,a), (r,g,b,a), ...]
    }
}

# Zápis do Blender objektu
mesh = bpy.data.meshes["FloorPlan"]
obj = bpy.data.objects["FloorPlan"]

# 1. Pojmenované atributy sítě (pro Geometry Nodes)
mesh.attributes["junction_id"].data.foreach_set("value", attributes_dict["vertex"]["junction_id"])
mesh.attributes["room_id"].data.foreach_set("value", attributes_dict["face"]["room_id"])

# 2. Celoobjektová metadata (Custom Properties)
obj["unit_system"] = "m"
obj["structure_version"] = 42
```

### Časování synchronizace

- **Čtení**: Geometry Nodes drivers čtou atributy každý frame
- **Zápis**: Python addon nejprve synchronizuje novou topologii přes BMesh (vytvoří/smaže vertexy a hrany) a až následně na ně zapíše/aktualizuje atributy.
- **Frekvence**: Dávkové zápisy za operaci (ne za prvek)
- **Validace**: Kontrola konzistence atributů po zápisu

---

## Pravidla validace parametrů

### Parametry stěny

```
thickness: 0.05 ≤ value ≤ 1.0 (metry)
height: 1.0 ≤ value ≤ 10.0 (metry)
angle: 0° ≤ value ≤ 180°
offset: -0.5 ≤ value ≤ 0.5 (metry)
```

### Parametry místnosti

```
area: > 1.0 (m²)  # Minimální místnost 1 m²
height: > 0
perimeter: > 4.0 (alespoň 2x2 čtverec)
aspect_ratio: 0.1 ≤ (width/length) ≤ 10.0  # Rozumné tvary
```

### Převod jednotek

```python
UNIT_CONVERSIONS = {
    "m": 1.0,        # Metry (základní jednotka)
    "cm": 0.01,
    "mm": 0.001,
    "ft": 0.3048,
    "in": 0.0254,
}

# Příklad: Převést 3m na stopy
value_in_m = 3.0
value_in_ft = value_in_m / UNIT_CONVERSIONS["ft"]  # ~9.84 ft
```