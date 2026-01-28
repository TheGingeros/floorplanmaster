# Analýza: Architectural Sketch Add-on pro Blender
## 1. Úvod:
Oblast architektonické vizualizace a digitálního návrhu prochází v posledních letech dynamickým vývojem. Zatímco dříve byl trh dominován, a stále je, drahými komerčními řešeními (často uzavřenými, bez možnosti uživatelského rozšíření), v současnosti roste popularita open-source softwaru, v našem konkrétním případě Blenderu. Ten se díky svému výkonnému renderovacímu jádru a nulovým licenčním poplatkům stává atraktivní alternativou pro profesionální studia i nezávislé tvůrce.

Přestože Blender exceluje v oblasti organického modelování, animace a finálního renderingu, jeho základní nástroje nejsou optimalizovány pro technické a parametrické navrhování, které je pro architekturu klíčové. Uživatelé tak narážejí na technologickou bariéru při snaze vytvořit přesné dispoziční řešení přímo v prostředí programu.

Tento dokument se zabývá analýzou a návrhem rozšiřujícího modulu, který má za cíl tuto mezeru překlenout. Zaměřuje se na implementaci intuitivního workflow pro tvorbu půdorysů, stěn a stavebních otvorů, které kombinuje rychlost skicování (charakteristickou pro nástroje typu SketchUp) s robustním prostředím Blenderu. Následující analýza definuje současné problémy workflow, identifikuje klíčové uživatelské skupiny a stanovuje požadavky pro vývoj takového nástroje.


### 1a. Současný stav
- **Absence nástrojů v Blenderu:** Blender v základu postrádá intuitivní nástroje pro tvorbu architektonických půdorysů. Modelování stěn pomocí Extrude/Scale je zdlouhavé, destruktivní a náchylné k chybám v topologii.
- **Roztříštěné workflow:** Architekti a designéři jsou nuceni používat placený software (SketchUp Pro, Archicad) pro fázi návrhu a poté exportovat data do Blenderu pro vizualizaci, případně jiného specializovaného softwaru na vizualizaci (Enscape, Lumion, 3DS Max, ...). Tento proces přináší problémy s kompatibilitou a neumožňuje snadné úpravy.
- **Ekonomická bariéra:** Profesionální CAD/BIM nástroje (Revit, Archicad) a rychlé vizualizéry (Lumion) stojí tisíce eur ročně, což je bariéra pro freelancery a studenty.


### 1b. Cíl řešení
- Vytvořit nástroj, který umožní celý proces od první skici po finální render udržet uvnitř Blenderu.

- Nahradit funkčnost SketchUpu ve fázi studie (Schematic Design) s využitím nativního prostředí Blenderu.

- Poskytnout data, která běžný modelovací software neposkytuje bez složitých pluginů.

## 2. Cílové skupiny / Persony
#### Persona A: Freelance Architekt / Interiérový Designér
- **Potřeba:** Potřebuje rychle převést náčrt od klienta do 3D, aby mohl začít vizualizovat. Nechce se zdržovat technickým modelováním.
- **Bariéra:** Blender je skvělý na render, ale nepraktický na přesné CAD rýsování.
#### Persona B: Archviz Specialista (3D Grafik zaměřený na architekturu)
- **Potřeba:** Dostane podklad (PDF/DWG) a musí co nejrychleji vytvořit "krabici" (shell) pro vizualizaci.
- **Bariéra:** Modelování stěn vertex po vertexu je ztráta času, který by raději věnoval materiálům a svícení.
#### Persona C: Indie Game Developer / Level Designer
- **Potřeba:** Rychle nasekat půdorysy domů pro herní prostředí. Nepotřebuje stavební přesnost, ale potřebuje rychlost a snadnou editaci (opakovatelnost).
- **Bariéra:** Složité add-ony (Archipack) jsou pro hru příliš "těžké" (mnoho parametrů), potřebuje něco jednoduššího.
#### Persona D: Hobbyista
- **Potřeba:** Chce si vymodelovat vlastní byt, aby viděl, jak tam sedne gauč nebo jakýkoliv jiný nábytek.
- **Bariéra:** Neumí v Blenderu pokročilé modelování, potřebuje nástroj „nakresli čáru -> vznikne zeď“.


## 3. Scénáře Použití
1. **Use Case:** 
Kreslení od ruky: Uživatel v Top-View kreslí myší čáry (jako v CADu), které se v reálném čase mění na 3D stěny s definovanou výškou a tloušťkou.
2. **Use Case:** 
Definice místnosti: Po uzavření smyčky stěn add-on rozpozná "místnost", vygeneruje podlahu/strop a automaticky vypočítá plochu ($m^2$) a objem ($m^3$).
3. **Use Case:** 
Vkládání oken/dveří: Drag & Drop okna z knihovny na stěnu. Okno se "přilepí" (snap), orientuje podle normály stěny a automaticky vyřízne otvor. Při posunu okna se otvor posouvá s ním.
4. **Use Case:** 
Iterativní změny: Posun stěny o 50 cm. Sousední stěny se natáhnou, podlaha se přepočítá, okna zůstávají na svých relativních pozicích (nebo absolutních, dle nastavení).

## 4. Specifikace požadavků
### 4a. Funkční požadavky
1. **Drawing Engine:** Nástroj pro kreslení stěn s podporou ortogonálního režimu.
2. **Parametrizace:** Možnost zadat číselně délku segmentu během kreslení a globální parametry (tloušťka zdi, výška).
3. **Snapping System:** Přichytávání k vrcholům, hranám a mřížce (Grid).
4. **Room Manager:** Detekce uzavřených cyklů a generování podlahy/stropu.
5. **Data Calculation:** Real time výpočet plochy podlahy (zobrazení v UI panelu nebo jako 3D text ve scéně).
6. **Library Manager:** Správa základních assetů (okno, dveře) a jejich vkládání s boolean operací.
### 4b. Nefunkční požadavky
1. **UX/UI:** Minimalizace kliknutí. Kreslení musí být plynulé. UI panel v N-Panelu (Sidebar).
2. **Topologie:** Výsledná mesh musí být čistá (pokud možno quads), aby na ni šly aplikovat textury bez artefaktů.
3. **Kompatibilita:** Blender verze LTS (4.2+).
4. **Přesnost:** Práce s reálnými jednotkami (Metrický/Imperiální systém) s přesností na mm.

## 5. Zdroje
CGArchitekt Survey - růst blenderu - https://drive.google.com/file/d/1-jB_xnpSZmc07KFVPD43-JXONG6Pm1YN/view  
Right-Click Select - Blender komunita - https://blender.community/c/rightclickselect/?sorting=hot  
Blender workflow z půdorysu - komentáře - https://www.youtube.com/watch?v=Q4rbqUbhYXY  
Blender workflow z půdorysu - složitost operací - https://youtu.be/94kAIpRnhcY?t=566  
SketchUp workflow z půdorysu - jednoduchost obkreslení - https://youtu.be/tkLfb-fuMSM?t=1580  
Archicad workflow, vytváření půdorysu - Klikání a výtvor stěn - https://youtu.be/PZv27GCxrgU?t=144  
Why I switched from SketchUp to Blender - komentáře ohledně architektonických návhrů - https://forums.sketchup.com/t/post-2021-sketchup-layout-petition-why-i-m-transitioning-to-blender-and-seeking-developers/282387/3  
Blender for 3d printing - komentáře ohledně CAD pluginů - https://www.reddit.com/r/blender/comments/1jvar87/switching_from_sketchup_to_blender_for_3d/  
Export z archicadu do blender - starý thread - https://community.graphisoft.com/t5/Collaboration-with-other/Export-to-Blender/td-p/265323
 