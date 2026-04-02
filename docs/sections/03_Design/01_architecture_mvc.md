# Vzor MVC v Blenderu
Architektura FloorPlanMaster aplikuje návrhový vzor Model-View-Controller (MVC), aby předešla nejčastější chybě při vývoji Blender addonů: neřízenému propletení logiky s přímou úpravou 3D sítě. Tento přístup jasně definuje hranice zodpovědnosti a optimalizuje výkon.

Jako Model fungují všechny tři datové vrstvy – od NetworkX grafů v Pythonu až po serializované pojmenované atributy. Model drží stav půdorysu, ale vůbec netuší, jak se má vykreslit. O zobrazení se stará View – nativní 3D pohled Blenderu a dynamická geometrie z Geometry Nodes, která pasivně a automaticky zrcadlí potvrzený stav Modelu. Spojníkem obou světů je Controller, reprezentovaný modálními operátory (např. nástroj Tužka), který odchytává uživatelské vstupy.

Tok dat je v této architektuře navržen s ohledem na maximální rychlost. Hlavní komunikační kanál vede z Controlleru výhradně do Modelu (zápis potvrzených úprav), odkud se změny přirozeně propisují do View. Existuje zde však jedna kritická, výkonnostní výjimka: dočasný náhled. Během interaktivních akcí – například při pohybu myší před finálním umístěním stěny – Controller komunikuje s View napřímo. Pomocí GPU modulu vykresluje pouze dočasné vodicí čáry, aniž by zatěžoval Model neustálým přepočítáváním topologie. Díky tomuto oddělení je addon vysoce responzivní a jeho datové jádro zůstává plně chráněno.

## Diagram MVC
```text
┌──────────────────────────────────────────────┐
│                    MODEL                     │
│ ──────────────────────────────────────────── │
│ [Zastřešující kontejner: Budova]             │
│  • Stav: active_floor_index                  │
│  └── [Data: Aktivní Podlaží]                 │
│       • Vrstva 1: Strukturální graf patra    │
│       • Vrstva 2: Graf místností patra       │
│       • Vrstva 3: Pojmenované atributy (Bl.) │
└──────────────────────────────────────────────┘
           ↑                    │
           │ (zápis a úprava)   │ (čtení přes GN driver)
           │                    ↓
           │             ┌──────────────────┐
           │             │  Geometry Nodes  │
           │             └──────────────────┘
           │                    ↓
           │             Síť/Geometrie
           │       ┌───────────────────────────┐
           │       │           VIEW            │
           │       │ ───────────────────────── │
           │       │ • Vykreslování pohledu    │
           │       │ • Zobrazení GPU náhledů   │
           │       │ • Vizualizace uživatele   │
           │       └───────────────────────────┘
           │                    ↑
           │                    │ (dočasný GPU náhled - nepotvrzená topologie)
┌──────────┴────────────────────┴──────────┐
│                CONTROLLER                │
│ ──────────────────────────────────────── │
│ • Modální operátory (Tužka, Finalizace)  │
│ • Obslužné programy událostí (myš, kl.)  │
│ • Logika stavového automatu              │
└──────────────────────────────────────────┘
```
