# 3.1 Architektura systému

Tato sekce popisuje třívrstvou hybridní architekturu FloorPlanMaster. Je to klíč k pochopení, jak se data proudí mezi jednotlivými komponenty a jak se udržuje konzistence při interakci uživatele. FloorPlanMaster není jen běžné GUI - je to komplexní datový systém, který kombinuje tři odlišné reprezentace půdorysu:
- **Vrstva 1 (Topologie)**: čistý graf propojovacích bodů a stěn - to, co měří a propojuje
- **Vrstva 2 (Sémantika)**: graf místností a jejich vztahů - to, co architekt chápe a používá
- **Vrstva 3 (Synchronizace)**: Blender atributy a Geometry Nodes - to, co vidí na obrazovce

Tato architektura zajišťuje nedestruktivní úpravy půdorysu bez ztráty informací a aktualizaci geometrie v reálném čase. Komunikace vrstev je striktně jednosměrná: grafy v Pythonu vypočítají nová data a skrze pojmenované atributy (Named Attributes) je předají do Blender sítě, kde je Geometry Nodes okamžitě vykreslí.

Systém přímo aplikuje návrhový vzor MVC, kde Python grafy tvoří nezávislý Model, Blender UI a 3D pohled fungují jako View a modální operátory zachytávající kliknutí myší slouží jako Controller. Celý datový tok tak začíná uživatelským vstupem, který změní čistou topologii, což automaticky vyvolá přepočet sémantiky místností a končí instantním překreslením 3D geometrie, aniž by se tyto vrstvy do sebe funkčně zamotaly.

## Vrstvy architektury

### Vrstva 1: Topologický skelet (Strukturální graf)

**Účel**: Reprezentovat čistě topologickou strukturu půdorysů - propojovací body stěn a jejich konektivitu.

**Datová struktura**:
- **Typ grafu**: NetworkX planární graf (`networkx.Graph`)
- **Uzly**: Propojovací body, kde se stěny setkávají
  - `id`: Jedinečný identifikátor
  - `position`: (x, y) souřadnice v 3D prostoru
  - `type`: "junction" nebo "corner"
- **Hrany**: Segmenty stěn propojující spojovací body
  - `id`: Jedinečný identifikátor
  - `wall_data`: Slovník obsahující:
    - `thickness`: Šířka stěny (metry, přizpůsobitelné jednotky)
    - `height`: Výška stěny (pro 3D generování)
    - `material`: Identifikátor materiálu/textury
    - `openings`: Seznam oken/dveří na této stěně

**Matematické vlastnosti**:
- Musí být planární (lze nakreslit na 2D rovině bez křížících se hran)
- NetworkX automaticky identifikuje všechny cykly/plochy
- Každý cyklus představuje uzavřený prostor (potenciální místnost)

**Klíčové operace**:
- Přidávání/odebírání propojovacích bodů
- Přidávání/odebírání stěn
- Detekce a validace cyklů
- Hledání průsečíků pro přichycování

### Vrstva 2: Sémantický graf místností (Duální graf)

**Účel**: Reprezentovat sémantické chápání prostorů - místnosti a jejich vztahy.

**Datová struktura**:
- **Typ grafu**: NetworkX neorientovaný graf (`networkx.DiGraph`)
- **Uzly**: Místnosti/prostory
  - `id`: Jedinečný identifikátor místnosti (perzistentní přes úpravy)
  - `cycle_id`: Odkaz na cyklus z vrstvy 1
  - `name`: Uživatelsky přívětivé jméno (např. "Obývací pokoj")
  - `properties`: Slovník
    - `area`: Vypočítané čtvereční metry
    - `perimeter`: Vypočítaný obvod v metrech
    - `height`: Výška místnosti
    - `floor_type`: Identifikátor materiálu
    - `ceiling_type`: Identifikátor materiálu stropu
    - `wall_color`: Výchozí barva stěny
    - `custom_data`: Uživatelem definovaná metadata

- **Hrany**: Vztahy sousedství mezi místnostmi
  - `wall_id`: Odkaz na stěnu z vrstvy 1, která odděluje místnosti
  - `openings`: Dveře, okna, atd.
  - `connection_type`: "door", "passage", "closed", atd.

**Klíčové vlastnosti**:
- Identita místnosti přetrvá, i když se geometrie změní
- Aktualizují se pouze atributy (plocha, konektivita), identity uzlů zůstávají stabilní
- Obousměrné vztahy s vrstvou 1
- Sousedství místností je obousměrné (hrany nemají směr), data o průchodech jsou sdílena

**Klíčové operace**:
- Vytvoření místnosti z cyklu
- Aktualizace plochy/obvodu místnosti
- Nalezení sousedních místností
- Dotaz na cesty konektivity

### Vrstva 3: Most synchronizace (Pojmenované atributy)

**Účel**: Synchronizovat sémantická data z vrstev 1-2 do Blenderovy sítě pro Geometry Nodes a vykreslování v reálném čase.

**Implementace**:
- **Pravidlo geometrie**: Každá místnost je v základní Blender síti reprezentována jako jediný N-gon (Face). Vztah je striktně 1 místnost = 1 Face.
- Změny v grafech (Python) se nejprve přes BMesh propíšou do základní topologie Blender sítě (vytvoření/smazání vertexů a hran).
- Následně se serializují data grafu z Pythonu do **pojmenovaných atributů** této sítě.
- Geometry Nodes čtou tyto atributy a dynamicky generují 3D geometrii.

**Domény atributů**:

| Doména | Název atributu | Typ | Hodnota | Účel |
|--------|---|---|---|---|
| **Vertex** | `junction_id` | String | UUID z vrstvy 1 | Sledujte, který propojovací bod každý vrchol představuje |
| **Edge** | `wall_id` | String | UUID z vrstvy 1 | Sledujte identitu stěny přes úpravy |
| **Edge** | `wall_thickness` | Float | metry | Šířka stěny pro 3D generování |
| **Edge** | `wall_height` | Float | metry | Výška stěny |
| **Face** | `room_id` | String | UUID z vrstvy 2 | Která místnost vlastní tuto plochu |
| **Face** | `room_area` | Float | čtvereční metry | Vypočítaná plocha místnosti |
| **Face** | `floor_type` | String | ID materiálu | Materiál podlahy |
| **Face** | `ceiling_type` | String | ID materiálu | Materiál stropu |

**Vlastní vlastnosti objektu (Custom Properties)**:
Celoobjektová metadata se neukládají jako pojmenované atributy sítě, ale jako standardní Custom Properties na samotném Blender objektu (dostupné v GN přes uzel Object Info).
- `floor_unit` (String): "m", "cm", "ft" - Jednotka zvolená uživatelem
- `structure_version` (Int): Číslo verze pro zneplatnění/obnovení mezipaměti

**Tok synchronizace**:
```
Vrstva 1 & 2 v Pythonu
        ↓ (serializace)
Pojmenované atributy (síť)
        ↓ (čtení přes GN driver)
Geometry Nodes
        ↓ (generování)
3D geometrie v pohledu
```

**Když se atributy aktualizují**:
- Uživatel upraví tloušťku stěny → Python aktualizuje atribut `wall_thickness`
- Geometry Nodes automaticky detekuje změnu atributu (přes driver)
- Strom GN se znovu vyhodnotí → 3D geometrie se aktualizuje v reálném čase
- ID místnosti zůstává nezměněno → nedestruktivní úprava

## Vzor MVC v Blenderu

```
┌─────────────────────────────────────────┐
│              MODEL                       │
│  ─────────────────────────────────────  │
│  • Vrstva 1: Strukturální graf (NetworkX)│
│  • Vrstva 2: Graf místností (NetworkX)   │
│  • Vrstva 3: Pojmenované atributy (Bl.)  │
└─────────────────────────────────────────┘
           ↑                    ↑
           │ serializace        │ (čtení přes GN driver)
           │                    ↓
         Python      ┌──────────────────┐
         API         │  Geometry Nodes  │
                     └──────────────────┘
                            ↓
                      Síť/Geometrie
           ┌───────────────────────────┐
           │        VIEW                │
           │  ───────────────────────  │
           │  • Vykreslování pohledu   │
           │  • Zobrazení GPU           │
           │  • Vizualizace uživatele   │
           └───────────────────────────┘
           ↑
           │ (zobrazení)
┌─────────────────────────────────────────┐
│         CONTROLLER                       │
│  ─────────────────────────────────────  │
│  • Modální operátory (Tužka, Finalizace)│
│  • Obslužné programy událostí (myš, kl.)│
│  • Logika stavového automatu             │
└─────────────────────────────────────────┘
```

## Organizace modulů

```
floorplanmaster/
│
├── __init__.py                       # Registrace addonu a vstupní bod
│
├── core/
│   ├── __init__.py
│   ├── structural_graph.py           # Vrstva 1: Operace grafu NetworkX
│   ├── room_graph.py                 # Vrstva 2: Sémantický graf místností
│   └── parameters.py                 # Definice parametrů a validace
│
├── geometry/
│   ├── __init__.py
│   ├── attribute_sync.py             # Vrstva 3: Synchronizace do pojmenovaných atributů
│   ├── geometry_nodes_setup.py       # Vytvoření stromu uzlů GN
│   └── bmesh_utils.py                # Nízkoúrovňové operace geometrie
│
├── operators/
│   ├── __init__.py
│   ├── pencil_tool.py                # FP1: Modální operátor kreslení
│   ├── finalize_tool.py              # FP4: Finalizace geometrie
│   ├── edit_room.py                  # Operátor úpravy místnosti
│   └── context_menu.py               # FP5: Kontextová nabídka
│
├── ui/
│   ├── __init__.py
│   ├── properties.py                 # Panely vlastností UI
│   ├── menus.py                      # Integrace hlavní nabídky
│   └── manipulators.py               # FP6: 3D manipulátory/rukojeti
│
├── utils/
│   ├── __init__.py
│   ├── snapping.py                   # Systém přichycování (osa, bod, mřížka)
│   ├── validation.py                 # Validace topologie a geometrie
│   ├── calculations.py               # Výpočty plochy, objemu, vzdálenosti
│   ├── constants.py                  # Konstanty a výchozí hodnoty
│   └── serialization.py              # Ukládání/načítání půdorysů
│
└── tests/
    ├── test_structural_graph.py
    ├── test_room_graph.py
    ├── test_operators.py
    └── test_calculations.py
```

## Tok dat: Základní operace

### 1. Kreslení půdorysu (FP1 - Nástroj Tužka)

```
Uživatel aktivuje nástroj Tužka (modální operátor)
            ↓
Modální vstup do stavu DRAWING (čeká na vstup)
            ↓
Uživatel klikne na bod 1 (vytvoření propojovacího bodu)
  • Operátor ověří pozici (přichycování, mřížka)
  • Vrstva 1: Přidá uzel do strukturálního grafu
  • Vrstva 3 (BMesh): Vytvoří reálný vrchol (vertex) v základní síti Blenderu
  • Vrstva 3 (Atributy): Zapíše/aktualizuje pojmenované atributy na tomto vrcholu
            ↓
Uživatel pohne myší (generování náhledu)
  • Modální je ve stavu DRAWING
  • Vypočítá geometrii náhledu stěny
  • Vykreslí náhled přes modul GPU
            ↓
Uživatel klikne na bod 2 (potvrzení stěny)
  • Modální ověří stěnu (délka, úhly)
  • Vrstva 1: Přidá hranu do strukturálního grafu
  • Vrstva 3 (BMesh): Vytvoří reálnou hranu v základní síti Blenderu spojující dané vrcholy
  • Vrstva 3 (Atributy): Zapíše pojmenované atributy na tuto hranu (např. `wall_id`, `wall_thickness`)
  • NetworkX detekuje nové cykly
            ↓
Vrstva 2 AUTOMATICKÁ AKTUALIZACE: Graf místností aktualizován
  • Detekce cyklů identifikuje nové místnosti
  • Přiřadí perzistentní ID místností
  • Vypočítá plochu, sousedství
            ↓
Vrstva 3: Serializace do pojmenovaných atributů
  • Aktualizuje atributy sítě
  • Geometry Nodes spustí obnovení
            ↓
Pohled se aktualizuje s 3D geometrií
            ↓
Opakování nebo stisk Enter/ESC pro ukončení
```

### 2. Úprava vlastností místnosti

```
Uživatel otevře panel Vlastnosti
            ↓
Vybere místnost ze seznamu nebo klikne na místnost v 3D
            ↓
Upraví parametr (např. tloušťka stěny, barva)
            ↓
Vrstva 1 nebo 2: Aktualizuje data grafu
            ↓
Vrstva 3: Serializuje atribut do pojmenovaných atributů
            ↓
Driver Geometry Nodes se aktualizuje
            ↓
Pohled se znovu vykreslí s novým parametrem
(ID místnosti nezměněno → nedestruktivní úprava)
```

### 3. Finalizace (FP4 - Převod na trvalou geometrii)

```
Uživatel klikne na tlačítko "Finalizace"
            ↓
Operátor čte pojmenované atributy
            ↓
Geometry Nodes vypečeí výstup do sítě
            ↓
Volitelné: Vytvoří jednotlivé objekty místností
            ↓
Volitelné: Sloučí do jednoho objektu
            ↓
Uloží do souboru (Blender .blend soubor obsahuje všechny vrstvy)
```

## Principy návrhu

1. **Oddělení zájmů**
   - Logika grafu (vrstvy 1, 2) nezávislá na Blenderu/GN (vrstva 3)
   - Operátory fungují jako tenké řadiče, ne složitá logika
   - Utility jsou bezstavové a opakovaně použitelné

2. **Nedestruktivní úpravy**
   - Identity místností/stěn přetrvávají přes změny parametrů
   - Undo/Redo podporováno přes systém operátorů Blenderu
   - Parametry lze upravovat nekonečně

3. **Zpětná vazba v reálném čase**
   - Náhled během kreslení (modul GPU)
   - Živé aktualizace při změně vlastností (GN drivers)
   - Responzivní UX i se složitými dispozicemi

4. **Modularita**
   - Každá vrstva se dá testovat nezávisle
   - Operace grafu nepotřebují Blenderův kontext
   - Snadné přidávání nových funkcí (okna, dveře, poznámky)

5. **Osvědčené postupy Blenderu**
   - Dodržujte konvence pojmenování Blenderu
   - Používejte modální operátory pro interaktivní nástroje
   - Využívejte Geometry Nodes pro nedestruktivní geometrii
   - Správná podpora undo/redo

## Technická rozhodnutí a zdůvodnění

| Rozhodnutí | Proč | Alternativa | Kompromis |
|----------|-----|-------------|-----------|
| Použití NetworkX pro grafy | Algoritmy planárních grafů, detekce cyklů, prostorová analýza | Vlastní třída grafu | Externí závislost, ale obrovský nárůst výkonu |
| Geometry Nodes pro 3D | Vykreslování v reálném čase, GPU akcelerované, nedestruktivní | Modifikátory Bmesh | GN obtížnější ladění, ale nedestruktivní |
| Most pojmenovaných atributů | Minimální režie synchronizace, nativní Blender | Ukládání v vlastních vlastnostech | Atributy bezproblémově integrují s GN drivers |
| Modální operátory | Hladká, responzivní interakce uživatele | Samostatné nástroje | Vyšší složitost správy stavů |
| Omezení planárního grafu | Validuje topologii půdorysu, umožňuje algoritmy | Povolit neplanární | Vyloučí architektonické nemožnosti |

## Aspekty výkonu

1. **Operace grafu**: Složitost O(n) přijatelná pro typické půdorysy (< 100 místností)
2. **Synchronizace atributů**: Serializuje pouze změněné uzly/hrany, aby se minimalizovaly aktualizace sítě
3. **Geometry Nodes**: Opětovné vyhodnocení GN je automatické; lze optimalizovat pomocí ukládání uzlů do mezipaměti
4. **Vykreslování náhledu**: Používejte lehké GPU čáry pro náhled, ne plnou geometrii
5. **Aktualizace pohledu**: Dávkové aktualizace, aby se zabránilo opětovnému vykreslení na událost

## Zabezpečení a validace

- **Validace topologie**: Zajistěte planární grafy, žádné vlastní průniky
- **Rozsahy parametrů**: Validujte tloušťku stěny, výšku v rozumných mezích
- **V/V souboru**: Validujte serializovaná data před načtením
- **Vstup uživatele**: Dezinfikujte jména místností, ID materiálů
