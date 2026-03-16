# Analýza - Blender add-on pro parametrické modelování prostorových dispozic

## Definice problému
- Blender je primárně obecný 3D polygonální modelovací nástroj, nikoliv specializovaný CAD/BIM software
- nabízí obrovskou flexibilitu, pro specifické potřeby architektonického navrhování avšak postrádá nativní nástroje, což vede k neefektivně a zdlouhavosti pracovních postupů
- tvorba půdorysů a 3D dispozic budov je v čistém Blenderu zdlouhavá a destruktivní

## Cíl projektu
- vytvoření rozšiřovacího modulu pro Blender zaměřený na parametrické modelování prostorových dispozic
- uživatel bude moci prostorové dispozice intuitivně vytvářet a nedestruktivně upravovat pomocí parametrů
- cílem je primárně urychlit ranou fázi architektonického návrhu

## Informační analýza

### Analýza existujících řešení
- [Současné hlavní architektonické rozšiřující moduly pro Blender](./files/existujici_reseni.md#současné-hlavní-architektonické-rozšiřující-moduly-pro-blender)
- [Hlavní architektonické nástroje mimo Blender](./files/existujici_reseni.md#hlavní-architektonické-nástroje-mimo-blender)

### Parametrické modelování
- [Definice](./files/definice.md#parametrické-modelování)

### Prostorové dispozice
- [Definice](./files/definice.md#prostorová-dispozice)

## Cílové skupiny
### Uživatelé
1. [Architekti](./files/cilove_skupiny.md#architekti)
2. [3D Umělci a Vizualizátoři](./files/cilove_skupiny.md#3d-umělci-a-vizualizátoři)
3. [Game Designeři / Level Designeři](./files/cilove_skupiny.md#game-designeři--level-designeři)

### Persony
1. [Architekt Adam](./files/cilove_skupiny.md#architekt-adam---zaměřeno-na-studii-a-rychlý-koncept)
2. [Vizualizátorka Věra](./files/cilove_skupiny.md#vizualizátorka-věra---zaměřeno-na-rychlost-a-čistou-topologii)
3. [Level Designer Denis](./files/cilove_skupiny.md#level-designer-denis---zaměřeno-na-blockout-a-hratelnost)

### Vstup
1. [2D podklady](./files/definice.md#2d-podklady)
2. [Kvantitativní zadání](./files/definice.md#kvantitativní-zadání-stavební-program)
3. [Čistý koncept](./files/definice.md#čistý-koncept-myšlenka)

### Výstup
1. [3D hmotový model](./files/definice.md#3d-hmotový-model-massing)
2. [Optimalizovaná geometrie pro export](./files/definice.md#optimalizovaná-geometrie-pro-export-blockout)
3. [Přehledná prostorová data](./files/definice.md#přehledná-prostorová-data)

### Uživatelské scénáře - use cases
#### 1. Architekti
[UC 1.1 Scénář 1.1: Hmotová studie na základě stavebního programu](./files/cilove_skupiny.md#scénář-11-hmotová-studie-na-základě-stavebního-programu)
[UC 1.2 Scénář 1.2: Zkoušení prostorových variant a posun stěn](./files/cilove_skupiny.md#scénář-12-zkoušení-prostorových-variant-a-posun-stěn)
#### 2. 3D Umělci a Vizualizátoři
[UC 2.1 Scénář 2.1: Obkreslení 2D půdorysu do čisté 3D geometrie](./files/cilove_skupiny.md#scénář-21-obkreslení-2d-půdorysu-do-čisté-3d-geometrie)
[UC 2.2 Scénář 2.2: Vložení otvorů pro přesné 3D modely oken/dveří](./files/cilove_skupiny.md#scénář-22-vložení-otvorů-pro-přesné-3d-modely-okendveří)
#### 3. Game Designeři
[UC 3.1 Scénář 3.1: Rychlý blockout a tvorba chodeb](./files/cilove_skupiny.md#scénář-31-rychlý-blockout-a-tvorba-chodeb)
[UC 3.2 Scénář 3.2: Iterace na základě playtestingu a finalizace pro export](./files/cilove_skupiny.md#scénář-32-iterace-na-základě-playtestingu-a-finalizace-pro-export)

## Analýza požadavků
### Tabulka
| Požadavek | Architekti | 3D Vizualizátoři | Game Designeři |
| :--- | :--- | :--- | :--- |
| **Rychlá tvorba základní geometrie** (skicování/parametry) | Vysoká | Vysoká | Vysoká |
| **Nedestruktivní / Parametrické úpravy** (posouvání stěn, změny rozměrů) | Vysoká | Střední | Vysoká |
| **Čistá topologie** (pro textury a modifikátory) | Nízká | Vysoká | Střední |
| **Automatická a nedestruktivní tvorba otvorů** (okna, dveře) | Střední | Vysoká | Střední |
| **Přesné zadávání číselných hodnot** (metry, centimetry) | Vysoká | Střední | Nízká |
| **Obkreslování podloženého 2D půdorysu** (např. z PDF) | Střední | Vysoká | Nízká |
| **Modulární návaznosti místností a chodeb** | Vysoká | Nízká | Vysoká |
| **Bezproblémový export do herních enginů** (včetně kolizí) | Nízká | Nízká | Vysoká |
| **Přehled o ploše místností** (metry čtvereční) | Vysoká | Nízká | Irelevantní |

- Vysoká - Must Have
- Střední - Should have
- Nízká - Nice to have
- Irelevantní - out of scope

### Funkční požadavky
1. [Interaktivní tvorba místností a kreslení - Pencil Tool - UC 2.1, UC 3.1](./files/analyza_pozadavku.md#1-interaktivní-tvorba-místností-a-kreslení---pencil-tool)
2. [Generování a úprava parametrických objektů - UC 1.1, UC 2.2, UC 3.2](./files/analyza_pozadavku.md#2-generování-a-úprava-parametrických-objektů)
3. [Správa prostoru a metadat - UC 1.1, UC 1.2 ](./files/analyza_pozadavku.md#3-správa-prostoru-a-metadat)
4. [Finalizační nástroj - UC 3.2](./files/analyza_pozadavku.md#4-finalizační-nástroj)
5. [Kontextová nabídka - UC 1.2, UC 2.2](./files/analyza_pozadavku.md#5-kontextová-nabídka---pet-palette)
6. [Interaktivní 3D manipulátory - UC 1.2](./files/analyza_pozadavku.md#6-interaktivní-3d-manipulátory)

### Nefunkční požadavky
1. [Architektura a technologie](./files/analyza_pozadavku.md#1-architektura-a-technologie)
2. [Výkon a Nedestruktivnost](./files/analyza_pozadavku.md#2-výkon-a-nedestruktivnost)
3. [Použitelnost a UX](./files/analyza_pozadavku.md#3-použitelnost-a-ux)
4. [Automatické kótování](./files/analyza_pozadavku.md#4-automatické-kótování)

## Návrh UI
TODO
## Technická analýza a návrh architektury
TODO
