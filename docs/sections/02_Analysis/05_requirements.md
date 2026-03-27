# 2.5 Analýza požadavků
úvod todo
## [Funkční požadavky](./05_func_requirements.md)
## [Nefunkční požadavky](./05_nonfunc_requirements.md)
## Tabulka požadavků a scénářů použití

| Požadavek | UC 1.1 | UC 1.2 | UC 2.1 | UC 2.2 | UC 3.1 | UC 3.2 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FP1 - Interaktivní tvorba místností a kreslení** |  |  | Ano | | Ano | |
| **FP2 - Generování a úprava parametrických objektů** | Ano |  |  |Ano | | Ano|
| **FP3 - Správa prostoru a metadat** | Ano | Ano |  | | | |
| **FP4 - Finalizační nástroj** |  |  |  | | |Ano |
| **FP5 - Kontextová nabídka** |  | Ano |  | Ano| | |
| **FP6 - Interaktivní 3D manipulátory** |  | Ano |  | | | |
| **FP7 - Automatické kótování** | Ano | Ano |  | | | |
## Tabulka požadavků a jejich priorit

| Požadavek | Architekti | 3D Vizualizátoři | Game Designeři | Vážený průměr | Výsledná priorita |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FP1 - Interaktivní tvorba místností a kreslení** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **FP2 - Generování a úprava parametrických objektů** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **FP6 - Interaktivní 3D manipulátory** | Vysoká | Střední | Vysoká | **2,67** | **Vysoká** |
| **FP3 - Správa prostoru a metadat** | Vysoká | Nízká | Irelevantní | **1,83** | **Střední** |
| **FP7 - Automatické kótování** | Vysoká | Nízká | Irelevantní | **1,83** | **Střední** |
| **FP4 - Finalizační nástroj** | Nízká | Střední | Vysoká | **1,67** | **Střední** |
| **FP5 - Kontextová nabídka** | Střední | Nízká | Nízká | **1,50** | **Střední** |
| **NP1 - Architektura a technologie** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **NP2 - Výkon a Nedestruktivnost** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |
| **NP3 - Použitelnost a UX** | Vysoká | Vysoká | Vysoká | **3,00** | **Vysoká** |


- Vážený průměr = (Priorita architeků * 3 + Priorita 3D Umělců * 2 + Priorita Game designerů * 1) / 6
- Vysoká - Must Have - váha 3
- Střední - Should have - váha 2
- Nízká - Nice to have - váha 1
- Irelevantní - out of scope - váha 0