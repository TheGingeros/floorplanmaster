# 3. Návrh (Design)
FloorPlanMaster je postaven na třívrstvé hybridní architektuře, kterou jsme zkoumali v předchozí kapitole v rámci technické analýzy. Tyto vrstvy kombinují grafové datové struktury s nativními systémy Blenderu. První vrstu tvoří topologické kostry stěn místností. V této vrstvě se řeší spojování stěn, detekce cyklů, resp. místností a jejich uzavřenost. Druhá vrstva obsahuje sématické grafy místností a jejich sousednosti. Tato vrsta zkoumá propojení místností, jak funkční(dveře nebo okna), tak nefuknční(sousedící stěny místností). Tyto dvě vrsty jsou propojeny třetí vrstvou, která představuje sychronizační most. Stará se o serializaci grafů do Blender mesh atributů. Ty pak Geometry nodes čtou v reálném čase a provádí nedestruktivní generování geometrie. 

## [3.1 Architektura systému](./sections/03_Design/01_architecture.md)
- Třívrstvá hybridní architektura (Strukturální graf, Graf místností, Pojmenované atributy)
- MVC vzor v Blenderu
- Organizace modulů
- Diagramy toku dat
- Principy návrhu a technická rozhodnutí

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