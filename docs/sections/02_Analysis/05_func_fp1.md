# FP1 - Interaktivní tvorba místností a kreslení - Pencil Tool
Pencil Tool je primárním vstupním nástrojem addonu, který umožňuje uživateli definovat půdorys klikáním bodů přímo ve 3D viewportu. Základem je modální operátor, jenž přebírá veškerou interakci s myší a klávesnicí po dobu kreslení a průběžně generuje stěny. Rozšiřující požadavky zahrnují automatický snapping k osám a průběžný vizuální náhled kreslené stěny před jejím potvrzením.
## Základ požadavku - must have:
- **Kreslení půdorysu v top view** - doplněk umožní uživateli definovat půdorys klikáním bodů ve 3D prostoru v pohledu shora
- **Nástroj jako modální operátor** - stav, kdy addon přebírá všechny vstupy z myši a klávesnice
## Rozšíření požadavku - should have:
- **Automatický snapping k osám XYZ** - kontrola vzdálenosti kurzoru od existujích bodů nebo os a pokud je dostatečně blízko, zarovná ho k nim
## Rozšíření požadavku - nice to have:
- **Vykreslování náhledu nové stěny před potvrzením** - systém musí neustále zachytávat pozici kurzoru, vykreslovat náhled budoucí stěny a čekat na kliknutí, zadání čísla nebo stisk klávesy enter