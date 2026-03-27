# Návrh uživatelského rozhraní - jak definovat a vykreslovat UI
## Paradigmata přímé manipulace a systém Gizmo
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
- 
## Vizualizace a výkon v reálném čase přes GPU modul
## Optimalizace a správa kontextu
## Matematické základy transformací v architektonickém prostoru