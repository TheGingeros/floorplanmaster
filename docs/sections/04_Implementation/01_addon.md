# 4.1 Addon pro Blender

FloorPlanMaster se integruje do Blenderu jako Python balíček spuštěný přímo uvnitř Blenderova interpretu. Tato integrace je výrazně hlubší než pouhé přidání funkce: addon sdílí s Blenderem stejný Python interpret, může registrovat vlastní typy, ovlivňovat chování viewportu a zachytávat události v reálném čase. Blender pro tuto formu integrace definuje kontraktní dvojici funkcí — funkci pro aktivaci, která u Blenderu zaregistruje veškeré operátory, panely a draw handlery addonu, a funkci pro deaktivaci, která vše bez zbytků odregistruje. Životní cyklus addonu je tak plně řízen Blenderem; addon nezanechává žádné vedlejší efekty mimo dobu své aktivace.

## Izolace závislosti na Blender API

Propojení s Blenderem přináší specifickou vývojovou výzvu: kód závislý na Blender API nelze testovat standardním pytestem spuštěným z terminálu, protože mimo Blender toto API není k dispozici. Kdybychom celý projekt tomuto omezení podřídili, ztratila by datová jádra systému — topologické grafy, validační logika a geometrické výpočty — možnost automatického testování a s ní schopnost předcházet regresím při každé změně.

FloorPlanMaster tuto výzvu řeší striktním rozlišením kódu závislého na Blender API od čistého Pythonu. Závislosní pravidlo je prosazeno architektonicky: celé datové jádro — topologické grafy, validační funkce a matematické utility — je implementováno bez jakékoliv přímé vazby na Blender. Integrační vrstva pak při startu addonu podmíněně ověří dostupnost Blender API; pokud je dostupné, zaregistruje operátory, panely a draw handlery; pokud ne — například při spuštění testů z IDE — registraci přeskočí a čisté Python jádro zůstane plně funkční a importovatelné. Jeden vývojový projekt tak obsluhuje oba světy bez jakékoliv duplikace kódu.

## Závislost na NetworkX

Algoritmy pro detekci cyklů v planárních grafech, na nichž stojí automatická detekce místností, jsou postaveny nad knihovnou NetworkX — Python balíčkem třetí strany, který Blender ve svém interpretu nenabízí. Pro distribuci jako Blender Extension (formát zavedený v Blenderu 4.2) je NetworkX přibalen jako archiv ve formátu Python wheel přímo do balíčku addonu. Python dokáže z takového archivu importovat moduly přímo bez rozbalení. Vstupní bod addonu proto po spuštění přidá složku s archivem do vyhledávací cesty interpretu — NetworkX se stane dostupným bez jakéhokoliv zásahu uživatele, transparentně na všech podporovaných platformách.

<!-- ## Persistence nastavení a Undo/Redo

Projektová nastavení — výchozí tloušťka a výška nových stěn — jsou uložena jako vlastnosti registrované přímo na Blender scéně. Tato volba není nahodilá: každý soubor `.blend` nese nastavení specifická pro daný projekt nezávisle na globální konfiguraci addonu, v souladu s konvencemi nástrojů pro architektonické modelování. Globální nastavení chování addonu jsou záměrně ponechána pro budoucí rozšíření a neovlivňují architektonická data projektu.

Za běhu udržuje addon pracovní kopii datového modelu — strukturálního grafu, grafu místností a mapovače identifikátorů — jako Python objekty v paměti. Blender ale pro operaci Undo/Redo pracuje výhradně na úrovni mesh dat: při stisknutí Ctrl+Z obnoví předchozí stav mesh geometrie a atributů, Python objekty v paměti se ale neobnoví automaticky. Aby se pracovní kopie grafů a autoritativní zdroj dat nerozešly, platí pevné pravidlo: mesh je vždy autoritativní zdroj pravdy, Python kopie je jen provizorní výpočetní cache. Každý operátor proto na svém začátku rekonstruuje pracovní grafy přímo z aktuálního stavu meshe — a tím zaručuje konzistenci i po libovolném počtu Undo a Redo kroků. -->

