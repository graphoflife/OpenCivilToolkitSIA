---
erzeugt: 747bc6405a67
art: modul
tags: [modul]
---
> [!abstract] opencivil/web/werkstoffkurven.py
> die Spannung-Dehnung-Linie je Material, als JSON.
> Paket [[opencivil.web]] · [Quelltext](../../opencivil/web/werkstoffkurven.py)

## VERANTWORTUNG

Was der Reiter «Diagramme» unter «Werkstoffgesetze» zeichnet: je Material
seine Linie, aus denselben Gesetzen, mit denen der Querschnitt rechnet
([[opencivil.querschnitt.werkstoffgesetz]]), in ‰ und N/mm². Welche Art
welche Linie hat, steht in [[opencivil.web.werkstoffkurven#Konstanten|KURVEN]] -- eine neue Materialart ohne
Linie faellt im Test auf, nicht erst beim Rechnen.

Bis 2026-11-26 stand das in [[opencivil.web.diagrammdaten]], das damit
an tausend Zeilen kam.

## Inhalt

### werkstoffgesetze

```python
def werkstoffgesetze(aufbau: Aufbau, loesung: Loesung) -> dict
```

Punktfolgen der Spannungs-Dehnungs-Beziehungen, je Material.

Gerechnet wird mit denselben Gesetzen wie im Nachweis -- die Kurve zeigt
also genau das, was der Querschnittsintegration zugrunde liegt, und nicht
eine zweite, nachgebaute Fassung.

Vorzeichen wie im ganzen Werkzeug: Zug positiv. Der Beton liegt damit im
dritten Quadranten, der Stahl spannt sich ueber beide.

Welche Kurve ein Material hat, sagt seine Art ([[opencivil.web.werkstoffkurven#Konstanten|KURVEN]]); fehlt ein
Kennwert in der Loesung, hat es noch keine. Bis 2026-11-26 galt alles,
was nicht Beton war, als Betonstahl, und ein Baustahl fiel still weg,
weil ihm dessen Kennwerte fehlten.

Ausser Punkten und Marken kann eine Kurve einen `hinweis` tragen: was
das Bild nicht zeigt -- beim Spannstahl der flachere Anstieg der Litzen --,
und eine `zweite` Linie, die ein Schalter zeigt: beim Beton den
Spannungsblock, beim Holz den Druck elastisch-plastisch.

### _betonkurve

```python
def _betonkurve(wert, sorte: str, schritte: int=80) -> Optional[dict]
```

Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung -- mit
Bemessungswerten, ohne Kriechen, gebaut wie in jeder Rechnung: der
Beiwert aus `E_cm` ([[opencivil.querschnitt.werkstoffgesetz#Betongesetz.mit_modul|Betongesetz.mit_modul]]).

### _spannungsblock

```python
def _spannungsblock(f_cd: float, eps_c2d: float) -> dict
```

Der vereinfachte, rechteckige Spannungsverlauf.

Unterhalb von `(1 - 0.85) * eps_c2d` wird keine Spannung angesetzt,
darueber durchgehend `f_cd`. Das ist dieselbe Vereinfachung, die auch der
Handrechnung zugrunde liegt -- dort als Druckzone der Hoehe `0.85 x`.
Beide Bilder gehoeren zusammen, und genau deshalb steht die Stufe hier neben
der Parabel: man sieht, was man aufgibt, wenn man von Hand rechnet.

### _stahlkurve

```python
def _stahlkurve(wert, sorte: str) -> Optional[dict]
```

Betonstahl: bilinear, auf Zug und Druck getrennt begrenzt.

### _baustahlkurve

```python
def _baustahlkurve(wert, sorte: str) -> Optional[dict]
```

Baustahl: elastisch -- ideal plastisch, in Zug und Druck gleich, mit `f_yd = f_y / gamma_M1`.

### _profilblechkurve

```python
def _profilblechkurve(wert, sorte: str) -> Optional[dict]
```

Profilblechstahl: wie der Baustahl, mit `f_ypd = f_yp / gamma_ap`.

### _knickkurve

```python
def _knickkurve(gesetz: Stahlgesetz, titel: str, fliessen: str='ε_yd') -> dict
```

Eine Linie ohne Verfestigung, aus ihrem Gesetz. Fuenf Eckpunkte genuegen
-- dazwischen ist sie gerade, und mehr Punkte wuerden nur vortaeuschen,
dass etwas gekruemmt waere.

### _spannstahlkurve

```python
def _spannstahlkurve(wert, sorte: str) -> Optional[dict]
```

Spannstahl: Figur 17, nur auf Zug -- mit dem Modul der Draehte und
Staebe. Hat die Sorte auch Litzen (Tabelle 7), sagt der Hinweis, dass
sie flacher ansteigen (195 statt 200 GPa) und wo sie zu fliessen beginnen.

### _holzkurve

```python
def _holzkurve(wert, sorte: str) -> Optional[dict]
```

Holz: linear bis zum Bruch, auf Zug wie auf Druck (SIA 265:2012,
3.1.2.1) -- und als zweite Linie der Druck elastisch-plastisch (3.1.2.2),
bis zur Grenzstauchung nach Vorgabe.


## Konstanten

- `KURVEN = {Baustoffart.BETON: _betonkurve, Baustoffart.BETONSTAHL: _stahlkurve,…` – Je Materialart ihre Spannung-Dehnung-Linie, aus den Kennwerten einer Loesung -- wo es eines gibt, ein Gesetz des Querschnitts -- und der Sorte: beim Spannstahl sagt sie, ob es Litzen gibt.

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.core.rechenwerk]]
- [[opencivil.material.basis]]
- [[opencivil.material.spannstahl]]
- [[opencivil.projekt]]
- [[opencivil.querschnitt.werkstoffgesetz]]
- [[opencivil.web.anzeige]]

## Gebraucht von

- [[opencivil.web.api]]
