# FP3: Správa prostoru a metadat
Tento modul tvoří organizační a analytický mozek celého addonu. Překračuje hranice pouhého 3D modelování a poskytuje uživateli základní BIM (Building Information Modeling) schopnosti. Zásadní rolí tohoto modulu je dodat nakresleným čarám sémantický význam – pochopit, že čtyři zdi tvoří místnost, a že několik místností tvoří podlaží. Umožňuje uživateli definovat celou hierarchii budovy, bezpečně přepínat mezi patry (aniž by došlo k porušení matematické planarity grafů) a udržovat v datech absolutní pořádek.

## Must-Have - součástí MVP
Následující požadavky definují kritickou datovou a analytickou infrastrukturu addonu. Zabezpečují, že systém dokáže sám rozpoznat logické celky budovy a poskytnout k nim základní metrická data. Bez těchto funkcí by addon nedokázal generovat podlahy a uživatel by neměl jak přepínat kontext mezi přízemím a patrem.

1. **Automatická detekce místností**
   - Systém na pozadí nepřetržitě analyzuje strukturální graf (Vrstvu 1) a pomocí detekce cyklů automaticky identifikuje uzavřené prostory stěn jako místnosti (Vrstva 2).
   - Umožňuje s těmito detekovanými místnostmi pracovat (vybírat je), přejmenovávat je, přidělovat jim typ (obytná, komerční) a evidovat jejich perzistentní ID.

2. **Výpočet a zobrazení prostorových dat**
   - Pro každou detekovanou místnost systém v reálném čase spočítá a zobrazí data o její hmotě (především přesnou podlahovou plochu v m² a délku obvodu).
   - Na základě parametru výšky místnosti a plochy umí systém poskytnout i data o celkovém objemu vzduchu v daném prostoru.

3. **Správa podlaží (Building Management)**
   - Vytvoření zastřešující struktury: přidávání, mazání a přejmenování nezávislých podlaží.
   - Nastavení výškové kóty (elevation) pro každé patro, čímž se patra poskládají správně nad sebe.
   - Nastavení aktivního podlaží (kritické pro nástroj Tužka, který musí vědět, do jakého 2D grafu právě zapisuje data).

4. **Perzistence dat (Interní serializace)**
   - Jelikož Blender nativně neukládá složité Python objekty (NetworkX grafy), systém musí zajišťovat automatickou serializaci datového jádra (hierarchie budovy, Vrstva 1 a 2) do formátu JSON.
   - Tento JSON řetězec se ukládá skrytě přímo do `.blend` souboru (jako Custom Property na kořenovém objektu).
   - Zajišťuje, že po zavření a opětovném otevření projektu se grafy v paměti bezztrátově obnoví a uživatel může plynule pokračovat v parametrické úpravě.

## Should-Have (Schopnosti)
Tato rozšiřující sada funkcí transformuje addon ze skvělého kreslícího nástroje na profesionální architektonický organizér. Hluboce integruje logiku addonu do nativního ekosystému Blenderu (přes Kolekce) a přináší pokročilé algoritmy pro prostorovou analýzu chování budovy.

1. **Hierarchizace v kolekcích a správa viditelnosti**
   - Doplněk automaticky zrcadlí logickou strukturu budovy do nativního systému Blender Collections (kolekcí).
   - Vytvoří přehlednou stromovou strukturu v Outlineru (Budova -> Podlaží -> Elementy).
   - Poskytuje vyhrazené UI rozhraní, které umožňuje hromadné a intuitivní přepínání viditelnosti (např. skrytí celého druhého patra a střechy pro čistý náhled do přízemí) na jedno kliknutí.