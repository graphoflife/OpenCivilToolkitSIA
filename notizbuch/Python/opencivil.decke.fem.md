---
erzeugt: a798291af40b
art: modul
tags: [modul]
---
> [!abstract] opencivil/decke/fem/__init__.py
> die Decke nach der Methode der finiten Elemente.
> Paket [[opencivil.decke]] · [Quelltext](../../opencivil/decke/fem/__init__.py)

## VERANTWORTUNG

Die zweite Art, eine Decke zu rechnen, neben der Streifenmethode: die ganze
Platte linear elastisch und ungerissen (SIA 262:2025, 4.1.4.1.1 und
4.1.4.1.3), als Platte nach Kirchhoff aus Dreiecken.

- [[opencivil.decke.fem.delaunay|delaunay]] – Dreiecke über Punkten,
- [[opencivil.decke.fem.netz|netz]] – das Netz der Decke, das ihren Linien folgt,
- [[opencivil.decke.fem.element|element]] – das Dreieck DKT und der Träger als Balken,
- [[opencivil.decke.fem.system|system]] – Lager, Unbekannte, Steifigkeit, Zerlegung,
- [[opencivil.decke.fem.belastung|belastung]] – die Lasten auf die Knoten,
- [[opencivil.decke.fem.glaetten|glaetten]] – die Schnittkräfte an den Knoten,
- [[opencivil.decke.fem.rechnung|rechnung]] – je Lastfall und Kombination,
- [[opencivil.decke.fem.auswertung|auswertung]] – an einer Stelle, längs eines Schnitts, im Träger,
- [[opencivil.decke.fem.herleitung|herleitung]] – wie sie es aufschreibt.

Die Ergebnisse haben die Formen der Streifenmethode, damit Bilder und
Bericht beide gleich zeigen ([[opencivil.web.deckendaten]]).

## Module

- [[opencivil.decke.fem.auswertung]] – die FEM an einer Stelle, längs eines Schnitts, im Träger.
- [[opencivil.decke.fem.belastung]] – die Lasten eines Falls auf den Knoten.
- [[opencivil.decke.fem.delaunay]] – eine Delaunay-Triangulierung, Punkt für Punkt.
- [[opencivil.decke.fem.element]] – das Dreieck der Platte und der Balken in ihr.
- [[opencivil.decke.fem.glaetten]] – die Schnittkräfte an den Knoten.
- [[opencivil.decke.fem.herleitung]] – wie die FEM einer Decke ihre Rechnung aufschreibt.
- [[opencivil.decke.fem.netz]] – das Dreiecksnetz einer Decke.
- [[opencivil.decke.fem.rechnung]] – die FEM der Decke, Fall für Fall.
- [[opencivil.decke.fem.system]] – das Gleichungssystem der Platte.
