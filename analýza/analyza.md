- cílové skupiny a uživatelé
- funkční požadavky
    - rozdělit na základní a specializované
    - základní jsou základní funkce, které addon musí umět bez ohledu na požadavky uživatelů - jak spojovat zdi, jak kreslit zdi apod
    - speciální jsou například jestli podporovat IFC apod.
# Blender add-on pro parametrické modelování architektonických dispozic
### Parametrické modelování
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
### Architektonické dispozice
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

### Computer-Aided Design - CAD (počítačem podporované projektování)
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

### Building Information Modeling - BIM (Informační modelování staveb)
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


### CAD vs BIM
- CAD je nástroj na kreslení. Nakreslí se dvě čáry a my víme, že je to zeď, ale počítač vidí jen dvě čáry - objekt nenese žádnou skutečnou informaci
- BIM je nástroj na stavění. Vloží se objekt "Zeď" a počítač ví, že je to zeď z cihel - objekt nese další informace jako je typ objektu, materiál, apod.
- většina moderních nástrojů je technicky CAD nástroj, ale je velmi pokročilejší a  tedy přechází v BIM

### Půdorys
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
## Cílové skupiny
### 1. Architekti ve fázi konceptuálního navrhování
- software není nástrojem pro tvorbu dokumentace a dat o 3d modelu
- software je nástroj pro prostorové myšlení
- pracovní postup je vysoce iterativní a vyžaduje okamžitou zpětnou vazbu
#### Architekt
- odborník s vysokou znalostí architektonické kompozice
- není expertem na komplexní technicky 3d modelování – retopologie, složité modifikátory, apod.
- **Potřeba:**
    - rychlost – možnost iterativně zkoušet nové myšlenky a prototypy
    - možnost vytáhnout stěny z nápadu během několika minut a modifikovat jejich tloušťku a posouvat otvory bez nutnosti ručního upravování geometrie a posouvání jednotlivých vrcholů
    - častá práce s referenčními obrázky nebo jednoduchými náčrty, které jsou potřeba převést do 3d podoby pro ověření světelných podmínek a měřítka

### 2. Interiéroví designéři
- začínají v prázdném prostoruj, který musí přesně zaměřit a následně vyplnit novými prvky
- vyžadují specifický přístup k modelování stávajících stavů
#### Interier designer
- kreativní profesionál zaměřený na detail, materiály a osvětlení
- modely bývají geometricky husté kvůli detailu nábytku a podobných modelů
- základní architektura tedy musí být co nejjednodušší na správu
- **Potřeba:**
    - přesnost v milimetrech
    - snadná manipulace s výplněmi otvorů
    - potřeba vizualizovat změny např. odstranění nenosné příčky nebo vytvoření nového otvoru

### 3. 3D Umělci a vizualizátoři
- blender hlavním pracovním nástrojem
- addon představuje prostředek/nástroj k automatizaci opakujících se úkolů, což umožňuje věnovat se více uměleckých částem
- přebírání podkladů od architektů a stavění finálního modelu pro render a prezentaci
- parametrický nástroj šetří čas při tvorbě oken, dvěří a nebo třeba schodišť, což by jinak vyžadovalo manuální modelování
#### 3D Umělec / Vizualizátor
- technicky zdatný uživatel, který rozumí principům renderování, stínování a kompozice
- dostávajá hotové plány ve formě DWG nebo PDF a úkolem je předtvořit do 3D
- **Potřeba:**
    - stabilita a čistota geometrie
    - vyžaduje aby addon generoval čistou geometrii, která je kompatibilní s renderovacími enginy a podporuje automatické UV mapování

### 4. Hobbyisté a laická věřejnost
- dostupnost blenderu roste a s tím i dostupnost pro laickou věřejnost
- hledání softwaru poskytující svobodu a otevřenost, které placené CAD programy zpravidla neposkytují
- často si hrají s nápady, experimentují s barvami a snaží se získat cit pro prostor svého budoucího domova
- addon představuje bránu pro přístupnější Blender
#### Hobbyista
- neškolený uživatel s velkým nadšením pro věc, ale s omezeným časem na studium komplexního rozhraní Blenderu
- **Potřeba:**
    - intuitivnost a vizuální jednoduchost
    - možnost kreslit tužkou jako na papír a vidět okamžitý 3D výsledek

### Zdroje
#### Architekti
- https://www.archivinci.com/blogs/parametric-design-and-examples
- https://www.archivinci.com/blogs/best-3d-modeling-softwares
- https://blenderartists.org/t/blender-for-architecture-anyone-with-professional-usage/1575076
- https://rendair.ai/blog/tools-top-7-sketchup-alternatives-for-architects-in-2026
- https://www.archivinci.com/blogs/parametric-design-and-examples
- https://community.graphisoft.com/t5/Modeling/Archicad-vs-Sketchup/td-p/82091
- https://80.lv/articles/turn-floor-plans-into-3d-interiors-in-minutes-with-this-blender-add-on

#### Interioérový design
- https://www.coohom.com/article/creating-stunning-3d-floor-plan-videos?hl=pl
- https://www.reddit.com/r/blenderhelp/comments/1e36f7o/complex_interior_design_in_blender_resulting_in/
- https://www.reddit.com/r/blender/comments/1ccjpjn/is_blender_the_right_tool_for_a_floor_plan/
- https://plan7architect.com/best-remodel-design-software-ai2/
- https://www.reddit.com/r/floorplan/comments/1ohdvdi/software_features/
- https://www.reddit.com/r/floorplan/comments/t2wlwo/people_have_been_asking_me_about_free_floor_plan/

#### 3D Umelci
- https://garagefarm.net/blog/how-blender-excels-as-an-architectural-tool
- https://blenderartists.org/t/blender-for-architecture-anyone-with-professional-usage/1575076
- https://scenegraphstudios.com/architecture-visualisation/blender-addons-for-architecture-visualisation/
- https://www.reddit.com/r/architecture/comments/1j8vu4u/thoughts_on_blender_for_architectural/
- https://blenderartists.org/t/blender-viable-for-architecture/1516598
- https://www.foxrenderfarm.com/news/top-blender-architecture-addons/
- https://scenegraphstudios.com/architecture-visualisation/blender-addons-for-architecture-visualisation/

#### Hobbyisti
- https://all3dp.com/2/sketchup-vs-blender-cad-software-compared/
- https://www.reddit.com/r/Homebuilding/comments/1mifhg8/starting_to_design_a_home_whats_the_best_software/
- https://www.reddit.com/r/Homebuilding/comments/179w99s/whats_the_best_most_user_friendly_design_a_floor/
- https://www.reddit.com/r/blender/comments/1ccjpjn/is_blender_the_right_tool_for_a_floor_plan/
- https://www.reddit.com/r/floorplan/comments/1ohdvdi/software_features/
- https://www.reddit.com/r/floorplan/comments/1hije25/what_features_do_you_want_in_your_ideal_floorplan/


## Současné hlavní architektonické nástroje pro Blender
- ArchiPack
- BonsaiBIm
- Archimesh
- Geometry Nodes
- JARCH-vis

## Metody generování geometrie a parametrické modelování
### Archipack:
- etablován jako nejvýkonější nástroj
- generování geometrie založeno na skriptovaných parametrických assetech
- schopnost dynamické úpravy rozměrů pomocí interaktivních handles přímo ve 3D viewportu
- geometrie není statická, při výběru objektu stěny addon automaticky aktivuje manipulátory, které umožňují měnit délku, výšku a tloušťku
- automatický snapping stěn k sobě
### Bonsai
- generuje geometrii a k ní metadata jako dodatečnou vrstu
- pracuje s industry standardem IFC - industry foundation classes
    - od prvního umístěného prvku uživatel nevytváří pouhý mesh, ale entitu definovanou schématem IFC
-  jeden architektonický prvek může mít více geometrických forem současně
- tyto formy lze editovat a poté opět vložit do IFC
### Geometry nodes
- založeno na uzlových sítích
- automatizace repetetivních úkolů
- generování rychlých variací konceptu primitivní změnou parametrů
- fungují jako modifikatory, nejsou destruktivní
- výpočetně efektivní pro optimalizaci pro instancování geometrie
### Archimesh
- zaměření na rychlou tvorbu místností
- možnost vytvořit místnost z kresby
    - interpretuje čáry jako stěny
### Jarch-vis
- specializace na generování povrchů - obložení, podlahy, střešní krytiny
- konvertuje objekty tvořené jednoduchými rovinami na komplexní architektonické prvky - JV objekty
    - umožňuje vytvářet i nepravidelné, neobdélníkové tvary podlah a střech

## Správa booleovských operací a tvorba otvorů
### Archipack i archimesh
- auto-boolean
    - zajišťuje čisté průniky mezi stěnami a otvory
    - řešeno skrytou kolekcí Holes, kde si addon spravuje boolean objekty provázané s konkrétními stěnami
    - při posunu addon automaticky aktulizuje odpovídající boolean objekt, tím se přepočte otvor a aktulizuje se
    - nedostatky při použitý solveru Exact namísto fast při vrstevných stěnách
### Bonsai a IFC standard
- správa otvorů hluboce integrována do IFC hiearchie - panel Geometric Reationships
- rozlišení mezi manuálními a automatickými bolean operacemi
- možnost přidat otvory pomocí tlačítka add opening
    - možnost spravovat vztah ke stěně jako hostitelskému objektu
- podpora half plane clip objects
    - využívá rovinu a její normálu k oříznutí geometrie
    - výpočetně stabilnější - zejména u šikmých střech
### Geometry Nodes
- řešeny uzlem mesh boolean
- umožňuje provádět operace jako sjednocení, rozdíl a průnik dynamicky
- velkou výhodou je možnost pracování s geometrií, která nemusí být nutně uzavřená (manifold)
    - pokud je použit správný solver, i když Blender stále doporučuje manifold sítě
- pro architektonické scény s velkým počtem oken je často výhodnější použít instancování namísto reálných booleovských řezů

## UI
### Archipack
- primárně situováno v sidebaru 3D viewportu
- předností je systém automatické aktivace manipulátorů
    - při výběru objektu se v reálném čase zobrazí interaktivní prvky
    - umožňují úpravy bez nutnosti hledat hodnoty v seznamech parametrů
### Bonsai
- integrováno hlouběji do standardních panelů Blenderu
- rozhraní je velmi husté a technické
- vyžaduje od uživatele hlubší znalost BIM procesů
### Jarch-vis
- JARCH-vis využívá panel v sidebaru
    - dynamicky se mění podle typu vybraného architektonického objektu
- možnost automatických nebo manuálních aktualizací meshe
- Cutout - uživatel v tabulce definuje polohu, rozměry a rotaci jednotlivých výřezů
### Archimesh
- taky sidebar
-  parametry jsou více orientovány na konkrétní geometrické vlastnosti prvků
- nekompatibilita s 5.0

### Geometry nodes
- uzly, klasika viz GN tab v blenderu