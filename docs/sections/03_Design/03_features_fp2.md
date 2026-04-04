# FP2 — Parametrické objekty a otvory
Analýza (FP2) definovala požadavek na dynamickou, nedestruktivní reprezentaci stěn a otvorů — model řízený parametry, ne statická polygonová síť. Návrhové rozhodnutí (kapitola 3.1) zvolilo Geometry Nodes jako výpočetní backend a pojmenované atributy jako datový bridge. Tato sekce popisuje, jak se parametrické chování realizuje v interakci Vrstvy 1, Vrstvy 3 a View.

## Parametry stěny a update mechanismus

Každá stěna ve Vrstvě 1 nese atributy `thickness`, `height` a `material_id`. Změna kteréhokoli parametru přes UI panel nebo 3D manipulátor (FP6) spustí přesně definovaný update cyklus:

1. Validace nové hodnoty vůči povoleným rozsahům (viz datový model, kapitola 3.2)
2. Zápis aktualizované hodnoty do Vrstvy 1
3. Pokud změna ovlivňuje metriku místnosti (`height` → maximální výška) → Vrstva 2 přepočítá dotčené místnosti
4. Vrstva 3 fáze 2: serializace pouze změněného atributu na příslušnou doménu mesh elementu
5. Geometry Nodes reevaluace → okamžitá vizuální aktualizace bez změny topologie

Tento update je levnější než přidání/odebrání stěny — neprovádí se detekce cyklů ani fáze 1 sync (topologie mesh se nemění).

## Otvory — GN Mesh Boolean

Otvory (dveře, okna) jsou definovány jako závislé objekty vázané na konkrétní stěnu ve Vrstvě 1. Každý otvor nese pozici na stěně (relativní parametr $t \in [0, 1]$), šířku a výšku. Tvorba otvorů probíhá výhradně ve View vrstvě — Python předá poziční data jako pojmenované atributy a Geometry Nodes uzly díru dynamicky vyříznou.

Architektura addonu reprezentuje stěny jako **hrany base meshe** s pojmenovanými atributy — Curve Trimming by vyžadovalo Blender Curve objekty jako vstup do GN stromu, což je neslučitelné s touto reprezentací. Správnou volbou je proto **GN Mesh Boolean**:

- uzel Mesh Boolean v GN stromu zpracovává celou kolekci cutter objektů (bounding boxy otvorů) jako jeden sloučený vstup — výrazně méně reevaluací než API modifikátory
- Python předá pouze poziční data otvorů (střed, šířka, výška) jako pojmenované atributy na přilehlé hrany Vrstvy 3; GN je čte a sestaví cutter geometrii interně
- pro zamezení artefaktů z coplanárních ploch se cuttery vytvářejí s nepatrným přesahem přes oba lícní povrchy stěny

Python nikdy nemanipuluje s polygony stěny přímo — veškerá geometrie otvorů je generována a aktualizována v GN modifikátoru v reálném čase.

## Vazba otvorů na stěnu

Závislost otvoru na stěně je uložena ve Vrstvě 1 jako atribut hrany `opening_refs` (seznam referencí). Po posunu junctionu nebo změně délky stěny:

- relativní pozice otvoru $t$ zůstává nezměněna → absolutní souřadnice se přepočítá automaticky z nové délky stěny
- orientace otvoru se přepočítá z nového směrového vektoru stěny
- Vrstva 3 fáze 2 serializuje nové poziční atributy → GN reevaluace posune otvor vizuálně