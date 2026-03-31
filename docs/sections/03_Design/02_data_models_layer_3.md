# Vrstva 3: Pojmenované atributy - Kompletní specifikace
Tato sekce definuje fyzický most (rozhraní) mezi abstraktní matematikou v Pythonu a C++ jádrem Blenderu. Vrstva 3 sama o sobě nevykonává žádnou logiku; její jedinou, avšak kriticky důležitou zodpovědností je přenést (serializovat) data z Vrstvy 1 a 2 do základní sítě tak, aby je Geometry Nodes mohly okamžitě vykreslit. Namísto pomalého a destruktivního generování 3D stěn přímo pomocí Blender Python API, zapisuje tento addon data pouze do takzvaných pojmenovaných atributů (Named Attributes). Tímto přístupem se veškerá práce s tvorbou finální 3D geometrie přesouvá na hardwarově akcelerované (GPU/multithread) uzly Blenderu.

## Tabulka atributů
Následující tabulka představuje datové schéma pro Geometry Nodes. Jasně mapuje, která datová abstrakce patří na jaký typ geometrického prvku sítě (propojovací bod na Vertex, stěna na Edge, místnost na Face). Zásadní architektonickou optimalizací je zde řízený překlad UUID řetězců z Pythonu na číselné indexy (Integers). Geometry Nodes totiž pracují s čísly o několik řádů rychleji než s textovými řetězci, což zaručuje plynulý běh i u rozsáhlých vícepodlažních projektů.

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

## Formát serializace
Přenos obrovského množství dat z Pythonu do interních datových struktur Blenderu představuje tradiční výzvu všech addonů. Aby FloorPlanMaster udržel okamžitou odezvu, striktně se vyhýbá použití pomalých cyklů (`for` loop) pro každý jednotlivý vrchol. Namísto toho se data v Pythonu formátují do souvislých polí v paměti a následně se zapisují do Blenderu dávkově přes nízkoúrovňové C API pomocí metody `foreach_set`, což zrychluje zápis.

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

## Časování a logika synchronizace
Aby nedošlo k pádu Blenderu (například zápisem dat na hranu, která ještě fyzicky neexistuje), musí být synchronizační pipeline řízena naprosto exaktním stavovým automatem. Proces probíhá v následujících, striktně uspořádaných krocích:

- **1. Odbavení uživatelského vstupu (Python Grafy):** Uživatel potvrdí operaci (např. nakreslí novou čáru). Vrstva 1 ihned upraví NetworkX graf a Vrstva 2 okamžitě přepočítá místnosti. V tento moment má Python hotová data, ale Blender o nich ještě neví.
- **2. Topologická aktualizace (BMesh):** Přes modul BMesh se vygeneruje hrubá, "holá" síť odpovídající tvaru grafů. Pokud přibyla hrana ve Vrstvě 1, vytvoří se fyzická hrana (Edge) v BMesh a zapíše se do sítě objektu. **Tento krok je kritický** – indexy a počty elementů v Python seznamech se nyní musí naprosto přesně shodovat s počtem vertexů a hran v Blender síti.
- **3. Dávkový zápis (Serializace Atributů):** Jakmile jsou fyzické vertexy, hrany a plošky (faces) v síti vytvořeny, aktivuje se serializace. Python hromadně vypíše pole připravených atributů z datových modelů přímo na odpovídající geometrické prvky (využívající výše popsaný `foreach_set`).
- **4. Reakce modifikátoru (Geometry Nodes):** Ve chvíli, kdy zápis atributů skončí a uvolní se blokování vlákna, interní systém Blenderu (Depsgraph) zaznamená změnu dat. Spustí vyhodnocení Geometry Nodes stromu, který tyto čerstvé atributy okamžitě přečte a během zlomku vteřiny z nich vygeneruje finální vizuální 3D reprezentaci pro viewport.

**Dávkování zápisu (Batching):** Z důvodu výkonu nedochází k této kaskádě po každém nepatrném pohybu myši. Pokud uživatel například táhne stěnu (interaktivní posun rohů), synchronizuje se typicky pouze pozice vrcholů v BMesh a základní parametry, zatímco složité přepočty místností a plná serializace atributů se spouští dávkově, až ve chvíli, kdy uživatel potvrdí operaci uvolněním levého tlačítka myši. Validace po skončení tohoto cyklu navíc ověřuje, zda se `len(atributových_dat)` přesně rovná `len(mesh.vertices/edges/faces)`.