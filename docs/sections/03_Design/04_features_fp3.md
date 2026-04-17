# FP3 — Detekce místností a metadata
Technická analýza ([lazy vs. eager strategie detekce místností](../../02_Analysis/06_ta_hybrid_connection.md#strategie-detekce-místností-lazy-vs-eager)) zvolila **lazy detekci** — místnosti (Vrstva 2) vznikají výhradně při detekci uzavřeného cyklu ve Vrstvě 1. Tato sekce popisuje jak je detekční algoritmus aplikován, správu metadat a perzistenci dat.

## Detekce cyklů → Vrstva 2

Detekce je spuštěna automaticky po každé změně topologie Vrstvy 1 (přidání nebo odebrání hrany). Algoritmus:

1. NetworkX detekuje všechny minimální cykly v planárním grafu Vrstvy 1
2. Každý nový cyklus (který dosud nemá odpovídající místnost ve Vrstvě 2) → vytvoření nového uzlu `Room` s perzistentním UUID → přiřazení celočíselného `room_id`
3. Zánik cyklu → odebrání příslušné místnosti z Vrstvy 2
4. Sloučení dvou cyklů (odebrání dělící stěny) → node fusion: jeden uzel místnosti přežije, metadata a ID zachovaného uzlu přetrvají
5. Každá hrana sdílená dvěma cykly → vytvoření nebo aktualizace hrany `Adjacency` ve Vrstvě 2

Výsledkem je, že Vrstva 2 je vždy deterministicky odvozena z aktuálního stavu Vrstvy 1 — bez manuálního vstupu uživatele.

## Prostorová data a metriky *(must-have)*

Pro každou místnost ve Vrstvě 2 systém udržuje a aktualizuje:

- **Plocha** (`room_area`) — vypočtena z souřadnic uzavřeného cyklu ve Vrstvě 1 pomocí Gaussovy vzorce pro polygon; přepočítá se při každé změně geometrie junctionů nebo délek stěn
- **Obvod** (`room_perimeter`) — součet délek všech ohraničujících stěn; aktualizuje se spolu s plochou
- **Centroid** — průměr souřadnic vrcholů cyklu; používá FP7 pro umístění kótovacího textu
- **Název** — metadata uložená v uzlu Vrstvy 2; přetrvávají při změně geometrie (perzistentní ID)

Metriky jsou serializovány do Vrstvy 3 jako pojmenované atributy na plochy (`room_area`, `room_perimeter`, `room_id`) a čtou je Geometry Nodes pro vizualizaci.

## Perzistence dat *(must-have)*

Technická analýza ([přístupy k perzistenci grafových dat](../../02_Analysis/06_ta_persistence_approaches.md)) porovnala tři přístupy — JSON v Custom Property, Pickle a rekonstrukci z meshe — a identifikovala rekonstrukci z meshe jako nejvhodnější pro architekturu s named attributes.

Zvolený přístup je **rekonstrukce z Vrstvy 3**. Base mesh, který Blender ukládá automaticky, již obsahuje veškerou topologickou informaci v named attributes (kapitola 3.3):

- **Vrchol + `junction_id`** → junction Vrstvy 1
- **Hrana + `wall_id`, `wall_thickness`, `wall_height`, `wall_material_id`** → stěna Vrstvy 1
- **Plocha + `room_id`** → opětovné spuštění detekce cyklů serializuje Vrstvu 2

Jediná data, která v meshi nejsou, je uživatelský název místnosti (`room_name`). Toto pole se ukládá jako Blender Custom Property na objekt, jako slovník indexovaný přes `room_id`:

```
object["room_metadata"] = {42: {"name": "Obývací pokoj"}, ...}
```

I pokud tato metadata chybí (poškozený soubor), systém mesh načte a grafy serializuje správně — místnosti pouze ztratí vlastní jména. Blender Undo/Redo ukládá snímky mesh stavu, takže rekonstrukce po Undo je stejný mechanismus jako rekonstrukce po načtení souboru.