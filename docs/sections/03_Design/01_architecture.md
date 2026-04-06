# 3.1 Architektura systému
Technická analýza (kapitola 2.6) identifikovala klíčové technologické volby pro realizaci addonu: Geometry Nodes jako výpočetní jádro pro generování 3D geometrie, strukturální graf a NRG pro datovou reprezentaci půdorysu, modální operátory pro interaktivní kreslení a pojmenované atributy jako synchronizační most mezi Pythonem a Blenderem. Tato sekce překládá analytické závěry do konkrétní softwarové architektury.

Základem návrhu je třívrstvá hybridní architektura, která striktně odděluje matematickou logiku v Pythonu od vizualizace v Blenderu. Python addon vlastní veškerou logiku — topologii stěn, sémantiku místností i validaci parametrů. Blender slouží výhradně jako zobrazovací engine, který skrze Geometry Nodes čte data z pojmenovaných atributů a generuje 3D geometrii v reálném čase. Komunikace je jednosměrná: Python → Blender, nikdy naopak. Scope návrhu je omezen na jedno podlaží — architektura je navržena tak, aby ji bylo v budoucnu možné rozšířit o hierarchii budov a pater, ale současný MVP pracuje s jedním půdorysem.

## [Třívrstvá hybridní architektura](./01_architecture_layers.md)

## Vzor MVC v kontextu Blenderu
Architektura přirozeně odpovídá vzoru Model-View-Controller přizpůsobenému prostředí Blenderu:

```mermaid
flowchart TD
    C["**CONTROLLER**<br/>Modální operátory + UI panely<br/>Zachytávají vstupy a volají metody Modelu"]:::ctrl
    M["**MODEL**<br/>Vrstva 1: Strukturální graf (stěny)<br/>Vrstva 2: Graf místností (místnosti)<br/>Čistý Python, bez závislosti na bpy"]:::model
    V3["**VRSTVA 3 — Synchronizační most**<br/>Pojmenované atributy na Blender mesh"]:::bridge
    V["**VIEW**<br/>Geometry Nodes — generuje 3D geometrii<br/>3D Viewport + GPU overlay"]:::view

    C -->|"volání metod"| M
    M -->|"synchronizační modul"| V3
    V3 -->|"čtení atributů"| V

    classDef ctrl   stroke:#d97c4a,stroke-width:2px
    classDef model  stroke:#4a90d9,stroke-width:2px
    classDef bridge stroke:#9b4ad9,stroke-width:2px
    classDef view   stroke:#4ad97c,stroke-width:2px
    linkStyle default stroke-width:2px
```

- **Model** — vrstvy 1 a 2 jsou čistě Python grafové struktury bez závislosti na Blender API; obsahují veškerou logiku: topologii stěn, sémantiku místností, validaci parametrů
- **Vrstva 3 (most)** — pojmenované atributy uložené na Blender mesh; synchronizační modul do nich zapisuje výsledky Modelu, Geometry Nodes je čtou jako vstupy; jednosměrný a jednoúčelový datový channel
- **View** — Geometry Nodes modifikátor generuje 3D geometrii čtením atributů z vrstvy 3; GPU overlay vykresluje kreslicí náhled a HUD nezávisle na GN
- **Controller** — modální operátory zachytávají uživatelské vstupy a překládají je na volání metod Modelu; UI panely zobrazují a umožňují editaci parametrů

## [Tok dat](./01_architecture_data_flow.md)

## [Organizace modulů](./01_architecture_modules.md)

## Principy návrhu
- **Oddělení zájmů** — grafová logika (Model) nezávisí na Blender API; lze ji testovat izolovaně jednotkovými testy
- **Nedestruktivní úpravy** — změna parametru nepřepisuje geometrii, ale vyvolá přegenerování skrze Geometry Nodes; uživatel se může kdykoli vrátit zpět nebo upravit libovolný parametr
- **Zpětná vazba v reálném čase** — každá změna v Modelu se okamžitě projeví ve View díky automatické reevaluaci Geometry Nodes modifikátoru
- **Modularita** — každý funkční požadavek (FP1–FP7) je realizován v samostatném Python modulu s jasně definovaným rozhraním
- **Konvence Blenderu** — addon dodržuje konvence pojmenování a registrace operátorů a panelů, integraci do nativního Undo/Redo systému a standardní strukturu addonu

## Klíčová technická rozhodnutí

| Rozhodnutí | Volba | Zdůvodnění (viz technická analýza) |
| :--- | :--- | :--- |
| Reprezentace geometrie | Geometry Nodes | Výkonnostně převyšují BMesh — paralelní zpracování, real-time feedback, multithreading ([2.6](../02_Analysis/06_ta_geometry_representation.md)) |
| Grafová knihovna | NetworkX (bundled) | Planární embedding, detekce cyklů, prostorové analýzy; knihovna je distribuována přímo s addonem pro splnění NP1 ([2.6](../02_Analysis/06_ta_data_model.md)) |
| Synchronizace Python↔Blender | Pojmenované atributy | Efektivní dávková serializace, přímé čtení v Geometry Nodes bez kopírování dat ([2.6](../02_Analysis/06_ta_saving_metadata.md)) |
| Interaktivní kreslení | Modální operátory | Jediný mechanismus pro kontinuální zachycení myši ve viewportu ([2.6](../02_Analysis/06_ta_modal_operators.md)) |
| Detekce místností | Lazy (po uzavření cyklu) | Místnost vzniká až při détekci uzavřeného cyklu ve Vrstvě 1, nikoli při nakreslení první stěny. Okamžité svázání stěny s "proto-místností" (eager binding) by bylo matematicky nekonzistentní — Layer 2 je definována jako duální graf cyklů Layer 1, takže bez cyklu neexistuje platná místnost. Navíc by eager přístup znemožnil deterministické přiřazení u T-spojů a větvení a hrozilo by rozbití identity místnosti při uzavření více cyklů najednou. Lazy detekce odpovídá standardnímu chování nástrojů jako ArchiCAD nebo Revit ([2.6](../02_Analysis/06_ta_hybrid_connection.md)) |
| Tvorba otvorů | GN Mesh Boolean | Architektura reprezentuje stěny jako hrany base meshe s pojmenovanými atributy — Curve Trimming vyžaduje Curve objekt jako vstup do GN, což je neslučitelné s mesh-based Vrstvou 3. GN Mesh Boolean zpracovává celé kolekce otvorů jako jeden sloučený vstup v O(m log m), bez nutnosti měnit reprezentaci stěn ([2.6](../02_Analysis/06_ta_holes_creation.md)) |
| Delegování výpočtů | Dávkové operace + GN backend | Překonání limitů interpretovaného Pythonu delegováním náročných výpočtů na C++ jádro Blenderu ([2.6](../02_Analysis/06_ta_limits_python_blender.md)) |
| Persistence globálních nastavení | Scene PropertyGroup | Projektová nastavení (výchozí tloušťka, výška, systém jednotek) jsou součástí `.blend` souboru; různé projekty mají nezávislé hodnoty; konzistentní s konvencemi Archimesh a Archipack. `AddonPreferences` se rezervují pro budoucí nastavení chování addonu (výkon, cesty), nikoli pro architektonická data ([2.6](../02_Analysis/06_ta_addon_preferences.md)) |
