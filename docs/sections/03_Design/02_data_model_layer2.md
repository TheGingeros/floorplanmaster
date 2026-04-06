# Vrstva 2: Graf místností
Sémantická vrstva addonu, matematicky duální graf k Vrstvě 1. Dává topologickým tvarům architektonický význam — z uzavřených polygonů se stávají místnosti s identitou, názvem a vizuálními vlastnostmi. Vrstva je spravována primárně automaticky na základě detekovaných cyklů z Vrstvy 1 ([2.6 - NRG](../02_Analysis/06_ta_nrg.md), [2.6 - Hybridní spojení](../02_Analysis/06_ta_hybrid_connection.md)).

## Model místnosti (Room)
Reprezentuje vrchol v grafu místností — jeden uzavřený prostor odvozený z cyklu ve Vrstvě 1. Klíčovým rozhodnutím je oddělení perzistentního `id` (identita místnosti, nemění se ani při změně tvaru) od `cycle_id` (odkaz na aktuální topologickou hranici).

- `id`: unikátní identifikátor místnosti, perzistentní přes úpravy geometrie
- `cycle_id`: odkaz na odpovídající cyklus ve Vrstvě 1
- `name`: uživatelský název (např. „Obývací pokoj")
- `room_type`: klasifikace typu — obytná, technická, komunikace
- `area`: vypočítaná plocha v $m^2$ (automaticky z cyklu)
- `perimeter`: vypočítaný obvod v metrech (automaticky z cyklu)
- `centroid`: $(x, y)$ — střed místnosti (automaticky z cyklu)
- `height`: výška místnosti v metrech
- `wall_color`: výchozí barva stěn (RGBA)
- `floor_material`: identifikátor materiálu podlahy
- `ceiling_material`: identifikátor materiálu stropu

**Omezení**:
- `id` je perzistentní — i když uživatel změní tvar místnosti k nepoznání, ID a sémantická metadata (název, materiály) přetrvávají, dokud nedojde k úplnému rozpojení cyklu
- `cycle_id` musí odkazovat na platný cyklus ve Vrstvě 1
- minimálně 3 hraniční vrcholy
- plocha a obvod musí splňovat validační pravidla (viz [rodičovský soubor](./02_data_model.md))

## Model sousedství (Adjacency)
Reprezentuje hranu v grafu místností — logické propojení dvou prostor. Definuje propustnost půdorysu a určuje nejen to, zda dvě místnosti sdílejí stěnu, ale jakého typu je jejich propojení.

- `room_a`: odkaz na první místnost
- `room_b`: odkaz na druhou místnost
- `shared_wall`: odkaz na sdílenou stěnu ve Vrstvě 1
- `connection_type`: typ propojení
    - "closed" — stěna bez otvorů
    - "door" — průchod dveřmi
    - "window" — vizuální propojení oknem
    - "passage" — otevřený průchod bez dveří
- `openings`: seznam odkazů na konkrétní otvory na sdílené stěně

## Operace grafu místností
Graf slouží jako hlavní rozhraní pro dotazování a manipulaci se sémantickými daty.

- **Místnosti (CRUD)**:
    - založení místnosti z detekovaného cyklu (automaticky při detekci)
    - odebrání místnosti (automaticky při zániku cyklu)
    - aktualizace vypočítaných vlastností (plocha, obvod, centroid) po změně geometrie
    - získání místnosti podle ID, všech místností, místností podle typu
- **Sousedství**:
    - přidání sousedství mezi dvě místnosti se sdílenou stěnou
    - získání sousedních místností k dané místnosti
    - zjištění, zda dvě místnosti sousedí
- **Analýza a dotazy**:
    - celková plocha všech místností (nebo dle typu)
    - identifikace vnějších místností (dotýkají se exteriéru) a vnitřních
    - analýza poměrů stran místností
