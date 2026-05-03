# 4.6 Současná omezení implementace

Implementace addonu pokrývá rozsah definovaný v návrhu jako MVP. Řada funkčních oblastí zůstala záměrně mimo tento rozsah — buď z důvodu prioritizace základní kreslicí a editační pipeline, nebo proto, že jejich správná realizace vyžaduje koordinaci více vrstev architektury a přidání nad rámec MVP by ohrozilo stabilitu jádra. Tato kapitola tyto oblasti shrnuje jako výchozí bod pro navazující vývoj. Kde to je relevantní, je uvedeno, které části architektury jsou pro danou funkci již připraveny a co konkrétně zbývá doimplementovat.

## Transformace FloorPlan objektu

Implementace předpokládá, že FloorPlan objekt leží v počátku souřadnicového systému světa s identitní rotací a jednotkovým měřítkem. Souřadnice vrcholů v Vrstvě 1 se zapisují přímo jako lokální souřadnice Blender objektu bez aplikace `matrix_world`. Pokud uživatel přesune objekt klávesou G nebo jej otočí klávesou R, Blender posune nebo otočí vizuální reprezentaci objektu ve světě, ale při příští synchronizaci Vrstvy 3 jsou vrcholy meshe přepsány z L1 souřadnic, které transformaci neznají — geometrie se vizuálně vrátí do původní lokální polohy. Stejné chování nastane při použití `S` pro změnu měřítka a při příkazu *Apply Transform* (Ctrl+A), který sice zapíše transformaci do lokálního meshe, ale L1 souřadnice zůstanou neaktualizovány, čímž dojde k trvalému desyncu.

Architektura na tuto funkci připravena je: Vrstva 1 ukládá souřadnice jako čistá Python čísla bez vazby na Blender prostor, takže přidání transformace spočívá v jedné systematické změně v `sync.py` — při zápisu vrcholů do bmesh se každá L1 souřadnice transformuje inverzí `obj.matrix_world`. Pohyb junctions v operátorech (FP1 tužka, FP2 endpoint edit) pak musí naopak transformovat souřadnice myši z world space do lokálního prostoru. Žádná strukturální změna datového modelu není potřeba.

## Duplikování FloorPlan objektu

Příkaz Shift+D vytvoří nový Blender objekt se zkopírovanými custom properties včetně serializovaného JSON grafu. Po aktualizaci depsgraphu addon detekuje nový objekt a rekonstruuje pro něj nezávislé Python grafy. Tím však přežijí identické UUIDs pro všechny junctions, stěny, otvory a místnosti — v `_graph_store` existují dva nezávislé grafy se shodným UUID prostorem, což může způsobit neočekávané chování při operacích, které se odvolávají na UUID napříč objekty. Navíc Blender do explicitního unlinkování sdílí mezi oběma objekty datový blok meshe: synchronizace jednoho objektu přepíše mesh, který vidí oba.

Podpora duplikování vyžaduje dvě doimplementace: (a) generování nových UUID při rekonstrukci grafu z kopírovaného JSON (identifikovatelné porovnáním existujícího klíče `_graph_store` se jménem nového objektu) a (b) vynucené odlinkování datového bloku meshe ihned po detekci duplikátu, analogicky příkazu *Make Single User*.

## Přejmenování FloorPlan objektu

`_graph_store` je slovník klíčovaný řetězcovým jménem objektu a `_mode_object_name` je rovněž prostý řetězec. Přejmenování objektu (F2) změní `obj.name` v Blenderu, ale addon nemá registrovaný handler pro událost přejmenování. Výsledkem je, že po přejmenování `_graph_store` stále obsahuje grafy pod starým klíčem, žádný lookup je nenajde a sémantický mód se tiše přeruší.

Oprava je lokalizovaná: buď přejít na klíčování podle `obj.data.name` nebo `id(obj)` (stabilnějšího identifikátoru), nebo registrovat `bpy.app.handlers.depsgraph_update_post` handler, který detekuje rozdíl mezi uloženým jménem v `_graph_store` a aktuálním `obj.name` a přeindexuje příslušný záznam.

## Paralelní práce s více FloorPlan objekty

`_mode_object_name` je jednoduché modulo-level stringové pole — v sémantickém módu může být nejvýše jeden FloorPlan objekt najednou. Výběrový stav `SelectionState` rovněž uchovává jediné `object_name`. Tato vlastnost je záměrná: v rámci MVP priority bylo zvoleno jednoduché a robustní řešení pro jednoobjektový scénář. Addon ale v ostatních ohledech s existencí více FloorPlan objektů ve scéně počítá — `_graph_store` udržuje grafy pro všechny z nich a pasivní overlay vrstva `wall_opening_highlight.py` kreslí stěny a otvory každého viditelného FloorPlan objektu bez ohledu na to, který je aktivní.

Rozšíření na plnohodnotnou podporu více objektů by vyžadovalo přepracování `_mode_object_name` a `SelectionState` z jednoduché hodnoty na slovník nebo sadu, úpravu dotazů `find_floorplan_obj(context)` a nastavení políčky přepínání aktivního objektu v UI. Datový model ani vrstvy 1–3 žádnou úpravu nepotřebují.


## Persistence stavu módu a výběru

Po načtení souboru je sémantický mód vždy vypnutý a výběr prázdný — `_mode_object_name` a `SelectionState` jsou modulo-level proměnné mimo Blender undo stack a nejsou serializovány do `.blend` souboru. Jde o záměrné bezpečné výchozí chování: po restartu Blenderu nebo načtení souboru začíná uživatel v neutrálním stavu a musí mód aktivovat explicitně (Shift+Q). Geometrie, grafy a veškerá topologická data jsou perzistovaná přes JSON custom property `_floorplan_graphs` a jsou korektně rekonstruována.
