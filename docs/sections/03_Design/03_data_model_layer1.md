# Vrstva 1: Strukturální graf
Vrstva 1 je čistě matematická reprezentace půdorysu. Nemá ponětí o místnostech ani o 3D geometrii — vnímá prostor pouze jako množinu bodů spojených úsečkami v planárním 2D grafu. Na validitě a planaritě tohoto grafu závisí veškeré další výpočty, zejména detekce uzavřených prostorů ve Vrstvě 2 ([2.6 - Strukturální graf](../02_Analysis/06_ta_structural_graph.md)).

## Model propojovacího bodu (Junction)
Reprezentuje vrchol v topologickém grafu — místo, kde stěna začíná, končí nebo se setkává s jinými stěnami (roh, T-křižovatka). Souřadnice jsou striktně dvoudimenzionální pro garantování planarity.

- `id`: unikátní identifikátor
- `position`: $(x, y)$ — 2D souřadnice v prostoru scény; osa Z se doplňuje implicitně
- `snap_priority`: celočíselná priorita pro algoritmus přichycování

**Omezení**:
- pozice musí být v rámci grafu unikátní (žádné duplicitní body na stejných souřadnicích)
- typ propojovacího bodu (roh, T-křižovatka, křížení) se odvozuje z počtu připojených hran

## Model stěny (Wall)
Reprezentuje hranu propojující právě dva existující propojovací body. Zapouzdřuje parametrické vlastnosti, které Vrstva 3 serializuje pro Geometry Nodes.

- `id`: unikátní identifikátor
- `junction_start`: odkaz na počáteční propojovací bod
- `junction_end`: odkaz na koncový propojovací bod
- `thickness`: tloušťka stěny v metrech (výchozí: 0.2)
- `height`: výška stěny v metrech (výchozí: 3.0)
- `material_id`: identifikátor materiálu
- `openings`: seznam otvorů (okna, dveře) s pozicí a rozměry na této stěně
- `is_external`: zda jde o vnější stěnu
- `is_bearing`: zda jde o nosnou stěnu

**Omezení**:
- počáteční a koncový bod musí být různé (`junction_start` ≠ `junction_end`)
- mezi dvěma konkrétními body může vést maximálně jedna stěna (prostý graf)
- tloušťka a výška musí splňovat validační pravidla (viz [rodičovský soubor](./03_data_model.md))

## Operace strukturálního grafu
Graf zapouzdřuje veškerou manipulaci s topologií podlaží. Po každé změně garantuje, že graf zůstane validní. CRUD = create, read, update, delete

- **Propojovací body (CRUD)**:
    - přidání bodu na zadanou pozici
    - odebrání bodu (a všech napojených stěn)
    - vyhledání bodů v okolí dané pozice (pro snapping)
    - získání všech bodů
- **Stěny (CRUD)**:
    - přidání stěny mezi dva body s parametry
    - odebrání stěny
    - získání stěn napojených na konkrétní bod
    - získání všech stěn
- **Analýza topologie**:
    - detekce všech minimálních cyklů (uzavřených prostorů) — klíčová operace pro Vrstvu 2
    - validace planarity grafu
    - celková validace topologie s výčtem chyb
- **Geometrické výpočty**:
    - délka stěny (vzdálenost mezi body)
    - úhel stěny
