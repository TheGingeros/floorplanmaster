# 3.5.4 Viewport UI

Viewport UI označuje veškeré vizuální prvky vykreslované přímo ve 3D Viewportu nad geometrií scény — nikoliv jako součást Blender panelového systému, ale jako GPU overlay vrstvy a interaktivní manipulátory. Tyto prvky nezasahují do geometrie scény ani do finalizované sítě a jsou plně reverzibilní. Technickým základem jsou Blender mechanismy popsané v [technické analýze GPU vykreslování](../02_Analysis/06_ta_ui_gpu.md) a [technické analýze Gizmo systému](../02_Analysis/06_ta_ui.md). Viewport UI addonu tvoří čtyři kategorie: HUD overlay aktivní při kreslení, kótovací overlay s rozměry, barevné odlišení místností a interaktivní gizmos.

## HUD overlay (Pencil Tool aktivní)

HUD (Heads-Up Display) je textová a grafická vrstva překrývající viewport po celou dobu aktivity Pencil Tool (FP1). Vzor je přejat z Blender vlastních nástrojů — Knife Tool zobrazuje délku řezu, Loop Cut zobrazuje počet smyček a jejich polohu, Extrude zobrazuje vzdálenost vytažení. Společným principem je, že modální nástroje s více stavy a klávesovými vstupy vyžadují okamžitou zpětnou vazbu bez nutnosti přepínat pohled na jiné části rozhraní. SketchUp zobrazuje délku v pravém dolním rohu při kreslení — FloorPlanMaster přejímá tento princip a zobrazuje hodnoty blíže kurzoru, kde je uživatelův pohled přirozeně zaměřen.

HUD je vykreslován v `POST_PIXEL` režimu (souřadnice obrazovky) — text a indikátory tedy zůstávají čitelné a pozičně stabilní nezávisle na zoomu nebo rotaci pohledu. Technické odůvodnění tohoto rozhodnutí je rozvedeno v [porovnání přístupů k vykreslování](../02_Analysis/06_ta_ui_gpu.md).

HUD zobrazuje výhradně **měřicí data a indikátor fáze** — nápověda kláves do HUD nepatří:

| Stav automatu | Obsah HUD |
| :--- | :--- |
| **ČEKÁNÍ** | Stavová zpráva „FloorPlan Pencil — Waiting for input" |
| **KRESLENÍ** | Délka navrhované stěny; úhel k poslednímu úseku |

Typografie HUD: výrazný font pro délku a úhel (klíčové hodnoty při kreslení), menší font pro stavovou zprávu fáze. Stavová zpráva přijímá barvu odpovídající konvenci Blender nativních hlášení — bílá pro informace.

## Nápověda kláves v dolní liště

Klávesové zkratky platné pro aktuální stav operátoru jsou zobrazeny v **dolní stavové liště Blenderu** (Header oblasti `STATUSBAR`). Toto umístění je standardem Blender nativních nástrojů — Extrude, Knife Tool, Annotate i Loop Cut používají tentýž mechanismus. Nápověda kláves ve viewportu jako GPU text by narušovala architektonický vzor Blenderu a ztěžovala čitelnost scény.

Technicky je nápověda implementována registrací draw funkce přes `bpy.types.STATUSBAR_HT_header.append()` při aktivaci operátoru a jejím odregistrováním při ukončení operátoru. Klávesy a tlačítka myši jsou zobrazeny jako **ikony** (`UILayout.label(icon=...)`), nikoliv jako prostý text — v souladu s Blender vizuálním jazykem:

| Stav automatu | Nápověda v liště |
| :--- | :--- |
| **ČEKÁNÍ** | `LMB` Place first junction · `Z` Undo · `Enter` Confirm · `ESC` Abort |
| **KRESLENÍ** | `LMB` Place next junction · `RMB` Cancel line · `Z` Undo · `Enter` Confirm · `ESC` Abort |

Při ukončení operátoru se draw funkce z hlavičky odregistruje a lišta se vrátí do výchozího stavu Blenderu.

## Kótovací overlay (FP7)

Kótovací overlay zobrazuje rozměry prvků průběžně bez nutnosti aktivovat speciální nástroj. Vzor je přejat z Revit a ArchiCAD, kde jsou délky stěn a plochy místností automaticky viditelné při pohledu Top View jako pomůcka pro kontrolu modelu. Přepínač viditelnosti (`T`) umožňuje overlay skrýt, pokud uživatel pracuje na detailech bez potřeby kótování.

Kótování je implementováno jako `POST_PIXEL` draw_handler — text zůstává ortogonálně čitelný nezávisle na úhlu pohledu. Data jsou čtena výhradně z Vrstvy 1 a Vrstvy 2, nikoli z geometrie Blender scény.

**Délky stěn** — pro každou hranu Vrstvy 1 je zobrazena délka jako text umístěný nad středem dané hrany; pozice je přepočítána z 3D souřadnic středu hrany na 2D souřadnice obrazovky pomocí `view3d_utils`. Hodnotaje zobrazena v nastaveném systému jednotek (metrický nebo imperiální).

**Metriky místností** — v centroidu každé místnosti (uzlu Vrstvy 2) jsou zobrazeny dvě hodnoty: název místnosti a plocha v m². Centroid je automaticky přepočítán při každé topologické změně Vrstvy 1. Zobrazení jména místnosti přímo ve viewportu eliminuje potřebu přepínat pohled do N-panelu pro orientaci ve složitějším půdorysu.

## Barevné odlišení místností

Místnosti jsou vizuálně odlišeny průhlednou barevnou výplní jejich plochy vykreslovanou v `POST_VIEW` režimu. Každá místnost dostane odlišnou barvu přiřazenou automaticky. Výplň je poloprůhledná, aby nerušila viditelnost geometrie.

Barevné odlišení slouží především k rychlé orientaci ve viewportu při pohledu seshora — uživatel ihned rozpozná prostorové rozložení bez nutnosti číst texty kóty nebo procházet N-panel. Vzor je rozšířen z architektonických nástrojů jako ArchiCAD (Color by Category) a Revit (Room Colors), kde barevné kódování místností patří k základní orientaci v půdorysu.

Barevná sémantika overlay prvků všeobecně přejímá konvence Blender vlastních nástrojů (Knife Tool, Loop Cut), aby byly pro uživatele Blenderu čitelné bez nutnosti učení:

| Prvek | Barva | Sémantika |
| :--- | :--- | :--- |
| Potvrzené stěny | Světle šedá | Existující hmota — neutrální |
| Preview stěna (FP1) | Modrá | Navrhovaný, nepotvrzený prvek — „zatím není v datech" |
| Snap indikátor u kurzoru | Žlutá | Aktivní přichycení — stav, na nějž se kurzor přichytí |
| Vybraný prvek (stěna, místnost) | Oranžová | Blender konvence pro výběr; uživatel tuto barvu asociuje s aktivním prvkem |
| Chybová indikace | Červená | Neplatná operace — konzistentní s Blender error state barvou |

## Gizmos — interaktivní manipulátory (FP6)

Gizmos jsou interaktivní grafické ovládací prvky zobrazované přímo ve viewportu při výběru prvku — umožňují přímou geometrickou manipulaci taháním myší bez přepínání nástrojů nebo otevírání dialogů. Vzor je zaveden v Archipack, kde při výběru stěny se automaticky zobrazí táhla pro tloušťku a výšku. SketchUp zobrazuje táhlo délky při přesunutí myši nad hranu. Společným principem je zkrácení interakčního cyklu: bez gizmů by úprava tloušťky stěny vyžadovala klik na stěnu, přepnutí do N-panelu, nalezení pole tloušťky a zadání hodnoty — s gizmem stačí uchopit šipku a táhnout.

Podmínky zobrazení gizmos (metoda `poll()` v `GizmoGroup`) zabraňují vizuálnímu smogu při práci s větším počtem prvků — gizmos jsou aktivní pouze při výběru konkrétního prvku, nikoliv globálně. Technické detaily Gizmo API jsou rozebrány v [technické analýze Gizmo systému](../02_Analysis/06_ta_ui.md).

Addon definuje tři typy gizmos:

**Manipulátor tloušťky stěny(Světle modrá barva)** — obousměrná šipka kolmá na osu vybrané stěny vykreslená v rovině XY; jsou zobrazeny dvě šipky (jedna na každou stranu stěny) ze středu stěny. Pohyb je omezen kolmo na osu stěny. Táhnutím se aktualizuje `wall_thickness` ve Vrstvě 1, Vrstva 3 synchronizuje atributy, Geometry Nodes okamžitě regeneruje geometrii. Topologie (junctiony, logické sousedství stěn) zůstává nezměněna.

**Manipulátor výšky stěny(Zelená barva)** — svislá šipka na středu vybrané stěny, pohyb omezen na osu Z. Táhnutím se aktualizuje `wall_height` ve Vrstvě 1. Z-souřadnice junctionů ve Vrstvě 1 se nemění (Vrstva 1 je striktně 2D planární graf); výška je uložena jako atribut hrany, nikoliv jako souřadnice vrcholu.

**Manipulátor pohybu junctionu(žlutá barva)** — kruh na vybraném junctionu, pohyb omezen přísně na rovinu XY (Z-složka tahu je zahozena). Táhnutím se přepočítají souřadnice junctionu ve Vrstvě 1, přepočítají se délky a úhly všech připojených stěn, spustí se detekce cyklů a Vrstva 2 a Vrstva 3 synchronizují stav. Omezení pohybu do roviny XY je kritické pro zachování planarity Vrstvy 1 — bez tohoto omezení by mohlo dojít ke stavu, kde strukturální graf přestane být planární a detekce místností selže.
