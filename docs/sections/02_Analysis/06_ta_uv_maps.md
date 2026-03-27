# Problém s pořadím UV map pro herní enginy:
- herní enginy jako Unreal Engine 5 vyžadují striktní pořadí UV kanálů
- blender však ukládá atributy v hash mapě - po aplikaci operací jako Join Geometry může dojít k náhodnému promíchání pořadí UV vrstev
- řešení spočívá v explicitním seřazením UV vrstev podle jména nebo indexu před finálním exportem:
1. Uložit data všech UV vrstev do paměti.
2. Odstranit všechny existující vrstvy
3. Znovu je vytvořit v požadovaném pořadí a data do nich vložit zpět
- alternativně lze upravit exportní skript (např. export_fbx_bin.py), aby při zápisu do souboru vynutil abecední řazení UV kanálů, což zajistí konzistenci v cílovém enginu