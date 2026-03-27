# Nefunkční požadavky
## NP1 - Architektura a technologie
- geometry nodes jako výpočetní jádro addonu
- logika tvarování geometrie bude díky geometry nodes stromům
- python bude sloužit jako manažer, které tyto stromy bude připojovat a měnit jejich vstupy
- oddělení vizuální logiky a aplikační logiky
- zero dependency - addon nesmí k běhu potřebovat doinstalování externích knihoven - pro běžného uživatele složité
- vše se musí zvládnout pomocí bpy a standardní knihovny Python

## NP2 - Výkon a Nedestruktivnost
- systém musí reagovat plynule, netrhat se a uživatel nesmí ztratit možnost úpravy ani pro komplexních úpravách a generace
- minimalizace výpočetní náročnosti při operacích
- důraz na optimalizaci při přepočtu parametrů
- respektování [DepsGraph](../../files/00_definitions.md#depsgraph---dependency-graph) - systém závislostí v Blenderu, aby nedocházelo ke zbytečným cyklickým přepočtům celé scény

## NP3 - Použitelnost a UX
- vzhled addonu by měl působit jako nativní součást blenderu
- striktní použití zabudovaných UI komponent - UILayout.row atd
- logické seskupování nástrojů do záložek, přidávání Tooltips
- důraz na ošetření chyb - srozumitelný feedback při špatných operací, například přidání okna do stěny, která je menší než zadaná velikost okna