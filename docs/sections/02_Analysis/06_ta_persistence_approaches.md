# Přístupy k perzistenci grafových dat v Blenderu

Blender při uložení `.blend` souboru automaticky ukládá veškerou mesh geometrii a Custom Properties objektů — Python objekty v paměti (NetworkX grafy) nikoli. Po zavření a opětovném otevření souboru jsou grafy ztraceny, pokud nejsou někde zachovány. Existují tři konceptuální přístupy:

| Přístup | Princip | Hlavní nevýhoda |
| :--- | :--- | :--- |
| **JSON v Custom Property** | Serializovat grafy do JSON stringu, uložit na objekt | Redundance — topologie je uložena dvakrát (mesh + JSON); nutno verzovat schéma |
| **Pickle v Custom Property** | Serializovat Python objekty do bajtů | Bezpečnostní riziko (spustitelný kód při deserializaci), citlivost na verze Pythonu/knihoven |
| **Rekonstrukce z meshe** | Po načtení přebudovat grafy z uložené mesh topologie | Vyžaduje, aby mesh byl jediným zdrojem pravdivých dat — platí pro architektury s vrstvou named attributes |

## Zhodnocení přístupů

**JSON v Custom Property** je nejpřístupnější a přímočarý, ale vede k redundanci dat: stejná topologická informace (junctiony, stěny) by existovala v meshi i v JSON stringu. Při každé změně by bylo nutné udržovat obojí synchronizovaně a při inkompatibilní změně schématu migrovat uložené soubory.

**Pickle** přidává bezpečnostní riziko — deserializace Pickle dat z externího souboru může spustit libovolný Python kód. V kontextu sdílených `.blend` souborů (např. v pracovní skupině) je to nepřijatelné. Navíc Pickle je citlivý na verze Pythonu i závislých knihoven.

**Rekonstrukce z meshe** je výhodná tehdy, pokud architektura addonu již pracuje s named attributes na base meshi (viz kapitola 3.2). V tom případě mesh přirozeně obsahuje veškerou topologickou informaci, takže samostatná serializace grafů je nadbytečná. Jedinou podmínkou je, aby mesh byl udržován jako jediný zdroj pravdivých dat — což je splněno v architektuře s dedikovanou synchronizační vrstvou.

Tento přístup je tedy výhodný specificky pro addony, které používají named attributes jako primární datové úložiště; pro addony bez takové vrstvy by byl komplikovanější.

[Zdroje](../../files/00_sources.md#ukládání-dat-a-správa-metadat)
