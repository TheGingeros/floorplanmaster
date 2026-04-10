# 2.5 Analýza požadavků
Analýza požadavků převádí identifikované potřeby uživatelů a scénáře použití do strukturovaných funkčních a nefunkčních požadavků. Funkční požadavky jsou organizovány do sedmi balíčků (FP1–FP7), nefunkční do tří oblastí (NP1–NP3). Kapitolu uzavírají dvě prioritizační tabulky: mapování požadavků na scénáře použití a vážená prioritizace podle cílových skupin.
## [Funkční požadavky](./05_func_requirements.md)
## [Nefunkční požadavky](./05_nonfunc_requirements.md)
## Tabulka požadavků a scénářů použití
Následující tabulka mapuje každý funkční balíček na scénáře použití, které ho motivují. Prázdná buňka znamená, že daná funkce není pro tento scénář vyžadována.

| Požadavek | UC 1.1 | UC 1.2 | UC 2.1 | UC 2.2 | UC 3.1 | UC 3.2 | UC 1.3 | UC 2.3 | UC 3.3 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FP1 - Interaktivní tvorba místností a kreslení** |  | Ano | Ano | | Ano | | | | |
| **FP2 - Generování a úprava parametrických objektů** | Ano | Ano | Ano | Ano | Ano | Ano | | | |
| **FP3 - Správa prostoru a metadat** | Ano | Ano | Ano | | Ano | Ano | | | |
| **FP4 - Finalizační nástroj** |  |  |  | Ano | | Ano | | | |
| **FP5 - Kontextová nabídka** |  |  |  |  | | | | Ano | |
| **FP6 - Interaktivní 3D manipulátory** |  |  |  |  | | | | | Ano |
| **FP7 - Automatické kótování** |  |  |  |  | | | Ano | | |
## Tabulka požadavků a jejich priorit
Každý požadavek je hodnocen zvlášť každou cílovou skupinou (Vysoká / Střední / Nízká / Irelevantní) a výsledná priorita se stanovuje jako vážený průměr s koeficienty odpovídajícími důležitosti skupiny (architekti ×3, vizualizátoři ×2, game designéři ×1).

| Požadavek | Architekti | 3D Vizualizátoři | Game Designeři | Vážený průměr | Výsledná priorita |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FP1 - Interaktivní tvorba místností a kreslení** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **FP2 - Generování a úprava parametrických objektů** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **FP6 - Interaktivní 3D manipulátory** | Střední | Střední | Nízká | **1,83** | **Střední** |
| **FP3 - Správa prostoru a metadat** | Vysoká | Nízká | Irelevantní | **1,83** | **Střední** |
| **FP7 - Automatické kótování** | Vysoká | Nízká | Irelevantní | **1,83** | **Střední** |
| **FP4 - Finalizační nástroj** | Nízká | Střední | Vysoká | **1,67** | **Střední** |
| **FP5 - Kontextová nabídka** | Střední | Nízká | Nízká | **1,50** | **Střední** |
| **NP1 - Architektura a technologie** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **NP2 - Výkon a Nedestruktivnost** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **NP3 - Použitelnost a UX** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |


- Vážený průměr = (Priorita architektů × 3 + Priorita 3D umělců × 2 + Priorita game designerů × 1) / 6
- Vysoká - Must Have - váha 3 — výsledný průměr ≥ 2,50
- Střední - Should have - váha 2 — výsledný průměr 1,00–2,49
- Nízká - Nice to have - váha 1 — výsledný průměr < 1,00
- Irelevantní - out of scope - váha 0