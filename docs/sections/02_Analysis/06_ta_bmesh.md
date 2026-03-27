# Datová struktura BMesh a její význam pro architektonické modelování
- BMesh je interní datová struktura Blenderu, která je na rozdíl od tradičních struktur založených na trojúhelnících podporuje n-gony (polygony s více než 4 vrcholy) 
- využívá systém podobný half-edge datovým strukturám, kde jsou vztahy mezi plochami a hranami uloženy tak, aby umožňovaly rychlou navigaci po povrchu sítě
- z pohledu parametrického modelování nabízí BMesh skrze python API (modul bmesh) nízkoúrovňový přístup k topologii
- možnost dotazovat se, které hrany jsou spojeny s daným vrcholem a tedy provádět akce jako je např. dissolve bez poškození okolní topologie
- tento přístup je nezbytný pro algoritmy, které vyžadují detailní manipulaci s jednotlivými elementy sítě na základě komplexních pravidel
## Implementace pomocí BMesh
- obvykle se začíná načtením 2D hran
- algoritmus musí identifikovat uzavřené smyčky hran představující obrysy místností nebo osy stěn
- výhodou Pythonu je snadná integrace s externími knihovnami pro výpočetní geometrii nebo grafové algoritmy
- operace tloušťky (offset) se v bmesh často provádí pomocí operátoru `bmesh.ops.bevel`
    - aplikovaný na hrany nebo vlastním algoritmem, který posouvá vrcholy podél normál hran
- API poskytuje funkci `offset_multiplier`, která pomáhá udržovat tloušťku stěny i při ostrých úhlech výpočtem sharpness faktoru vrcholu
- tento proces je v Pythonu relativně pomalý, zejména pokud je třeba neustále validovat integritu sítě a předcházet vzniku non-manifold geometrie
    - struktura sítě (mesh), která by nemohla existovat v reálném fyzickém světě