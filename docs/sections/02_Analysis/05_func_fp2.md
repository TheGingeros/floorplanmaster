# FP2 - Generování a úprava parametrických objektů
úvod todo
## Základ požadavku - must have:
- **Dynamická reprezentace stěn** - objekt stěny nebo otvorů není obyčejná mesh z polygonů, ale dynamický systém řízený vstupními parametry jako je délka, výška, tloušťka, pozice na ose
- **Dynamický update stěn při změně parametrů** - každý objekt si pamatuje své parametry, když se hodnota změní na posuvníku, addon musí tuto změnu zachytit pomocí funkce update a přepočítat geometrii
- **Dynamický posun otvorů při posunu stěn** - systém musí umět matematicky a datově svázat otvor s danou stěnou, pokud se stěna posune, všechny závislé otvory na ní musí s ní
## Rozšíření požadavku - should have:
- **Chytrá správa vytváření otvorů** - ořez otvorů řešen dynamicky, např. pomocí boolean operací v geometry nodes