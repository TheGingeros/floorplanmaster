# Životní cyklus addonu v Blenderu
## 1. Fáze objevení a inicializace
- při zapnutí blenderu, program prohledá specifické složky na disku
- přečte metadata - `slovník bl_info` a python soubor `__init__.py`
- stav - addon je v tuto chvíli v systému známý, objeví se v seznaku v preferences, ale není aktivní a nezasahuje do paměti ani rozhraní blenderu
## 2. Fáze registrace a aktivace
- jestliže uživatel v preferences zaškrtně políčko pro aktivaci addonu, program zavolá jedinou avšak kritickou funkci - `register()`
    - touto funkcí říká addon blenderu, jaké jsou jeho třídy a nová data, a aby si je uložil do své vnitřní databáze
    - typicky se zde volá `bpy.utils.register_class()` pro každou třídu addonu
- zde se taky definují globální proměnné a nastavení addonu, které se navěšují přímo na existující datové struktury Blenderu
## 3. Fáze běhu a interakce
- po zaregistrování addon čeká, dokud není uživatelem nebo vnitřní událostí Blenderu vyvolán
- veškerý kód běží ve stejném vlákně jako samotný Blender - je omezen tzv. Global Interpreter Lockerem
- interakce probíhá třemi hlavními způsoby:
    1. Spuštění operátoru - u6ivatel klikne na tlačítko nebo použije zkratku, Blender najde zaregistrovanou třídu operátoru a zavolá její metodu `execute()`, operátor provede úkol a okamžitě skončí
    2. Modální běh - Speciální typ operátoru, který se po spouštění neukončí ale převezme kontrolu nad vstupy, volá se jeho metoda `modal()`, která běží ve smyčce event loop a naslouchá, dokud jí uživatel neukončí - například cut tool
    3. Reakce na události - addon může mít zaregistrované tzv. handlery (`bpy.app.handlers`), ty naslouchají změnám v pozadí, addon může obsahovat funkci, která se automaticky spustí například těsně před začátkem renderování, při uložení soubor nebo při změně framu v animaci
## 4. Fáze deaktivace a odregistrace
- proběhne pokud uživatel addon odškrtne v preferences nebo se blender vypne, program zavolá funkci `unregister()`
- nejdůležitější část pro stabilitu systému - addon zde musí po sobě absolutně dokonale vše uklidit
    - vše co bylo registrováno v register - `bpy.utils.unregister_class()`
- pokud se něco zapomene a uživatel addon vypne, v paměti programu zůstanou dead reference, často vede ke zmatení rozhraní a nevyhnutelnému pádu celé aplikace

## 5. Odinstalace
- probíhá čistě na úrovni operačního systému
- blender po odregistrování addonu jednoduše smaže jeho zdrojové .py soubory z disku
- adon už v paměti blenderu vůbec neexistuje

# Teorie grafů a topologická reprezentace prostorových uspořádání
## Aplikace grafů při strukturální analýze půdorysů
- při abstrahování fyzické formy do logické se využívají primárně grafy [konektivity](./definice.md#graf-konektivity) a [sousednosti](./definice.md#graf-sousednosti)
- vrcholy typicky reprezentující jednotlivé místnosti a hrany jsou fyzické nebo logické propojení mezi nimi
    - tato reprezentace je známá z analýzy vizibility a axiálních map, v architektuře se používá pro algoritmické hodnocení pohybu chodců či evakuačních tras
TODO