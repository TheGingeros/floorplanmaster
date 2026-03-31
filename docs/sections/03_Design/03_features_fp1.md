# FP1: Nástroj Tužka - Interaktivní kreslení půdorysů
Nástroj Tužka představuje absolutní jádro uživatelského rozhraní addonu. Jde o komplexní modální operátor (Controller), který překládá kliknutí myší ve 3D viewportu do exaktních topologických dat uvnitř aktuálně aktivního podlaží. Zajišťuje plynulé interaktivní kreslení s okamžitou vizuální odezvou (přes modul `gpu`), aniž by během tažení myší zbytečně přetěžoval a přepisoval hlavní datové modely. K fyzickému zápisu do grafů a synchronizaci dochází až po potvrzení bodu.

## Must-Have - součástí MVP
Následující seznam definuje kritické funkce, bez kterých nelze nástroj považovat za provozuschopný. Tvoří absolutní základ (Minimum Viable Product) a zajišťují, že uživatel dokáže nakreslit přesný, spojený a matematicky validní půdorys.

1. **Modální operátor se stavovým automatem**
   - Operátor vstupí do modálního stavu po aktivaci
   - Následuje přechody stavů: START → DRAWING → CONFIRMING → RECORDING → finished/cancelled
   - Reaguje na pohyb myši, kliknutí a vstup z klávesnice

2. **Umístění bodů (2D Projekce)**
   - Kliknutí ve 3D pohledu se okamžitě promítne do striktní 2D roviny (x, y) aktuálně aktivního podlaží.
   - Z-ová souřadnice z myši je ignorována (výška se řeší na úrovni podlaží/místnosti), čímž se chrání planární graf před deformací.
   - Validace: Žádné duplicitní propojovací body v toleranci v rámci jednoho podlaží.

3. **Vytváření stěn**
   - Po prvním bodu: Zobrazit náhledovou linii sledující myš
   - Kliknutí na druhý bod: Vytvoří stěnu mezi propojovacími body
   - Stěna je přidána do strukturálního grafu vrstvy 1
   - Automatická detekce cyklů aktualizuje vrstvu 2

4. **Základní přichycování** (Should-Have zvýšeno na Must-Have)
   - **Přichycování osy**: Přichytit k osám X, Y v případě, že je kurzor v 10 pixelech
   - **Přichycování bodu**: Přichytit na existující propojovací body v rámci 15 pixelů
   - Vizuální indikátor (kruh) když je přichycování aktivní
   - Uživatel může přichycování přepnout klávesou modifikátoru (Shift)

5. **Vykreslování náhledu**
   - Zobrazit ducha/náhledovou stěnu před potvrzením
   - Náhled v reálném čase při pohybu myši
   - Barva náhledu odlišná od potvrzených stěn
   - Používá modul `gpu` pro výkon

6. **Potvrzení a zrušení**
   - Stiskněte **Enter/LMB**: Potvrdit bod
   - Stiskněte **Esc/RMB**: Zrušit aktuální akci
   - Stiskněte **Z** pak Enter: Vrátit poslední bod
   - Přechody stavů se zpracovávají bez chyb

7. **Vizuální zpětná vazba**
   - Zobrazování souřadnic v reálném čase (HUD overlay)
   - Zobrazení délky stěny během kreslení
   - Zobrazení úhlu (stupně)
   - Stavové zprávy v levém horním rohu pohledu

## Should-Have (Schopnosti)
Tato sada rozšiřujících funkcí posouvá základní kreslení na úroveň profesionálních CAD nástrojů. Nejsou sice nezbytné pro fungování architektury, ale drasticky zrychlují workflow, minimalizují chybovost uživatele a umožňují zadávat přesné hodnoty z klávesnice již během samotného kreslení.

1. **Vstup tloušťky stěny**
   - Po druhém bodu: Umožnit uživateli zadržet hodnotu tloušťky
   - Stiskněte Enter pro potvrzení, ESC pro výchozí
   - Zobrazena hodnota v aktuálním systému jednotek

2. **Vstup výšky stěny**
   - Podobně jako tloušťka, umožnit přizpůsobení výšky
   - Výchozí 3.0m, uživatel může přepsat

3. **Nepřetržité kreslení**
   - Po potvrzení stěny je připraven automaticky pro další stěnu
   - Předchozí koncový bod se stane novým počátečním bodem
   - Uživatel může stisknout ESC pro ukončení režimu kreslení

4. **Přichycování úhlu**
   - Možnost přichycovat k 45°, 90°, 135°, atd.
   - Přepnout klávesou **A**
   - Vizuální indikátor úhlu při přichycování

5. **Přichycování mřížky**
   - Volitelná mřížka (0.1m, 0.5m, 1.0m)
   - Přepnout klávesou **G**
   - Kurzor přichytit na nejbližší bod mřížky

6. **Vrácení během kreslení**
   - Stiskněte **Z** pro vrácení poslední bodu v aktuální relaci kreslení
   - Opakovat s **Y**
   - Omezeno na aktuální relaci (do Esc/Enter)

## Diagram stavového automatu
Aby modální operátor bezpečně zvládal nejrůznější kombinace uživatelských vstupů a nikdy neskončil v chybovém stavu (například pokusem o vytvoření stěny bez existujícího počátečního bodu), je jeho běh řízen striktním stavovým automatem (State Machine). Následující diagram mapuje povolené přechody mezi jednotlivými fázemi interakce.

```
        ┌─────────────┐
        │   START     │
        └──────┬──────┘
               │
         (Uživatel klikne)
               │
               ▼
        ┌─────────────┐
        │   DRAWING   │◄────┐
        │             │     │
        │ (show prev) │     │ (pohyb myši)
        └──────┬──────┘     │
               │            │
        (klik/Enter)    ┌───┘
               │        │
               ▼        │
        ┌─────────────┐ │
        │ CONFIRMING  ├─┘
        │             │
        │ (add wall)  │
        └──────┬──────┘
               │
        (Opakovat nebo Esc)
               │
               ▼
        ┌─────────────┐
        │  FINISHED   │
        │ (cleanup)   │
        └─────────────┘
```

## Zpracování událostí
Tato tabulka slouží jako přesná implementační matice pro metodu `modal()`. Definuje, jak operátor reaguje na specifické události (Eventy) z klávesnice a myši v závislosti na tom, ve kterém stavu se právě nachází, a určuje, jaký stav bude bezprostředně následovat.

| Událost | Stav | Akce | Příští stav |
|---------|------|--------|-----------|
| LMB Kliknutí | START | Přidat propojovací bod | DRAWING |
| Pohyb myši | DRAWING | Aktualizovat náhled | DRAWING |
| LMB Kliknutí | DRAWING | Přidat stěnu, detekovat cykly | CONFIRMING |
| Zadejte číslo | CONFIRMING | Nastavit tloušťku stěny | CONFIRMING |
| Enter | CONFIRMING | Potvrdit stěnu | DRAWING |
| Esc (1x) | DRAWING | Odebrat poslední bod | START |
| Esc (2x) | START | Ukončit operátor | FINISHED |
| Z | Libovolný | Vrátit bod | Předchozí |
| Y | Libovolný | Znovu vytvořit bod | Příští |
| Scroll | Libovolný | Zoom (PASS_THROUGH) | Aktuální |
| Střední myš | Libovolný | Pan (PASS_THROUGH) | Aktuální |

## Poznámky k implementaci
- **Modální handler**: Zaregistrovat s `context.window_manager.modal_handler_add(self)`
- **Návratové hodnoty**:
  - `RUNNING_MODAL`: Pokračovat v zpracování vstupů
  - `PASS_THROUGH`: Umožnit interakci pohledu (zoom, pan)
  - `FINISHED`: Operace úspěšná, vytvořit krok vrácení
  - `CANCELLED`: Přerušit operaci
- **Vykreslování GPU**: Použít `gpu.types.GPUBatch` a shadery pro náhled
- **Výkon**: Ukládat geometrické výpočty do mezipaměti, aktualizovat pouze na významný pohyb