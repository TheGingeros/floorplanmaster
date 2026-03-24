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


#### Archimesh - add-on pro Blender, který umožňuje generovat místnosti, okna, dveře a další architektonické prvky. [Archimesh stránka](https://extensions.blender.org/add-ons/archimesh/)
##### Výhody:
- Jednoduchost a dostupnost (rychlé „naklikání“ místnosti/okna/dveří).
- Rychlé generování základních prvků – místnost i s otvory bez většího nastavování.
- Nízká bariéra pro začátečníky; hodí se na „blockout“ a hrubé dispozice. (Souhrny a tutoriály to takto používají.)
##### Nevýhody:
- Parametrika je omezenější (po vygenerování už není vše pohodlně „živě“ upravitelné on-screen jako u Archipacku).
- Údržba/robustnost některých nástrojů – uživatelé zmiňují potřebu větších update a občasné potíže (např. auto-holes u dveří/oken).
- Méně „BIM-like“ (Building Information Modeling) workflow (spíš generátor prvků než kompletní systém s rozšířenou 2D→3D, kótami apod.)
#### Archipack - robustní framework pro Blender, zaměřený na architektonické modelování (parametrické stěny, okna, schodiště…). [Archipack stránka](https://blender-archipack.org/)
##### Výhody:
- Parametrické objekty s bohatými vlastnostmi (zdi, okna/dveře, schody, střechy, stropy, podlahy…).
- Realtime on-screen editace (manipulátory, rychlé úpravy na scéně).
- Širší nástroje/workflow: 2D→3D, auto-boolean, podpora BlenderBIM kót, import z křivek/grease-pencil jako stěny.
- Aktivnější vývoj a dokumentace mimo Blender manuál (changelog, nové funkce).
##### Nevýhody:
- Složitější křivka učení a „těžší“ UI (víc panelů a voleb, někdy těžkopádné).
- Dualita verzí (základ vs. rozšířená/placená), takže některé funkce jsou mimo čistě „stock“ Blender.
- Smíšené dojmy komunity — část uživatelů jej miluje, část volí ruční modelování kvůli jednoduchosti/robustnosti.
 
#### Mezery současných řešení, které lze vylepšit a nabídnout tak konkurenční add-on:
- „SketchUp-like“ kreslení zdí - Archipack sice umí stěny z křivky a grease-pencil, ale UX není vyloženě „tužka v půdorysu“ jako v SU/ArchiCAD.
- Robustní a srozumitelné vkládání otvorů se snapem na stěnu + auto-boolean + parametry (šířka, výška, odskoky od hran) – u Archimeshe jsou s „auto-holes“ hlášené slabiny; u Archipacku je to silné, ale UI je těžší. FloorPlanMaster může nabídnout štíhlé, specializované UX.
- Jednoduchý analytický modul (výměry/objemy) přímo navázaný na místnosti vytvořené kreslením — v obou add-onech to není centrální, „na jedno kliknutí“. Tyto detaily a analytiky jsou často uživately schované za náročným UI