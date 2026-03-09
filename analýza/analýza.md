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
TODO
- [Současné hlavní architektonické rozšiřující moduly pro Blender](./files/existujici_reseni.md#současné-hlavní-architektonické-rozšiřující-moduly-pro-blender)
- [Hlavní architektonické nástroje mimo Blender](./files/existujici_reseni.md#hlavní-architektonické-nástroje-mimo-blender)

### Parametrické modelování
- [Definice](./files/definice.md#parametrické-modelování)

### Prostorové dispozice
- [Definice](./files/definice.md#prostorová-dispozice)

## Cílové skupiny
TODO
### Uživatelé
### Persony
### Uživatelské scénáře - use cases

## Analýza požadavků
TODO
### Funkční požadavky
### Nefunkční požadavky

## Návrh UI
TODO
## Technická analýza a návrh architektury
TODO

### 1. Architekti ve fázi konceptuálního navrhování
- software není nástrojem pro tvorbu dokumentace a dat o 3d modelu
- software je nástroj pro prostorové myšlení
- pracovní postup je vysoce iterativní a vyžaduje okamžitou zpětnou vazbu
- přemýšlí v objemech a hmotách, nikoliv v polygonech
- dům - soubor objemů, prostorů a hmot
- nezajímá je, jaké jso normály nebo quady
- vyžaduje nedestruktivní workflow
    - jestliže při změně návrhu se musí celý nebo část modelu vymazat a začít znovu je velice nepohodlné a hraje důležitou roli v pracovním postupu
- důraz na vizuální workflow, nechce se starat o technické detaily
#### Přístup k problému návrhu
- holistický a zároveň interativní přístup
    - neustálý dialog mezi vnitřní funkcí a vnějším kontextem
    - často nelze postupovat jen jedním směrem
- **zevnitř ven: (funkce a provoz)**
    - vychází  z potřeb uživatele/klienta
    - řeší se provozní schéma - jak na sebe navazují místnosti, nároky na plochu, světlo a ergonomii
    - převažuje u vysoce funkčních budov - nemocnice, továrny, laboratoře
- **zvenku dovnitř: (kontext a forma)**
    - reaguje na okolí
    - architekt analyzuje tvar pozemku, orientaci ke světovým stranám, výhledy, sklon terénu, limity územního plánu a charakter okolní zástavby
    - tvar budovy navrhnut z těchto vnějších omezení
- **V praxi:**
    - začíná se hrubou hmotou vycházející s vnějších limitů - zvenku dovnitř
    - následně se do ní naskládá požadovaný program - zevnitř ven
    - pokud se funkce do hmoty nevejde, je potřeba hmotu upravit
    - tento cyklus se opakuje tak dlouho, dokud nenastane dokonalá shoda
- **Fáze problému návrhu:**
    - 1. Analýza - Architekt zkoumá zadání klienta a místnost
        - klient - zadání, budget, požadavky
        - místo - limity pozemku, geologie, infrastruktura
    - 2. Koncept - hledání jádra návrhu - specifický tvar, způsob prosvětlení nebo materiál
    - 3. Studie - z konceptu do konkrétních půdorysů, řezů a fasády
        - vznikají první 3D modely
        - zde se odehrává největší část interativního procesu
    - 4. Technický rozvoj a detail
        - od řešení celku se přechází k řešení detailů
        - detail - např. jak navazuje okno na fasádu, jaký bude obklad, kudy povedou trubky
- **Příklad typického postupu:**
    - Architekt rozešle podklady všem profesím
    - Specialisté zakreslí své sítě a požadavky do modelu
    - Proběhne koordinační schůzka - dnes často pomocí BIM
    - Zjistí se kolize - např. trubka vzduchotechniky prochází přes ocelový nosník
    - Architekt rozhodne o řešení - sníží se podhled / statik udělá průraz do nosníku / vzduchotechnika se povede jinudy
    - Model se aktualizuje
    - tento proces se opakuje v každé fázi projektu
#### Architekt
- odborník s vysokou znalostí architektonické kompozice
- není expertem na komplexní technicky 3d modelování – retopologie, složité modifikátory, apod.
- **Potřeba:**
    - rychlost – možnost iterativně zkoušet nové myšlenky a prototypy
    - možnost vytáhnout stěny z nápadu během několika minut a modifikovat jejich tloušťku a posouvat otvory bez nutnosti ručního upravování geometrie a posouvání jednotlivých vrcholů
    - častá práce s referenčními obrázky nebo jednoduchými náčrty, které jsou potřeba převést do 3d podoby pro ověření světelných podmínek a měřítka

- **Scénáře použítí:**
    - 1. Rychlá skica/náčrtek - má v ruce půdorys a potřebuje z něho vytáhnout geometrii určité výšky a tloušťky, aniž by musel řešit technické detaily v blenderu jako jsou modifikátory a editace geometrie
    - 2. Testování světla - je potřeba zkusit několik variant umístění oken na například jižní fasádě, potřeba upravit několik oken naráz a naráz je posunout nebo zvětšit a podívat se na nové osvětlení
    - 3. Klient chce posunout vchodové dveře o metr doprava. Doplňek musí tento posun umožnit jedním tahem myši, přičemž posune i otvor ve zdi a zárubeň

- Jaké z toho vyplývají technické nároky:
    - parametrizace - objekty musí zůstat parametrizovatelné do exportu, tedy co nejdéle
    - chytré objekty - stěna musí být vidět že je stěna se svými parametry, když se do ní vloží otvor, musí se chovat jako hostitel
    - presety/knihovna běžných použití, aby se pokaždé nemusel základní postup opakovat
    - i když neřeší topologii, je potřeba udržet čisté UV pro renderování

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

#### Přístup k problému návrhu:
- primárně zvenku dovnitř, ale probíhá lehká kombinace
- **zvenku dovnitř** - kompozice, světlo, kontext:
    - začíná se zasazením holého modelu do prostředí
    - hledají se nejlepší úhly kamery a testují se hlavní zdroje světla
    - jaký příběh má vizualizace vyprávět
- **zevnitř ven** - materiály, detaily:
    - přesouvání se k detailům
    - definice fyzikálně přesných materiálů, řešení odrazů, přidává nábytek, lidi, rostliny
    - postup od detailu k finálnímu obrazu
- **pracovní postup:**
    - 1. Briefing a sběr dat - shromažďování 3D modelů, 2D výkřesů, referenční obrázky
    - 2. Clay render - import modelů, nastavení kamery a světla
    - 3. LookDev - aplikace barev a textur - vytváření Proběhne
    - 4. Set Dressing - přidávání detailů - nábytek, auta, zeleň, lidé
    - 5. Finální render a postproduction


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

### 5. Game designer - level design/ environmental design
- skupina představující vývojáře 3D do her
- potřeba návrhu herních prostor pro hru 
- důraz na low poly a čistou geometrii pro snažší UV mapování
- potřeba interativně vytvářet návrhy prostorů pro testování integrování herních mechanik
- **Potřeba:**
    - iterativně navrhovat vnitřní prostory pro herní prostředí
    - automatické spojování a vytváření místností z uzavřených spojů
    - možnost vkládat otvory do vytvořených prostor a manipulace s nimi
    - vytvořená geometrie musí mít čistou topologii a UV připravené na mapování textur
- **Bariéry:**
    - iterativnost - upravování již existujícího modelu interiéru je v blenderu zdlouhavé
    - je potřeba upravit každý vrchol v geometrii při posunu nějaké zdi, velká náchylnost na chybu
    - vkládání otvorů je destruktivní, v případě odebrání otvoru nebo komplexnější změny je potřeba celou část geometrii předělat od nuly
- **Scénáře Použití:**
    - 1. Rychlé vytažení geometrie z návrhu "půdorysu" - má v ruce návrh jak by mělo rozložení prostor vidět a potřebuje tento 2D návrh převést do 3D, ideálně iterativně s možností upravovat detaily v případě nalezení problémů

    - 2. Práce s existujícím modelem interiéru - potřeba upravit detaily rozmístění po testování herních mechanik

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