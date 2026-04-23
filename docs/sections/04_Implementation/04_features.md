# 4.4 Funkce

Funkce addonu jsou implementovány jako Blender operátory — Python třídy registrované u Blenderu, které uživatel spouští z panelu, klávesové zkratky nebo kontextového menu. Každý operátor odpovídá jednomu funkčnímu požadavku (FP1–FP7) a pracuje výhradně přes rozhraní Vrstvy 1 a 2, nikoliv přímo s Blender mesh daty.

## FP1 — Tužkový nástroj

Tužkový nástroj je primární způsob kreslení stěn. Je implementován jako modální operátor — typ Blender operátoru, který po spuštění nezanikne okamžitě, ale drží kontrolu nad událostmi viewportu (kliknutí, pohyb myši, klávesy) až dokud ho uživatel explicitně neukončí. Toto chování je pro interaktivní kreslení nezbytné a Blender jej pro tyto účely nativně podporuje.

Operátor funguje jako stavový automat se dvěma stavy. V prvním stavu čeká na umístění prvního vrcholu; ve druhém táhne linku od posledního umístěného vrcholu ke kurzoru. Kliknutím levým tlačítkem myši se potvrdí nový vrchol a propojující stěna se zapíše do Vrstvy 1; pravé tlačítko přeruší aktuální linku a vrátí operátor do stavu čekání; klávesa Enter uzavře sekvenci a stěny se synchronizují do Blenderu; Escape celou operaci zruší bez potvrzení.

Při každém pohybu myši operátor prohledá okolí kurzoru a hledá existující vrcholy v dosahu snapping tolerance (15 pixelů). Pokud takový vrchol najde, nabídne přichycení — linka se zachytí přesně na vybraný vrchol a případné kliknutí ho využije místo vytvoření nového. Tímto způsobem uživatel přirozeně napojuje stěny na existující síť bez nutnosti přesného kliknutí na pixel.

Operátor při spuštění uloží aktuální pohled kamery a přepne viewport do horní ortografické projekce — standardního pohledu pro 2D kreslení půdorysu. Po ukončení operátoru je pohled obnoven do původní polohy. Veškeré GPU vykreslování probíhá přes centralizovaný overlay manager (viz 4.5): operátor při spuštění zaregistruje své kreslicí funkce a při ukončení je odstraní. Vizuálně operátor zobrazuje náhledovou linku probíhající stěny, zvýraznění potvrzených stěn aktuální sekvence a indikátor aktivního snap cíle. Ve stavovém řádku Blenderu se zobrazují nápovědy dostupných ovládacích prvků.

## FP2 — Výběr a parametrické úpravy

Výběr stěn a místností probíhá kliknutím levým tlačítkem myši v 3D viewportu. Operátor projikuje všechny stěny a místnosti do prostoru 2D souřadnic okna a testuje, zda kliknutá pozice leží uvnitř jejich průmětného polygonu. Protože stěny jsou trojrozměrná tělesa (obdélníkový průřez extrudovaný do výšky), testuje se průmět všech šesti ploch — čelní, zadní a čtyři boky — aby výběr fungoval i při šikmém pohledu a ne jen z pohledu shora. Pokud kliknutí zasáhne více stěn (jejich průměty se na obrazovce překrývají), vybrána bude ta nejblíže kameře.

Výsledek výběru je uložen do sdíleného stavu výběru (viz 4.5) a N-panel se okamžitě aktualizuje, aby zobrazil parametry vybraného prvku. Parametrické úpravy stěny — tloušťka a výška — probíhají přes live update mechanismus vlastností: kdykoli uživatel změní hodnotu v N-panelu, odpovídající změna se okamžitě promítne do Vrstvy 1 a spustí synchronizaci Vrstvy 3. Změna je viditelná ve viewportu v reálném čase bez nutnosti potvrzovat.

Otvory (dveře a okna) se přidávají operátorem dostupným z N-panelu při vybrané stěně. Po spuštění se zobrazí panel pro nastavení parametrů: typ otvoru, šířka, výška, výška parapetu a pozice podél stěny. Parametry jsou průběžně korigovány tak, aby výsledný otvor nepřesahoval délku stěny a nepřekrýval jiný existující otvor — dialogové okno nikdy neukazuje geometricky neplatný stav.

Vložení místnosti umístí pravoúhlou místnost se středem v aktuální poloze 3D kurzoru. Uživatel zadá rozměry a parametry stěn; k dispozici je funkce Redo pro zpětnou úpravu parametrů.

## FP3 — Metadata místností

V současné implementaci je realizována základní část práce s metadaty místností. Jakmile Vrstva 2 detekuje novou místnost, vytvoří pro ni objekt nesoucí jméno, plochu, obvod, centroid a výšku. Tato data se následně zobrazují v uživatelském rozhraní a tvoří základ pro další práci s místnostmi.

Uživatel může místnosti procházet v sekci **Místnosti** v N-panelu, kde se zobrazuje jejich seznam, aktuální jméno a plocha. Každou položku lze rozbalit, zvýraznit ve viewportu a přejmenovat. Přejmenování probíhá obousměrně: změna provedená v panelu se zapíše do grafu místností a zároveň se perzistuje do Blender objektu tak, aby zůstala zachována i po opětovném načtení nebo rekonstrukci datového modelu.

Při výběru místnosti přímo ve viewportu se zobrazí samostatný panel **Selected Room**, který zpřístupní aktuální jméno a základní souhrnné údaje o místnosti — plochu, obvod, počet stěn a výšku. Implementace tedy v této fázi nepokrývá plnou správu sémantických atributů místností v rozsahu celého návrhu, ale základní identifikace, přejmenování a zobrazení klíčových metrik již funkční jsou.

## FP4 — Finalizace

*(todo — není implementováno)*

## FP5 — Kontextové menu

*(todo — není implementováno)*

## FP6 — Gizma

*(todo — není implementováno)*

## FP7 — Kótování

*(todo — není implementováno)*
