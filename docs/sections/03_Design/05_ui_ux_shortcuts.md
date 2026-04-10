# 3.5.3 Klávesové zkratky

Klávesové zkratky urychlují nejčastěji opakované akce a umožňují workflow bez přepínání pohledu mezi viewportem a panely. Návrh zkratek se řídí dvěma principy: (1) zkratky musí být kompatibilní se stávající svalovou pamětí uživatelů Blenderu a AutoCADu, aby nemuseli přeučovat zafixované zvyky; (2) zkratky specifikované pro modální kontext (Pencil Tool aktivní) nesmějí kolidovat s Blender globálními zkratkami, aby se nenarušilo standardní chování editoru mimo aktivní nástroj. Logika odvozování zkratek je popsána v [analýze UI vzorů — Jednoznakové zkratky](../02_Analysis/06_ta_ui_patterns.md).

## Tabulka zkratek

| Akce | Klávesa | Kontext | Zdůvodnění |
| :--- | :--- | :--- | :--- |
| Aktivovat Pencil Tool (FP1) | `D` | Globální (3D Viewport) | `D` = Draw; konvence z AutoCADu, kde jednoznakové zkratky odpovídají prvnímu písmenu akce (L = Line, C = Circle); v Blenderu `D` není obsazeno globálně v Object Mode |
| Potvrdit bod / stěnu | `LMB` nebo `Enter` | Pencil Tool aktivní | LMB jako primární potvrzovací vstup je Blender standardem od verze 2.80 (výchozí keymap); `Enter` jako alternativa pro tablety nebo numerické vstupy |
| Vrátit poslední bod | `Z` | Pencil Tool — stav KRESLENÍ | Inkrementální undo specifické pro modální nástroj; `Z` jako Undo je etablovaná konvence (Ctrl+Z = globální Undo v Blenderu, AutoCADu i Windows); jednoznakové `Z` bez modifikátoru je v navrhovaném kontextu bezpečné, protože globální Ctrl+Z zůstává funkční a Z bez modifikátoru není v Blenderu v Edit Mode rezervováno pro jiné účely |
| Zrušit aktuální linii | `ESC` | Pencil Tool aktivní | Blender konvence pro přerušení modálního operátoru; shodné s Knife Tool a Loop Cut; RMB jako alternativa není použitelná, protože RMB slouží pro kontextovou nabídku (viz FP5) |
| Kontextová nabídka (FP5) | `RMB` | Nad libovolným prvkem nebo prázdnou plochou | RMB jako vstup kontextové nabídky je Blender primární konvencí; Archipack i nativní Blender nástroje toto mapování zachovávají; přemapování by porušilo svalovou paměť uživatelů |
| Přepnout kótování (FP7) | `T` | Globální (3D Viewport) | `T` = Toggle; v Blenderu `T` standardně přepíná Toolbar, ale pouze v případech kde není redefinováno; pro addon kontext je `T` voleno záměrně jako mnemotechnická pomůcka; alternativně lze zkratku nastavit v Nastavení addonu |
| Dočasně potlačit snap | `Shift` (držet) | Pencil Tool aktivní | Blender konvence pro dočasné přepnutí snap modu; použití stejného modifikátoru jako Blender nativní Grab (Shift = potlačí snap na středové body) zaručuje konzistenci s obecným pohybem |

## Konflikty a bezpečnost mapování

Všechny zkratky jsou registrovány jako `MODAL` (aktivní pouze uvnitř modálního operátoru) nebo jako `KEYMAP` s podmínkou kontextu (`bl_space_type = 'VIEW_3D'`), čímž se zabraňuje globálním konfliktům. Specificky: `D` je registrováno pouze pro `Object Mode → VIEW_3D`, kde Blender tuto klávesu nativně neobsazuje. Klávesové mapování lze v Blenderu přepsat v Preferences → Keymap — addon respektuje tuto možnost a neregistruje zkratky jako neměnné.
