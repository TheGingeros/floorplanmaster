# FP2: Parametrické generování a úprava
Tato funkce zajišťuje, že půdorys nezůstane jen statickou kresbou, ale stává se plně responzivním modelem. Umožňuje uživatelům nedestruktivně upravovat parametry stěn, otvorů a místností uvnitř aktivního podlaží. Model není reprezentován jako obyčejná statická síť (mesh) polygonů, ale jako dynamický matematický systém řízený vstupními parametry (délka, výška, tloušťka). Jakákoliv změna parametru v UI vyvolá přepočet a bezprostředně se propíše přes Pojmenované atributy do Geometry Nodes.

## Must-Have - součástí MVP
Následující požadavky definují absolutní technologický základ pro parametrické chování addonu. Bez těchto bodů by se jednalo pouze o obyčejný kreslící nástroj. Zajišťují, že systém správně reaguje na změny hodnot, udržuje logické vazby mezi nadřazenými a podřízenými objekty (stěna a její otvory) a garantuje, že žádná úprava nezničí původní data.

1. **Dynamická reprezentace a úprava stěn**
   - Stěny si pamatují své parametry (tloušťka: 0.05m - 1.0m, výška: 1.0m - 10.0m, materiál, posun na ose).
   - Úpravy probíhají přes panel vlastností (Properties) nebo 3D manipulátory ve viewportu.
   - Geometrie stěny se generuje dynamicky, není to destruktivní polygonový model.

2. **Dynamický posun otvorů (Oken a Dveří)**
   - Systém musí datově a matematicky svázat otvor s konkrétní stěnou ve Vrstvě 1.
   - Pokud uživatel posune roh stěny (změní její délku nebo úhel), všechny závislé otvory na této stěně se musí automaticky posunout a zrotovat spolu s ní (např. udržením relativní pozice na úsečce).

3. **Zachycení změn (Update Callbacks)**
   - Všechny posuvníky a textová pole v UI Blenderu mají navázanou funkci `update`.
   - Když uživatel změní hodnotu parametru, addon tuto změnu okamžitě zachytí, propíše novou hodnotu do datového modelu (Vrstva 1 nebo 2) a vyvolá synchronizační cyklus.

4. **Úprava parametrů místnosti**
   - Jméno, typ místnosti, materiál podlahy/stropu, barvy.
   - Perzistentní ID místností zůstávají nedotčena i při masivní změně parametrů (metadata se neztratí).

5. **Zpětná vazba v reálném čase a nedestruktivnost**
   - Geometry Nodes drivers automaticky čtou aktualizované atributy.
   - 3D pohled se překresluje okamžitě, bez nutnosti manuálního refreshe sítě.
   - Plná podpora Blender Undo/Redo systému pro každý posun posuvníku.

## Should-Have (Schopnosti)
Tato rozšiřující funkce posouvá technickou eleganci a výkon addonu. Přestože vyřezávání otvorů lze řešit i primitivnějšími metodami, přesun této zodpovědnosti přímo do vizualizační vrstvy zamezuje vzniku chyb v topologii a drasticky zjednodušuje Python kód.

1. **Chytrá správa vytváření otvorů (Geometry Nodes Booleans)**
   - Místo složitého a náchylného dělení polygonů v Pythonu (pomocí BMesh booleans) se ořezávání otvorů pro okna a dveře řeší zcela dynamicky až ve Vrstvě 3.
   - Python předá pouze poziční data (bounding boxy otvorů) a uzel *Mesh Boolean* v Geometry Nodes se postará o vizuálně čisté vyříznutí díry do stěny v reálném čase.