# Možnosti a limity Blender API
- co blender nativně umožňuje, jaké jsou hranice blender api a jak pracovat s interakcí v reálném čase
## Modální operátory - modal operators - FP1
- modální operátor je podtřída bpy.types.Operator
- na rozdíl od standartních operátorů, které vykonávají jednorázovou funkci a okamžitě skončí svou činnost, modální operátor zůstává aktivní a kontinuálně naslouchá událostem generovaným uživatelem nebo systémem
- nezbytný pro plynulé kreslení, kdy systém musí v každém okamžiku vědět, kde se nachází kurzor myši, a dynamicky na tuto polohu reagovat vizualizací budoucí geometrie
### Inicializace
- začíná metodou invoke() - připraví počáteční stav a registruje operátor do modálního handleru správce oken pomocí context.window_manager.modal_handler_add(self)
- od toho momentu je každá událost ve viewportu, jako je pohyb myši, stisk klávesy nebo rotace pohledu, předávána metodě modal()
### Návratové hodnoty
- určují, jakým způsobem bude blender s událostí dále nakládat

| Návratová hodnota | Funkční dopad na systém | Architektonický význam |
| :--- | :--- | :--- |
| `RUNNING_MODAL` | Operátor pokračuje v běhu a čte událost | Umožňuje plynulé tažení stěny nebo změnu rozměru |
| `PASS_THROUGH` | Operátor běží, ale událost je předána dalším nástrojům | Nezbytné pro zoomování a rotaci pohledu během kreslení |
| `FINISHED` | Operátor končí a systém generuje Undo krok | Finalizuje umístění stěny a ukládá ji do databáze scény |
| `CANCELLED` | Operátor končí bez uložení změn a bez Undo kroku | Umožňuje uživateli přerušit akci klávesou ESC | 
## Vykreslování vlastního UI ve scéně - FP7
## Limity výkonu Pythonu v Blenderu