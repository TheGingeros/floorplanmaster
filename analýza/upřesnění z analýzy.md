## Zůžení cílovích skupin
### Hlavní cílové skupiny/uživatelé - společný průsečík
- Architekti
- 3D Umělci/Vizualizátoři
- Game Designéři (Level design)

- **Společné potřeby:**
    - rychlé iterativní navrhování v objemech
    - čistá geometrie
    - nedestruktivní vkládání otvorů

- Pro interiérový designery, hobbysti nepotřebujeme vyvíjet speciální funkce, mělo by je chytit UI ale to je součástí již potřeb hlavních cílových skupin

## Hlavní vize addonu
- nástroj pro rychlé kreslení a iteraci prostorových dispozic
- nejedná se o BIM manažer - neřešíme rozpočty (5D), energetiku (6D) ani exporty do složitých IFC struktur
- nedestruktivní, kdykoliv musí jít element posunout bez toho, aniž by se geometrie rozbila
- nebudou se ručně posouvat vertexy nebo polygony
- úpravy budou pomocí parametrických vstupů nebo úprav pomocí UI ve viewportu

## Návrh funkcí vycházejíc z potřeb uživatelů
### 1. Kreslící nástroj - priorita - WallBuilder
- TODO
    - kreslení čáry vs kreslení zdi
    - jaké parametry zobrazovat v topbaru - viz inspirace
    - co kreslit v HUD - viz inspirace

- cílem je vytvořit nástroj/workflow, který nevyžaduje neustálé klikání do panelů
#### Uživatelský scénář
1. Aktivace
    - kliknutí na ikonu nástroje v levém toolbaru nebo klávesovou zkratkou
    - kurzor myši se změní - například na křížek nebo tužku
2. První klik
    - kliknutí do 3D viewportu (left click) - zafixování počátečního bodu stěny
3. Tažení
    - jak se hýbe myší, od prvního bodu se táhne virtuální čára ke kurzoru
    - primární směr by měl být automaticky buď ve směru X, Y nebo Z, přepnutí na volný úhel, který lze zadat numericky, při klávesové zkratce
    - uprostřed této čáry se vznáší text s aktuální délkou
4. Zadání přesné hodnoty (parametrizace)
    - uživatel pustí myš, na klávesnici napíše 5.5 a stiskne enter
    - čára se prodlouží/zkrátí přesně na 5,5 metru ve směru kam zrovna ukazovala myš/jaká osa v tu chvíli byla aktivní
5. Řetězení
    - nástroj kreslí další segment z posledního koncového bodu nebo z ručně zvoleného libovolného existující bodu v prostoru
6. Ukončení
    - jakmile je uživatel hotov, zmáčkne pravé tlačítko myši nebo esc
    - uzavřením tvaru se smyčka také automaticky ukončí

#### Inspirace z existujících softwarů podporující podobný nástroj
1. SketchUp - Line Tool
    - inference engine
    - automaticky zamyká směry na X, Y, Z
    - pokud se napíše číslo, automaticky se aplikuje na aktuální směr
2. Archicad / Revit - Wall Tool
    - uživatel kreslí čáru ale software na obrazovce ukazuje zvolenou tloušťku zdi
    - možnost přepínat za běhu zda se kreslí na střed nebo vnitřní/vnější líc
3. Blender - Knife Tool/ Poly Build
 - knife tool je ukázkový modální operátor - kreslí čáry přes obrazovku
 - chytá se vertexů a čeká na potvrzení - enter

#### Zasazení v Blenderu - UI
1. aktivní nástroj 
    - dostupný přes T panel jako vlastní ikonu
    - neprovádí pouze jednorázovou akci ale je to stav, do kterého se blender přepne

2. Top Bar
    - když je nástroj aktivní, v top baru se objeví základní nastavení
    - např. výška, tloušťka, zarování apod. 

3. HUD
    - kreslit informace přímo na 3D viewportu, nezávisle na 3D geometrii
    - kóty, úhly, pomocné vodící čáry apod. 
### 2. Správa stěn a otvorů - "srdce" addonu
### 3. Uživatelské rozhraní - zásadní pro přijetí uživateli
### 4. Správa místností a podlaží - nice to have

