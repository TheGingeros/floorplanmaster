# FP2 - Generování a úprava parametrických objektů
Tento požadavek definuje parametrické chování všech prvků půdorysu — stěn i otvorů. Každý prvek si pamatuje své parametry (délka, výška, tloušťka, pozice) a při jejich změně přepočítá svou geometrii, zachová relativní polohu navázaných otvorů a dynamicky vyřezává otvory pro okna a dveře pomocí Boolean operací v Geometry Nodes.
## Základ požadavku - must have:
- **Dynamická reprezentace stěn** - objekt stěny nebo otvorů není obyčejná mesh z polygonů, ale dynamický systém řízený vstupními parametry jako je délka, výška, tloušťka, pozice na ose
- **Dynamický update stěn při změně parametrů** - každý objekt si pamatuje své parametry, když se hodnota změní na posuvníku, addon musí tuto změnu zachytit pomocí funkce update a přepočítat geometrii
- **Dynamický posun otvorů při posunu stěn** - systém musí umět matematicky a datově svázat otvor s danou stěnou, pokud se stěna posune, všechny závislé otvory na ní musí s ní
- **Chytrá správa vytváření otvorů** - ořez otvorů řešen dynamicky, např. pomocí boolean operací v geometry nodes