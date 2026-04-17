# Vztah mezi vrstvami
Všechny tři vrstvy jsou provázány jednosměrným asymetrickým tokem dat: Vrstva 1 (topologie) diktuje obsah Vrstvy 2 (sémantika), a obě společně zásobují Vrstvu 3 (synchronizace), která přenáší data do Blender mesh a spouští Geometry Nodes vizualizaci. Zpětný tok neexistuje.

## Statický pohled — závislosti tříd

```mermaid
flowchart LR
    subgraph V1["VRSTVA 1 — Strukturální"]
        C1["Cyklus stěn<br/>(geometrická hranice)"]:::v1
        C2["Sdílená stěna<br/>(fyzický oddělovač)"]:::v1
    end
    subgraph V2["VRSTVA 2 — Sémantická"]
        R1["Místnost<br/>(metadata + ID)"]:::v2
        R2["Sousedství<br/>(typ propojení)"]:::v2
    end
    subgraph V3["VRSTVA 3 — Synchronizace"]
        A1["Named attributes<br/>(mesh domény)"]:::v3
        A2["Geometry Nodes<br/>(vizualizace)"]:::v3
    end

    C1 -->|"tvoří"| R1
    C2 -->|"definuje"| R2
    V1 -->|"topologie (Phase 1)"| V3
    V2 -->|"sémantika (Phase 2)"| V3
    A1 -->|"řídí"| A2

    classDef v1 stroke:#4a90d9,stroke-width:2px
    classDef v2 stroke:#9b4ad9,stroke-width:2px
    classDef v3 stroke:#d94a4a,stroke-width:2px
    linkStyle default stroke-width:2px
```

## Dynamický pohled — sekvenční diagram

```mermaid
sequenceDiagram
    actor User as Uživatel
    participant Op as Pencil Tool<br/>(Operátor)
    participant L1 as StructuralGraph<br/>(Vrstva 1)
    participant L2 as RoomGraph<br/>(Vrstva 2)
    participant L3 as AttributeSync<br/>(Vrstva 3)
    participant Mesh as Blender Mesh<br/>(Named Attributes)
    participant GN as Geometry Nodes<br/>(View)

    User->>Op: potvrdí stěnu (LMB)
    Op->>L1: add_junction(pos_a)
    Op->>L1: add_junction(pos_b)
    Op->>L1: add_wall(j_a, j_b, thickness, height)
    L1-->>Op: wall_id

    Op->>L2: sync(structural_graph)
    L2->>L1: find_minimal_cycles()
    L1-->>L2: [cycle_1, cycle_2, ...]
    L2->>L2: diff → přidat/odebrat místnosti
    L2-->>Op: updated RoomGraph

    Op->>L3: sync_graph_to_mesh(obj, sg, rg)
    L3->>Mesh: Phase 1 — bmesh vertices + edges + faces
    L3->>Mesh: Phase 2 — named attributes (wall_id, room_area, ...)
    Mesh-->>GN: reevaluace modifikátoru
    GN-->>User: 3D vizualizace stěny
```

Klíčové vzory chování:
- přidání stěny do Vrstvy 1 → detekce nových cyklů → založení nové místnosti ve Vrstvě 2 s perzistentním ID
- odebrání stěny → zánik nebo sloučení cyklů → odebrání nebo sloučení místností
- posun propojovacího bodu → změna tvaru cyklu → přepočet plochy, obvodu a centroidu; ID a metadata zůstávají
- tloušťka a výška stěny (Vrstva 1) → vstupní parametry pro Geometry Nodes přes named attributes (Vrstva 3)
