# Tok dat mezi vrstvami
Komunikace mezi vrstvami je striktně jednosměrná a hierarchická: změny vždy iniciuje Vrstva 1, která automaticky spouští reakci Vrstvy 2, a teprve po ustálení obou grafů se data serializují do Vrstvy 3. Zpětný tok (Vrstva 3 → Vrstva 2 nebo Vrstva 1) neexistuje — Blender mesh je vždy jen odrazem aktuálního stavu grafů, nikoliv jejich výchozím bodem.

## Přidání hrany (nová stěna)

```mermaid
flowchart TD
    V1["**Vrstva 1**<br/>Přidán junction nebo použit existující<br/>Přidána stěna s atributy (thickness, height, material)<br/>Detekce minimálních cyklů"]:::v1
    V2["**Vrstva 2**<br/>Nový cyklus -> nová místnost s unikátním ID<br/>Výpočet metriky: area, perimeter<br/>Sdílená hrana dvou cyklů -> nové sousedství"]:::v2
    V3F1["**Vrstva 3 — fáze 1: topologie**<br/>Přidán vrchol pro každý junction<br/>Přidána hrana mezi vrcholy<br/>Přidána plocha pro každý uzavřený cyklus"]:::v3
    V3F2["**Vrstva 3 — fáze 2: atributy**<br/>Zápis ID a parametrů na vrcholy, hrany a plochy<br/>Geometry Nodes reevaluace"]:::v3

    V1 --> V2 --> V3F1 --> V3F2

    classDef v1 stroke:#4a90d9,stroke-width:2px
    classDef v2 stroke:#9b4ad9,stroke-width:2px
    classDef v3 stroke:#4ad97c,stroke-width:2px
    linkStyle default stroke-width:2px
```

## Odebrání hrany (smazání stěny)

```mermaid
flowchart TD
    V1["**Vrstva 1**<br/>Odebrána stěny z grafu<br/>Detekce: které cykly zanikly nebo se sloučily"]:::v1
    V2["**Vrstva 2**<br/>Zánik cyklu -> odebrání místnosti<br/>Sloučení cyklů -> node fusion (ID zachovaného uzlu přetrvá)<br/>Aktualizace sousedství a metrik"]:::v2
    V3F1["**Vrstva 3 — fáze 1: topologie**<br/>Odebrání hrany a izolovaných vrcholů<br/>Odebrání nebo sloučení dotčených ploch"]:::v3
    V3F2["**Vrstva 3 — fáze 2: atributy**<br/>Přepsání atributů dle Vrstvy 2<br/>Geometry Nodes reevaluace"]:::v3

    V1 --> V2 --> V3F1 --> V3F2

    classDef v1 stroke:#4a90d9,stroke-width:2px
    classDef v2 stroke:#9b4ad9,stroke-width:2px
    classDef v3 stroke:#4ad97c,stroke-width:2px
    linkStyle default stroke-width:2px
```

## Změna atributu (parametrická úprava)

```mermaid
flowchart TD
    V12["**Vrstva 1 nebo Vrstva 2**<br/>Aktualizace hodnoty atributu hrany nebo uzlu<br/>Pokud ovlivní metriku -> Vrstva 2 přepočítá area, perimeter<br/>Topologie grafu se nemění"]:::v12
    V3["**Vrstva 3**<br/>Serializace změněného atributu na příslušnou doménu<br/>Geometry Nodes reevaluace"]:::v3

    V12 --> V3

    classDef v12 stroke:#4a90d9,stroke-width:2px
    classDef v3  stroke:#4ad97c,stroke-width:2px
    linkStyle default stroke-width:2px
```

- nejlevnější operace v systému — nemění strukturu grafů, pouze číselné hodnoty
- ID místností a stěn zůstávají nezměněna, úprava je vždy nedestruktivní
