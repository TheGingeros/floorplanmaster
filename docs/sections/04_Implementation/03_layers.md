# 4.3 Vrstvy

Třívrstvá architektura tvoří výpočetní páteř addonu. Porozumět jejímu fungování nejlépe umožňuje sledovat konkrétní událost: uživatel potvrdí nový vrchol v tužkovém nástroji a čeká, až se ve viewportu zhmotní nová stěna. Tato zdánlivě jednoduchá akce projde všemi třemi vrstvami a nakonec spustí reevaluaci Geometry Nodes modifikátoru v C++ jádru Blenderu. Závislostní tok vrstev je přísně jednosměrný — Vrstva 1 poskytuje data Vrstvě 2, ta Vrstvě 3, která připraví vstup pro Geometry Nodes — zpětný tok neexistuje.

## Vrstva 1 — Strukturální graf

První vrstva přijme požadavek na přidání nového vrcholu a stěny a ještě než cokoliv zapíše do svého stavu, provede sadu validačních kontrol na vstupní hranici: zda nová stěna není příliš krátká, zda na zadaných souřadnicích již neexistuje jiný vrchol, zda nevznikne duplicitní stěna. Pokud jakákoliv kontrola selže, vrstva požadavek odmítne a vrátí specifický chybový kód — grafová struktura zůstane beze změny v platném stavu. Toto pravidlo platí bez výjimky pro všechny operace zápisu: validace probíhá vždy na vstupní hranici, nikdy uvnitř interní logiky. Výsledkem je silný invariant — datový model je v libovolném okamžiku topologicky správný a konzistenci není třeba ověřovat na více místech kódu.

Pro efektivní vyhledávání blízkých vrcholů — operaci klíčovou pro funkci přichycení v tužkovém nástroji — udržuje Vrstva 1 prostorový index v podobě slovníku mapujícího zaokrouhlené souřadnice na identifikátor existujícího vrcholu. Dotaz na vrcholy v blízkosti dané polohy je tak operací v konstantním čase, nezávislou na celkovém počtu vrcholů v grafu.

Každá entita — vrchol i stěna — dostane při vzniku universally unique identifier. UUID identifikuje entitu jednoznačně po celou dobu životnosti projektu, a to i přes uložení a načtení souboru. Tato stabilita identifikátorů je podmínkou správné funkce výběru ve viewportu, sledování příslušnosti otvorů k stěnám i fungování mapovače, který UUID překládá na kompaktní celá čísla pro komunikaci s Geometry Nodes.

Topologicky nejnáročnější operací Vrstvy 1 je detekce minimálních cyklů — uzavřených stěnových smyček vymezujících potenciální místnosti. Implementace vychází z planárního embeddingu konstruovaného nad knihovnou NetworkX: nejprve jsou z grafu odstraněny listové vrcholy, které součástí žádného cyklu být nemohou; poté se zkonstruuje planární embedding a z jeho hraniční struktury se extrahují všechny minimální ohraničené oblasti. Výsledkem je deterministická sada smyček. Výsledek je cachovaný a invaliduje se pouze při změně topologie — průběžné dotazy na seznam cyklů se tak nemusejí přepočítávat při každém pohybu myši.

## Vrstva 2 — Graf místností

Vrstva 2 reaguje na dokončení operace v Vrstvě 1 a synchronizuje svůj stav s aktuálním seznamem minimálních cyklů. Tato synchronizace je záměrně líná — neprobíhá průběžně při každé dílčí změně, ale vždy až po dokončení celé uživatelské operace. Synchronizace porovná aktuální sadu cyklů s množinou stávajících místností na základě kanonického klíče každého cyklu — setříděné množiny jeho hraničních stěn. Nové smyčky dostanou nové objekty místností; smyčky, které ze topologie zmizely, jsou odstraněny spolu se svými metadaty; zachované smyčky zůstávají nedotčeny — jejich jméno, typ a ostatní atributy jsou stabilní.

Tato stabilita identit místností není vedlejším efektem, ale záměrným architektonickým rozhodnutím. Přidání nové, nesouvisející stěny na druhém konci půdorysu nesmí způsobit, že dříve pojmenovaná místnost ztratí svůj identifikátor nebo metadata. Destrukce identity místnosti nastane jedině tehdy, pokud se topologie její hraniční smyčky skutečně změní.

Plocha, obvod a centroid každé místnosti jsou přepočítány ze souřadnic vrcholů příslušné smyčky při každé synchronizaci — jsou odvozené veličiny, nikoliv primárně uložená data, a proto nikdy nemohou být zastaralé. Sousedství místností je detekováno analogicky: po každé synchronizaci jsou pro každou dvojici místností sdílejících alespoň jednu stěnu vytvořeny nebo aktualizovány záznamy sousedství.

## Vrstva 3 — Synchronizace s Blenderem

Vrstva 3 překládá Python datový model do formátu, jemuž Blender a Geometry Nodes rozumějí. Jejím výstupem je jeden Blender mesh objekt — tzv. base mesh půdorysu — nesoucí veškerou topologii a parametry ve formě pojmenovaných atributů čitelných přímo z GN stromu.

Synchronizace probíhá ve dvou fázích. V první fázi se rekonstruuje geometrie meshe od základu: pro každou stěnu se vypočítá přesný čtyřúhelníkový obrys v rovině XY. Tato geometrická operace je nejnáročnějším krokem celé synchronizační vrstvy: na každém konci stěny je třeba správně vyřešit, jak se setkají obrysy sousedních stěn. Algoritmus řeší tuto úlohu metodou angular-sort — seřadí všechny stěny napojené na daný vrchol v pořadí jejich úhlů (CCW) a pro každý sousední pár stěn vypočítá průsečík jejich bočních obrysových přímek. Výsledný rohový bod leží přesně tam, kde se boky sousedních stěn geometricky setkávají — bez mezer ani přesahů, pro libovolný úhel napojení. Na vrcholech se třemi a více stěnami doplní algoritmus přesný výplňový polygon pokrývající plochu křížení a uzavírající tak geometricky otevřené horní plochy složitých spojů. Plochy otvorů — dveří a oken — jsou přidány jako samostatné box polygony, které v pozdější fázi slouží jako geometrické cuttery pro Boolean operaci.

Ve druhé fázi jsou na jednotlivé plochy meshe zapsány pojmenované atributy: příznak příslušnosti plochy ke stěně, otvoru nebo podlaze; číselné identifikátory stěny a místnosti odvozené z UUID přes mapovač; a výška stěny jako per-face hodnota, jež umožňuje každé stěně nést jinou výšku bez globálního nastavení. Psaní atributů probíhá přes nativní atributové API Blenderu po dokončení topologie — tím se zaručí dostupnost hodnot v Geometry Nodes uzlech při reevaluaci.

Protože Blender při operaci Undo/Redo obnoví předchozí stav mesh geometrie a atributů, ale Python pracovní kopie grafů tuto obnovu automaticky nereflektuje, platí pro celou Vrstvu 3 pravidlo autoritativního zdroje: mesh je vždy pravdivý zdroj, Python grafová cache je jen provizorní výpočetní kopie. Každý operátor proto na svém začátku přebuduje pracovní grafy přímo z aktuálního stavu meshe.

## Geometry Nodes — generování 3D geometrie

Geometry Nodes modifikátor přebírá od Vrstvy 3 připravený 2D base mesh a autonomně generuje finální trojrozměrnou geometrii. GN strom je sestaven programaticky při první aktivaci addonu; pro detekci zastaralých verzí nese strom číslo verze — pokud se číslo po aktualizaci addonu neshoduje s očekávanou hodnotou, strom se automaticky přebuduje bez zásahu uživatele.

Tok zpracování uvnitř stromu probíhá přes tři separační větve. Z celkového base meshe jsou nejprve izolovány plochy stěn; ty jsou extrudovány kolmo vzhůru, přičemž každá plocha nese vlastní výšku v per-face atributu — různé výšky stěn tak nevyžadují žádné globální nastavení. Paralelně jsou izolovány plochy otvorů, které jsou extrudovány do trojrozměrných těles. Tato tělesa jsou operací Boolean Difference odečtena od geometrie stěn — vznikají stěny s geometricky přesnými výřezy pro dveře a okna. Výsledek je sloučen s podlahovými plochami místností a předán na výstup modifikátoru.

Celé zpracování probíhá v C++ jádru Blenderu a je automaticky reevaluováno při každé změně base meshe nebo jeho atributů. Jakmile Vrstva 3 dokončí synchronizaci, Blender reevaluje GN modifikátor bez explicitního volání — tím vzniká reaktivní vizualizační smyčka popsaná v návrhu: Python strana aktualizuje data, vizualizaci zajistí Blender.
