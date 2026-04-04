# 3.3 Návrh funkcí
Analýza (kapitola 2.5) specifikovala sedm funkčních požadavků FP1–FP7 z pohledu uživatele — popsala *co* systém musí umět. Tato sekce překládá každý požadavek do návrhového řešení: *jak* ho realizovat v rámci třívrstvé architektury, jaké mechanismy využít a jak funkce interaguje s datovým modelem. Každý FP je vázán na jednu nebo více vrstev architektury a přispívá do životního cyklu půdorysu — od interaktivního kreslení přes parametrické úpravy a správu metadat až po finalizaci do statické geometrie.

| Požadavek | Název | Primární vrstva | Mechanismus |
| :--- | :--- | :--- | :--- |
| [FP1](./03_features_fp1.md) | Interaktivní kreslení (Pencil Tool) | Controller + Vrstva 1 | Modální operátor + GPU overlay |
| [FP2](./03_features_fp2.md) | Parametrické objekty a otvory | Vrstva 1 + View | Geometry Nodes + GN Mesh Boolean |
| [FP3](./03_features_fp3.md) | Detekce místností a metadata | Vrstva 2 + Vrstva 3 | Detekce cyklů + pojmenované atributy |
| [FP4](./03_features_fp4.md) | Finalizační nástroj | View | Aplikace GN modifikátorů |
| [FP5](./03_features_fp5.md) | Kontextová nabídka | Controller | Raycast + GPU/BLF overlay |
| [FP6](./03_features_fp6.md) | Interaktivní 3D manipulátory | Controller | Gizmo API |
| [FP7](./03_features_fp7.md) | Automatické kótování | View | BLF draw_handler + L1/L2 data |
