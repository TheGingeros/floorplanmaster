# 3.6 API rozhraní a třídy

Tento dokument je referenční dokumentace pro všechny Python třídy, jejich metody a signatury. Obsahuje kompletní specifikaci API pro třídy StructuralGraph, RoomGraph, AttributeSync a operátory. Slouží jako bible pro implementátora.

Toto je **API dokumentace**. Nenajdete zde dlouhé vysvětlování "proč" - najdete zde "co" a "jak".

Každá třída je specifikovaná s:
- **`__init__`** - jak ji inicializovat, jaké parametry má
- **Veřejné metody** - co s ní můžete dělat (`add_junction()`, `remove_wall()`, atd.)
- **Signatury** - jaké parametry metoda přijímá, co vrací
- **Chování** - co se stane, když zavoláte metodu
- **Výjimky** - jaké chyby mohou nastat
- **Příklady** - jak se třída používá v praxi

Třetiny:

**StructuralGraph (Vrstva 1)** - Spravuje topologický graf. Operace: přidávat/odebírat propojovací body, přidávat/odebírat stěny, hledat sousedy, aktualizovat vlastnosti.

**RoomGraph (Vrstva 2)** - Spravuje místnosti. Operace: detekce cyklů, tvorba místností, hledání sousedních místností, nejkratší cesty, izolované místnosti.

**AttributeSync (Vrstva 3)** - Synchronizace s Blenderem. Operace: mapování grafů na atributy, aktualizace objektů, dávkové synchronizace.

**Operátory a Panely** - Blender UI prvky. FLOORPLAN_OT_draw_pencil je modální operátor kreslení.

V tomto dokumentu se dozvíte:
- Kompletní API všech tříd s metodami a podpisy
- Jak třídy používat v praxi (příklady kódu)
- Jaké jsou výjimky a chyby
- Výčty a konstanty (ROOM_TYPES, WALL_TYPES, atd.)
- Jak třídy interagují s Blenderem

Toto je váš zdroj pravdy pro implementaci - když si nejste jisti, jak zavolat metodu, podívejte se sem.

## Přehled

Tato sekce definuje úplné Python API pro FloorPlanMaster addon. Všechny třídy, metody a atributy jsou specifikovány s jejich podpisy a chováním.

---

## Vrstva 1: Strukturální graf

### Třída `StructuralGraph`

Spravuje propojovací body a stěny jako orientovaný graf.

```python
class StructuralGraph:
    """
    Reprezentuje strukturální prvky půdorysu (propojení, stěny).
    Používá NetworkX DiGraph pro efektivní operace.
    """
    
    def __init__(self, scene: bpy.types.Scene):
        """
        Inicializace strukturálního grafu.
        
        Args:
            scene: Blender scéna pro vyhledání objektů
        """
        self.graph = nx.DiGraph()
        self.junctions: dict[int, Junction] = {}
        self.walls: dict[int, Wall] = {}
        self.next_junction_id = 0
        self.next_wall_id = 0
        self.scene = scene
        self.on_change: Callable = None  # event callback
    
    def add_junction(self, position: tuple[float, float, float], 
                    tolerance: float = 0.01) -> int:
        """
        Přidá propojovací bod do grafu.
        
        Args:
            position: Souřadnice (X, Y, Z) v světě
            tolerance: Minimální vzdálenost od existujících bodů
        
        Returns:
            ID nově přidaného bodu, nebo ID existujícího (pokud v toleranci)
        
        Raises:
            ValueError: Pokud je bod mimo svět nebo invalid
        """
        # Kontrola duplicitního bodu
        for j_id, junction in self.junctions.items():
            if self._distance(position, junction.position) < tolerance:
                return j_id
        
        # Vytvořit nový bod
        junction_id = self.next_junction_id
        self.next_junction_id += 1
        
        junction = Junction(
            id=junction_id,
            position=position,
            wall_ids=set()
        )
        
        self.junctions[junction_id] = junction
        self.graph.add_node(junction_id)
        
        if self.on_change:
            self.on_change('junction_added', junction_id)
        
        return junction_id
    
    def remove_junction(self, junction_id: int) -> bool:
        """
        Odebere propojovací bod a všechny připojené stěny.
        
        Args:
            junction_id: ID bodu k odstranění
        
        Returns:
            True pokud byl bod odstraněn, False pokud neexistoval
        """
        if junction_id not in self.junctions:
            return False
        
        junction = self.junctions[junction_id]
        
        # Odstranit všechny stěny připojené k tomuto bodu
        walls_to_remove = list(junction.wall_ids)
        for wall_id in walls_to_remove:
            self.remove_wall(wall_id)
        
        # Odstranit bod z grafu
        del self.junctions[junction_id]
        self.graph.remove_node(junction_id)
        
        if self.on_change:
            self.on_change('junction_removed', junction_id)
        
        return True
    
    def get_junction(self, junction_id: int) -> 'Junction | None':
        """Vrátí propojovací bod dle ID."""
        return self.junctions.get(junction_id)
    
    def add_wall(self, start_id: int, end_id: int,
                thickness: float = 0.2, height: float = 3.0,
                material: str = "Default") -> int:
        """
        Přidá stěnu mezi dvěma body.
        
        Args:
            start_id: ID počátečního propojení
            end_id: ID koncového propojení
            thickness: Tloušťka stěny v metrech
            height: Výška stěny v metrech
            material: Identifikátor materiálu
        
        Returns:
            ID nově přidané stěny
        
        Raises:
            ValueError: Pokud body neexistují nebo jsou shodné
        """
        if start_id not in self.junctions or end_id not in self.junctions:
            raise ValueError("Invalid junction IDs")
        
        if start_id == end_id:
            raise ValueError("Cannot create wall to itself")
        
        if self.graph.has_edge(start_id, end_id):
            raise ValueError("Wall already exists between these junctions")
        
        # Vytvořit stěnu
        wall_id = self.next_wall_id
        self.next_wall_id += 1
        
        wall = Wall(
            id=wall_id,
            start_id=start_id,
            end_id=end_id,
            thickness=thickness,
            height=height,
            material=material
        )
        
        self.walls[wall_id] = wall
        self.graph.add_edge(start_id, end_id, wall_id=wall_id)
        
        # Zaznamenat do propojení
        self.junctions[start_id].wall_ids.add(wall_id)
        self.junctions[end_id].wall_ids.add(wall_id)
        
        if self.on_change:
            self.on_change('wall_added', wall_id)
        
        return wall_id
    
    def remove_wall(self, wall_id: int) -> bool:
        """
        Odebere stěnu a aktualizuje propojení.
        
        Args:
            wall_id: ID stěny k odstranění
        
        Returns:
            True pokud byla stěna odstraněna
        """
        if wall_id not in self.walls:
            return False
        
        wall = self.walls[wall_id]
        
        # Odstranit z grafu
        self.graph.remove_edge(wall.start_id, wall.end_id)
        
        # Aktualizovat propojení
        self.junctions[wall.start_id].wall_ids.discard(wall_id)
        self.junctions[wall.end_id].wall_ids.discard(wall_id)
        
        # Odstranit stěnu
        del self.walls[wall_id]
        
        if self.on_change:
            self.on_change('wall_removed', wall_id)
        
        return True
    
    def get_wall(self, wall_id: int) -> 'Wall | None':
        """Vrátí stěnu dle ID."""
        return self.walls.get(wall_id)
    
    def get_neighbors(self, junction_id: int) -> list[int]:
        """Vrátí seznam sousedních propojení."""
        return list(self.graph.successors(junction_id))
    
    def update_wall_property(self, wall_id: int, property: str, value: any):
        """Aktualizuje vlastnost stěny."""
        if wall_id not in self.walls:
            raise ValueError(f"Wall {wall_id} not found")
        
        wall = self.walls[wall_id]
        if hasattr(wall, property):
            setattr(wall, property, value)
            if self.on_change:
                self.on_change('wall_property_changed', wall_id)
    
    def _distance(self, p1: tuple, p2: tuple) -> float:
        """Euclidovská vzdálenost mezi dvěma body."""
        return ((p1[0] - p2[0])**2 + 
                (p1[1] - p2[1])**2 + 
                (p1[2] - p2[2])**2) ** 0.5

# Pomocné třídy

class Junction:
    """Propojovací bod v sieti"""
    def __init__(self, id: int, position: tuple[float, float, float],
                wall_ids: set[int]):
        self.id = id
        self.position = position
        self.wall_ids = wall_ids

class Wall:
    """Stěna mezi dvěma propojovacími body"""
    def __init__(self, id: int, start_id: int, end_id: int,
                thickness: float = 0.2, height: float = 3.0,
                material: str = "Default"):
        self.id = id
        self.start_id = start_id
        self.end_id = end_id
        self.thickness = thickness
        self.height = height
        self.material = material
```

---

## Vrstva 2: Graf místností

### Třída `RoomGraph`

Spravuje místnosti a jejich vztahy.

```python
class RoomGraph:
    """
    Reprezentuje místnosti a jejich vazby (sousedství, hierarchie).
    Místo Room je polygon ohraničený stěnami.
    """
    
    def __init__(self, structural_graph: StructuralGraph):
        """
        Inicializace grafu místností.
        
        Args:
            structural_graph: Reference na vrstvu 1
        """
        self.rooms: dict[int, Room] = {}
        self.adjacency_graph = nx.Graph()  # neorientovaný graf
        self.structural_graph = structural_graph
        self.next_room_id = 0
        self.on_change: Callable = None
    
    def add_room(self, cycle: list[int], name: str = "Room",
                room_type: str = "generic") -> int:
        """
        Přidá místnost na základě cyklu v grafu.
        
        Args:
            cycle: Seznam ID propojení tvořících cyklus
            name: Jméno místnosti
            room_type: Typ (obytná, komerční, atd.)
        
        Returns:
            ID nově přidané místnosti
        """
        room_id = self.next_room_id
        self.next_room_id += 1
        
        room = Room(
            id=room_id,
            cycle=cycle,
            name=name,
            room_type=room_type,
            area=self._calculate_area(cycle),
            metadata={}
        )
        
        self.rooms[room_id] = room
        self.adjacency_graph.add_node(room_id)
        
        if self.on_change:
            self.on_change('room_added', room_id)
        
        return room_id
    
    def remove_room(self, room_id: int) -> bool:
        """Odebere místnost."""
        if room_id not in self.rooms:
            return False
        
        del self.rooms[room_id]
        self.adjacency_graph.remove_node(room_id)
        
        if self.on_change:
            self.on_change('room_removed', room_id)
        
        return True
    
    def get_room(self, room_id: int) -> 'Room | None':
        """Vrátí místnost dle ID."""
        return self.rooms.get(room_id)
    
    def add_adjacency(self, room1_id: int, room2_id: int,
                     wall_ids: set[int]):
        """
        Přidá vazbu sousedství mezi dvěma místnostmi.
        
        Args:
            room1_id: ID první místnosti
            room2_id: ID druhé místnosti
            wall_ids: Sada ID stěn dělící místnosti
        """
        if self.adjacency_graph.has_edge(room1_id, room2_id):
            return
        
        self.adjacency_graph.add_edge(
            room1_id, room2_id,
            wall_ids=wall_ids
        )
    
    def get_neighbors(self, room_id: int) -> list[int]:
        """Vrátí seznam sousedních místností."""
        return list(self.adjacency_graph.neighbors(room_id))
    
    def find_path(self, room1_id: int, room2_id: int) -> list[int] | None:
        """
        Najde cestu mezi dvěma místnostmi (Dijkstrův algoritmus).
        
        Returns:
            Seznam ID místností na cestě, nebo None pokud cesta neexistuje
        """
        try:
            path = nx.shortest_path(self.adjacency_graph,
                                   room1_id, room2_id)
            return path
        except nx.NetworkXNoPath:
            return None
    
    def get_isolated_rooms(self) -> list[int]:
        """Vrátí seznam izolovaných místností."""
        isolated = []
        for room_id in self.rooms:
            if self.adjacency_graph.degree(room_id) == 0:
                isolated.append(room_id)
        return isolated
    
    def _calculate_area(self, cycle: list[int]) -> float:
        """Výpočet plochy místnosti pomocí Shoelaceova vzorce."""
        if len(cycle) < 3:
            return 0.0
        
        coords = [self.structural_graph.get_junction(j_id).position
                 for j_id in cycle]
        
        area = 0.0
        for i in range(len(coords)):
            x1, y1, _ = coords[i]
            x2, y2, _ = coords[(i + 1) % len(coords)]
            area += (x1 * y2 - x2 * y1)
        
        return abs(area) / 2.0
    
    def detect_cycles(self) -> list[list[int]]:
        """
        Detekuje všechny základní cykly v grafu.
        
        Returns:
            Seznam cyklů (každý je seznam ID propojení)
        """
        cycles = []
        
        # Použít NetworkX algoritmus pro hledání cyklů
        for cycle in nx.simple_cycles(self.structural_graph.graph):
            if len(cycle) >= 3:
                cycles.append(cycle)
        
        return cycles

class Room:
    """Místnost reprezentovaná jako polygon"""
    def __init__(self, id: int, cycle: list[int], name: str,
                room_type: str, area: float, metadata: dict):
        self.id = id
        self.cycle = cycle  # seznam ID propojení tvořících hranici
        self.name = name
        self.room_type = room_type
        self.area = area
        self.metadata = metadata
```

---

## Vrstva 3: Synchronizace atributů

### Třída `AttributeSync`

Spravuje synchronizaci pojmenovaných atributů Blenderu.

```python
class AttributeSync:
    """
    Mapuje graf (vrstva 1, 2) na pojmenované atributy Blenderu.
    Umožňuje Geometry Nodes číst data a aktualizovat geometrii.
    """
    
    JUNCTION_ATTRS = {
        'junction_id': 'INT',
        'wall_ids': 'STRING',  # JSON encoded
        'position': 'FLOAT_VECTOR'
    }
    
    WALL_ATTRS = {
        'wall_id': 'INT',
        'start_junction_id': 'INT',
        'end_junction_id': 'INT',
        'thickness': 'FLOAT',
        'height': 'FLOAT',
        'material_name': 'STRING'
    }
    
    ROOM_ATTRS = {
        'room_id': 'INT',
        'room_name': 'STRING',
        'room_type': 'STRING',
        'area': 'FLOAT',
        'cycle_junctions': 'STRING'  # JSON encoded
    }
    
    def __init__(self, structural_graph: StructuralGraph,
                room_graph: RoomGraph):
        """Inicializace synchronizace atributů."""
        self.structural_graph = structural_graph
        self.room_graph = room_graph
        self.object_cache: dict[int, bpy.types.Object] = {}
    
    def sync_junctions_to_scene(self, scene: bpy.types.Scene):
        """
        Synchronizuje propojovací body z grafu do objektů scény.
        Vytváří/aktualizuje objekty "junction_*"
        """
        for junction_id, junction in self.structural_graph.junctions.items():
            # Najít nebo vytvořit objekt
            obj_name = f"junction_{junction_id}"
            obj = scene.objects.get(obj_name)
            
            if not obj:
                # Vytvořit objekt
                mesh = bpy.data.meshes.new(obj_name)
                obj = bpy.data.objects.new(obj_name, mesh)
                scene.collection.objects.link(obj)
                
                # Přidat custom properties
                for attr_name, attr_type in self.JUNCTION_ATTRS.items():
                    self._add_attribute(obj.data, attr_name, attr_type)
            
            # Aktualizovat polohu a atributy
            obj.location = junction.position
            
            # Atributy
            obj['junction_id'] = junction_id
            obj['wall_ids'] = json.dumps(list(junction.wall_ids))
            
            self.object_cache[junction_id] = obj
    
    def sync_walls_to_scene(self, scene: bpy.types.Scene):
        """Synchronizuje stěny z grafu do atributů Blender objektů."""
        for wall_id, wall in self.structural_graph.walls.items():
            # Najít objekt stěny (obvykle síťový objekt)
            obj_name = f"wall_{wall_id}"
            obj = scene.objects.get(obj_name)
            
            if obj and obj.type == 'MESH':
                # Aktualizovat atributy
                obj['wall_id'] = wall_id
                obj['start_junction_id'] = wall.start_id
                obj['end_junction_id'] = wall.end_id
                obj['thickness'] = wall.thickness
                obj['height'] = wall.height
                obj['material_name'] = wall.material
    
    def sync_rooms_to_scene(self, scene: bpy.types.Scene):
        """Synchronizuje místnosti z grafu do atributů."""
        for room_id, room in self.room_graph.rooms.items():
            obj_name = f"room_{room_id}"
            obj = scene.objects.get(obj_name)
            
            if obj and obj.type == 'MESH':
                obj['room_id'] = room_id
                obj['room_name'] = room.name
                obj['room_type'] = room.room_type
                obj['area'] = room.area
                obj['cycle_junctions'] = json.dumps(room.cycle)
    
    def _add_attribute(self, mesh: bpy.types.Mesh,
                      name: str, attr_type: str):
        """Přidá pojmenovaný atribut k síťovému objektu."""
        if name not in mesh.attributes:
            if attr_type == 'INT':
                mesh.attributes.new(name, 'INT', 'POINT')
            elif attr_type == 'FLOAT':
                mesh.attributes.new(name, 'FLOAT', 'POINT')
            elif attr_type == 'FLOAT_VECTOR':
                mesh.attributes.new(name, 'FLOAT_VECTOR', 'POINT')
            elif attr_type == 'STRING':
                # Blender neobsahuje string atribut - použít custom property
                pass
    
    def batch_sync(self, scene: bpy.types.Scene):
        """
        Dávková synchronizace všech vrstev najednou.
        Optimalizováno pro výkon.
        """
        # Zastavit refresh během synchronizace
        with context.temporary_override(scene=scene):
            self.sync_junctions_to_scene(scene)
            self.sync_walls_to_scene(scene)
            self.sync_rooms_to_scene(scene)
        
        # Refresh geometrie
        scene.update_tag(refresh={'GEOMETRY'})
```

---

## Třídy operátorů

### `FLOORPLAN_OT_draw_pencil`

Modální operátor pro kreslení půdorysu.

```python
class FLOORPLAN_OT_draw_pencil(bpy.types.Operator):
    """Kreslení tužkou interaktivně"""
    
    bl_idname = "floorplan.draw_pencil"
    bl_label = "Draw Pencil"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        """Inicializace operátora"""
        # Inicializace stavu
        self.state = "START"
        self.structural_graph = context.scene.floorplan.structural_graph
        
        # Registrace modálního handleru
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}
    
    def modal(self, context, event):
        """Zpracování vstupů"""
        # Implementace dle 05_state_management.md
        pass
```

### `FLOORPLAN_OT_finalize`

Operátor pro finalizaci půdorysu.

```python
class FLOORPLAN_OT_finalize(bpy.types.Operator):
    """Finalizace půdorysu na trvalou geometrii"""
    
    bl_idname = "floorplan.finalize"
    bl_label = "Finalize Floorplan"
    bl_options = {'REGISTER', 'UNDO'}
    
    # Vlastnosti operátora
    method: bpy.props.EnumProperty(
        items=[('GEOMETRY_NODES', 'Geometry Nodes', 'Bake GN'),
               ('BMESH', 'BMesh', 'Direct mesh gen')],
        default='GEOMETRY_NODES'
    )
    
    organization: bpy.props.EnumProperty(
        items=[('MERGED', 'Merged', 'Single object'),
               ('BY_ROOM', 'By Room', 'Room per object'),
               ('BY_TYPE', 'By Type', 'Type per object')],
        default='BY_ROOM'
    )
    
    def execute(self, context):
        """Provede finalizaci"""
        # Implementace finalizačního procesu
        pass
```

---

## Panely vlastností

### `FLOORPLAN_PT_rooms`

Panel se seznamem místností.

```python
class FLOORPLAN_PT_rooms(bpy.types.Panel):
    """Panel pro správu místností"""
    
    bl_label = "Rooms"
    bl_idname = "FLOORPLAN_PT_rooms"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    
    def draw(self, context):
        """Vykreslení panelu"""
        layout = self.layout
        scene = context.scene
        
        # Seznam místností
        layout.label(text="Rooms:")
        
        for room in scene.floorplan.room_graph.rooms.values():
            row = layout.row()
            row.label(text=f"{room.name} ({room.area:.2f} m²)")
            row.operator("floorplan.edit_room", text="Edit")
            row.operator("floorplan.remove_room", text="X")
```

---

## Výčty a konstanty

```python
# Mody kreslení
DRAW_MODES = {
    'new': 'Nový plán',
    'edit': 'Úprava existujícího',
    'append': 'Přidání ke stávajícímu'
}

# Typy místností
ROOM_TYPES = {
    'residential': 'Obytná',
    'commercial': 'Komerční',
    'industrial': 'Průmyslová',
    'generic': 'Obecná'
}

# Typy stěn
WALL_TYPES = {
    'interior': 'Interní',
    'exterior': 'Vnější',
    'shared': 'Sdílená'
}

# Režimy přichycování
SNAP_MODES = {
    'free': 'Volný',
    'grid': 'Mřížka',
    'angle': 'Úhel',
    'point': 'Bod',
    'axis': 'Osa'
}
```
