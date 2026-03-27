# Hybridní spojení - princip minimálních cyklů
- klíčem k realizaci je, že místnost v NRG je v podstatě minimální uzavřený cyklus ve strukturálním grafu

| Akce v addonu | Změna ve strukturálním grafu | Dopad na NRG Room Graph |
| :--- | :--- | :--- |
| Nakreslení nové stěny | Přidání hrany $E_s$ | Algoritmus hledá, zda vznikl nový cyklus. Pokud ano, v NRG vznikne uzel místnosti |
| Vložení dveří | Atribut na hraně $E_s$ | V NRG se vytvoří hrana $E_r$ propojující sousední uzly místností |
| Smazání stěny | Odstranění hrany $E_s$ | Dvě sousední místnosti v NRG se spojí do jedné (node fusion) pokud je stěna spojovala, jinak odstranění uzlu místnosti |