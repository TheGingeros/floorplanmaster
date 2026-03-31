# Vztah mezi vrstvou 1 a 2
Tato sekce definuje převodník mezi nízkoúrovňovou topologií a architektonickou sémantikou. Vrstva 1 a Vrstva 2 neexistují ve vakuu; jsou úzce provázány. Tento vztah je přísně asymetrický: Vrstva 1 (geometrie) diktuje tvar a existenci Vrstvy 2 (místností). Zatímco tvar a hranice se mohou neustále měnit, Vrstva 2 si drží svá perzistentní metadata (ID, název, materiály) nezávisle na těchto geometrických úpravách.

## Mapování
Následující diagram znázorňuje princip takzvaného duálního grafu. Ukazuje, jak se strukturní prvky z první vrstvy logicky překládají do sémantických prvků vrstvy druhé.

```text
┌─────────────────────────┐                 ┌─────────────────────────┐
│ VRSTVA 1 (Strukturální) │                 │ VRSTVA 2 (Sémantická)   │
├─────────────────────────┤                 ├─────────────────────────┤
│                         │                 │                         │
│ Uzavřený cyklus stěn    ├───── tvoří ───▶│ UZEL: Místnost          │
│ (Geometrická hranice)   │                 │ (Nese metadata a ID)    │
│                         │                 │                         │
│ Sdílená stěna (Hrana)   ├──── definuje ─▶│ HRANA: Sousedství       │
│ (Fyzický oddělovač)     │                 │ (Dveře, okna, průchody) │
│                         │                 │                         │
└─────────────────────────┘                 └─────────────────────────┘
```

## Pravidla synchronizace
Aby systém zůstal nedestruktivní a konzistentní, podléhá datový tok mezi vrstvami přísným pravidlům. Synchronizace probíhá vždy automaticky na pozadí a je striktně jednosměrná (topologie ovlivňuje sémantiku, nikdy ne naopak).

1. **Detekce cyklu** (automatické zakládání a mazání)
   - Když je stěna přidána do vrstvy 1 → NetworkX detekuje nové cykly.
   - Nové cykly → Vytvoří nové uzly místností ve vrstvě 2 a přiřadí jim nová perzistentní ID.
   - Cyklus odstraněn (např. zbouráním stěny) → Odstraní odpovídající místnost ve vrstvě 2 (po případném varování uživateli o ztrátě sémantických dat).

2. **Propagace vlastností** (jednosměrný přenos parametrů)
   - Tloušťka stěny (Vrstva 1) → Diktuje fyzický odstup podlahy/stropu ve Vrstvě 2 a následně slouží Geometry Nodes pro 3D šířku.
   - Výška stěny (Vrstva 1) → Určuje maximální možnou výšku místnosti.
   - Materiál stěny (Vrstva 1) → Slouží jako výchozí (default) materiál pro vnitřní ohraničení místnosti ve Vrstvě 2.

3. **Aktualizace geometrie** (udržení perzistence)
   - Stěna je přesunuta (Vrstva 1) → Tvar cyklu se změní → Plocha, střed (centroid) a obvod místnosti ve Vrstvě 2 se automaticky přepočítají.
   - Propojovací bod je přidán/odstraněn → Topologie stěn se změní → Místnosti se mohou rozdělit nebo sloučit.
   - **Kritické pravidlo:** I když uživatel změní tvar místnosti k nepoznání, její ID a sémantická data (název, barva podlahy) přetrvávají po celou dobu, dokud nedojde k úplnému rozpojení cyklu.