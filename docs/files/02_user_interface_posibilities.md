# Návrh uživatelského rozhraní - jak definovat a vykreslovat UI
## Princip vykreslování
- blender funguje na principu Immediate Mode - rozhraní se zahazuje a znovu se staví při každém překreslení obrazovky nebo při nějaké změně
- důsledkem pro výkon je, že logika, která určuje co se má zobrazit musí být extrémně rychlá
- výhodou je flexibilita - rozhraní vždy dokonale odráží aktuální stav, neexistuje žádná mezivrstva, která by data a UI synchronizovala
- každá změna dat na pozadí se automaticky reflektuje při dalším snímku

## Hiearchie členění prostoru obrazovky
- dělení obrazovky spravuje itnerní Window Manager
- architektura se dělí do striktní hiearchie:
    - **Screen**: Celé hlavní okno aplikace
    - **Area**: Obrazovka je rozdělena do obdélníkových oblastí
    - **Region**: Každá oblast má specifické regiony. Například 3D Viewport má region pro hlavní 3D zobrazení, postranní panel (Sidebar), horní lištu (Header) a nástrojovou lištu (Toolbar)

## Datový most mezi UI a daty
- striktní oddělení vizuální podoby rozhraní a samotných dat scény
- k propojení se používá zmínění interní systém RNA
- data v rozhraní jsou pouze vizuálním ukazatelem do datových struktur c++ jádra Blenderu
- když uživatel změní hodnotu, rozhraní hodnotu nikam neukládá, ale okamžitě jí propíše přes RNA systém přímo do databáze scény

## Systém Gizmos manipulátorů
- systém Gizmos představuje vizuální a interaktivní vrstvu
- zprostředkovává vztah mezi uživatelským vstupem a datovými strukturami scény
- možnost uchopit hranu stěny a tažením měnit její délku, přičemž v reálném čase aktulizují kótovací čáry i navazující konstrukce
- definována ve třídě `bpy.types.Gizmo`
- každá instance gizma v sobě nese informace o své vizuální reprezentaci, prostorové transformacri a propojení s daty
- jednotlivá gizma jsou organizována do skupin prostřednictvím `bpy.types.GizmoGroup`
    - tato třída spravuje životní cyklus manipulátorů a definuje podmínky, za kterých jsou viditelné
- důležitou metodou je `poll()`, umožňující gizmos aktivovat pouze v případě, že je vybrán relativní architektonický prvek, což předchází vizuálnímu smogu scény
## Propojení manipulátorů s datovým modelem
- vytvoření přímé datové vazby mezi vizuálním rozhraním a datovým modelem scény
- mapování mezi 3D ovládacím prvkem a vlastnostmi architektonického objektu
    - využití metody `gz.target_set_prop("offset", wall_object, "length")`
- vizuální manipulátor je referenčně svázán s geometrií stěny
- jakákoliv prostorová změna provedená uživatelem na manipulátoru se díky této vazbě okamžitě propisuje do definičních rozměrů daného architektonického prvku
- blender automaticky řeší přepočet pohybu myši v 3D prostoru na změnu číselné hodnoty
- v architektuře jsou rozměry často závislé na sobě - potřeba dynamicky aktulizovat pozici gizma, pokud se změnila geometrie objektu jiným nástrojem
    - využití metody `draw_prepare(context)` před každým překreslením
## Kontextově senzitivní rozhraní pro architektonické prvky
- uživatelské rozhraní musí bt adaptivní a dynamicky reagovat na aktuální kontext práce
- v blender na výběr mezi Pie Menus (rychlá volba) a Pop Overů (plovoucí panely)
- **Rychlá vrstva - pie menus**
    - nabízejí okamžitý přístup k nástrojům na základě toho, jaký prvek je zrovna vybrán
    - podporují svalovou paměť a umožňují spouštet akce rychlími gesty myší bez vizuálnmí kontroly - zrychlení workflow
- **Detailní vrstva - pop overs**
    - poskytují prostor pro zadávájí přesných číselných parametrů
    - inteligentní objevování u kurzoru myši a zobrazují pouze data relevantní pro daný objekt
## GPU Modul - Hardwarově akcelerované vykreslování
- viz vykreslování vlastního UI v FP7 [zde](./02_options_and_limits_blender_api.md#vykreslování-vlastního-ui-ve-scéně---fp7)
- **offscreen rendering** - možnost generování náhledů prvků ještě před tím než jsou umístěny do scény
    - využití `gpu.types.GPUOffScreen` objektu, do kterého je vykreslena geometrie okna nebo dvěří
    - textura je pak zobrazena ve 3D viewportu pod kurzorem myši jako průhledný objekt

[Zdroje](./00_sources.md#uživatelského-rozhraní)

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

