# Design - Rychlá reference

Tato složka obsahuje úplnou specifikaci designu FloorPlanMaster addonu.

## Obsah

### 00_design_checklist.md
**Kontrolní seznam designu** - Verifikace všech designových rozhodnutí a požadavků

### 01_architecture.md
**Architektura systému** - Třívrstvá architektura, principy návrhu, organizace modulů
- Vrstva 1: Strukturální graf (propojení, stěny)
- Vrstva 2: Graf místností (cykly, sousedství)
- Vrstva 3: Synchronizace s Blenderem
- MVC vzor a komunikace mezi moduly

### 02_data_models.md
**Datové modely** - Struktury dat ve vrstvách 1-3
- Datové typy a atributy
- API operace tříd
- Serializace a perzistence

### 03_features.md
**Specifikace funkcí** - Podrobný popis všech funkcí (FP1-FP7)
- FP1: Nástroj Tužka - interaktivní kreslení
- FP2: Parametrické generování
- FP3: Správa prostoru a metadat
- FP4: Finalizace
- FP5: Kontextová nabídka
- FP6: 3D manipulátory
- FP7: Automatické kótování

### 04_ui_ux.md
**Uživatelské rozhraní** - Rozvrh UI, prvky interakce, vizuální styl
- Layout pracovního prostoru
- HUD overlay
- Dialogy a panely
- Klávesové zkratky
- Barvy a typografie

### 05_state_management.md
**Správa stavu** - Stavové automaty, event pipeline, snapping
- Stavy operátora Tužka
- Zpracování vstupů
- Snapping mechanismy (grid, angle, point, axis)
- Undo/redo systém
- Optimalizace výkonu

### 06_api_interfaces.md
**API a třídy** - Úplná specifikace Python API
- Třída StructuralGraph (vrstva 1)
- Třída RoomGraph (vrstva 2)
- Třída AttributeSync (vrstva 3)
- Operátory a panely
- Výčty a konstanty

---

## Jak čít dokumenty

**Počáteční přečtení**: 01_architecture.md → 02_data_models.md → 00_design_checklist.md

**Pro konkrétní funkci**: Jít do 03_features.md, najít FP* specifikaci

**Pro UI/UX**: Čtěte 04_ui_ux.md

**Pro implementaci stavů**: Čtěte 05_state_management.md

**Pro Python API**: Čtěte 06_api_interfaces.md

---

## Konvence

### Pojmenování
- Třídy: PascalCase (např. `StructuralGraph`, `Room`)
- Metody/funkce: snake_case (např. `add_junction()`, `detect_cycles()`)
- Konstanta: UPPER_SNAKE_CASE (např. `WALL_ATTRS`, `ROOM_TYPES`)
- Privátní metody: `_snake_case` (např. `_distance()`)

### Blender atributy
- Pojmenované objekty: `type_ID` (např. `junction_42`, `wall_3`)
- Custom properties: Blender native `obj['prop_name']`
- Pojmenované atributy: `mesh.attributes['attr_name']`

### Jednotky
- Délka: Metrů (m)
- Plocha: Metrů čtvereční (m²)
- Úhel: Stupní (°) v UI, radiánů v kódu
- Toleranční vzdálenost: 0.01m (vnitřní), 15px (obrazovka)

### Kódování
- Python: UTF-8
- Markdown: UTF-8
- Diagrams: ASCII art (kompatibilní s all terminály)

---

## Nefunkční požadavky

### Výkon
- Zpracování 50+ místností bez prodlení
- < 100ms doba odezvy na vstup
- Náhled v reálném čase (60 FPS)

### Nedestruktivnost
- ID místností zůstávají perzistentní
- Plná podpora Blender Undo/Redo
- Efektivní ukládání stavu

### Integrace
- Kompatibilita s Blender 3.2+
- Blender Python API (bpy, bmesh, gpu)
- NetworkX pro algoritmy grafů

### Přístupnost
- Klávesové zkratky pro všechny funkce
- Jasné chybové zprávy
- Nápověda v aplikaci (HUD, tooltips)

---

## Postup implementace

1. **Fáze 1 - Jádro** (Vrstva 1-2 + Tužka FP1)
   - Dokumenty: 01_architecture, 02_data_models, 03_features (FP1), 05_state_management
   - Výstupy: Fungující kreslení základního půdorysu

2. **Fáze 2 - Rozšíření** (Zbývající features)
   - Dokumenty: 03_features (FP2-FP7), 04_ui_ux, 06_api_interfaces
   - Výstupy: Parametrizace, manipulátory, finalizace

3. **Fáze 3 - Integrace** (Testování, dokumentace)
   - Testy: Unit testy vrstva 1-2, integrační testy operátorů
   - Dokumentace: User guide, troubleshooting, FAQ

---

## Poznámky pro budoucí vývoj

### Možná rozšíření
- Automatické generování okne a dveří
- Detekce architekturních chyb (např. nefunkční místnosti)
- Export do standardních formátů (DWG, IFC)
- Import ze stávajících plánů (tato aktuální beta nerealizuje)
- Kolaborativní editace

### Technické úpravy
- Migrovat z NetworkX na vlastní strukturu pro lepší kontrolu
- Zvážit GPU akceleraci pro velké grafy
- Implementovat delta compression pro undo/redo
- Cachování geometrie Geometry Nodes

### UX vylepšení
- Automatické úpravy při přesunu propojení
- Visuální návrhy při nevhodném kreslení
- Tipy pro optimalizaci prostoru
- Podpora redos/undo animací

---

## Kontakt a zpětná vazba

Odesílej bug reportsne na: [issues URL]
Požadavky na funkce: [features URL]
