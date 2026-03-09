
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

# Persony
TODO

# Uživatelské scénáře