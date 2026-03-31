# Vrstva 2: Graf místností - Detailní specifikace

Tato sekce definuje sémantickou vrstvu addonu, z matematického hlediska takzvaný duální graf k Vrstvě 1. Zatímco první vrstva řeší pouze čáry a body, Vrstva 2 dává těmto tvarům architektonický význam. Zde se z pouhých uzavřených polygonů stávají plnohodnotné „místnosti“ s vlastní identitou, uživatelským jménem a vizuálními vlastnostmi. Systém spravuje tuto vrstvu primárně automaticky na základě detekovaných cyklů z Vrstvy 1. Změny v topologii (například posunutí zdi) se sem dynamicky propisují, čímž vzniká robustní a nedestruktivní datový model.

## Model uzlu místnosti

Model `Room` představuje vrchol (node) v grafu místností a tvoří páteř uživatelského zážitku. Fyzicky odpovídá jednomu uzavřenému prostoru. Zásadním architektonickým rozhodnutím je zde oddělení perzistentního `id` (které definuje identitu místnosti a nemění se ani při drastické změně tvaru) a `cycle_id` (které ukazuje na aktuální topologickou hranici z Vrstvy 1). Tento model v sobě zároveň agreguje veškerá vizuální a sémantická metadata (barvy, materiály, výpočty plochy), ze kterých následně Vrstva 3 generuje finální 3D podlahy a stropy v Blenderu.

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

## Model hrany sousedství

Model `Adjacency` reprezentuje hranu (edge) v grafu místností. Na rozdíl od strukturálního grafu zde hrana neznamená fyzickou zeď, ale logické „propojení“ či „sousedství“ dvou prostorů. Tento model je kritický pro architektonickou analýzu a definuje propustnost celého půdorysu. Určuje nejen to, zda dvě místnosti sdílejí stěnu, ale jakého typu je jejich propojení (např. dveře, otevřený průchod). Právě díky typu `stairs` umožňuje tento model vytvářet logické vazby i mimo vlastní 2D rovinu a propojovat místnosti napříč různými podlažími.

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

## Operace grafu místností

Třída `RoomGraph` slouží jako hlavní rozhraní pro dotazování a manipulaci se sémantickými daty. Na rozdíl od nízkoúrovňových operací v první vrstvě se zde řeší architektonická logika. Kromě standardní správy životního cyklu místností (jejich automatické zakládání při detekci cyklu a aktualizace jejich vypočtených vlastností) poskytuje třída výkonné analytické nástroje. Umožňuje například hledat nejkratší průchozí cestu budovou (využitím Dijkstrova algoritmu přes hrany sousedství) nebo okamžitě detekovat, které místnosti přiléhají k exteriéru.

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