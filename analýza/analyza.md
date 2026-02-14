- TODO
    - BIM - Building Information Modeling
    - CAD - Computer-Aided Design

# Blender add-on pro parametrické modelování architektonických dispozic
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
- odborný výraz pro uspořádání vnitřních prostor stavby
- logický systém, který určuje, kde se nachází jaká místnost, jak jsou velké, jak na sebe navazují a kudy se mezi nimi prochází
- klíčové prvky:
    - rozdělení na zóny/fukční celky - společenská, klidová, hospodářská, technická, vstupní, ...
    - orientace ke světovým stranám - jih (obývací pokoje, dětské pokoje),  východ (ložnice, kuchyně), sever (technické místnosti, koupelny, ...)
    - komunikace - pohyb po domě 

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
    - 

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