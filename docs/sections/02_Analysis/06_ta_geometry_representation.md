# Reprezentace geometrie
- **geometrie** = definuje polohu prvků v prostoru
- **topologie** = definuje vzájemné vztahy a propojení
- v blenderu je základní jednotkou mesh - složena z vrcholů, hran a ploch
- každá mesh nese specifické informace o své roli v celkové struktuře

## [Datová struktura BMesh a její význam pro architektonické modelování](./06_ta_bmesh.md)
## [Geometry nodes a paradigma polí](./06_ta_geometry_nodes.md)
## Porovnání bmesh a Geometry nodes pro generování 3D stěn

| Charakteristika | BMesh | Geometry Nodes |
| :--- | :--- | :--- |
| **Základní jednotka** | Entita (Vertex, Edge, Face) | Doména a Atributy |
| **Způsob práce** | Iterativní / Imperativní | Paralelní / Deklarativní |
| **Výkon** | Omezený interpretací Pythonu  | Vysoce optimalizované C++  |
| **Topologická flexibilita** | Absolutní (přímá změna struktury) | Omezená na definované uzly |
| **Vizuální odezva** | Po spuštění skriptu | Real-time v 3D viewportu  |
## Výkonnostní analýza a stabilita
- v rozsáhlých scénách se Geometry nodes jeví jako efektivnější a rychlejší
- python script musí při každé změně znovu vybudovat celou BMesh strukturu a promítnout jí
- geometry nodes pracují v rámci modifikátorského stacku a reevaluují pouze nezbytné části

| Operace | bmesh (Python) | Geometry Nodes |
| :--- | :--- | :--- |
| **Vytváření tloušťky** | Přesné, ale výpočetně drahé | Vyžaduje manuální matematickou korekci |
| **Multithreading** | Ne (omezení Pythonu) | Ano (nativní implementace)  |
| **Stabilita topologie** | Riziko vzniku non-manifold chyb  | Stabilnější díky omezenému rozsahu operací |
| **Iterace vývoje** | Pomalá (editace kódu) |Rychlá (přetahování uzlů) |

[Zdroje](../../files/00_sources.md#reprezentace-geometrie---bmesh-a-geometry-nodes)