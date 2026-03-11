# Definice analýzy

## Prostorová dispozice
- logické a funkční uspořádání trojrozměrného objemu do smysluplných celků (místností a zón) a definování vztahů mezi nimi

## Parametrické modelování
- způsob vytváření 3D modelů
- tvar objektu není definován pevně, je definován pomocí parametrů (čís. hodnot) a vztahů
- čtverec například nadefinujeme takto:
    - parametr A: šířka - 100mm
    - parametr B: délka - 50mm
    - pravidlo: strany jsou na sebe kolmé
    - později je možné parametry změnit a čtverec se sám překreslí
- rozdíly oproti klasickému polygonálnímu modelování: polygonální vs parametrické
    - práce s body, hranami, plochami, táhnutí pro úpravu VS. práce s čísly, funkcemi, historií kroků
    - obtížné změny vs. snadné změny
    - využítí pro hry, filmy, animace vs. architektura, strojírenství, design produktů
- dva typy parametrického modelování:
    - **Historické** - CAD/BIM
        - software si pamatuje časovou osu úprav/kroků
        - např. 1. vytvoř kvádr, 2. zaobli hrany, 3. vytvoř díru 
        - možnost se vrátit ke kroku 1. a změnit velikost kvádru a software automaticky přepočítá zaoblení a vytvořenou díru
        - standard ve strojírenství(SolidWorks) a architektuře (Revit)
    - **Algoritmické** - vizuální skriptování
        - používané v moderní architektuře, hodně podobné geometry nodes

## Architektonické dispozice
- dispozice = uspořádání, rozestavení, rozvržení
- architektonická dispozice = logické a funkční uspořádání jednotlivých místností a prostorů v budově
- odborný výraz pro uspořádání vnitřních prostor stavby
- logický systém, který určuje, kde se nachází jaká místnost, jak jsou velké, jak na sebe navazují a kudy se mezi nimi prochází
- klíčové prvky:
    - půdorysové řešení - kde jsou stěny, příčky, atd
    - otvory - kde jsou dveře, kudy jde světlo / kde jsou okna
    - funkce - co to je za místnost
    - prostor - plocha a objem
- co slovo neznamená:
    - konstrukce - neřeším, z čeho je stěna, pouze tloušťku a polohu
    - interiérový design - dispozice končí u stěn a podlah, neřeší nábytek závěsy, dekorace
    - dispozice se primárně týká vnitřního uspořádání, neřešíme tedy střechy nebo fasády

## Computer-Aided Design - CAD (počítačem podporované projektování)
- technologie, která nahradila rýsovací prkna, tužky a pravítka
- využití počítačového softwaru k tvorbě, úpravě, analýze a optimalizaci návrhu
- od BIM je především o přesné geometrii
- Jak funguje?
    - pracuje s vektorovou grafikou
    - 1. Matematika
        - čára/hrana uložena jako úsečka z bodu A[0,0,0] do bodu B[10,0,0]
        - výkres možno přibližovat do nekonečna => čára dokonale ostrá a přesná
    - 2. Souřadnicový systém (X, Y, Z)
        - kartézský souřadnicový systém
        - každý bod má přesnou adresu v prostoru
        - umožňuje absolutní přesnost
    - 3. Vrstvy
        - možnost vidět objekty za zdivem pomocí skrytí zdiva apod.
- typy:
    - 2D CAD (Digitální rýsovací prkno)
        - pouze plocha o souřadnicích x a y
        - vytváření technických výkresů, půdorysů a řezů
        - využítí pro jednodušší stavební výkresy, schémata zapojení, vypalování plechů laserem 
    - 3D CAD (Prostorové modelování)
        - obsahuje i osu z
        - Plošné modelování (Surface Modeling)
            - model je uvnitř prázdný, tvoří se pouze slupka objektu
            - design karoserií aut, ergonomické tvary myší k počítači
        - Objemové modelování (Solid Modeling)
            - tvoří se plná tělesa, počítat ví, že je uvnitř materiál
            - využití ve strojírenství - dokáže spočítat hmotnost, těžiště nebo pevnost součástky
- využití:
    - Architektura a stavebnictví
        - návrhy domů, mostů, silnic
        - zde přechází CAD v BIM
    - Strojírenství
        - návrhy aut, letadel, telefonů, kávovarů
    - Elektrotechnika
        - návrhy plošných spojů a čipů
    - Fashion design
        - střihy oblečení a návrhy látek

## Building Information Modeling - BIM (Informační modelování staveb)
- moderní proces vytváření a správy digitálního modelu budovy
- stavění budovy z virtuálních objektů, které mají skutečné vlastnosti
- **nejdůležitější na modelu je to, že nese informace**
- pokud klikneme na objekt okna:
    - CAD:
        - 4 čáry, žádná informace o tom, jestli je to okno
    - BIM:
        - informace o tom, že objekt je okno, má nějaká uložená data
            - rozměry, materiál, tepelná izolace, cena, výrobce, datum montáže, ...
- hlavní principy:
    - parametrické chování
        - založen na parametrickém modelování
        - objekt/model je databáze dat
    - spolupráce
        - všichni odborníci (architekt, statik, topenář, elektrikář) pracují na jednom centrálním modelu
    - detekce kolizí
        - software automaticky detekuje chyby
        - např. okno se překrývá s jiným oknem nebo dveřmi
        - nebo trubka vede tam, kde bude zeď
        - software upozorní červeným upozorněním
- rozměry BIM:
    - 3D - Geometrie, prostor, vizualizace
    - 4D - Plánování výstavby, posloupnost stavby
    - 5D - náklady a rozpočet - počet objektů a množství materiálu
    - 6D - Udržitelnost - energetické analýzy, spotřeba energie, atd.
    - 7D - správa budovy po dokončení

## Půdorys
- základní a nejdůležitější výkres ve stavebnictví a architektuře
- laicky: pohled na dům shora bez střechy
- odborně: vodorovný řez objektem vedený v určité výšce
- technická definice:
    - vznikne myšleným horizontálním řezem
    - řez se vede zhruba 1 metr nad podlahou daného patra
    - aby zasáhl případná okna, pokud by byl u podlahy, byly by vidět pouze stěny
    - směr pohledu je kolmo zeshora dolů
- co je vidět na výkresu:
    - tlusté čáry: to, co přeřízl řez - nosné zdi, příčky, ...
    - tenké čáry: to, co je pod rovinou řezu - podlahy, prahy, schody směrem dolů
    - přerušované čáry: to, co je nad rovinou řezu, ale je důležité vidět - klenba, překlad, ...
- **půdorys ve 3D softwaru:**
    - rozdíl jestli se používá CAD software nebo chytrý BIM software
    - přístup v CAD softwaru:
        - nahrání 2D podkladu
        - obkreslení stěn
        - extrude stěn do požadované výšky a potřeba dalších úprav
        - jakmile se půdorys změní, je často potřeba celý proces opakovat
    - přístup v BIM softwaru:
        - ve 3D prostoru se staví virtuální zdi, okna, dveře, ...
        - vygeneruje se pohled na tento půdorys
        - následně se zvolí výška řezné roviny a půdorys se vygeneruje automaticky

## Stěnová konstrukce aka 3D půdorys
- parametrické 3D geometrické objemy, které vznikají vertikální extruzí nad 2D vektorovou osou
- jsou charakterizovány svou tloušťkou, výškou, vzájemnou topologickou vazbou (spoje stěn) a schopností hostit podřízené objekty prostřednictvím booleanovských operací
- stěnová konstrukce není jen plocha, ale objem
- není izolovaný prvek, zahrnuje systémové chování (automatické řešení spojů, vymezení uzavřených oblastí)
- svým způsobem je to vlastně graf, kde stěny jsou hrany a spoje jsou vrcholy
- slouží jako hostitel nebo modifikátor pro okna a dveře, které odečítají objem ze stěny

## CAD vs BIM
- CAD je nástroj na kreslení. Nakreslí se dvě čáry a my víme, že je to zeď, ale počítač vidí jen dvě čáry - objekt nenese žádnou skutečnou informaci
- BIM je nástroj na stavění. Vloží se objekt "Zeď" a počítač ví, že  to zeď z cihel - objekt nese další informace jako je typ objektu, materiál, apod.
- většina moderních nástrojů je technicky CAD nástroj, ale je velmi pokročilejší a  tedy přechází v BIM

## Holistický přístup - pohled na celek
- nedíváme se na izolované kousky problému ale na celý komplexní systém
- vše souvisí se vším a celek je více než jen součet jeho částí - provázanost
- v architektuře:
    - architekt nenavrhuje dům tak, že by kreslil půdorys a k těmu dal fasádu a potom chtěl po topenáři, ať tam zavede topení - musí se uvažovat o všem najednou jako celku
    - příklad:
        - architekt se rozhodne zvětšit okno na jižní fasádě
        - musí přemýšlet holisticky nad důsledky - v létě přehřívání místnosti
        - nutná venkovní žaluzie
        - architekt vnímá stavbu jako propojený celek, kde jedna změna spustí řetězovou reakci
## Iterativní přístup - postupné vylepšování v cyklech
- iterace = opakování
- finální a úplný návrh se nedělá hned na první pokus
- postupuje se ve smyčkách
- hrubý návrh, poté zhodnocení, zjištění nedostatků a návrh se upravý
- s každým dalším krokem je návrh propracovanější 
- v architektuře - pokus - vyhodnocení - úprava (v návrhu)
- příklad:
    - 1. iterace - architekt navrhne jednoduché místnosti, zjistí, že se do přízemí nevejde schodiště
    - 2. Změní tvar, čímz vznikne prostor pro schodiště, pošle to statikovi
    - 3. Statik zjistí nedostatek, například v podobě příliš velkého stropu a doprostřed místnosti je tím pádem potřeba přidat spolupráce
    - 4. Architekt nechce sloup v obýváku, mírně posune nosnou stěnu a zmenší rozpoznat
    - 5. Zaslání klientovi, který zase chce větší např. koupelnu a proces pokračuje v další iteraci

#### IFC - industry foundation classses
- otevřený, na platformě nezávislý datový standard pro ukládání a výměnu dat ve stavebnictví a facility managementu
- formát: .ifc nebo xml verze .ifcXML
- objektově orientovaný datový model
- hlavní myšlenkou je interoperabilita
    - výměna dat
    - koordinace
    - archivace
    - openBIm - filozofie, že data by neměla být uzamčena v softwaru jednoho výrobce
- databáze vztahů a vlastností - hiearchie
    - ifcproject
    - ifcsite
    - ifcbuilding
    - ifcbuildingstorey
    - ifcwall, ifcwindow, ...

## Depsgraph - Dependency graph
- klíčová komponenta Blender API
- graf, který hlídá, v jakém pořadí se mají počítat a aktualizovat věci ve scéně
- probíhá s ním komunikace pokaždé, kdy z interaktivní stěny probíhá generace finálního modelu
- objekt A, B, C. A parent B a B parent C, jakmile pohneme objektem A, blender musí vědět, co má přepočítat dřív. Depsgraph si proto pamatuje závislosti A -> B -> C
- Original vs Evaluated data
    - stěna je ve skutečnosti křivka s dvěma body - original, pomocí geometry nodes vypadá jako stěna - pokud chce při finálním nástroji model stěny, tázám se na evaluated ata. 

- změny výšky stěny nad original daty se pouze ukládají do paměti
- při změně je potřeba nastavit tag pomocí - obj.update_tag() - tím říkám depsgraphu aby přepočítal vše v celém stromu co s daným objektem 

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
- existence BIM základů jako např. automatický výpočet plochy, což se např. architektům hodí znát okamžitě při návrhusouvisí

## Vstup
### 2D podklady
- naskenované ruční skici, PDF výkresy, obrázky půdorysů nebo importované 2D CAD výkresy (DXF/DWG), které uživatel potřebuje transformovat do 3D
### Kvantitativní zadání (Stavební program)
- seznam požadavků od klienta nebo game designera (např. "potřebujeme obývák o rozloze 30 $m^2$", "šířka chodby musí být přesně 2 metry kvůli pohybu NPC")
### Čistý koncept (Myšlenka)
- uživatel nemá žádný podklad, začíná s prázdnou scénou a potřebuje nástroj, který udrží krok s jeho rychlým tokem myšlenek při navrhování

## Výstup
### 3D hmotový model (Massing)
- čistá prostorová 3D reprezentace stěn, místností a otvorů
- slouží k vizuální kontrole proporcí, tvorbě úvodních renderů, světelných studií nebo k prezentaci klientovi

### Optimalizovaná geometrie pro export (Blockout)
- vyčištěný 3D model bez topologických chyb, který si level designer může okamžitě vyexportovat (např. přes FBX/OBJ) do herního enginu

### Přehledná prostorová data
- rychlá zpětná vazba o tom, zda uživatel splnil zadání (zobrazení vypočítaných metrů čtverečních jednotlivých místností, kontrola tloušťky nosných stěn)