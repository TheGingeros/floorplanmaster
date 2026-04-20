# 3.5.3 Klávesové zkratky

Klávesové zkratky urychlují nejčastěji opakované akce a umožňují workflow bez přepínání pohledu mezi viewportem a panely. Návrh zkratek se řídí dvěma principy: (1) zkratky musí být kompatibilní se stávající svalovou pamětí uživatelů Blenderu a AutoCADu, aby nemuseli přeučovat zafixované zvyky; (2) zkratky specifikované pro modální kontext (Pencil Tool aktivní) nesmějí kolidovat s Blender globálními zkratkami, aby se nenarušilo standardní chování editoru mimo aktivní nástroj. Logika odvozování zkratek je popsána v [analýze UI vzorů — Jednoznakové zkratky](../02_Analysis/06_ta_ui_patterns.md).

Keymap Pencil Toolu je záměrně navržen analogicky k Blender Knife Toolu: rozlišuje stav **ČEKÁNÍ** (žádná linie rozpracována) a stav **KRESLENÍ** (linie zahájena), přičemž `Enter` potvrzuje celou sezení a `ESC` ji beze změn ukončí.

## Tabulka zkratek

| Akce | Klávesa | Kontext | Zdůvodnění |
| :--- | :--- | :--- | :--- |
| Aktivovat Pencil Tool (FP1) | `D` | Globální (3D Viewport, Object Mode) | `D` = Draw; konvence z AutoCADu; v Blenderu `D` není obsazeno globálně v Object Mode |
| Umístit první bod / pokračovat v linii | `LMB` | Pencil Tool aktivní | LMB jako primární potvrzovací vstup je Blender standardem od verze 2.80 |
| Potvrdit sezení a uložit změny | `Enter` / `Numpad Enter` | Pencil Tool aktivní (oba stavy) | `Enter` jako potvrzení modálního operátoru je Blender konvencí (Knife Tool, Loop Cut); ukončí nástroj, synchronizuje graf do meshe a zapíše krok do undo stacku |
| Vrátit poslední umístěný bod | `Z` | Pencil Tool aktivní (oba stavy) | Inkrementální undo specifické pro modální nástroj; `Z` jako Undo je etablovaná konvence; jednoznakové `Z` bez modifikátoru je bezpečné — Blender `Z` (shading pie) je potlačeno po dobu aktivity modálního operátoru |
| Zrušit aktuální rozpracovanou linii | `RMB` | Pencil Tool — stav KRESLENÍ | Zruší linii od posledního umístěného bodu a vrátí nástroj do stavu ČEKÁNÍ; nezruší již potvrzené stěny z dřívějších linií; analogie s Knife Toolem, kde RMB ukončuje aktuální řez |
| Kontextová nabídka (FP5) | `RMB` | Pencil Tool — stav ČEKÁNÍ | Ve stavu ČEKÁNÍ (žádná linie aktivní) RMB propustí událost do Blenderu a zobrazí standardní kontextovou nabídku |
| Přerušit celou sezení bez uložení | `ESC` | Pencil Tool aktivní (oba stavy) | Ukončí modální operátor, odstraní všechny stěny a body umístěné v aktuální sezení z grafu a nemodifikuje mesh; platí v obou stavech — není nutné nejprve zrušit linii |
| Dočasně potlačit snap | `Shift` (držet) | Pencil Tool aktivní | Blender konvence pro dočasné přepnutí snap modu |
| Přepnout kótování (FP7) | `T` | Globální (3D Viewport) | `T` = Toggle; mnemotechnická pomůcka; alternativně nastavitelné v Preferences |

## Konflikty a bezpečnost mapování

Všechny zkratky jsou registrovány jako `MODAL` (aktivní pouze uvnitř modálního operátoru) nebo jako `KEYMAP` s podmínkou kontextu (`bl_space_type = 'VIEW_3D'`), čímž se zabraňuje globálním konfliktům. Specificky: `D` je registrováno pouze pro `Object Mode → VIEW_3D`, kde Blender tuto klávesu nativně neobsazuje. Po dobu aktivity modálního operátoru jsou ostatní klávesové zkratky Blenderu (nástroje, menu) blokovány — s výjimkou navigačních vstupů (střední tlačítko myši, scrollování, Numpad pohledy) a `RMB` ve stavu ČEKÁNÍ. Klávesové mapování lze v Blenderu přepsat v Preferences → Keymap — addon respektuje tuto možnost a neregistruje zkratky jako neměnné.
