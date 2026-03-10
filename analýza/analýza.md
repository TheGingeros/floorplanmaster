# Analýza
Název projektu: Blender add-on pro parametrické modelování prostorových dispozic

## Definice problému
- tvorba půdorysů a 3D dispozic budov je v čistém Blenderu zdlouhavá a destruktivní

## Cíl projektu
- vytvoření rozšiřovacího modulu pro Blender zaměřený na parametrické modelování prostorových dispozic
- uživatel bude moci prostorové dispozice intuitivně vytvářet a nedestruktivně upravovat pomocí parametrů
- cílem je primárně urychlit ranou fázi architektonického návrhu

## Informační analýza

### Analýza existujících řešení
- [Současné hlavní architektonické rozšiřující moduly pro Blender](./files/existujici_reseni.md#současné-hlavní-architektonické-rozšiřující-moduly-pro-blender)
- [Hlavní architektonické nástroje mimo Blender](./files/existujici_reseni.md#hlavní-architektonické-nástroje-mimo-blender)

### Parametrické modelování
- [Definice](./files/definice.md#parametrické-modelování)

### Prostorové dispozice
- [Definice](./files/definice.md#prostorová-dispozice)

## Cílové skupiny
### Uživatelé
1. [Architekti](./files/cilove_skupiny.md#architekti)
2. [3D Umělci a Vizualizátoři](./files/cilove_skupiny.md#3d-umělci-a-vizualizátoři)
3. [Game Designeři / Level Designeři](./files/cilove_skupiny.md#game-designeři--level-designeři)
### Persony
TODO
### Uživatelské scénáře - use cases
1. [Scénář 1: Vytvoření základní místnosti pomocí kreslení](./files/cilove_skupiny.md#scénář-1-vytvoření-základní-místnosti-pomocí-kreslení)
2. [Scénář 2: Vytvoření základní místnosti pomocí parametrů](./files/cilove_skupiny.md#scénář-2-vytvoření-základní-místnosti-pomocí-parametrů)
3. [Scénář 3: Parametrická úprava místnosti](./files/cilove_skupiny.md#scénář-3-parametrická-úprava-místnosti)
4. [Scénář 4: Vložení otvoru do stěny](./files/cilove_skupiny.md#scénář-4-vložení-otvoru-do-stěny)

## Analýza požadavků
TODO
### Funkční požadavky
1. [Interaktivní tvorba místností a kreslení - Pencil Tool](./files/analyza_pozadavku.md#1-interaktivní-tvorba-místností-a-kreslení---pencil-tool)
2. [Generování a úprava parametrických objektů](./files/analyza_pozadavku.md#2-generování-a-úprava-parametrických-objektů)
3. [Správa prostoru a metadat](./files/analyza_pozadavku.md#3-správa-prostoru-a-metadat)
4. [Finalizační nástroj](./files/analyza_pozadavku.md#4-finalizační-nástroj)

### Nefunkční požadavky
1. [Architektura a technologie](./files/analyza_pozadavku.md#1-architektura-a-technologie)
2. [Výkon a Nedestruktivnost](./files/analyza_pozadavku.md#2-výkon-a-nedestruktivnost)
3. [Použitelnost a UX](./files/analyza_pozadavku.md#3-použitelnost-a-ux)

### Volitelné / Rozšiřující požadavky
1. [Kontextová nabídka](./files/analyza_pozadavku.md#1-kontextová-nabídka)
2. [Interaktivní 3D manipulátory](./files/analyza_pozadavku.md#2-interaktivní-3d-manipulátory)
3. [Automatické kótování](./files/analyza_pozadavku.md#3-automatické-kótování)

## Návrh UI
TODO
## Technická analýza a návrh architektury
TODO



## Současné pracovní postupy
- při vytváření jednoduchého půdorysu v SketchUpu uživatel nakreslí obdélník, napíše rozměry a nástrojem Push/Pull vytáhne stěny
- v blenderu bez doplňků stejná operace vyžaduje řadu kroků:
    - přidání roviny
    - vstup do edit modu
    - posun podle souřadnic
    - vysunutí / extrude
    - přidání např. modifikátoru solidify pro tloušťku
- každý z tento kroků zvyšuje šanci chyby a zpomaluje kreativní tok

- potřeba parametrické inteligence bez BIM detailů
- addon musí umožnit tvorbu inteligentní geometrie bez složitých náležitostí BIM
- geometry first:
    - umožní uživateli soustředit se na estetiku a proporce
    - umožní iterativně vytvářet chytrou geometrii rychle a intuitivně
- existence BIM základů jako např. automatický výpočet plochy, což se např. architektům hodí znát okamžitě při návrhu

## Požadované funkce - funční požadavky

### 1. Kreslící nástroj typu "Pencil"
- napříč všemi uživ. skupinami je poptávka po možnosti kreslit stěny interaktivně
- režim by měl fungovat v modálním režimu podobně jako nástroj Knife nebo Grease Pencil
    - modální režim je stav, kdy konkrétní nástroj dočasně převezme plnou kontrolu nad vstupem, dokud se práce nebo modul neukončí
    - změna kurzoru myši na tužku
    - kliknutí myši už nevybírá objekt ve scéně ale začíná kreslit zeď
    - nástroj nedělá jednu věc, čeká na sérii kroků - klik -> pohyb myší -> klik -> pohyb -> atd.
    - specifická klávesová zkratka
- **Interativní délka a úhel:**
    - při kreslení se zobrazují dynamické kóty a uživatel by měl mít možnost zadat přesnou délku pomocí kláves
- **Zarovnání/snapping:**
    - systém musí podporovat inteligentní přichytávání k osám, k existujícím vrcholům a k prodloužením hran, což je základem rychlosti SketchUpu
- **Tloušťka a zarovnání stěny:**
    - uživatel musí mít možnost přepínat mezi kreslením stěny na středovou osu, vnitřní nebo vnější líc přímo během procesu kreslení

### 2. Parametrické stavební objekty
- každý objekt generovaný addon musí zůstat editovatelný prostřednictvím panelu vlastností nebo interaktivních manipulátorů v 3D okně

- **a. Stěny:**
    - automatické začištění spojů v rozích (L-spoje, T-spoje, křížení) bez nutnosti manuálního ořezávání¨
    - možnost zakřivených stěn s nastavitelnou segmentací
- **b. Výplné otvorů:**
    - systém hostování:  okno musí být svázáno se stěnou, při posunu okna se automaticky posune i výřez ve stěně
    - knihovna základních typů: moderní, historická, fixní okna, posuvné dveře
    - parametrizace rámů, křídel, klik a parapetů¨
- **c. Podlahy a stropy:**
    - automatické generování plochy na základě uzavřeného obvodu stěn
    - parametry pro tloušťku a odsazení od podkladu
### 3. Správa místností a dispozic
- správa uspořádání prostoru
- uživatelé potřebují správu těchto celků
- **a. Detekce místností:**
    - addon by měl být schopen rozpoznat uzavřené prostory a přiřadit jim název a vizuální štítek s plochou
- **b. Správa podlaží:**
    - možnost organizovat model do pater s definovanou výškou. Přepínání viditelnosti pater by mělo být intuitivní, ideálně jedním kliknutím v dedikovaném panelu
- **c. Měřítko a kóty:**
    -  systém pro automatické kótování, které zůstává dynamicky propojeno s geometrií
    - kóta: je v architektuře a technickém kreslení grafický prvek, který určuje přesný rozměr objektu. Není to pouhý text s číslem; je to komplexní objekt, který říká: „Odsud potud je to přesně tolik.“

### 4. UI
- v architektonickém modelování je UI stejně důležité jako samotné funkce
- v blenderu je často workflow rozstříštěná do několika panelů, addon musí nabídnout koncetrované prostředí
- UI addonu by mělo přijmou konvence v základním blenderu, aby pro uživatele působil přirozeně

- **Pet Pallete a on screen manipulátory:**
    - inspirace z archicadu v podobě kontextové nabídky - pet pallete
    - objeví přímo u kurzoru při výběru objektu, je jedním z nejčastějších požadavků profesionálů
    - uživatel klikne na hranu stěny, dostane možnosti jako posunout hranu, přidat bod nebo změnit tloušťku
    - toto minimalizuje cestování myší do postranního panelu
    - na podobném způsobu by měli fungovat i on screen manipulátory ve 3D viewportu
    - namísto zadávání výšky stěny do pole by uživatel měl mít možnost chytit šipku nad stěnou a intuitivně ji vytáhnout, přičemž se vedle kurzoru zobrazuje aktuální hodnota

### 5. Nedestruktivní workflow
- využítí geometry nodes
- stěna jako jednoduchá čára, na které jsou aplikovány uzly generující tloušťku, výšku a otvory
- možnost pohnout s vrcholem čáry a stěna se v reálném čase přizpůsobí, včetně oken, dvěří v ní umístěný
- důraz na nedestruktivnost boolean operací pro otvory a pro čistou geometrii¨

## Technická řešerše implementace v Blenderu
### Výkon a správa geometrie
- při modelování celých budov může počet polygonů rychle narůst
- addon by měl implementovat techniky pro zvýšení výkonu
- Instance: okna a dveře stejného typu by měly být řešeny jako instance
- Booleovské optimalizace: použití fast solveru pro interaktivní práci a přepnutí na exact pouze pro finální render nebo export
### Python API a integrace rozhraní
- modálního operátoru pro kreslení tužkou musí správně reagovat na události myši a klávesnice, aniž by blokoval ostatní funkce Blenderu
- důležitým prvkem je integrace do horního panelu (Top Bar) nebo kontextových menu (Right Click), což je trend v blenderu 4.x pro udržení čistého pracovního prostoru
- uživatel by měl mít možnost přizpůsobit si klávesové zkratky pro nejčastější operace
