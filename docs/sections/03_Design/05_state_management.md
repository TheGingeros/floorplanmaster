# 3.5 Správa stavu a event pipeline

Tento dokument popisuje, jak FloorPlanMaster spravuje stavy operátora, zpracovává vstupní události, implementuje snapping a udržuje historii undo/redo. Je kritický pro pochopení toho, jak operátor "Tužka" funguje v reálném čase.

Když jste v "režimu kreslení" a pohybujete myškou, co se děje? Pojďme si to rozebrat.

Addon pracuje s modálním operátorem - to je interaktivní nástroj, který "zachvátí" vstup od uživatele a reaguje na něj. Musí si pamatovat svůj stav: "Jsem v START (čekám na první bod)?" "Jsem v DRAWING (vykresluju náhled)?" "Jsem v CONFIRMING (čekám, než uživatel potvrdí parametry)?"

Operátor musí také:
- Zpracovat stovky event za sekundu (myš se pohybuje mnohem rychleji, než se kreslí)
- Přichytit kurzor k bodům, mřížce, osám nebo úhlům (snapping)
- Udržovat historii pro undo/redo (co jsem přidal, mohu vrátit)
- Aktualizovat náhled v reálném čase (60 FPS)
- Synchronizovat data s Blenderem (atributy, objekty)
- Zvládat chyby elegantně

V tomto dokumentu se dozvíte:
- Úplný stavový automat s 5 stavy a všemi přechody
- Event pipeline: jak se vstup zpracovává od klasifikace až po vykreslení
- Čtyři typy snappingu (grid, angle, point, axis) s algoritmy
- Undo/redo architektura integrovaná s Blenderem
- Optimalizace výkonu (debouncing, cachování, batching)
- Zpracování chyb a obnova

Toto je nejkomplexnější část - zde se vše spojuje dohromady. Musíte pochopit stavový automat, abyste mohli implementovat FP1 Tužku.

## Přehled

Správa stavu v FloorPlanMaster je řízena modálními operátory, stavovými automaty a event pipeline. Cílem je zachovat logiku oddělenu od Blender UI a umožnit kompletní undo/redo bez vedlejších účinků.

---

## Stavové automaty

### Státu Tužka (Draw Pencil Tool)

Modální operátor implementuje stavový automat se 5 stavy.

```
        ╔═════════════════════════════╗
        ║        START STATE          ║
        ║ (očekávání prvního kliknutí)║
        ╚═════════════════════════════╝
                        │
                        │ uživatel klikne (LMB)
                        │ validate_click_position()
                        │
                        ▼
        ╔═════════════════════════════╗
        ║      DRAWING STATE          ║
        ║ (interaktivní kreslení)    ║
        ║                             ║
        ║ - náhled stěny (live)       ║
        ║ - zpracování pohybu myši    ║
        ║ - přichycování              ║
        ║ - klávesy: Z (undo),        ║
        ║           Y (redo),         ║
        ║           Esc (cancel)      ║
        ║           Enter/LMB (next)  ║
        ╚═════════════════════════════╝
         ▲                         │
         │ Z (vrátit)             │ klik/Enter (potvrzení)
         │                        │ add_wall()
         │                        │ update_graphs()
         └────────────────────────┘
                                  │
                                  ▼
        ╔═════════════════════════════╗
        ║    CONFIRMING STATE         ║
        ║ (potvrzení parametrů)       ║
        ║                             ║
        ║ - vstup tloušťky            ║
        ║ - vstup výšky               ║
        ║ - potvrzení/zrušení         ║
        ╚═════════════════════════════╝
                        │
                        │ Enter (accept)
                        │ add_to_collection()
                        │ undo_push()
                        │
                        ▼
        ╔═════════════════════════════╗
        ║    RECORDING STATE          ║
        ║ (záznam do history)         ║
        ║                             ║
        ║ - vytvoření kroku vrácení   ║
        ║ - příprava na další stěnu   ║
        ╚═════════════════════════════╝
                        │
                        │ [LOOP → DRAWING]
                        │ nebo
                        │ Esc (končit režim)
                        │
                        ▼
        ╔═════════════════════════════╗
        ║     FINISHED STATE          ║
        ║ (čištění a výstup)          ║
        ║                             ║
        ║ - vyčištění předchod. stav  ║
        ║ - deregistrace handleru     ║
        ║ - vrácení FINISHED          ║
        ╚═════════════════════════════╝
```

### Tabulka přechodů stavů

| Aktuální | Výstup | Akce | Příští | Poznámka |
|----------|--------|-------|--------|----------|
| START | LMB | add_junction() | DRAWING | Přidat propojovací bod |
| START | Esc | cleanup() | FINISHED | Zrušit operátor |
| DRAWING | LMB/Enter | add_wall() + validate() | CONFIRMING | Přidat stěnu |
| DRAWING | Z | undo_last_point() | START | Vrátit poslední bod |
| DRAWING | Mouse | update_preview() | DRAWING | Náhled v reálném čase |
| DRAWING | Esc | cleanup() | FINISHED | Zrušit operátor |
| CONFIRMING | Enter | push_undo_step() | RECORDING | Potvrdit stěnu |
| CONFIRMING | Esc | revert_wall() | DRAWING | Zrušit stěnu |
| RECORDING | [auto] | next_state() | DRAWING | Příprava na další |
| RECORDING | Esc | cleanup() | FINISHED | Zrušit režim kreslení |

### Stavové proměnné

```python
class DrawState:
    """Stavová instance operátora kreslení"""
    
    # Identifikátory
    current_state: str  # "START", "DRAWING", "CONFIRMING", "RECORDING", "FINISHED"
    mode: str  # "new", "edit", "append"
    
    # Geometrie
    current_junction_id: int | None  # ID aktuálního propojení
    preview_junction_pos: tuple[float, float, float]  # (X, Y, Z) pozice náhledu
    walls_in_session: list[int]  # ID stěn vytvořené v rámci session
    
    # Parametry
    current_thickness: float  # tloušťka stěny v metrech
    current_height: float    # výška stěny v metrech
    snap_mode: str  # "free", "grid", "angle", "point"
    snap_distance: float  # vzdálenost přichycování (pixely)
    
    # Historie
    undo_stack: list[dict]  # Historie akcí v session
    redo_stack: list[dict]  # Vrácené akce
    
    # HUD
    show_hud: bool  # Viditelnost HUD
    mouse_pos: tuple[int, int]  # Aktuální pozice myši (screen space)
    world_pos: tuple[float, float, float]  # Pozice myši v světě
```

---

## Event Pipeline

### Zpracování vstupů

```
Vstup (Mouse/Keyboard)
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Klasifikace vstupů               │
│    - Identifikovat typ: LMB, RMB,   │
│      Mouse, Keyboard, Scroll        │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 2. Validace kontextu                │
│    - Je operátor aktivní?           │
│    - Správný stavový kontext?       │
│    - Priorita: modal > pass_through │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 3. Aplikace přichycování            │
│    - Grid snapping                  │
│    - Angle snapping                 │
│    - Point snapping                 │
│    - Axis snapping                  │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 4. Vykonání akce                    │
│    - Přidání bodu/stěny             │
│    - Aktualizace grafu              │
│    - Detekce cyklů                  │
│    - Undo/Redo                      │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 5. Vykreslování                     │
│    - Náhled stěny                   │
│    - HUD overlay                    │
│    - GPU vykreslování               │
│    - Aktualizace pohledu            │
└──────────┬──────────────────────────┘
           │
           ▼
         Výstup (RUNNING_MODAL)
```

### Tabulka event zpracování

| Event | Kategorie | Priorita | Handler | State |
|-------|-----------|----------|---------|-------|
| LMB | Input | Vysoká | handle_click() | Libovolný |
| RMB | Input | Vysoká | handle_context_menu() | Libovolný |
| Mouse Motion | Input | Střední | handle_mouse_move() | DRAWING |
| Scroll | Input | Nízká | PASS_THROUGH | Libovolný |
| Střed. Myš | Input | Nízká | PASS_THROUGH | Libovolný |
| Klávesa | Input | Vysoká | handle_key() | Libovolný |
| Timer | System | Střední | timer_tick() | DRAWING |

### Hlavní handler zpracování

```python
def modal(self, context, event):
    """Hlavní modální handler"""
    
    # PASS_THROUGH pro pohyb pohledu
    if event.type in {'SCROLL', 'MIDDLEMOUSE'}:
        return {'PASS_THROUGH'}
    
    # Klasifikace vstupů
    if event.type == 'MOUSEMOVE':
        return self.handle_mouse_move(context, event)
    
    elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
        return self.handle_click(context, event)
    
    elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
        return self.handle_context_menu(context, event)
    
    elif event.type in self.KEYMAP:
        return self.handle_key(context, event)
    
    elif event.type == 'TIMER':
        return self.handle_timer(context, event)
    
    else:
        return {'RUNNING_MODAL'}
```

---

## Snapping mechanismus

### Typy snappingu

#### 1. Grid Snap
```
┌─────────────────────────────────────┐
│ Povoleno: Uživatel stiskne 'G'      │
│ Vzdálenost: 0.1m, 0.5m, 1.0m       │
│                                     │
│ Výpočet:                            │
│ snapped_x = round(x / grid) * grid  │
│ snapped_y = round(y / grid) * grid  │
│                                     │
│ Vizualizace: Kurzor skáče na body   │
│ mřížky, body jsou zvýrazněny        │
└─────────────────────────────────────┘
```

#### 2. Angle Snap
```
┌─────────────────────────────────────┐
│ Povoleno: Uživatel stiskne 'A'      │
│ Úhly: 0°, 45°, 90°, 135°, atd.      │
│                                     │
│ Výpočet:                            │
│ angle = atan2(dy, dx)               │
│ snapped_angle = round(angle / 45°)  │
│ snapped_x = dist * cos(snapped_ang) │
│ snapped_y = dist * sin(snapped_ang) │
│                                     │
│ Vizualizace: Linie se přichytí k    │
│ nejbližšímu úhlu, zobrazit stupně   │
└─────────────────────────────────────┘
```

#### 3. Point Snap
```
┌─────────────────────────────────────┐
│ Povoleno: Vždy aktivní              │
│ Vzdálenost: 15 pixelů v screen      │
│ Toleranční poloměr: 0.01m (svět)    │
│                                     │
│ Výpočet:                            │
│ for junction in all_junctions:      │
│   if distance(mouse, junction) < 15px:
│     snapped_pos = junction.pos      │
│                                     │
│ Vizualizace: Kruh kolem bodu,       │
│ kurzor skáče na propojení           │
└─────────────────────────────────────┘
```

#### 4. Axis Snap
```
┌─────────────────────────────────────┐
│ Povoleno: Vždy aktivní              │
│ Tolerance: 10 pixelů od osy         │
│                                     │
│ Výpočet:                            │
│ if abs(mouse_x - start_x) < 10px:   │
│   snapped_y = start_y (vertikální)  │
│ if abs(mouse_y - start_y) < 10px:   │
│   snapped_x = start_x (horizontální) │
│                                     │
│ Vizualizace: Čáry os procházející   │
│ počátečním bodem, kurzor se přichyt │
└─────────────────────────────────────┘
```

### Indikátor snappingu

```python
def draw_snap_indicator(self, context):
    """Vykreslování indikátoru přichycování v GPU"""
    
    if self.snap_active:
        # Kruh kolem bodu snappingu
        draw_circle(
            position=self.snap_pos,
            radius=15,  # pixely
            color=(0.0, 1.0, 0.5, 0.8),  # zelená
            segments=16
        )
        
        # Typ snappingu jako text
        snap_text = {
            'grid': f"Grid: {self.snap_distance}m",
            'angle': f"Angle: {self.snap_angle}°",
            'point': "Point",
            'axis': f"Axis: {'X' if self.snap_axis == 0 else 'Y'}"
        }
        draw_text(
            text=snap_text[self.snap_mode],
            position=self.snap_pos,
            size=12,
            color=(0.0, 1.0, 0.5, 1.0)
        )
```

---

## Undo/Redo systém

### Architektura

FloorPlanMaster využívá Blender native undo/redo mechanismu s vlastní implementací.

```python
def apply_undo_step(self, context):
    """Vytvoření kroku vrácení v Blenderu"""
    
    # Připravit data pro vrácení
    undo_step = {
        'type': 'wall_addition',
        'wall_id': wall.id,
        'junction_ids': [start_id, end_id],
        'thickness': wall.thickness,
        'height': wall.height,
        'timestamp': time.time()
    }
    
    # Zaregistrovat u operátora
    bpy.ops.ed.undo_push(
        message=f"Add Wall {wall.id}"
    )
```

### Operace Undo/Redo

| Operace | Zpracování | Efekt |
|---------|-----------|--------|
| Vrátit (Ctrl+Z) | Smazat poslední stěnu | Obnovit stav |
| Znovu (Ctrl+Shift+Z) | Znovu přidat stěnu | Vrátit vrácení |
| Opakovat (Y v režimu) | Lokální redo | Znovu bod |
| Vrátit (Z v režimu) | Lokální undo | Vrátit bod |

### Historie v session

```python
class SessionHistory:
    """Historie akcí v rámci session kreslení"""
    
    def __init__(self):
        self.actions = []  # list[Action]
        self.current_idx = -1
    
    def record_action(self, action: dict):
        """Zaznamenat akci"""
        self.actions.append(action)
        self.current_idx += 1
    
    def undo(self):
        """Vrátit poslední akci"""
        if self.current_idx > 0:
            self.current_idx -= 1
            return self.actions[self.current_idx]
    
    def redo(self):
        """Znovu vytvořit akci"""
        if self.current_idx < len(self.actions) - 1:
            self.current_idx += 1
            return self.actions[self.current_idx]
```

---

## Optimalizace výkonu

### Event debouncing

```python
def handle_mouse_move(self, context, event):
    """Optimalizované zpracování pohybu myši"""
    
    # Debouncing - aktualizovat náhled pouze každých 16ms (60 FPS)
    current_time = time.time()
    if current_time - self.last_update_time < 0.016:
        return {'RUNNING_MODAL'}
    
    self.last_update_time = current_time
    
    # Aktualizovat náhled
    self.update_preview(context, event)
    
    return {'RUNNING_MODAL'}
```

### Cachování výpočtů

```python
def get_nearby_junctions(self, world_pos, tolerance=0.01):
    """Efektivní hledání blízkých propojení"""
    
    # Kontrola cache
    cache_key = tuple(world_pos)
    if cache_key in self._cache:
        return self._cache[cache_key]
    
    # Výpočet
    nearby = [j for j in self.junctions 
              if distance(j.pos, world_pos) < tolerance]
    
    # Uložit do cache
    self._cache[cache_key] = nearby
    
    return nearby
```

### Batching operací

```python
def batch_update_graphs(self, walls_added):
    """Dávková aktualizace grafů"""
    
    # Zastavit refresh během dávky
    context.scene.update_tag(refresh={'GEOMETRY'})
    
    # Aktualizovat vrstvu 1
    for wall in walls_added:
        self.graph_layer1.add_edge(wall.start_id, wall.end_id)
    
    # Detekovat cykly jednou
    self.graph_layer2.detect_cycles()
    
    # Refresh
    context.scene.update_tag(refresh={'GEOMETRY'})
```

---

## Chybové stavy a obnova

### Detekce chyb

```python
def validate_wall_creation(self, start_id, end_id):
    """Validace před vytvořením stěny"""
    
    errors = []
    
    # Kontrola: duplicitní propojení
    if start_id == end_id:
        errors.append("Nemůžete vytvořit stěnu samo sobě")
    
    # Kontrola: stěna již existuje
    if self.graph_layer1.has_edge(start_id, end_id):
        errors.append("Stěna mezi těmito body již existuje")
    
    # Kontrola: bod blízký existujícímu
    if len(self.get_nearby_junctions(start_pos)) > 0:
        errors.append("Bod je příliš blízko existujícího bodu")
    
    return errors
```

### Zpracování chyb

```python
def handle_error(self, error_msg: str):
    """Obnovená chybě"""
    
    # Zobrazit zprávu uživateli
    self.hud.show_error(error_msg)
    
    # Vrátit do DRAWING bez úspěšného přidání
    self.state = "DRAWING"
    
    # Zaznamenat do logu
    logger.warning(f"Draw error: {error_msg}")
```

---

## Synchronizace stavu

### Aktivní synchronizace s Blender objekty

```python
def sync_junction_to_blender(self, junction_id):
    """Synchronizace propojovacího bodu s Blender objektem"""
    
    junction = self.graph_layer1.get_junction(junction_id)
    obj = context.scene.objects.get(f"junction_{junction_id}")
    
    if obj:
        obj.location = junction.position
        obj['junction_id'] = junction_id
        obj['wall_ids'] = list(junction.wall_ids)
```

### Pasivní monitorování

```python
def check_external_changes(self, context):
    """Kontrola změn mimo operátor (např. mazání objektu)"""
    
    for junction in self.graph_layer1.junctions:
        obj = context.scene.objects.get(f"junction_{junction.id}")
        if not obj:
            # Objekt byl smazán, obnova
            logger.warning(f"Junction {junction.id} object missing")
            self.graph_layer1.remove_junction(junction.id)
```
