"""
opencivil/gleichungen -- Analytische Gleichungen, Zeile fuer Zeile.

Ein Blatt wie in Mathcad: jede Zeile eine Definition (``b = 2a + 1\\,\\mathrm{m}``),
eine Auswertung (``a \\cdot b =``), ein Projektwert (``f_{cd}`` aus einem
Baustoff) oder ein Text. Gerechnet wird mit Einheiten (:class:`Groesse`),
dargestellt wie jede Herleitung: Symbol, Formel, Zahlen, Ergebnis.

* :mod:`.ausdruck` -- Zerlegen, Auswerten und Darstellen einer Zeile.
* :mod:`.blatt`    -- das Blatt als Berechnung im Rechenwerk.
"""
