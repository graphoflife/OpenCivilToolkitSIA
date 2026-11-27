"""
opencivil/decke/fem -- die Decke nach der Methode der finiten Elemente.

VERANTWORTUNG:
Die zweite Art, eine Decke zu rechnen, neben der Streifenmethode: die ganze
Platte linear elastisch und ungerissen (SIA 262:2025, 4.1.4.1.1 und
4.1.4.1.3), als Platte nach Kirchhoff aus Dreiecken.

- :mod:`~opencivil.decke.fem.delaunay` -- Dreiecke über Punkten,
- :mod:`~opencivil.decke.fem.netz` -- das Netz der Decke, das ihren Linien folgt,
- :mod:`~opencivil.decke.fem.element` -- das Dreieck DKT und der Träger als Balken,
- :mod:`~opencivil.decke.fem.system` -- Lager, Unbekannte, Steifigkeit, Zerlegung,
- :mod:`~opencivil.decke.fem.belastung` -- die Lasten auf die Knoten,
- :mod:`~opencivil.decke.fem.glaetten` -- die Schnittkräfte an den Knoten,
- :mod:`~opencivil.decke.fem.rechnung` -- je Lastfall und Kombination,
- :mod:`~opencivil.decke.fem.auswertung` -- an einer Stelle, längs eines Schnitts, im Träger,
- :mod:`~opencivil.decke.fem.herleitung` -- wie sie es aufschreibt.

Die Ergebnisse haben die Formen der Streifenmethode, damit Bilder und
Bericht beide gleich zeigen (:mod:`opencivil.web.deckendaten`).
"""
