# 4.3 Vrstvy

Třívrstvá architektura tvoří výpočetní jádro addonu. Porozumět jejímu fungování nejlépe umožňuje sledovat konkrétní událost: uživatel potvrdí nový vrchol v tužkovém nástroji a čeká, až se ve viewportu vytvoří nová stěna. Tato zdánlivě jednoduchá akce projde všemi třemi vrstvami a nakonec spustí reevaluaci Geometry Nodes modifikátoru v C++ jádru Blenderu.

## Vrstva 1 — Strukturální graf

První vrstva přijme požadavek na přidání nového vrcholu a stěny a ještě než cokoliv zapíše do svého stavu, provede sadu validačních kontrol na vstupu: zda nová stěna není příliš krátká, zda na zadaných souřadnicích již neexistuje jiný vrchol, zda nevznikne duplicitní stěna. Pokud jakákoliv kontrola selže, vrstva požadavek odmítne a vrátí specifický chybový kód — grafová struktura zůstane beze změny v platném stavu. Toto pravidlo platí pro všechny operace zápisu bez výjimky. Výsledkem je silný invariant — datový model je v libovolném okamžiku topologicky správný a konzistenci není třeba ověřovat na více místech kódu.

Pro efektivní vyhledávání blízkých vrcholů — operaci klíčovou pro funkci přichycení v tužkovém nástroji — udržuje Vrstva 1 prostorový index v podobě slovníku mapujícího zaokrouhlené souřadnice na identifikátor existujícího vrcholu. Dotaz na vrcholy v blízkosti dané polohy je tak operací v konstantním čase, nezávislou na celkovém počtu vrcholů v grafu.

Každá entita — vrchol i stěna — dostane při vzniku universally unique identifier. UUID identifikuje entitu jednoznačně po celou dobu životnosti projektu, a to i přes uložení a načtení souboru. Tato stabilita identifikátorů je podmínkou správné funkce výběru ve viewportu, sledování příslušnosti otvorů k stěnám i fungování mapovače, který UUID překládá na kompaktní celá čísla pro komunikaci s Geometry Nodes.

Planární embedding je reprezentace planárního grafu, která ke každému vrcholu ukládá cyklické pořadí jeho sousedů v rovině. Z tohoto pořadí lze algoritmicky odvodit hranice všech ohraničených oblastí — tzv. faces planárního grafu — aniž by bylo nutné provádět geometrické výpočty. Pro půdorys, jehož stěny tvoří planární graf, odpovídá každá ohraničená oblast právě jedné potenciální místnosti.

Topologicky nejnáročnější operací Vrstvy 1 je detekce minimálních cyklů — uzavřených stěnových smyček vymezujících potenciální místnosti. Implementace vychází z planárního embeddingu konstruovaného nad knihovnou NetworkX: nejprve jsou z grafu odstraněny listy, které součástí žádného cyklu být nemohou; poté se zkonstruuje planární embedding a z jeho hraniční struktury se extrahují všechny minimální ohraničené oblasti. Výsledkem je deterministická sada smyček. Výsledek je cachovaný a invaliduje se pouze při změně topologie — průběžné dotazy na seznam cyklů se tak nemusejí přepočítávat při každém pohybu myši.

## Vrstva 2 — Graf místností

Vrstva 2 reaguje na dokončení operace v Vrstvě 1 a synchronizuje svůj stav s aktuálním seznamem minimálních cyklů. Tato synchronizace je záměrně líná — neprobíhá průběžně při každé dílčí změně, ale vždy až po dokončení celé uživatelské operace. Synchronizace porovná aktuální sadu cyklů s množinou stávajících místností na základě kanonického klíče každého cyklu — setříděné množiny jeho hraničních stěn. Nové smyčky dostanou nové objekty místností; smyčky, které ze topologie zmizely, jsou odstraněny spolu se svými metadaty; zachované smyčky zůstávají nedotčeny — jejich jméno, typ a ostatní atributy jsou stabilní.

Tato stabilita identit místností není vedlejším efektem, ale záměrným architektonickým rozhodnutím. Přidání nové, nesouvisející stěny na druhém konci půdorysu nesmí způsobit, že dříve pojmenovaná místnost ztratí svůj identifikátor nebo metadata. Destrukce identity místnosti nastane jedině tehdy, pokud se topologie její hraniční smyčky skutečně změní.

Plocha, obvod a centroid každé místnosti jsou přepočítány ze souřadnic vrcholů příslušné smyčky při každé synchronizaci — jsou odvozené veličiny, nikoliv primárně uložená data, a proto nikdy nemohou být zastaralé. Sousedství místností je detekováno analogicky: po každé synchronizaci jsou pro každou dvojici místností sdílejících alespoň jednu stěnu vytvořeny nebo aktualizovány záznamy sousedství.

## Vrstva 3 — Synchronizace s Blenderem

Vrstva 3 překládá Python datový model do formátu, jemuž Blender a Geometry Nodes rozumějí. Jejím výstupem je jeden Blender mesh objekt — tzv. base mesh půdorysu — nesoucí topologii i parametry ve formě pojmenovaných atributů čitelných přímo z GN stromu.

Plná synchronizace probíhá ve dvou fázích. V první fázi se mesh rekonstruuje od nuly: pro každou stěnu se vypočítá přesný čtyřúhelníkový obrys v rovině XY přes jádro v `junction_solver.py` (angular-sort nad stěnami v každém vrcholu), aby spoje fungovaly pro libovolné úhly bez mezer a přesahů. Na vrcholech se třemi a více stěnami se doplní výplňový polygon spoje a pro každý otvor se vytvoří šestistěnný cutter box. Současně se dopočte a vloží podlahový polygon místnosti po vnitřní hraně stěn.

Ve druhé fázi se přes `mesh.attributes` zapíší per-face atributy: `is_wall`, `is_opening`, `wall_id`, `wall_height`, `wall_thickness`, `room_id`, `room_area` a `room_perimeter`. Tím je zaručeno, že hodnoty jsou ihned dostupné pro Geometry Nodes. Po zápisu se objekt pouze označí pro přepočet (`update_tag`) a reevaluace proběhne líně při redraw; synchronizace záměrně nevolá explicitní synchronní update depsgraphu.

Vrstva 3 obsahuje i lokální synchronizaci pro editaci parametrů stěny. Pokud se mění pouze výška, přepíše se jen `wall_height` na známých indexech stěnových a junction-fill faces bez rebuildu topologie; změna tloušťky stále spouští plný sync. Pro tento režim se po každém plném syncu udržují mapy `wall UUID -> face index` a `junction UUID -> face index`.

Kvůli Undo/Redo a addon reloadu je mesh primárním zdrojem dat. Python grafy i mapovač UUID se po každém syncu serializují do JSON custom property objektu a při obnově se rekonstruují zpět; operátory tak mohou začít z konzistentního stavu i po návratu v historii nebo po znovunačtení addonu.

## Geometry Nodes — generování 3D geometrie

Geometry Nodes modifikátor přebírá od Vrstvy 3 připravený base mesh a autonomně generuje finální trojrozměrnou geometrii. GN strom je sestaven programaticky při první aktivaci addonu a nese interní číslo verze; při nesouladu verze se strom automaticky přebuduje.

Tok zpracování uvnitř stromu běží ve třech krocích. Nejprve se oddělí stěnové faces (`is_wall == 1`) od zbytku. Ze zbytku se dále oddělí opening cutter faces (`is_opening == 1`) a zbývající část tvoří podlahy. Stěnové faces se extrudují podle per-face hodnoty `wall_height`. Cutter boxy se už v GN neextrudují — do stromu vstupují jako hotová 3D tělesa z Vrstvy 3 a operací Boolean Difference (EXACT) se odečtou od stěn. Výsledek se spojí s podlahovými plochami a pošle na výstup modifikátoru.

Celé zpracování probíhá v C++ jádru Blenderu a je automaticky reevaluováno při každé změně base meshe nebo jeho atributů. Jakmile Vrstva 3 dokončí synchronizaci, Blender reevaluje GN modifikátor bez explicitního volání — tím vzniká reaktivní vizualizační smyčka popsaná v návrhu: Python strana aktualizuje data, vizualizaci zajistí Blender.
