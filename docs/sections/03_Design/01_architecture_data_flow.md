# Tok dat mezi vrstvami
Komunikace mezi vrstvami je striktně jednosměrná a hierarchická: změny vždy iniciuje Vrstva 1, která automaticky spouští reakci Vrstvy 2, a teprve po ustálení obou grafů se data serializují do Vrstvy 3. Zpětný tok (Vrstva 3 → Vrstva 2 nebo Vrstva 1) neexistuje — Blender mesh je vždy jen odrazem aktuálního stavu grafů, nikdy zdrojem pravdy.

## Přidání hrany (nová stěna)

```mermaid
flowchart TD
    V1["**Vrstva 1**<br/>Přidán junction nebo použit existující<br/>Přidána stěna s atributy (thickness, height, material)<br/>Detekce minimálních cyklů"]
    V2["**Vrstva 2**<br/>Nový cyklus -> nová místnost s unikátním ID<br/>Výpočet metriky: area, perimeter<br/>Sdílená hrana dvou cyklů -> nové sousedství"]
    V3F1["**Vrstva 3 — fáze 1: topologie**<br/>Přidán vrchol pro každý junction<br/>Přidána hrana mezi vrcholy<br/>Přidána plocha pro každý uzavřený cyklus"]
    V3F2["**Vrstva 3 — fáze 2: atributy**<br/>Zápis ID a parametrů na vrcholy, hrany a plochy<br/>Geometry Nodes reevaluace"]

    V1 --> V2 --> V3F1 --> V3F2
```

## Odebrání hrany (smazání stěny)

```mermaid
flowchart TD
    V1["**Vrstva 1**<br/>Odebrána stěna z grafu<br/>Detekce: které cykly zanikly nebo se sloučily"]
    V2["**Vrstva 2**<br/>Zánik cyklu -> odebrání místnosti<br/>Sloučení cyklů -> node fusion (ID zachovaného uzlu přetrvá)<br/>Aktualizace sousedství a metrik"]
    V3F1["**Vrstva 3 — fáze 1: topologie**<br/>Odebrání hrany a osiřelých vrcholů<br/>Odebrání nebo sloučení dotčených ploch"]
    V3F2["**Vrstva 3 — fáze 2: atributy**<br/>Přepsání atributů dle Vrstvy 2<br/>Geometry Nodes reevaluace"]

    V1 --> V2 --> V3F1 --> V3F2
```

## Změna atributu (parametrická úprava)

```mermaid
flowchart TD
    V12["**Vrstva 1 nebo Vrstva 2**<br/>Aktualizace hodnoty atributu hrany nebo uzlu<br/>Pokud ovlivní metriku -> Vrstva 2 přepočítá area, perimeter<br/>Topologie grafu se nemění"]
    V3["**Vrstva 3**<br/>Serializace změněného atributu na příslušnou doménu<br/>Geometry Nodes reevaluace"]

    V12 --> V3
```

- nejlevnější operace v systému — nemění strukturu grafů, pouze číselné hodnoty
- ID místností a stěn zůstávají nezměněna, úprava je vždy nedestruktivní
