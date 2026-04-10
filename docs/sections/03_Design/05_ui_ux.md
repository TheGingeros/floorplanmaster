# 3.5 Návrh uživatelského rozhraní (UI a UX)
Tato sekce obaluje definované funkce (kapitola 3.4) vizuálním a interaktivním rozhraním — popisuje, jak uživatel systém fyzicky ovládá a jakou vizuální zpětnou vazbu od Blenderu dostává. Návrh se opírá o zavedené vzory z existujících architektonických nástrojů: Archimesh a Archipack (N-panel s parametry, gizmo manipulace), AutoCAD (klávesové zkratky pro kreslení, HUD s rozměry) a SketchUp (okamžitá vizuální zpětná vazba při kreslení). Společným jmenovatelem těchto nástrojů je princip „nakresli a ihned uprav" — uživatel nemusí přepínat mezi režimy, parametry jsou dostupné okamžitě po vytvoření prvku. Blender mechanismy pro realizaci těchto vzorů (draw_handler, Gizmo API, kontextová menu, RNA datový most) jsou podrobně popsány v [technické analýze UI](../02_Analysis/06_ta_ui.md) a [analýze UI vzorů](../02_Analysis/06_ta_ui_patterns.md).

## Uspořádání pracovního prostoru

Addon nevyžaduje vlastní editor ani nová okna — využívá standardní Blender layout a rozšiřuje ho o záložku v N-panelu a GPU overlay vrstvy. Tento přístup odpovídá konvenci Archipack i Archimesh, které se integrují do stávajícího 3D Viewportu bez nutnosti přepínat workspace:

- **3D Viewport** — hlavní kreslicí plocha; addon přidává overlay vrstvy (HUD, snap indikátory, kóty FP7); geometrie scény se nemění dokud není spuštěna finalizace (FP4). Přístup odpovídá SketchUp modelu, kde uživatel kreslí přímo v perspektivním pohledu a náhled geometrie se aktualizuje v reálném čase.
- **N-panel → záložka "FloorPlanMaster"** — seznam místností a stěn s metrikami, statické parametry vždy viditelné; vzor přejat z Archipack Properties panelu, kde po výběru objektu se jeho parametry automaticky zobrazí v N-panelu (Auto-manipulate on select)
- **Toolbar vlevo (T-panel)** — ikonové tlačítko pro aktivaci Pencil Tool; ostatní nástroje jsou dostupné přes klávesovou zkratku nebo RMB kontextovou nabídku. Umístění v T-panelu odpovídá Blender konvenci pro modální nástroje (Knife Tool, Loop Cut, Poly Build).

## Nástroje a klávesové zkratky

Nástroje jsou aktivovatelné z Toolbaru i klávesovou zkratkou. Jednoznakové zkratky přejaty z AutoCAD konvence (D = Draw) a Blender slovníku (Z = vrácení akce, ESC = zrušení operátoru), aby uživatel pracující v obou prostředích nemusel přepínat mentální nastavení. Mapování je konzistentní s konvencemi Blenderu: LMB pro potvrzení (výchozí binding od Blenderu 2.80), RMB pro kontextovou nabídku, ESC pro zrušení — shodně s nativními nástroji Knife Tool a Poly Build.

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

GPU draw_handler overlay vrstva (realizace viz [technická analýza GPU](../02_Analysis/06_ta_ui_gpu.md)) nezasahuje do geometrie scény ani do finalizované sítě. Barevná sémantika overlay prvků přejata z Blenderových vlastních nástrojů (Knife Tool, Loop Cut), aby konvence byly pro uživatele Blenderu okamžitě čitelné bez nutnosti učení:

| Prvek | Barva | Stav |
| :--- | :--- | :--- |
| Potvrzené stěny | Světle šedá | Normální |
| Preview stěna (FP1) | Modrá | Navrhovaný, nepotvrzený prvek |
| Snap indikátor u kurzoru | Žlutá | Aktivní přichycení |
| Vybraný prvek | Oranžová | Blender konvence výběru |
| Chybová indikace | Červená | Neplatná operace |

**HUD overlay** (vzor viz [HUD během modálního nástroje](../02_Analysis/06_ta_ui_patterns.md#hud-během-modálního-nástroje)) — aktivní po dobu Pencil Tool operátoru; zobrazuje: aktuální stav automatu (ČEKÁNÍ / KRESLENÍ), souřadnice kurzoru, délku a úhel navrhované stěny, aktivní snap typ, nápovědu platných kláves pro aktuální stav. HUD se skryje při přechodu do stavu NEAKTIVNÍ.

**Kóty** (FP7) — délky stěn nad středy hran; plocha a název místnosti v centroidu; přepínatelné klávesou T. Velikost textu a odsazení od stěny je konfigurovatelné v sekci Nastavení N-panelu.

## N-panel — záložka FloorPlanMaster

Panel je členěn do tří sekcí odpovídajících hierarchii datového modelu (kapitola 3.3). Vzor odpovídá Archipack Auto-manipulate on select — vybráním prvku ve viewportu se jeho parametry okamžitě zobrazí v příslušné sekci panelu. Archimesh používá obdobný princip, kde každý parametrický objekt (stěna, pokoj, sloup) má vlastní panel s editovatelnými parametry; FloorPlanMaster tento vzor přejímá, ale organizuje panel podle hierarchie datového modelu (místnosti → stěny) místo podle typu objektu.

**Nástroje** — tato sekce obsahuje akce pro vkládání prvků; je oddělena od seznamu existujících prvků, protože nepracuje s výběrem, ale s 3D kurzorem:
- tlačítko **Nakreslit tužkou** — alternativa k stisku `D`; aktivuje Pencil Tool (FP1)
- tlačítko **Vložit místnost** — otevře inline formulář se vstupy pro šířku, hloubku (nebo plochu + poměr stran), výšku stěn a tloušťku stěn; po potvrzení vloží pravoúhlou místnost se středem v pozici 3D kurzoru (FP2)

**Místnosti** — seznam uzlů Vrstvy 2 s metrikami (plocha, obvod, typ místnosti); klik na položku vybere místnost ve viewportu a zobrazí gizmos (FP6); inline editace názvu a typu místnosti bez nutnosti otevírat dialog.

**Stěny** — seznam hran Vrstvy 1 filtrovaný pro vybranou místnost; zobrazuje délku a tloušťku; klik vybere stěnu a zobrazí gizmos tloušťky a výšky (FP6).

**Nastavení** — globální parametry scény: systém jednotek, hustota mřížky, výchozí tloušťka stěny, výchozí výška stěny, velikost textu kót.

## Pop-over dialogy

Pro operace vyžadující textový vstup nebo potvrzení se použijí Blender pop-over dialogy otevírané z kontextové nabídky (FP5) — vzor popsaný v [analýze UI vzorů](../02_Analysis/06_ta_ui_patterns.md#pop-over-dialog-pro-detailní-parametry). Pop-over se otevírá u kurzoru myši a zobrazuje pouze parametry relevantní pro vybraný typ prvku. Pole pouze pro čtení (plocha, obvod) jsou zobrazena jako text bez editačního pole.

Dialog finalizace (FP4) je jedním z těchto pop-overů — zobrazuje volby organizace výstupu, přiřazení materiálů a opci zachování originálu, jak je specifikováno v [návrhu FP4](./04_features_fp4.md).
