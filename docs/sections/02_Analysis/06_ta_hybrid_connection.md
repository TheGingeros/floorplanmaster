# Hybridní spojení - princip minimálních cyklů
- klíčem k realizaci je, že místnost v NRG je v podstatě minimální uzavřený cyklus ve strukturálním grafu

| Akce v addonu | Změna ve strukturálním grafu | Dopad na NRG Room Graph |
| :--- | :--- | :--- |
| Nakreslení nové stěny | Přidání hrany $E_s$ | Algoritmus hledá, zda vznikl nový cyklus. Pokud ano, v NRG vznikne uzel místnosti |
| Vložení dveří | Atribut na hraně $E_s$ | V NRG se vytvoří hrana $E_r$ propojující sousední uzly místností |
| Smazání stěny | Odstranění hrany $E_s$ | Dvě sousední místnosti v NRG se spojí do jedné (node fusion) pokud je stěna spojovala, jinak odstranění uzlu místnosti |

## Strategie detekce místností: lazy vs. eager

Při návrhu detekčního mechanismu existují dvě základní strategie.

**Eager přístup** — každá nová stěna je při svém vzniku přiřazena k dočasnému objektu místnosti. Jakmile dojde k uzavření polygonu, je tento objekt validován jako plnohodnotná místnost. V případě sloučení více dočasných objektů algoritmus určí, který z nich bude zachován.

**Lazy přístup** — místnost vznikne výhradně tehdy, kdy je detekován uzavřený cyklus v strukturálním grafu; do té doby žádný objekt místnosti neexistuje.

### Problémy eager přístupu

**1. Nedefinovaný stav dočasného objektu místnosti**
Eager přístup vyžaduje zavedení „dočasného objektu místnosti“ — entity, která je evidována v paměti, ale nedisponuje uzavřenou geometrií. Tento dočasný objekt musí být systémem průběžně reprezentován, udržován a případně odstraňován. Představuje tak celou novou kategorii stavu s vlastními pravidly pro přechody.

**2. Konflikt při slučování (Merge conflict) po uzavření cyklu**
Když uživatel nakreslí stěnu, která cyklus uzavírá (například čtvrtou stěnu čtverce), vznikne situace, kdy se setkají stěny s odkazy na různé dočasné objekty. Systém musí vybrat jeden z nich, přiřadit mu výslednou geometrii a zbylé objekty zrušit. Pro toto rozhodnutí však neexistuje objektivní kritérium — výsledek závisí čistě na pořadí, v jakém uživatel stěny kreslil.

**3. Simultánní uzavření více cyklů**
Přidáním jediné stěny (např. napojením ve tvaru písmene T) lze uzavřít dva či více cyklů současně. Eager přístup pak musí detekovat a vyřešit $N$ slučovacích operací v rámci jediné transakce, přičemž každá z těchto operací může kaskádovitě ovlivnit ty ostatní.

**4. Narušení kroku zpět (Undo)**
Aplikace funkce Undo na akci, která uzavřela cyklus, by musela sloučené dočasné objekty místností znovu rozpojit do jejich původního neuzavřeného stavu. To by vyžadovalo uložení přesného snímku stavu před sloučením (pre-merge snapshot). Eager přístup tak zbytečně vyžaduje vlastní komplexní správu historie, která je oddělená od nativního zásobníku historie (Undo stack) v Blenderu.

**5. Závislost na historii editace (History-dependence)**
Ke stejné výsledné topologii lze dospět různými posloupnostmi kroků. V eager přístupu se může stát, že identická výsledná geometrie povede k různým stavům metadat (např. zachování jiného ID místnosti) čistě v závislosti na tom, jakou cestou k ní uživatel dospěl. Takové nedeterministické chování je ze softwarového hlediska velmi obtížně testovatelné a laditelné.

### Výhody lazy přístupu

**Invariant bez výjimek:** `Room ↔ minimální uzavřený cyklus` platí vždy a plně. Neexistuje žádný stav "rozpracované místnosti". Systém má vždy konzistentní obraz reality.

**Přirozené zvládnutí simultánních cyklů:** NetworkX vrátí seznam všech nových minimálních cyklů najednou — pro každý vznikne jeden Room node. Žádná merge logika.

**Undo zdarma:** Odebrání uzavírající stěny znamená zánik cyklu → zánik Room nodu. Přesně stejná logika se použije i při rekonstrukci z uloženého meshe (viz perzistence). Není potřeba vlastní snapshot mechanismus.

**Determinismus:** Stejná topologie Vrstvy 1 vždy produkuje stejnou Vrstvu 2 — bez závislosti na pořadí editací.

### Přijatelnost omezení pro uživatele

Lazy přístup neumožňuje pojmenovat prostor dříve, než je uzavřen. Toto je sémanticky správné chování — nepojmenovaná místnost neexistuje, pouze se staví. Žádný z analyzovaných nástrojů (RoomSketcher, Planner 5D, AutoCAD) tento "eager labeling" UX pattern nepoužívá. Pro uživatele addonu je omezení transparentní: metadata místnosti jsou dostupná v momentě, kdy místnost vznikne uzavřením polygonu.

**Závěr:** Lazy detekce je zvolená strategie. Výhody (invariant, determinismus, Undo integrace, jednoduchá implementace simultánních cyklů) jednoznačně převyšují jediné omezení (metadata nelze přiřadit před uzavřením), které se v praxi neprojeví.