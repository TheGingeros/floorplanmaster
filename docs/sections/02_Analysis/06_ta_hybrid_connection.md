# Hybridní spojení - princip minimálních cyklů
- klíčem k realizaci je, že místnost v NRG je v podstatě minimální uzavřený cyklus ve strukturálním grafu

| Akce v addonu | Změna ve strukturálním grafu | Dopad na NRG Room Graph |
| :--- | :--- | :--- |
| Nakreslení nové stěny | Přidání hrany $E_s$ | Algoritmus hledá, zda vznikl nový cyklus. Pokud ano, v NRG vznikne uzel místnosti |
| Vložení dveří | Atribut na hraně $E_s$ | V NRG se vytvoří hrana $E_r$ propojující sousední uzly místností |
| Smazání stěny | Odstranění hrany $E_s$ | Dvě sousední místnosti v NRG se spojí do jedné (node fusion) pokud je stěna spojovala, jinak odstranění uzlu místnosti |

## Strategie detekce místností: lazy vs. eager

Při návrhu detekčního mechanismu existují dvě základní strategie.

**Eager přístup** — každá nová stěna dostane při vzniku odkaz na "tentativní místnost" (polotovar); při uzavření polygonu se z ní stane plná místnost, při sloučení se rozhodne, která přežije.

**Lazy přístup** — místnost vznikne výhradně tehdy, kdy je detekován uzavřený cyklus v strukturálním grafu; do té doby žádný objekt místnosti neexistuje.

### Problémy eager přístupu

**1. Nedefinovaný stav tentativní místnosti**
Eager přístup vyžaduje zavést objekt "polotovar místnosti" — entitu, která existuje, ale nemá uzavřenou geometrii. Tato entita musí být reprezentována, udržována a odstraňována. Je to celá kategorie stavu navíc s vlastními přechody.

**2. Merge conflict při uzavření cyklu**
Když uživatel nakreslí uzavírající stěnu (čtvrtá stěna čtverce), existují čtyři stěny, každá s odkazem na jinou tentativní místnost. Systém musí vybrat jednu, přiřadit jejímu uzlu výsledné souřadnice a zbytek zrušit. Toto rozhodnutí nemá přirozené kritérium — závisí na pořadí kreslení.

**3. Simultánní uzavření více cyklů**
Přidáním jediné T-stěny lze uzavřít dva cykly najednou. Eager přístup musí detekovat a vyřešit $N$ merge operací v jediné transakci, přičemž každá může navzájem ovlivnit tu druhou.

**4. Rozbití Undo**
Undo vrácení uzavírající stěny musí "rozrozplynout" sloučené tentativní místnosti zpět do původního stavu — tedy uložit pre-merge snapshot. Eager přístup proto vyžaduje vlastní historii stavu, která je oddělená od Blender Undo stacku.

**5. History-dependence**
Stejná výsledná topologie lze sestavit různými posloupnostmi editací. V eager přístupu může identická geometrie vést k různým metadatovým stavům podle toho, jakou cestou k ní uživatel dospěl — to je těžko testovatelné a laditelné.

### Výhody lazy přístupu

**Invariant bez výjimek:** `Room ↔ minimální uzavřený cyklus` platí vždy a plně. Neexistuje žádný stav "rozpracované místnosti". Systém má vždy konzistentní obraz reality.

**Přirozené zvládnutí simultánních cyklů:** NetworkX vrátí seznam všech nových minimálních cyklů najednou — pro každý vznikne jeden Room node. Žádná merge logika.

**Undo zdarma:** Odebrání uzavírající stěny znamená zánik cyklu → zánik Room nodu. Přesně stejná logika se použije i při rekonstrukci z uloženého meshe (viz perzistence). Není potřeba vlastní snapshot mechanismus.

**Determinismus:** Stejná topologie Vrstvy 1 vždy produkuje stejnou Vrstvu 2 — bez závislosti na pořadí editací.

### Přijatelnost omezení pro uživatele

Lazy přístup neumožňuje pojmenovat prostor dříve, než je uzavřen. Toto je sémanticky správné chování — nepojmenovaná místnost neexistuje, pouze se staví. Žádný z analyzovaných nástrojů (RoomSketcher, Planner 5D, AutoCAD) tento "eager labeling" UX pattern nepoužívá. Pro uživatele addonu je omezení transparentní: metadata místnosti jsou dostupná v momentě, kdy místnost vznikne uzavřením polygonu.

**Závěr:** Lazy detekce je zvolená strategie. Výhody (invariant, determinismus, Undo integrace, jednoduchá implementace simultánních cyklů) jednoznačně převyšují jediné omezení (metadata nelze přiřadit před uzavřením), které se v praxi neprojeví.