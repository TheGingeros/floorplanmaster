# Geometry nodes a paradigma polí
- uživatel definuje systém pravidel, která jsou aplikována na celou geometrii současně
- data jsou reprezentována jako pole atributů, která jsou vázána na různé domény - vrcholy, hrany, plochy, instance
- pro architekturu to znamená, že informace jako typu stěny nebo příslušnost k místnosti mohou být uloženy přímo v geometrii jako pojmenované atributy
- tento přístup umožňuje extrémně rychlou vizuální zpětnou vazbu, neboť systém je optimalizován pro multithreading a běží v nativním kódu C++

## Implementace pomocí Geometry Nodes
- stěny se nejčastěji generují z křivek pomocí uzlu` Curve to Mesh`
- hlavní výzvou je zde Miter Joint problém - standardní vytažení profilu podél křivky vede ke ztenčení stěny v ostrých rozích
- je potřeba implementovat **matematickou korekci měřítka profilu v každém bodě:**
    - koreční faktor f pro bod v rohu s úhlem theta je dán vztahem: f= 1 / sin(theta/2)
    - v geometry nodes se tento výpočet provádí pomocí vektorové matematiky, kde se určuje úhel mezi sousedními segmenty stěny pomocí skalárního součinu a následně se mění měřítko profilu v daném bodě
    - přestože je toto nastavení v uzlech komplexnější na přípravu, jeho použití je rychlé a umožňuje dynamicky měnit tloušťku stěn pouhým posunutím bodu v 2D půdorysu