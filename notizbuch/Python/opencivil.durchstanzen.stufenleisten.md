---
erzeugt: 6b19dace7d58
art: modul
tags: [modul]
---
> [!abstract] opencivil/durchstanzen/stufenleisten.py
> Leisten an der Stufe eines Bereichs zur Stütze hin.
> Paket [[opencivil.durchstanzen]] · [Quelltext](../../opencivil/durchstanzen/stufenleisten.py)

## VERANTWORTUNG

Hält der Schnitt an der Stufe eines Bereichs zur Stütze hin nicht (Figur
24a, [[opencivil.durchstanzen.stufen|.stufen]]), schlägt das Werkzeug dort eigene Leisten vor – einen
Satz je Stufe, neben dem an der Stütze –, mit denselben vier Nachweisen wie
an der Stütze (4.3.6.5.1, [[opencivil.durchstanzen.mit_bewehrung#am_ort|.mit_bewehrung.am_ort]]) und je Bereich
eigenen Graden ([[opencivil.durchstanzen.stufenleisten#grade|grade]]). Der Schnitt an der Stufe hat dann kein
eigenes Urteil mehr: wie an der Stütze bleibt sein Grad ohne Bewehrung ein
Wert der Herleitung.


## WIE DIE LEISTEN STEHEN

(nach Vorgabe, nicht nachgeschlagen – die Norm regelt
Leisten an einer Stufe nicht im Einzelnen):

- Der Bereich ist ihre gestützte Fläche, mit seiner konvexen Hülle wie der
  Schnitt an der Stufe (Figur 22c). Die Leisten setzen an ihr an wie an
  einer Stütze oder einem Stahlpilz und laufen nach aussen.
- Sie sind so hoch, wie die Platte jenseits der Stufe dick ist, bleiben in
  dem Bereich, der dort liegt, und ausserhalb aller übrigen, je c_nom von
  der Stufe ([[opencivil.durchstanzen.mit_bewehrung#Platz|.mit_bewehrung.Platz]]).
- Es gelten d, d_v, k_e, u, k_r und die Querkraft des Schnitts an der Stufe;
  ψ ist das der Stütze, wie für V_Rd,c an der Stufe.
- k_sys gilt wie an der Stütze: ein Kopf über einer Innenstütze trägt wie
  eine grosse Innenstütze.


## WO NICHT

Auf der Gegenseite (Figur 24c) liegt der Schnitt innerhalb des Bereichs,
und der Schnitt durch verschiedene Dicken ([[opencivil.durchstanzen.weg|.weg]]) hat keine Stufe, an
der eine Leiste ansetzen könnte: dort schlägt das Werkzeug keine eigenen
vor ([[opencivil.durchstanzen.stufenleisten#moeglich|moeglich]]).


## EINHEITEN

SI-Basis; Kräfte in N.

## Inhalt

### moeglich

```python
def moeglich(bereich: Plattenbereich) -> bool
```

Ob an der Stufe dieses Bereichs Leisten stehen können: nur zur Stütze hin (Dateikopf).

### grade

```python
def grade(basis: str, bereich: Plattenbereich) -> Tuple[WertDef, ...]
```

Die vier Grade mit Leisten an der Stufe von `bereich`, in der Reihe von
[[opencivil.durchstanzen.mit_bewehrung#Konstanten|.mit_bewehrung.FAELLE]].

### nachweisen

```python
def nachweisen(n: 'Durchstanzen', e: Eingaben, p: Protokoll, w: Zwischenwerte, g: 'Stuetzenschnitt', r: 'Widerstand', st: Stufe, sw: Stufenwerte) -> Tuple[List[NachweisUrteil], Optional[Leistenpruefung]]
```

Die Leisten an der Stufe `st`, deren Schnitt ohne sie nicht hält: ihre
vier Urteile und die Leisten – oder, wo keine passt, die Urteile offen
mit dem Grund. `sw` sind die Werte des Schnitts an der Stufe.

### _platz

```python
def _platz(e: Eingaben, g: 'Stuetzenschnitt', st: Stufe) -> Platz
```

Wo die Leisten an der Stufe liegen dürfen: in dem, was jenseits liegt, so
hoch, wie es dick ist, und ausserhalb aller Bereiche, die den Bereich der
Stufe weder enthalten noch in ihm liegen.


## Konstanten

- `ZU_69 = 'In (69) gilt dasselbe ψ wie für V_Rd,c an der Stufe: die Drehung der…` – Was die Herleitung zu ψ und d in (69) an einer Stufe sagt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.nachweis]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.durchstanzen.bereiche]]
- [[opencivil.durchstanzen.mit_bewehrung]]
- [[opencivil.durchstanzen.nachweis]]
- [[opencivil.durchstanzen.pruefung]]
- [[opencivil.durchstanzen.schnitt]]
- [[opencivil.durchstanzen.stufen]]

## Gebraucht von

- [[opencivil.durchstanzen.nachweis]]
