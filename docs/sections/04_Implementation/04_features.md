# 4.4 Funkce

Funkce addonu jsou implementovány jako Blender operátory — spustitelné příkazy registrované u Blenderu a přiřazené klávesovým zkratkám nebo tlačítkům panelu. Každý operátor pracuje výhradně přes rozhraní datových vrstev a tvoří tak řídicí vrstvu (Controller) MVC architektury popsané v návrhu. Operátory nestojí na sobě navzájem — každý je samostatnou jednotkou, přistupující ke sdílené cache grafů a sdílenému stavu výběru přes definovaná rozhraní.

## FP1 — Tužkový nástroj

Tužkový nástroj je primárním způsobem kreslení stěn a je implementován jako modální operátor — druh Blender operátoru, který po spuštění nepředá řízení zpět okamžitě, ale drží kontrolu nad událostmi viewportu až do explicitního ukončení. Toto chování je pro interaktivní kreslení nezbytné; Blender je nativně podporuje pro právě tento typ scénáře.

Operátor funguje jako stavový automat se dvěma stavy. V prvním čeká na určení výchozího bodu nové stěny; ve druhém táhne náhledovou linku od posledního potvrzeného vrcholu ke kurzoru a čeká na potvrzení dalšího bodu. Každé potvrzení vrcholu zapíše novou entitu do Vrstvy 1; stiskem klávesy pro zrušení posledního kroku je tato entita odstraněna a operátor se vrátí o jeden krok zpět. Ukončení sekvence — klávesou nebo uzavřením smyčky — spustí finální synchronizaci: Vrstva 3 zapíše výsledný mesh a Geometry Nodes generují 3D geometrii.

Tento návrh odhalil výkonnostní problém: pokud by se po každém potvrzeném vrcholu spustila plná synchronizace Vrstvy 3 (přepočet všech stěnových obrysů, zápis atributů, reevaluace GN modifikátoru), rostla by cena každého kliknutí lineárně s počtem stěn v grafu — celková cena za nakreslenou sekvenci W stěn by dosahovala O(W²). FloorPlanMaster tento problém řeší odsunutím synchronizace na konec celé kreslicí sekvence. Během kresby udržuje operátor pouze čistě Python výpočet aktuálních stěnových obrysů — bez jakékoliv závislosti na Blenderu — a zobrazuje je jako okamžitou vizuální odezvu ve viewportu. Celková cena klesla na O(W) za celou sezení, přičemž vizuální odezva zůstala okamžitá.

Při spuštění operátor zaregistruje své kreslicí funkce v centrálním overlay manageru (viz 4.5), uloží aktuální pohled kamery a přepne viewport do horní ortografické projekce. Po ukončení jsou kreslicí funkce odregistrovány a pohled je obnoven.

## FP2 — Výběr a parametrické úpravy

Výběr stěn probíhá kliknutím myší ve viewportu. Správná identifikace zasažené stěny vyžaduje řešení, které funguje nezávisle na aktuálním pohledu kamery — tedy nejen z pohledu shora, ale i z libovolné šikmé perspektivy. Prostá projekce kliknuté pozice do roviny Z=0 a test vůči 2D obrysům stěn by pro šikmý perspektivní pohled selhala. Implementace proto projikuje všech šest ploch trojrozměrného tělesa každé stěny — spodní, horní a čtyři boky — do 2D souřadnic okna a testuje kliknutou pozici vůči těmto promítnutým polygonům. Výsledkem je přesný výběr bez ohledu na nastavení pohledu.

Výsledek výběru je zapsán do sdíleného stavu výběru a N-panel se okamžitě aktualizuje, aby zobrazil parametry vybrané stěny. Parametrické úpravy — tloušťka a výška — fungují přes mechanismus live update vlastností: Blender při každé změně hodnoty automaticky zavolá zaregistrovanou callback funkci, která provede validaci, zapíše změnu do Vrstvy 1 a spustí synchronizaci Vrstvy 3. Změna se projeví ve viewportu okamžitě, bez nutnosti potvrzovat. Aby programatické naplnění polí panelu hodnotami při výběru stěny nespustilo nechtěnou synchronizaci, chrání tento mechanismus příznak, jehož přítomnost callback funkce detekuje a přeskočí.

Přidávání otvorů pracuje s dalšími omezujícími podmínkami: otvor nesmí přesáhnout délku stěny, nesmí zasahovat do oblasti překryvu spojů sousedních stěn a nesmí se překrývat s jiným existujícím otvorem. Dialogové okno průběžně koriguje zadávané hodnoty tak, aby geometricky neplatný stav nikdy nenastal — výška otvoru se nemění automaticky při zvyšování parapetu a poloha otvoru neovlivňuje jeho šířku. Každá hodnota je korigována nezávisle v rámci svého platného rozsahu.

Vložení místnosti umístí pravoúhlý půdorys místnosti na aktuální polohu 3D kurzoru se zadanými rozměry jako plnohodnotnou transakci Vrstvy 1.

## FP3 — Metadata místností

Jakmile Vrstva 2 detekuje novou uzavřenou smyčku stěn, vytvoří odpovídající objekt místnosti s automaticky vypočítanou plochou, obvodem a polohou centroidu. Uživatel může místnosti procházet v N-panelu, kde je zobrazen jejich seznam s klíčovými metrikami, a každou místnost přejmenovat. Přejmenování probíhá obousměrně: změna provedená v panelu se zapíše do grafu místností a zároveň se persistuje do Blender objektu tak, aby přežila rekonstrukci grafů po reloadu nebo Undo.

Implementace pokrývá základní identifikaci, přejmenování a zobrazení klíčových metrik. Plná správa sémantických atributů místností ve smyslu celého návrhu — materiály, typy povrchů, hierarchie prostorů — tato verze addonu neimplementuje.

## Neimplementované funkce

Operátory pro finalizaci a export (FP4), kontextové menu (FP5), 3D manipulátory (FP6) a automatické kótování (FP7) nebyly v rámci implementace realizovány. Architektura je navržena tak, aby je bylo možné doplnit jako samostatné operátory bez zásahu do datového jádra — jednosměrný závislostní tok tuto rozšiřitelnost přímo garantuje.
