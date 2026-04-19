# 3.1 Definice MVP scopu a rozšiřitelnosti

Dříve než bude popsána architektura, datový model a jednotlivé funkce, je nutné přesně vymezit hranice projektu. Tato sekce definuje, co je a co záměrně není součástí aktuálního návrhu, a slouží jako výchozí bod pro všechna následující technologická a designová rozhodnutí. Jasné mantinely umožňují obhájit každé návrhové rozhodnutí vůči pevně stanoveným cílům.

## Prioritizace prvků

Funkční požadavky FP1–FP7 z analýzy (kapitola 2.5) jsou rozděleny na dílčí prvky, z nichž každý nese prioritu:

- **Must-have** — prvky tvořící jádro MVP. Bez nich addon nesplňuje minimální funkční požadavky a nemůže být nasazen. Tyto prvky jsou předmětem celého následujícího návrhu (kapitoly 3.2–3.5) a jejich pokrytí je ověřeno v kapitole 3.6 (Testování a validace návrhu).
- **Should-have** — prvky s vysokou hodnotou, které rozšiřují použitelnost addonu, ale nejsou podmínkou funkčního MVP. Jsou prioritní pro budoucí rozšíření.
- **Nice-to-have** — prvky zvyšující komfort (vizuální zpětná vazba, pokročilý snapping), implementované sekundárně po should-have prvcích.

Konkrétní označení každého dílčího prvku je uvedeno přímo v návrhu příslušného funkčního požadavku (kapitola 3.4).

## Rozsah MVP

MVP realizuje kompletní workflow jednoho podlaží: interaktivní kreslení stěn, automatickou detekci místností, parametrické otvory, kótování a finalizaci do statické geometrie. Do MVP patří výhradně must-have prvky:

| Požadavek | MVP základ (must-have) |
| :--- | :--- |
| FP1 | Kreslení půdorysu klikáním bodů v top view; nástroj jako modální operátor |
| FP1 | GPU overlay náhled stěny a HUD |
| FP2 | Dynamická reprezentace stěn řízená parametry; update geometrie při změně parametrů; svázání otvorů se stěnou; GN Mesh Boolean pro vizuální výřez otvorů |
| FP3 | Automatická detekce uzavřených místností; zobrazení plochy místnosti |
| FP4 | Aplikace modifikátorů a finalizace do statické geometrie |

## Záměrně vyloučené prvky

Následující should-have a nice-to-have části požadavků FP1, FP2 a FP3 jsou záměrně odloženy za MVP:

| Zdroj | Odložený prvek | Priorita |
| :--- | :--- | :--- |
| FP1 | Snap na osu, mřížku a úhel | should-have |
| FP1 | Mód preview čáry stěny | should-have |
| FP3 | Hierarchizace místností | nice-to-have |
| FP5 | Kontextová nabídka | should-have |
| FP6 | Interaktivní 3D manipulátory | should-have |
| FP7 | Automatické kótování | should-have |

Vše nad rámec jednoho podlaží (více podlaží, import DXF/IFC, generování střech a schodišť, export do BIM formátů, napojení místnosti na existující půdorys) leží mimo scope celého návrhu.
