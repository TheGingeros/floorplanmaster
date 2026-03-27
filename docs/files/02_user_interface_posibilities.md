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