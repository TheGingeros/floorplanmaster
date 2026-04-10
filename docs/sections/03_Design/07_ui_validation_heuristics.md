# 3.7.2 Heuristické hodnocení

Heuristické hodnocení je analytická metoda použitelnosti, při níž je návrh rozhraní systematicky porovnáván s etablovanými principy dobré praxe — tzv. heuristikami — bez nutnosti provádět uživatelské testování. Použity jsou tři z deseti Nielsenových heuristik použitelnosti, které jsou pro nástrojový addon v kontextu 3D editoru nejvíce relevantní: viditelnost stavu systému, shoda se skutečným světem a uživatelská kontrola a svoboda. Zbývající heuristiky (konzistence, prevence chyb, flexibilita apod.) jsou do značné míry adresovány v rámci kontroly konzistence (kapitola 3.7.1) a analýzy okrajových případů (kapitola 3.6).

## Heuristika 1: Viditelnost stavu systému

*Systém musí uživatele vždy informovat o tom, co se právě děje — prostřednictvím vhodné zpětné vazby v přiměřeném čase.*

Nejvýraznějším rizikovým místem FloorPlanMasteru v této oblasti je modální nástroj Pencil Tool (FP1): pokud uživatel neví, v jakém stavu se automat nachází, může provádět akce s neočekávanými výsledky (například se pokusit kreslit, aniž by byl nástroj aktivní). Návrh adresuje toto riziko na třech úrovních:

**HUD overlay** — po aktivaci Pencil Tool se v levém dolním rohu viewportu (Blender standardní pozice pro statusová hlášení nástrojů) zobrazí stavová zpráva udávající aktuální stav automatu (ČEKÁNÍ / KRESLENÍ) a nápovědu platných kláves. Vzor je přímo přejat z Blender nativního Knife Tool, který ve stejné pozici zobrazuje „Cut" / „Confirm" pokyny. Uživatel znalý Blenderu tedy zprávu automaticky čte v místě, kde ji očekává.

**Preview stěna** — ve stavu KRESLENÍ se dynamicky aktualizuje modrá linka od posledního junctionu ke kurzoru. Vizuální zpětná vazba potvrzuje, že systém přijal počáteční bod a čeká na potvrzení dalšího. Bez tohoto prvku by uživatel neměl žádný způsob, jak zjistit, zda jeho první klik byl zaregistrován.

**Snap indikátor** — žlutý kruh u kurzoru při aktivním přichycení signalizuje, že příští LMB klik bude přichycen na konkrétní pozici (junction nebo mřížka). Tento typ viditelné zpětné vazby před akcí (ne jen po ní) je klíčový pro přesné kreslení; SketchUp používá identický vzor (zelený kruh = inference lock).

**Synchronizace N-panelu** — při výběru prvku se N-panel okamžitě aktualizuje a zobrazuje parametry vybraného prvku. Uživatel vždy vidí aktuální hodnoty bez nutnosti explicitně otevírat dialog — stav systému je průběžně viditelný.

Hodnocení: Heuristika je návrhem dobře pokryta. Každý krok, který systém provede nebo který od uživatele očekává, má přiřazenou viditelnou zpětnou vazbu.

## Heuristika 2: Shoda se skutečným světem

*Systém by měl mluvit jazykem uživatele — pojmy, fráze a koncepty ze světa uživatele, nikoli ze systémového pojmosloví. Informace by měly plynout přirozeným a logickým řádem.*

FloorPlanMaster cílí na tři odlišné uživatelské skupiny (architekty, vizualizátory, game designery) popsané v kapitole 2.2. Volba terminologie a pracovního modelu musí být srozumitelná průřezově.

**Terminologie** — návrh používá architektonické pojmy: „místnost", „stěna", „junction" (jako technický termín pro uzel grafu bez přeloženého ekvivalentu v češtině), „tloušťka", „výška stěny", „otvor". Tyto pojmy odpovídají slovní zásobě architektů i game designerů pracujících s půdorysy. Naopak se vyhýbá interním technickým pojmům viditelným v návrhu (Vrstva 1, Vrstva 2, junction_id), které by v UI nikdy neměly být zobrazeny uživateli.

**Systém jednotek** — rozměry jsou zobrazeny v nastavitelném systému jednotek (metrický / imperiální), nikoli jako interní hodnoty v metrech. Uživatel pracující s normovými minimami v milimetrech nebo s herní mechanikou zalofoženou na palcích může přepnout jednotky bez zásahu do interní reprezentace dat.

**Mentální model kreslení** — workflow Pencil Tool (bod → stěna → uzavření cyklu → místnost) odpovídá způsobu, jakým architekti ručně kreslí půdorysy: tužkou se kreslí stěny jako čáry a místnosti existují jako logický důsledek uzavřených smyček. Uživatel nemusí explicitně deklarovat místnost — vzniká automaticky, stejně jako při ručním kreslení. Toto je zásadní rozdíl oproti nástrojům jako Archimesh, kde se místnosti vkládají jako předpřipravené objekty; FloorPlanMaster reflektuje přirozenější volnoruční model.

**Vizuální metafory** — ikona Pencil Tool v Toolbaru je tužka, ikona finalizace je aplikace modifikátoru (odpovídá Blender ikoně „Apply"), ikona kótování jsou pravítko a tužka. Všechny ikony odpovídají zavedené ikonografii Blenderu a architektonického softwaru.

Hodnocení: Heuristika je v návrhu pokryta. Terminologie a pracovní model odpovídají mentálnímu modelu cílových uživatelů.

## Heuristika 3: Uživatelská kontrola a svoboda

*Uživatelé si často vybírají funkce omylem a potřebují jasně označený „nouzový východ" pro opuštění nechtěného stavu bez procházení rozšířeným dialogem.*

Tato heuristika je pro modální nástroj s destruktivním potenciálem (nechtěná stěna v půdorysu, smazaná místnost) kritická.

**ESC jako nouzový východ** — kdykoli během aktivního Pencil Tool stisknutí `ESC` zruší aktuální kreslicí akci a vrátí automat do stavu ČEKÁNÍ bez zápisu do dat. Opakované `ESC` deaktivuje nástroj a vrátí Blender do standardního režimu. Tento vzor je identický s chováním Knife Tool a Loop Cut — uživatel si jej nemusí učit.

**`Z` jako inkrementální vrácení** — ve stavu KRESLENÍ umožňuje `Z` vrátit poslední potvrzený junction bez opuštění nástroje. Uživatel tak může opravit chybu bez nutnosti zavřít nástroj, přejít do Undo a nástroj znovu aktivovat — zrychlení iterativního kreslicího cyklu o dva kroky.

**Blender Undo integrace** — každá operace modifikující Vrstvu 1 nebo Vrstvu 2 je registrována do Blender Undo stacku (`bpy.ops.ed.undo`). Uživatel může kdykoli mimo aktivní nástroj použít `Ctrl+Z` pro globální Undo, které vrátí stav grafu i synchronizovanou geometrii.

**Nedestruktivní úpravy** — změna parametru stěny (tloušťka, výška) nepřepisuje nepřímo navazující geometrii, ale vyvolá přegenerování přes Geometry Nodes. Uživatel může parametr kdykoli vrátit na původní hodnotu bez ztráty informace. Tato vlastnost je přímým důsledkem architektonického rozhodnutí zachovat Python graf jako zdroj pravdy odděleně od Blender geometrie.

**Potvrzení pro destruktivní akce** — smazání místnosti nebo stěny z kontextové nabídky zobrazí pop-over s potvrzením (název prvku, tlačítka Smazat / Zrušit). Nevratné akce bez potvrzení by porušovaly jak tuto heuristiku, tak Blender konvenci (nativní operátory jako Delete Object zobrazují potvrzovací dialog při mazání více prvků).

Hodnocení: Heuristika je v návrhu pokryta. Každá destruktivní nebo těžko reverzibilní akce má přiřazený nouzový východ nebo potvrzovací krok.
