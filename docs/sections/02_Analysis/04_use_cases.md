# 2.4 Scénáře použití
úvod todo
## UC 1.1 Scénář 1.1: Hmotová studie na základě stavebního programu
- uživatel vloží do scény parametrickou místnosti na základě vstupních parametrů
- přes nabídku v panelu zadá požadovanou plochu a poměr stran, například 30 m^2
- addon automaticky vygeneruje místnost o daných parametrech
- uživatel zapne zobrazení metadat - štítek s plochou v m^2 přímo v 3D view pro rychlou vizuální kontrolu
## UC 1.2 Scénář 1.2: Zkoušení prostorových variant a posun stěn
- uživatel vybere sdílenou příčku mezi dvěma vytvořenými místnostmi
- pomocí interaktivní 3D manipulátoru stěnu posune o 1 metr
- addon nedestruktvně přepočítá obě místnosti, jedna se zvětší, druhá zmenší a podlahové plochy se automaticky aktulizují
## UC 2.1 Scénář 2.1: Obkreslení 2D půdorysu do čisté 3D geometrie
- uživatel si na pozadí Blenderu vloží obrázek s půdorysem
- aktivuje nástroj pro kreslení a se zapnutým přichytáváním odklikává rohy místností přesně podle obrázku
- addon automaticky generuje stěny s přednastavenou tloušťkou a výškou. Geometrie je tvořena čistými quady - pokud možno
## UC 2.2 Scénář 2.2: Vložení otvorů pro přesné 3D modely oken/dveří
- uživatel vybere stěnu a aktivuje funkci "Vložit otvor"
- nakreslí otvor přímo na plochu stěny nebo zadá jeho přesné rozměry (např. 1500x1250 mm) a výšku parapetu
- otvor se aplikuje nedestruktivně
- uživatel později zjistí, že klient změnil velikost okna – v parametrech otvoru jednoduše přepíše hodnotu a stěna se upraví
## UC 3.1 Scénář 3.1: Rychlý blockout a tvorba chodeb
- uživatel použije kreslící nástroj a hrubě načrtne sérii navazujících místností
- soustředí se pouze na proporce a pocit z prostoru. Nepotřebuje řešit metry čtvereční, ale vizuální měřítko vůči hráčské postavě
- nástroj plynule generuje napojené stěny a podlahy, tvoří modulární celky, které do sebe zapadají
## UC 3.2 Scénář 3.2: Iterace na základě playtestingu a finalizace pro export
- uživatel zjistí, že chodba mezi arénami je příliš úzká
- vybere osu chodby nebo obě stěny a parametricky je rozšíří. Přilehlé místnosti se této změně automaticky přizpůsobí
- následně použije "Finalizační nástroj", který z parametrického add-on objektu vytvoří standardní Blender Mesh, aplikuje modifikátory, odstraní přebytečné hrany (pokud existují) a připraví objekt na FBX/GLTF export