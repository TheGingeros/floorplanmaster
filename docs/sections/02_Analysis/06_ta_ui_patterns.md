# UI vzory v architektonických nástrojích

Analýza existujících řešení (kapitola 2.1) popsala Archimesh, Archipack a CAD nástroje z pohledu jejich funkcí. Tato sekce extrahuje konkrétní UI vzory, které se opakují napříč nástroji a které jsou zavedeny v cílové uživatelské skupině — tedy vzory, které uživatel již ovládá a které není třeba se učit.

## Sidebar / Properties panel

**Kde se vyskytuje:** Archimesh (záložka v N-panelu), Archipack (vlastní Properties system), Revit (Properties palette)

Parametry vybraného objektu jsou trvale viditelné v postranním panelu jako alternativa k modálním dialogům. Uživatel vidí aktuální hodnoty i bez editace, může iterativně upravovat parametry bez zavírání a otevírání oken.

Archipack tento vzor posouvá dál: vybráním objektu se jeho parametry *automaticky* zobrazí v N-panelu bez nutnosti klikání na "Properties" tlačítko — eliminuje jeden krok z každé editace.

Alternativou jsou modální dialogy (AutoCAD příkaz `Properties`, SketchUp Entity Info) — ty vyžadují explicitní otevření a uzavření, což zpomaluje iterativní workflow.

**Vhodné pro:** statické parametry (tloušťka stěny, typ místnosti, výška), kde uživatel potřebuje hodnotu vidět i bez aktivní editace.

## Gizmo při výběru (Auto-manipulate on select)

**Kde se vyskytuje:** Archipack — při výběru stěny se ve viewportu automaticky zobrazí táhla pro tloušťku a výšku; SketchUp — přesunutí myši nad hranu zobrazí táhlo pro změnu délky

Gizmos umožňují přímou geometrickou manipulaci bez přepnutí do jiného nástroje nebo otevření panelu. Jsou optimální pro nejčastější operace (změna délky, tloušťky), nikoli pro méně časté operace vyžadující zadání textu nebo výběr z enumu.

Alternativou je workflow "select → edit panel" (Blender standardní přístup, Revit) — přesnější, ale vyžaduje více kliků pro jedno rozhodnutí.

**Vhodné pro:** geometrické úpravy prováděné tažením myši, kde přesnost není kritická (uživatel vidí výsledek in-place).

## HUD během modálního nástroje

**Kde se vyskytuje:** Blender vlastní nástroje (Knife Tool, Loop Cut, Extrude) — zobrazují aktuální hodnoty a nápovědu kláves přímo ve viewportu; SketchUp — délka v pravém dolním rohu při kreslení

HUD (Heads-Up Display) slouží jako nápovědní systém pro operace, které ne každý uživatel ovládá zpaměti. Zobrazení aktuálních hodnot (délka, úhel) eliminuje nutnost přepínat pohled mezi viewportem a jiným panelem.

**Vhodné pro:** modální nástroje s více stavy a více klávesovými vstupy, kde uživatel potřebuje okamžitou zpětnou vazbu o probíhající operaci.

## Kontextová nabídka na RMB

**Kde se vyskytuje:** Blender (RMB = kontextová nabídka u kurzoru), Archipack (RMB na objekt otevírá rychlou nabídku), AutoCAD (RMB = kontextová nabídka nebo repeat last command)

RMB jako přístup k méně frekventovaným akcím je v Blenderu primární UI konvencí a uživatelé Blenderu ji mají zafixovanou. Kontextová nabídka je citlivá na vybraný prvek — pro místnost zobrazuje jiné akce než pro stěnu nebo prázdnou plochu. Tím se redukuje vizuální šum (uživatel nevidí irelevantní akce).

**Vhodné pro:** akce prováděné méně než jednou za editační cyklus (přejmenování, smazání, nastavení materiálu).

## Pop-over dialog pro detailní parametry

**Kde se vyskytuje:** Archipack (pop-over u kurzoru pro parametry prvku); Blender nativně (F9 otevírá pop-over pro úpravu poslední operace)

Pop-over se otevírá u pozice kurzoru a poskytuje prostor pro zadání hodnot, které v gizmech nebo N-panelu není místo — zejména text (název místnosti) a výběr z enumu (typ místnosti). Výhodou oproti modálnímu dialogu je, že pop-over se zavře kliknutím mimo, bez nutnosti `OK / Zrušit` potvrzení pro čtecí operace.

**Vhodné pro:** operace vyžadující textový vstup nebo potvrzení (přejmenování, nastavení finalizačních parametrů FP4).

## Jednoznakové zkratky

**Kde se vyskytuje:** AutoCAD (L = Line, C = Circle, E = Erase, Mezerník = opakování posledního příkazu); Blender (G = Grab, R = Rotate, S = Scale, X = Delete)

Jednoznakové zkratky snižují latenci opakovaných akcí a umožňují workflow bez přepnutí pohledu na toolbar. Podmínkou je, aby zkratky odpovídaly prvnímu písmenu akce nebo ustálené konvenci v daném prostředí.

**Vhodné pro:** nejčastěji používané nástroje, které jsou spouštěny vícekrát za session.

[Zdroje](../../files/00_sources.md#uživatelského-rozhraní)
