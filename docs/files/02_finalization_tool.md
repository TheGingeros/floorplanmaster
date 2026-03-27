# Finalizační nástroj
- převedení procedurální nebo parametrické geometrie na statický, optimalizovaný, topologicky čistý mesh představuje jeden z nejnáročnějších úkolů v moderních 3D produkčních pipelines
- základem pro jakoukoliv automatizaci finalizace je pochopení rozdílu mezi původními daty a generovanými daty, která jsou výsledkem vyhodnocovacího řetězce
## Mechanismus Dependency Graphu a jeho role v finalizaci
- Depsgraph funguje jako centrální uzel, který spravuje vztahy mezi objekty
- pro účely finalizace geometrie je klíčový tzv. Evaluated Depsgraph - obsahuje finální stav geometrie po započtení všech vlivů
- k získání finálního meshe pro export je nutné použít vyhodnocený objekt - pomocí metody `evaluated_get()`
- proces finalizace je tedy o extrakci vyhodnoceného stavu do nového, statického kontejneru
- výhodou tohoto přístupu je, že proces zůstává pro původní scénu nedestruktivní, dokud se vývojář nerozhodne původní objekt nahradit
- **Rozdíly v přístupu k datům:**

| **Datová vrstva** | **Přístup přes Python API** | **Obsah dat** |
| :--- | :--- | :--- |
| **Original Data**| `obj.data` | Základní mesh bez vlivu modifikátorů a uzlů |
| **Evaluated Object** | `obj.evaluated_get(depsgraph)` | Objekt se všemi aplikovanými modifikátory v reálném čase |
| **Evaluated Mesh** | `bpy.data.meshes.new_from_object(obj_eval)` | Nový, nezávislý mesh datablock vytvořený z vyhodnoceného objektu |
| **Legacy to_mesh** | 	`obj.to_mesh(scene, apply_modifiers, settings)` | Starší metoda, která vracela dočasný mesh |

## Bezpečná automatizace aplikace modifikátorů a Geometry Nodes
- aplikace modifikátorů přes Python API s sebou nese rizika spojená s nestabilitou kontextu a dynamickou povahou kolekcí modifikátorů
- iterace přes `obj.modifiers` a volání `bpy.ops.object.modifier_apply()` je náchylná k chybám, protože každá úspěšná aplikace modifikátoru mění indexy zbývajících položek v seznamu
- aby bylo možné aplikovat komplexní stack, který může obsahovat desítky položek včetně uzlů Geometry Nodes, je nutné implementovat robustní algoritmus, který počítá s možným selháním jednotlivých článků
- v praxi se osvědčily dva přístupy:
1. **Statický seznam jmen:**
     - před zahájením smyčky se vytvoří seznam jmen všech modifikátorů
     - smyčka pak iteruje přes tato jména a vyhledává modifikátory v objektu dynamicky podle názvu, nikoli podle indexu
2. **While smyčka s detekcí chyb:**
    - smyčka běží, dokud objekt obsahuje aplikovatelné modifikátory
    - pokud aplikace selže, modifikátor je označen jako rozbitý a přeskočen
- aplikace modifikátorů v Geometry Nodes vyžaduje specifickou pozornost
- kasické modifikátory pracují s fixními strukturami meshe, Geometry Nodes mohou měnit topologický typ
- po každé aplikaci uzlového systému může dojít k drastické změně v atributech objektu
## Správa UV map a atributů v procedurálním potrubí
- v Geometry Nodes jsou UV mapy reprezentovány jako 2D vektory uložené v doméně Face Corner
- pro export do herních enginů je však nezbytné, aby tyto atributy byly korektně identifikovány jako "UV vrstvy", jinak je exportéry jako FBX nebo glTF ignorují
- při finalizaci geometrie dochází často k situaci, kdy jsou UV data po aplikaci Geometry Nodes uložena pouze jako pojmenované atributy, aby se z nich staly funkční UV mapy editovatelné v UV Editoru, je nutné provést konverzi
- [Problém s pořadím UV map pro herní enginy](./02_01_finalization_tool.md#problém-s-pořadím-uv-map-pro-herní-enginy)
## Správa materiálových slotů a konsolidace geometrie
- při realizaci instancí v rámci Geometry Nodes dochází k procesu slučování geometrií, které mohou mít různé materiálové definice
- Blender v tomto případě agreguje všechny materiálové sloty ze všech vstupních geometrií do jednoho seznamu u výstupního meshe
- uzel Join Geometry a proces realizace instancí se řídí pravidlem, že výsledný mesh musí obsahovat všechny unikátní materiály ze vstupů
- to však v praxi často vede k redundanci, kdy objekt po finalizaci obsahuje desítky identických materiálových slotů, což zvyšuje počet draw calls v herních enginech
- při automatizaci finalizace je nezbytné implementovat materiálový cleanup:
1. **Analýza slotů:** skript projde všechny sloty objektu a identifikuje duplicitní materiály
2. **Přemapování indexů:** v rámci BMesh se změní index materiálu u všech polygonů tak, aby odkazovaly na první výskyt daného materiálu v seznamu slotů
3. **Odstranění prázdných slotů:** po přemapování se volá operace pro odstranění nepoužívaných slotů, čímž vznikne čistá materiálová definice

