# 3.5 MVP scope a rozšiřitelnost

Návrh addonu explicitně vymezuje rozsah první verze (MVP) a zároveň definuje architektonické principy, které umožní budoucí rozšíření bez nutnosti přepisovat jádro systému.

## MVP scope

MVP realizuje kompletní workflow jednoho podlaží: interaktivní kreslení stěn, automatická detekce místností, parametrické otvory, kótování a finalizaci do statické geometrie. Všechny funkční požadavky FP1–FP7 patří do MVP.

Následující funkce jsou záměrně vyloučeny z MVP:

| Funkce | Důvod vyloučení |
| :--- | :--- |
| Více podlaží a budovy | Vyžaduje hierarchii objektů nad současnou jednopodlažní vrstvou; architektura to umožňuje, ale není součástí MVP |
| Import DXF/IFC | Samostatná vstupní pipeline mimo scope kreslicího nástroje |
| Generování střech a schodišť | Komplexní geometrické úlohy nad rámec půdorysu |
| Spolupráce více, uživatelů | Blender jako aplikace nepodporuje simultánní editaci |
| Export do BIM formátů | Definováno jako možné rozšíření po MVP |

## Rozšiřitelnost architektury

Třívrstvá hybridní architektura je navržena tak, aby klíčová rozšíření nevyžadovala zásah do jádra Vrstvy 1 ani 2:

**Více podlaží** — Vrstva 1 (StructuralGraph) modeluje jeden půdorys jako planární graf. Hierarchie budov by přidala koordinační vrstvu nad stávající Vrstvy 1 a 2, které by zůstaly beze změny. Každé podlaží by bylo samostatnou instancí grafu.

**Nové typy prvků** — Stěny, okna a dveře jsou v datovém modelu reprezentovány jako hrany/atributy s typem. Přidání nového prvku (např. sloup, příčka) nevyžaduje změnu struktury grafu — stačí rozšířit sadu atributů a přidat odpovídající GN strom.

**Alternativní výstupní formáty** — Finalizační nástroj (FP4) pracuje výhradně s daty z Vrstvy 3 (AttributeSync). Přidání nového exportního formátu znamená implementaci alternativního konzumenta těchto dat bez změny zbytku systému.

**Nové nástroje kreslení** — Modální operátory (Controller) volají metody Vrstvy 1 přes stabilní rozhraní. Nový nástroj (např. kreslení místnosti jako polygonu) implementuje stejné rozhraní, aniž by zasahoval do datové logiky.
