# Persony
Každá z identifikovaných uživatelských skupin je blíže popsána prostřednictvím konkrétní persony, která shrnuje typický profil, technické zázemí, pracovní cíle a klíčové frustrace. Persony slouží jako referenční bod pro hodnocení návrhářských rozhodnutí: Adam zachycuje potřeby architekta, Věra potřeby vizualizátorky a Denis potřeby level designéra.
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
- následně jedním kliknutím vkládat otvory - okna  a dveře s tím, že addon se stará o čistou topologii otvor

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