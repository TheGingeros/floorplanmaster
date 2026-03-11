# Analýza
Název projektu: Blender add-on pro parametrické modelování prostorových dispozic

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
2. [Vizualizátorka Klára](./files/cilove_skupiny.md#vizualizátorka-klára---zaměřeno-na-rychlost-a-čistou-topologii)
3. [Level Designer Tomáš](./files/cilove_skupiny.md#level-designer-tomáš---zaměřeno-na-blockout-a-hratelnost)

### Vstup
1. [2D podklady](./files/definice.md#2d-podklady)
2. [Kvantitativní zadání](./files/definice.md#kvantitativní-zadání-stavební-program)
3. [Čistý koncept](./files/definice.md#čistý-koncept-myšlenka)

### Výstup
1. [3D hmotový model](./files/definice.md#3d-hmotový-model-massing)
2. [Optimalizovaná geometrie pro export](./files/definice.md#optimalizovaná-geometrie-pro-export-blockout)
3. [Přehledná prostorová data](./files/definice.md#přehledná-prostorová-data)

### Uživatelské scénáře - use cases
1. [Scénář 1: Vytvoření základní místnosti pomocí kreslení](./files/cilove_skupiny.md#scénář-1-vytvoření-základní-místnosti-pomocí-kreslení)
2. [Scénář 2: Vytvoření základní místnosti pomocí parametrů](./files/cilove_skupiny.md#scénář-2-vytvoření-základní-místnosti-pomocí-parametrů)
3. [Scénář 3: Parametrická úprava místnosti](./files/cilove_skupiny.md#scénář-3-parametrická-úprava-místnosti)
4. [Scénář 4: Vložení otvoru do stěny](./files/cilove_skupiny.md#scénář-4-vložení-otvoru-do-stěny)

## Analýza požadavků
### Tabulka
| Potřeba / Funkční požadavek | Architekti | 3D Vizualizátoři | Game Designeři |
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
1. [Interaktivní tvorba místností a kreslení - Pencil Tool](./files/analyza_pozadavku.md#1-interaktivní-tvorba-místností-a-kreslení---pencil-tool)
2. [Generování a úprava parametrických objektů](./files/analyza_pozadavku.md#2-generování-a-úprava-parametrických-objektů)
3. [Správa prostoru a metadat](./files/analyza_pozadavku.md#3-správa-prostoru-a-metadat)
4. [Finalizační nástroj](./files/analyza_pozadavku.md#4-finalizační-nástroj)

### Nefunkční požadavky
1. [Architektura a technologie](./files/analyza_pozadavku.md#1-architektura-a-technologie)
2. [Výkon a Nedestruktivnost](./files/analyza_pozadavku.md#2-výkon-a-nedestruktivnost)
3. [Použitelnost a UX](./files/analyza_pozadavku.md#3-použitelnost-a-ux)

### Volitelné / Rozšiřující požadavky
1. [Kontextová nabídka](./files/analyza_pozadavku.md#1-kontextová-nabídka)
2. [Interaktivní 3D manipulátory](./files/analyza_pozadavku.md#2-interaktivní-3d-manipulátory)
3. [Automatické kótování](./files/analyza_pozadavku.md#3-automatické-kótování)

## Návrh UI
TODO
## Technická analýza a návrh architektury
TODO
