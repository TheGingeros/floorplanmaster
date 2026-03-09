Analýza existujících řešení

# Současné hlavní architektonické rozšiřující moduly pro Blender
## Úvod
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
- 

## BonsaiBIM

## Ostatní
# Hlavní architektonické nástroje mimo Blender
TODO
## Sketchup

## Archicad

## Revit

## Ostatní