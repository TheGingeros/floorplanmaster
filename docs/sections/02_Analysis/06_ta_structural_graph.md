# Strukturální graf pro základ kreslení
- pro reprezentaci logické struktury jako je budova jsou nejvhodnější **strukturální grafy:**
    - **Uzly/Vrcholy** reprezentují funkční prostory(místnosti) nebo wall-junctions (body setkání stěn) - možnost použít oba jako duální graf
    - **Hrany** reprezentují fyzické stěny nebo komunikační propojení(dveře, otvory)
- pro interaktivní kreslení je strukturální graf nezbytný, protože přímo odpovídá fyzické realitě stěn
##Reprezentace
    - Uzly ($V_s$) jsou body spojení stěn s XY souřadnicemi 
    - Hrany ($E_s$) jsou osy stěn
## Role
    - slouží jako vodicí geometrie pro Geometry Nodes
    - tato vrstva řeší úhly napojení a tloušťku stěn
## Technické specifikum
    - graf je planární. 
    - každá hrana v něm reprezentuje fyzickou stěnu, která odděluje buď dva prostory, nebo prostor od exteriéru