# 3.4 Návrh funkcí
Analýza (kapitola 2.5) specifikovala sedm funkčních požadavků FP1–FP7 z pohledu uživatele — popsala *co* systém musí umět. Tato sekce překlápí abstraktní datové toky a modely do reálných akcí a operátorů: *jak* každý požadavek realizovat v rámci třívrstvé architektury (kapitola 3.2), jaké mechanismy využít a jak funkce interaguje s datovým modelem (kapitola 3.3). Každá událost (např. kliknutí nástrojem) spoustí konkrétní datový tok v architektuře. Prvky označené jako must-have (viz MVP scope, kapitola 3.1) jsou povinné pro MVP; should-have a nice-to-have prvky jsou exlicitně označeny a odloženy za MVP.

| Požadavek | Název | Primární vrstva | Mechanismus |
| :--- | :--- | :--- | :--- |
| [FP1](./04_features_fp1.md) | Interaktivní kreslení (Pencil Tool) | Controller + Vrstva 1 | Modální operátor + GPU overlay |
| [FP2](./04_features_fp2.md) | Parametrické objekty, otvory a vložení místnosti z parametrů | Vrstva 1 + View + Controller | Geometry Nodes + GN Mesh Boolean + N-panel |
| [FP3](./04_features_fp3.md) | Detekce místností a metadata | Vrstva 2 + Vrstva 3 | Detekce cyklů + pojmenované atributy |
| [FP4](./04_features_fp4.md) | Finalizační nástroj | View | Aplikace GN modifikátorů |
| [FP5](./04_features_fp5.md) | Kontextová nabídka | Controller | Raycast + GPU/BLF overlay |
| [FP6](./04_features_fp6.md) | Interaktivní 3D manipulátory | Controller | Gizmo API |
| [FP7](./04_features_fp7.md) | Automatické kótování | View | BLF draw_handler + L1/L2 data |
