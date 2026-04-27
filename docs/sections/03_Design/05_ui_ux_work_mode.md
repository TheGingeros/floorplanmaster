# FloorPlan kontext — simulovaný pracovní mód

Ideálním designovým řešením pro addon operující na sémantické vrstvě nad obecnou Blender geometrií by byl vlastní pracovní mód paralelní k Object Mode a Edit Mode — „FloorPlan Mode" s jasně vymezeným kontextem, vlastními klávesami a explicitní bariérou vůči obecným Blender nástrojům. Takový mód by uživateli jednoznačně signalizoval, na jaké úrovni abstrakce se pohybuje.

Blender Python API ale neumožňuje přidání nového nativního módu — `object.mode_set()` je pevně omezeno na módy implementované v C jádru Blenderu. Návrh proto realizuje ekvivalentní řešení kompozicí dostupných mechanismů:

- **WorkspaceTool** (Pencil Tool, FP1) se zapíše do Toolbaru jako plnohodnotný Blender nástroj s vlastní ikonou — Blender sám vizuálně indikuje aktivní kontext odlišný od výchozího nástroje.
- **Persistentní GPU overlay** (overlay manager, sekce 3.5.4) vizuálně odlišuje sémantická data po celou dobu aktivního addonu — junction tečky, stěnové obrysy a barevné výplně místností zůstávají viditelné nezávisle na tom, který Blender nástroj je právě aktivní.
- **Modální operátor** při aktivním Pencil Tool pohltí klávesové události, které by jinak obsluhoval Blender (`G`, `E`, `X`, LMB) — sémantické operace tak mají prioritu před obecnými Blender transformacemi po celou dobu kreslení.

Výsledný efekt se uživateli chová jako mód: rozhraní je vizuálně odlišné, klávesy mají jiný kontext a reprezentace dat odpovídá sémantické úrovni. Limit oproti nativnímu módu spočívá v tom, že blokování obecných Blender nástrojů platí výhradně po dobu aktivity modálního operátoru — mimo aktivní kreslení může uživatel přepnout do Edit Mode a editovat mesh přímo, čímž obejde sémantickou vrstvu. Tato situace je vědomým důsledkem jednosměrného datového toku popsaného v kapitole 3.2.

## Viditelnost overlaye a podmínky výběru prvků

Výše popsaný model vyvolává konkrétní návrhové rozhodnutí: za jakých podmínek je GPU overlay viditelný a kdy je dostupný výběr sémantických prvků (stěna, místnost)?

Návrh zavádí **dvoustupňový přístup** odpovídající Blender konvencím:

| Podmínka | Stav overlaye | Dostupnost výběru stěny / místnosti |
| :--- | :--- | :--- |
| FloorPlan objekt skrytý v kolekci | Overlay skrytý | Výběr nedostupný |
| FloorPlan objekt viditelný, není aktivní | Overlay viditelný | Výběr nedostupný |
| FloorPlan objekt viditelný a aktivní | Overlay viditelný | Výběr dostupný |

**Overlay jako vlastnost viditelného objektu.** Kótování, barevné výplně místností, obrysy stěn a názvy místností jsou vizuální reprezentací dat patřících konkrétnímu FloorPlan objektu. Jsou proto viditelné kdykoli je objekt viditelný v kolekci — bez ohledu na to, zda je vybrán. Toto chování je konzistentní s Blender konvencemi: textura, barva materiálu nebo modifier preview jsou viditelné nezávisle na výběru.

V implementaci je ale účelné rozlišit dvě třídy overlay vrstev. **Pasivní vrstvy** navázané čistě na vizualizaci objektu mohou zůstat viditelné pro každý viditelný FloorPlan objekt. Naproti tomu **interakční vrstvy** navázané na aktivní výběr a klávesové akce (highlight vybrané stěny nebo místnosti, panel vlastností, klávesové hinty a zkratky typu `X`) jsou vázány na aktivní FloorPlan objekt. Uživatel tak stále vidí, že v scéně existují další FloorPlan objekty, ale sémanticky upravovat může vždy jen ten aktivní.

**Výběr sémantických prvků pouze pro aktivní objekt.** Raycast na stěny a místnosti (LMB v Object Mode) je dostupný výhradně tehdy, když je příslušný FloorPlan objekt aktivní (`context.active_object`). Tím se zabrání nechtěnému výběru stěny v pozadí při práci na jiném objektu. Technicky operátor `FLOORPLAN_OT_select_wall` obsahuje `poll()`, který vrátí `False`, pokud aktivní objekt není FloorPlan mesh.

**Problém dvojího kliknutí a jeho řešení.** Dvoustupňový přístup naivně zavádí dvojí kliknutí: uživatel nejdřív klikne na objekt (aktivace), pak klikne na stěnu (výběr). Řešení je **smart select**: LMB handler nejdřív testuje, zda klik zasáhl mesh FloorPlan objektu. Pokud zasáhl mesh neaktivního FloorPlan objektu, handler tento objekt nejdřív aktivuje (standardní Blender `ops.object.select_all` + set active) bez výběru stěny nebo místnosti — uživatel jedním klikem přepne kontext. Teprve druhý klik nad již aktivním FloorPlan objektem spouští raycast sémantických prvků. Stejným pravidlem se řídí i pomocné affordance: panel vlastností vybrané stěny či místnosti a klávesové hinty pro příslušné akce se zobrazují až v aktivním kontextu daného objektu.

**Dopad na scény s více FloorPlan objekty.** Jeden `.blend` soubor může obsahovat více FloorPlan objektů (různá podlaží, různé varianty). Overlay viditelný pro všechny viditelné FloorPlan objekty zároveň je žádoucí pro orientaci. Výběr stěny pracuje vždy jen s aktivním objektem — uživatel explicitně přepíná kontext kliknutím. Toto chování je identické s tím, jak Blender zpracovává editaci více meshe objektů: editovatelný je vždy jen aktivní.