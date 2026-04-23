# 4.1 Addon pro Blender

Blender svou rozšiřitelnost staví na systému addonů — Python modulů, které Blender načítá a spravuje ve svém vestavěném interpretu. Každý addon poskytuje dvojici funkcí `register` a `unregister`, které Blender volá při aktivaci a deaktivaci; jejich úkolem je zaevidovat u Blenderu veškeré operátory, panely, vlastnosti a handlery, jež addon přidává. Mimo tyto dvě funkce popisuje addon sám sebe v metadatovém slovníku — uvádí název, verzi, minimální podporovanou verzi Blenderu a kategorii, pod níž se zobrazí ve správci addonů.

FloorPlanMaster je strukturován jako Python balíček. Kořenový soubor `__init__.py` plní roli vstupního bodu a orchestrátora registrace; jednotlivé podsložky (`core`, `operators`, `ui`, `geometry`, `utils`) tvoří samostatné submoduly. Tato struktura přímo odpovídá třívrstvé architektuře popsané v návrhu (3.2) — každá složka zastupuje jasně ohraničenou vrstvu zodpovědnosti.

## Izolace závislosti na Blender API

Klíčovým implementačním rozhodnutím bylo striktní oddělení kódu závislého na Blender API od čistého Pythonu. Vrstvy 1 a 2 (strukturální graf, graf místností) a veškeré utility nijak Blender API nevyžadují. Díky tomu lze tyto moduly importovat a testovat standardním interpretem Pythonu zcela mimo Blender, což je nezbytným předpokladem jednotkového testování pomocí pytest.

Aby byl addon stále funkční i při spuštění uvnitř Blenderu, při startu se podmíněně ověří dostupnost Blender API: pokud importování selže (prostředí bez Blenderu, například pytest spouštěný z terminálu), registrace všech tříd závislých na Blender API se přeskočí. V prostředí Blenderu proběhne registrace standardně. Tímto způsobem sdílí jeden vývojový projekt vývoj v IDE s testováním i integraci do Blenderu bez jakékoliv duplikace kódu.

## Závislost na NetworkX

NetworkX je knihovna třetí strany, kterou Blender ve svém Python prostředí nenabízí. Pro vývoj se instaluje přes pip ze souboru `requirements-dev.txt`. Pro distribuci addonu jako Blender Extension (systém zavedený v Blenderu 4.2) je knihovna přibalena jako `.whl` soubor odkazovaný v manifestu `blender_manifest.toml`. Soubory `.whl` jsou zip-kompatibilní archivy, z nichž Python umí importovat moduly přímo — není tedy třeba je rozbalovat. Při startu addonu proto kořenový vstupní bod přidá složku `wheels/` do vyhledávací cesty Pythonu — NetworkX se stane dostupným bez zásahu uživatele.

## Persistence nastavení a stavový model

Projektová nastavení addonu — výchozí tloušťka a výška stěny — jsou uchována ve vlastnostech (PropertyGroup) registrovaných přímo na Blender scéně. Tato volba zajišťuje, že nastavení jsou součástí `.blend` souboru a různé projekty mají na sobě nezávislé hodnoty, v souladu s konvencemi nástrojů Archimesh a Archipack. Globální nastavení chování addonu (výkon, cesty k šablonám) jsou záměrně rezervovány pro budoucí rozšíření a neovlivňují architektonická data projektu.

Za běhu udržuje addon v paměti sdílenou cache, která pro každý Blender objekt půdorysu uchovává pracovní kopii strukturálního grafu, grafu místností a mapovače identifikátorů. Autoritativním zdrojem dat pro účely uložení a Undo/Redo je vždy Blender mesh s pojmenovanými atributy. Každý operátor proto na svém začátku tuto cache obnoví rekonstrukcí grafů z aktuálního stavu meshe — garantuje se tím, že operace zrušená přes Undo se při opakovaném spuštění promítne do konzistentního stavu grafů.
