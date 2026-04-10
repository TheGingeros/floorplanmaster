# Interaktivní kreslení a interakce ve viewportu
Interaktivní kreslení ve viewportu stojí na modálních operátorech — podtřídách `bpy.types.Operator`, které po spuštění zůstávají aktivní a naslouchají událostem myši a klávesnice. Tato sekce popisuje jejich životní cyklus, stavový automat v metodě `modal()` a výkonnostní limity Pythonu v Blenderu spolu se strategiemi pro jejich překonání delegováním výpočtů na C++ jádro.
## [Modální operátory](./06_ta_modal_operators.md)
## [Limity výkonu Pythonu v Blenderu](./06_ta_limits_python_blender.md)