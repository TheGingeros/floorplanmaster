# Současné hlavní architektonické rozšiřující moduly pro Blender
- blender za posledních 10 let prošel dramatickou evolucí
- původně vnimán jako nástroj pro organické modelování, animace a vizuální efekty
- díky open source a robustní Python API transformován v platformu schopnou realizovat komplexní architektonické projekty

## Archimesh
- základní kámen architektonických nástrojů pro Blender
- autor - Antonio Vazquez (antonioya)
- za cíl je automatizovat tvorbu interiérových a exteriérových prvků, které by jinak zabrali hodně času manuálním modelováním
- díky stabilitě a užitečnosti byl dlouhodobě integrován přímo do oficiální distribuce Blenderu jako komunitní doplňek
- primárně určen pro rychlé skicování prostor a interiérový design
- intuitivní rozhraní umístěné v postranním panelu
- generace objektů pouhým kliknutím a následná úprava jeho parametrů

### Archimesh - Tvorba místností
- buď definování počtu stěn a jejich rozměrů nebo využití nástroje Grease Pencil
- uživatel v půdorysném pohledu nakreslí hrubé obrysy místností a doplněk tyto tahy automaticky převede na trojrozměrné stěny s definovanou výškou a tloušťkou
- výrazně urychluje počáteční fázi návrhu, kdy architekt pracuje s koncepčními skicami
- umožňuje automatické generování podlah a stropů, které se dynamicky přizpůsobují uzavřeným obvodům stěn

### Archimesh - Otvory
- umožňuje dva typi oken - kolejnicová a panelová
- panelová jsou technicky velmi detailní
- součástí oken jsou i parametrické parapety a systém žaluzií

### Archimesh - Interiérové prvky a rekvizity
- generátor kuchyňských linek
- generátor polic
- generátor knih, lamp a závěsů

## Archipack
- vytvořen jako robustnější a výkonnější alternativa k Archimesh
- zaměřen primárně pro profesionální architekty a vizualizátory
- autor - Stephen Leger
- navrhnut jako komplexní framework pro architektonické navrhnování v Blenderu
- existují dvě verze - Community Edition a Pro

### Archipack - parametrické modelování
- důraz na interaktivní manipulaci
- systém Auto-manipulate on select - při výběru objektu se ve 3D viewportu objeví táhla (gizmos) a textové popisky, které umožňují měnit rozměry, pozici a rotaci prvků přímým tažením myši
- spravování objektů pomocí vlastního systému Properties - zůstavájí zachovány po celou dobu životnosti projektu
- uživatel může kdykoliv vybrat stěnu a změnit její tloušťku nebo výšku, všechny připojené prvky, jako jsou okna, dveře nebo podlahy, na tuto změnu reagují

### Archipack - export a interoperabilita
- nástroj pro generování řezů a půdorysů, ty lze exportovat do formátu SVG pro další úpravy v programech jako Inkscape nebo Illustrator
- PRO verze nabízí export do formátu IFC 

## BonsaiBIM
- oproti Archimeshi a Archipacku je navržen jako nativní platforma pro tvorbu a správu informačních modelů budov, založena na mezinárodním standardu IFC - ISO 16739

### BonsaiBIM - IFC
- [IFC](../../files/00_definitions.md#ifc---industry-foundation-classses)

## Shrnutí
- archimesh a archipeck jsou nástavby nad standardním modelovacím procesem
- data jsou spjata s .blend souborem
- bonsai naproti tomu umožňuje Blenderu fungovat jako prohlížeč a editor databáze IFC

