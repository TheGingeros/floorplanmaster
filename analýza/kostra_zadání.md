**Název práce (CZ):**
Vývoj nástroje pro konceptuální architektonické navrhování v prostředí Blender

### Cíl práce
Cílem práce je návrh a implementace doplňku (add-onu) pro software Blender, který zefektivní proces tvorby architektonických studií. Nástroj propojí intuitivnost skicování (workflow inspirované nástroji typu SketchUp) s možností správy parametrických dat (základy BIM).

1. **Analýza současných řešení a požadavků**
    - Rešerše existujících nástrojů pro architektonický koncepční návrh (např. SketchUp, BlenderBIM, Archimesh) a srovnání jejich klíčových vlastností.
    - Analýza potřeb cílové skupiny (architekti, designéři) se zaměřením na přechod od 2D půdorysu k 3D modelu.

2. **Návrh řešení (Design & UX)**
    - Návrh uživatelského rozhraní a ovládání doplňku s důrazem na intuitivnost a rychlou iteraci návrhu.
    - Definice datového modelu pro architektonické prvky (nositelé informací, nejen geometrie).

3. **Implementace**
    - Vývoj doplňku v jazyce Python s využitím Blender API.
    - Implementace nástrojů pro generování 3D dispozic z 2D podkladů a manipulaci s objekty.
    
4. **Testování a vyhodnocení**
    - Ověření funkčnosti nástroje na modelovém příkladu (např. studie rodinného domu).
    - Vyhodnocení efektivity workflow ve srovnání se standardními postupy v Blenderu.

### Abstrakt (Návrh)
Tato bakalářská práce se zabývá absencí intuitivních nástrojů pro ranou fázi architektonického navrhování v open-source softwaru Blender. Zatímco Blender dominuje ve vizualizaci, jeho nativní modelovací nástroje jsou pro architektonické skicování často příliš technické. Práce analyzuje workflow průmyslových standardů a implementuje vlastní Python addon. Ten umožňuje uživatelům efektivně převádět 2D půdorysné informace do 3D prostoru, zachovat datovou strukturu prvků.