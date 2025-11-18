# FloorPlanMaster - návrh zadání pro bakalářskou práci z oboru Počítačová Grafika na FIT ČVUT

**Autor:** Oskar Wladař (username: wladaosk)        
**Název:** Vývoj add-on modulu pro Blender pro architektonickou dispozici: rychlé kreslení půdorysu, generování místností a vkládání otvorů     
**Cíl práce:** Vytvořit rozšiřující modul (add-on) pro software Blender, zaměřený na architektonické použití, který umožní uživateli v top-view (pohled shora) kreslit dispozice „tužkou“, definovat parametry stěn (délka, šířka, výška) v uživatelsky zvolených jednotkách, poté je rozdělit do jednotlivých místností, volit barvy/stěny/podlahy/stropu, a dále vkládat okna a dveře s přesným snapováním ke stěně, včetně tvorby otvoru pomocí boolean operace. Add-on také vypočítá výměry (plocha) a objem každé místnosti.

## Funkční požadavky:       
#### 1. "Kreslení" stěn v top-view
- Uživatel v pohledu shora („top view“) spustí nástroj „kresli stěnu“ (tužkou) a nakreslí tvar místnosti či dispozice jako polylinku či segmenty.
- Po dokončení kresby je možno definovat výšku stěn (např. 2,8 m) nebo jinou hodnotu
- Stěny mají parametry: délka, šířka (tloušťka stěny), výška. Jednotky jsou zvolitelné (metry, milimetry, jednotky Blenderu).
#### 2. Generování místností a rozdělení podle objektů
- Na základě uzavřených smyček stěn add-on identifikuje místnosti.
- Uživatel může pojmenovat každou místnost (např. „Kuchyň“, „Koupelna“).
- Uživatel může volit barvu / materiál pro stěny, podlahu i strop pro každou místnost.
- Možnost zapnout/vypnout viditelnost stěn/podlahy/stropu pro každou místnost (např. skrýt strop pro pohled shora).
#### 3. Výpočty a analytika
- Pro každou místnost vypočítat a zobrazit: plocha v m², objem v m³.
- U jednotlivých stěn zobrazit jejich aktuální šířku, délku a výšku(případně další informace).
#### 4. Vkládání oken a dveří
- Uživatel vybere typ prvku (Okno / Dveře) z knihovny objektů (přednastavené typy: jednokřídlé dveře, posuvné dveře; okna různé rozměry).
- Nástroj „vložit otvor“ umožní kliknout na stěnu, prvek se „snapne“ na plochu stěny (např. stěna je mesh, prvek je child objekt).
- Po vložení se stěna automaticky upraví — provede se boolean operace (výřez) pro vytvoření otvoru.
- Uživatel může upravovat parametry otvoru: šířku, výšku, vzdálenost od horního okraje/stěny, vzdálenost od bočních hran.
- Prvky lze přesouvat po normále stěny (tzn. změnit hloubku umístění, pokud relevantní).
- Možnost změnit typ dveří/okna nebo jejich velikost z UI.
#### 5. Uživatelské rozhraní
- Panel v Blenderu (např. v N-panelu) s kategoriemi: „Kreslení stěn“, „Definice místností“, „Barvy a materiály“, „Okna a dveře“, „Výpočty“.
- Každá operace dostupná jako operator s klávesovou zkratkou.
- Dialogy pro vstup parametrů stěn/místností/otvorů.
#### 6. Technické požadavky
- Implementováno v Python 3 pomocí API Blenderu (bpy).
- Datové struktury pro reprezentaci stěny, místnosti, otvoru (např. vlastní PropertyGroup).
- Boolean operace pro výřez otvorem musí být robustní (míněno řešit průnik/vedlejší hrany).
## Ukázka existujících řešení, jejich porovnání a jejich výhody/nevýhody
#### Archimesh - add-on pro Blender, který umožňuje generovat místnosti, okna, dveře a další architektonické prvky. [Archimesh stránka](https://extensions.blender.org/add-ons/archimesh/)
##### Výhody:
- Jednoduchost a dostupnost (rychlé „naklikání“ místnosti/okna/dveří).
- Rychlé generování základních prvků – místnost i s otvory bez většího nastavování.
- Nízká bariéra pro začátečníky; hodí se na „blockout“ a hrubé dispozice. (Souhrny a tutoriály to takto používají.)
##### Nevýhody:
- Parametrika je omezenější (po vygenerování už není vše pohodlně „živě“ upravitelné on-screen jako u Archipacku).
- Údržba/robustnost některých nástrojů – uživatelé zmiňují potřebu větších update a občasné potíže (např. auto-holes u dveří/oken).
- Méně „BIM-like“ (Building Information Modeling) workflow (spíš generátor prvků než kompletní systém s rozšířenou 2D→3D, kótami apod.)
#### Archipack - robustní framework pro Blender, zaměřený na architektonické modelování (parametrické stěny, okna, schodiště…). [Archipack stránka](https://blender-archipack.org/)
##### Výhody:
- Parametrické objekty s bohatými vlastnostmi (zdi, okna/dveře, schody, střechy, stropy, podlahy…).
- Realtime on-screen editace (manipulátory, rychlé úpravy na scéně).
- Širší nástroje/workflow: 2D→3D, auto-boolean, podpora BlenderBIM kót, import z křivek/grease-pencil jako stěny.
- Aktivnější vývoj a dokumentace mimo Blender manuál (changelog, nové funkce).
##### Nevýhody:
- Složitější křivka učení a „těžší“ UI (víc panelů a voleb, někdy těžkopádné).
- Dualita verzí (základ vs. rozšířená/placená), takže některé funkce jsou mimo čistě „stock“ Blender.
- Smíšené dojmy komunity — část uživatelů jej miluje, část volí ruční modelování kvůli jednoduchosti/robustnosti.
 
#### Mezery současných řešení, které lze vylepšit a nabídnout tak konkurenční add-on:
- „SketchUp-like“ kreslení zdí - Archipack sice umí stěny z křivky a grease-pencil, ale UX není vyloženě „tužka v půdorysu“ jako v SU/ArchiCAD.
- Robustní a srozumitelné vkládání otvorů se snapem na stěnu + auto-boolean + parametry (šířka, výška, odskoky od hran) – u Archimeshe jsou s „auto-holes“ hlášené slabiny; u Archipacku je to silné, ale UI je těžší. FloorPlanMaster může nabídnout štíhlé, specializované UX.
- Jednoduchý analytický modul (výměry/objemy) přímo navázaný na místnosti vytvořené kreslením — v obou add-onech to není centrální, „na jedno kliknutí“. Tyto detaily a analytiky jsou často uživately schované za náročným UI

## Závěr
FloorPlanMaster bude klást důraz na „pencil-wall“ nástroj (top-view), snap-based otvory (okna/dveře) s live booleany a jednoduché UI pro rozčlenění na místnosti + výpočty. Tím se jasně odliší od Archimeshe i od Archipacku.
