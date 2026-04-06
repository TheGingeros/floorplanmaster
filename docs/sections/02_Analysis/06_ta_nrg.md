# Node Relation Graph pro sémantiku místností

Vrstva 1 (strukturální graf) uchovává topologii stěn a propojovacích bodů — je to čistě geometrická informace. Pro architektonické dotazy (jaký typ má místnost, sousedí tyto dvě místnosti, jaká je celková plocha ložnic) nestačí: stěna je hrana grafu, ale nepovídá nic o prostorech, které odděluje. Vrstva 2 tento sémantický rozměr doplňuje jako duální reprezentace.

## Reprezentace

- **Uzly ($V_r$)** — každý uzel reprezentuje jednu místnost; nese nefyzikální metadata: název, typ místnosti, plocha, obvod, centroid
- **Hrany ($E_r$)** — každá hrana reprezentuje vztah sousednosti dvou místností (sdílejí fyzickou stěnu); hrana může být typizována: `WALL` (plná stěna), `DOOR` (otvor s dveřmi), `WINDOW` (otvor s oknem), `PASSAGE` (průchod)

## Role

- uchovává nefyzikální metadata nezávisle na geometrii
- umožňuje dotazy: *Sousedí obývací pokoj s chodbou?*, *Jaká je celková plocha všech ložnic?*, *Je koupelna přístupná z chodby?*
- centroidy uzlů slouží jako pozice popisků v kótovacím overlayeru (FP7)

## Proč duální graf, ne seznam místností

Alternativou k NRG je prostý seznam místností (pole/slovník) — každá místnost nese svá metadata, vztahy sousedství nejsou explicitně modelovány a jsou dopočítávány ze sdílených hran Vrstvy 1 při každém dotazu.

Nevýhoda prostého seznamu: dotaz *„sousedí A s B?"* vyžaduje průchod Vrstvou 1 a hledání sdílené hrany — O(E) na každý dotaz. Navíc nelze snadno přiřadit metadata ke vztahu (typ otvoru, šířka průchodu) — ta by musela být uložena na hraně Vrstvy 1, kde sémanticky nepatří.

NRG (explicitní hrany sousednosti) tento dotaz redukuje na O(1) vyhledání v adjačenčním seznamu. Typizace hrany (`DOOR`, `WINDOW`, `PASSAGE`) je přirozená — hrana nesou metadata vztahu, uzel nese metadata místnosti. Implementace přes NetworkX umožňuje využít existující grafové algoritmy (BFS pro dostupnost, Dijkstra pro nejkratší trasu) bez vlastní implementace.

## Vazba na Vrstvu 1

Vrstva 2 je vždy přísně odvozená z Vrstvy 1 — nikdy není editována přímo (vyjma uživatelských metadat: název, typ). Každý minimální cyklus ve Vrstvě 1 odpovídá jednomu uzlu Vrstvy 2. Každá sdílená hrana dvou cyklů odpovídá jedné hraně Vrstvy 2. Tato bijekce je udržována automaticky po každé změně topologie Vrstvy 1 (viz [hybridní spojení a strategie detekce](./06_ta_hybrid_connection.md)).

[Zdroje](../../files/00_sources.md#datová-reprezentace-logické-struktury-sítě-místností)