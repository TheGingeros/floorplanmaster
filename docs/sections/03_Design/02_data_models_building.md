# Hierarchie budovy (Zastřešující modely)
Aby bylo možné v addonu navrhovat vícepodlažní objekty, aniž by došlo ke zhroucení planárních algoritmů (křížení stěn různých pater v jednom 2D prostoru), je celá datová struktura zabalena do ochranné hierarchie. Tato úroveň nedefinuje transformační vrstvy, ale slouží jako organizační kontejner. Zajišťuje, že matematické jádro každého podlaží běží ve svém vlastním izolovaném prostoru a data se vzájemně neovlivňují.

## Model budovy
Tento model funguje jako hlavní kořenový objekt (root) celého projektu půdorysu. Jeho nejdůležitější architektonickou rolí, kromě uchovávání globálních parametrů, je správa seznamu pater a udržování informace o tom, ve kterém patře uživatel aktuálně pracuje (`active_floor_index`). Všechny uživatelské vstupy odchycené Controllerem (např. kliknutí nástrojem Tužka) jsou vždy směrovány výhradně do datového jádra tohoto aktivního podlaží.
```python
Building:
  - id: UUID
  - name: str                    # Název projektu
  - floors: list[Floor]          # Seznam podlaží (seřazený odspodu nahoru)
  - active_floor_index: int      # Index patra, které uživatel aktuálně upravuje
  - project_settings: dict       # Globální nastavení (např. výchozí výška stěn)
```

## Model podlaží
Model podlaží představuje jeden zcela izolovaný 2D vesmír. Zásadní je, že každá instance podlaží si nese svou vlastní nezávislou Vrstvu 1 (`structural_graph`) a Vrstvu 2 (`room_graph`). Díky tomu, že je parametr výšky umístění v prostoru (`elevation`) definován zastřešujícím způsobem až na úrovni celého podlaží, mohou samotné uzly uvnitř strukturálního grafu zůstat striktně dvoudimenzionální (x, y), což je nutností pro bezchybné fungování NetworkX analýz. Tento model také řídí stav zobrazení (`is_visible`), což umožňuje snadné skrývání pater v Blender viewportu.
```python
Floor:
  - id: UUID
  - name: str                    # např. "Přízemí", "1. Patro"
  - elevation: float             # Z-výška, na které podlaží začíná (např. 0.0m, 3.2m)
  - is_visible: bool             # Stav zobrazení v UI/Viewportu
  
  # Datové jádro podlaží (izolované instance)
  - structural_graph: StructuralGraph  # Vlastní Vrstva 1
  - room_graph: RoomGraph              # Vlastní Vrstva 2
```