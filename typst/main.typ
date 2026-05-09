#import "ctufit-thesis.typ": *
#import "@preview/fletcher:0.5.7" as fletcher: diagram, node, edge
#import "glossarium/glossarium.typ": gls



// TODO
#let acknowledgment = [
  // Mé díky patří mému vedoucímu, Ing. Lukáši Bařinkovi, za jeho pomoc při formulaci mého vlastního tématu a jeho převedení do plnohodnotné práce, za jeho ochotu, přínosné rady a kritické hodnocení. Dále děkuji E. a mým přátelům za veškerou podporu a trpělivost, kterou se mnou měli během našich studií. 

  Aniž bych opomněl ostatní, mé díky patří především mému vedoucímu, Ing. Lukáši Bařinkovi.

  Nejvíce si cením jeho pomoci při formulaci vlastního tématu a jeho převedení do plnohodnotné práce.

  Kromě toho mu děkuji za jeho ochotu, přínosné rady a kritické hodnocení.

  A dále samozřejmě děkuji E. a mým přátelům za veškerou podporu.

  Především pak za trpělivost, kterou se mnou měli během našich studií.

]

#let declaration = [
  Prohlašuji, že jsem předloženou práci vypracoval samostatně a že jsem uvedl veškeré použité informační zdroje v souladu s Metodickým pokynem o dodržování etických principů při přípravě vysokoškolských závěrečných prací. 
  
  
  Beru na vědomí, že se na moji práci vztahují práva a povinnosti vyplývající ze zákona č. 121/2000 Sb., autorského zákona, ve znění pozdějších předpisů. V souladu s ust. § 2373 odst. 2 zákona č. 89/2012 Sb., občanský zákoník, ve znění pozdějších předpisů, tímto uděluji nevýhradní oprávnění (licenci) k užití této mojí práce, a to včetně všech počítačových programů, jež jsou její součástí či přílohou a veškeré jejich dokumentace (dále souhrnně jen „Dílo“), a to všem osobám, které si přejí Dílo užít. Tyto osoby jsou oprávněny Dílo užít jakýmkoli způsobem, který nesnižuje hodnotu Díla, avšak pouze k nevýdělečným účelům. Toto oprávnění je časově, teritoriálně i množstevně neomezené.

  Prohlašuji, že jsem v průběhu příprav a psaní závěrečné práce použil nástroje umělé inteligence. Vygenerovaný obsah jsem ověřil. Stvrzuji, že jsem si vědom, že za obsah závěrečné práce plně zodpovídám.


  // I hereby declare that the presented thesis is my own work and that I have cited all sources of information in accordance with the Guideline for adhering to ethical principles when elaborating an academic final thesis. I declare that I have used AI tools during the preparation and writing of my thesis. I have verified the generated content. I confirm that I am aware that I am fully responsible for the content of the thesis.
  // \
  // \
  // I acknowledge that my thesis is subject to the rights and obligations stipulated by the Act No. 121/2000 Coll., the Copyright Act, as amended. In accordance with Section 2373(2) of Act No. 89/2012 Coll., the Civil Code, as amended, I hereby grant a non-exclusive authorization (licence) to utilize this thesis, including all computer programs that are part of it or attached to it and all documentation thereof (hereinafter collectively referred to as the "Work"), to any and all persons who wish to use the Work. Such persons are entitled to use the Work in any manner that does not diminish the value of the Work and for any purpose (including use for profit). This authorisation is unlimited in time, territory and quantity.
]

#let abstract-ENG = [
  The thesis deals with the design and implementation of the FloorPlanMaster extension for Blender, enabling parametric and non-destructive modelling of architectural floor plans. Based on an analysis of three target user groups — architects, 3D visualizers, and game designers — and a comparative analysis of existing tools, functional and non-functional requirements were elicited. To meet these requirements, a three-layer hybrid architecture was designed, combining a structural graph for wall and junction topology, a semantic room graph for automatic detection of closed cycles, and a synchronization layer transferring data into the Blender mesh with named attributes read by the Geometry Nodes module.

  The result is a functional add-on implemented in Python, encompassing an interactive wall drawing tool based on a modal operator, parametric editing of wall thickness and height, automatic room detection with area computation, and support for openings (doors and windows) with positional validation. The add-on fills an identified gap in the Blender ecosystem and allows the entire workflow — from the initial floor plan sketch through parametric editing to the final mesh — to be carried out within a single environment, without the need to switch between specialized applications.
]

#let abstract-CZE = [
  Práce se zabývá návrhem a implementací rozšiřovacího modulu FloorPlanMaster pro Blender umožňujícího parametrické a nedestruktivní modelování architektonických půdorysů. Na základě analýzy tří cílových skupin uživatelů — architektů, 3D vizualizátorů a game designérů — a komparativní analýzy existujících nástrojů byly stanoveny funkční a nefunkční požadavky. Pro jejich splnění byla navržena třívrstvá hybridní architektura kombinující strukturální graf pro topologii stěn a styků, sémantický graf místností pro automatickou detekci uzavřených cyklů a synchronizační vrstvu přenášející data do Blender meshe s pojmenovanými atributy čtenými modulem Geometry Nodes.

  Výsledkem je funkční add-on implementovaný v Pythonu, zahrnující interaktivní nástroj pro kreslení stěn na základě modálního operátoru, parametrickou editaci tloušťky a výšky stěn, automatickou detekci místností s výpočtem jejich ploch a podporu otvorů (dveře, okna) s poziční validací. Addon zaplňuje identifikovanou mezeru v ekosystému programu Blender a umožňuje celý pracovní postup — od prvního náčrtu dispozice přes parametrické úpravy až po finální mesh — realizovat v jednom prostředí bez nutnosti přepínat mezi specializovanými programy.
]

#show: ctufit-thesis.with(
  title: "FloorPlanMaster: Blender add-on pro parametrické modelování místností",
  author-full: "Oskar Wladař",
  author-surnames: "Wladař",
  author-given-names: "Oskar",
  department: "Katedra softwarového inženýrství",
  study-program: "Informatika",
  specialization: "Počítačová Grafika",
  supervisor: "Ing. Lukáš Bařinka",
  year: "2026",
  declaration: declaration,
  declaration-place: "Praze",
  // TODO: CHECK DATE
  declaration-date: datetime.today(),
  acknowledgment: acknowledgment,
  abstract-CZE: abstract-CZE,
  abstract-ENG: abstract-ENG,
  keywords-CZE: "Blender add-on, parametrické modelování, půdorys, architektonická vizualizace, Geometry Nodes, grafový datový model, prostorová dispozice, Python API",
  keywords-ENG: "Blender add-on, parametric modeling, floor plan, architectural visualization, Geometry Nodes, graph data model, spatial layout, Python API",
  thesis-type: "bachelor",
  lang: "czech",
  twosided: false,
)

#let err-color = red.lighten(60%)
#let ok-color = green.lighten(60%)
#let holds-color = green.lighten(40%)
#let not-color = red.lighten(40%)
#let unknown-color = yellow.lighten(18%)

// #let impl(name) = {
//   // font: https://github.com/typst/typst/pull/6000
//   // set text(font: "DejaVu Sans Mono")
//   box(
//     baseline: 25%,
//     inset: 0.3em,
//     fill: blue.lighten(80%),
//     radius: 0.32em, // consistent with codly
//     text(size: 0.88em, name)
//   )
//   h(0.25em)
// }
// #let clause(state, name) = {
//   box(
//     baseline: 25%,
//     // inset: 0.34em,
//     inset: 0.3em,
//     fill: state,
//     radius: 0.32em, // consistent with codly
//     text(size: 0.88em, name)
//     // name
//   )
// }
// #let clauses(..pairs) = {
//   // set text(size: 0.885em)
//   for (state, name) in pairs.pos() {
//     clause(state, name)
//     h(0.25em)
//   }
// }

#show figure.where(kind: table): it => {
  let b = {
    box(
      width: 100%,
      grid(
        rows: (auto),
        row-gutter: it.gap,
        it.caption,
        {
          h(1fr)
          box(it.body)
          h(1fr)
        },
      )
    )
  }
  if it.placement == none {
    b
  } else {
    place(it.placement, float: true, b)
  }
  par[]
}

= Analýza <chap-analysis>

Blender je všestranný, ale pro architektonické skicování nevhodně vybavený nástroj — každá změna půdorysu se mění v destruktivní opravu vrcholů a přepočítávání otvorů, což narušuje plynulost návrhového procesu. Aby bylo možné FloorPlanMaster navrhnout správně, je nutné nejprve porozumět tomu, proč stávající řešení nestačí, kdo addon skutečně bude používat a co od něj v konkrétních situacích čeká. Tato analýza tedy postupně buduje obraz od problémové domény přes uživatele a jejich scénáře až ke strukturovaným požadavkům a výběru technologií, na nichž addon stojí.

== Doménová analýza

Architektonická dispozice vzniká iterativně: místnosti se posouvají, chodby se zužují, stěny mění tloušťku --- a každá z těchto změn by měla být otázkou sekund, ne minut ručního přepočítávání geometrie. Cílem doménové analýzy je pochopit, proč Blender jako obecný nástroj tento požadavek nativně nenaplňuje a jaký typ řešení by mezeru zaplnil. Nejprve je proto potřeba vymezit, čím se parametrické modelování liší od klasické polygonální práce, a poté zmapovat, jak se s tímto problémem vypořádala stávající řešení --- jak uvnitř programu Blender, tak mimo něj.

Blender @blender je primárně 3D polygonální modelovací nástroj. Ačkoliv nabízí obrovskou flexibilitu, pro specifické potřeby architektonického navrhování postrádá nativní nástroje: uživatel se musí soustředit na ruční opravu geometrie místo na samotný návrh. Cílem projektu je tuto mezeru zaplnit rozšiřovacím modulem, který umožní prostorové dispozice intuitivně vytvářet a nedestruktivně upravovat pomocí parametrů.

=== Parametrické modelování a prostorová dispozice

Parametrické modelování je způsob vytváření 3D modelů, kde tvar objektu není definován pevně, ale pomocí proměnných parametrů (číselných hodnot) a geometrických vztahů. Tvůrce přímo kontroluje vstupy a algoritmickou logiku závislostí: čtverec lze například nadefinovat parametrem šířky, parametrem délky a pravidlem kolmosti stran, přičemž pozdější změna parametrů způsobí automatické překreslení tvaru bez nutnosti manuálního zásahu.

Oproti klasickému polygonálnímu modelování, kde se pracuje s body, hranami a plochami jejich přímou manipulací, parametrické modelování pracuje s čísly, funkcemi a historií kroků. Polygonální modelování je primárně vhodné pro hry, filmy a animace; parametrické modelování převládá v architektuře, strojírenství a produktovém designu.

Rozlišují se dvě hlavní paradigmata @architizer_parametric @bim_vs_cad. _Historické_ modelování, typické pro #gls("cad", long: false) a #gls("bim", long: false) software, si pamatuje časovou osu úprav: software zaznamenává sekvenci kroků a umožňuje vrátit se k dřívějšímu kroku a automaticky přepočítat všechny závislé operace. Toto paradigma je standardem v průmyslovém #gls("cad", long: false) (SolidWorks @solidworks) i architektonickém #gls("bim", long: false) (Revit @revit). _Algoritmické_ modelování, označované také jako vizuální skriptování, popisuje geometrii pomocí uzlových grafů a je analogické Geometry Nodes v Blenderu.

Parametrické modelování v architektuře přináší posun od tradičního reprezentačního kreslení k algoritmickému přístupu. Tradiční #gls("cad", long: false) systémy se spoléhají na explicitní definici geometrie pomocí statických bodů a úseček. Parametrický přístup zavádí systém vzájemně propojených proměnných, matematických omezení a deduktivních pravidel, která dynamicky generují a aktualizují výslednou formu. Úprava jediného parametru --- například celkové výšky podlaží nebo tloušťky nosné stěny --- automaticky a kaskádovitě modifikuje všechny závislé entity @architizer_parametric.

_Prostorová dispozice_ je logické a funkční uspořádání trojrozměrného objemu do smysluplných celků (místností a zón) s definovanými vztahy mezi nimi. Tento pojem vymezuje konkrétní předmět návrhu, se kterým addon pracuje.

=== Analýza existujících řešení

Před návrhem nového nástroje je nutné pochopit, co již existuje a kde existující řešení selhávají --- jinak hrozí, že FloorPlanMaster jen zopakuje jejich slabiny. Tato sekce proto hodnotí nejvýraznější architektonické addony přímo pro Blender a porovnává je s nástroji mimo jeho ekosystém, aby bylo jasné, jaká mezera zůstala nezaplněna.

Všechny nástroje jsou hodnoceny podle pěti shodných kritérií: (1) _interaktivní kreslení půdorysu_ — přímé klikání bodů do viewportu způsobem tužky; (2) _parametrická editace stěn_ — možnost kdykoli změnit tloušťku, výšku nebo polohu stěny bez narušení sousední geometrie; (3) _automatická detekce místností_ — samostatné rozpoznávání uzavřených cyklů stěn jako místností s výpočtem ploch; (4) _správa otvorů_ — okna a dveře svázané s parametry stěny, pohybující se spolu s ní; a (5) _nedestruktivní workflow_ — parametrická úprava geometrii okamžitě přepočítá bez ručního zásahu do okolní topologie.

==== Architektonické rozšiřující moduly pro Blender

// Blender za posledních deset let prošel dramatickou evolucí. Původně vnímaný jako nástroj pro organické modelování, animace a vizuální efekty byl díky open-source modelu a robustnímu Python #gls("api", long: false) transformován v platformu schopnou realizovat komplexní architektonické projekty. Vzniklo tak několik specializovaných addonů.

*Archimesh* @archimesh je základním kamenem architektonických nástrojů pro Blender. Vytvořil ho Antonio Vazquez s cílem automatizovat tvorbu interiérových a exteriérových prvků, která by jinak zabrala hodně času manuálním modelováním. Díky stabilitě a užitečnosti byl dlouhodobě integrován přímo do oficiální distribuce Blenderu jako komunitní doplněk a je primárně určen pro rychlé skicování prostor a interiérový design.

Pro tvorbu místností nabízí Archimesh dva přístupy: definování počtu stěn a jejich rozměrů, nebo využití nástroje Grease Pencil, kde uživatel v půdorysném pohledu nakreslí hrubé obrysy místností a doplněk tyto tahy automaticky převede na trojrozměrné stěny. Addon dále umožňuje automatické generování podlah a stropů. Co se týče otvorů, podporuje dva typy oken --- kolejnicová a panelová --- s parametrickými parapety a systémem žaluzií. Součástí je rovněž generátor kuchyňských linek, polic a dalšího interiérového vybavení @archimesh.

*Archipack* @archipack byl vytvořen jako robustnější a výkonnější alternativa k Archimesh, zaměřená primárně na profesionální architekty a vizualizátory. Autorem je Stephen Leger a addon existuje ve dvou verzích --- Community Edition a Pro. Klíčovým rysem je důraz na interaktivní manipulaci: systém Auto-manipulate on select při výběru objektu zobrazí přímo ve 3D viewportu táhla (gizmos) a textové popisky. Parametry prvků jsou spravovány vlastním systémem vlastností, které zůstávají zachovány po celou dobu životnosti projektu --- uživatel může kdykoliv vybrat stěnu a změnit její tloušťku nebo výšku a všechny připojené prvky automaticky na tuto změnu reagují. Pro export nabízí Archipack generování řezů a půdorysů ve formátu #gls("svg", long: false); Pro verze pak export do formátu #gls("ifc", long: false) @archipack.

*BonsaiBIM* @bonsaibim zaujímá zcela odlišnou pozici: na rozdíl od Archimesh a Archipack je navržen jako nativní platforma pro tvorbu a správu informačních modelů budov, fungující na mezinárodním standardu #gls("ifc", long: false) @iso16739 (#gls("iso", long: false) 16739). Zatímco Archimesh a Archipack jsou nadstavby nad standardním modelovacím procesem a jejich data jsou spjata s `.blend` souborem, BonsaiBIM transformuje program Blender v plnohodnotný prohlížeč a editor databáze #gls("ifc", long: false) @bonsaibim.

==== Architektonické nástroje mimo Blender

Kromě Blenderu existují na trhu tři hlavní nástroje pro architektonické modelování, které udávají standard a pomáhají nám pochopit, co uživatelé potřebují.

*SketchUp* @sketchup je intuitivní 3D modelovací nástroj od společnosti Trimble. Jeho hlavní výhodou je, že se dá velmi rychle naučit a umožňuje snadno přenést nápady do 3D. Základem je nástroj Push/Pull, kterým uživatel nakreslí 2D plochu a jedním tahem z ní vytáhne 3D objekt. Díky tomu lze jednoduše rýsovat půdorysné obrysy stěn přímo v pracovním prostoru. Ze všech zmíněných nástrojů se tak SketchUp nejvíce blíží klasickému kreslení tužkou na papír. Parametrické úpravy jsou však velmi omezené --- jakmile objekt dokončíte, jeho rozměry se do systému neukládají jako parametry. Každá další změna proto znamená ruční zásah do geometrie. Nedestruktivní postup práce tu nefunguje a otvory se do stěn vyřezávají ručně pomocí booleovských operací, aniž by s danou zdí zůstaly dál propojené. Pro modelování nabízí SketchUp rozsáhlou online knihovnu (3D Warehouse) a export do mnoha formátů.

*Archicad* @archicad od společnosti Graphisoft patří k historickým průkopníkům parametrického #gls("bim", long: false) navrhování. Na rozdíl od SketchUpu nepracuje jen s prázdnou geometrií, ale s chytrými stavebními prvky: stěna má své konkrétní vlastnosti --- tloušťku, materiál, skladbu konstrukcí a návaznost na okolí. Při kreslení půdorysu uživatel vynáší stěny velmi jednoduše a intuitivně, přičemž program sám automaticky řeší jejich křížení a rohové spoje. Okna i dveře tvoří plnohodnotné objekty, které jsou pevně vázané na stěnu: zachovávají svou polohu v segmentu zdi a při změně tloušťky se samy přizpůsobí. Archicad také automaticky detekuje uzavřené místnosti a jejich plochu umí rovnou propisovat do výkazů. Umožňuje export do formátu #gls("ifc", long: false), #gls("dwg", long: false) a dalších standardů. Hlavní nevýhodou zůstává horší propojení s Blenderem a vysoká cena komerční licence.

*Revit* @revit od Autodesku je robustní parametrický #gls("bim", long: false) nástroj, který funguje jako komplexní projektová databáze. Každý prvek v modelu tvoří instanci takzvané „rodiny“ (family). Jakmile změníte její vlastnost --- například tloušťku stěny nebo výšku patra --- úprava se okamžitě propíše do všech výkresů, řezů, pohledů i výkazů výměr. Díky tomu je celá projektová dokumentace vždy aktuální a provázaná. Stěny se do půdorysu vynášejí zadáváním os nebo líců a systém opět automaticky řeší napojení na další konstrukční prvky i prostupy. Otvory fungují jako chytré parametrické objekty obdobně jako v Archicadu. V současnosti jde o průmyslový standard pro ty nejkomplexnější stavební projekty, cílí ale čistě na profesionální využití v #gls("bim", long: false) prostředí. Z toho plynou jeho úskalí: jeho osvojení je nesmírně časově náročné, vyžaduje silný hardware a drahou licenci. Pokud potřebujete jen naskicovat koncept nebo připravit jednoduchou vizualizaci, je zbytečně složitý a těžkopádný.

#figure(
  {
    set text(size: 0.8em)
    table(
      columns: (2fr, 1fr, 1fr, 1fr, 1fr, 1fr),
      align: (left, center, center, center, center, center),
      table.header(
        [*Nástroj*], [*Kreslení*], [*Param. editace*], [*Místnosti*], [*Otvory*], [* Nedestruktivní*],
      ),
      [Archimesh @archimesh], [Částečně], [Částečně], [Ne], [Ano], [Částečně],
      [Archipack @archipack], [Částečně], [Ano], [Ne], [Ano], [Ano],
      [BonsaiBIM @bonsaibim], [Ne], [Ano], [Ne], [Ano], [Ano],
      [SketchUp @sketchup], [Ano], [Částečně], [Ne], [Částečně], [Ne],
      [Archicad @archicad], [Ano], [Ano], [Ano], [Ano], [Částečně],
      [Revit @revit], [Částečně], [Ano], [Ano], [Ano], [Ano],
    )
  },
  caption: [Srovnání analyzovaných nástrojů podle hodnotících kritérií],
) <tab-tools-comparison>

==== Zjištěné nedostatky a příležitosti pro zlepšení

Z přehledu stávajících řešení vyplývají opakující se nedostatky, které nám jasně ukazují, jakým směrem by se měl ubírat vývoj nového modulu FloorPlanMaster.

*Chybí nástroj pro intuitivní rýsování půdorysů.* Archimesh ani Archipack nemají funkci, která by umožnila skicovat dispozici prostým zadáváním bodů přímo v pracovním okně (viewportu), jak jsme zvyklí ze SketchUpu nebo Archicadu. Archimesh sice umí převést tahy nástroje Grease Pencil na zdi a Archipack je dokáže vygenerovat z křivky, ale ani jedno nepůsobí jako přirozené kreslení. FloorPlanMaster by proto měl přinést interaktivní „tužku“ jako hlavní způsob rýsování --- nástroj, který by sledoval kurzor a na každé kliknutí okamžitě vytvořil segment stěny.

*Nespolehlivé vyřezávání otvorů.* Automatická tvorba otvorů v modulu Archimesh má známé problémy u složitějších stěn, zvlášť při použití výpočetní metody Exact. Archipack sice v tomto ohledu funguje spolehlivě, ale vložení okna nebo dveří znamená proklikat se nepřehledným množstvím složitých panelů s nastavením. V tomto směru se nabízí uživatelské prostředí radikálně zjednodušit: otvor by mělo stačit přidat pouhým kliknutím na stěnu a zadáním tří základních rozměrů (šířky, výšky a výšky parapetu). O bezchybnou návaznost geometrie by se na pozadí staraly Geometry Nodes (Mesh Boolean) přes datovou vazbu.

*Chybějící výkazy místností a ploch.* Žádný z testovaných doplňků v Blenderu neumí automaticky rozpoznat uzavřené prostory (místnosti) a rovnou spočítat jejich podlahovou plochu. Výpočty výměr jsou v Archipacku i Archimeshi buď nešikovně skryté v technickém nastavení, nebo zcela chybí. Přitom okamžitý přehled o místnostech a jejich výměrách přímo v hlavním panelu (N-panel) je naprosto zásadní informací pro architekty i game designéry, aby si mohli průběžně ověřovat parametry svého návrhu.

*Složitý přenos dat z externích programů do Blenderu.* SketchUp, Archicad i Revit jsou sice ve svém oboru špička, ale práce v nich je od ekosystému Blenderu izolovaná. Přenos konceptuálního modelu ze SketchUpu do renderovací scény v Blenderu vyžaduje export a zdlouhavé čistění topologie sítě. Tím se navíc ztratí všechny původní parametrické vlastnosti. Cílem modulu FloorPlanMaster je tuto bariéru zbourat a zajistit, aby celý proces návrhu --- od první skicy dispozice přes parametrické ladění až po finální 3D model (mesh) připravený na render --- probíhal pohodlně v jediné scéně přímo v Blenderu.

== Cílové skupiny

Parametrické modelování půdorysů v Blenderu může urychlit práci architektovi skicujícímu varianty pro klienta, vizualizátorce převádějící 2D výkresy z #gls("pdf", long: false) do 3D prostoru, i game designérovi, který po sérii testování potřebuje narychlo rozšířit herní chodbu. Každý z nich však od addonu očekává něco trochu jiného. Cílem této sekce je tyto skupiny přesně vymezit, pojmenovat jejich konkrétní frustrace s nativním Blenderem a ztělesnit je v uživatelských personách. Ty pak poslouží jako měřítko pro hodnocení každého budoucího návrhového rozhodnutí.

=== Uživatelské skupiny

Společným problémem všech tří skupin je frustrace z toho, že Blender nedokáže udržet krok s rychlostí jejich myšlení: potřeba změnit dispozici často přichází ve chvíli, kdy je geometrie již pevně spojená v jeden celek a její úprava je zdlouhavá. Každá skupina však naráží na specifické problémy a upřednostňuje jiné vlastnosti addonu, proto je nutné popsat je zvlášť.

==== 1. Architekti ve fázi konceptuálního navrhování

Architekti pracující na konceptuálním návrhu tvoří primární cílovou skupinu addonu. Jedná se o profesionály nebo studenty tvořící úvodní hmotové a prostorové studie. V této fázi se nezdržují mikrodetaily (jako je typ kování u dveří), ale zaměřují se na celkové proporce, návaznosti místností a celkové uspořádání půdorysu.

Vyžadují rychlou iteraci návrhu, přesné zadávání číselných hodnot (délky, šířky, výšky) a nedestruktivní úpravy — tedy možnost kdykoliv změnit parametry místnosti nebo plynule posouvat okna a dveře podél stěn. Modelování těchto prvků pomocí standardních nástrojů Blenderu pro ně představuje destruktivní proces: každá změna vyžaduje manuální opravu okolní geometrie, posouvání vrcholů a složité přepočítávání otvorů. To odvádí jejich pozornost od samotného navrhování a narušuje plynulost tvůrčí práce.

==== 2. 3D umělci a vizualizátoři

Vizualizátoři potřebují co nejrychleji postavit základní geometrii místností, aby se mohli naplno věnovat tomu hlavnímu — materiálům, nasvícení a samotnému renderingu. Jde o tvůrce zaměřené primárně na estetiku. Hrubá stavba pro ně představuje pouhé „plátno“, do kterého následně vkládají detailní modely nábytku a vybavení.

Kromě rychlosti je pro ně klíčová také čistá topologie výsledné geometrie, na které budou bezchybně fungovat textury a další renderovací modifikátory. Ruční modelování stěn a vyřezávání oken pomocí nativních Boolean modifikátorů totiž často vytváří nevzhlednou topologii a její ruční čištění je pro tyto umělce nepříjemnou a vysoce neefektivní rutinou.

==== 3. Game a level designéři

Game a level designéři využívají addon k rychlé tvorbě a iteraci herních blockoutů — hrubých modelů úrovní sloužících k testování hratelnosti, průchodnosti a pohybu hráče či kamery.

Požadují především modulární přístup k tvorbě prostoru, schopnost okamžitě měnit proporce na základě zpětné vazby z herního testování a bezproblémový export hotových tvarů do enginů jako Unreal Engine nebo Unity. Nativní modelovací nástroje Blenderu nejsou pro rychlý level design optimalizovány, a tak je ruční upravování rozměrů místností nebo přesouvání otvorů během prototypování příliš těžkopádné.

=== Persony

Abstraktní popis cílových skupin neukáže, jak přesně se zmíněné frustrace projevují v praxi — zda architekta brzdí přepočítávání návazných stěn, nebo spíše chybějící přehled o podlahové ploše; zda vizualizátorku zdržuje samotné modelování, nebo až následné čištění topologie po ořezu. Pro každou skupinu je proto definována jedna konkrétní persona. Její profil, cíle a frustrace slouží jako referenční bod při rozhodování o podobě a funkčnosti addonu.

==== 1. Architekt Adam

Adam (32 let) pracuje v menším architektonickém ateliéru a má na starosti úvodní studie a komunikaci s klienty při hledání tvaru a dispozice budovy. Běžně pracuje v profesionálních #gls("cad", long: false) a #gls("bim", long: false) programech (ArchiCAD, Revit), ale pro rychlé 3D koncepty a objemové studie si oblíbil Blender díky jeho svižnosti a real-time zobrazení. Neumí však programovat a práce s Geometry Nodes je pro něj příliš složitá.

Jeho typickým cílem je během pár hodin vytvořit pro klienta tři různé varianty prostorového uspořádání domu. Primárně ho zajímá hmota, návaznosti místností a základní rozměry. Frustruje ho zdlouhavé extrudování polygonů v nativním Blenderu: když klient požádá o rozšíření obývacího pokoje o metr, Adam musí ručně posouvat vertexy a složitě přepočítávat navazující stěny, přičemž mu navíc chybí okamžitý přehled o rozměrech místností. Od addonu očekává jednoduché rozhraní, ve kterém zadá rozměry místnosti nebo je naskicuje, a systém při jakékoliv změně automaticky zachová tloušťku zdiva a nerozbije návaznost na další prostory.

==== 2. Vizualizátorka Věra

Věra (28 let) je vizualizátorka na volné noze, která se specializuje na tvorbu fotorealistických interiérů pro developery a realitní kanceláře. Blender ovládá na špičkové úrovni — má hluboké znalosti materiálů, nasvícení i renderingu — a profiluje se spíše umělecky než technicky.

Běžně dostává od klienta 2D půdorys v #gls("pdf", long: false) a potřebuje z něj co nejrychleji vytvořit hrubý 3D obraz bytu, aby se mohla věnovat tomu hlavnímu: světlu, texturám a vybavení. Zdlouhavé modelování holých stěn ji zdržuje a odvádí od kreativní práce. Navíc nativní vyřezávání otvorů přes Boolean jí často zaneřádí síť ošklivou topologií, kterou pak musí před renderingem složitě čistit. Očekává proto nástroj podobný tužce, kterým podložený půdorys jednoduše obkreslí, a možnost vkládat otvory na jedno kliknutí s jistotou, že addon udrží topologii čistou.

==== 3. Level designer Denis

Denis (25 let) je vývojář v nezávislém herním studiu. Navrhuje herní úrovně a testuje pohyb hráče v prostoru. Primárně pracuje v herních enginech (Unreal Engine, Unity), přičemž Blender využívá k rychlé tvorbě takzvaných blockoutů — hrubé geometrie určené pro okamžité testování hratelnosti.

Jeho úkolem je v krátkém čase vybudovat rozsáhlou herní mapu (například spleť chodeb a místností), vyexportovat ji do enginu a projít si ji s herní postavou. Když při testování zjistí, že je chodba příliš úzká nebo strop příliš nízký, je úprava takové úrovně v čistém Blenderu (pokud je spojená do jednoho souvislého kusu geometrie) neefektivní a zdlouhavá. Od addonu proto vyžaduje robustnost a rychlost iterace: parametrický přístup by mu měl umožnit kliknout na chodbu, v panelu přepsat její šířku ze dvou metrů na tři, a nechat systém automaticky vyřešit zbytek. Nezbytností je pro něj také export, který po přesunu do enginu nerozbije fyzikální kolize.

== Vstupy a výstupy

FloorPlanMaster je navržen tak, aby dokázal reagovat na reálné pracovní situace: architekt často začíná s prázdnou scénou a úvodní myšlenkou, vizualizátorka dostane od klienta 2D půdorys ve formátu #gls("pdf", long: false) a game designér vychází z přibližných rozměrů v herním design dokumentu. Tato sekce jasně vymezuje, jaké formy vstupních dat addon zpracovává a jaké výstupy následně produkuje, čímž definuje hranice životního cyklu celého modelu.

=== Vstupy

Addon dokáže zpracovat tři základní kategorie vstupů. První kategorií jsou *2D podklady* — naskenované ruční skice, výkresy v #gls("pdf", long: false), obrázky půdorysů nebo importované 2D #gls("cad", long: false) výkresy (#gls("dxf", long: false)/#gls("dwg", long: false)), které uživatel potřebuje převést do 3D prostoru. Podkladový soubor se typicky umístí na pozadí scény a slouží jako vizuální reference pro následné obkreslování.

Druhou kategorií je *kvantitativní zadání* — přesný seznam požadavků od klienta nebo technické specifikace (např. „obývací pokoj musí mít minimálně 30 m²“ nebo „minimální šířka chodby jsou 2 metry“). Tyto hodnoty lze přímo zadávat do panelu nástroje jako číselné parametry.

Třetí kategorií je *volný návrh* — situace, kdy uživatel nemá žádné přesné podklady, začíná s prázdnou scénou a potřebuje nástroj, který ho nebude omezovat v rychlém a intuitivním skicování úvodních konceptů.

=== Výstupy

Výstupy z addonu se dělí do tří kategorií. Tou první je *3D hmotový model* — prostorová 3D reprezentace stěn, místností a otvorů, která slouží primárně k vizuální kontrole proporcí, tvorbě hmotových renderů, analýze osvětlení nebo k základní prezentaci klientovi. 

Druhou kategorií je *optimalizovaná geometrie pro export*. Jedná se o čistou topologickou síť (mesh) bez chyb nebo překrývajících se stěn, kterou může level designér okamžitě a bez dalších úprav vyexportovat (například do formátu #gls("fbx", long: false) nebo #gls("obj", long: false)) pro použití v herním enginu. 

Třetí a poslední kategorií jsou *prostorová a analytická data* — rychlá vizuální zpětná vazba pro uživatele. Zahrnuje automatické výpočty podlahové plochy jednotlivých místností a jasnou indikaci tloušťky stěn přímo v uživatelském rozhraní.

== Scénáře použití

Abstraktní požadavky typu „parametrické úpravy“ či „nedestruktivní workflow“ samy o sobě nedefinují, s jakou odezvou se musí stěna přepočítat po kliknutí myší, ani jak se systém zachová, když uživatel do scény přiloží #gls("pdf", long: false) výkres a začne jej obkreslovat. Tyto situace konkretizují až scénáře použití (Use Cases). Každý scénář sleduje konkrétní personu od jejího prvního kliknutí až po požadovaný výsledek a jasně odkrývá, které funkce modulu jsou pro daný úkol klíčové.

=== UC 1.1: Hmotová studie na základě stavebního programu

Architekt zadá do panelu nástroje požadovanou podlahovou plochu a poměr stran pro každou místnost (například 30 m², poměr 1:1,5). Addon automaticky vypočítá potřebné rozměry a vloží pravoúhlou místnost přímo do scény. Uživatel tento postup zopakuje pro všechny místnosti ze stavebního programu. Výsledkem je schematická dispozice, u níž lze v panelu okamžitě ověřit plochu každého prostoru.

=== UC 1.2: Kreslení dispozice tužkou

Architekt aktivuje kreslicí nástroj a pouhým klikáním bodů přímo ve 3D viewportu načrtne hrubou dispozici. Addon průběžně generuje stěny a při uzavření polygonu automaticky detekuje vzniklé místnosti. Uživatel následně doladí tloušťku a výšku stěn zadáním přesných hodnot v N-panelu.

=== UC 1.3: Kontrola rozměrů vůči normovým minimům

Architekt má navrženou dispozici a potřebuje ověřit, zda šířky chodeb a rozměry místností splňují minimální normové požadavky. V N-panelu zapne kótovací vrstvu (overlay). Addon prostřednictvím překreslovacího modulu (#gls("blf", long: false) draw handler) okamžitě zobrazí délky všech stěn a plochy místností přímo ve viewportu. Uživatel tak může vizuálně zkontrolovat kritická místa a případně upravit parametry stěn v panelu.

=== UC 2.1: Obkreslení dodaného 2D půdorysu

Vizualizátorka si na pozadí scény vloží referenční obrázek s půdorysem. Aktivuje kreslicí nástroj a se zapnutým přichytáváním (snapping) na existující uzly odklikává rohy místností přesně podle podkladu. Addon během kreslení průběžně generuje stěny a při uzavření cyklů automaticky detekuje jednotlivé místnosti. Výšku a tloušťku stěn následně hromadně nebo individuálně nastaví v N-panelu.

=== UC 2.2: Příprava modelu pro renderovací pipeline

Vizualizátorka vybere na existujícím půdorysu konkrétní stěnu a v N-panelu k ní přidá otvor zadáním přesných rozměrů (například 1500 × 1250 mm). Addon otvor dynamicky vyřízne pomocí logiky Geometry Nodes (Mesh Boolean). Při jakékoliv změně rozměrů v panelu se otvor okamžitě zaktualizuje. Po dokončení celé dispozice uživatelka spustí finalizační nástroj, který aplikuje všechny modifikátory, zpracuje #gls("uv", long: false) mapy a připraví čistou statickou síť (mesh) pro renderovací pipeline.

=== UC 2.3: Rychlá editace vlastností prvků přes kontextovou nabídku

Vizualizátorka potřebuje přiřadit různé materiály podlah jednotlivým místnostem, ideálně bez neustálého přepínání do postranních panelů. Klikne proto pravým tlačítkem myši na plochu místnosti ve viewportu. Vyvolaná kontextová nabídka zobrazí dostupné akce pro daný prvek. Uživatelka zvolí možnost „Změnit materiál podlahy“ a vybere odpovídající texturu. Stejným způsobem může místnost rovnou přejmenovat.

=== UC 3.1: Rychlý level blockout

Game designér aktivuje kreslicí nástroj a hrubě načrtne sérii navazujících místností. Soustředí se především na proporce a měřítko prostoru vůči hráčské postavě. Addon mezitím průběžně generuje stěny a detekuje vznikající místnosti. Uniformní výšku stěn pro celý půdorys designér následně nastaví v N-panelu.

=== UC 3.2: Finalizace a export herní úrovně

Na hotovém blockoutu přidá game designér dveřní otvory zadáním požadovaných parametrů v N-panelu u vybraných stěn. Zkontroluje podlahové plochy místností zobrazené v panelu a spustí finalizační nástroj. Ten aplikuje modifikátory Geometry Nodes, zkonvertuje atributy #gls("uv", long: false) map a připraví statickou geometrii pro bezproblémový export do herního enginu ve formátu #gls("fbx", long: false) nebo #gls("gltf", long: false).

=== UC 3.3: Interaktivní úprava rozložení místností

Game designér po herním testování (playtestingu) zjistí, že chodba mezi dvěma arénami je pro pohyb hráče příliš úzká. Vybere proto uzel na okraji chodby a pomocí 3D manipulátoru (gizmo) bod plynule posune v rovině XY. Addon automaticky udržuje planaritu a v reálném čase přepočítává sousední místnosti. Výslednou šířku chodby designér ověří čistě vizuálně ve viewportu, aniž by musel zadávat přesné číselné hodnoty.

== Analýza požadavků

Z definovaných person a scénářů použití vyplývá, že modul musí umožňovat interaktivní kreslení půdorysu, parametrickou úpravu stěn a otvorů, automatickou detekci místností i přípravu modelu pro další zpracování (rendering či nasazení v herním enginu). Ne všechny tyto funkce jsou však pro jednotlivé cílové skupiny stejně důležité. Tato sekce proto strukturovaně rozděluje zjištěné potřeby do sedmi funkčních a tří nefunkčních požadavků a ústí v prioritizační analýzu, která hodnotí váhu každého požadavku napříč cílovými skupinami.

=== Funkční požadavky

Následujících sedm funkčních požadavků pokrývá celý zamýšlený rozsah modulu – od interaktivního kreslení přes parametrickou správu prvků až po finalizaci modelu a integraci pomocných grafických vrstev.

==== FP1 — Interaktivní tvorba místností a kreslení (Pencil Tool)

Nástroj pro kreslení představuje primární vstup addonu. Umožňuje uživateli definovat půdorys klikáním bodů přímo ve 3D scéně. Jádrem je modální operátor, který po dobu kreslení přebírá veškerou interakci s myší a klávesnicí a průběžně generuje stěny.

Nezbytným minimem pro realizaci je kreslení půdorysu v pohledu shora a spolehlivá správa uživatelských vstupů modálním operátorem. Důležitým rozšířením je automatické přichytávání (snapping) k osám XY odvozené od vzdálenosti kurzoru k existujícím bodům či osám. Jako volitelné vylepšení se nabízí průběžné vykreslování náhledu budoucí stěny před jejím potvrzením – systém by neustále sledoval pozici kurzoru, kreslil vodicí linku a čekal na potvrzení uživatelem.

==== FP2 — Generování a úprava parametrických objektů

Tento požadavek definuje parametrické chování všech prvků půdorysu, tedy stěn i otvorů. Každý objekt si uchovává své parametry (délku, výšku, tloušťku, pozici v prostoru). Při jejich změně se automaticky přepočítá geometrie prvku a dynamicky se zaktualizuje poloha případných navázaných otvorů.

Základní implementace vyžaduje dynamickou reprezentaci stěn formou parametrického systému (nikoliv jako statickou síť), okamžitou aktualizaci geometrie při úpravě hodnot, zachování relativní pozice otvorů vůči stěně pomocí pevných datových vazeb a inteligentní generování ořezů (Boolean operací) přímo prostřednictvím Geometry Nodes.

==== FP3 — Správa prostoru a metadat

Správce prostoru tvoří sémantickou vrstvu nad obyčejnou 3D geometrií. Modul musí umět automaticky detekovat uzavřené cykly stěn, rozpoznat je jako samostatné místnosti a vypočítat jejich plochu. Jako volitelné rozšíření je koncipována hierarchizace prostorů – organizace místností a celých podlaží do přehledných kolekcí, které umožní například hromadné přepínání viditelnosti v projektu.

==== FP4 — Finalizační nástroj

Finalizační nástroj uzavírá nedestruktivní fázi návrhu. Po dokončení úprav převede parametrický systém na čistou, statickou 3D geometrii, která je připravená pro #gls("uv", long: false) mapování, export do herního enginu nebo nasazení v renderovací pipeline. Hlavním požadavkem je trvalá aplikace všech procedurálních generátorů a modifikátorů u vybraných objektů scény.

==== FP5 — Kontextová nabídka

Kontextová nabídka zpřístupňuje akce vázané na konkrétní prvek pomocí plovoucí uživatelské nabídky zobrazené přímo u kurzoru. Addon by měl využívat metodu vržení paprsku (raycast) k identifikaci cílového objektu a přes moduly #gls("gpu", long: false) nebo #gls("blf", long: false) vykreslovat vlastní rozhraní překrývající 3D viewport.

==== FP6 — Interaktivní 3D manipulátory

Interaktivní 3D manipulátory (gizma) nabízejí alternativu k ručnímu vypisování parametrů. Umožňují geometrickou manipulaci přímo v prostoru: uživatel uchopí barevné grafické táhlo u daného prvku a tažením myši plynule mění jeho rozměry nebo výšku. Implementace by měla využít nativní rozhraní `bpy.types.Gizmo` a `GizmoGroup`.

==== FP7 — Automatické kótování

Kótovací vrstva průběžně zobrazuje délky stěn a plochy místností jako dynamický text přímo ve viewportu, takže uživatel nemusí zjišťovat rozměry v postranních panelech. Texty generované modulem #gls("blf", long: false) přes překreslovací smyčku (draw handler) se musejí aktualizovat v reálném čase při každé změně dispozice.

=== Nefunkční požadavky

==== NP1 — Architektura a technologie

Výpočetní jádro modulu je postaveno na Geometry Nodes: logika generování a tvarování geometrie probíhá uvnitř uzlových stromů, zatímco Python plní roli správce, který tyto stromy propojuje a dynamicky upravuje jejich vstupy. Toto striktní oddělení vizuální a aplikační logiky je klíčovým architektonickým principem. Z hlediska distribuce nesmí modul vyžadovat ruční doinstalaci externích knihoven. Cílová platforma (Blender 4.2+) umožňuje definovat závislosti přímo v konfiguračním souboru `blender_manifest.toml`. Externí knihovny, jako například NetworkX využívaná pro grafové výpočty (detekce cyklů, planární embedding), tak budou zabaleny jako standardní Wheel soubory (`.whl`) a nainstalují se automaticky při aktivaci addonu.

==== NP2 — Výkon a nedestruktivní přístup

Systém musí reagovat naprosto plynule: uživatel si musí zachovat možnost interaktivní úpravy i při komplexnějších změnách půdorysu a souběžném překreslování geometrie. Hlavním architektonickým důrazem je zde minimalizace výpočetní náročnosti, optimalizace přepočtů parametrů a důsledné respektování grafu závislostí v Blenderu (DepsGraph) @blender_dev, aby nedocházelo k neefektivním cyklickým přepočtům celé 3D scény.

==== NP3 --- Použitelnost a #gls("ux", long: false) (Uživatelská zkušenost)

Uživatelské rozhraní modulu musí působit jako nativní součást Blenderu. Toho bude dosaženo konzistentním využíváním zabudovaných #gls("ui", long: false) komponent (např. `UILayout.row`) a logickým seskupováním nástrojů do přehledných záložek s vysvětlujícími popisky (tooltips). Důraz je kladen na ošetření chyb a srozumitelnou zpětnou vazbu při pokusu o neplatnou operaci – např. při snaze vložit velké okno do příliš krátké stěny.

=== Prioritizace požadavků

Následující tabulka mapuje každý funkční balíček na scénáře použití, které ho motivují.

#figure(
  table(
    columns: 10,
    align: center,
    table.header(
      [*Požadavek*], [*UC 1.1*], [*UC 1.2*], [*UC 2.1*], [*UC 2.2*], [*UC 3.1*], [*UC 3.2*], [*UC 1.3*], [*UC 2.3*], [*UC 3.3*],
    ),
    [FP1], [], [●], [●], [], [●], [], [], [], [],
    [FP2], [●], [●], [●], [●], [●], [●], [], [], [],
    [FP3], [●], [●], [●], [], [●], [●], [], [], [],
    [FP4], [], [], [], [●], [], [●], [], [], [],
    [FP5], [], [], [], [], [], [], [], [●], [],
    [FP6], [], [], [], [], [], [], [], [], [●],
    [FP7], [], [], [], [], [], [], [●], [], [],
  ),
  caption: [Mapování funkčních balíčků na scénáře použití (● = relevantní)],
) <tab-fp-uc>

Každý požadavek je hodnocen zvlášť každou cílovou skupinou (Vysoká / Střední / Nízká / Irelevantní) a výsledná priorita se určuje jako vážený průměr s koeficienty: architekti ×3, vizualizátoři ×2, game designéři ×1. Výsledný průměr ≥ 2,50 odpovídá prioritě Vysoká (must-have), rozmezí 2,50--1,75 prioritě Střední (should-have) a zbytek je hodnocen jako Nízká (nice-to-have) priorita. 

#figure(
  table(
    columns: (2fr, auto, auto, auto, auto, auto),
    align: (left, center, center, center, center, center),
    table.header(
      [*Požadavek*], [*Architekti*], [*Vizualizátoři*], [*Game Des.*], [*Průměr*], [*Priorita*],
    ),
    [FP1 --- Kreslení], [Vysoká], [Vysoká], [Vysoká], [3,00], [*Vysoká*],
    [FP2 --- Parametry], [Vysoká], [Vysoká], [Vysoká], [3,00], [*Vysoká*],
    [NP1 --- Architektura], [Vysoká], [Vysoká], [Vysoká], [3,00], [*Vysoká*],
    [NP2 --- Výkon], [Vysoká], [Vysoká], [Vysoká], [3,00], [*Vysoká*],
    [NP3 --- #gls("ux", long: false)], [Vysoká], [Vysoká], [Vysoká], [3,00], [*Vysoká*],
    [FP6 --- Manipulátory], [Střední], [Střední], [Nízká], [1,83], [Střední],
    [FP3 --- Prostory], [Vysoká], [Nízká], [Irelevantní], [1,83], [Střední],
    [FP7 --- Kótování], [Vysoká], [Nízká], [Irelevantní], [1,83], [Střední],
    [FP4 --- Finalizace], [Nízká], [Střední], [Vysoká], [1,67], [Nízká],
    [FP5 --- Kontext. nabídka], [Střední], [Nízká], [Nízká], [1,50], [Nízká],
  ),
  caption: [Vážená prioritizace požadavků podle cílových skupin],
) <tab-req-priority>

Tabulka nám v další kapitole návrhu poslouží jako výchozí bod pro určení definice minimálního funkčního produktu a jeho hranic. 

== Technická analýza

Funkční požadavky říkají _co_ má addon umět; technická analýza odpovídá na otázku _jak_ --- které části Blender #gls("api", long: false) to umožňují, jaké jsou jejich limity a kde hrozí designová nedostatky, které by ovlivnily celou architekturu. Klíčové otázky jsou, jak zachytit kreslení půdorysu v reálném čase bez ztráty výkonu, jak reprezentovat půdorys jako responsivní datový model schopný detekovat místnosti a reagovat na každou změnu stěny, a jak parametrické objekty převést do statické geometrie připravené pro export.

=== Architektura Blenderu

Blender je modulární systém postavený na unikátním způsobu správy dat --- dualitě systému #gls("dna", long: false) a #gls("rna", long: false). #gls("dna", long: false) (Blender's Data Architecture) definuje struktury C pro veškerá interní data scény, zatímco #gls("rna", long: false) (Runtime Notification Architecture) poskytuje reflexivní #gls("api", long: false), přes které Python přistupuje k těmto strukturám a reaguje na jejich změny @blender_dev_dna.

Blender využívá kombinaci vzoru #gls("mvc", long: false) (Model-View-Controller), která umožňuje oddělit uživatelské rozhraní (View) od vnitřní logiky (Model) a zpracování vstupů (Controller). Addony mohou definovat vlastní výpočty například v Geometry Nodes (Model), zatímco Blender se stará o jejich vykreslení do viewportu a zachytávání událostí myši přes Python #gls("api", long: false) @blender_dev.

=== Interaktivní kreslení a interakce ve viewportu

Plynulé kreslení stěny — sledování kurzoru, průběžná aktualizace náhledové linky a potvrzení kliknutím — vyžaduje zpracování každého z těchto kroků v rámci jednoho snímku. Tato sekce vysvětluje, jak Blender takovou interakci umožňuje přes modální operátory a stavový automat.
==== Modální operátory

Interaktivní kreslení ve viewportu stojí na modálních operátorech --- podtřídách `bpy.types.Operator` @blender_api_operator, které po spuštění zůstávají aktivní a naslouchají událostem myši a klávesnice. Na rozdíl od standardních operátorů, které vykonávají jednorázovou funkci a okamžitě skončí, modální operátor kontinuálně naslouchá událostem generovaným uživatelem nebo systémem. Je nezbytný pro plynulé kreslení, kdy systém průběžně sleduje polohu kurzoru a dynamicky na ni reaguje.

Inicializace operátoru začíná metodou `invoke()`, která připraví počáteční stav a registruje operátor do modálního handleru správce oken pomocí `context.window_manager.modal_handler_add(self)`. Od tohoto momentu je každá událost ve viewportu předávána metodě `modal()`. Návratové hodnoty `modal()` určují, jak Blender s událostí dále naloží:

#figure(
  table(
    columns: (auto, 1fr, 1fr),
    align: (left, left, left),
    table.header([*Hodnota*], [*Funkční dopad*], [*Architektonický význam*]),
    [`RUNNING_MODAL`], [Operátor pokračuje v běhu], [Plynulé tažení stěny nebo změna rozměru],
    [`PASS_THROUGH`], [Operátor běží, událost předána dál], [Zoomování a rotace pohledu během kreslení],
    [`FINISHED`], [Operátor končí, generuje Undo krok], [Finalizace a uložení stěny do databáze],
    [`CANCELLED`], [Operátor končí bez uložení], [Přerušení akce klávesou ESC],
  ),
  caption: [Návratové hodnoty modálního operátoru],
) <tab-modal-returns>

Metoda `modal()` funguje na principu stavového automatu, který umožňuje operátoru měnit chování v závislosti na fázi interakce. Stavový automat přináší tři klíčové výhody: řízení složitosti při implementaci vícekrokových nástrojů, možnost kontextového snappingu (v různých stavech jsou aktivní různé typy přichytávání) a optimalizaci výkonu --- složité operace se spouštějí pouze při přechodu mezi stavy, zatímco při pohybu myši se aktualizuje pouze drobná vizualizace.

// Pro kreslení půdorysu jsou typické stavy: `START` (čekání na první kliknutí), `DRAWING` (průběžné přepočítávání délky a úhlu stěny a vykreslování náhledové linky přes GPU modul), `EXTRUDING` (definování tloušťky nebo výšky) a `FINISHING` (zápis geometrie do scény a čištění draw handlerů).



// ==== Limity výkonu jazyka Python v programu Blender

// Python je v programu Blender interpretovaným jazykem, proto je potřeba náročné operace delegovat na stranu programu Blender nebo GPU využívající C++. Zkušenosti z vývoje komplexních generativních nástrojů ukazují, že čistý Python je při hromadném zpracování dat řádově pomalejší. V kontextu architektonického kreslení jsou hlavními limitujícími faktory iterace přes mesh data pomocí `for` smyčky, rostoucí počet unikátních objektů ve scéně a časté aktualizace DepsGraphu.

// K překonání těchto limitů se v profesionálních addonech využívají tři techniky. Metody `foreach_set` a `foreach_get` umožňují přenášet celá pole dat mezi jazykem Python a interními C++ strukturami v jedné operaci namísto nastavování každého vrcholu zvlášť. Delegování na modifikátory spočívá v tom, že Python vytvoří pouze základní čárový model a na něj aplikuje modifikátory jako Solidify nebo Bevel --- ty jsou implementovány v C++, plně využívají multithreading a jsou optimalizovány pro real-time aktualizaci. Geometry Nodes jako výpočetní backend pak umožňují jazyku Python pouze manipulovat se vstupními hodnotami uzlového stromu, zatímco veškerý výpočet geometrie probíhá v nativním kódu programu Blender.

=== Reprezentace geometrie

Přesná tloušťka v ostrých rozích, interaktivní odezva na změnu parametru a čistá topologie vhodná pro #gls("uv", long: false) mapování jsou tři protichůdné nároky, které ne každý přístup k reprezentaci geometrie splňuje najednou. Tato sekce analyzuje tři dostupné možnosti: imperativní BMesh, který nabízí maximální topologickou kontrolu za cenu výkonu; deklarativní Geometry Nodes, které výpočet přesouvají do nativního C++ jádra programu Blender; a hybridní přístup kombinující přesný výpočet geometrie v Pythonu s #gls("gn", long: false) jako vykreslovacím backendem.

Geometrie (poloha prvků v prostoru) a topologie (vzájemné vztahy a propojení) tvoří základní dualitu jakékoli 3D struktury. V programu Blender je základní jednotkou mesh složená z vrcholů, hran a ploch.

==== Datová struktura BMesh

BMesh je interní datová struktura programu Blender @blender_api_bmesh, která na rozdíl od tradičních struktur založených na trojúhelnících podporuje n-gony (polygony s více než čtyřmi vrcholy). 

// Využívá systém podobný half-edge datovým strukturám, kde jsou vztahy mezi plochami a hranami uloženy tak, aby umožňovaly rychlou navigaci po povrchu sítě.

Z pohledu parametrického modelování nabízí BMesh skrze Python #gls("api", long: false) (modul `bmesh`) nízkoúrovňový přístup k topologii --- možnost dotazovat se, které hrany jsou spojeny s daným vrcholem, a tím provádět operace jako dissolve bez poškození okolní topologie. Algoritmus pro generování stěn obvykle začíná načtením 2D hran, identifikuje uzavřené smyčky jako obrysy místností a operací tloušťky (offset) --- například přes `bmesh.ops.bevel` nebo posunem vrcholů podél normál hran --- vytváří 3D stěny. Tento proces je v Pythonu relativně pomalý a neumožňuje plynulou interaktivní odezvu, zejména při průběžné validaci integrity sítě. Na druhou stranu ale poskytuje absolutní kontrolu nad datovou strukturou a zaručuje bezchybnou, čistou topologii.

==== Geometry Nodes

Geometry Nodes (#gls("gn", long: false)) @blender_api zastupují deklarativní, paralelní přístup: uživatel definuje systém pravidel aplikovaných na celou geometrii současně. Data jsou reprezentována jako pole atributů vázaných na různé domény (vrcholy, hrany, plochy, instance), přičemž výpočet probíhá v nativním kódu C++ s plným multithreadingem.

Pro generování stěn se v #gls("gn", long: false) nejčastěji používá uzel `Curve to Mesh`. Klíčovou výzvou je Miter Joint problém @blender_curve_miter --- standardní vytažení profilu podél křivky vede ke ztenčení stěny v ostrých rozích. 
// Řešením je matematická korekce měřítka profilu v každém bodě křivky pomocí faktoru $f = 1 / sin(theta / 2)$, kde $theta$ je úhel mezi sousedními segmenty stěny. Tento výpočet se v GN realizuje pomocí vektorové matematiky (skalární součin pro výpočet úhlu) a ač je komplexnější na přípravu, umožňuje dynamicky měnit tloušťku stěn pouhým posunutím bodu v 2D půdorysu. 

Zásadní slabinou #gls("gn", long: false) je ovšem výsledná topologie. Zvláště po aplikaci booleovských operací (např. pro otvory oken a dveří) #gls("gn", long: false) často generují nepředvídatelnou, triangulovanou nebo nevhodnou n-gonovou síť, která silně komplikuje čisté #gls("uv", long: false) mapování a další manuální úpravy @blender_gn_boolean.

==== Hybridní přístup: Python quad-polygon a #gls("gn", long: false) extrude

Třetí možností je kombinace obou předchozích přístupů, kde Python řeší geometricky náročné výpočty a Geometry Nodes (#gls("gn", long: false)) fungují primárně jako vykreslovací backend. Důvodem je, že čistě programový ani čistě uzlový přístup nedokážou současně zajistit všechny tři úvodní požadavky: přesné napojení stěn, interaktivní odezvu i čistou topologii --- každý z nich má v určitém ohledu slabinu.

// Zvláštní pozornost je věnována rohům a křížení stěn pod různými úhly, kde by jednoduchý kolmý řez vytvářel mezery nebo nechtěné překryvy. Tento problém je řešen algoritmicky na straně Pythonu. Systém analyzuje všechny stěny v daném spoji, seřadí je podle úhlu odchozího směru a následně vypočítá přesné průsečíky jejich hran. Pro každou stěnu tak vznikne přesný 2D půdorys, který plně respektuje její osu a tloušťku. U složitějších spojů, jako jsou křížení ve tvaru T nebo X, algoritmus navíc generuje speciální výplňovou geometrii (_junction fill_), která spoj plynule uzavře a zabrání vzniku vizuálních děr v horní ploše křížení.

// Vypočítané půdorysy jsou následně zapsány do základní sítě modelu společně s potřebnými metadaty, jako je cílová výška stěn. Role stromu Geometry Nodes je díky tomu zredukována na minimalistickou a stabilní sadu operací: vyfiltrování příslušného půdorysu, jeho vytažení do 3D prostoru na základě předaných parametrů a následné vyříznutí otvorů pro architektonické prvky pomocí booleovských operací.

Zásadní výhodou tohoto řešení je, že úspěšně uzavírá pomyslný trojúhelník nároků definovaný v úvodu. Generování 2D půdorysů a spojů čistě v Pythonu zajišťuje naprostou přesnost tloušťky i čistou quad topologii, přičemž oddělenou logiku lze spolehlivě ověřovat pomocí standardních automatizovaných testů. Následné delegování 3D extruze na C++ jádro #gls("gn", long: false) zase poskytuje potřebný výkon pro rychlou interaktivní odezvu při úpravách. Nevýhodou je naopak o něco náročnější implementace synchronizační vrstvy. Přenos vypočítaných vlastností z Pythonu do Geometry Nodes vyžaduje pečlivou správu dat a obcházení určitých limitací při zápisu interních atributů sítě. Celkové srovnání analyzovaných přístupů napříč klíčovými technickými parametry shrnuje @tab-bmesh-gn.

#figure(
  table(
    columns: (1.5fr, 1fr, 1fr, 1fr),
    align: (left, left, left, left),
    table.header([*Charakteristika*], [*BMesh*], [*Geometry Nodes*], [*Hybridní*]),
    [Způsob práce], [Iterativní / Imperativní], [Paralelní / Deklarativní], [Python geometrie + #gls("gn", long: false) render],
    [Výkon], [Omezený interpretací Pythonu], [Vysoce optimalizované C++], [Python sync odložen na konec seance],
    [Topologická flexibilita], [Absolutní], [Omezená na definované uzly], [Plná (Python vrstva)],
    [Vizuální odezva], [Po spuštění skriptu], [Real-time ve viewportu], [#gls("gpu", long: false) preview per-click; full sync na konci],
    [Přesnost spojů], [Přesné, výpočetně drahé], [Vyžaduje manuální korekci], [Přesné (angular sort)],
    [Multithreading], [Ne (omezení #gls("gil", long: false)u)], [Ano (nativní)], [#gls("gn", long: false) část ano; Python část ne],
    [Testovatelnost], [Omezená (závislost na bpy)], [Obtížná], [Plná (čistý Python, bez bpy)],
    [Implementační složitost], [Střední], [Nízká], [Vysoká (sync vrstva)],
  ),
  caption: [Srovnání přístupů k reprezentaci geometrie stěn],
) <tab-bmesh-gn>

=== Datový model

Samotná 3D síť (mesh) sice přesně zachycuje tvar a polohu stěn v prostoru, ale nenese žádné sémantické informace o prostorech samotných --- nemá jak zjistit, zda spolu dvě místnosti sousedí, jaký mají účel nebo jaké jsou jejich parametry. Parametrický modul, jehož úkolem je automaticky detekovat místnosti, počítat jejich podlahové plochy a dynamicky reagovat na každou topologickou změnu, proto nevyhnutelně vyžaduje dedikovanou datovou vrstvu. Tato sekce analyzuje možné přístupy k její reprezentaci.

==== Reprezentace bez samostatné datové vrstvy

Nejjednodušší možný přístup vůbec nevytváří oddělenou datovou strukturu: půdorys je uložen výhradně v geometrii Blenderu a veškerá sémantická data jsou vázána přímo na konkrétní prvky sítě pomocí uživatelských vlastností (Custom Properties) nebo pojmenovaných atributů (Named Attributes). V takovém modelu představují hrany sítě stěny a jednotlivé polygony (faces) tvoří místnosti.

Hlavní výhodou je jednoduchost --- řešení nevyžaduje žádné externí knihovny a nabízí přímou kompatibilitu s modifikátory Geometry Nodes, které umějí pojmenované atributy číst v reálném čase. Zásadní nevýhodou je však velmi nízká efektivita dotazování. Hledání odpovědí na otázky typu „sousedí místnost A s místností B?“ nebo „kolik místností je dostupných z hlavní haly?“ vyžaduje iterativní procházení celé topologie sítě s časovou složitostí $O(E)$ pro každý jednotlivý dotaz.

==== Lineární datové struktury

Druhý přístup udržuje aplikační stav v Pythonu pomocí plochých seznamů nebo slovníků. Eviduje uzly (styky stěn), stěny a místnosti jako samostatné objekty. Každý prvek má přiřazen jednoznačný identifikátor (ID) a informace o sousednosti je uložena přímo v záznamu daného prvku jako seznam ID jeho sousedů.

Tato varianta je plně implementovatelná pomocí standardních knihoven Pythonu a lze ji snadno testovat i nezávisle na programu Blender. Jejím hlavním limitem je však rychlé snížení výkonu při složitějších topologických operacích. Například automatická detekce nově vzniklých místností (uzavřených cyklů) by vyžadovala implementaci vlastních algoritmů pro prohledávání grafu a výpočetní náročnost při opakovaném přepočítávání sousednosti by expocencionálně rostla s každým novým prvkem.

==== Grafová reprezentace

Z matematického hlediska je nejpřirozenějším modelem půdorysu neorientovaný planární graf @hu2024gsdiff, kde uzly ($V$) odpovídají stykům stěn a hrany ($E$) představují osy samotných stěn. Tento formát otevírá cestu k využití standardních, vysoce optimalizovaných grafových algoritmů: od detekce minimálních cyklů (místností), přes ověřování planarity, až po výpočty dostupnosti. Pro Python navíc existuje robustní knihovna NetworkX @networkx, která všechny tyto operace nativně implementuje a umožňuje jejich testování zcela nezávisle na Blenderu.

Hlavním architektonickým rozhodnutím při použití grafové reprezentace je hloubka struktury modelu: tedy zda zachovat jeden sjednocený graf kombinující topologii se sémantikou (uzly nesou jak geometrické souřadnice, tak metadata místnosti), nebo striktně oddělit topologický skelet (uzly = spoje stěn, hrany = osy stěn) od sémantického grafu (uzly = místnosti, hrany = sousedství). Sjednocený graf je jednodušší na průběžnou správu. Oddělené vrstvy sice vyžadují synchronizaci, ale mnohem lépe izolují zodpovědnosti jednotlivých domén. Rozdíl ve výkonu je zde markantní: zatímco v čistě topologickém grafu má zjištění sousednosti dvou místností složitost $O(E)$, v explicitním sémantickém grafu jde o triviální dotaz se složitostí $O(1)$.

S grafovou reprezentací úzce souvisí i strategie automatické detekce místností při uzavírání stěnových cyklů, jíž se detailně věnuje následující podkapitola.

==== Způsoby detekce místností

Pro detekci místností existují dva přístupy. _Eager_ přístup ihned při vzniku stěny vytváří dočasný objekt místnosti, který je při uzavření cyklu validován. Toto vede k řadě problémů: nedefinovanému stavu dočasného objektu, konfliktu při slučování po uzavření cyklu (systém musí vybrat, který dočasný objekt zachovat), problémům se simultánním uzavřením více cyklů a složité vlastní správou Undo historie.

_Lazy_ přístup naproti tomu vytváří místnost výhradně tehdy, kdy je detekován uzavřený cyklus v strukturálním grafu. Invariant `Room ↔ minimální uzavřený cyklus` platí vždy a plně --- neexistuje žádný stav „rozpracované místnosti". NetworkX vrátí seznam všech nových minimálních cyklů najednou, pro každý vznikne jeden Room node bez spojovací logiky. Undo je přirozené: odebrání uzavírající stěny znamená zánik cyklu a zánik Room nodu. Lazy detekce zajišťuje determinismus --- stejná topologie spojů a stěn vždy produkuje stejnou sématiku místností bez závislosti na pořadí editací.

=== Tvorba otvorů pro okna a dveře

Nedestruktivní přístup k otvorům předpokládá, že pohyb stěny automaticky přesune i zabudované okno, změna tloušťky ho přizpůsobí a aktualizace parametrů otvor okamžitě regeneruje --- bez jakéhokoli ručního zásahu. Splnit ji lze více způsoby, přičemž každý nabízí jiný kompromis mezi výkonem, numerickou stabilitou a topologickou čistotou výsledné geometrie. Tato sekce porovnává následující tři hlavní přístupy jak zmíněnou podmínku splnit:

_Boolean operace spravované přes Python #gls("api", long: false)_ využívají standardní modifikátorový stack, kde Python dynamicky vytváří cutter objekty a přiřazuje je ke stěně. Hlavní nevýhodou je vysoká režie při správě stacku s desítkami modifikátorů a numerická nestabilita --- pokud souřadnice po transformaci nejsou binárně identické (kvůli zaokrouhlení floatů), `Exact` solver může selhat při detekci společných ploch.

_Mesh Boolean v Geometry Nodes_ nahrazuje objektový stack jedním uzlovým stromem, kde operace probíhají nad toky geometrických dat. Na rozdíl od modifikátorů, které pracují v párech, uzel Mesh Boolean v #gls("gn", long: false) dokáže zpracovat celé kolekce instancí oken jako jeden sloučený vstup --- to dramaticky snižuje počet reevaluací. Problémem je, že solver považuje vše zapojené do vstupu za jediné těleso; pokud se dvě stěny překrývají, může dojít ke vzniku dutých výsledků @blender_gn_boolean.

_Metody bez Boolean operací_ se vyhýbají výpočtům průsečíků a otvory vkládají přímo do procesu generování topologie. Curve Trimming ořízne vodicí křivku před vytažením do 3D, čímž vzniknou fyzické mezery s čistou topologií --- tato metoda však vyžaduje reprezentaci stěn jako Blender Curve objektů a není kompatibilní s architekturou pracující s base meshem a Named Attributes. Modulární instancování chápe stěnu jako pole buněk s plnými nebo prázdnými moduly. Vertex Group Topology označí specifické vrcholy atributem `is_window` a #gls("gn", long: false) je posunou aby vytvořily pravoúhlý otvor.

Následující tabulka zobrazuje hlavní rozdíly mezi zmíněnými přístupy:
#figure(
  table(
    columns: (1fr, 1fr, 1fr, 1fr),
    align: (left, left, left, left),
    table.header(
      [*Parametr*], [*#gls("api", long: false) Modifikátory*], [*#gls("gn", long: false) Mesh Boolean*], [*Curve Trimming*],
    ),
    [Výpočetní složitost], [$O(n times m)$], [$O(m log m)$], [$O(n)$],
    [Numerická stabilita], [Nízká (float drift)], [Střední], [Absolutní],
    [Topologický výstup], [Artefakty, n-gony], [n-gony, nutný cleanup], [Perfektní quads],
    [Flexibilita], [Vysoká], [Vysoká], [Omezená],
  ),
  caption: [Srovnání metod pro tvorbu otvorů ve stěnách],
) <tab-holes>

=== Ukládání dat a správa metadat

Parametrický addon pracuje s daty na dvou odlišných úrovní: s geometrií stěn, která musí přežít každý zpětný (Undo) krok, i s metadaty místností --- jejich názvem, typem a plochou --- která musí zůstat konzistentní při sdílení souborů nebo instancování objektů. Tato sekce analyzuje, které mechanismy Blender #gls("api", long: false) pro tato data nabízí, na které úrovni hierarchie programu Blender je přirozeně ukládat a jak zajistit, aby grafové struktury v paměti přežily uložení a opětovné otevření `.blend` souboru.

==== Systémy pro správu uživatelských parametrů

Blender nabízí dva hlavní mechanismy. *Vlastnosti ID* (Custom Properties) @blender_api_props jsou flexibilní mechanismus pro připojování libovolných dat k jakémukoliv datovému bloku --- ukládají celá čísla, desetinná čísla, řetězce a pole. Pro komplexní architektonické systémy mají nedostatky: absenci striktní typové kontroly a omezené možnosti definice logiky při změně hodnoty. *Modul `bpy.props`* @blender_api_props umožňuje definovat vlastnosti registrované přímo do systému #gls("rna", long: false) s plnou podporou zpětných volání (`update`, `get`, `set`), klíčových pro reaktivní architektonické prvky.

Pro správu informací o prostorech (název, plocha, typ místnosti, výška) je optimálním vzorem `bpy.types.PropertyGroup`, který seskupuje souvísející parametry do logického celku připojeného k datovému bloku pomocí `PointerProperty` (vazba 1:1) nebo `CollectionProperty` (vazba 1:N).

// ==== Vazby dat na úrovně hierarchie Blenderu

// Rozhodnutí, na jakou úroveň hierarchie Blenderu budou metadata uložena, má hluboké důsledky pro stabilitu addonu a chování při Undo/Redo.

// Úroveň *Scéna* (`bpy.types.Scene`) je vhodná pro globální parametry projektu. Data specifická pro jednotlivé místnosti jsou na této úrovni nevhodná: smazání objektu ve viewportu nezpůsobí automatické smazání metadat v kolekci, což vede k hromadění dat. Úroveň *Objekt* (`bpy.types.Object`) nese informace o transformaci a viditelnosti. Komplikace nastávají při instancování: vytvoření instance přes Alt+D vytvoří dva objekty sdílející stejná geometrická data, ale s unikátními daty na úrovni Object --- změna rozměru jednoho okna by se neprojevila u ostatních instancí. Úroveň *Geometrie* (`bpy.types.Mesh`) je nejvhodnějším přístupem pro architektonické prvky: mesh reprezentuje „definici typu" prvku a všechny sdílené instance mají identické parametry, v souladu s principy BIM.

==== Perzistence grafových dat

Blender při uložení `.blend` souboru automaticky ukládá mesh geometrii a Custom Properties objektů --- Python objekty v paměti (např. NetworkX grafy) nikoli @blender_dev. Po zavření a opětovném otevření souboru jsou grafy ztraceny, pokud nejsou zachovány.

#figure(
  table(
    columns: (auto, 1fr, 1fr),
    align: (left, left, left),
    table.header([*Přístup*], [*Princip*], [*Hlavní nevýhoda*]),
    [#gls("json", long: false) v Custom Property], [Serializovat grafy do #gls("json", long: false) stringu], [Redundance; nutno verzovat schéma],
    [Pickle v Custom Property], [Serializovat Python objekty do bajtů], [Bezpečnostní riziko; citlivost na verze],
    [Rekonstrukce z meshe], [Po načtení přebudovat grafy z uložené topologie], [Mesh musí být jediným zdrojem pravdy],
  ),
  caption: [Přístupy k perzistenci grafových dat v Blenderu],
) <tab-persistence>

==== Perzistence globálních nastavení addonu

Addon spravuje dvě kategorie nastavení. *Projektová data* (výchozí tloušťka stěny, výška, systém jednotek) přímo ovlivňují geometrii konkrétního půdorysu. *Nastavení chování addonu* (výkon, cesty k souborům, #gls("ui", long: false) preference) jsou naopak nezávislá na projektu.

Pro každou kategorii nabízí Blender jiný mechanismus: `bpy.types.AddonPreferences` ukládá data globálně do `userpref.blend` (platí napříč projekty), zatímco `bpy.types.PropertyGroup` na `Scene` ukládá data per-projekt do aktuálního `.blend` souboru. Analýza existujících addonů ukazuje, že oba hlavní architektonické addony (Archimesh @archimesh, Archipack @archipack) projektová data do `AddonPreferences` neukládají --- ten rezervují výhradně pro chování addonu. Pro FloorPlanMaster je proto optimálním řešením *Scene PropertyGroup* se zapečenými výchozími hodnotami: projektové hodnoty jsou součástí `.blend` souboru, jsou tedy přenositelné a verzovatelné s projektem. `AddonPreferences` se použijí výhradně pro nastavení nesouvisející s konkrétním projektem.

=== Uživatelské rozhraní

Architekt, který musí odtrhnout pohled od půdorysu, aby v postranním panelu dohledal tlačítko, ztrácí soustředění právě ve chvíli, kdy je nejcennější. Dobrý #gls("ui", long: false) addon proto nesmí nutit uživatele hledat --- parametry stěny se musí zobrazit samy při jejím výběru, délky stěn musí být čitelné přímo ve viewportu a editace hodnotou i tažením myši musí být dostupné ze stejného místa. Tato sekce popisuje, jaké mechanismy Blender #gls("api", long: false) pro takové rozhraní nabízí a jaké #gls("ui", long: false) vzory se v existujících architektonických nástrojích opakují a proč.

#gls("ui", long: false) systém Blenderu je postaven na principu Immediate Mode rendering @blender_dev --- rozhraní se kompletně překresluje při každém snímku nebo změně. Logika určující, co se má zobrazit, musí být extrémně rychlá; výhodou je flexibilita --- rozhraní vždy dokonale odráží aktuální stav bez synchronizace. Prostor obrazovky je hierarchicky členěn: Screen (celé hlavní okno), Area (obdélníkové oblasti) a Region (specifické části každé oblasti, v 3D Viewportu to jsou hlavní 3D zobrazení, Sidebar, Header a Toolbar). K propojení #gls("ui", long: false) s daty scény slouží #gls("rna", long: false) systém: data v rozhraní jsou pouze vizuálním ukazatelem do datových struktur C++ jádra a uživatelská změna hodnoty se okamžitě propíše přes #gls("rna", long: false) přímo do databáze scény.

==== #gls("gpu", long: false) modul a draw handlery

Modul `gpu` @blender_api_gpu slouží jako abstrakční vrstva nad nízkoúrovňovými grafickými #gls("api", long: false) (OpenGL, Metal, Vulkan) a je pro architektonický addon klíčový: umožňuje vykreslovat vodící linky, kóty a náhledy stěn přímo na #gls("gpu", long: false) bez nutnosti vytvářet geometrii v databázi Blenderu. Draw handlery se registrují k `bpy.types.SpaceView3D` metodou `draw_handler_add`. Existují dva hlavní režimy: `POST_VIEW` pracuje v souřadném systému 3D scény (ideální pro vodící linky) a `POST_PIXEL` pracuje v souřadnicích obrazovky a je nezbytný pro textové popisky a kóty, které mají zůstat čitelné nezávisle na míře přiblížení. Každý přidaný handler musí být při ukončení operátoru odstraněn pomocí `draw_handler_remove()`.

Pro kótovací popisky lze použít modul #gls("blf", long: false) @blender_api_blf (Blender Font Library), který vykresluje text přímo do viewportu s možností kontroly nad pozicí a vzhledem. Pro kótovací overlay je rozhodující čitelnost nezávislá na úhlu pohledu --- #gls("gpu", long: false) `POST_PIXEL` overlay tuto podmínku splňuje; alternativní přístup s #gls("gn", long: false) String to Curves generuje 3D mesh textu, který je při šikmém pohledu hůře čitelný.

==== #gls("ui", long: false) vzory v architektonických nástrojích

Analýza existujících řešení odhalila opakující se #gls("ui", long: false) vzory, které cílová uživatelská skupina již ovládá. *Sidebar / Properties panel* --- parametry vybraného objektu jsou trvale viditelné v postranním panelu; Archipack posouvá tento vzor dál automatickým zobrazením parametrů v N-panelu při výběru objektu bez nutnosti klikat na tlačítko @archipack. *Gizmo při výběru (Auto-manipulate on select)* --- při výběru stěny se automaticky zobrazí táhla pro tloušťku a výšku, vhodné pro geometrické úpravy tažením myši. *#gls("hud", long: false) během modálního nástroje* --- aktuální hodnoty a nápověda kláves zobrazeny přímo ve viewportu, nezbytné pro nástroje s více stavy. *Kontextová nabídka na #gls("rmb", long: false)* --- přístup k méně frekventovaným akcím (přejmenování, smazání, nastavení materiálu) je primární #gls("ui", long: false) konvencí Blenderu; nabídka je závislá na vybraný prvek, čímž redukuje vizuální šum. *Pop-over dialog* --- otevírá se u kurzoru, poskytuje prostor pro textový vstup nebo výběr z enumu a zavře se kliknutím mimo bez nutnosti potvrzení. *Jednoznakové zkratky* --- odpovídající prvnímu písmenu akce nebo ustálené konvenci prostředí, snižují latenci opakovaných akcí bez přepnutí pohledu na toolbar.

=== Finalizační nástroj

Parametrický model je neustále se měnící systém, ale renderovací a herní enginy potřebují přesný opak: čistou a statickou geometrii (mesh) se správnými #gls("uv", long: false) mapami a bez zbytečných materiálů. 

Úkolem finalizačního nástroje je převést procedurální objekt na topologicky čistou síť. Je naprosto klíčové to provést tak, abychom si původní, dál editovatelný model nezničili. Běžný postup postupného aplikování modifikátorů přes `modifier_apply()` je riskantní, protože v průběhu mění indexy těch zbývajících. Mnohem spolehlivější je proto využití vyhodnoceného grafu závislostí (DepsGraph). 

Pomocí metody `evaluated_get()` @blender_api si načteme aktuální, vyhodnocený stav objektu (tedy stav po aplikaci všech modifikátorů a Geometry Nodes). Z něj pak voláním `bpy.data.meshes.new_from_object()` vygenerujeme zcela novou statickou síť. Původní parametrický objekt tak zůstane beze změny ukrytý ve scéně pro případné další úpravy.

Během tohoto procesu je nutné ohlídat dvě hlavní technické komplikace:

- *#gls("uv", long: false) mapy:* V Geometry Nodes se #gls("uv", long: false) data ukládají jen jako 2D vektory v rozích polygonů (doména _Face Corner_). Standardní exportéry (jako #gls("fbx", long: false) nebo #gls("gltf", long: false)) by je v této podobě ignorovaly, takže je skript musí explicitně převést na klasické #gls("uv", long: false) vrstvy.
- *Duplicitní materiály:* Slučování instancí často nabaluje duplicitní materiálové sloty. V herních enginech by tento balast zbytečně zvyšoval počet vykreslovacích požadavků (_draw calls_). Skript proto musí pomocí modulu BMesh zanalyzovat existující sloty, přemapovat indexy materiálů na samotných polygonech a následně všechny prázdné nebo nadbytečné sloty z objektu odstranit.


#pagebreak()
= Návrh <chap-design>

Tato kapitola převádí FloorPlanMaster do realizovatelného technického návrhu: vymezuje přesné hranice #gls("mvp", long: false), aby bylo jasné, které části (kreslení stěn, detekce místností, parametrické otvory, finalizace meshe) tvoří jádro první verze a které prvky zůstávají odloženy. Následně definuje třívrstvou architekturu, v níž strukturální graf drží topologii stěn a junctions, graf místností odvozuje semantiku uzavřených cyklů a synchronizační vrstva zapisuje data do pojmenovaných atributů meshe pro Geometry Nodes. Návrh dále konkretizuje datové entity a jejich vazby (Junction, Wall, Room, Adjacency), způsob propagace změn od uživatelské akce po přegenerování geometrie, pravidla práce operátorů a podobu rozhraní ve viewportu i panelech. Závěr kapitoly ověřuje konzistenci návrhu vůči scénářům použití a připravuje podklad pro implementaci bez doplňování chybějících rozhodnutí.

== Definice rozsahu #gls("mvp", long: false)

Funkční požadavky FP1 až FP7 identifikované v analýze (@tab-req-priority) pokrývají kompletní workflow od prvního načrtnutí dispozice až po finální export pro herní engine či renderovací pipeline. Tato sekce zavádí MoSCoW prioritizaci jako filtr: musí být zcela jasné, které dílčí prvky tvoří nezbytné jádro #gls("mvp", long: false), které jsou hodnotnou, ale volitelnou nadstavbou a které lze realizovat až v pozdějších iteracích. Toto rozlišení prostupuje celým návrhem a v každé z následujících sekcí je každá funkce explicitně označena svou prioritou.

#gls("mvp", long: false) realizuje kompletní workflow jednoho podlaží: interaktivní kreslení stěn, automatickou detekci místností, parametrické otvory a finalizaci do statické geometrie. Must-have prvky tvoří minimální sadu, bez níž addon nesplňuje základní účel a nemůže být nasazen.

#figure(
  table(
    columns: (auto, 2fr, 2fr),
    align: (left, left, left),
    table.header(
      [*Požadavek*], [*Must-have základ*], [*Odložené prvky*],
    ),
    [FP1], [Kreslení bodů klikáním v top view; modální operátor; preview stěny], [Snap na osu, mřížku a úhel; pokročilý #gls("gpu", long: false) overlay],
    [FP2], [Dynamické parametry stěny; update geometrie; vazba otvorů; #gls("gn", long: false) Mesh Boolean], [Napojení místnosti na existující půdorys],
    [FP3], [Automatická detekce uzavřených místností; zobrazení plochy], [Hierarchizace místností],
    [FP4], [Finalizace --- aplikace #gls("gn", long: false) modifikátoru, konverze #gls("uv", long: false), konsolidace materiálů], [---],
    [FP5], [---], [Kontextová nabídka a raycast elementů (nice-to-have)],
    [FP6], [---], [Interaktivní 3D manipulátory (should-have)],
    [FP7], [---], [Automatické kótování (should-have)],
  ),
  caption: [MoSCoW prioritizace prvků FP1--FP7; must-have prvky tvoří jádro #gls("mvp", long: false)],
) <tab-mvp-scope>

Ačkoliv požadavek FP4 byl identifikován jako prvek s nízkou prioritou, pro game designery by add-on bez této funkce nedával smysl a proto byl zařazen do kategorie must-have. 

Záměrně vyloučeny z celého rozsahu návrhu jsou: více podlaží a hierarchie budov, import a export formátů #gls("dxf", long: false) a #gls("ifc", long: false), generování střech a schodišť a napojení nové místnosti na existující geometrii při vkládání z parametrů. Tato omezení nejsou chybami návrhu --- architektura je na tato rozšíření připravena, avšak jejich detailní specifikace je v této fázi záměrně odložena do navazujících iterací jako budoucí rozšiřující funkčnost.

== Architektura systému

Analýza odhalila klíčový problém: Blender @blender jako obecný 3D nástroj zná geometrické primitivy --- vrchol, hranu, plochu --- ale nezná stěnu, junction ani místnost. Bez sémantické vrstvy by každý objekt v scéně byl pouhým seskupením polygonů bez doménového kontextu a jakákoli změna půdorysu by vyžadovala manuální přepočítání okolní geometrie. Architektura add-onu FloorPlanMaster tuto mezeru zaplňuje oddělením sémantické logiky v Pythonu od vizualizace v Blenderu: Python vlastní veškeré znalosti o stěnách, místnostech a jejich vztazích; Blender slouží výhradně jako zobrazovací engine. Analogický přístup volí Revit @revit, ArchiCAD @archicad a FreeCAD Arch @freecad --- jsou postaveny na obecném geometrickém jádru, ale přidávají nad ním sémantickou vrstvu entit (stěna, místnost, podlaží) s vlastními omezeními a vztahy.

=== Proč oddělená sémantická vrstva

Oddělení sémantiky od Blender dat není pouze implementační preference, ale vědomé architektonické rozhodnutí. Jádro problému spočívá v tom, že požadované operace addonu (detekce cyklů místností, stabilní identita stěn při editaci, validace topologie, sousednosti mezi místnostmi) jsou primárně grafové a relační, zatímco Blender mesh je primárně geometrická reprezentace optimalizovaná pro zobrazení a modelovací operace. Pokud by sémantika vznikala jen "zpětným čtením" z meshe, každá složitější editace by vyžadovala opakovanou rekonstrukci doménových vztahů z vrcholů, hran a ploch.

V prostředí Blenderu existují i alternativní cesty, jak sémantiku řešit:

#figure(
  table(
    columns: (1.35fr, 2.35fr, 2.35fr),
    align: (left, left, left),
    table.header([*Přístup*], [*Hlavní výhody*], [*Hlavní omezení*]),
    [Bez samostatné sémantické vrstvy (mesh-first)], [Jednodušší datový tok; jeden zdroj dat přímo v geometrii; přirozená vazba na Undo/Redo a uložení `.blend`], [Složitá a výpočetně náročná rekonstrukce významu z topologie; obtížná stabilita identit při změnách; slabší testovatelnost mimo Blender],
    [Oddělený Python model + synchronizace do meshe (zvolený)], [Přirozené vyjádření grafových vztahů; čisté #gls("api", long: false) modelu; jednotkové testy bez Blenderu; predikovatelné chování při evoluci funkcí], [Nutnost navrhnout robustní synchronizaci a perzistenci; vyšší implementační složitost; riziko desynchronizace při chybách v bridge vrstvě],
  ),
  caption: [Alternativy reprezentace sémantiky v Blender addonu a jejich trade-offy],
)

Zvolená architektura tedy nepředpokládá, že ostatní varianty jsou "špatně"; pouze přesouvá optimalizační cíl od krátkodobé jednoduchosti k dlouhodobé konzistenci doménového modelu. Nevýhody zvoleného směru (synchronizační režie, potřeba explicitní perzistence a rekonstrukce) jsou přijaty záměrně, protože umožňují stabilní rozvoj funkcí nad stejným modelem dat i v dalších iteracích (více podlaží, nové typy prvků, exportní adaptéry) bez nutnosti měnit základní princip architektury.

=== Třívrstvá hybridní architektura <sec-design-architecture>

Jádrem návrhu je architektura, která striktně odděluje výpočetní logiku od vizualizace. Celý systém je postaven na třech specializovaných vrstvách: první dvě jsou implementovány výhradně v jazyce Python a zajišťují topologii a sémantiku půdorysu, zatímco třetí vrstva slouží jako jednosměrný most do vykreslovacího jádra programu Blender.

==== Vrstva 1: Topologický základ půdorysu

*Vrstva 1* (strukturální graf) tvoří primární strukturu dispozice. Definuje počáteční a koncové body stěn, jejich vzájemné návaznosti a hlavní parametry. Díky tomu systém neustále pracuje s jednoznačně určenou strukturou dispozice a dokáže zajistit, že nedochází k nekonzistencím v geometrickém uspořádání stěn. Detailní datový model první vrstvy je popsán v kapitole 3.3.

==== Vrstva 2: Sémantický graf místností

*Vrstva 2* (sémantický graf místností) je přímo odvozena z první vrstvy. Jakmile stěny vytvoří uzavřený prostor, systém jej automaticky detekuje jako místnost a průběžně vypočítává její základní parametry, jako jsou celková plocha a obvod. Každá místnost disponuje trvalým identifikátorem a uživatelsky definovaným názvem, což umožňuje její spolehlivou identifikaci i během následných úprav dispozice. Sdílejí-li dvě místnosti společnou stěnu, systém tuto vazbu eviduje jako sousednost, čímž jasně mapuje vzájemné propojení jednotlivých prostorů.

==== Vrstva 3: Synchronizační most

*Vrstva 3* (synchronizační most) transformuje data z předchozích dvou vrstev do formátu, který Blender využívá pro zobrazení a další manipulaci s modelem. Datový tok je striktně jednosměrný: nejprve se plně zpracuje logika půdorysu a místností a teprve poté se tyto informace promítnou do výsledné geometrie. Tento postup zaručuje, že vizuální výstup vždy koresponduje s aktuálním stavem návrhu, čímž se předchází jakýmkoli rozporům mezi datovým modelem systému a tím, co reálně vidí uživatel.

// === Dynamika systému --- tok dat

// Komunikace mezi vrstvami je striktně jednosměrná: Vrstva 1 → Vrstva 2 → Vrstva 3 → Geometry Nodes. Zpětný tok neexistuje --- Blender mesh je vždy odrazem aktuálního stavu grafů, nikoli jejich výchozím bodem. Toto jednosměrné uspořádání eliminuje cyklické přepočty a zaručuje konzistenci dat: žádná operace v Blenderu nemůže nepozorovaně změnit stav grafů. Přidání stěny spouští kompletní řetězec (Vrstva 1 → Vrstva 2 → Vrstva 3 fáze 1 → fáze 2 → GN reevaluace); parametrická změna spouští pouze fázi 2 sync, protože topologie mesh se nemění. Následující diagramy zobrazují názorný tok dat v rámci návrhnutého modelu u častých uživatelských operacích:

// #figure(
//   image("/typst/assets/add_edge_diagram.png", width: 80%),
//   caption: [Tok dat: Přidání stěny],
// ) <fig-toolbar>

// #figure(
//   image("/typst/assets/add_room_diagram.png", width: 80%),
//   caption: [Tok dat: Přidání místnosti / uzavření cyklu],
// ) <fig-toolbar>

// #figure(
//   image("/typst/assets/remove_edge_diagram.png", width: 80%),
//   caption: [Tok dat: Odstranění stěny],
// ) <fig-toolbar>

// #figure(
//   image("/typst/assets/change_attribute_diagram.png", width: 80%),
//   caption: [Tok dat: Změna atributu],
// ) <fig-toolbar>

=== Vzor #gls("mvc", long: false) v kontextu Blenderu

Architektura přirozeně odpovídá vzoru #gls("mvc", long: false) v prostředí Blenderu. *Model* tvoří Vrstvy 1 a 2 --- čisté Python struktury bez závislosti na `bpy`, testovatelné izolovaně jednotkovými testy. *Vrstva 3* funguje jako synchronizační most, který zapisuje výsledky Modelu do Blender mesh. *View* zahrnuje Geometry Nodes modifikátor pro 3D geometrii a #gls("gpu", long: false) overlay pro kreslicí náhled a #gls("hud", long: false). *Controller* jsou modální operátory zachytávající uživatelské vstupy a překládající je na volání metod Modelu; Controller nikdy nepíše přímo do Blender geometrie.

#figure(
  image("/typst/assets/mvc_diagram.png", width: 80%),
  caption: [#gls("mvc", long: false) diagram reprezentující oddělení vrstev addonu],
) <fig-toolbar>

=== Principy návrhu

Návrh se řídí pěti principy: *oddělení zájmů* (grafová logika nezávisí na `bpy`, lze ji testovat jednotkovými testy bez Blenderu); *nedestruktivní úpravy* (změna parametru spustí přegenerování přes Geometry Nodes, nikoli přepis geometrie); *zpětná vazba v reálném čase* (každá změna v Modelu se okamžitě projeví díky automatické reevaluaci #gls("gn", long: false) modifikátoru); *modularita* (každý funkční požadavek FP1--FP7 je realizován v samostatném Python modulu); a *konvence Blenderu* (addon dodržuje standardní pojmenování operátorů, integraci Undo/Redo a strukturu addonu pro Blender Extensions).

=== Rozšiřitelnost architektury

Třívrstvá architektura je navržena s výhledem na budoucí rozšíření. Více podlaží lze přidat koordinační vrstvou nad stávající Vrstvy 1 a 2 --- ty samotné zůstanou beze změny. Nové typy prvků (sloup, příčka) nevyžadují změnu struktury grafu: stačí rozšířit sadu atributů a přidat odpovídající #gls("gn", long: false) podstrom. Alternativní výstupní formáty pracují výhradně s daty Vrstvy 3, bez zásahu do zbytku systému.

== Datový model

Architektura vymezila, z jakých vrstev se systém skládá a jak tyto vrstvy komunikují. Tato sekce přibližuje pohled na úroveň samotných dat: jaká je struktura entit, jaké atributy nesou a jaká pravidla musejí dodržovat. Datový model je záměrně oddělen od implementačních detailů --- popisuje logické entity a jejich vztahy, nikoli konkrétní Python třídy s kódem.

=== Vrstva 1: Strukturální graf

Třída `StructuralGraph` (Vrstva 1) nabízí operace pro celý životní cyklus grafu: přidávání a odebírání junctions a stěn, vyhledávání junctions v blízkosti zadané polohy (pro snap-on-junction), získávání stěn napojených na daný junction, detekci minimálních cyklů (implementováno přes NetworkX @networkx) a validaci planarity.

#figure(
  image("/typst/assets/layer1_classdiagram.png", width: 55%),
  caption: [Diagram tříd na vrstvě 1],
) <fig-toolbar>

=== Vrstva 2: Sémantický graf místností

Třída `RoomGraph` spravuje kolekci místností a sousedností, poskytuje prostorové dotazy (sousedé místnosti, celková plocha dle typu, nalezení vnějších místností) a synchronizuje stav s Vrstvou 1 při každé topologické změně.

#figure(
  image("/typst/assets/layer2_classdiagram.png", width: 60%),
  caption: [Diagram tříd na vrstvě 2],
) <fig-toolbar>

=== Vrstva 3: Synchronizační bridge

Vrstva 3 je jednosměrný datový kanál z Python grafů do Blender mesh. Synchronizační modul má dvě fáze, které musejí proběhnout v tomto pořadí: *fáze 1* udržuje topologii mesh v souladu s Vrstvou 1 (přidává a odebírá vrcholy, hrany a plochy); *fáze 2* zapisuje hodnotové atributy z Vrstev 1 a 2 na příslušné elementy mesh přes `mesh.attributes` #gls("api", long: false). Geometry Nodes tyto atributy čtou jako pojmenované vstupy a generují z nich 3D geometrii.

#figure(
  image("/typst/assets/layer3_classdiagram.png", width: 80%),
  caption: [Diagram tříd na vrstvě 3],
) <fig-toolbar>

#figure(
  table(
    columns: (auto, 2fr, auto, 2fr),
    align: (left, left, left, left),
    table.header(
      [*Doména*], [*Atribut*], [*Typ*], [*Účel*],
    ),
    [Vertex], [`junction_id`], [Integer], [identifikace styku stěn],
    [Edge], [`wall_id`], [Integer], [identifikace stěny],
    [Edge], [`wall_thickness`], [Float], [tloušťka pro 3D generování],
    [Edge], [`wall_height`], [Float], [výška stěny],
    [Face], [`room_id`], [Integer], [identifikace místnosti],
    [Face], [`room_area`], [Float], [plocha místnosti v $m^2$],
    [Face], [`is_wall`], [Integer], [příznak stěnové plochy (1 = stěna, 0 = podlaha)],
    [Face], [`is_opening`], [Integer], [příznak plochy otvoru (cutter pro Mesh Boolean)],
  ),
  caption: [Pojmenované atributy Vrstvy 3 zapisované synchronizačním modulem a čtené Geometry Nodes],
) <tab-named-attributes>

#gls("uuid", long: false) identifikátory z Vrstev 1 a 2 se převádějí na celá čísla třídou `IdMapper` pro optimalizaci #gls("gpu", long: false) zpracování v Geometry Nodes. Celoobjektová metadata a data persistence jsou ukládána jako Custom Property na Blender objekt.

=== Vztah mezi vrstvami

Všechny tři vrstvy jsou provázány jednosměrným asymetrickým tokem dat. Vrstva 1 (topologie) diktuje obsah Vrstvy 2 (sémantika): cyklus stěn ve Vrstvě 1 tvoří místnost ve Vrstvě 2; sdílená stěna dvou cyklů definuje sousedství. Vrstvy 1 a 2 společně zásobují Vrstvu 3 (synchronizace): topologie přechází z Vrstvy 1 do Vrstvy 3 v první fázi synchronizace; sémantická metadata přechází z Vrstvy 2 do Vrstvy 3 ve druhé fázi. Geometry Nodes čtou výsledné atributy a generují 3D geometrii. Zpětný tok neexistuje: Blender mesh je vždy odrazem aktuálního stavu grafů, nikoli jejich výchozím bodem.

#figure(
  image("/typst/assets/static_flow_diagram.png", width: 80%),
  caption: [Statický pohled — závislosti tříd],
) <fig-toolbar>

#figure(
  image("/typst/assets/seq_diagram.png", width: 80%),
  caption: [Dynamický pohled — sekvenční diagram],
) <fig-toolbar>

// === Validační pravidla

// Validace se aplikuje před zápisem dat do grafů a zabraňuje vzniku degenerované geometrie, která by způsobila vizuální artefakty nebo selhání algoritmů. Pro stěny platí: tloušťka $0{,}05 <= t <= 1{,}0$ m (tenčí stěny způsobují Z-fighting, tlustší nemají architektonický smysl), výška $1{,}0 <= h <= 10{,}0$ m, úhel napojení $0° < alpha <= 180°$. Pro místnosti: minimální plocha $> 1{,}0 m^2$ (menší prostory typicky indikují chybu v kreslení, ne reálnou místnost), poměr stran $0{,}1 <= "šířka"/"délka" <= 10{,}0$ a minimálně 3 hraniční vrcholy. Pro otvory: šířka je validována vůči délce stěny s odečtením inset zón u junctions (junction inset = polovina maximální tloušťky sousedních stěn), výška nesmí přesáhnout výšku stěny a cutter boxy nesmějí přesahovat pod Z = 0 (podmínka numerické stability EXACT Boolean solveru). Veškeré interní výpočty probíhají v metrech; převod jednotek se aplikuje výhradně na prezentační vrstvě při zobrazování v #gls("ui", long: false).

== Návrh funkcí <sec-design-functions>

Architektura a datový model definují statiku systému --- z čeho se skládá a jaká data nese. Tato sekce popisuje dynamiku: jak systém reaguje na uživatelské akce v každé funkci FP1 až FP7. Každá funkce je označena prioritou (must-have / should-have) v souladu s #gls("mvp", long: false) filtrem z kapitoly 3.1.

=== FP1 --- Nástroj tužka

Pencil Tool je primárním vstupním rozhraním addonu --- modální operátor zachytávající vstupy myši a klávesnice a překládající je na operace nad Vrstvou 1. Veškerá logika kreslení probíhá ve 2D rovině XY; Z-souřadnice je ignorována.

==== Stavový automat

Operátor je řízen třístavovým automatem, který garantuje, že stěna nikdy nevznikne bez platného počátečního bodu a nelze skončit v nekonzistentním stavu. Stav *NEAKTIVNÍ* --- nástroj je registrován, ale nepřijímá vstupy; jiné nástroje Blenderu fungují normálně. Stav *ČEKÁNÍ* --- nástroj aktivní, kurzor sleduje myš, žádný počáteční bod ještě nebyl umístěn; #gls("gpu", long: false) overlay zobrazuje existující geometrii a snap indikátory. Stav *KRESLENÍ* --- první junction byl umístěn; overlay v reálném čase kreslí náhled stěny od posledního bodu ke kurzoru a #gls("hud", long: false) zobrazuje délku a úhel navrhované stěny. Z obou aktivních stavů lze sezení buď *potvrdit* (všechny stěny sezení se synchronizují do meshe a zapíší do Undo stacku jedním krokem) nebo *přerušit* bez uložení (všechny stěny a junctions sezení se odstraní, mesh zůstane nezměněn). Zrušení aktuální čáry (přechod KRESLENÍ → ČEKÁNÍ) neodstraňuje dříve potvrzené stěny téže sezení.

#figure(
  image("/typst/assets/fp1_statediagram.png", width: 100%),
  caption: [Stavový diagram nástroje tužka],
) <fig-toolbar>

==== Snapping

Snapping má přesně danou prioritní hierarchii. Nejvyšší prioritu má *snap na existující junction* _(must-have)_ --- kurzor blíže než 15 pixelů od existujícího junctionu se přichytí na jeho přesné souřadnice. Nižší prioritu mají snap na osu, snap na mřížku a snap na úhel násobků 45° _(všechny should-have)_. Aktivní snap je vizuálně indikován žlutým kruhem u kurzoru; podržení Shift snap dočasně potlačí.

// ==== Interakce s datovým modelem

// Zápis do Vrstvy 1 nastane vždy až po potvrzení bodu, nikdy průběžně při pohybu myši. Potvrzení bodu vyvolá `L1.add_junction(x, y)` nebo reuse existujícího junctionu v toleranci. Potvrzení stěny vyvolá `L1.add_wall(j_start, j_end, thickness, height, material)`, spustí detekci cyklů a synchronizační cyklus Vrstvy 3 (fáze 1 + fáze 2). Vrácení posledního bodu vyvolá `L1.remove_wall(last_wall_id)` a odstraní osiřelé junctions. Přerušení sezení žádný zápis do dat neprovádí.

==== Vizuální zpětná vazba (#gls("gpu", long: false) overlay)

Veškerý kreslicí náhled probíhá v `draw_handler` registrovaném na `SpaceView3D` --- neukládá se do geometrie ani datového modelu. Náhled stěny: čára od posledního junctionu ke kurzoru v odlišné barvě od potvrzených stěn. #gls("hud", long: false): délka navrhované stěny a úhel k poslednímu úseku aktualizované při každém pohybu myši; ve stavu ČEKÁNÍ zobrazuje stavovou zprávu. Snap indikátor: barevný kruh u kurzoru při aktivním snapu. Nápověda kláves: ikony kláves a tlačítek myši v dolní stavové liště Blenderu (`STATUSBAR_HT_header`) --- vzor přejatý z nativního Blender Knife Tool.

==== Způsob generování stěny

Preview stěny reprezentuje osu stěny, avšak fyzická stěna má tloušťku, kterou je nutné rozložit. Tři *módy generování stěny* _(should-have)_ --- Center (symetricky na obě strany), Left (tloušťka nalevo od směru kreslení) a Right (napravo) --- odpovídají konvenci používané ve vektorových nástrojích a #gls("cad", long: false) programech. Mód lze přepínat klávesou `Tab` kdykoli během aktivního nástroje bez přerušení sezení; pojmy „levá" a „pravá" jsou vztaženy k _směru kreslení_, nikoli k pohledu kamery.

=== FP2 --- Parametrické objekty a otvory

FP2 definuje, jak se změna parametru stěny propíše do geometrie a jak jsou otvory svázány se stěnou tak, aby se pohybovaly spolu s ní.

==== Parametry stěny a update mechanismus

Každá stěna ve Vrstvě 1 nese atributy `thickness`, `height` a `material_id`. Změna kteréhokoli z nich spustí přesně definovaný *update cyklus*: validace nové hodnoty → zápis do Vrstvy 1 → případný přepočet sousedních místností ve Vrstvě 2 → Vrstva 3 fáze 2 serializuje pouze změněný atribut → Geometry Nodes reevaluace. Tento update je záměrně levnější než přidání stěny: neprovádí se detekce cyklů ani fáze 1 sync, protože topologie mesh se nemění.

==== Otvory --- #gls("gn", long: false) Mesh Boolean

*Otvory* (dveře, okna) jsou svázány s konkrétní stěnou --- uchovávají svou polohu, šířku, výšku a výšku parapetu jako součást záznamu o stěně ve Vrstvě 1. Výřez otvoru v geometrii zajišťuje Geometry Nodes prostřednictvím operace Mesh Boolean: ze zadaných rozměrů sestaví tvar výřezu a ten od stěny odečte. Výsledek se aktualizuje automaticky při každé změně parametrů.

==== Vložení pravoúhlé místnosti z parametrů

Toto vložení _(must-have)_ je alternativní vstupní metodou k Pencil Toolu: uživatel zadá šířku, hloubku, výšku a tloušťku stěn v N-panelu a addon vytvoří čtyři junctions a čtyři stěny se středem v poloze 3D kurzoru Blenderu. Výsledná místnost je datově nerozeznatelná od místnosti nakreslené tužkou --- všechny navazující operace (FP5, FP6, FP7) fungují identicky. V rámci #gls("mvp", long: false) se místnost vkládá vždy jako samostatná izolovaná místnost bez sdílených junctions s existující sítí. Rozšiřující možností _(should-have)_ této funkce, je zadání více parametrů pro vkládanou místností, např. počet stěn, jejich poměr nebo tvar místnosti. 

// ==== Vazba otvorů na stěnu

// Závislost otvoru na stěně je uložena ve Vrstvě 1 jako atribut hrany. Po posunu junctionu nebo změně délky stěny se relativní pozice otvoru $t in [0, 1]$ zachovává --- absolutní souřadnice se přepočítá automaticky z nové délky stěny; orientace otvoru se přepočítá z nového směrového vektoru stěny. Vrstva 3 fáze 2 serializuje nové poziční atributy a GN reevaluace posune otvor vizuálně.

=== FP3 --- Detekce místností a metadata

FP3 _(must-have)_ představuje klíčovou funkcionalitu, která odlišuje FloorPlanMaster od běžných nástrojů pro 3D modelování: místnosti nevznikají manuálním zadáváním, ale jako implicitní výsledek nakreslené dispozice. Jakmile stěny vytvoří uzavřený prostor, systém jej automaticky detekuje jako místnost. Přepočet neprobíhá kontinuálně, ale efektivně pouze ve chvíli, kdy je to skutečně nutné --- tedy po každé úpravě půdorysu. Odstraní-li uživatel dělicí stěnu mezi dvěma místnostmi, systém tyto prostory sloučí do jednoho a zachová přitom metadata původní místnosti.

U každého prostoru systém průběžně eviduje jeho *plochu*, *obvod*, polohu středu (pro správné ukotvení textových popisků) a uživatelsky definovaný *název*.

Geometrie uložená v souboru modelu obsahuje veškerá potřebná data k tomu, aby systém při opětovném načtení projektu nebo po použití funkce Zpět kompletně zrekonstruoval aktuální stav dispozice. Uživatelské názvy místností se ukládají odděleně; pokud by z jakéhokoli důvodu chyběly, celková funkčnost logiky půdorysu zůstane zachována --- místnosti budou existovat i nadále, pouze se zobrazí bez svých pojmenování.

=== FP4 --- Finalizační nástroj

Finalizační nástroj _(must-have)_ provede nevratný převod parametrického modelu do statické polygonové sítě vhodné pro export, #gls("uv", long: false) mapování nebo herní engine. Jde o jednosměrnou operaci --- proto addon před zahájením vygeneruje záchranný bod Undo. Operátor je řízen automatem se stavy NEAKTIVNÍ → DIALOG (spuštění) → BAKING (potvrzení voleb) → HOTOVO nebo CHYBA.

#figure(
  image("/typst/assets/fp4_statediagram.png", width: 100%),
  caption: [Stavový diagram finalizačního nástroje],
) <fig-toolbar>

V dialogu uživatel volí: *organizaci výstupu* (jeden objekt / per místnost / separace stěny + podlahy + stropy), *přiřazení materiálů* (automaticky z metadat Vrstvy 2 nebo ponechat výchozí Blender materiál), *čistění atributů* (odstranit named attributes z výsledné sítě pro úsporu dat) a *zachovat originál* (duplikovat před finalizací vs. finalizovat přímo).

// Technicky finalizace pracuje přes vyhodnocený depsgraph (`evaluated_get(depsgraph)`): aplikace GN modifikátoru z vyhodnoceného stavu → konverze UV atributů z face-corner domény na standardní UV vrstvy (`MeshUVLoopLayer`, jinak je exportéry #gls("fbx", long: false) a glTF ignorují) → deduplikace materiálových slotů (Join Geometry v GN produkuje duplicitní sloty; identické materiály se sloučí, indexy polygonů přemapují, prázdné sloty odstraní).

=== FP5 --- Kontextová nabídka

Kontextová nabídka _(nice-to-have)_ poskytuje rychlý přístup k méně frekventovaným operacím (přejmenování, smazání, rozdělení stěny) bez nutnosti hledat je v panelech. Vyvolává se stiskem #gls("rmb", long: false) ve 3D Viewportu --- zaběhlá Blender konvence.

Klíčovým mechanismem je *raycast*: addon vrhne paprsek z pozice kurzoru přes Vrstvu 3 (Blender mesh s named attributes) a identifikuje typ elementu. Plocha → místnost; hrana → stěna; vrchol → junction; prázdný prostor → globální akce. Obsah nabídky se dynamicky přizpůsobuje kontextu: uživatel vidí vždy jen akce relevantní pro kliknutý prvek, nikoli celý katalog operátorů addonu.

Pro kontext místnosti jsou dostupné přejmenování, změna materiálu a smazání (kaskádové odebrání stěn z Vrstvy 1). Pro kontext stěny: editace tloušťky, výšky a materiálu; přidání otvoru; rozdělení stěny vložením nového junctionu; smazání. Pro kontext junctionu: smazání s přilehlými stěnami; sloučení s nejbližším junctionem (merge v toleranci). Pro prázdný prostor: přepnutí viditelnosti mřížky, kótování a spuštění Pencil Tool --- alternativa ke klávesové zkratce pro uživatele preferující nabídky.

=== FP6 --- Interaktivní manipulátory

Gizmos _(should-have)_ jsou interaktivní grafické ovládací prvky ve 3D Viewportu, které umožňují přímou geometrickou manipulaci taháním myší bez přepínání nástrojů. Vzor je přejat z Archipack @archipack, kde výběr stěny automaticky zobrazí táhla pro tloušťku a výšku.

Addon definuje tři typy manipulátorů. *Manipulátor tloušťky stěny* (světle modrá) --- obousměrná šipka kolmá na osu stěny v rovině XY; táhnutím se aktualizuje `wall_thickness` ve Vrstvě 1 a spouští fáze 2 sync a #gls("gn", long: false) reevaluace, topologie Vrstvy 1 zůstává nezměněna. *Manipulátor výšky stěny* (zelená) --- svislá šipka na středu stěny, pohyb omezen na osu Z; aktualizuje `wall_height` bez změny topologie. *Manipulátor pohybu junctionu* (žlutá) --- kruh na vybraném junctionu; pohyb striktně omezen na rovinu XY (*2D zámek*) --- Z-složka tahu je zahozena, protože pohyb mimo rovinu by narušil planarita Vrstvy 1 a způsobil selhání detekce místností.

=== FP7 --- Automatické kótování

Kótovací overlay _(should-have)_ zobrazuje rozměry stěn a metriky místností průběžně ve 3D Viewportu bez nutnosti aktivovat speciální nástroj. Text je vykreslován jako `POST_PIXEL` overlay přes draw_handler registrovaný na `SpaceView3D` (@blender_api) --- zůstává čitelný nezávisle na úhlu kamery, protože pracuje v souřadnicích obrazovky. Data jsou čtena výhradně z Vrstev 1 a 2, nikoli z geometrie scény: délky stěn z Euklidovské vzdálenosti junction--junction, plochy a centroidy z uzlů Vrstvy 2. Viditelnost kótování přepíná globální přepínač v Nastavení (klávesa `T`).

== Návrh uživatelského rozhraní <sec-design-ui>

Architektura a funkce definují, co systém dělá. Tato sekce popisuje, jak uživatel se systémem komunikuje --- kde jsou nástroje umístěny, jaká klávesová zkratka co spouští a jak viewport vizuálně reflektuje aktuální stav. Návrh #gls("ui", long: false) vychází z principu konzistence s ekosystémem Blenderu: každý prvek rozhraní kopíruje vzor, který uživatelé Blenderu již ovládají, aby minimalizoval náklady na učení. Současně musí návrh reflektovat omezení Blender Python #gls("api", long: false), zejména nemožnost přidat nativní pracovní mód, a dosáhnout ekvivalentního výsledku kompozicí dostupných mechanismů.

=== Toolbar --- umístění nástroje tužka

 Konvencí Blenderu je, že nástroj ovládaný levým tlačítkem myši v kontinuálním modálním režimu patří do Toolbaru. Pencil Tool tuto podmínku splňuje: po aktivaci přebírá všechny vstupy a každé #gls("lmb", long: false) kliknutí potvrzuje bod. Addon proto registruje Pencil Tool jako `WorkspaceTool` --- Blender jej automaticky zobrazí jako ikonové tlačítko v Toolbaru, vizuálně zvýrazní při aktivaci a zobrazí tooltip s názvem a klávesovou zkratkou.

Při aktivaci nástroje se v levém horním rohu viewportu a v sekci Active Tool v N-panelu zobrazí ovládací prvky pro tloušťku, výšku a příchycení stěny --- vzor přejatý z nativních sculpting nástrojů Blenderu.

=== Postranní panel (N-panel)

N-panel (Sidebar) je standardním místem pro trvalé rozhraní addonů. Addon přidává záložku *FloorPlanMaster* se čtyřmi skládacími sekcemi. Toto členění přejímá vzor z Archipack @archipack, kde je panel rozdělen na sekci operátorů a sekci parametrů vybraného objektu.

*Sekce Nástroje* sdružuje spouštěče akcí: tlačítko Pencil Tool (alternativa ke klávesové zkratce `D`), Vložit místnost (otevírá inline formulář s poli šířka, hloubka, výška, tloušťka) a Zapéct (spouští finalizační pop-over FP4 s volbami výstupu). Toto odlišení je záměrné: Blender konvencí je, že akce vkládající nové prvky patří do sekce Nástrojů, nikoli do sekcí modifikujících výběr.

#figure(
  image("../docs/assets/blender_ui_tools.png", width: 80%),
  caption: [Návrh #gls("ui", long: false) pro sekci Nástroje],
) <fig-toolbar>

*Sekce Místnosti* je přehledem uzlů Vrstvy 2: seznam všech místností s editovatelným názvem a průběžně aktualizovanou plochou. Kliknutím na položku dojde k výběru místnosti ve viewportu a rozbalení detailního pohledu přímo pod položkou (obvod, výška, počet stěn). Vzor odpovídá technice „list panel s automatickým výběrem", kterou Blender nativně používá pro vertex groups nebo shape keys.

Jako rozšiřující možností této sekce je přidat hiearchický list stěn dané místnosti pro přehlednou kontrolu uživatelem.

#figure(
  image("../docs/assets/blender_ui_rooms.png", width: 80%),
  caption: [Návrh #gls("ui", long: false) pro sekci Místnosti],
) <fig-toolbar>

*Sekce Nastavení* obsahuje globální parametry scény uložené v `Scene PropertyGroup`. Záměrně jsou sem zařazeny pouze parametry ovlivňující chování celého projektu --- nikoli parametry jednotlivých prvků.

#figure(
  image("../docs/assets/blender_ui_settings.png", width: 80%),
  caption: [Návrh #gls("ui", long: false) pro sekci Nastavení],
) <fig-toolbar>

#figure(
  table(
    columns: (2fr, auto, 2fr),
    align: (left, center, left),
    table.header(
      [*Parametr*], [*Výchozí hodnota*], [*Popis*],
    ),
    [Systém jednotek], [Metrický], [Přepíná zobrazení rozměrů; interně vždy metry],
    [Výchozí tloušťka stěny], [0,3 m], [Přednabídnuto při kreslení a vkládání místnosti],
    [Kótovací overlay], [Vypnuto], [Zapíná draw_handler FP7],
    [Barevné odlišení místností], [Vypnuto], [Každá místnost dostane automaticky odlišnou barvu],
    [Názvy místností ve viewportu], [Zapnuto], [Text v centroidu místnosti],
    [Highlight výběru], [Zapnuto], [Označí aktuálně vybraný prvek],
    [Manipulátory (gizmos)], [Vypnuto], [Zobrazí táhla pro vybranou stěnu],
  ),
  caption: [Přehled globálních nastavení v sekci Nastavení N-panelu s výchozími hodnotami],
) <tab-settings>

*Sekce aktuálně vybrané stěny* je umístěna na spodu záložky a zobrazuje se výhradně tehdy, když je ve scéně vybrána stěna. Zobrazuje délku stěny, editovatelnou tloušťku a výšku a seznam otvorů s možností přidání a odebrání. Detail každého otvoru poskytuje editaci názvu, typu (dveře/okno), šířky, výšky, výšky parapetu a relativní polohy na stěně.

Možným rozšířením je přidání editace polohy stěny a jejích koncových bodů.

=== Klávesové zkratky

Návrh klávesových zkratek se řídí dvěma principy: zkratky musejí být kompatibilní se stávající svalovou pamětí uživatelů Blenderu; zkratky platné v modálním kontextu nesmějí kolidovat s globálními Blender zkratkami. Klávesový mód Pencil Tool je záměrně analogický Blender Knife Tool: rozlišuje stav ČEKÁNÍ a stav KRESLENÍ.

#figure(
  table(
    columns: (2fr, auto, auto, 2fr),
    align: (left, center, left, left),
    table.header(
      [*Akce*], [*Klávesa*], [*Kontext*], [*Zdůvodnění*],
    ),
    [Aktivovat Pencil Tool], [`D`], [Object Mode], [`D` = Draw; ArchiCAD konvence; v Blenderu Object Mode neobsazeno],
    [Umístit bod / pokračovat], [`LMB`], [Pencil Tool aktivní], [#gls("lmb", long: false) jako primární potvrzovací vstup --- Blender standard od v2.80],
    [Potvrdit sezení], [`Enter`], [Oba stavy], [Blender konvence pro potvrzení modálního operátoru (Knife Tool, Loop Cut)],
    [Vrátit poslední bod], [`Z`], [Oba stavy], [`Z` jako Undo; bezpečné --- Blender `Z` (shading pie) blokováno po dobu aktivity operátoru],
    [Zrušit aktuální čáru], [`RMB`], [Stav KRESLENÍ], [Analogie s Knife Toolem; ve stavu ČEKÁNÍ #gls("rmb", long: false) propustí do Blenderu (kontextová nabídka)],
    [Přerušit sezení bez uložení], [`ESC`], [Oba stavy], [Zruší všechny změny sezení; identické chování s Knife Tool a Loop Cut],
    [Potlačit snap], [Shift (držet)], [Pencil Tool aktivní], [Blender konvence pro dočasné přepnutí snap modu],
    [Přepnout kótování FP7], [`T`], [3D Viewport], [`T` = Toggle; alternativně nastavitelné v Preferences],
  ),
  caption: [Klávesové zkratky addonu s kontextem a zdůvodněním volby klávesy],
) <tab-shortcuts>

// Všechny zkratky jsou registrovány s podmínkou kontextu (`bl_space_type = 'VIEW_3D'`). Klávesa `D` je registrována pouze pro Object Mode, kde Blender tuto klávesu nativně neobsazuje. Po dobu aktivity modálního operátoru jsou ostatní Blender zkratky blokovány --- s výjimkou navigačních vstupů (střední tlačítko myši, Numpad pohledy) a `RMB` ve stavu ČEKÁNÍ.

// === Viewport UI

// Viewport #gls("ui", long: false) tvoří tři kategorie vizuálních prvků vykreslovaných přímo ve 3D Viewportu nad geometrií scény prostřednictvím #gls("gpu", long: false) overlay vrstev.

// *#gls("hud", long: false) overlay (Pencil Tool aktivní)* --- text a grafika překrývající viewport po dobu aktivity Pencil Tool, vykreslované v `POST_PIXEL` režimu.

// *Kótovací overlay (FP7)* --- délky stěn jako text nad středem každé hrany. Text vykreslován přes modul #gls("blf", long: false) v `POST_PIXEL` handleru.

// *Barevné odlišení místností* --- průhledná barevná výplň uzavřených cyklů vykreslovaná v `POST_VIEW` režimu; každá místnost dostane automaticky odlišnou barvu. Výplň je poloprůhledná, aby nerušila viditelnost geometrie. Vzor přejat z ArchiCAD a Revit @revit, kde barevné kódování místností patří k základní orientaci v půdorysu.

// #figure(
//   table(
//     columns: (auto, auto, 2fr),
//     align: (left, left, left),
//     table.header(
//       [*Prvek*], [*Barva*], [*Sémantika*],
//     ),
//     [Potvrzené stěny], [Světle šedá], [Existující hmota --- neutrální],
//     [Preview stěna (FP1)], [Modrá], [Navrhovaný, nepotvrzený prvek],
//     [Snap indikátor], [Žlutá], [Aktivní přichycení --- příští klik se přichytí na tuto pozici],
//     [Vybraný prvek (stěna, místnost)], [Oranžová], [Blender konvence pro aktivní výběr],
//     [Chybová indikace], [Červená], [Neplatná operace --- Blender error state barva],
//   ),
//   caption: [Barevná sémantika overlay vrstvy v souladu s konvencemi nativních Blender nástrojů],
// ) <tab-colors>

// *Gizmos (FP6)* --- interaktivní táhla zobrazující se při výběru prvku: manipulátor tloušťky (světle modrá obousměrná šipka kolmá na stěnu v rovině XY), manipulátor výšky (zelená svislá šipka na středu stěny) a manipulátor pohybu junctionu (žlutý kruh omezený na rovinu XY).

// === Kontextová nabídka

// Kontextová nabídka je vyvolána stiskem #gls("rmb", long: false) ve 3D Viewportu. Raycast identifikuje typ elementu a obsah nabídky se dynamicky přizpůsobuje: uživatel v každém kontextu vidí pouze relevantní akce, čímž se redukuje vizuální šum. Vzor kopíruje Archipack @archipack (RMB na objekt zobrazuje akce specifické pro typ architektonického prvku) a AutoCAD @autocad (RMB = kontextová nabídka závislá na výběru). Operace vyžadující textový vstup nebo výběr z enumu otevírají *pop-over dialog* u pozice kurzoru --- shodný vzor jako F9 Last Operator pop-over v nativním Blenderu; zavírá se kliknutím mimo bez nutnosti potvrzení.

=== FloorPlan kontext --- simulovaný pracovní mód

Ideálním designovým řešením by byl vlastní pracovní mód paralelní k Object Mode a Edit Mode --- „FloorPlan Mode" s jednoznačně vymezeným kontextem, vlastními klávesami a explicitní bariérou vůči obecným Blender nástrojům. Blender Python #gls("api", long: false) @blender_dev však neumožňuje přidání nativního módu; `object.mode_set()` je pevně omezeno na módy implementované v C jádru. Návrh proto realizuje ekvivalentní řešení složením tří mechanismů:

1. *Interakční stav* --- FloorPlan mód lze aktivovat pouze pro objekt, který je současně aktivní i vybraný. Aktivace je mapována na klávesu rezervovanou v Object Mode (např. `Shift+Q`). Po zapnutí se režim stává „vlastníkem" interakcí v 3D Viewportu pro daný objekt. Deaktivace vrátí kontrolu obecným Blender nástrojům.

2. *Selektivní propuštění vstupů* --- Během aktivního FloorPlan módu modální komponent řídí příjem klávesnice a myši. Navigace kamery (orbit/zoom/pan), Undo/Redo a nastavení panelů se propouští Blenderu. Levé kliknutí provádí sémantický výběr stěny či místnosti pomocí raycasting přes mesh. Běžné Blender zkratky pro editaci (W, G, Tab, X) jsou konzumovány addonem, aby se zabránilo nežádoucím operacím. Pokud Pencil Tool právě kreslí, vstup je jemu svěřen.

3. *Vizuální rozlišení kontextu* --- Během aktivního módu se vypne standardní Blender highlight vybraných objektů a jejich místo zaujme sémantické zvýraznění prvků: oranžové obarvení vybrané stěny, průhledné vyplnění vybrané místnosti, barevné označení otvorů. Globální informační overlaye (délky stěn, plochy místností, výšky) zůstávají viditelné pro všechny FloorPlan objekty v projektu nezávisle na módu, ale interaktivní kontext --- výběr a úpravy --- patří pouze objektu, který je vlastníkem aktivního režimu.

Jeden `.blend` soubor tak může obsahovat více FloorPlan objektů. Informace všech jsou viditelné pro orientaci, ale editační operace proběhnou pouze pro jeden vybraný vlastníka módu. Přepnutí režimu na jiný FloorPlan objekt je jednoduché --- deaktivace stávajícího a aktivace nového přes tutéž klávesovou zkratku.

*Koncepční analogie s Edit Mode.* FloorPlan mód sdílí filozofii s Blender Edit Mode: oba se aktivují na vybraném objektu a transformují dostupnou sadu akcí do speciálně vymezené domény. Edit Mode přesunuje fokus z úrovně objektu na úroveň primitivů (vrcholy, hrany, faces), kde se standardní operace (G, S, R) aplikují na geometrické prvky; FloorPlan mód analogicky přesunuje fokus do domény architektonického návrhu (junctions, walls, rooms), kde interakční gesta mají odlišný význam a dostupné nástroje jsou úzce zaměřeny na kreslení a editaci půdorysu. Oba módy tedy sdílí paradigma --- vstup se interpretuje v kontextu speciální domény, nikoli v obecném Object Mode kontextu. Tato analógie propůjčuje FloorPlan módu na sebe pochopitelnosti: uživatelé již zvyklí na mód-driven workflow v Blenderu rozpoznají princip a přenesou své mentální modely mezi módy. Výsledek je seamless přepínání mezi obecným 3D modelováním (Object Mode) a specifickým architektonickým návrhem (FloorPlan mód) bez pocitu diskontinuity. 

== Testování a validace návrhu

Před zahájením implementace je nezbytné ověřit, že navržená architektura a funkce společně spolehlivě pokrývají zadání z #gls("mvp", long: false) scope a neobsahují logické mezery. Tato kapitola plní roli kontroly návrhu prostřednictvím kontrolních seznamů, teoretických průchodů scénáři a analýzy okrajových případů.

=== Pokrytí požadavků

Každý must-have prvek FP1--FP4 má jednoznačně přiřazenou návrhovou sekci (kapitola 3.4), datový model (kapitola 3.3) a průchoditelný tok dat napříč vrstvami. Should-have prvky FP5--FP7 jsou navrhnuty a datově pokryty, ale nejsou součástí #gls("mvp", long: false) scope --- architektura je připravena je pojmout bez změny Vrstev 1 a 2.

#figure(
  table(
    columns: (1fr, 1.8fr, 1.5fr, 0.6fr),
    align: (left, left, left, center),
    stroke: 0.5pt,
    table.header(
      [*Požadavek*], [*Navrhující sekce*], [*Datový model*], [*#gls("mvp", long: false)*],
    ),
    [FP1 --- modální\ kreslení], [FP1 --- stavový\ automat], [Junction, Wall (L1)], [✓],
    [FP1 --- snap na\ junction], [FP1 --- snapping], [Junction.position (L1)], [✓],
    [FP2 --- update stěny], [FP2 --- update\ mechanismus], [Wall.thickness/\ height (L1)], [✓],
    [FP2 --- otvory\ #gls("gn", long: false) Boolean], [FP2 --- otvory], [Wall.openings,\ L3 atributy], [✓],
    [FP3 --- detekce\ místností], [FP3 --- detekce\ cyklů], [Room (L2) z\ cyklu (L1)], [✓],
    [FP4 --- finalizace], [FP4 --- interakce\ s modelem], [L3 → statická mesh], [✓],
    [FP5 --- kontextová\ nabídka], [FP5 --- raycast +\ akce], [L3 raycast →\ L1/L2], [---],
    [FP6 --- manipulátory], [FP6 --- typy gizmos], [Wall.thickness/height,\ Junction.pos], [---],
    [FP7 --- kótování], [FP7 --- datový\ pipeline], [L1 délky, L2 area\ + centroid], [---],
  ),
  caption: [Tabulka pokrytí požadavků návrhovou dokumentací; ✓ = součást #gls("mvp", long: false), --- = odloženo za #gls("mvp", long: false)],
) <tab-coverage>

Nefunkční požadavky jsou pokryty architekturálně. NP1 (Geometry Nodes jako backend, Python jako manažer) je zajištěn oddělením Vrstev 1--2 od Vrstvy 3. NP2 (výkon a nedestruktivnost) je zajištěn jednosměrným tokem dat a dvoufázovou synchronizací --- změna atributu nevyvolá detekci cyklů (pouze fáze 2). NP3 (použitelnost) je zajištěn výběrem klávesových zkratek a barevné sémantiky konzistentních s Blender konvencemi a validačními chybami hlášenými pop-overem.

=== Průchod scénáři použití

Průchod scénáři ověřuje, že navržená architektura a funkce společně pokrývají celý uživatelský workflow. Všechny scénáře (UC 1.1--3.2) jsou plně řešitelné must-have prvky (FP1--FP4).

- *UC 1.1 (hmotová studie z parametrů):* architekt zadá plochu a poměr stran → FP2 vytvoří čtyři stěny → Vrstva 2 vypočítá metriky (FP3) → opakování pro stavební program.

- *UC 1.2 (kreslení dispozice tužkou):* aktivace Pencil Tool (FP1) → kreslení s snapem na existující junctiony (FP1) → uzavření cyklu spouští detekci místnosti (FP3) → úprava parametrů v N-panelu (FP2) → #gls("gn", long: false) reevaluace.

- *UC 2.1 (obkreslení 2D půdorysu):* vizualizátor vloží obrázek na pozadí → aktivuje Pencil Tool s snapem (FP1) → odklikává rohy podle obrázku → addon generuje stěny a detekuje místnosti (FP3) → nastavení tloušťky a výšky (FP2).

- *UC 2.2 (příprava pro rendering):* výběr stěny a přidání otvoru (FP2 --- #gls("gn", long: false) Boolean) → parametry otvoru v N-panelu → finalizace (FP4).

- *UC 3.1 (level blockout):* game designer aktivuje Pencil Tool (FP1) → kreslí sérii navazujících místností (FP1, FP3) → uniformní výška v N-panelu (FP2).

- *UC 3.2 (export herní úrovně):* přidání dveřních otvorů (FP2 --- #gls("gn", long: false) Boolean) → ověření ploch místností v N-panelu (FP3) → finalizace a export (FP4).

Následující tři scénáře rozšiřují základní workflow o pokročilé funkce a nejsou součástí #gls("mvp", long: false) scope. Jejich implementace je záměrně odložena za prvotní fázi projektu. Architektura je však již připravena jejich pojetí bez jakýchkoli změn Vrstev 1 a 2, a datový základ (geometrické metriky a identifikace prvků) je dostupný od #gls("mvp", long: false).

- *UC 1.3 (kótování):* zapnutí kótovacího overlaye (FP7) — závisí na FP7, datový základ dostupný.

- *UC 2.3 (kontextová editace):* #gls("rmb", long: false) na prvek → dynamická nabídka (FP5) — závisí na FP5, datový základ dostupný.

- *UC 3.3 (interaktivní manipulace):* gizmo pohybu junctionu (FP6) — závisí na FP6, datový základ dostupný.

// === Analýza okrajových případů

// Topologické edge cases jsou ošetřeny validací Vrstvy 1: stěna s nulovým rozpětím (start = end junction) je odmítnuta, duplicitní stěna mezi dvěma junctions je odmítnuta (prostý graf), posun junctionu vedoucí ke crossing edges spouští planaritní kontrolu. Sémantické edge cases jsou ošetřeny automatickou synchronizací: smazání dělící stěny provede node fusion (zachová ID místnosti), zánik posledního cyklu odstraní místnost, změna geometrie bez změny topologie přepočítá pouze metriky. Persistence edge cases jsou pokryty rekonstrukcí z named attributes: reload souboru bez Custom Property (poškozený soubor) rekonstruuje grafy funkčně --- místnosti ztratí uživatelská jména, ale jsou jinak plně funkční. Undo po přidání stěny obnoví mesh snapshot a rekonstrukce ze snapshottu vrátí konzistentní stav Vrstev 1 a 2.

== Hodnocení návrhu uživatelského rozhraní

Kapitola 3.5 definovala návrh #gls("ui", long: false) addonu. Před zahájením implementace je vhodné provést jeho systematické hodnocení --- ověřit, že navržené rozhraní je konzistentní s ekosystémem Blenderu, splňuje klíčové principy použitelnosti a umožňuje novému uživateli dokončit základní úkoly bez zbytečných překážek. Hodnocení aplikuje tři doplňující se metody: kontrolu konzistence, heuristické hodnocení dle Nielsena a kognitivní průchody vybranými scénáři.

=== Konzistence s ekosystémem Blenderu

Kontrola konzistence hodnotí, jak plynule addon zapadá do stávajícího Blender ekosystému a zda je vnitřně soudržný.

*Vnější konzistence.* Pencil Tool je registrován jako WorkspaceTool v T-panelu, shodně s nativními modálními nástroji Knife Tool, Loop Cut a Poly Build --- addony umísťující modální nástroje mimo Toolbar (Archimesh @archimesh, Archipack @archipack) tak činí z historických důvodů předcházejících WorkspaceTool #gls("api", long: false). Klávesové zkratky respektují stávající Blender keymapping: #gls("lmb", long: false) jako potvrzení, #gls("rmb", long: false) jako kontextová nabídka, ESC pro zrušení modálního operátoru (identické s Knife Tool). Barevná sémantika přejímá konvence nativních nástrojů: oranžová pro výběr odpovídá standardnímu Blender theme, modrá pro nepotvrzené prvky odpovídá Loop Cut preview, žlutá pro snap odpovídá nativnímu Blender snap markeru. N-panel sekce Nástroje → Místnosti → Nastavení odpovídá logické hierarchii Blender Properties editoru (Tool → Item → View).

*Vnitřní konzistence.* Každá klíčová akce je dosažitelná více cestami se shodným výsledkem: aktivace Pencil Tool přes `D`, tlačítko v N-panelu i klik na ikonu v Toolbaru vede do identického vstupního stavu FP1 automatu; přepnutí kótování přes `T`, přepínač v kontextovém menu i v Nastavení mění tentýž stav FP7 draw_handleru. Obousměrná synchronizace výběru (klik na místnost v N-panelu vybere ji ve viewportu a naopak) zabraňuje situaci, kde uživatel edituje jiný prvek než zvýrazněný.

=== Heuristické hodnocení

Heuristické hodnocení porovnává návrh s třemi Nielsonovými heuristikami použitelnosti nejvíce relevantními pro nástrojový addon v 3D editoru.

*Viditelnost stavu systému.* Pencil Tool jako modální operátor s více stavy je nejvýraznějším rizikovým místem --- uživatel musí vždy vědět, zda je nástroj aktivní a v jakém stavu se automat nachází. Návrh adresuje toto riziko na třech úrovních: #gls("hud", long: false) overlay v levém dolním rohu viewportu zobrazuje aktuální stav automatu (ČEKÁNÍ / KRESLENÍ) a nápovědu platných kláves --- vzor přejatý z Blender Knife Tool; dynamická preview stěna ve stavu KRESLENÍ potvrzuje, že první bod byl zaregistrován; snap indikátor (žlutý kruh) signalizuje výsledek příštího kliknutí ještě před jeho provedením --- SketchUp @sketchup používá identický vzor. Hodnocení: heuristika je dobře pokryta.

*Shoda se skutečným světem.* Terminologie addonu (místnost, stěna, otvor, tloušťka, výška) odpovídá slovní zásobě architektů i game designérů. Rozměry jsou zobrazeny v nastaveném systému jednotek, nikoli jako interní hodnoty v metrech. Workflow Pencil Tool (bod → stěna → uzavření cyklu → místnost) odpovídá způsobu, jakým architekti ručně kreslí půdorysy --- místnosti vznikají jako logický důsledek uzavřených smyček bez explicitní deklarace; zásadní rozdíl oproti Archimesh @archimesh, kde se místnosti vkládají jako předpřipravené objekty. Hodnocení: heuristika je pokryta.

*Uživatelská kontrola a svoboda.* ESC kdykoli během Pencil Tool zruší aktuální kreslicí akci a vrátí automat do stavu ČEKÁNÍ; opakované ESC deaktivuje nástroj. `Z` vrátí poslední potvrzený junction bez opuštění nástroje --- zkrácení iterativního cyklu o dva kroky oproti globálnímu `Ctrl+Z`. Každá operace modifikující Vrstvy 1 nebo 2 je zapsána do Blender Undo stacku. Nedestruktivní architektura #gls("gn", long: false) zaručuje, že změna parametru stěny je kdykoliv vrátitelná. Smazání místnosti nebo stěny z kontextové nabídky zobrazí pop-over s potvrzením --- nevratné akce bez potvrzení by porušovaly jak tuto heuristiku, tak Blender konvenci. Hodnocení: heuristika je pokryta.

=== Kognitivní průchody

Kognitivní průchod simuluje zkušenost nového uživatele při plnění konkrétního úkolu. Hodnotitel prochází každý krok a klade čtyři otázky: ví uživatel, jakou akci provést? Vidí ovládací prvek? Pokročil správným směrem? Je zpětná vazba správná? 

_Poznámka: Hodnocení je expertní průchod architektury; kvalitativní uživatelské testování neproběhlo a je doporučeno v implementační fázi._

Zvoleny jsou dva reprezentativní scénáře:

*UC 1.2 --- Kreslení dispozice tužkou.* Aktivace nástroje (krok 1) --- ikona tužky v Toolbaru s tooltipem je dohledatelná průzkumem Toolbaru nebo N-panelu; po aktivaci se ikona zvýrazní a #gls("hud", long: false) zobrazí stavovou zprávu se stavem ČEKÁNÍ --- zpětná vazba je správná. Umístění prvního bodu (krok 2) --- stavová zpráva říká „#gls("lmb", long: false): umístit první bod"; po kliknutí se preview linka táhne ke kurzoru a #gls("hud", long: false) přejde do stavu KRESLENÍ --- zpětná vazba potvrzuje přechod stavu. Uzavření místnosti (krok 3) --- snap indikátor u prvního junctionu signalizuje možnost uzavření; uzavření cyklu způsobí okamžité zobrazení barevné výplně plochy --- vizuální signál detekce místnosti bez technické hlášky. Identifikovaný potenciál rizika: uživatel nemusí vědět, že uzavření cyklu na první junction je podmínkou vzniku místnosti; snap indikátor a chybějící barevná výplň při neuzavření toto riziko zmírňují.

*UC 1.1 --- Vložení místnosti z parametrů.* Nalezení funkce (krok 1) --- tlačítko „Vložit místnost" je v sekci Nástroje jako první viditelný prvek; tooltip říká „Vloží pravoúhlou místnost se středem na 3D kurzoru". Identifikované riziko: uživatel bez Blender zkušenosti nemusí znát pojem „3D kurzor" --- riziko akceptovatelné, protože 3D kurzor je fundamentální Blender koncept předcházející práci s libovolným addonem pro modelování. Zadání parametrů a potvrzení (krok 2) --- po potvrzení se místnost ihned zobrazí ve viewportu jako obarvená plocha a N-panel sekce Místnosti zobrazí novou položku s vypočítanou plochou --- okamžitá vizuální a numerická zpětná vazba potvrzující správnost operace.

=== Závěr hodnocení

Hodnocení provedené třemi metodami neprokázalo žádné systémové nedostatky zabraňující zahájení implementace. Kontrola konzistence potvrdila soulad s Blender konvencemi na všech úrovních. Heuristické hodnocení dospělo u všech tří heuristik k pozitivnímu výsledku. Kognitivní průchody UC 1.2 a UC 1.1 identifikovaly dvě drobná rizika (nutnost uzavřít cyklus pro vznik místnosti; znalost pojmu 3D kurzor) a obě jsou zmírněna vizuálními mechanismy nebo jsou akceptovatelná pro cílovou skupinu se základní znalostí programu Blender.

#pagebreak()
= Implementace

Kapitola implementace navazuje přímo na výsledky analýzy v kapitole @chap-analysis a technický návrh z kapitoly @chap-design. Východiskem je #gls("mvp", long: false) rozsah a třívrstvá architektura definovaná v sekci @sec-design-architecture. Implementace zachovává stejný datový tok i rozdělení odpovědností: čisté Python jádro řeší topologii a sémantiku, synchronizační vrstva je most do programu Blender a vizualizaci zajišťuje #gls("gn", long: false) modifikátor a #gls("ui", long: false) vrstva.

== Addon pro Blender

FloorPlanMaster se integruje do programu Blender jako Python balíček spuštěný přímo uvnitř Blender interpretu. Tato integrace je výrazně hlubší než pouhé přidání funkce: addon sdílí se softwarem stejný Python interpret, může registrovat vlastní typy, ovlivňovat chování viewportu a zachytávat události v reálném čase. Blender pro tuto formu integrace definuje dvojici funkcí --- funkci pro aktivaci, která zaregistruje veškeré operátory, panely a draw handlery addonu, a funkci pro deaktivaci, která vše bez zbytků odregistruje. Životní cyklus addonu je tak plně řízen systémem programu; addon nezanechává žádné vedlejší efekty mimo dobu své aktivace.

Izolace kódu závislého na Blenderu od čistého Pythonu nevznikla uměle v rámci návrhu, ale z bezprostřední praktické nutnosti. Jakmile byly napsány první testy pro strukturální graf, pytest okamžitě selhal: `import bpy` ve vrcholku modulu způsobil `ModuleNotFoundError`, protože mimo Blender Python interpret toto #gls("api", long: false) neexistuje. Vzor s podmíněným importem byl proto zaveden hned na začátku jako ochranný mechanismus, nikoliv jako dodatečná úprava kódu. Přímým důsledkem je, že veškerá základní logika --- topologické grafy, validátory, matematické utility --- je dostupná jako standardní Python balíček a pokrytá automatickými testy bez jakékoliv závislosti na Blenderu. Do budoucna je možné toto oddělení provést elegantněji, s čímž návrh i implementace počítají. 

Algoritmy pro detekci cyklů v planárních grafech jsou postaveny nad knihovnou NetworkX --- Python balíčkem třetí strany, který Blender ve svém interpretu nenabízí. Pro distribuci jako Blender Extension (formát zavedený v Blenderu 4.2) je NetworkX přibalen jako archiv ve formátu Python wheel přímo do balíčku addonu. Python dokáže z takového archivu importovat moduly přímo bez rozbalení. Vstupní bod addonu proto po spuštění přidá složku s archivem do vyhledávací cesty interpretu --- NetworkX se stane dostupným bez jakéhokoliv zásahu uživatele.


== Organizace modulů

Struktura složek a organizace modulů addonu reflektuje architekturu celého systému. Jednotlivé vrstvy jsou rozděleny dle svých logických a funkčních vlastností. Každý modul v `core/` a `utils/` smí importovat výhradně standardní Python knihovny a lokální moduly ze stejné úrovně --- nikoliv Blender moduly. Porušení pravidla se projeví okamžitě jako selhání testovací sady, která se spouští standardním pytestem. Složky `operators/`, `ui/` a `geometry/` naopak na Blender spoléhají plně. Oddělení je záměrně struktiní, bez hybridních modulů --- každý soubor patří buď do čistého Python světa, nebo do Blender světa, nikoliv do obou.

#block(breakable: false)[
```text
src/
├── __init__.py              # addon entry point
├── core/
│   ├── structural_graph.py  # Vrstva 1 — junction, wall topologie
│   ├── room_graph.py        # Vrstva 2 — room, synchronizace
│   ├── sync.py              # Vrstva 3 — Python grafy → Blender mesh
│   ├── final_mesh_builder.py
│   ├── junction_solver.py
│   └── validators.py        # sdílené funkce s chybovými kódy
├── operators/               # Blender modální operátory (FP1–FP4)
├── ui/                      # N-panel, overlay, properties
├── geometry/                # Geometry Nodes tree builder
├── utils/
│   ├── constants.py         # výchozí hodnoty, validační limity
│   └── math_helpers.py      # 2D geometrie, polygon area, centroid
├── tests/                   # pytest unit testy pro core/ a utils/
└── wheels/                  # bundlované .whl závislosti (networkx)
```
]

== Vrstvy

Třívrstvá architektura tvoří výpočetní jádro addonu. Porozumět jejímu fungování nejlépe umožňuje sledovat konkrétní událost: uživatel potvrdí nový vrchol v tužkovém nástroji a čeká, až se ve viewportu vytvoří nová stěna. Tato zdánlivě jednoduchá akce projde všemi třemi vrstvami a nakonec spustí reevaluaci #gls("gn", long: false) modifikátoru v C++ jádru Blenderu.

=== Vrstva 1 --- Strukturální graf

První vrstva přijme požadavek na přidání nového vrcholu a stěny a ještě než cokoliv zapíše do svého stavu, provede sadu validačních kontrol na vstupu: zda nová stěna není příliš krátká, zda na zadaných souřadnicích již neexistuje jiný vrchol, zda nevznikne duplicitní stěna. Pokud jakákoliv kontrola selže, vrstva požadavek odmítne a vrátí specifický chybový kód --- grafová struktura zůstane beze změny v platném stavu. Toto pravidlo platí pro všechny operace zápisu.

Pro efektivní vyhledávání blízkých vrcholů --- operaci klíčovou pro funkci přichycení v tužkovém nástroji --- udržuje Vrstva 1 prostorový index v podobě slovníku mapujícího zaokrouhlené souřadnice na identifikátor existujícího vrcholu. Dotaz na vrcholy v blízkosti dané polohy je tak operací v konstantním čase, nezávislou na celkovém počtu vrcholů v grafu.

Topologicky nejnáročnější operací Vrstvy 1 je detekce minimálních cyklů --- uzavřených stěnových smyček vymezujících potenciální místnosti. Implementace vychází z planárního embeddingu konstruovaného nad knihovnou NetworkX.

Planární embedding je reprezentace planárního grafu, která ke každému vrcholu ukládá cyklické pořadí jeho sousedů v rovině. Z tohoto pořadí lze algoritmicky odvodit hranice všech ohraničených oblastí --- tzv. faces planárního grafu --- aniž by bylo nutné provádět geometrické výpočty. Pro půdorys, jehož stěny tvoří planární graf, odpovídá každá ohraničená oblast právě jedné potenciální místnosti.

Z grafu jsou pak nejprve odstraněny listy, které součástí žádného cyklu být nemohou; poté se zkonstruuje planární embedding a z jeho hraniční struktury se extrahují všechny minimální ohraničené oblasti. Výsledkem je deterministická sada cyklů. Výsledek je uložen a invaliduje se pouze při změně topologie --- průběžné dotazy na seznam cyklů se tak nemusejí přepočítávat při každém dotazu nebo úpravy od uživatele.

Nejpodstatnější algoritmický problém Vrstvy 1 se projevil až při testování T-spojů a X-spojů. Prvotní implementace funkce pro výpočet rohů stěnového quadu procházela všechny sousední stěny v daném vrcholu a vybírala průsečík postranní přímky stěny s nejmenším absolutním parametrem $|t|$ podél přímky --- kde $t$ je skalární parametr parametrické rovnice přímky $P(t) = A + t dot.op arrow(d)$ udávající vzdálenost průsečíku od referenčního bodu $A$ ve směru $arrow(d)$. Pro L-spoje (dva sousedé ve vrcholu) tato strategie fungovala korektně. Jakmile se ale vrchol spojoval se třemi nebo více stěnami, `|t|` minimum vybíralo špatnou stranu --- rohový bod quadu přeskočil přes sousední stěnu a vytvořil překrývající se geometrii. Oprava vyžadovala přepracování výpočtu na algoritmus řazení podle úhlu (angular-sort): `_junction_entries()` seřadí všechny stěny v daném vrcholu podle úhlu jejich odchozího směru, čímž vznikne cyklus sousedů. Levý roh stěny se poté hledá jako průsečík levé postranní přímky stěny $i$ s pravou postranní přímkou angulárně-sousední stěny $i+1$ v CCW pořadí. Tento přístup je deterministický pro libovolný počet stěn ve vrcholu.

=== Vrstva 2 --- Graf místností

Vrstva 2 reaguje na dokončení operace ve Vrstvě 1 a synchronizuje svůj stav s aktuálním seznamem minimálních cyklů. Tato synchronizace neprobíhá průběžně při každé dílčí změně, ale vždy až po dokončení celé uživatelské operace. Synchronizace porovná aktuální sadu cyklů s množinou stávajících místností na základě kanonického klíče každého cyklu --- setříděné množiny jeho hraničních stěn. Nové smyčky dostanou nové objekty místností; smyčky, které z topologie zmizely, jsou odstraněny spolu se svými metadaty; zachované smyčky zůstávají nedotčeny --- jejich jméno, typ a ostatní atributy jsou stabilní.

Tato volba není nahodilá: alternativou bylo sledovat identitu cyklu přes pořadí vrcholů nebo přes první stěnu smyčky, ale obě alternativy jsou nestabilní při geometrických editacích. Přidání nové stěny do smyčky může změnit pořadí vrcholů i první stěnu při procházení. Konkrétní příklad: místnost tvoří čtyři stěny $S_1, S_2, S_3, S_4$ a uživatel ji pojmenuje „Obývací pokoj". Pokud by byl klíč místnosti určen pořadím vrcholů při průchodu $[J_1, J_2, J_3, J_4]$, pak přidání nové příčky kdekoliv jinde v půdorysu --- zcela mimo tuto místnost --- může průchod planárním embeddingem provést vrcholy v jiném pořadí $[J_2, J_3, J_4, J_1]$, čímž by vznikl jiný klíč a místnost by ztratila přiřazené jméno. Setřízená množina #gls("uuid", long: false) $\{S_1, S_2, S_3, S_4\}$ je naopak neměnná vůči pořadí procházení: dokud se nemění hraniční stěny místnosti, klíč zůstává stejný bez ohledu na zbytek půdorysu. Tato volba má přímý dopad na uživatelský zážitek: pojmenování a metadata místnosti "přežijí" topologicky nesouvisející úpravy, které by jiným přístupem způsobily ztrátu identity.


=== Vrstva 3 --- Synchronizace s Blenderem

Vrstva 3 překládá Python datový model do formátu, jemuž Blender a Geometry Nodes rozumějí. Jejím výstupem je jeden Blender mesh objekt --- tzv. base mesh půdorysu --- nesoucí topologii i parametry ve formě pojmenovaných atributů čitelných přímo z #gls("gn", long: false) stromu.

Plná synchronizace probíhá ve dvou fázích. V první fázi se mesh rekonstruuje od nuly: pro každou stěnu se vypočítá přesný čtyřúhelníkový obrys v rovině XY pomocí `junction_solver.py` (zmíněný angular-sort nad stěnami v každém vrcholu), aby spoje fungovaly pro libovolné úhly bez mezer a přesahů. Na vrcholech se třemi a více stěnami se doplní výplňový polygon spoje a pro každý otvor se vytvoří šestistěnný cutter box. Současně se dopočte a vloží podlahový polygon místnosti po vnitřní hraně stěn.

Ve druhé fázi se přes `mesh.attributes` zapíší per-face atributy: `is_wall`, `is_opening`, `wall_id`, `wall_height`, `wall_thickness`, `room_id`, `room_area` a `room_perimeter`. Tím je zaručeno, že hodnoty jsou ihned dostupné pro Geometry Nodes. Po zápisu se objekt pouze označí pro přepočet (`update_tag`) a reevaluace proběhne až při redraw; synchronizace záměrně nevolá explicitní synchronní update depsgraphu.

Implementace Vrstvy 3 prošla v průběhu vývoje jedním zásadním přepisem. Ten se týkal strategie generování stěnové geometrie. Prvotní implementace generovala stěny jako per-edge instance 3D kvádrů (MeshToPoints na hranách → InstanceOnPoints) s parametry rotace a škálování z atributů. Problémem bylo, že kvádry mají 90° čela, která neumožňují geometricky přesné spoje pro libovolné úhly: na T-spojích a X-spojích se kvádry překrývaly. Přechod na strategii _quad polygon + extrude_ --- kde každá stěna je 2D čtyřúhelník vypočítaný z průsečíků postranních přímek sousedních stěn --- odstranil problém překryvů strukturálně.

=== Geometry Nodes --- generování 3D geometrie

#gls("gn", long: false) modifikátor přebírá od Vrstvy 3 připravenou základní síť (base mesh) a autonomně generuje finální trojrozměrnou geometrii. #gls("gn", long: false) strom je sestaven při první aktivaci addonu a nese interní číslo verze; při nesouladu verze se strom automaticky přebuduje. Tok zpracování ve stromu probíhá ve třech krocích: oddělení stěnových plošek (`is_wall == 1`), oddělení ořezových ploch otvorů (`is_opening == 1`) a vytažení stěn podle lokální výšky (`wall_height`).

Kritický problém #gls("gn", long: false) fáze přišel s implementací dveřních otvorů. Exaktní booleovský řešič (#gls("gn", long: false) uzel Mesh Boolean s metodou DIFFERENCE/EXACT) vyžaduje zcela uzavřenou ořezovou síť (watertight cutter mesh), jejíž geometrie nesmí zasahovat mimo těleso, do kterého řeže. Ořezové těleso (cutter) pro dveře začínalo na `z = 0` --- přesně na spodní ploše stěny. Numerická tolerance exaktního řešiče tento stav vyhodnotila jako průsečík s podlahou stěny, což vedlo k nestabilnímu chování: díra buď nevznikla vůbec, nebo řešič zobrazil ořezové těleso jako solidní objekt. Okenní otvory přitom fungovaly bezchybně, protože jejich geometrie začíná na výšce parapetu (`z = sill_height - ε > 0`) --- celé těleso leží uvnitř stěnového polygonu. Oprava pro dveře spočívala v posunutí dolní hrany geometrie na `z = +0,01 m` (konstanta `OPENING_CUTTER_Z_OVERSHOOT`), čímž se vyloučila numerická interakce s podlahou. Výsledná mezera 1 cm u podlahy dveří je v praxi nepozorovatelná a pro účely addonu zanedbatelná. Do budoucna by bylo ideální problém vyřešit exaktním výřezem a opravou geometrie, aby při práci nevznikaly nežádoucí artefakty.

== Funkce

Funkce addonu jsou implementovány jako Blender operátory --- spustitelné příkazy registrované u Blenderu a přiřazené klávesovým zkratkám nebo tlačítkům panelu. Každý operátor pracuje výhradně přes rozhraní datových vrstev a tvoří tak řídicí vrstvu (Controller) #gls("mvc", long: false) architektury popsané v návrhu v sekci @sec-design-architecture. Operátory nestojí na sobě navzájem --- každý je samostatnou jednotkou, přistupující ke sdílené cache grafů a sdílenému stavu výběru přes definovaná rozhraní.

=== FP1 --- Nástroj tužka

Nástroj tužka je primárním způsobem kreslení stěn a je implementován jako modální operátor. Operátor funguje jako stavový automat se třemi stavy. První stav je neaktivní, kdy nástroj čeká na aktivaci, ale je zvolen v přes ikonu v tool baru. V druhém čeká na určení výchozího bodu nové stěny; ve třetím táhne náhledovou linku od posledního potvrzeného vrcholu ke kurzoru a čeká na potvrzení dalšího bodu. Každé potvrzení vrcholu zapíše novou entitu do Vrstvy 1; stiskem klávesy pro zrušení posledního kroku je tato entita odstraněna a operátor se vrátí o jeden krok zpět. Ukončení sekvence --- klávesou nebo uzavřením smyčky --- spustí finální synchronizaci: Vrstva 2 automaticky detekuje další mínosti, Vrstva 3 zapíše výsledný mesh a Geometry Nodes generují 3D geometrii.

Vývoj tužkového nástroje byl doprovázen sérií propojených problémů, z nichž většina se projevila teprve při testování s reálnou dispozicí obsahující přibližně čtyřicet stěn. Prvním a nejzávažnějším byl výkonnostní problém: každý potvrzený vrchol spouštěl plnou synchronizaci Vrstvy 3 --- přepočet stěnových obrysů, zápis osmi pojmenovaných atributů, přepočítání #gls("gn", long: false) modifikátoru a serializaci grafů do #gls("json", long: false) custom property. S rostoucím počtem stěn cena každého kliknutí rostla lineárně, přičemž celková cena za nakreslení sekvence $W$ stěn dosahovala $O(W^2)$. Řešením bylo přesunutí plné synchronizace na konec celé kreslicí sekvence a náhrada okamžité (per-klik) vizualizace čistě Pythonovými výpočty stěnových obrysů bez volání `bpy`. Výpočetní náročnost na jedno kliknutí klesla na $O(W)$; přepočet uzlů #gls("gn", long: false) proběhne pouze jednou při ukončení nástroje.

Druhým problémem byla obnova pohledu po deaktivaci. Prvotní implementace obnovovala uloženou matici pohledu bezpodmínečně --- pokud uživatel v průběhu kresby ručně otočil viewport a ukončil nástroj z perspektivy, pohled nechtěně přeskočil zpět na uloženou horní ortografii. Oprava podmínila obnovu pohledu: matice se obnoví pouze tehdy, pokud viewport stále zobrazuje horní ortografii, jinak se zachová aktuální pohled uživatele.

#figure(
  image("/typst/assets/pencil_tool_2.png", width: 85%),
  caption: [Začátek kreslení první stěny pro navazující místnost],
) <fig-toolbar>

#figure(
  image("/typst/assets/pencil_tool_3.png", width: 90%),
  caption: [Preview doposud vytvořených stěn v aktuální sekvenci stěn],
) <fig-toolbar>

#figure(
  image("/typst/assets/pencil_tool_4.png", width: 90%),
  caption: [Uzavření cyklu nové navazující místnosti],
) <fig-toolbar>

#figure(
  image("/typst/assets/pencil_tool_5.png", width: 90%),
  caption: [Potvrzení nových stěn a automatická detekce nové místnosti],
) <fig-toolbar>


=== FP2 --- Výběr a parametrické úpravy

Interaktivní editace běží v dedikovaném FloorPlan módu, který je implementován jako modal controller nad viewportem. Tento režim přebírá ne-navigační události, chrání před nechtěnými globálními zkratkami a centralizuje klikací výběr stěn i místností. Výběr funguje nezávisle na pohledu kamery: implementace testuje klik vůči projekci šesti ploch 3D tělesa stěny (top, bottom, čtyři boky), takže funguje i v perspektivním pohledu.

Výsledek výběru se zapisuje do sdíleného `SelectionState` a N-panel okamžitě zobrazuje parametry vybrané entity. Parametrické úpravy stěn pokrývají nejen tloušťku a výšku, ale i polohu: samostatnou editaci obou koncových vrcholů (Start/End XY) a posun stěny po normále přes ovladač středu. Funkce zpětného volání (callbacky) využívají ochranné příznaky proti zacyklení a při rychlé manipulaci s posuvníky se uplatňuje odložená synchronizace (debouncing).

/* 
Přidávání otvorů vynucuje geometrická omezení už při zadávání: otvor nesmí přesáhnout délku stěny, nesmí vstoupit do junction inset zón a nesmí se překrývat s jiným otvorem. Dialog průběžně clampuje hodnoty tak, aby nikdy nevznikl neplatný stav. Součástí FP2 jsou i destruktivní operace: odstranění vybrané stěny a odstranění místnosti při zachování sdílených stěn sousedních místností.

Vložení místnosti umístí pravoúhlý půdorys na aktuální pozici 3D kurzoru se zadanými rozměry jako transakci Vrstvy 1. */

#figure(
  image("/typst/assets/select_wall_1.png", width: 100%),
  caption: [Výběr místnosti pro úpravu v FloorPlan módu],
) <fig-toolbar>

#figure(
  image("/typst/assets/select_wall_2.png", width: 100%),
  caption: [Parametrický posun vybrané místnosti podle své normály],
) <fig-toolbar>

Výběr stěn kliknutím do viewportu prošel dvěma zcela odlišnými implementacemi. Prvotní přístup projektoval pozici myši na rovinu Z=0 a testoval, zda bod leží uvnitř 2D quadu stěny. Tato metoda fungovala v ortografickém top-down pohledu, ale selhávala v perspektivním pohledu nebo při pohledu šikmém: kliknutí na horní hranu 3D stěny se na rovině Z=0 projektovalo mimo stěnu --- do středu místnosti. Přechod na screen-space testování šesti ploch 3D tělesa stěny (top, bottom, čtyři boky) situaci vyřešil: každá plocha se projektuje do 2D souřadnic obrazovky a klik se testuje vůči výsledným 2D polygonům. Tato metoda funguje v libovolném pohledu a přirozeně zohledňuje hloubku.

Přidávání otvorů přineslo nejsložitější validační logiku celého addonu. Otvor nesmí přesáhnout délku stěny, nesmí zasahovat do junction inset zóny a nesmí se překrývat s jiným otvorem. Hodnoty se průběžně omezují (clampují) v metodě `check()` Blender dialogu. Při implementaci se ukázalo, že pořadí omezování rozhoduje: pokud se nejprve omezí šířka a pak poloha, pohyb středu otvoru ke kraji může neočekávaně zúžit otvor. Správné chování --- výška je fixní, parapet se zastaví u stropu, šířka je konstanta stěny nezávislá na poloze --- vyžadovalo přesnou specifikaci invariantů ještě před psaním kódu omezovací logiky.

#figure(
  image("/typst/assets/insert_opening_1.png", width: 100%),
  caption: [Vložení parametrického otvoru dveří a úprava jeho hodnot v rámci Undo panelu],
) <fig-toolbar>

#figure(
  image("/typst/assets/insert_opening_2.png", width: 100%),
  caption: [Vložení další paramerického otvoru, tentokrát okna a úprava jeho hodnot],
) <fig-toolbar>

=== FP3 --- Metadata místností

Jakmile Vrstva 2 detekuje novou uzavřenou smyčku stěn, vytvoří odpovídající objekt místnosti s automaticky vypočítanou plochou, obvodem a polohou těžiště (centroidu). Uživatel může místnosti procházet v N-panelu, kde je zobrazen jejich seznam s klíčovými metrikami, a každou místnost přejmenovat. Přejmenování probíhá obousměrně: změna provedená v panelu se zapíše do grafu místností a zároveň se trvale uloží do objektu v Blenderu tak, aby se zachovala i po znovunačtení souboru nebo kroku zpět (Undo).

Implementace pokrývá základní identifikaci, přejmenování a zobrazení klíčových metrik. Zároveň obsahuje jednoduché zobrazení hierarchie stěn pro danou místnost. Seznam lze zobrazit a parametry upravit pouze tehdy, je-li uživatel v aktivním pracovním režimu. Plná správa sémantických atributů místností ve smyslu celého návrhu --- materiály, typy povrchů --- tato verze addonu neimplementuje. Je ale připravena pro budoucí rozšíření a implementaci v dalších verzích.

Implementace metadat místností odhalila specifický problém ukládání jmen přes historii kroků (Undo) a po opětovném načtení. Jméno místnosti je uloženo v paměti jako Python objekt (`Room.name`), který systém Zpět/Vpřed neobnovuje --- Blender při Undo obnoví síť (mesh), ale Python grafy v `_graph_store` zůstanou ve stavu po poslední operaci. Výsledkem je, že přejmenování místnosti provedené před krokem zpět může zůstat zachováno, i když topologie se vrátila. Řešením je zápis jmen místností do #gls("json", long: false) custom property při každé synchronizaci a jejich zpětná rekonstrukce z #gls("json", long: false) formátu při každém `reset_graphs_for_obj()`. Tím je polygonální síť vždy primárním zdrojem dat a Python objekty slouží pouze jako odvozená mezipaměť (cache), kterou lze ze sítě kdykoliv obnovit.

=== FP4 --- Finalizace a zapečení modifikátorů

FP4 je implementováno operátorem Bake (zapečení), který převádí parametrický objekt půdorysu na statickou polygonální síť, připravenou pro další práci nebo export. Operátor před zapečením nejprve rekonstruuje grafy ze stavu objektu, potom vygeneruje finální geometrii přes specializovaný skript pro tvorbu sítě a odstraní procedurální identitu objektu. Uživatel může zvolit nedestruktivní variantu (ponechat originál a vytvořit takto zpracovanou kopii) i destruktivní variantu.

/* 
Finalizační krok zahrnuje i úklid dat: převod rohových `float2` atributů na #gls("uv", long: false) vrstvy, volitelné odstranění pojmenovaných atributů a přiřazení výchozího materiálu. Součástí implementace je také ochrana vstupu do režimu úprav (Edit Mode): při pokusu o přechod na ruční editaci sítě se zobrazí varovný dialog s volbami Cancel, Bake nebo Lose Data, aby přechod ze sémantického modelu na běžný objekt byl vždy explicitní. */

Finalizační operátor překonává architektonické oddělení procedurálního a statického modelu. Parametrický objekt modelu nese celou historii topologie v #gls("json", long: false) formátu a vizualizaci přenechává na #gls("gn", long: false) modifikátoru; statická síť oproti tomu obsahuje jen prostá geometrická data bez sémantiky. Před samotným zapečením operátor zrekonstruuje grafy z aktuálního stavu objektu, vygeneruje finální geometrii přes `final_mesh_builder.py` s přesnými spoji a odstraní #gls("gn", long: false) modifikátor i #gls("json", long: false) vlastnost. Ochrana vstupu do režimu úprav zabraňuje situaci, kdy by uživatel neúmyslně přepsal #gls("gn", long: false) síť ručními úpravami: obslužný proces (handler) zachytávající přechod do editace sítě nabídne tři volby --- zrušit přechod, provést Bake a pak editovat, nebo vstoupit a ztratit sémantická data. Tato ochrana brání neočekávaným chybám, které by jinak vznikly použitím standardních nástrojů Blenderu na procedurálním objektu.

#figure(
  image("/typst/assets/bake_1.png", width: 100%),
  caption: [Floor Plan objekt před exportem pomocí operátoru Bake],
) <fig-toolbar>

#figure(
  image("/typst/assets/bake_2.png", width: 100%),
  caption: [Výsledný mesh po vygenerování přes operátor Bake],
) <fig-toolbar>

=== Neimplementované funkce

V aktuální verzi zůstávají neimplementované kontextové menu (FP5), 3D manipulátory (FP6) a automatické kótování (FP7). Export jako samostatný cílový výstupní krok nad rámec bake workflow také není dokončen. Architektura je však navržena tak, aby šlo tyto části doplnit jako izolované operátory bez zásahu do datového jádra.

== Uživatelské rozhraní <sec-impl-ui>

Architektura #gls("ui", long: false) --- N-panel jako centrum interakce, overlay manager jako centrální dispatcher #gls("gpu", long: false) vizualizace vzorem Mediátor a sdílený stav výběru jako modulová proměnná bez vazby na Blender vlastnosti --- byla realizována dle návrhu v sekcích @sec-design-ui. Tato kapitola popisuje implementační rozhodnutí a rozšíření, která vznikla nad rámec návrhu.

=== N-panel

/* Stav rozbalení záznamu místnosti v N-panelu je persistován přímo jako custom property na FloorPlan objektu (`room_expanded_{room_id}`). Alternativami byly modul-level slovník (smazán při addon reloadu) nebo `Scene PropertyGroup` (sdílená přes všechny FloorPlan objekty). Objekt jako nosič stavu je správná volba: stav rozbalení je atribut konkrétní instance, přežije reload souboru a je automaticky součástí undo stacku. */

Při implementaci N-panelu vyvstala otázka, kde persistovat vizuální stav rozhraní --- konkrétně stav rozbalení záznamu místnosti. Modul-level Python slovník je smazán při reloadu addonu; přiřazení do `bpy.types.Scene` by sdílelo stav přes všechny FloorPlan objekty ve scéně, čímž by rozbalení místnosti v jednom projektu ovlivnilo zobrazení v jiném. Správným nosičem se ukázal samotný FloorPlan objekt jako Blender datový blok: custom property `room_expanded_{room_id}` je automaticky součástí `.blend` souboru, přežívá reload a je součástí Undo stacku --- uživatel může Ctrl+Z obnovit nejen geometrii, ale i stav rozbalení panelu.

=== Overlay manager <sec-overlay-manager>

/* Implementace přidává odolnostní chování vůči chybám v jednotlivých vrstvách, které návrh neřešil: `_report_layer_failure()` odchytí výjimku z libovolné overlay vrstvy, vypíše podrobnou hlášku do konzole a zaeviduje klíč chyby do sady `_reported_failures`. Opakovaně selhávající vrstva nevypíše log na každý frame, ale pouze jednou, čímž se zabrání zahlcení konzole při runtime chybě.

Oproti obecnému popisu overlay vrstev v návrhu bylo implementováno pět konkrétních vrstev:

- `wall_selection.py` a `room_selection.py` --- interakční zvýraznění vybrané stěny oranžovým OBB boxem a vybrané místnosti; dle návrhu
- `labels.py` --- textové popisky místností (název + plocha v centroidu) ve viewportu; dle návrhu
- `wall_opening_highlight.py` --- pasivní vrstva, vždy viditelná pro každý viditelný FloorPlan objekt bez ohledu na výběr; kreslí hrany všech stěnových boxů černě a hrany otvorů barevně dle typu (dveře azurově, okna fialově); vrstva nebyla explicitně navržena --- vznikla z potřeby vizuálně odlišit otvory ve scéně nezávisle na výběru, aby byl půdorys čitelný i mimo aktivní sémantický mód
- `active_floorplan_hint.py` --- textový hint v levém dolním rohu viewportu zobrazující název aktivního FloorPlan objektu; vrstva nebyla v návrhu; přidána pro orientaci v scénách s více FloorPlan objekty */

#gls("gpu", long: false) overlay architektura prošla zásadním refaktorem (Issue #38). Původní implementace registrovala `draw_handler_add` přímo v každém modulu a operátoru: pencil tool, select wall i room selection měly každý vlastní handler. Výsledkem byl nekontrolovaný počet handlerů bez centrálního cleanup mechanismu; při reloadu addonu nebo při výjimce v `unregister()` mohly handlery přetrvat a způsobit přístup do neplatné paměti při dalším redraw. Centrální overlay manager registruje jediný POST_VIEW a jediný POST_PIXEL handler, které dispatchují do listů registrovaných layer callbacků. Přidání nové overlay vrstvy vyžaduje vytvoření jednoho souboru v `ui/overlays/` a jedno volání `register_layer()` v `register()` --- bez jakékoliv změny v handler logice.

Praktickým důsledkem refaktoru bylo oddělení persistentních vrstev (wall selection highlight, room highlight, labels) od transientních vrstev (pencil tool kreslení preview). Transientní vrstvy se registrují v `invoke()` a odregistrují v `_finish()` --- bezpečně i při abnormálním ukončení operátoru. Odolnostní mechanismus `_report_layer_failure()` zajišťuje, že výjimka v libovolné vrstvě způsobí jednorázový log do konzole, ale nerozhodí zbytek overlay systému. Oproti návrhu přibyly dvě vrstvy, které nebyly explicitně navrženy: `wall_opening_highlight.py` (pasivní vizualizace hrany stěn a barevné rozlišení otvorů nezávisle na výběru) a `active_floorplan_hint.py` (orientační hint pro scény s více FloorPlan objekty).

=== Sdílený stav výběru

/* `SelectionState` byl rozšířen o dvě pole, která návrh neobsahoval.

Pole `object_name` uchovává název FloorPlan objektu, ke kterému aktuální výběr patří. Bez tohoto pole by overlay vrstvy a `poll()` funkcí panelů nemohly rozlišit, zda vybraná stěna patří aktivnímu, či jinému FloorPlan objektu --- ve scéně s více FloorPlan objekty by se pak zobrazovaly vlastnosti stěny z jiného objektu, než na který uživatel kliká. Metody `belongs_to_object(obj)`, `has_wall_for_object(obj)` a `has_room_for_object(obj)` centralizují tuto kontrolu tak, aby ji volající kód nemusel reimplementovat.

Pole `room_viewport_selected` rozlišuje, zda místnost byla vybrána kliknutím ve viewportu (`True`) nebo pouze rozbalením záznamu v N-panelu (`False`). `poll()` top-panelu vlastností místnosti tuto hodnotu čte a zobrazí top-panel pouze při kliknutí ve viewportu, aby při procházení seznamu místností v N-panelu panel samovolně neposouvalo a nerušilo práci. */

Prvotní implementace uchoávala #gls("uuid", long: false) vybrané stěny jako `StringProperty` v `FloorPlanSettings` (Scene PropertyGroup). Tato volba se ukázala jako chybná ze dvou důvodů. Za prvé, `StringProperty` je persistovaná v `.blend` souboru a po Undo/Redo může ukazovat na #gls("uuid", long: false), které již neodpovídá aktuálnímu stavu grafu. Za druhé, programatické přiřazení #gls("uuid", long: false) v select operátoru spouštělo PropertyGroup callback, který inicioval sync --- kruhová závislost zastavitelná pouze příznakovým guardem `_updating_wall_props`. Přesun #gls("uuid", long: false) do module-level `SelectionState` singletonu oba problémy odstranile: #gls("uuid", long: false) žije výhradně v Pythonu mimo Blender property systém, nevyvolává callbacky a je vždy konzistentní s aktuálním stavem grafů.

`SelectionState` byl nad rámec návrhu rozšířen o dvě pole. Pole `object_name` uchovává název FloorPlan objektu, ke kterému výběr patří --- bez něj by overlay vrstvy a `poll()` funkcí panelů nemohly rozlišit, zda vybraná stěna patří aktivnímu, nebo jinému FloorPlan objektu ve scéně. Pole `room_viewport_selected` rozlišuje výběr kliknutím ve viewportu od pouhého rozbalení záznamu v N-panelu --- `poll()` top-panelu vlastností místnosti zobrazí panel pouze při kliknutí ve viewportu, aby procházení seznamu místností v N-panelu panel samovolně neposouvalo.

== Současná omezení implementace

/* Implementace addonu pokrývá rozsah definovaný v návrhu jako #gls("mvp", long: false). Řada funkčních oblastí zůstala záměrně mimo tento rozsah --- buď z důvodu prioritizace základní kreslicí a editační pipeline, nebo proto, že jejich správná realizace vyžaduje koordinaci více vrstev architektury a přidání nad rámec #gls("mvp", long: false) by ohrozilo stabilitu jádra. */

Tato kapitola shrnuje oblasti, které nebyly součástí #gls("mvp", long: false) rozsahu, nebo kde implementace odhalila technické omezení, jehož oprava by vyžadovala strukturální zásah. U každé oblasti je uveden i rozsah potřebných doimplementací, aby byl výchozí bod pro navazující vývoj konkrétní.

/* *Transformace FloorPlan objektu.* Implementace předpokládá, že FloorPlan objekt leží v počátku souřadnicového systému světa s identitní rotací a jednotkovým měřítkem. Pokud uživatel přesune objekt klávesou G nebo jej otočí klávesou R, Blender posune nebo otočí vizuální reprezentaci objektu, ale při příští synchronizaci Vrstvy 3 jsou vrcholy meshe přepsány z L1 souřadnic, které transformaci neznají --- geometrie se vizuálně vrátí do původní lokální polohy. Architektura na tuto funkci připravena je: přidání transformace spočívá v jedné systematické změně v `sync.py` --- při zápisu vrcholů do bmesh se každá L1 souřadnice transformuje inverzí `obj.matrix_world`. Žádná strukturální změna datového modelu není potřeba. */

*Transformace FloorPlan objektu.* Přesunutí nebo otočení FloorPlan objektu klávesami G, R ve Blenderu má neočekávaný efekt: při příší synchronizaci Vrstvy 3 jsou vrcholy meshe přepsány z L1 souřadnic, které o transformaci neví, a geometrie se vizuálně vrátí do původní lokální polohy. Problém vznikl tím, že souřadnice vrcholů se zapisují přímo jako lokální souřadnice objektu bez aplikace `matrix_world`. Architektura na opravu připravena je: stačí transformovat každou L1 souřadnici inverzí `obj.matrix_world` při zápisu do bmesh v `sync.py`. Pohyb junctions v operátorech musí naopak transformovat souřadnice myši z world space do lokálního prostoru. Žádná strukturální změna datového modelu není potřeba.

/* *Duplikování FloorPlan objektu.* Příkaz Shift+D vytvoří nový Blender objekt se zkopírovanými custom properties včetně serializovaného #gls("json", long: false) grafu. Po aktualizaci depsgraphu addon detekuje nový objekt a rekonstruuje pro něj nezávislé Python grafy. Tím však přežijí identické UUID pro všechny junctions, stěny, otvory a místnosti --- v `_graph_store` existují dva nezávislé grafy se shodným UUID prostorem, což může způsobit neočekávané chování. Navíc Blender do explicitního unlinkování sdílí mezi oběma objekty datový blok meshe: synchronizace jednoho objektu přepíše mesh, který vidí oba. Podpora duplikování vyžaduje dvě doimplementace: generování nových UUID při rekonstrukci grafu z kopírovaného #gls("json", long: false) a vynucené odlinkování datového bloku meshe ihned po detekci duplikátu. */

*Duplikování FloorPlan objektu.* Příkaz Shift+D zkopíruje custom properties i serializovaný #gls("json", long: false) graf a addon pro duplicitní objekt rekonstruuje nezávislé Python grafy se shodnými #gls("uuid", long: false). V `_graph_store` tak existují dva grafy se stejným #gls("uuid", long: false) prostorem, což může způsobit kolize při operacích odvolávajících se na #gls("uuid", long: false) napříč objekty. Navíc Blender sdílí datový blok meshe mezi oběma objekty do explicitního unlinkování: synchronizace jednoho přepíše mesh, který vidí oba. Oprava vyžaduje dvě doimplementace: přegenerování #gls("uuid", long: false) při rekonstrukci grafu z kopírovaného #gls("json", long: false) a vynucené odlinkování datového bloku meshe ihned po detekci duplikátu.

/* *Přejmenování FloorPlan objektu.* `_graph_store` je slovník klíčovaný řetězcovým jménem objektu. Přejmenování objektu (F2) změní `obj.name` v Blenderu, ale addon nemá registrovaný handler pro událost přejmenování --- `_graph_store` stále obsahuje grafy pod starým klíčem a sémantický mód se tiše přeruší. Oprava je lokalizovaná: buď přejít na klíčování podle stabilnějšího identifikátoru, nebo registrovat `bpy.app.handlers.depsgraph_update_post` handler, který detekuje rozdíl a přeindexuje příslušný záznam. */

*Přejmenování FloorPlan objektu.* Přejmenování objektu klávesou F2 změní `obj.name` v Blenderu, ale `_graph_store` zůstane indexovaný pod starým jménem. Žádný handler na přejmenování není registrovaný, takže sémantický mód se tiše přeruší: operátory nenajdou grafy pod novým klíčem a chovají se, jako by objekt neměl žádnou historii. Oprava je lokalizovaná a nevyžaduje zásah do datového modelu: buď přejít na klíčování podle stabilnějšího identifikátoru (`obj.data.name`), nebo registrovat `bpy.app.handlers.depsgraph_update_post` handler, který porovná uložené jméno s aktuálním a přeindexuje příslušný záznam.

/* *Paralelní práce s více FloorPlan objekty.* `_mode_object_name` je jednoduché module-level stringové pole --- v sémantickém módu může být nejvýše jeden FloorPlan objekt najednou. Tato vlastnost je záměrná: v rámci #gls("mvp", long: false) priority bylo zvoleno jednoduché a robustní řešení pro jednoobjektový scénář. Addon ale v ostatních ohledech s existencí více FloorPlan objektů ve scéně počítá --- `_graph_store` udržuje grafy pro všechny z nich a pasivní overlay vrstva `wall_opening_highlight.py` kreslí stěny a otvory každého viditelného FloorPlan objektu bez ohledu na to, který je aktivní. */

*Paralelní práce s více FloorPlan objekty.* V sémantickém módu může být aktivní nejvýše jeden FloorPlan objekt najednou: `_mode_object_name` je jednoduché module-level pole a `SelectionState` drží jediné `object_name`. Tato vlastnost je záměrná a odpovídá #gls("mvp", long: false) prioritě. Addon s více FloorPlan objekty ve scéně v ostatních ohledech počítá: `_graph_store` udržuje grafy pro všechny z nich a pasivní overlay vrstva `wall_opening_highlight.py` vizualizuje stěny a otvory každého viditelného FloorPlan objektu. Rozšíření na plnohodnotnou podporu by vyžadovalo přepracování `_mode_object_name` a `SelectionState` z jednoduché hodnoty na slovník nebo sadu a úpravu `find_floorplan_obj(context)` --- datový model ani vrstvy 1--3 žádnou úpravu nepotřebují.

/* *Persistence stavu módu a výběru.* Po načtení souboru je sémantický mód vždy vypnutý a výběr prázdný --- `_mode_object_name` a `SelectionState` jsou module-level proměnné mimo Blender undo stack a nejsou serializovány do `.blend` souboru. Jde o záměrné bezpečné výchozí chování: po restartu Blenderu nebo načtení souboru začíná uživatel v neutrálním stavu a musí mód aktivovat explicitně (Shift+Q). Geometrie, grafy a veškerá topologická data jsou perzistovaná přes #gls("json", long: false) custom property `_floorplan_graphs` a jsou korektně rekonstruována. */

*Persistence stavu módu a výběru.* Po načtení souboru je sémantický mód vždy vypnutý a výběr prázdný. `_mode_object_name` a `SelectionState` jsou module-level Python proměnné mimo Blender undo stack a nejsou serializovány do `.blend` souboru --- jde o záměrné a bezpečné výchozí chování. Uživatel po otevření souboru začíná v neutrálním stavu a aktivuje mód explicitně (Shift+Q). Geometrie, grafy a veškerá topologická data jsou naopak plně perzistovaná: #gls("json", long: false) custom property `_floorplan_graphs` je součástí `.blend` souboru a grafy se z ní korrektně rekonstruují po každém načtení.

*Použitelnost --- riziková místa.* Manuální testování identifikovalo dvě místa, která mohou způsobovat potíže zejména uživatelům bez předchozí zkušenosti s addonem. Prvním je aktivace FloorPlan módu: klávesová zkratka Shift+Q není v rozhraní viditelně indikována a uživatel, který mód neaktivuje, může nabýt dojmu, že addon nereaguje, přestože je ve scéně přítomen FloorPlan objekt. Nápravou by bylo přidat upozornění přímo ve viewportu indikující neaktivní mód, nebo zpřístupnit aktivaci primárně přes tlačítko v N-panelu --- obě varianty nevyžadují zásah do datového modelu. Druhým rizikovým místem je vizuální zpětná vazba při clamping otvorů: pohyb středu otvoru ke kraji stěny šířku otvoru nemění a výška parapetu se zastaví u stropu bez informace o provedené úpravě, takže uživatel neví, proč se jím zadaná hodnota nezobrazuje. Obě omezení lze adresovat na úrovni UI.

== Směr navazujícího vývoje

Implementace popsaná v této kapitole tvoří funkční základ, na nějž lze navázat ve třech navzájem nezávislých oblastech: opravou zmíněných nedostatků, doplněním zbývajících částí #gls("mvp", long: false) a rozšířením mimo jeho rámec.

Čtyři omezení popsaná v předchozí podkapitole --- transformace objektu, duplikování, přejmenování a jednoobjektový sémantický mód --- jsou nedostatky s přesně identifikovaným místem zásahu, nikoliv projevy chyb v architektonickém návrhu. Pro každé z nich existuje v kódu konkrétní bod napojení: `sync.py` pro aplikaci `matrix_world` při zápisu vrcholů do meshe, `depsgraph_update_post` handler pro přeindexaci `_graph_store` po přejmenování, přegenerování #gls("uuid", long: false) s vynuceným unlinkováním datového bloku meshe pro případ duplikování a rozšíření `_mode_object_name` a `SelectionState` ze skalárních hodnot na množiny pro souběžně aktivní objekty. Datový model ani vrstvy 1--3 žádnou z těchto oprav nevyžadují.

Tři funkční oblasti z původního návrhu zůstaly mimo #gls("mvp", long: false) rozsah a pro každou z nich je v kódu předpřipraven konkrétní opěrný bod. Kontextové menu (FP5) je ze zbývajících funkcí nejblíže dokončení: `_pick_element()` v `select_wall.py` vrací typovaný výsledek `('wall', uuid)` nebo `('room', uuid)` a samotná nabídka je věcí nového Blender operátoru bez zásahu do logiky výběru. 3D manipulátory (FP6) mohou přímo vyjít z výstupů `junction_solver.py` --- přesné rohové body stěnového quadu jsou dostupné pro každý endpoint, overlay manager poskytuje kreslicí kontext a `move_junction_xy()` v `StructuralGraph` je vstupní branou pro napojení gizma. Automatické kótování (FP7) pracuje výhradně s daty Vrstvy 1 --- délkami stěn a souřadnicemi vrcholů --- a kreslení kót přes BLF draw handler je přirozené rozšíření stávající overlay architektury bez dotyku synchronizační vrstvy. Vedle samotných funkcí jsou v kódu explicitně sledovány záměrně odložené datové atributy: `Wall.is_bearing`, `Room.wall_color`, `Adjacency.connection_type` a `Adjacency.openings`. Datová struktura pro ně připravena je; jejich aktivace nevyžaduje refaktor, pouze doplnění konkrétních hodnot a rozšíření UI.

Za hranicemi původního zadání se nabízejí tři přirozené směry navazujícího rozvoje, pro něž jsou architektonické podmínky splněny již v aktuální verzi. Podpora více podlaží by nevyžadovala zásah do Vrstev 1 a 2 --- postačovala by koordinační vrstva replikující stávající datový model pro každé podlaží a přidávající vazby mezi nimi; grafy, validátory i synchronizační pipeline by pracovaly per-podlaží beze změny. Exportní pipeline do formátů DXF, SVG nebo IFC pracuje výhradně s daty Vrstvy 3; základ pro ni tvoří bake operátor, jenž ze synchronizované geometrie a named atributů generuje statický mesh --- export by byl dalším výstupním krokem nad týmiž daty, nikoli novým principem. Prostorová validace --- kontrola minimálních průchodů, požárních únikových cest nebo normových plošných požadavků --- nevyžaduje rozšíření datového modelu: architektura `validators.py` je navržena pro přidávání izolovaných pravidel a `StructuralGraph` i `RoomGraph` poskytují veškerý topologický a geometrický kontext, který taková pravidla vyžadují.

Třívrstvé jádro s jasně vymezenými zodpovědnostmi, centralizovaný overlay manager a synchronizační pipeline tvoří základ, na nějž lze navazovat bez zásahu do existující funkcionality. Architektura k tomu vede přirozenou cestou --- nové schopnosti se přidávají za výstupem stávajících vrstev nebo jejich rozšiřováním, nikoliv přepisováním jejich vnitřní logiky.

#pagebreak()
= Testování

Testování addonu probíhá na dvou úrovních. První tvoří automatizované testy pokrývající čisté Python jádro; druhou je uživatelské testování implementovaného #gls("mvp", long: false) s reprezentativní skupinou účastníků z definovaných cílových skupin. Tato kapitola popisuje stav automatizovaných testů a připravený plán uživatelského testování, jehož realizace je plánována jako bezprostřední navazující krok po dokončení implementace.

== Automatizované testy

Testovací sada pokrývá celé čisté Python jádro: Vrstvu 1, Vrstvu 2, validátory a matematické utility. Každý testovací soubor ověřuje standardní scénáře i hraniční podmínky --- minimální a maximální hodnoty parametrů, duplicitní entity, topologicky neplatné grafy a výpočetně degenerované situace (nulová délka stěny, kolineární vrcholy, degenerovaný polygon místnosti). Celkem je k dispozici přes 190 testovacích případů a všechny procházejí bez chyby.

Synchronizační vrstva a operátory automatickými testy pokryty nejsou, neboť vyžadují přítomnost Blenderu a jeho Python interpretu. Jejich správnost je proto ověřována manuálně přímo v Blenderu na sadě referenčních scénářů: kreslení dispozice s různými typy spojů, přidávání otvorů, finalizace meshe a obnova grafů po reloadu souboru.

== Plán uživatelského testování

#gls("mvp", long: false) addonu je implementačně dokončen a způsobilý pro uživatelské testování. Tato sekce definuje metodiku, scénáře a strukturu dotazníku, podle nichž testování proběhne --- slouží zároveň jako podklad pro hodnotitele a jako dokumentace testovacího záměru.

=== Cílové skupiny a výběr účastníků

Výběr účastníků vychází přímo z analýzy cílových skupin v kapitole @chap-analysis: testování se zúčastní zástupci architektů, 3D vizualizátorů a game designérů, přičemž z každé skupiny bude osloveno více účastníků tak, aby výsledky umožnily porovnání chování skupin navzájem. Zásadní proměnnou je předchozí zkušenost s programem Blender --- uživatelé bez této zkušenosti narážejí na odlišné překážky než uživatelé zkušení, pro něž je ovládání viewportu přirozenou součástí pracovního postupu. Dotazník proto zahrnuje vstupní otázky zjišťující úroveň zkušenosti s Blenderem a se specializovanými nástroji pro tvorbu půdorysů.

=== Metodika

Testování probíhá formou samostatně plněných úkolů bez přítomnosti moderátora. Každý účastník dostane předem připravený soubor se zadáním a vyplní dotazník po splnění --- nebo pokusu o splnění --- každého úkolu. Účastníci jsou předem instruováni, aby při obtížích zdokumentovali, kde se zastavili, nikoliv aby úkol přeskočili bez záznamu. Tím se zajistí, že i neúspěšné pokusy přinesou použitelná data.

Testovací sada obsahuje čtyři scénáře odpovídající use case z analytické části (UC 1.1--3.2). Každý scénář je formulován jako konkrétní zadání bez technického žargonu:

- *Scénář A* --- Nakresli dispozici se čtyřmi místnostmi navzájem propojenými chodbou. Ověřuje základní workflow nástroje tužka, přichycení na existující vrcholy a automatickou detekci místností.
- *Scénář B* --- Uprav tloušťku nosných stěn a příček a nastav různé výšky jednotlivých místností. Ověřuje parametrickou editaci přes N-panel a aktivaci FloorPlan módu.
- *Scénář C* --- Přidej dveřní otvory do každé místnosti a okno do obývacího pokoje. Ověřuje workflow přidávání otvorů a chování validačních omezení.
- *Scénář D* --- Zkontroluj plochy místností, přejmenuj je dle zadání a vyexportuj dispozici jako statický mesh. Ověřuje čitelnost metadat místností a workflow finalizace.

=== Struktura dotazníku

Dotazník se skládá ze čtyř částí. Vstupní část zjišťuje zkušenostní předpoklady respondenta: cílová skupina, délka práce s Blenderem (kategorie: nikdy, příležitostně, pravidelně) a zkušenost se specializovanými nástroji pro půdorysy. Pro každý scénář zvlášť dotazník zaznamenává, zda byl úkol dokončen (ano / s obtížemi / nedokončen), odhadovaný čas plnění a hodnocení obtížnosti na pětibodové stupnici. Doplňující otevřená otázka ke každému scénáři zjišťuje, co bylo matoucí nebo neočekávané.

Třetí část tvoří uzavřené otázky hodnotící celkový dojem ze tří dimenzí: srozumitelnost ovládání (zejména aktivace FloorPlan módu a nástroje tužka), konzistence s konvencemi programu Blender a přehlednost N-panelu. Závěrečná otevřená část vyzývá respondenta k volnému komentáři a k formulaci jednoho nejdůležitějšího návrhu na zlepšení.

=== Identifikovaná rizika použitelnosti

Manuální testování v průběhu implementace odhalilo oblasti, v nichž lze pro určité skupiny uživatelů očekávat zvýšené tření. Tyto poznatky budou ověřeny uživatelským testováním a poslouží jako vstup pro prioritizaci navazujících iterací.

Pro skupinu zkušených uživatelů Blenderu budou pravděpodobně hlavním podnětem dílčí nedostatky v plynulosti ovládání: absence klávesové zkratky pro přidání otvoru přímo z viewportu, chybějící vizuální nápověda pro příkaz Remove Wall v N-panelu nebo absence zobrazení délky stěny přímo u kurzoru při kreslení. Tato místa tření se netýkají principiálního návrhu a lze je adresovat jako izolovaná UI vylepšení v navazující iteraci. Rizika specifická pro uživatele bez předchozí zkušenosti s addonem --- aktivace pracovního módu a chování clampingu otvorů --- jsou detailněji popsána v sekci omezení implementace.
