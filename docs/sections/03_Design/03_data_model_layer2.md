# Vrstva 2: Graf místností
Sémantická vrstva addonu, matematicky duální graf k Vrstvě 1. Dává topologickým tvarům architektonický význam — z uzavřených polygonů se stávají místnosti s identitou, názvem a vizuálními vlastnostmi. Vrstva je spravována primárně automaticky na základě detekovaných cyklů z Vrstvy 1 ([2.6 - NRG](../02_Analysis/06_ta_nrg.md), [2.6 - Hybridní spojení](../02_Analysis/06_ta_hybrid_connection.md)).

## Diagram tříd

```mermaid
classDiagram
    class RoomType {
        <<enumeration>>
        LIVING
        TECHNICAL
        CIRCULATION
    }
    class ConnectionType {
        <<enumeration>>
        CLOSED
        DOOR
        WINDOW
        PASSAGE
    }
    class Room {
        +UUID id
        +UUID cycle_id
        +str name
        +RoomType room_type
        +float area
        +float perimeter
        +float centroid_x
        +float centroid_y
        +float height
        +str wall_color
        +int floor_material
        +int ceiling_material
    }
    class Adjacency {
        +UUID room_a
        +UUID room_b
        +UUID shared_wall
        +ConnectionType connection_type
        +list openings
    }
    class RoomGraph {
        +add_room(cycle_id) Room
        +remove_room(id) void
        +update_room_geometry(id) void
        +get_room(id) Room
        +get_all_rooms() list
        +get_rooms_by_type(type) list
        +add_adjacency(a, b, wall) Adjacency
        +get_neighbors(room_id) list
        +are_adjacent(a, b) bool
        +total_area(type) float
        +find_external_rooms() list
    }
    RoomGraph "1" o-- "0..*" Room : obsahuje
    RoomGraph "1" o-- "0..*" Adjacency : obsahuje
    Adjacency "1" --> "2" Room : propojuje
    Room --> RoomType : klasifikace
    Adjacency --> ConnectionType : typ propojení
```

## Omezení

### Místnost (Room)
- `id` je perzistentní — i když uživatel změní tvar místnosti k nepoznání, ID a sémantická metadata (název, materiály) přetrvávají, dokud nedojde k úplnému rozpojení cyklu
- `cycle_id` musí odkazovat na platný cyklus ve Vrstvě 1
- minimálně 3 hraniční vrcholy
- plocha a obvod musí splňovat validační pravidla (viz [rodičovský soubor](./03_data_model.md))

### Sousedství (Adjacency)
- sousedství vzniká automaticky při detekci sdílené stěny mezi dvěma cykly
- jedna dvojice místností může sdílet nejvýše jednu hranu sousedství (prostý graf místností)

## Operace grafu místností
Graf slouží jako hlavní rozhraní pro dotazování a manipulaci se sémantickými daty. Operace jsou seskupeny do tří skupin:

- **Místnosti (CRUD)**: automatické zakládání z cyklů, odebrání při zániku cyklu, aktualizace vypočítaných vlastností (plocha, obvod, centroid), dotazy podle ID nebo typu
- **Sousedství**: automatické přidání při detekci sdílené stěny, dotaz na sousedy dané místnosti, test sousedství dvou místností
- **Analýza a dotazy**: celková plocha (volitelně dle typu), identifikace vnějších a vnitřních místností, analýza poměrů stran
