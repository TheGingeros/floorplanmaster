# Tok dat mezi vrstvami
Komunikace mezi vrstvami je striktně jednosměrná a hierarchická: změny vždy iniciuje Vrstva 1, která automaticky spouští reakci Vrstvy 2, a teprve po ustálení obou grafů se data serializují do Vrstvy 3. Zpětný tok (Vrstva 3 → Vrstva 2 nebo Vrstva 1) neexistuje — Blender mesh je vždy jen odrazem aktuálního stavu grafů, nikdy zdrojem pravdy.

## Přidání hrany (nová stěna)

```
Vrstva 1
  → přidán uzel (junction) nebo použit existující
  → přidána hrana (stěna) s atributy: thickness, height, material
  → spuštění detekce minimálních cyklů
        ↓
Vrstva 2
  → každý nový cyklus → nový uzel místnosti s unikátním ID
  → výpočet metriky: area, perimeter
  → každá sdílená hrana dvou cyklů → nová hrana sousedství
        ↓
Vrstva 3 — fáze 1: aktualizace topologie base mesh
  → přidání/aktualizace vrcholu pro každý junction
  → přidání hrany mezi příslušnými vrcholy
  → přidání plochy pro každý nový uzavřený cyklus
Vrstva 3 — fáze 2: serializace atributů
  → zápis identifikátorů a parametrů na vrcholy, hrany a plochy
  → Geometry Nodes reevaluace → přegenerování 3D geometrie
```

## Odebrání hrany (smazání stěny)

```
Vrstva 1
  → odebrána hrana (stěna) z grafu
  → spuštění detekce cyklů — které cykly zanikly nebo se sloučily
        ↓
Vrstva 2
  → zánik cyklu → odebrání uzlu místnosti (místnost zmizí)
  → sloučení dvou cyklů → node fusion: jeden uzel místnosti zůstane,
    druhý se odstraní, metadata i ID zachovaného uzlu přetrvají
  → aktualizace sousedství a metrik dotčených místností
        ↓
Vrstva 3 — fáze 1: aktualizace topologie base mesh
  → odebrání hrany a případných osiřelých vrcholů
  → odebrání nebo sloučení dotčených ploch
Vrstva 3 — fáze 2: serializace atributů
  → přepsání atributů na plochy podle nového stavu Vrstvy 2
  → Geometry Nodes reevaluace
```

## Změna atributu (parametrická úprava)

```
Vrstva 1 nebo Vrstva 2
  → aktualizace hodnoty atributu hrany nebo uzlu
    (např. wall_thickness, room_height, material)
  → pokud změna ovlivní metrii → Vrstva 2 přepočítá area, perimeter
  (topologie grafu se nemění — žádná detekce cyklů)
        ↓
Vrstva 3
  → serializace pouze změněného atributu na příslušnou doménu
  → Geometry Nodes reevaluace → vizuální aktualizace bez změny topologie mesh
```

- nejlevnější operace v systému — nemění strukturu grafů, pouze číselné hodnoty
- ID místností a stěn zůstávají nezměněna, úprava je vždy nedestruktivní
