# 4.3 Vrstvy

Třívrstvá hybridní architektura tvoří datové a výpočetní jádro addonu. Vrstva 1 modeluje topologii stěn jako planární 2D graf, Vrstva 2 nad ní buduje sémantický duální graf místností, Vrstva 3 přenáší výsledky obou grafů do Blenderu prostřednictvím pojmenovaných atributů a Geometry Nodes modifikátor z těchto atributů generuje finální 3D geometrii. Každá vrstva je implementována v samostatném souboru a závislostní tok mezi nimi je přísně jednosměrný: Vrstva 1 → Vrstva 2 → Vrstva 3 → Geometry Nodes.

## Vrstva 1 — Strukturální graf

Vrstva 1 reprezentuje půdorys jako planární 2D graf uzlů (junctions) propojených hranami (walls). Junction je vrchol se souřadnicemi v rovině XY; Wall je hrana nesoucí geometrické parametry — tloušťku, výšku a seznam otvorů (dveří a oken). Každá entita dostane při vzniku universally unique identifier (UUID), který ji jednoznačně identifikuje po celou dobu životnosti, a to i přes operace uložení a načtení souboru.

Za správu těchto entit zodpovídá grafová struktura implementovaná nad knihovnou NetworkX. Nabízí operace pro vkládání a odstraňování vrcholů a hran se zabudovanou validací na hranici s Controllerem: pokud uživatel požaduje stěnu kratší než povolené minimum (0,05 m), přidání duplicitní stěny nebo umístění vrcholu na již obsazenou pozici, grafu tuto operaci odmítne dříve, než zapíše cokoliv do svého stavu, a vrátí chybu s konkrétním kódem problému. Datový model je tak vždy v platném stavu — nevzniká potřeba ověřovat konzistenci na více místech.

Pro efektivní detekci duplicitních pozic vrcholů udržuje graf prostorový index: slovník mapující zaokrouhlené souřadnice na identifikátor existujícího junctionu. Kontrola při vložení je tak operací v konstantním čase namísto lineárního procházení celého grafu.

Topologicky nejnáročnější operací Vrstvy 1 je detekce minimálních cyklů — uzavřených smyček stěn vymezujících plochy místností. Implementace využívá planární embedding z NetworkX: z aktuálního grafu stěn se nejprve odstraní listové uzly (vrcholy napojené pouze na jednu stěnu, které nemohou být součástí cyklu), nad takto ořezaným grafem se zkonstruuje planární embedding a z něj se extrahují hraniční cykly. Výsledkem je deterministická sada minimálních uzavřených smyček — každá potenciálně definuje jednu místnost. Výsledek je cachovaný a invalidovaný jen při změně topologie, aby se opakované dotazy na cykly nemusely vždy přepočítávat od začátku.

## Vrstva 2 — Graf místností

Vrstva 2 je sémantický duální graf Vrstvy 1: každé uzavřené smyčce stěn odpovídá jeden uzel (Room) a každé sdílené stěně mezi dvěma místnostmi odpovídá jedna hrana (Adjacency). Room nese identifikátor, jméno, typ místnosti, plochu, obvod, centroid a výšku. Adjacency popisuje, jak jsou dvě místnosti propojeny — zda je stěna plná, nebo zda obsahuje otvor.

Vrstva 2 sama o sobě žádnou místnost nevytváří ani neodstraňuje — veškeré změny pocházejí ze synchronizace s Vrstvou 1. Tato tzv. líná synchronizace probíhá vždy po dokončení operace, která modifikuje Vrstvu 1: Vrstva 2 vyžádá seznam minimálních cyklů z aktuálního grafu, porovná je s množinou stávajících místností a provede odsouhlasení stavu — nové cykly dostanou nové Room objekty, cykly jež zmizely jsou odstraněny, zachované zůstávají beze změny. Díky porovnávání na základě kanonického klíče každého cyklu (setříděná množina hran) jsou Room objekty se svými metadaty stabilní po celou dobu, po kterou odpovídající cyklus v topologii existuje. Přidání nesouvisející stěny tedy nijak nenarušuje identitu dříve vzniklých místností.

Plocha, obvod a centroid každé místnosti jsou vypočítány přímo z pozic vrcholů tvořících cyklus pomocí Gaussovy formulace (shoelace) a standardního výpočtu těžiště polygonu. Výsledky jsou přepočítány při každé synchronizaci a uloženy přímo v objektu místnosti. Detekce sousedství probíhá analogicky — po každé synchronizaci se pro každou dvojici místností sdílejících alespoň jednu stěnu vytvoří nebo zaktualizuje Adjacency.

## Vrstva 3 — Synchronizace s Blenderem

Vrstva 3 překládá data z Python grafů do formátu, který Blender a Geometry Nodes rozumějí. Synchronizace probíhá ve dvou fázích, přičemž obě operují nad jediným Blender mesh objektem — tzv. base mesh půdorysu.

První fáze rekonstruuje topologii meshe: pro každou stěnu vypočítá čtyřúhelníkový obrys (quad polygon) v rovině XY a přidá ho jako polygonální plochu meshe. Pro každou místnost přidá odpovídající podlahový polygon. Výpočet obrysu stěny je geometricky nejnáročnější částí celé Vrstvy 3: na každém konci stěny je potřeba rozhodnout, jak se setkají obrysy sousedních stěn v místě napojení. Je-li junction sdílen více stěnami, obrys každé z nich se prodlouží nebo zkrátí tak, aby průsečík sousedních obrysů tvořil přesnou rohovou pozici — tzv. miter joint. Je-li junction volný konec, obrys se uzavře kolmou úsečkou. Tímto mechanismem vznikají geometricky korektní spoje bez viditelných mezer ani přesahů, a to pro libovolné úhly napojení stěn.

Druhá fáze ukládá na jednotlivé plochy meshe pojmenované atributy — datové kanály přístupné přímo ze Geometry Nodes. Každá plocha dostane příznak, zda je stěnou nebo místností, číselné identifikátory stěny a místnosti a hodnotu výšky stěny platné pro danou plochu. Protože pojmenované atributy na plochách meshe nepodporují textové řetězce, jsou UUID entity překládána na stabilní celá čísla skrze interní mapovač, který pro dané UUID vždy vrátí stejné číslo po celou dobu sezení.

Protože Blender nativní Undo a Redo operuje na úrovni mesh dat, nikoliv Python objektů, může se Python cache grafů po operaci Undo rozejít s aktuálním stavem meshe. Vrstva 3 proto poskytuje mechanismus, který celý strukturální graf i graf místností přebuduje z pojmenovaných atributů aktuálního meshe. Každý operátor zaznamenávající Undo krok tuto rekonstrukci provede na svém začátku — mesh je autoritativní zdroj, Python cache je výhradně pracovní kopie.

Jména místností nelze uložit jako pojmenovaný atribut (ten je vázán na plochu meshe, nikoliv na místnost jako celek), ukládají se proto jako vlastnosti přmo na Blender objektu, které se při rekonstrukci grafů obnoví.

## Geometry Nodes — vizualizace

Geometry Nodes modifikátor čte 2D base mesh připravený Vrstvou 3 a generuje z něj finální 3D geometrii stěn. GN strom je sestaven programaticky při první aktivaci addonu a uložen v datovém bloku Blenderu. Verzování stromu zajišťuje, že zastaralá verze se při potřebě automaticky přebuduje — uživatel nemusí modifikátor ručně resetovat.

Tok zpracování uvnitř GN stromu postupuje přes tři separační kroky. Nejprve jsou z celkového meshe izolovány plochy stěn, které jsou následně extrudovány kolmo vzhůru — každá stěna je extrudována o hodnotu uloženou v jejím per-face atributu výšky, takže každá stěna může mít jinou výšku bez globálního nastavení. Ze zbývajících ploch jsou odděleny plochy otvorů (dveří a oken). Ty jsou také extrudovány, aby tvořily trojrozměrná tělesa vhodná pro operaci odčítání. Pomocí Mesh Boolean se tato tělesa odečtou od příslušných stěn — výsledkem jsou stěny s geometricky správnými výřezy pro dveře a okna. Nakonec jsou stěny sloučeny s podlahovými plochami místností a předány na výstup modifikátoru.

Celé zpracování probíhá v C++ jádře Blenderu a je automaticky reevaluováno při každé změně vstupního meshe nebo atributů. Python strana stačí aktualizovat data a Blender vizualizaci zajistí — tento princip je základem zpětné vazby v reálném čase popsané v návrhu.
