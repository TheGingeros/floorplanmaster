
# Uživatelé
## Architekti ve fázi konceptuálního navrhování 
### Definice
- profesionálové nebo studenti architektury, kteří vytvářejí prvotní hmotové a prostorové studie - koncepty
- v této fázi neřeší mikrodetaily (např. typ kování u dveří), ale zaměřují se na celkové proporce, návaznost místností a uspořádání půdorysu na pozemku

### Potřeby
- rychlá iterace návrhu
- přesné zadávání číselných hodnot (délka, šířka, výška v metrech/centimetrech)
- nedestruktivní úpravy – možnost kdykoliv změnit parametry místnosti nebo plynule posouvat okna a dveře po stěně

### Současné bariéry
- modelování architektonických prvků pomocí standardních nástrojů Blenderu je destruktivní
- změny znamenají zdlouhavou manuální opravu okolní geometrie, posouvání vertexů a přepočítávání otvorů, což výrazně brzdí kreativní proces a prodlužuje čas návrhu

## 3D Umělci a Vizualizátoři
### Definice
- tvůrci zaměření primárně na estetiku a tvorbu realistických renderů 
- hrubá stavba (stěny, podlaha, strop) je pro ně pouze „plátnem“, do kterého vkládají detailní modely, nastavují materiály a světlo

### Potřeby
- získat co nejrychleji hotovou základní geometrii místnosti, aby mohli začít s kreativní fází
- vygenerovaná geometrie musí mít čistou topologii, aby na ní bez problémů fungovalo mapování textur a modifikátory např. pro zaoblování hran

### Současné bariéry
- ruční modelování stěn a vyřezávání oken pomocí Boolean modifikátorů často vytváří nevzhlednou topologii
- ruční začišťování těchto chyb je pro umělce nezáživná, neefektivní rutina, která je okrádá o čas

## Game Designeři / Level Designeři
### Definice
- vývojáři her, kteří navrhují herní prostředí s důrazem na hratelnost a průchodnost
- vytvářejí tzv. blockouty (hrubé modely úrovní), na kterých testují, jak se v prostoru pohybuje hráč nebo kamera

### Potřeby
- modulární přístup ke stavbě prostoru
- schopnost okamžitě měnit proporce (např. rozšířit chodbu, posunout dveře) na základě zpětné vazby z herního testování
- snadný export hrubých tvarů (využitelných jako kolizní modely) do herních enginů jako Unreal Engine nebo Unity

### Současné bariéry
- modelovací nástroje Blenderu nejsou primárně optimalizovány pro rychlý level design
- ruční přestavování rozměrů místnosti nebo přesouvání otvorů během prototypování je příliš pomalé, což ztěžuje plynulé iterování hratelnosti a omezuje rychlost vývoje herní úrovně

### [Více informací o cílových skupinách](./cilove_skupiny_rozsahlejsi.md)

# Persony
## Architekt Adam - zaměřeno na studii a rychlý koncept
### Profil
- 32 let
- pracuje v menším architektonickém ateliéru
- zodpovědní za úvodní studie a komunikaci s klienty ve fázi hledání tvar a dispozice budovy
### Technické zázemí
- pracuje v CAD/BIM softwaru (AutoCAD, Revit)
- pro rychlé 3D koncepty a objemové studie začal používat Blender protože je svižnější a nabízí hezčí real-time zobrazení
- neumí programovat a Geometry Nodes jsou pro něj příliš složité
### Cíle
- potřebuje vytvořit během několika hodin 3 různé varianty prostorového uspořádání domu, pro ukázku pro klienta
- primárně mu jde o hmotu, návaznost místností a základní rozměry
### Flustrace
- v čistém blenderu ho zdržuje extrudování polygonů, když klient řekne, že chce obývák o metr širší, musí ručně posouvat vertexy a přepočítávat návaznosti
- chybí také rychlý přehled o metrech čtverečních
### Očekávání
- očekává jednoduché UI, kde zadá rozměry místnosti, nebo je naskicuje
- při změně parametru addon automaticky zachová tloušťku zdiva a nerozbije návaznost na další místnosti

## Vizualizátor - zaměřeno na rychlost a čistou topologii
### Profil
### Technické zázemí
### Cíle
### Flustrace
### Očekávání

## Level Designer - zaměřeno na "Blockout" a hratelnost
### Profil
### Technické zázemí
### Cíle
### Flustrace
### Očekávání

# Uživatelské scénáře
## Scénář 1: Vytvoření základní místnosti pomocí kreslení v top-down pohledu
- uživatel aktivuje kreslící nástroj addonu v ortografickém pohledu shora
- klikáním do 3D prostoru definuje rohové body a tvar půdorysu 
- po uzavření tvaru nebo potvrzení addon automaticky vytáhne 3D stěny s výchozí výškou a tloušťkou
## Scénář 2: Vytvoření základní místnosti pomocí parametrů
- uživatel v uživatelském rozhraní addonu klikne na tlačítko pro přidání výchozí místnosti (např. obdélníkové) se zvolenými parametry jako je objem, šířka, délka, ...
- addon vygeneruje na pozici 3D kurzoru základní blok místnosti s danými parametry
## Scénář 3: Parametrická úprava místnosti
- uživatel vybere již dříve vygenerovanou místnost ve 3D Viewportu nebo v panelu
- v panelu vlastností addonu změní na posuvníku libovolný parametr (např. zvětší tloušťku stěn nebo zvedne výšku stropu)
- addon v reálném čase nedestruktivně přepočítá 3D model, aniž by bylo nutné cokoli ručně modelovat
## Scénář 4: Vložení otvoru do stěny
- uživatel označí konkrétní stěnu místnosti a v panelu klikne na „Add window / doors“
- addon na daném místě vytvoří otvor, který automaticky a čistě prostupuje celou tloušťkou stěny
- pomocí dodatečných parametrů (např. posuvníků pro osu X a Z) uživatel přesně doladí umístění a velikost otvoru v rámci vybrané stěny