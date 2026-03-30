# 3. Návrh (Design)
Tato kapitola představuje kompletní návrh addonu FloorPlanMaster. Zatímco předchozí analytická část definovala, co má systém umět, tento návrh exaktně specifikuje, jak toho bude technicky dosaženo. Základním stavebním kamenem celého řešení je sice třívrstvá hybridní architektura, která elegantně odděluje prostorovou matematiku v Pythonu od nedestruktivního 3D vykreslování v Blenderu, dokument však pokrývá kompletní životní cyklus aplikace.

Návrh detailně mapuje celou cestu od uživatelského rozhraní až po nízkoúrovňový kód. Definuje vizuální filozofii a ergonomii UI/UX, včetně panelů vlastností, klávesových zkratek a interaktivních 3D manipulátorů (gizmo) přímo ve viewportu. Tyto ovládací prvky jsou úzce navázány na detailní specifikaci funkcí, která překládá hrubé požadavky do konkrétních algoritmů – ať už jde o kreslení nástrojem Tužka, automatické kótování nebo závěrečnou finalizaci geometrie.

Pro zajištění absolutní stability v interaktivním prostředí Blenderu se návrh rigorózně věnuje správě stavů. Rozepisuje chování modálních operátorů pomocí stavových automatů, navrhuje robustní systém přichycování (snapping) a řeší korektní integraci do nativního Undo/Redo systému. Celou kapitolu pak uzavírá specifikace API, která definuje přesné popisy metod, datové modely a strukturu modulů, čímž vytváří jasný a jednoznačný podklad pro samotnou implementaci doplňku.

## [3.1 Architektura systému](./sections/03_Design/01_architecture.md)
- Třívrstvá hybridní architektura (Strukturální graf, Graf místností, Pojmenované atributy)
- MVC vzor v Blenderu
- Organizace modulů
- Diagramy toku dat
- Technická rozhodnutí

## [3.2 Specifikace datových modelů](./sections/03_Design/02_data_models.md)
- **Vrstva 1**: Strukturální graf (uzly propojení, hrany stěn)
- **Vrstva 2**: Graf místností (sémantické vztahy)
- **Vrstva 3**: Pojmenované atributy (synchronizační most)
- Kompletní datové struktury s omezeními
- Vztahy a pravidla synchronizace
- Pravidla validace parametrů

## [3.3 Specifikace funkcí](./sections/03_Design/03_features.md)
- **FP1**: Nástroj Tužka (interaktivní kreslení)
- **FP2**: Parametrické generování a úprava
- **FP3**: Správa prostoru a metadat
- **FP4**: Nástroj finalizace
- **FP5**: Kontextová nabídka
- **FP6**: 3D manipulátory (gizmo)
- **FP7**: Automatické kótování
- Nefunkční požadavky (NP1, NP2, NP3)

## [3.4 Design uživatelského rozhraní](./sections/03_Design/04_ui_ux.md)
- Filozofie designu
- Layout UI (menu, properties panel, HUD viewport)
- Klávesové zkratky
- Barevná schémata
- Dialogová okna a modály
- Kontextové nabídky
- Funkce přístupnosti
- Responzivní design

## [3.5 Správa workflow a stavu](./sections/03_Design/05_state_management.md)
- Stavový automat modálního operátora (podrobné diagramy)
- Pipeline zpracování událostí
- Systém přichycování (osa, bod, mřížka, úhel)
- Integrace undo/redo
- Časování synchronizace geometrie
- Zpracování chyb a obnovení

## [3.6 API rozhraní a specifikace modulů](./sections/03_Design/06_api_interfaces.md)
- API jádra s úplnými podpisy metod
- `core.structural_graph.StructuralGraph`
- `core.room_graph.RoomGraph`
- `geometry.attribute_sync.AttributeSync`
- `operators.pencil_tool.PencilTool`
- Pomocné moduly
- Tok event systému