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