# Možnosti a limity Blender API
- co blender nativně umožňuje, jaké jsou hranice blender api a jak pracovat s interakcí v reálném čase
## Modální operátory - modal operators - FP1
### Obecně
- modální operátor je podtřída `bpy.types.Operator`
- na rozdíl od standartních operátorů, které vykonávají jednorázovou funkci a okamžitě skončí svou činnost, modální operátor zůstává aktivní a kontinuálně naslouchá událostem generovaným uživatelem nebo systémem
- nezbytný pro plynulé kreslení, kdy systém musí v každém okamžiku vědět, kde se nachází kurzor myši, a dynamicky na tuto polohu reagovat vizualizací budoucí geometrie
- důležité je dodržování konvencí pojmenovávání a struktury kódu
- třídy jsou camelcase, metody pak malými písmeny s podtržítky
- v architektonickém kontextu je důležité oddělit logiku interakce od logiky datového modelu
- operátory by měly fungovat pouze jako tenká vrstva volající vysokoúrovňové funkce, což usnadní testování a opětovnou použitelnost kódu mimo modální kontext

### Inicializace
- začíná metodou `invoke()` - připraví počáteční stav a registruje operátor do modálního handleru správce oken pomocí `context.window_manager.modal_handler_add(self)`
- od toho momentu je každá událost ve viewportu, jako je pohyb myši, stisk klávesy nebo rotace pohledu, předávána metodě `modal()`
### Návratové hodnoty
- určují, jakým způsobem bude blender s událostí dále nakládat

| Návratová hodnota | Funkční dopad na systém | Architektonický význam |
| :--- | :--- | :--- |
| `RUNNING_MODAL` | Operátor pokračuje v běhu a čte událost | Umožňuje plynulé tažení stěny nebo změnu rozměru |
| `PASS_THROUGH` | Operátor běží, ale událost je předána dalším nástrojům | Nezbytné pro zoomování a rotaci pohledu během kreslení |
| `FINISHED` | Operátor končí a systém generuje Undo krok | Finalizuje umístění stěny a ukládá ji do databáze scény |
| `CANCELLED` | Operátor končí bez uložení změn a bez Undo kroku | Umožňuje uživateli přerušit akci klávesou ESC | 

### Zpracování událostí a stavový automat v metodě modal()
#### Princip fungování
- metoda `modal()` funguje na principu stavového automatu - programátorský vzor, který umožňuje operátoru měnit své chování v závislosti na tom, v jaké fázi interakce se uživatel právě nachází
- metoda je volána Blenderem při každé události, aby operátor věděl, co má v danou chvíli dělat, musí si v instanci třídy uchovávat informaci o aktuálním stavu
- bez stavového automatu by modal pouze reagovala na izolované událostix

#### Typické stavy pro kreslení půdorysu
- `START` - operátor byl spuštěn, čeká na první kliknutí myši pro určení počátečního bodu
- `DRAWING` - uživatel pohnul myší po prvním kliknutí, v tomto stavu modal neustále přepočítává délku a úhel stěn a přes `gpu` modul vykresluje náhledovou linku
- `EXTRUDING` - po druhém kliknutí se může stav změnit na definování tloušťky nebo výšky stěny
- `FINISHING` - probíhá zápis reálné geometrie do scény a čištění draw handlerů
- implementace je většinou pomocí if/else statementu nebo pomocí match v novější verzi Pythonu
#### Klíčové výhody pro architektonické doplňky
- **Řízení složitosti** - umožňuje implementovat krok za krokem nástroje
- **Interaktivní snapping** - v stavu může být snapping aktivní jinak, ve stavu `DRAWING` může systém prioritně přichytávat k osám, zatímco ve stavu `IDLE` k vrcholům existujících objektů
- **Optimalizace výkonu** - stavový automat brání zbytečným výpočtům, složité operace, jako je generování bmesh nebo aktualizace modifikátorů, se spouštějí pouze při přechodu mezi stavy, zatímco při pohybu myši se aktualizuje pouze lehká vizualizace přes modul `gpu`

[Zdroje](./sources.md#modální-operátory---modal-operators---fp1)

## Vykreslování vlastního UI ve scéně - FP7
- modul `gpu`, který slouží jako abstrakční vrstva nad nízkoúrovňovými grafickými knihovnami jako OpenGL, Metal a Vulkan
- pro architektonický addon je tento modul naprosto klíčový, protože umožňuje vykreslovat vodící linky, kóty a náhledy stěn přímo na grafickou kartu bez nutnosti vytvářet náročnou 3D geometrii v databázi Blenderu

### Architektura GPU kreslení a vestavěné shadery
- vykreslování pomocí modulu `gpu` probíhá prostřednictvím draw handlerů, které se registrují do 3D viewportu
- tyto handlery jsou volány při každém překreslení okna a využívají GPU dávky (GPUBatch) složené z vertexových bufferů (GPUVertBuf) a shaderů
- blender poskytuje řadu vestavěných shaderů, které pokrývají většinu potřeb architektonické vizualizace

| Název shaderu | Vlastnosti a použití | Klíčové uniformy/atributy |
| :--- | :--- | :--- |
| `2D_UNIFORM_COLOR` | Ploché kreslení kót a 2D symbolů přes viewport | `color` (RGBA), `pos` (2D) |
| `3D_UNIFORM_COLOR` | Vodící linky v prostoru, osy a drátové náhledy | `color` (RGBA), `pos` (3D) |
| `3D_POLYLINE_UNIFORM_COLOR` | Čáry s tloušťkou, ideální pro obrysy zdí | `lineWidth`, `viewportSize`, `color` |
| `3D_SMOOTH_COLOR` | Stínované náhledy ploch s barevnými přechody | `pos` (3D), `color` (per vertex) |
| `IMAGE` | Vykreslování textur, například ikon nástrojů ve 3D prostoru | `image` (sampler2D), `texCoord` |

- využití `3D_POLYLINE_UNIFORM_COLOR` je v architektuře zásadní pro kreslení čitelných půdorysů, protože standardní čáry v moderních API často postrádají nativní podporu pro tloušťku větší než jeden pixel
#### Implementace Drawing Handlers a správa paměti
- draw handlery se přidávají k `bpy.types.SpaceView3D` pomocí metody `draw_handler_add`
- dva hlavní režimy vykreslování: `POST_VIEW` a `POST_PIXEL`
    - `POST_VIEW` vykresluje objekty v souřadném systému 3D scény, ideální pro vodící linky stěn
    - `POST_PIXEL` pracuje v souřadnicích obrazovky a je nezbytný pro textové popisky a kóty, které mají zůstat čitelné nezávisle na zoomu
- důležitou odpovědností je správa paměti, každý přidaný handler musí být odstraněn v `modal()` nebo `__del__()` pomocí `draw_handler_remove()`
- v případě selhání nastává hromadění handlerů v paměti, což může způsobit vizuální artefakty a pád aplikace
- pro aktulizaci vizualizace se používá `area.tag_redraw()`, signalizuje Blenderu, že se  data v GPU bufferech změnila a je třeba viewport překreslit

[Zdroje](./sources.md#vykreslování-vlastního-ui-ve-scéně---fp7)

### Typografie a dynamické kótování s modulem BLF
- textový modul BLF - ideální pro vizualizaci rozměrů v reálném čase
- umožňuje vykreslovat text přímo do viewportu s vysokou kontrolou nad pozicí a vzhledem
- ideální pro zobrazení délek stěn, úhlů a ploch místností
- pro kótování ve 3D prostoru je nutné kombinovat blf s utilitami pro transformaci souřadnic

[Zdroje](./sources.md#typografie-a-dynamické-kótování-s-modulem-blf)

## Prostorová matematika a transformace souřadnic - FP1
- přesně kreslení půdorysu vyžaduje precizní převod 2D polohy myši na 3D body v prostoru scény
- blender k tomuto poskytuje modul `bpy_extras.view3d_utils`, řeší inverzní projekci z plochy obrazovky do hloubky 3D scény
- klíčové transformační funkce:
    1. `region_2d_to_vector_3d` - vypočítá normalizovaný směrový vektor paprsku vycházejícího z pozice kamery směrem k bodu pod kurzorem
    2. `region_2d_to_origin_3d` - určí počáteční bod paprsku v 3D prostoru, což je u perspektivní kamery její poloha a u ortografického zobrazení bod na blízké ořezové rovině
    3. `region_2d_to_location_3d` - umožňuje projektovat kurzor na specifickou rovinu v hloubce scény, což je základ pro kreslení na podlahu (rovina XY)

- pro implementaci snappingu k vrcholům a hranám je iterace přes všechny objekty v Pytohnu příliš pomalá
- výkonnným řešením je `mathutils.bvhtree.BVHTree`
    - datová struktura umožňující prostorové dělení scény, díky němuž lze dotaz na nejbližší bod k myši vyřídit v logaritmickém čase namísto lineárního, což je u komplexních půdorysů a scén kritické

[Zdroje](./sources.md#prostorová-matematika-a-transformace-souřadnic---fp1)

## Limity výkonu Pythonu v Blenderu
- python je v prostředí blenderu interpretovaným jazykem
- je potřeba náročné operace delegovat na stranu Blenderu nebo GPU, které využívají C++
- zkušnosti z vývoje komplexních importérů a generativních nástrojů ukazují, že čistý Python je řádově pomalejší při úlohách vyžadující hromadné zpracování dat
- v kontextu architektonického kreslení jsou hlavními limitujícími faktory:
    1. **Iterace přes mesh data** - procházení vrcholů pomocí for smyčky je pomalé
    2. **Počet objektů v `bpy.data.objects`** - blender zpomaluje exponenciálně s rostoucím počtem unikátních objektů ve scéně
    3. **Časté aktulizace DepsGraphu** - každá změna geometrie vynucuje přepočet grafu závislosti, 

### Metody delegování výpočtů na C++ jádro
k překonání těchto limitů se v profesionálních add-onech využívají následující techniky:
#### Využítí foreach_set a foreach_get
- tyto metody umožňují přenášet celá pole dat  mezi Pythonem a C++ strukturami Blenderu jedinou operací
- operátor vypočítá novou pozici stěny, namísto nastavování každého vrcholu zvlášť by měl použít NumPy pole a metodu `foreach_set`, což přinese zrychlení
#### Delegování na modifikátory
- místo aby Python generoval detailní geometrii, měl by vytvořit pouze základní čárový model a na něj aplikovat modifikátory jako Solidify, Bevel nebo Array
- modifikátory jsou implementovány v C++, plně využívají multithreading a jsou optimalizovány pro real-time aktualizaci při změně parametrů
- python operátor pak v modálním běhu pouze mění číselné hodnoty jako modifier.thickness, což je operace s téměř nulovou režií
#### Geometry nodes jako výpočetní backend
- moderním přístupem je využití Geometry Nodes jako vysoce výkonného generativního motoru
- python add-on může vytvořit uzel Geometry Nodes, který obsahuje veškerou logiku pro stavbu domu a přes API pouze manipulovat se vstupními hodnotami tohoto uzlu
- výpočet samotné geometrie pak probíhá v nativním kódu Blenderu, který je o několik řádů rychlejší a efektivnější než jakýkoli skript v Pythonu

[Zdroje](./sources.md#limity-výkonu-pythonu-v-blenderu)