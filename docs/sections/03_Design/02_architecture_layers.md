# Třívrstvá hybridní architektura
Systém stojí na oddělení abstraktní datové logiky od 3D zobrazení pomocí tří specializovaných vrstev. První dvě vrstvy běží čistě v Pythonu a starají se o topologii a sémantiku půdorysu. Třetí vrstva funguje jako jednosměrný most do vykreslovacího jádra Blenderu.

V praxi systém funguje kaskádovitě: Vrstva 1 spravuje exaktní souřadnice spojů a stěn jako planární 2D graf. Jakmile stěny vytvoří uzavřený prostor, Vrstva 2 jej automaticky detekuje jako novou místnost a vypočítá její vlastnosti. Tato data se jednosměrně zrcadlí do Vrstvy 3, která je zapíše do Blender mesh ve formě pojmenovaných atributů. Na tyto atributy čekají Geometry Nodes, které z nich v reálném čase vygenerují finální 3D geometrii. 3D model je tak vždy jen vizuálním odrazem podkladových grafů, což umožňuje zcela nedestruktivní úpravy.

## Vrstva 1: Topologický skelet (Strukturální graf)
- realizována jako planární graf ([2.6 - Datový model](../02_Analysis/06_ta_data_model.md))
- **uzly** ($V_s$) reprezentují propojovací body (junctions) — místa setkání stěn
    - `id`: unikátní identifikátor (UUID interně, integer v serializaci)
    - `position`: 2D souřadnice $(x, y)$ v prostoru scény
- **hrany** ($E_s$) reprezentují osy stěn propojující dva uzly
    - `id`: unikátní identifikátor
    - `thickness`: tloušťka stěny v metrech
    - `height`: výška stěny v metrech
    - `material`: identifikátor materiálu
    - `openings`: seznam otvorů (okna, dveře) s pozicí a rozměry
- planarita grafu garantuje, že se stěny v rámci podlaží nekříží — odpovídá fyzické realitě ([2.6 - Strukturální graf](../02_Analysis/06_ta_structural_graph.md))
- klíčová operace: detekce minimálních cyklů pro automatickou identifikaci místností ([2.6 - Hybridní spojení](../02_Analysis/06_ta_hybrid_connection.md))

## Vrstva 2: Sémantický graf místností (NRG)
- duální graf odvozený z Vrstvy 1 pomocí algoritmu detekce minimálních cyklů ([2.6 - NRG](../02_Analysis/06_ta_nrg.md))
- **uzly** ($V_r$) reprezentují místnosti — každá mapována na uzavřený cyklus ve Vrstvě 1
    - `id`: unikátní identifikátor místnosti, perzistentní přes úpravy geometrie
    - `cycle_id`: odkaz na odpovídající cyklus ve Vrstvě 1
    - `name`: uživatelský název (např. „Obývací pokoj")
    - `area`: vypočítaná plocha v $m^2$
    - `perimeter`: vypočítaný obvod v metrech
    - `height`: výška místnosti

    - `materials`: podlaha, strop, výchozí barva stěn
- **hrany** ($E_r$) reprezentují relace sousednosti nebo prostupnosti
    - `wall_id`: odkaz na sdílenou stěnu ve Vrstvě 1
    - `connection_type`: "wall" (uzavřená), "door", "passage" (otevřená)
- identita místnosti přetrvává i při změně geometrie — aktualizují se pouze metriky (plocha, obvod), ID zůstává stabilní
- umožňuje prostorové dotazy: sousedství, konektivita, celková plocha dle typu

## Vrstva 3: Synchronizační most (Pojmenované atributy)
- jednosměrný bridge mezi Python grafy a vizualizací v Blenderu ([2.6 - Metadata](../02_Analysis/06_ta_saving_metadata.md))
- synchronizační modul serializuje grafová data do pojmenovaných atributů na Blender mesh dávkovými operacemi pro výkon ([2.6 - Limity Pythonu](../02_Analysis/06_ta_limits_python_blender.md))
- Geometry Nodes modifikátor čte tyto atributy a generuje 3D geometrii v reálném čase
- UUID identifikátory z Vrstvy 1 a 2 se převádějí na celá čísla pro optimalizaci GPU zpracování

| Doména | Atribut | Typ | Účel |
| :--- | :--- | :--- | :--- |
| Vertex | `junction_id` | Integer | identifikace propojovacího bodu |
| Edge | `wall_id` | Integer | identifikace stěny |
| Edge | `wall_thickness` | Float | tloušťka stěny pro 3D generování |
| Edge | `wall_height` | Float | výška stěny |
| Face | `room_id` | Integer | identifikace místnosti |
| Face | `room_area` | Float | plocha místnosti v $m^2$ |
| Face | `floor_type` | Integer | ID materiálu podlahy |
| Face | `ceiling_type` | Integer | ID materiálu stropu |

- celoobjektová metadata (jednotky, verze) se ukládají jako vlastnosti objektu dostupné pro Geometry Nodes
- synchronizační modul má dvě odpovědnosti, které musí proběhnout v tomto pořadí:
    1. **Udržování topologie base mesh** — synchronizuje strukturu mesh s Vrstvou 1: přidává/odebírá vertexy (junctions), hrany (stěny) a face (místnosti = uzavřené cykly); pojmenované atributy nelze zapsat na element, který v mesh neexistuje
    2. **Serializace atributů** — teprve po aktualizaci topologie zapisuje hodnotové atributy z Vrstev 1 a 2 na příslušné elementy mesh
- Geometry Nodes čtou tuto base mesh (2D plochá síť odpovídající půdorysu) jako vstupní geometrii a generují z ní 3D objem stěn a prostorů