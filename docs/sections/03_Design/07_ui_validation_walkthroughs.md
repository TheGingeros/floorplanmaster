# 3.7.3 Kognitivní průchody

Kognitivní průchod (Cognitive Walkthrough) je metoda hodnocení použitelnosti, která simuluje zkušenost nového uživatele při plnění konkrétního úkolu. Hodnotitel prochází každý krok scénáře a klade čtyři otázky: (1) Uživatel ví, jakou akci provést? (2) Uvidí ovládací prvek, který akci spouští? (3) Po provedení akce rozpozná, že pokročil správným směrem? (4) Přináší zpětná vazba systému správný efekt? Metoda odhaluje problémy s pochopitelností UI bez nutnosti provádět formální uživatelské testování.

Zvoleny jsou dva reprezentativní scénáře pokrývající primární interakční vzory addonu: kreslení tužkou (UC 1.2) jako nejzákladnější a nejčastěji opakovaná akce, a vložení místnosti z parametrů (UC 1.1) jako odlišný vstupní bod pro uživatele preferující parametrický přístup.

## UC 1.2 — Kreslení dispozice tužkou

Předpoklady: uživatel otevřel Blender, má aktivní 3D Viewport v Object Mode, addon je nainstalován. Uživatel nemá předchozí zkušenost s addonem.

**Krok 1 — Aktivace nástroje**

Úkol: aktivovat Pencil Tool.

- *Ví uživatel, co dělat?* — Nový uživatel pravděpodobně prohledá Toolbar, protože ostatní kreslicí nástroje (Draw, Annotate) jsou tam umístěny. Ikona tužky s tooltipem „FloorPlanMaster — Pencil Tool (D)" je okamžitě dohledatelná. Alternativní cesta přes tlačítko v N-panelu je dostupná pro uživatele, kteří Toolbar přehlédnou.
- *Vidí ovládací prvek?* — Ano; ikona v Toolbaru je vizuálně odlišena addonovým oddělovačem od nativních nástrojů a tooltip se zobrazí při přejetí myší.
- *Pokročil správným směrem?* — Po kliknutí se ikona zvýrazní (Blender standardní highlight aktivního nástroje) a v levém dolním rohu viewportu se zobrazí stavová zpráva „ČEKÁNÍ — LMB: umístit první bod".
- *Zpětná vazba správná?* — Ano; uživatel vidí, že nástroj přijal vstup a čeká na první klik.

Hodnocení kroku: bez problémů. Umístění v Toolbaru a tooltip eliminují potřebu předchozí znalosti.

**Krok 2 — Umístění prvního bodu**

Úkol: kliknout do viewportu a zahájit kreslení.

- *Ví uživatel, co dělat?* — Stavová zpráva z kroku 1 explicitně říká „LMB: umístit první bod". Uživatel nezná pojem „junction", ale zpráva nepoužívá technický termín — říká pouze, co stisknout.
- *Vidí ovládací prvek?* — Ovládacím prvkem je cursor myši; není třeba vizuálního vyhledávání.
- *Pokročil správným směrem?* — Po kliknutí se stavová zpráva změní na „KRESLENÍ — LMB: potvrdit, Z: vrátit, ESC: zrušit" a od místa kliknutí ke kurzoru se dynamicky táhne modrá preview linka.
- *Zpětná vazba správná?* — Ano; preview linka a změna stavové zprávy jasně signalizují přechod do stavu KRESLENÍ.

Hodnocení kroku: bez problémů.

**Krok 3 — Kreslení a uzavření místnosti**

Úkol: nakreslit sérii stěn a uzavřít místnost.

- *Ví uživatel, co dělat?* — Opakované klikání potvrzuje stěny. Vizuálně: každá potvrzená stěna přejde z modré (preview) na světle šedou (potvrzená). HUD průběžně zobrazuje délku a úhel navrhované stěny.
- *Vidí ovládací prvek?* — Snap indikátor (žlutý kruh) se zobrazí při přiblížení ke stávajícímu junctionu — uživatel vidí, kdy může uzavřít cyklus přichycením na počáteční bod.
- *Pokročil správným směrem?* — Uzavření cyklu (přichycení na první junction) způsobí, že uzavřená plocha dostane barevnou výplň odpovídající výchozímu typu místnosti. Tato okamžitá vizuální změna potvrzuje, že místnost byla detekována.
- *Zpětná vazba správná?* — Ano; barevná výplň je přímou indikací úspěšné detekce místnosti, nikoli technická hláška. Uživatel tuto zpětnou vazbu chápe intuitivně jako „uzavřel jsem prostor".

Hodnocení kroku: bez problémů. Potenciální riziko: uživatel nemusí vědět, že uzavření cyklu na první junction je nutné pro vznik místnosti. Snap indikátor a barevná výplň po uzavření toto riziko zmírňují — pokud uživatel nemíří na první bod, místnost nevznikne a chybějící barevná výplň slouží jako implicitní indikace.

**Krok 4 — Úprava tloušťky stěny**

Úkol: po dokončení kresby upravit tloušťku jedné ze stěn.

- *Ví uživatel, co dělat?* — Uživatel buď klikne na stěnu ve viewportu a hledá editaci v N-panelu, nebo uchopí gizmo tloušťky (obousměrná šipka kolmá na stěnu) přímo ve viewportu. Obě cesty jsou dostupné; zkušenější uživatelé Blenderu pravděpodobně volí gizmo, méně zkušení N-panel.
- *Vidí ovládací prvek?* — Gizmo se zobrazí automaticky při výběru stěny (bez nutnosti přepnutí do speciálního režimu); N-panel zobrazí parametry vybrané stěny v sekci Místnosti. Oba ovládací prvky jsou viditelné bez dalšího hledání.
- *Pokročil správným směrem?* — Tažením gizma nebo úpravou hodnoty v N-panelu se geometrie okamžitě aktualizuje přes GN reevaluaci; uživatel vidí změnu v reálném čase.
- *Zpětná vazba správná?* — Ano; okamžitá vizuální aktualizace geometrie potvrzuje, že změna byla přijata.

Hodnocení kroku: bez problémů.

## UC 1.1 — Vložení místnosti z parametrů

Předpoklady: totožné jako UC 1.2. Uživatel chce vložit místnost zadáním rozměrů bez ručního kreslení.

**Krok 1 — Nalezení funkce „Vložit místnost"**

Úkol: otevřít N-panel a najít tlačítko pro vložení místnosti.

- *Ví uživatel, co dělat?* — Nový uživatel Blenderu může potřebovat vědět, že `N` otevírá N-panel (Sidebar). Tato znalost je základní Blender konvencí; tooltip oblasti naznačuje, že N-panel lze otevřít stiskem `N`. Ve FloorPlanMaster záložce je sekce Nástroje jako první — uživatel narazí na „Vložit místnost" bez potřeby scrollování.
- *Vidí ovládací prvek?* — Tlačítko „Vložit místnost" je v sekci Nástroje jako samostatný výrazný prvek. Popis (`tooltip`) říká: „Vloží pravoúhlou místnost se středem na 3D kurzoru".
- *Pokročil správným směrem?* — Po kliknutí se v panelu rozbalí inline formulář s poli: šířka, hloubka, výška stěn, tloušťka stěn. Uživatel vidí konkrétní vstupní pole bez přepnutí okna.
- *Zpětná vazba správná?* — Ano; formulář je kontextuálně smysluplný a pole mají výchozí hodnoty z nastavení scény.

Hodnocení kroku: bez problémů. Riziko: uživatel nemusí vědět, co je „3D kurzor" jako referenční bod vložení. Tooltip toto vysvětluje, ale pro uživatele bez Blender zkušenosti může být pojem nový. Riziko je akceptovatelné — 3D kurzor je fundamentální Blender koncept a jeho pochopení předchází práci s libovolným addonem pro modelování.

**Krok 2 — Zadání parametrů a potvrzení**

Úkol: zadat šířku 5 m, hloubku 4 m a potvrdit.

- *Ví uživatel, co dělat?* — Vstupní pole jsou číselná s jednotkami (výchozí metrický systém); uživatel je edituje přímým zápisem hodnot nebo kliknutím a tažením (Blender standartní způsoby editace číselných polí).
- *Vidí ovládací prvek?* — Ano; formulář je plně viditelný v N-panelu, tlačítko „Potvrdit" je výrazně umístěno pod poli.
- *Pokročil správným směrem?* — Po potvrzení se místnost vloží se středem na 3D kurzoru a ve viewportu se ihned zobrazí jako obarvená plocha s šedými stěnami. N-panel sekce Místnosti zobrazí novou položku s vypočítanou plochou (20 m²).
- *Zpětná vazba správná?* — Ano; okamžitá vizualizace místnosti a automaticky vypočítaná plocha v N-panelu potvrzují, že operace proběhla správně a výsledek odpovídá zadání.

Hodnocení kroku: bez problémů.

## Shrnutí kognitivních průchodů

Oba průchody neodhalily systémové problémy s pochopitelností. Identifikovány byly dvě drobné rizikové oblasti:

| Skénář | Krok | Riziko | Zmírnění v návrhu |
| :--- | :--- | :--- | :--- |
| UC 1.2 | Uzavření cyklu | Uživatel nemusí vědět, že uzavření je nutné pro vznik místnosti | Snap indikátor na prvním junctionu + barevná výplň po uzavření |
| UC 1.1 | Vložení místnosti | Pojem „3D kurzor" nemusí být znám novým uživatelům Blenderu | Tooltip vysvětluje chování; jedná se o fundamentální Blender koncept |

Obě rizika jsou na úrovni akceptovatelné pro addon určený uživatelům se základní znalostí Blenderu (definice cílové skupiny v kapitole 2.2). Žádné z nich nevyžaduje změnu návrhu UI.
