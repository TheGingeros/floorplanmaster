# 3.4 Uživatelské rozhraní a UX

Tento dokument specifikuje vizuální design, layout, interakční prvky, klávesové zkratky a vizuální styl uživatelského rozhraní. Obsahuje wireframy, palety barev, typografii a pravidla přístupnosti.

Máte funkcionalitu, máte data. Teď musí všechno být přístupné uživateli - architektovi, který chce kreslit půdorysy.

Tento dokument řeší tři otázky:
1. **Kde věci jsou?** - Jak se organizuje UI prostor? Properties panel vlevo, 3D viewport uprostřed, HUD v levém horním rohu. Kde jsou tlačítka, seznamy, dialogy?

2. **Jak se s ním interaguje?** - Jaké jsou klávesové zkratky? (D pro kreslení, Z pro vrácení, G pro mřížku). Jak se pohybuje myškou? LMB pro body, RMB pro menu. Jak se aktivují funkce?

3. **Jak to vypadá?** - Jaké jsou barvy, fonty, ikony? Jak vypadá HUD s informacemi? Jak se indikuje, že je přichycování aktivní?

Podotýkám - toto není estetika pro estetiku. Každé rozhodnutí (např. zelená barva pro úspěch, červená pro chybu) je zamýšleno tak, aby se architektu snadněji orientoval a dělal méně chyb.

V tomto dokumentu se dozvíte:
- Layout pracovního prostoru s ASCII diagramy
- Detailní specifikaci HUD overlay (co se zobrazuje kdy)
- Všechny klávesové zkratky (20+ akcí)
- Palety barev se smyslem
- Wireframy dialogů a panelů
- Návody na přístupnost
- Responsive design pravidla

Pokud vám chybí nějaký UI prvek, tady ho hledejte.

## Přehled UI architektu

FloorPlanMaster používá typickou rozvrhu Blenderu s vlastním HUD overlay a operátory. Cílem je minimalizovat zásah do původního Blender UI, přičemž poskytuje snadný přístup k všem funkcím.

### Rozvrh pracovního prostoru

```
┌──────────────────────────────────────────────────────────────────┐
│  Blender Menu Bar                                                │
├──────────────────────────────────────────────────────────────────┤
│  Toolbar  │  3D Viewport (s HUD overlay)     │  Properties Panel │
│           │                                   │                   │
│  FP Tools │                                   │  FP Scene Props   │
│  ├─ Draw  │                                   │  ├─ Rooms List    │
│  ├─ Param │                                   │  ├─ Walls List    │
│  ├─ Edit  │                                   │  ├─ Settings      │
│  ├─ Bake  │                                   │  └─ Export        │
│  └─ Exp   │  (HUD v levém horním rohu)       │                   │
│           │  Stav: DRAWING                    │                   │
│           │  Souř: X:2.5m Y:1.3m              │                   │
│           │  Délka: 4.2m Úhel: 45°            │                   │
│           │  Podržte Shift pro přichycování   │                   │
└──────────────────────────────────────────────────────────────────┘
```

### Oblasti UI

#### 1. Vlastní panel vlevo (Sidebar)

**Umístění**: Properties panel pod "Tool" (Tab)

```
┌─ FloorPlan Master ─────────────────────┐
│                                         │
│  Místnosti:                            │
│  ├ ☐ Obývací pokoj (14.2 m²)          │
│  ├ ☐ Ložnice (12.5 m²)                │
│  ├ ☐ Kuchyň (9.8 m²)                  │
│  └ ☐ Koupelna (5.2 m²)                │
│                                         │
│  [+ Nová] [- Smazat] [▲ Vlastnosti]    │
│                                         │
│  Stěny:                                │
│  ├ Stěna 1 (4.2m)                      │
│  ├ Stěna 2 (3.5m)                      │
│  ├ Stěna 3 (4.2m)                      │
│  └ Stěna 4 (3.5m)                      │
│                                         │
│  [+ Nová] [- Smazat] [▲ Vlastnosti]    │
│                                         │
│  Nastavení:                            │
│  Jednotky: [Metrické ▼]                │
│  Mřížka: [0.5m ▼]  ☐ Vidět             │
│  Přichycování: [15px ▼]                │
│  Úhel snapping: [45° ▼]                │
│                                         │
│  [? Nápověda]  [⚙ Možnosti]            │
└─────────────────────────────────────────┘
```

#### 2. HUD Overlay (3D Viewport)

Zobrazuje se v levém horním rohu během kreslení.

```
╔════════════════════════════════════════╗
║  FLOORPLAN MASTER v1.0                 ║
╠════════════════════════════════════════╣
║  Nástroj: Tužka (DRAWING)              ║
║  ─────────────────────────────────────  ║
║  Souřadnice: X: 2.532m  Y: 1.834m     ║
║  Délka: 4.256m  Úhel: 42.3°            ║
║  Tloušťka: 0.20m  Výška: 3.0m          ║
║  ─────────────────────────────────────  ║
║  Klávesy:                               ║
║  ├─ LMB / Enter: Potvrdit bod           ║
║  ├─ RMB / Esc: Zrušit                   ║
║  ├─ Z: Vrátit   Y: Znovu                ║
║  ├─ Shift: Vypnout přichycování         ║
║  ├─ A: Přichycování úhlu                ║
║  ├─ G: Přichycování mřížky              ║
║  └─ H: Skrýt tuto nápovědu              ║
╚════════════════════════════════════════╝
```

Prvky overlay:
- **Název nástroje**: Aktuální operátor a stav
- **Souřadnice**: Reálný čas pozice myši
- **Rozměry**: Délka, úhel, tloušťka, výška
- **Nápověda klávesů**: Dynamické na základě stavu
- **Stavová zpráva**: Varovné/chybové zprávy

#### 3. Kontextová nabídka (RMB)

```
┌─────────────────────────────┐
│ Místnost                     │
│ ├─ Vlastnosti…              │
│ ├─ Přejmenovat…             │
│ ├─ Typ místnosti…           │
│ ├─ Materiál…                │
│ ├─ ─────────────────         │
│ ├─ Duplikovat                │
│ ├─ Smazat                    │
│ └─ Exportovat                │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Stěna                        │
│ ├─ Vlastnosti…              │
│ ├─ Tloušťka…                │
│ ├─ Výška…                   │
│ ├─ Materiál…                │
│ ├─ ─────────────────         │
│ ├─ Přidat okno…             │
│ ├─ Přidat dveře…            │
│ ├─ Rozdělit…                │
│ ├─ Smazat                    │
│ └─ ─────────────────         │
│    Vybrat všechny            │
└─────────────────────────────┘
```

---

## Objekty interakce

### Myš

| Akce | Kontejner | Výsledek |
|------|-----------|---------|
| LMB | Prázdný prostor | Kliknutí bodu (kreslení) |
| LMB | Výběr propojení | Výběr propojení |
| LMB drag | Manipulátor | Manipulace (gizmo) |
| RMB | Propojení/Stěna/Místnost | Kontextová nabídka |
| RMB | Prázdný prostor | Zrušit (v módě) |
| Scroll | Libovolný | Zoom (PASS_THROUGH) |
| Scroll + Shift | Libovolný | Změna tloušťky nástroje |
| Střední myš | Libovolný | Pan pohledu |
| Shift + Střední | Libovolný | Rotace pohledu |

### Klávesnice

#### Primární zkratky

| Klávesa | Kontext | Funkce |
|---------|---------|--------|
| D | Libovolný | Aktivovat Tužka nástroj (Draw) |
| P | Libovolný | Parametrická úprava (Param) |
| E | Libovolný | Úpravy (Edit) - modální |
| F | Libovolný | Finalizace (Finish/Finalize) |
| X | Libovolný | Export |
| H | HUD viditelný | Skrýt HUD |
| G | Kreslení | Přichycování mřížky (Grid) |
| A | Kreslení | Přichycování úhlu (Angle) |
| Shift | Kreslení | Vypnout přichycování |
| Z | Kreslení | Vrátit bod (Undo) |
| Y | Kreslení | Znovu vytvořit bod (Redo) |
| Enter | Kreslení | Potvrdit bod |
| Esc | Kreslení | Zrušit akci |
| I | Libovolný | Importovat plán |
| O | Libovolný | Otevřít možnosti |

#### Sekundární zkratky

| Klávesa | Funkce |
|---------|--------|
| Ctrl+Z | Vrácení (Blender native) |
| Ctrl+Shift+Z | Opakování (Blender native) |
| Shift+D | Duplikovat vybraný prvek |
| Del | Smazat vybraný prvek |
| Num + | Zoom přiblížit (při kreslení) |
| Num - | Zoom oddálit (při kreslení) |
| . (Num) | Zaměřit na vybraný prvek |
| V | Přepnout viditelnost (místnost/stěna) |
| M | Přepnout režim zobrazení (Wireframe/Solid) |

---

## Dialog okna

### Dialog vlastností místnosti

```
┌─────────────────────────────────────────┐
│  Vlastnosti místnosti                   │
├─────────────────────────────────────────┤
│                                         │
│  Název:            [Obývací pokoj    ▼] │
│                                         │
│  Typ:              [Obytná          ▼] │
│                                         │
│  Plocha:           14.24 m²  (R/O)      │
│  Obvod:            15.60 m   (R/O)      │
│                                         │
│  ─────────────────────────────────────  │
│  Materiál podlahy: [Dub           ▼]   │
│  Barva podlahy:    [Přirozená     ▼]   │
│  ─────────────────────────────────────  │
│  Materiál stropu:  [Omítka        ▼]   │
│  Barva stropu:     [Bílá          ▼]   │
│  ─────────────────────────────────────  │
│  Poznámka:                              │
│  [Hlavní obývací prostor s krbem]       │
│                                         │
│  ─────────────────────────────────────  │
│                         [OK]  [Zrušit]  │
└─────────────────────────────────────────┘
```

### Dialog vlastností stěny

```
┌─────────────────────────────────────────┐
│  Vlastnosti stěny                       │
├─────────────────────────────────────────┤
│                                         │
│  Délka:            4.24 m   (R/O)       │
│  Tloušťka:         0.20 m   [     ⬆ ]  │
│  Výška:            3.00 m   [     ⬆ ]  │
│                                         │
│  ─────────────────────────────────────  │
│  Typ:              [Interní         ▼]  │
│  Materiál:         [Cihla          ▼]   │
│  Barva:            [Krémová        ▼]   │
│                                         │
│  ─────────────────────────────────────  │
│  ☐ Nosná stěna                          │
│  ☐ Zvukotěsná                          │
│  ☐ Umožnit okna                        │
│  ☐ Umožnit dveře                       │
│                                         │
│  ─────────────────────────────────────  │
│                         [OK]  [Zrušit]  │
└─────────────────────────────────────────┘
```

### Dialog finalizace

```
┌──────────────────────────────────────────┐
│  Finalizace půdorysu                     │
├──────────────────────────────────────────┤
│                                          │
│  Metoda pečení:                          │
│  ○ Geometry Nodes (doporučeno)           │
│  ○ BMesh (alternativa)                   │
│                                          │
│  ─────────────────────────────────────── │
│  Organizace objektu:                     │
│  ○ Sloučeno (jeden objekt)               │
│  ○ Odděleno (místnost = objekt)          │
│  ○ Rozděleno (typ = objekt)              │
│                                          │
│  ─────────────────────────────────────── │
│  ☐ Přiřadit materiály                    │
│  ☐ Vytvořit kolekce                      │
│  ☐ Optimalizovat geometrii               │
│                                          │
│  ─────────────────────────────────────── │
│  ☐ Ponechat originál (nedestruktivní)   │
│  ☐ Smazat atributy po pečení             │
│  ☐ Smazat Geometry Nodes po pečení       │
│                                          │
│  ─────────────────────────────────────── │
│                     [Pečit!]  [Zrušit]  │
└──────────────────────────────────────────┘
```

---

## Vizuální styl

### Barvy

```
┌──────────────────────────────────────────┐
│ Primární barvy                           │
│ ├─ FP Modrá:    #4A90E2  (Hlavní acent)  │
│ ├─ FP Tmavě:    #2C3E50  (Pozadí)        │
│ └─ FP Světlá:   #ECF0F1  (Text)          │
│                                          │
│ Sekundární barvy                         │
│ ├─ Úspěch:      #27AE60  (Zelená)        │
│ ├─ Varování:    #F39C12  (Oranžová)      │
│ ├─ Chyba:       #E74C3C  (Červená)       │
│ └─ Info:        #3498DB  (Jasná modrá)   │
│                                          │
│ UI prvky                                 │
│ ├─ Stěna normální:   #A0A0A0 (Šedá)     │
│ ├─ Stěna vybraná:    #4A90E2 (Modrá)    │
│ ├─ Propojení norm.:  #666666 (Tmavá)    │
│ ├─ Propojení vyb.:   #FFD700 (Zlatá)    │
│ ├─ Náhled:           #90EE90 (Sv. zelená) │
│ └─ Mřížka:           #D3D3D3 (Sv. šedá) │
└──────────────────────────────────────────┘
```

### Typy textu

| Prvek | Styl | Použití |
|-------|------|--------|
| Nadpis | Sans-serif, 18px, Bold | Panel záhlaví |
| Popis | Sans-serif, 12px, Regular | Obsah panelu |
| Chyba | Sans-serif, 11px, Bold, Červená | Chybové zprávy |
| HUD | Monospace, 11px, Regular | Náhledové informace |
| Tlačítko | Sans-serif, 12px, Bold | Interaktivní prvky |

---

## Zpřístupnění a nápověda

### Nápověda v aplikaci

1. **Klávesová nápověda** (Stiskněte H v operátoru kreslení)
   - Zobrazit všechny dostupné klávesy
   - Popis každé funkce
   - Dynamicky se mění dle stavu

2. **Nástrojové tipy** (Hover na tlačítka)
   - Krátký popis funkce
   - Zkratka klávesy (pokud existuje)
   - Upozornění (pokud relevantní)

3. **Stavové zprávy** (Dolní levý HUD)
   - Instruktivní zprávy průběhu kreslení
   - Varovné zprávy při problémech
   - Chybové zprávy s návrhy

### Piktogramy

```
Piktogramy nástrojů:
├─ Tužka:     ✏️  (kreslení)
├─ Parametr:  ⚙️  (nastavení)
├─ Úprava:    ✂️  (úpravy)
├─ Finalizace: 🔒 (finalizace)
├─ Export:    📤 (export)
├─ Importace: 📥 (importace)
└─ Nastavení: ⚡ (konfigurační)
```

---

## Responzivní prvky

### Dynamické čtení HUD

```python
# HUD se automaticky adaptuje:
- Při změně nástroje: Nový obsah HUD
- Při změně stavu: Nová instrukce
- Při pohybu myši: Aktualizovány souřadnice
- Při přichycování: Indikátor aktivace
```

### Výklopné panely

```
┌─ Místnosti ────────────┐
│ [▼] Obývací pokoj      │
│     ├─ Plocha: 14.2m²  │
│     ├─ Tloušťka: 0.2m  │
│     └─ Materiál: Dub   │
│ [▶] Ložnice            │
└────────────────────────┘
```

Panely se rozbalují/sbalují kliknutím na ikonu [▼] / [▶].

---

## Výkonnostní optimalizace UI

1. **Vykreslování HUD**: Pouze když je operátor aktivní
2. **Panely**: Lazy-loading (načítají se pouze když otevřeny)
3. **Seznamy**: Virtualizovány (viditelné položky pouze)
4. **Výběry**: Využívají Blender native selection system
5. **Aktualizace**: Batched (maximálně 1x za frame)
