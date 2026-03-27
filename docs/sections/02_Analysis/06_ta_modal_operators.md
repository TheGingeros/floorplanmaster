# Modální operátory
## Obecně
- modální operátor je podtřída `bpy.types.Operator`
- na rozdíl od standartních operátorů, které vykonávají jednorázovou funkci a okamžitě skončí svou činnost, modální operátor zůstává aktivní a kontinuálně naslouchá událostem generovaným uživatelem nebo systémem
- nezbytný pro plynulé kreslení, kdy systém musí v každém okamžiku vědět, kde se nachází kurzor myši, a dynamicky na tuto polohu reagovat vizualizací budoucí geometrie
- důležité je dodržování konvencí pojmenovávání a struktury kódu
- třídy jsou camelcase, metody pak malými písmeny s podtržítky
- v architektonickém kontextu je důležité oddělit logiku interakce od logiky datového modelu
- operátory by měly fungovat pouze jako tenká vrstva volající vysokoúrovňové funkce, což usnadní testování a opětovnou použitelnost kódu mimo modální kontext

## Inicializace
- začíná metodou `invoke()` - připraví počáteční stav a registruje operátor do modálního handleru správce oken pomocí `context.window_manager.modal_handler_add(self)`
- od toho momentu je každá událost ve viewportu, jako je pohyb myši, stisk klávesy nebo rotace pohledu, předávána metodě `modal()`
### Návratové hodnoty
- určují, jakým způsobem bude blender s událostí dále nakládat

| Návratová hodnota | Funkční dopad na systém | Architektonický význam |
| :--- | :--- | :--- |
| `RUNNING_MODAL` | Operátor pokračuje v běhu a čte událost | Umožňuje plynulé tažení stěny nebo změnu rozměru |
| `PASS_THROUGH` | Operátor běží, ale událost je předána dalším nástrojům | Nezbytné pro zoomování a rotaci pohledu během kreslení |
| `FINISHED` | Operátor končí a systém generuje Undo krok | Finalizuje umístění stěny a ukládá ji do databáze scény |
| `CANCELLED` | Operátor končí bez uložení změn a bez Undo kroku | Umožňuje uživateli přerušit akci klávesou ESC | 

## Zpracování událostí a stavový automat v metodě modal()
#### Princip fungování
- metoda `modal()` funguje na principu stavového automatu - programátorský vzor, který umožňuje operátoru měnit své chování v závislosti na tom, v jaké fázi interakce se uživatel právě nachází
- metoda je volána Blenderem při každé události, aby operátor věděl, co má v danou chvíli dělat, musí si v instanci třídy uchovávat informaci o aktuálním stavu
- bez stavového automatu by modal pouze reagovala na izolované událostix

#### Typické stavy pro kreslení půdorysu
- `START` - operátor byl spuštěn, čeká na první kliknutí myši pro určení počátečního bodu
- `DRAWING` - uživatel pohnul myší po prvním kliknutí, v tomto stavu modal neustále přepočítává délku a úhel stěn a přes `gpu` modul vykresluje náhledovou linku
- `EXTRUDING` - po druhém kliknutí se může stav změnit na definování tloušťky nebo výšky stěny
- `FINISHING` - probíhá zápis reálné geometrie do scény a čištění draw handlerů
- implementace je většinou pomocí if/else statementu nebo pomocí match v novější verzi Pythonu
#### Klíčové výhody pro architektonické doplňky
- **Řízení složitosti** - umožňuje implementovat krok za krokem nástroje
- **Interaktivní snapping** - v stavu může být snapping aktivní jinak, ve stavu `DRAWING` může systém prioritně přichytávat k osám, zatímco ve stavu `IDLE` k vrcholům existujících objektů
- **Optimalizace výkonu** - stavový automat brání zbytečným výpočtům, složité operace, jako je generování bmesh nebo aktualizace modifikátorů, se spouštějí pouze při přechodu mezi stavy, zatímco při pohybu myši se aktualizuje pouze lehká vizualizace přes modul `gpu`

[Zdroje](../../files/00_sources.md#modální-operátory---modal-operators---fp1)