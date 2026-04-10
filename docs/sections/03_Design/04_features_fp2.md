# FP2 — Parametrické objekty a otvory
Analýza (FP2) definovala požadavek na dynamickou, nedestruktivní reprezentaci stěn a otvorů — model řízený parametry, ne statická polygonová síť. Návrhové rozhodnutí (kapitola 3.2) zvolilo Geometry Nodes jako výpočetní backend a pojmenované atributy jako datový bridge. Tato sekce popisuje, jak se parametrické chování realizuje v interakci Vrstvy 1, Vrstvy 3 a View.

## Parametry stěny a update mechanismus *(must-have)*

Každá stěna ve Vrstvě 1 nese atributy `thickness`, `height` a `material_id`. Změna kteréhokoli parametru přes UI panel nebo 3D manipulátor (FP6) spustí přesně definovaný update cyklus:

1. Validace nové hodnoty vůči povoleným rozsahům (viz datový model, kapitola 3.3)
2. Zápis aktualizované hodnoty do Vrstvy 1
3. Pokud změna ovlivňuje metriku místnosti (`height` → maximální výška) → Vrstva 2 přepočítá dotčené místnosti
4. Vrstva 3 fáze 2: serializace pouze změněného atributu na příslušnou doménu mesh elementu
5. Geometry Nodes reevaluace → okamžitá vizuální aktualizace bez změny topologie

Tento update je levnější než přidání/odebrání stěny — neprovádí se detekce cyklů ani fáze 1 sync (topologie mesh se nemění).

## Otvory — GN Mesh Boolean *(must-have)*

Otvory (dveře, okna) jsou definovány jako závislé objekty vázané na konkrétní stěnu ve Vrstvě 1. Každý otvor nese pozici na stěně (relativní parametr $t \in [0, 1]$), šířku a výšku. Tvorba otvorů probíhá výhradně ve View vrstvě — Python předá poziční data jako pojmenované atributy a Geometry Nodes uzly díru dynamicky vyříznou.

Architektura addonu reprezentuje stěny jako **hrany base meshe** s pojmenovanými atributy:

- uzel Mesh Boolean v GN stromu zpracovává celou kolekci cutter objektů (bounding boxy otvorů) jako jeden sloučený vstup — výrazně méně reevaluací než API modifikátory
- Python předá pouze poziční data otvorů (střed, šířka, výška) jako pojmenované atributy na přilehlé hrany Vrstvy 3; GN je čte a sestaví cutter geometrii interně
- pro zamezení artefaktů z coplanárních ploch se cuttery vytvářejí s nepatrným přesahem přes oba lícní povrchy stěny

Python nikdy nemanipuluje s polygony stěny přímo — veškerá geometrie otvorů je generována a aktualizována v GN modifikátoru v reálném čase.

## Vložení pravoúhlé místnosti z parametrů *(must-have)*

Vedle Pencil Toolu (FP1) existuje druhý způsob vložení místnosti: uživatel zadá rozměry přímo v N-panelu a addon automaticky vytvoří pravoúhlou místnost.
Vstupní parametry (zadané v N-panelu, sekce Nástroje):
- **šířka** a **hloubka** místnosti (m) — nebo alternativně **plocha** + **poměr stran**, ze kterých addon šířku a hloubku dopočítá
- **výška stěn** (přednaplněna výchozí hodnotou ze Scene PropertyGroup)
- **tloušťka stěn** (přednaplněna výchozí hodnotou)

Po potvrzení se pravoúhlá místnost vloží se středem v poloze 3D kurzoru Blenderu. Uživatel ručně nastaví pozici 3D kurzoru před vložením (standardní Blender konvence: `Shift+RMB`).

**MVP — vložení vždy jako samostatná izolovaná místnost.** Addon zavolá sekvenci `L1.add_junction()` a `L1.add_wall()` pro čtyři stěny; vzniklé junctions nikdy nesdílejí vrcholy s existující sítí, takže ve Vrstvě 2 nevznikají žádné nové sousednosti. Detekce cyklů spustí Vrstvu 2 a synchronizační cyklus Vrstvu 3. Výsledná místnost je datově nerozeznatelná od místnosti nakreslené tužkou a všechny navazující operace (FP5 kontextová nabídka, FP6 gizmos, FP7 kóty) na ni fungují identicky.

**Rozšíření (mimo MVP):** výběr existující místnosti, světové strany napojení (sever / jih / východ / západ) a způsobu sdílení stěny; systém by pak sloučil příslušné junctions a společná hrana by se stala sdílenou hranou dvou cyklů ve Vrstvě 2 — viz [3.1 Rozšiřitelnost](./01_mvp_scope.md).

Poznámka: pro MVP jsou podporovány pouze pravoúhlé místnosti. Jiné tvary (L, T, polygonální) jsou záměrně vyloučeny — viz [3.1 Rozšiřitelnost](./01_mvp_scope.md).

## Vazba otvorů na stěnu *(must-have)*

Závislost otvoru na stěně je uložena ve Vrstvě 1 jako atribut hrany `opening_refs` (seznam referencí). Po posunu junctionu nebo změně délky stěny:

- relativní pozice otvoru $t$ zůstává nezměněna → absolutní souřadnice se přepočítá automaticky z nové délky stěny
- orientace otvoru se přepočítá z nového směrového vektoru stěny
- Vrstva 3 fáze 2 serializuje nové poziční atributy → GN reevaluace posune otvor vizuálně