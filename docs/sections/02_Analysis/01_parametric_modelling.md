# Parametrické modelování a prostorová dispozice
úvod here

## Parametrické modelování
- způsob vytváření 3D modelů
- exaktně definován uživatelem stanovenými proměnnými a pevnými geometrickými vztahy, kde tvůrce přímo kontroluje vstupy a algoritmickou logiku závislostí
- tvar objektu není definován pevně, je definován pomocí parametrů (čís. hodnot) a vztahů
- čtverec například nadefinujeme takto:
    - parametr A: šířka - 100mm
    - parametr B: délka - 50mm
    - pravidlo: strany jsou na sebe kolmé
    - později je možné parametry změnit a čtverec se sám překreslí
- rozdíly oproti klasickému polygonálnímu modelování: polygonální vs parametrické
    - práce s body, hranami, plochami, táhnutí pro úpravu VS. práce s čísly, funkcemi, historií kroků
    - obtížné změny vs. snadné změny
    - využítí pro hry, filmy, animace vs. architektura, strojírenství, design produktů
- dva typy parametrického modelování:
    - **Historické** - CAD/BIM
        - software si pamatuje časovou osu úprav/kroků
        - např. 1. vytvoř kvádr, 2. zaobli hrany, 3. vytvoř díru 
        - možnost se vrátit ke kroku 1. a změnit velikost kvádru a software automaticky přepočítá zaoblení a vytvořenou díru
        - standard ve strojírenství(SolidWorks) a architektuře (Revit)
    - **Algoritmické** - vizuální skriptování
        - používané v moderní architektuře, hodně podobné geometry nodes

## Problematika parametrického modelování v architektuře
- představuje fundamentální posun od tradičního reprezentování kreslení k algoritmickému a objektově orientovanému přístupu
- tradiční systémy [CAD](../../files/00_definitions.md#computer-aided-design---cad-počítačem-podporované-projektování) se spoléhají na explicitní definici geometrie pomocí statických bodů, úseček a mnohoúhelníků reprezentující pouhé vizuální symboly
- parametrické modelování zavádí systém vzájemně propojených proměnných, matematických omezení a deduktivních pravidel, které dynamicky generují a aktulizují výslednou formu
- umožňuje, aby modifikace jediného parametru – například celkové výšky podlaží nebo tloušťky nosné stěny – automaticky a kaskádovitě modifikovala všechny závislé entity, jako jsou příčky, vkládaná okna či schodiště, aniž by bylo nutné tyto prvky manuálně a destruktivně přestavovat
- je potřeba rozlišovat mezi parametrickým modelováním, [procedurálním generováním](../../files/00_definitions.md#procedurální-generování) a [informačním modelováním](../../files/00_definitions.md#building-information-modeling---bim-informační-modelování-staveb)
- ačkoliv se tyto tři domény v praxi do jisté míry překrývají, vývoj 

[Zdroje](../../files/00_sources.md#problematika-parametrického-modelování)


## Prostorová dispozice
- logické a funkční uspořádání trojrozměrného objemu do smysluplných celků (místností a zón) a definování vztahů mezi nimi