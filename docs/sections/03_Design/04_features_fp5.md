# FP5 — Kontextová nabídka
Kontextová nabídka poskytuje rychlý přístup k nejčastějším operacím bez nutnosti hledat je v panelech. Vyvolává se pravým tlačítkem myši ve 3D viewportu. Klíčovým mechanismem je raycast — addon vrhne paprsek z pozice kurzoru do scény a identifikuje, na jaký element půdorysu uživatel klikl. Podle výsledku raycastu zobrazí relevantní sadu akcí.

## Raycast a detekce kontextu *(should-have)*

Raycast prochází Vrstvou 3 (Blender mesh) a identifikuje typ elementu:

- **Plocha** → místnost; menu zobrazí akce pro místnost (Vrstva 2 metadata)
- **Hrana** → stěna; menu zobrazí akce pro stěnu (Vrstva 1 atributy)
- **Vrchol** → junction; menu zobrazí akce pro propojovací bod
- **Prázdný prostor** → žádný element; menu zobrazí globální akce

Nabídka je vykreslena jako floating panel přes GPU/BLF overlay přímo na pozici kurzoru — jde o vlastní UI vrstvu nezávislou na standardních Blender menu.

## Dostupné akce dle kontextu *(should-have)*

**Kontext: místnost**
- Přejmenovat místnost (editace `room_name` ve Vrstvě 2)
- Změnit materiál podlahy / stropu
- Smazat místnost (odebrání všech ohraničujících hran z Vrstvy 1 → kaskádový zánik cyklu → L2 + L3 sync)

**Kontext: stěna**
- Upravit tloušťku / výšku / materiál (editace atributů Vrstvy 1)
- Přidat otvor — dveře / okno (vytvoření závislého otvoru na dané hraně)
- Rozdělit stěnu (vložení nového junctionu na hranu Vrstvy 1)
- Smazat stěnu (odebrání hrany z Vrstvy 1 → L2 + L3 sync)

**Kontext: junction**
- Smazat junction a přilehlé stěny
- Sloučit s nejbližším junctionem (merge v toleranci)

**Kontext: prázdný prostor**
- Zobrazit / skrýt mřížku
- Zobrazit / skrýt kótování (FP7)
