# 3.7.1 Kontrola konzistence

Kontrola konzistence hodnotí, jak plynule a přirozeně navržený addon zapadá do stávajícího ekosystému hostitelského programu (Blenderu) a zda je vnitřně soudržný — tedy zda totožné akce vedou k totožným výsledkům bez ohledu na to, z jakého místa rozhraní jsou spouštěny. Návrh vykazuje vysokou míru vnější i vnitřní konzistence, kterou dokumentují níže uvedené oblasti.

## Vnější konzistence — soulad s Blender ekosystémem

**Umístění nástroje (Toolbar)** — Pencil Tool je registrován jako WorkspaceTool a umístěn v T-panelu po levé straně 3D Viewportu, shodně s nativními modálními nástroji Knife Tool, Loop Cut a Poly Build. Blender od verze 2.80 rezervuje Toolbar výhradně pro nástroje pracující v kontinuálním modálním režimu s LMB vstupem — Pencil Tool tuto podmínku splňuje. Addony umísťující modální nástroje mimo Toolbar (Archimesh, Archipack) to činí z historických důvodů předcházejících WorkspaceTool API; nový návrh se přiklání k aktuální Blender konvenci.

**Klávesové zkratky** — mapování zkratek respektuje stávající Blender keymapping bez kolizí. `LMB` jako potvrzení je výchozí Blender binding od verze 2.80. `RMB` jako kontextová nabídka je primární Blender konvencí. `ESC` pro zrušení modálního operátoru je identické chování jako u Knife Tool a Loop Cut. `Z` jako inkrementální vrácení kroku v kontextu modálního nástroje rozšiřuje ustálenou asociaci klávesy s operací Undo, aniž by kolidovalo s globálním `Ctrl+Z`.

**Barevná sémantika** — overlay vrstva (kapitola 3.5.4) přejímá barevné konvence zavedené Blender nástroji:
- **Oranžová** pro vybraný prvek odpovídá barvě aktivního výběru ve 3D Viewportu (standardní Blender theme)
- **Modrá** pro nepotvrzené (preview) prvky odpovídá konvenci Blender nástrojů pro navrhuované/dočasné elementy (viz Loop Cut preview)
- **Žlutá** pro snap indikátor odpovídá vizuálnímu jazyku snap markeru v nativním Blender Snap systému
- **Červená** pro chybové stavy odpovídá Blender standardnímu error state zbarvení (varování v Info oblasti)

**N-panel vzor** — záložka FloorPlanMaster v N-panelu dodržuje konvenci ostatních architektonických addonů (Archimesh, Archipack): sekce jsou skládací (`collapsible`), výběr prvku ve viewportu automaticky synchronizuje stav panelu. Sekce Nástroje → Místnosti → Nastavení odpovídá logické hierarchii od spouštění akcí přes prohlížení prvků až ke konfiguraci — shodný princip jako v Blender Properties editoru (Tool → Item → View).

**Pop-over dialogy** — pop-overy otevírané u pozice kurzoru (vložení místnosti, parametry otvoru, finalizace) kopírují vzor F9 Last Operator pop-overu, který Blender nativně nabízí pro úpravu parametrů poslední operace; uživatelé Blenderu jsou s tímto vzorem dobře obeznámeni.

## Vnitřní konzistence — soudržnost v rámci addonu

**Multiplicity přístupu ke stejné akci** — každá klíčová akce je dosažitelná více cestami, přičemž výsledek je vždy identický:
- Aktivace Pencil Tool: klávesa `D` / tlačítko v N-panelu / klik na ikonu v Toolbaru → vždy stejný vstupní stav FP1 automatu
- Přepnutí kótování: klávesa `T` / přepínač v kontextovém menu / přepínač v N-panelu sekci Nastavení → vždy stejný stav FP7 draw_handleru
- Finalizace: tlačítko v N-panelu / kontextové menu prázdné plochy → vždy stejný pop-over FP4

**Parametry a jejich umístění** — parametry konkrétního prvku (tloušťka stěny, název místnosti) jsou vždy dostupné ve dvou sousedících místech: inline v N-panelu při výběru prvku a v pop-overu z kontextové nabídky. Nikdy nejsou duplicitně v Nastavení, které je vyhrazeno globálním výchozím hodnotám. Toto rozdělení je konzistentní napříč všemi typy prvků.

**Synchronizace výběru** — kliknutí na prvek v N-panelu vybere prvek ve viewportu; kliknutí na prvek ve viewportu aktualizuje stav N-panelu. Obousměrná synchronizace je konzistentní pro místnosti i stěny a zabraňuje situaci, kde uživatel edituje jiný prvek, než který vidí ve viewportu zvýrazněný — chyba, na kterou upozorňují uživatelé Archimesh v komunitních diskuzích.
