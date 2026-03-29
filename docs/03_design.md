# 3. Návrh (Design)

Tato sekce obsahuje úplnou specifikaci designu FloorPlanMaster addonu.

## Obsah

### [3.1 Architektura systému](./sections/03_Design/01_architecture.md)
- Třívrstvá hybridní architektura (Strukturální graf, Graf místností, Pojmenované atributy)
- MVC vzor v Blenderu
- Organizace modulů
- Diagramy toku dat
- Principy návrhu a technická rozhodnutí

### [3.2 Specifikace datových modelů](./sections/03_Design/02_data_models.md)
- **Vrstva 1**: Strukturální graf (uzly propojení, hrany stěn)
- **Vrstva 2**: Graf místností (sémantické vztahy)
- **Vrstva 3**: Pojmenované atributy (synchronizační most)
- Kompletní datové struktury s omezeními
- Vztahy a pravidla synchronizace
- Pravidla validace parametrů

### [3.3 Specifikace funkcí](./sections/03_Design/03_features.md)
- **FP1**: Nástroj Tužka (interaktivní kreslení)
- **FP2**: Parametrické generování a úprava
- **FP3**: Správa prostoru a metadat
- **FP4**: Nástroj finalizace
- **FP5**: Kontextová nabídka
- **FP6**: 3D manipulátory (gizmo)
- **FP7**: Automatické kótování
- Nefunkční požadavky (NP1, NP2, NP3)

### [3.4 Design uživatelského rozhraní](./sections/03_Design/04_ui_ux.md)
- Filozofie designu
- Layout UI (menu, properties panel, HUD viewport)
- Klávesové zkratky
- Barevná schémata
- Dialogová okna a modály
- Kontextové nabídky
- Funkce přístupnosti
- Responzivní design

### [3.5 Správa workflow a stavu](./sections/03_Design/05_state_management.md)
- Stavový automat modálního operátora (podrobné diagramy)
- Pipeline zpracování událostí
- Systém přichycování (osa, bod, mřížka, úhel)
- Integrace undo/redo
- Časování synchronizace geometrie
- Zpracování chyb a obnovení

### [3.6 API rozhraní a specifikace modulů](./sections/03_Design/06_api_interfaces.md)
- API jádra s úplnými podpisy metod
- `core.structural_graph.StructuralGraph`
- `core.room_graph.RoomGraph`
- `geometry.attribute_sync.AttributeSync`
- `operators.pencil_tool.PencilTool`
- Pomocné moduly
- Tok event systému

---

## Shrnutí filosofie designu

**FloorPlanMaster** používá **třívrstvou hybridní architekturu**:

1. **Vrstva 1: Topologické kostry** (NetworkX graf)
   - Čistá topologie: propojovací body a připojení stěn
   - Validace planarity, detekce cyklů
   - Nedestruktivní, trvalá ID místností

2. **Vrstva 2: Sémantický graf místností** (Duální graf)
   - Uzly místností, vztahy sousedství
   - Prostorová analýza (konektivita, cesty, analýzy)
   - Identita místnosti persituje across edits

3. **Vrstva 3: Synchronizační most** (Pojmenované atributy)
   - Serializace grafů do Blender mesh atributů
   - Geometry Nodes čtou atributy v reálném čase
   - Nedestruktivní generování geometrie

---

## Rychlá navigace

- **Začínáte implementací?** → Čtěte [3.1 Architektura](./sections/03_Design/01_architecture.md)
- **Potřebujete detaily datových struktur?** → Čtěte [3.2 Datové modely](./sections/03_Design/02_data_models.md)
- **Stavba nástroje Tužka?** → Čtěte [3.5 Správa stavu](./sections/03_Design/05_state_management.md) & [3.6 API](./sections/03_Design/06_api_interfaces.md)
- **Přidávání prvků UI?** → Čtěte [3.4 UI/UX](./sections/03_Design/04_ui_ux.md)
- **Chcete detaily funkcí?** → Čtěte [3.3 Funkce](./sections/03_Design/03_features.md)