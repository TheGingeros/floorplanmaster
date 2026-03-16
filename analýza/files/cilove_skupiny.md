
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

## Vizualizátorka Věra - zaměřeno na rychlost a čistou topologii
### Profil
- 28 let
- vizualizátorka na volné noze - freelance
- specializace na fotorealistické interiéry pro developery a realitní kanceláře
### Technické zázemí
- blender ovládá na velmi vysoké úrovni
- dokonale zná materály, nasvícení a rendering
- spíše umělecky zaměřena, než technicky
### Cíle
- od klienta dostane 2D půdorys v PDF a potřebuje co nejrychleji vytvořit 3D shell bytu - aby se věnovala hlavnímu a to je nasvícení, materiály a vybavení nábytkem
### Flustrace
- modelování holích zdí ji zdržuje a nebaví
- nativní boolean operace na otvory vytváří ošklivou topologii, kterou musí čistit, kvůli renderingu a materiálům
### Očekávání
- chce nástroj podobný tužce, s kterým obkreslí podložený půdorys
- následně jedním kliknutím vkládat otvory - okna  a dveře s tím, že addon se stará o čistou topologii otvorů

## Level Designer Denis - zaměřeno na "Blockout" a hratelnost
### Profil
- 25 let
- vývojář v nezávislém herním studiu
- vytváří herní úrovně a testuje, jak se v nich hráč pohybuje
### Technické zázemí
- primárně pracuje v herních enginech - UE a Unity
- Blender používá k tvorbě takzvaného "Blockoutu" nebo "Greyboxingu" – rychlé tvorbě hrubých geometrických bloků
### Cíle
- rychle vybudovat komplexní herní mapu (např. spleť chodeb a místností), vyexportovat ji do enginu a projít si ji s herní postavou
### Flustrace
- po testování často zjistí, že chodba je pro souboj příliš úzká nebo strop moc nízký. Pokud má úroveň vymodelovanou z jednoho kusu geometrie v čistém Blenderu, je její úprava destruktivní a zdlouhavá
### Očekávání
- hledá robustnost a rychlost iterace
- parametrické místnosti mu umožní po playtestu jednoduše kliknout na chodbu, změnit v panelu šířku z 2 metrů na 3 metry a add-on se postará o zbytek
- bezproblémový export, který nerozbije kolize pro herní engine

# Uživatelské scénáře
## 1. Architekti
### Scénář 1.1: Hmotová studie na základě stavebního programu
- uživatel vloží do scény parametrickou místnosti na základě vstupních parametrů
- přes nabídku v panelu zadá požadovanou plochu a poměr stran, například 30 m^2
- addon automaticky vygeneruje místnost o daných parametrech
- uživatel zapne zobrazení metadat - štítek s plochou v m^2 přímo v 3D view pro rychlou vizuální kontrolu
### Scénář 1.2: Zkoušení prostorových variant a posun stěn
- uživatel vybere sdílenou příčku mezi dvěma vytvořenými místnostmi
- pomocí interaktivní 3D manipulátoru stěnu posune o 1 metr
- addon nedestruktvně přepočítá obě místnosti, jedna se zvětší, druhá zmenší a podlahové plochy se automaticky aktulizují

## 2. 3D Umělci a Vizualizátoři
### Scénář 2.1: Obkreslení 2D půdorysu do čisté 3D geometrie
- uživatel si na pozadí Blenderu vloží obrázek s půdorysem
- aktivuje nástroj pro kreslení a se zapnutým přichytáváním odklikává rohy místností přesně podle obrázku
- addon automaticky generuje stěny s přednastavenou tloušťkou a výškou. Geometrie je tvořena čistými quady - pokud možno
### Scénář 2.2: Vložení otvorů pro přesné 3D modely oken/dveří
- uživatel vybere stěnu a aktivuje funkci "Vložit otvor"
- nakreslí otvor přímo na plochu stěny nebo zadá jeho přesné rozměry (např. 1500x1250 mm) a výšku parapetu
- otvor se aplikuje nedestruktivně
- uživatel později zjistí, že klient změnil velikost okna – v parametrech otvoru jednoduše přepíše hodnotu a stěna se upraví

## 3. Game Designeři
### Scénář 3.1: Rychlý blockout a tvorba chodeb
- uživatel použije kreslící nástroj a hrubě načrtne sérii navazujících místností
- soustředí se pouze na proporce a pocit z prostoru. Nepotřebuje řešit metry čtvereční, ale vizuální měřítko vůči hráčské postavě
- nástroj plynule generuje napojené stěny a podlahy, tvoří modulární celky, které do sebe zapadají
### Scénář 3.2: Iterace na základě playtestingu a finalizace pro export
- uživatel zjistí, že chodba mezi arénami je příliš úzká
- vybere osu chodby nebo obě stěny a parametricky je rozšíří. Přilehlé místnosti se této změně automaticky přizpůsobí
- následně použije "Finalizační nástroj", který z parametrického add-on objektu vytvoří standardní Blender Mesh, aplikuje modifikátory, odstraní přebytečné hrany (pokud existují) a připraví objekt na FBX/GLTF export









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