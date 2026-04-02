# 3.1 Architektura systému
Tato sekce popisuje třívrstvou hybridní architekturu FloorPlanMaster. Je to klíč k pochopení, jak se data proudí mezi jednotlivými komponenty a jak se udržuje konzistence při interakci uživatele. FloorPlanMaster není jen běžné GUI - je to komplexní datový systém, který kombinuje tři odlišné reprezentace půdorysu:
- **Vrstva 1 (Topologie)**: čistý graf propojovacích bodů a stěn - to, co měří a propojuje
- **Vrstva 2 (Sémantika)**: graf místností a jejich vztahů - to, co architekt chápe a používá
- **Vrstva 3 (Synchronizace)**: Blender atributy a Geometry Nodes - to, co vidí na obrazovce

Tato architektura zajišťuje nedestruktivní úpravy půdorysu bez ztráty informací a aktualizaci geometrie v reálném čase. Komunikace vrstev je striktně jednosměrná: grafy v Pythonu vypočítají nová data a skrze pojmenované atributy (Named Attributes) je předají do Blender sítě, kde je Geometry Nodes okamžitě vykreslí.

Systém přímo aplikuje návrhový vzor MVC, kde Python grafy tvoří nezávislý Model, Blender UI a 3D pohled fungují jako View a modální operátory zachytávající kliknutí myší slouží jako Controller. Celý datový tok tak začíná uživatelským vstupem, který změní čistou topologii, což automaticky vyvolá přepočet sémantiky místností a končí instantním překreslením 3D geometrie, aniž by se tyto vrstvy do sebe funkčně zamotaly.

Aby byla matematicky zaručena striktní planarita topologických grafů i u vícepodlažních objektů, zavádí architektura zastřešující hierarchii - budovu. Každé podlaží budovy (Přízemí, 1. Patro) funguje jako zcela nezávislý ekosystém se svou vlastní Vrstvou 1 a Vrstvou 2. Uživatel v UI vždy pracuje v kontextu aktivního podlaží, čímž se zabraňuje neplatnému křížení stěn mezi patry. Pro optimalizaci a snadnou správu viditelnosti (skrývání pater ve viewportu) se pak každé podlaží generuje jako samostatný 3D objekt s vlastním Geometry Nodes modifikátorem.

## [Vrstvy architektury](./01_architecture_layers.md)
- Vrstva 1: Topologický skelet (Strukturální graf)
- Vrstva 2: Sémantický graf místností (Duální graf)
- Vrstva 3: Most synchronizace (Pojmenované atributy)

## [Vzor MVC v Blenderu](./01_architecture_mvc.md)
- diagram MVC

## [Organizace modulů](./01_architecture_modules_struct.md)
- reprezentace organizace modulů

## [Tok dat: Základní operace](./01_architecture_data_flow.md)
- Kreslení půdorysu (FP1 - Nástroj Tužka)
- Úprava vlastností místnosti
- Finalizace (FP4 - Převod na trvalou geometrii)

## [Principy návrhu](./01_architecture_design_principles.md)
- Oddělení zájmů
- Nedestruktivní úpravy
- Zpětná vazba v reálném čase
- Modularita
- Osvědčené postupy Blenderu

## [Technická rozhodnutí a zdůvodnění](./01_architecture_technical_decisions.md)
- tabulka rozhodnutí
