# Vrstvy architektury
Jádro systému FloorPlanMaster stojí na striktním oddělení abstraktní datové logiky od samotného 3D zobrazení. Tohoto oddělení je dosaženo prostřednictvím tří specializovaných vrstev. Zatímco první dvě vrstvy běží čistě na pozadí v Pythonu a starají se o prostorovou matematiku, třetí vrstva funguje jako fyzický most do vykreslovacího jádra Blenderu.

V praxi systém funguje kaskádovitě: Vrstva 1 (Topologie) spravuje exaktní souřadnice spojů a délky stěn jako 2D graf. Jakmile stěny vytvoří uzavřený prostor, Vrstva 2 (Sémantika) jej automaticky detekuje jako novou místnost, přiřadí jí identitu a vypočítá její vlastnosti (plochu, sousedství). Tato čerstvě spočítaná data se následně jednosměrně zrcadlí do Vrstvy 3 (Synchronizace). Ta je zapíše do základní sítě Blender objektu ve formě pojmenovaných atributů (Named Attributes). Na tyto atributy už čekají Geometry Nodes, které z nich okamžitě a v reálném čase vygenerují finální 3D geometrii. Tento přístup zajišťuje, že samotný 3D model je vždy jen bezchybným vizuálním odrazem podkladových grafů, což umožňuje bezpečné a zcela nedestruktivní úpravy.

## Vrstva 1: Topologický skelet (Strukturální graf)
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

## Vrstva 2: Sémantický graf místností (Duální graf)
**Účel**: Reprezentovat sémantické chápání prostorů - místnosti a jejich vztahy.

**Datová struktura**:
- **Typ grafu**: NetworkX neorientovaný graf (`networkx.Graph`)
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

## Vrstva 3: Most synchronizace (Pojmenované atributy)
**Účel**: Synchronizovat sémantická data z vrstev 1-2 do Blenderovy sítě pro Geometry Nodes a vykreslování v reálném čase.

**Implementace**:
- **Pravidlo geometrie**: Každá místnost je v základní Blender síti reprezentována jako jediný N-gon (Face). Vztah je striktně 1 místnost = 1 Face.
- Změny v grafech (Python) se nejprve přes BMesh propíšou do základní topologie Blender sítě (vytvoření/smazání vertexů a hran).
- Následně se serializují data grafu z Pythonu do **pojmenovaných atributů** této sítě.
- Geometry Nodes čtou tyto atributy a dynamicky generují 3D geometrii.

**Domény atributů**:

| Doména | Název atributu | Typ | Hodnota | Účel |
|--------|---|---|---|---|
| **Vertex** | `junction_id` | Integer | Unikátní index z vrstvy 1 | Sledujte, který propojovací bod každý vrchol představuje |
| **Edge** | `wall_id` | Integer | Unikátní index z vrstvy 1 | Sledujte identitu stěny přes úpravy |
| **Edge** | `wall_thickness` | Float | metry | Šířka stěny pro 3D generování |
| **Edge** | `wall_height` | Float | metry | Výška stěny |
| **Face** | `room_id` | Integer | Unikátní index z vrstvy 2 | Která místnost vlastní tuto plochu |
| **Face** | `room_area` | Float | čtvereční metry | Vypočítaná plocha místnosti |
| **Face** | `floor_type` | Integer | ID materiálu | Materiál podlahy |
| **Face** | `ceiling_type` | Integer | ID materiálu | Materiál stropu |

*(Poznámka: Vrstva 1 a 2 používají UUID stringy, ale pro Vrstvu 3 se převádí na Integery kvůli optimalizaci v Geometry Nodes).*

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