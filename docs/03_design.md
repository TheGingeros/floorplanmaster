# 3. Návrh (Design)
Tato kapitola představuje kompletní návrh addonu FloorPlanMaster. Zatímco předchozí analytická část definovala, co má systém umět, tento návrh exaktně specifikuje, jak toho bude technicky dosaženo. Základním stavebním kamenem celého řešení je sice třívrstvá hybridní architektura, která elegantně odděluje prostorovou matematiku v Pythonu od nedestruktivního 3D vykreslování v Blenderu, dokument však pokrývá kompletní životní cyklus aplikace.

Návrh detailně mapuje celou cestu od uživatelského rozhraní až po nízkoúrovňový kód. Definuje vizuální filozofii a ergonomii UI/UX, včetně panelů vlastností, klávesových zkratek a interaktivních 3D manipulátorů (gizmo) přímo ve viewportu. Tyto ovládací prvky jsou úzce navázány na detailní specifikaci funkcí, která překládá hrubé požadavky do konkrétních algoritmů – ať už jde o kreslení nástrojem Tužka, automatické kótování nebo závěrečnou finalizaci geometrie.

Pro zajištění absolutní stability v interaktivním prostředí Blenderu se návrh rigorózně věnuje správě stavů. Rozepisuje chování modálních operátorů pomocí stavových automatů, navrhuje robustní systém přichycování (snapping) a řeší korektní integraci do nativního Undo/Redo systému. Celou kapitolu pak uzavírá specifikace API, která definuje přesné popisy metod, datové modely a strukturu modulů, čímž vytváří jasný a jednoznačný podklad pro samotnou implementaci doplňku.

## [3.1 Architektura systému](./sections/03_Design/01_architecture.md)
- Vrstvy architektury
- MVC vzor v Blenderu
- Organizace modulů
- Tok dat: Základní operace
- Principy návrhu
- Technická rozhodnutí a zdůvodnění

## [3.2 Specifikace datových modelů](./sections/03_Design/02_data_models.md)
- Hierarchie budovy (Zastřešující modely)
- Vrstva 1: Strukturální graf - Detailní specifikace
- Vrstva 2: Graf místností - Detailní specifikace
- Vztah mezi vrstvou 1 a 2
- Vrstva 3: Pojmenované atributy - Kompletní specifikace
- Pravidla validace parametrů

## [3.3 Specifikace funkcí](./sections/03_Design/03_features.md)
- FP1: Nástroj Tužka - Interaktivní kreslení půdorysů
- FP2: Parametrické generování a úprava
- FP3: Správa prostoru a metadat
- FP4: Nástroj finalizace
- FP5: Kontextová nabídka
- FP6: Interaktivní 3D manipulátory (Gizma)
- FP7: Automatické kótování
- Nefunkční požadavky (NP1, NP2, NP3)

## 3.4 Design uživatelského rozhraní

## 3.5 Správa workflow a stavů

## 3.6 API rozhraní a specifikace modulů