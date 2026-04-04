# GPU Modul - Hardwarově akcelerované vykreslování
- modul `gpu`, který slouží jako abstrakční vrstva nad nízkoúrovňovými grafickými knihovnami jako OpenGL, Metal a Vulkan
- pro architektonický addon je tento modul naprosto klíčový, protože umožňuje vykreslovat vodící linky, kóty a náhledy stěn přímo na grafickou kartu bez nutnosti vytvářet náročnou 3D geometrii v databázi Blenderu
## offscreen rendering
- možnost generování náhledů prvků ještě před tím než jsou umístěny do scény
- využití `gpu.types.GPUOffScreen` objektu, do kterého je vykreslena geometrie okna nebo dvěří
- textura je pak zobrazena ve 3D viewportu pod kurzorem myši jako průhledný objekt

## Architektura GPU kreslení a vestavěné shadery
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
## Implementace Drawing Handlers a správa paměti
- draw handlery se přidávají k `bpy.types.SpaceView3D` pomocí metody `draw_handler_add`
- dva hlavní režimy vykreslování: `POST_VIEW` a `POST_PIXEL`
    - `POST_VIEW` vykresluje objekty v souřadném systému 3D scény, ideální pro vodící linky stěn
    - `POST_PIXEL` pracuje v souřadnicích obrazovky a je nezbytný pro textové popisky a kóty, které mají zůstat čitelné nezávisle na zoomu
- důležitou odpovědností je správa paměti, každý přidaný handler musí být odstraněn v `modal()` nebo `__del__()` pomocí `draw_handler_remove()`
- v případě selhání nastává hromadění handlerů v paměti, což může způsobit vizuální artefakty a pád aplikace
- pro aktulizaci vizualizace se používá `area.tag_redraw()`, signalizuje Blenderu, že se  data v GPU bufferech změnila a je třeba viewport překreslit

[Zdroje](../../files/00_sources.md#vykreslování-vlastního-ui-ve-scéně---fp7)

## Typografie a dynamické kótování s modulem BLF
- textový modul BLF - ideální pro vizualizaci rozměrů v reálném čase
- umožňuje vykreslovat text přímo do viewportu s vysokou kontrolou nad pozicí a vzhledem
- ideální pro zobrazení délek stěn, úhlů a ploch místností
- pro kótování ve 3D prostoru je nutné kombinovat blf s utilitami pro transformaci souřadnic

## Porovnání přístupů k vykreslování kótovacího textu

Pro zobrazení kótovacích popisků ve 3D viewportu připadají v úvahu dva přístupy:

| Přístup | Princip | Výhody | Nevýhody |
| :--- | :--- | :--- | :--- |
| **GPU draw_handler + BLF** | 2D text vykreslován přes viewport v `POST_PIXEL` režimu | Vždy čitelný nezávisle na úhlu kamery; nulová geometrická zátěž scény; registrace/odregistrace za běhu | Nutná ruční správa draw_handleru a správa paměti |
| **Geometry Nodes** (String to Curves) | Textová geometrie generována GN stromem z named attributes | Integrován v GN pipeline; bez extra kódu | Text je 3D mesh — při šikmém pohledu hůře čitelný; přidává geometrii do finalizované sítě |

Pro kótovací overlay je rozhodující čitelnost nezávislá na úhlu pohledu — architektonický půdorys se prohlíží z různých zoomů i os, přičemž text musí zůstat vždy ortogonálně čitelný. GPU `POST_PIXEL` overlay tuto podmínku splňuje; GN String to Curves nikoli. Zvolený přístup je proto **GPU draw_handler + BLF**.

[Zdroje](../../files/00_sources.md#typografie-a-dynamické-kótování-s-modulem-blf)

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

[Zdroje](../../files/00_sources.md#prostorová-matematika-a-transformace-souřadnic---fp1)