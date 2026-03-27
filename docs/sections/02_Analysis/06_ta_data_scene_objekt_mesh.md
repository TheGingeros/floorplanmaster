# Vazby dat, Scéna, Objekt, Mesh
- rozhodnutí o tom, na jaké úrovni hierarchie Blenderu budou metadata uložena, má hluboké důsledky pro stabilitu doplňku, chování při operacích zpět (Undo) a správu instancí
## Úroveň scény - bpy.types.Scene
- vazba dat na této úrovni je vhodná pro globální parametry projektu, jako je geografická poloha, nastavení jednotek nebo globální materiálové standardy
- pro data specifická pro jednotlivé místnosti nebo prvky je však tato úroveň nevhodná
- hlavní problém je perzistence - pokud jsou metadata o konkrétním okně uložena v kolekci na úrovni scény, smazání tohoto objektu ve viewportu nezpůsobí automatické smazání metadat v kolekci, což vede k hromadění dat
## Úroveň objektu - bpy.types.Object
- objekt v Blenderu funguje jako kontejner, který nese informace o transformaci, viditelnosti a hierarchických vztazích
- uložení metadat na úroveň objektu je intuitivní, ale přináší komplikace v případě instancování
- vytvoření instance přes Alt + D vytvoří dva objekty, které sdílejí stejná geometrická data (Mesh), ale mají unikátní data na úrovni Object
- změna rozměru jednoho okna by se neprojevila u ostatních instancí, což popírá princip parametrického navrhování 
## Úroveň geometrie - bpy.types.Mesh
- považováno za nejvhodnější přístup pro architektonické prvky
- reprezentuje "definici typu" prvku
- pokud je `PropertyGroup` s parametry okna vázána na Mesh, všechny instance v projektu sdílející tento Mesh budou mít vždy identické parametry
- v souladu s principy BIM, kde rozlišujeme mezi Typem a Instancí
- data na této úrovni jsou lépe chráněna při komplexních operacích jako je export nebo linkování mezi soubory
## Porovnání
| Úroveň vazby | Architektonický význam | Chování při instancování | Stabilita při Undo/Redo |
| :--- | :--- | :--- | :--- |
| **Scene** | Globální projektová data | Metadata jsou sdílena celou scénou | Náchylné k desynchronizaci |
| **Object** | 	Unikátní vlastnosti instance | Každá instance má vlastní metadata | Velmi stabilní |
| **Mesh** | Definice typu prvku | 	Instance sdílejí metadata (změna u jednoho změní vše) | Velmi stabilní |
---
z toho vyplývá, že se použije hybridní model:
    - parametry definující tvar a funkci (rozměry, materiály, typ místnosti) ukládat na úroveň Mesh
    - identifikační data a specifické stavy (GUID prvku, stav revize konkrétního kusu) ukládat na úroveň Object
    - projektová data (název akce, stupeň dokumentace) ukládat na úroveň Scene