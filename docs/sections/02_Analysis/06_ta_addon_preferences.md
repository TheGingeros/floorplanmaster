# Persistence globálních nastavení addonu

Addon spravuje dvě kategorie nastavení: **projektová data** (hodnoty přímě ovlivňující geometrii konkrétního půdorysu — výchozí tloušťka stěny, výška, hustota mřížky, systém jednotek) a **nastavení chování addonu** (výkon, cesty k souborům, UI preference). Blender nabízí pro každou kategorii jiný mechanismus:

| Mechanismus | Kde je uložen | Rozsah platnosti |
| :--- | :--- | :--- |
| `bpy.types.AddonPreferences` | `userpref.blend` (Blender user data) | Globální pro celý Blender, přetrvává napříč projekty |
| `bpy.types.PropertyGroup` na `Scene` | aktualní `.blend` soubor | Per-projekt; každá scéna má vlastní hodnoty |
| `bpy.types.PropertyGroup` na `Object`/`Mesh` | aktualní `.blend` soubor | Per-objekt; viz [Vazby dat, Scéna, Objekt, Mesh](./06_ta_data_scene_objekt_mesh.md) |

## Jak to řeší existující addon

**Archimesh** registruje `ArchimeshProperties` PropertyGroup přímo na `bpy.types.Scene`. Všechna nastavení — výška místnosti, tloušťka stěny, systém jednotek — jsou per-scéna. `AddonPreferences` Archimesh nepouívá vůbec. Výchozí hodnoty jsou napevno zakódovány v definici PropertyGroup (`default=` parametr), nikoli v uživatelsky přizpůsobitelné preferenci.

**Archipack** má `ArchipackPreferences(bpy.types.AddonPreferences)`, ale ukládá do ní výhradně: cestu k externím knihovnám assetů, nastavení throttlingu (výkonnostní limit) a přepínače viditelnosti panelů. Výchozí rozměry architektonických prvků v `AddonPreferences` nejsou — každý objekt nese vlastní PropertyGroup s parametry s napevno zakódovanými výchozími hodnotami.

## Jak to řeší CAD nástroje

AutoCAD rozlišuje **systémové proměnné** (globální pro aplikaci, např. výchozí typ čáry, UNITS default) a **výkresové proměnné** (per-soubor, hodnota UNITS v právě otevřeném výkrese). Projekt-level hodnota vždy přebíjí systémový default. Toto dvouúrovňové řešení AutoCAD opravňuje tím, že uživatel pracuje na různých typech projektů (metrické i imperiální) zároveň, takže globální default je jen startovacím bodem.

## Porovnání přístupů pro FloorPlanMaster

| Přístup | Výhoda | Nevýhoda |
| :--- | :--- | :--- |
| **Scene PropertyGroup** (Archimesh vzor) | Projektová data jsou součástí `.blend`; různé projekty mají různé defaults; conceptuálně čisté; implementačně jednodušší | Uživatel musí nastavit preference znovu pro každý nový projekt |
| **AddonPreferences jako výchozí hodnoty** | Uživatel nastaví jednou a platí pro nové projekty | Mísí "chování addonu" s "hodnotami projektu"; `userpref.blend` nepatří do verzovacího systému — preference se mohou lišit mezi pracovními stanicemi |
| **Hybrid** (AddonPreferences → Scene PropertyGroup) | Nabízí obojí: globální uživatelský default + per-projekt přepsání | Vyšší implementační složitost; nutno explicitně zkopírovat hodnoty při vytváření nového půdorysu |

## Závěr

Oba hlavní Blender architektonické addony (Archimesh, Archipack) se vyhýbají ukládání hodnot projektových parametrů do `AddonPreferences`. Tento mechanismus rezervují pro chování addonu (cesty, výkon, UI), nikoli pro architektonická data. Dvouúrovňový přístup AutoCADu je opodstatněný jeho multi-dokumentovým pracovním modelem, který Blender (single-scene model) nesdílí.

Pro FloorPlanMaster je optimálním řešením **Scene PropertyGroup** se zapečenými výchozími hodnotami v definici třídy:
- projektové hodnoty jsou součástí `.blend` souboru → přenositelné a verzovatelné s projektem
- různé projekty mohou mít různé defaults, aniž by jeden přepsal druhý
- implementace je přímočará a konzistentní s konvencemi Blenderu

`AddonPreferences` se použijí pouze pokud bude v budoucnu potřeba uchovávat nastavení nesouvisející s konkrétním projektem (výkonnostní limity, cesta k exportní šabloně apod.).

[Zdroje](../../files/00_sources.md#ukládání-dat-a-správa-metadat)
