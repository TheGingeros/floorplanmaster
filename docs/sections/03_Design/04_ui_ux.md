# 3.4 Uživatelské rozhraní
Technická analýza identifikovala [UI vzory z existujících architektonických nástrojů](../../02_Analysis/06_ta_ui_patterns.md) (Archimesh, Archipack, AutoCAD, SketchUp), které jsou v cílové uživatelské skupině zavedeny. Blender mechanismy pro jejich realizaci (draw_handler, Gizmo, kontextová menu, RNA datový most) jsou popsány v [technické analýze UI](../../02_Analysis/06_ta_ui.md).

## Uspořádání pracovního prostoru

Addon nevyžaduje vlastní editor ani nová okna — využívá standardní Blender layout a rozšiřuje ho o záložku v N-panelu a GPU overlay vrstvy:

- **3D Viewport** — hlavní kreslicí plocha; addon přidává overlay vrstvy (HUD, snap indikátory, kóty FP7); geometrie scény se nemění dokud není spuštěna finalizace (FP4)
- **N-panel → záložka "FloorPlan"** — seznam místností a stěn s metrikami, statické parametry vždy viditelné; vzor přejat z Archipack Properties panelu
- **Toolbar vlevo** — ikonové tlačítko pro aktivaci Pencil Tool; ostatní nástroje jsou dostupné přes klávesovou zkratku nebo RMB kontextovou nabídku

## Nástroje a klávesové zkratky

Nástroje jsou aktivovatelné z Toolbaru i klávesovou zkratkou. Jednoznakové zkratky přejaty z AutoCAD konvence (D = Draw) a Blender slovníku (Z = vrácení akce, ESC = zrušení operátoru), aby uživatel pracující v obou prostředích nemusel přepínat mentální model.

| Akce | Klávesa | Kontext |
| :--- | :--- | :--- |
| Aktivovat Pencil Tool (FP1) | D | Globální |
| Potvrdit bod | LMB nebo Enter | Pencil Tool aktivní |
| Vrácení posledního bodu | Z | Pencil Tool — stav KRESLENÍ |
| Zrušit aktuální čáru | ESC | Pencil Tool aktivní |
| Kontextová nabídka (FP5) | RMB | Nad jakýmkoliv prvkem nebo prázdnou plochou |
| Přepnout kótování (FP7) | T | Globální |
| Dočasně potlačit snap | Shift (držet) | Pencil Tool aktivní |

RMB jako spouštěč kontextové nabídky je Blender konvencí — zachován beze změny, aby uživatel nemusel měnit svalovou paměť.

## Overlay vrstva

GPU draw_handler overlay vrstva (realizace viz [technická analýza GPU](../../02_Analysis/06_ta_ui_gpu.md)) nezasahuje do geometrie scény ani do finalizované sítě. Barevná sémantika overlay prvků přejata z Blenderových vlastních nástrojů (Knife Tool, Loop Cut), aby konvence byly pro uživatele Blenderu okamžitě čitelné bez nutnosti učení:

| Prvek | Barva | Stav |
| :--- | :--- | :--- |
| Potvrzené stěny | Světle šedá | Normální |
| Preview stěna (FP1) | Modrá | Navrhovaný, nepotvrzený prvek |
| Snap indikátor u kurzoru | Žlutá | Aktivní přichycení |
| Vybraný prvek | Oranžová | Blender konvence výběru |
| Chybová indikace | Červená | Neplatná operace |

**HUD overlay** (vzor viz [HUD během modálního nástroje](../../02_Analysis/06_ta_ui_patterns.md#hud-během-modálního-nástroje)) — aktivní po dobu Pencil Tool operátoru; zobrazuje: aktuální stav automatu (ČEKÁNÍ / KRESLENÍ), souřadnice kurzoru, délku a úhel navrhované stěny, aktivní snap typ, nápovědu platných kláves pro aktuální stav. HUD se skryje při přechodu do stavu NEAKTIVNÍ.

**Kóty** (FP7) — délky stěn nad středy hran; plocha a název místnosti v centroidu; přepínatelné klávesou T. Velikost textu a odsazení od stěny je konfigurovatelné v sekci Nastavení N-panelu.

## N-panel — záložka FloorPlan

Panel je členěn do tří sekcí odpovídajících hierarchii datového modelu (kapitola 3.2). Vzor odpovídá Archipack Auto-manipulate on select — vybráním prvku ve viewportu se jeho parametry okamžitě zobrazí v příslušné sekci panelu.

**Nástroje** — tato sekce obsahuje akce pro vkládání prvků; je oddělena od seznamu existujících prvků, protože nepracuje s výběrem, ale s 3D kurzorem:
- tlačítko **Nakreslit tužkou** — alternativa k stisku `D`; aktivuje Pencil Tool (FP1)
- tlačítko **Vložit místnost** — otevře inline formulář se vstupy pro šířku, hloubku (nebo plochu + poměr stran), výšku stěn a tloušťku stěn; po potvrzení vloží pravoúhlou místnost se středem v pozici 3D kurzoru (FP2)

**Místnosti** — seznam uzlů Vrstvy 2 s metrikami (plocha, obvod, typ místnosti); klik na položku vybere místnost ve viewportu a zobrazí gizmos (FP6); inline editace názvu a typu místnosti bez nutnosti otevírat dialog.

**Stěny** — seznam hran Vrstvy 1 filtrovaný pro vybranou místnost; zobrazuje délku a tloušťku; klik vybere stěnu a zobrazí gizmos tloušťky a výšky (FP6).

**Nastavení** — globální parametry scény: systém jednotek, hustota mřížky, výchozí tloušťka stěny, výchozí výška stěny, velikost textu kót.

## Pop-over dialogy

Pro operace vyžadující textový vstup nebo potvrzení se použijí Blender pop-over dialogy otevírané z kontextové nabídky (FP5) — vzor popsaný v [analýze UI vzorů](../../02_Analysis/06_ta_ui_patterns.md#pop-over-dialog-pro-detailní-parametry). Pop-over se otevírá u kurzoru myši a zobrazuje pouze parametry relevantní pro vybraný typ prvku. Pole pouze pro čtení (plocha, obvod) jsou zobrazena jako text bez editačního pole.

Dialog finalizace (FP4) je jedním z těchto pop-overů — zobrazuje volby organizace výstupu, přiřazení materiálů a opci zachování originálu, jak je specifikováno v [návrhu FP4](./03_features_fp4.md).
