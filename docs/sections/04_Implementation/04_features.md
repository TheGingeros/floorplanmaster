# 4.4 Funkce

Funkce addonu jsou implementovány jako Blender operátory — spustitelné příkazy registrované u Blenderu a přiřazené klávesovým zkratkám nebo tlačítkům panelu. Každý operátor pracuje výhradně přes rozhraní datových vrstev a tvoří tak řídicí vrstvu (Controller) MVC architektury popsané v návrhu. Operátory nestojí na sobě navzájem — každý je samostatnou jednotkou, přistupující ke sdílené cache grafů a sdílenému stavu výběru přes definovaná rozhraní.

## FP1 — Nástroj tužka

Nástroj tužka je primárním způsobem kreslení stěn a je implementován jako modální operátor. Operátor funguje jako stavový automat se dvěma stavy. V prvním čeká na určení výchozího bodu nové stěny; ve druhém táhne náhledovou linku od posledního potvrzeného vrcholu ke kurzoru a čeká na potvrzení dalšího bodu. Každé potvrzení vrcholu zapíše novou entitu do Vrstvy 1; stiskem klávesy pro zrušení posledního kroku je tato entita odstraněna a operátor se vrátí o jeden krok zpět. Ukončení sekvence — klávesou nebo uzavřením smyčky — spustí finální synchronizaci: Vrstva 3 zapíše výsledný mesh a Geometry Nodes generují 3D geometrii.

Tento návrh odhalil výkonnostní problém: pokud by se po každém potvrzeném vrcholu spustila plná synchronizace Vrstvy 3 (přepočet všech stěnových obrysů, zápis atributů, reevaluace GN modifikátoru), rostla by cena každého kliknutí lineárně s počtem stěn v grafu — celková cena za nakreslenou sekvenci W stěn by dosahovala O(W²). FloorPlanMaster tento problém řeší odsunutím synchronizace na konec celé kreslicí sekvence. Během kresby udržuje operátor pouze čistě Python výpočet aktuálních stěnových obrysů — bez jakékoliv závislosti na Blenderu — a zobrazuje je jako okamžitou vizuální odezvu ve viewportu. Celková cena klesla na O(W) za celou sezení, přičemž vizuální odezva zůstala okamžitá.

Při spuštění operátor zaregistruje své kreslicí funkce v centrálním overlay manageru (viz 4.5), uloží aktuální pohled kamery a přepne viewport do horní ortografické projekce. Po ukončení jsou kreslicí funkce odregistrovány a pohled je obnoven.

## FP2 — Výběr a parametrické úpravy

Interaktivní editace běží v dedikovaném FloorPlan módu (Shift+Q), který je implementován jako modal controller nad viewportem. Tento režim přebírá ne-navigační události, chrání před nechtěnými globálními zkratkami a centralizuje klikací výběr stěn i místností. Výběr funguje nezávisle na pohledu kamery: implementace testuje klik vůči projekci šesti ploch 3D tělesa stěny (top, bottom, čtyři boky), takže funguje i v perspektivním pohledu.

Výsledek výběru se zapisuje do sdíleného SelectionState a N-panel okamžitě zobrazuje parametry vybrané entity. Parametrické úpravy stěn pokrývají nejen tloušťku a výšku, ale i polohu: samostatnou editaci obou koncových vrcholů (Start/End XY) a posun stěny po normále přes ovladač středu. Callbacky používají guard flagy proti cyklickým update voláním a pro rychlé tahání sliderů je nasazen debounced sync.

Synchronizační cesta pro editace stěn je optimalizovaná: změna pouze výšky se aplikuje lokálním přepisem atributů bez rebuildu topologie, zatímco změna tloušťky přepíná na plný přepočet. Uživatel tak dostává okamžitou odezvu i při kontinuální editaci.

Přidávání otvorů vynucuje geometrická omezení už při zadávání: otvor nesmí přesáhnout délku stěny, nesmí vstoupit do junction inset zón a nesmí se překrývat s jiným otvorem. Dialog průběžně clampuje hodnoty tak, aby nikdy nevznikl neplatný stav. Součástí FP2 jsou i destruktivní operace: odstranění vybrané stěny a odstranění místnosti při zachování sdílených stěn sousedních místností.

Vložení místnosti umístí pravoúhlý půdorys na aktuální pozici 3D kurzoru se zadanými rozměry jako transakci Vrstvy 1.

## FP3 — Metadata místností

Jakmile Vrstva 2 detekuje novou uzavřenou smyčku stěn, vytvoří odpovídající objekt místnosti s automaticky vypočítanou plochou, obvodem a polohou centroidu. Uživatel může místnosti procházet v N-panelu, kde je zobrazen jejich seznam s klíčovými metrikami, a každou místnost přejmenovat. Přejmenování probíhá obousměrně: změna provedená v panelu se zapíše do grafu místností a zároveň se persistuje do Blender objektu tak, aby přežila rekonstrukci grafů po reloadu nebo Undo.

Implementace pokrývá základní identifikaci, přejmenování a zobrazení klíčových metrik. Plná správa sémantických atributů místností ve smyslu celého návrhu — materiály, typy povrchů, hierarchie prostorů — tato verze addonu neimplementuje.

## FP4 — Finalizace a bake

FP4 je implementováno operátorem Bake, který převádí parametrický FloorPlan objekt na statický mesh připravený pro další práci nebo exportní pipeline Blenderu. Operátor před bake nejprve rekonstruuje grafy z autoritativního stavu objektu, potom vygeneruje finální geometrii přes specializovaný mesh builder a odstraní procedurální identitu objektu. Uživatel může zvolit nedestruktivní variantu (ponechat originál a vytvořit baked kopii) i destruktivní variantu.

Finalizační krok zahrnuje i cleanup dat: převod corner float2 atributů na UV vrstvy, volitelné odstranění named attributes a přiřazení výchozího materiálu. Součástí implementace je také ochrana vstupu do Edit Mode: při pokusu o přechod do mesh editace se zobrazí varovný dialog s volbami Cancel, Bake nebo Lose Data, aby přechod ze sémantického modelu na běžný mesh byl vždy explicitní.

## Neimplementované funkce

V aktuální verzi zůstávají neimplementované kontextové menu (FP5), 3D manipulátory (FP6) a automatické kótování (FP7). Export jako samostatný cílový výstupní krok nad rámec bake workflow také není dokončen. Architektura je však navržena tak, aby šlo tyto části doplnit jako izolované operátory bez zásahu do datového jádra.
