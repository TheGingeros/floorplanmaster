# Metody bez Booleovských operací (Procedurální dekompozice)
- tyto metody se vyhýbají drahým výpočtům průsečíků ploch a místo toho otvory vkládají přímo do procesu generování topologie
## Curve Trimming (Ořez křivek): 
- pokud jsou stěny generovány z vodicích křivek, využívá se uzel Trim Curve ještě před vytažením do 3D
- matematicky se křivka rozdělí v parametrickém prostoru na segmenty, čímž vzniknou fyzické mezery
- výsledný 3D mesh je topologicky čistý a nevyžaduje žádné čištění hranic
- nelze využít pro okna

## Modulární instancování: 
- stěna není chápána jako monolit, ale jako pole buněk
- pomocí uzlu Instance on Points se na vodicí mesh umisťují buď plné moduly stěn, nebo moduly s předpřipravenými otvory pro okna

## Vertex Group Topology: 
- pokročilé workflow, kde se specifické vrcholy vodicího meshe označí atributem (např. „is_window“)
- Geometry Nodes následně tyto vrcholy posunou tak, aby vytvořily pravoúhlý otvor, a pomocí uzlu Bridge Edge Loops se vytvoří ostění oken
- tento přístup je nejrychlejší z hlediska výkonu, ale vyžaduje striktní kontrolu nad indexy vrcholů