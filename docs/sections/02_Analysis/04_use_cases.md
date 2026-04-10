# 2.4 Scénáře použití
Scénáře použití dokumentují konkrétní pracovní postupy všech tří cílových skupin. Šest scénářů musí-mít (UC 1.1–UC 3.2) pokrývá klíčové flows od hmotové studie přes kreslení půdorysu, obkreslení 2D podkladu až po finalizaci a export. Tři scénáře by-mělo-mít (UC 1.3, UC 2.3, UC 3.3) popisují rozšiřující funkce kótování, kontextové nabídky a interaktivních gizmos.
## UC 1.1 Scénář 1.1: Hmotová studie na základě stavebního programu
- architekt zadá do panelu addonu požadovanou plochu a poměr stran pro každou místnost (např. 30 m², poměr 1:1,5)
- addon automaticky dopočítá rozměry a vloží pravoúhlou místnost do scény
- uživatel opakuje vložení pro všechny místnosti ze stavebního programu
- výsledkem je schematická dispozice, u které lze v panelu ověřit plochu každé místnosti
## UC 1.2 Scénář 1.2: Kreslení dispozice tužkou
- architekt aktivuje kreslící nástroj a klikáním bodů přímo ve 3D viewportu načrtne dispozici
- addon průběžně generuje stěny a při uzavření cyklu automaticky detekuje místnosti
- uživatel doladí tloušťku a výšku stěn zadáním hodnot v N-panelu
## UC 2.1 Scénář 2.1: Obkreslení dodaného 2D půdorysu
- vizualizátor si na pozadí Blenderu vloží obrázek s půdorysem
- aktivuje kreslící nástroj a se zapnutým přichytáváním na existující junctions odklikává rohy místností přesně podle obrázku
- addon průběžně generuje stěny a automaticky detekuje místnosti při uzavření cyklů
- uživatel nastaví výšku a tloušťku stěn v N-panelu
## UC 2.2 Scénář 2.2: Příprava modelu pro renderovací pipeline
- vizualizátor na existujícím půdorysu vybere stěnu a v N-panelu přidá otvor zadáním přesných rozměrů (např. 1500 × 1250 mm) a výšky parapetu
- addon dynamicky vyřízne otvor přes GN Mesh Boolean; při změně rozměrů v panelu se otvor okamžitě aktualizuje
- po dokončení dispozice spustí finalizační nástroj, který aplikuje modifikátory, zpracuje UV a připraví statickou mesh pro renderovací pipeline
## UC 3.1 Scénář 3.1: Rychlý level blockout
- game designer aktivuje kreslící nástroj a hrubě načrtne sérii navazujících místností
- soustředí se na proporce a měřítko vůči hráčské postavě; addon průběžně generuje stěny a detekuje místnosti
- výšku stěn nastaví uniformně v N-panelu pro celý půdorys
## UC 3.2 Scénář 3.2: Finalizace a export herní úrovně
- game designer na hotovém blokoute přidá dveřní otvory zadáním parametrů v N-panelu na vybraných stěnách
- ověří plochy místností viditelné v N-panelu
- spustí finalizační nástroj, který aplikuje GN modifikátory, konvertuje UV atributy a připraví statickou mesh na export ve formátu FBX nebo GLTF
## UC 1.3 Scénář 1.3: Kontrola rozměrů vůči normovým minimům (should-have)
- architekt má hotovou dispozici a potřebuje ověřit, zda šíře chodeb a místností splňují normová minima
- zapne kótovací overlay v N-panelu; addon zobrazí délky všech stěn a plochy místností přímo ve viewportu prostřednictvím BLF draw_handleru
- vizuálně zkontroluje kritická místa (šíře chodby, průchod dveřmi) a případně upraví parametry stěn v N-panelu
## UC 2.3 Scénář 2.3: Rychlá editace vlastností prvků přes kontextovou nabídku (should-have)
- vizualizátor chce přiřadit různé materiály podlahy jednotlivým místnostem bez přepínání do separátního panelu
- klikne pravým tlačítkem na plochu místnosti ve viewportu; kontextová nabídka zobrazí akce pro danou místnost
- vybere „Změnit materiál podlahy" a přiřadí odpovídající materiál; stejným způsobem přejmenuje místnost pro přehlednost scény
## UC 3.3 Scénář 3.3: Interaktivní adjustace rozložení místností (should-have)
- game designer zjistí po playtestingu, že chodba mezi dvěma arénami je příliš úzká pro pohyb hráče
- vybere junction na kraji chodby a pomocí gizma pohybu táhne bod v rovině XY; addon zachovává planaritu a průběžně přepočítává sousední místnosti
- výsledná šíře chodby je ověřena vizuálně ve viewportu bez nutnosti zadávat číselné hodnoty