---
erzeugt: dca5205a79ab
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/beispiele_verbund.py
> die Querschnitte im Verbund des Pruefprojekts.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/beispiele_verbund.py)

## VERANTWORTUNG

Die Querschnittsanalysen nach SIA 264:2014, die «Jeder Nachweis»
([[opencivil.projekt.beispiele#jeder_nachweis|opencivil.projekt.beispiele.jeder_nachweis]]) einmal laut fuehrt:
zwei Verbundtraeger, einer mit Kopfbolzenduebeln, zwei Verbundstuetzen
und zwei Blechverbunddecken. Sie zeigen auf die Materialien des
Pruefprojekts: `b1` C30/37, `s1` B500B, `st1` S355, `st2` S460 und
`pb1` SE 350 G. Bis 2026-11-27 standen sie in
[[opencivil.projekt.beispiele]], die sonst ueber tausend Zeilen bekommen
haette.

## Inhalt

### traeger

```python
def traeger(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein HEA 300 aus S460 unter einer Platte 1500 × 120 mm aus C30/37, Beton
auch zwischen den Flanschen, Betonstahl B500B in der Platte, zweiachsig
(SIA 264:2014). Der Kammerbeton hebt die gedrückten Flansche nach
Tabelle 3 in die Klasse 2 und den Steg nach 5.2.1.3; S460 mindert mit β.

Im Feld plastisch und schief, die Nulllinie im Profil; an der Stütze
negativ, der Betonstahl gezogen, mit einer Querkraft über der Hälfte von
V_Rd, die dem Steg nimmt, und mit Torsion, die nur ein Hinweis ist; mit
viel Druck reicht die Druckzone über 0.4 h, wo Figur 1 endet; reiner Zug,
reiner Druck und eine Druckkraft jenseits des Widerstands.

### traeger_mit_duebeln

```python
def traeger_mit_duebeln(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein IPE 400 aus S355 unter einer Platte 2000 × 150 mm aus C30/37 mit
Betonstahl B500B, einachsig, mit Kopfbolzendübeln ⌀19 × 125 mm (SIA
264:2014, 6.1). Im Feld teilverdübelt, (29) gehalten -- mit zu wenig
Dübeln nicht; an der Stütze verlangt das negative Moment volle
Verdübelung; ohne Zahl der Dübel und ohne L_e grau; L_e über 25 m
verlangt volle Verdübelung; ohne Moment prüft er die Dübel nicht. Als
Verbundstütze kennt ihn Tabelle 7 nicht: sein Stabilitätsfall steht grau.

### stuetze

```python
def stuetze(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein HEB 300 aus S355, ganz einbetoniert in 500 × 500 mm aus C30/37, mit
vier ⌀20 aus B500B in den Ecken, zweiachsig, Kriechzahl 2 (SIA 264:2014,
5.3). Einachsig gebogen um y, zweiachsig, zentrisch, um y gehalten und
ohne Druck; grau, wo die Knicklänge die Stütze überragt und wo λ̄ über 2
liegt; ausgeknickt, wo N_Ed N_cr,eff erreicht.

### rohr

```python
def rohr(kennung: str) -> QuerschnittsanalyseEintrag
```

Ein ROR 219.1 x 8 aus S355, mit C30/37 gefüllt und vier ⌀16 aus B500B,
einachsig (SIA 264:2014, 5.3): der Beton mit 1.0 statt 0.85 (5.3.2.5),
ρ_s unter 3 % und darum Kurve a, ohne Kriechen.

### blechdecke

```python
def blechdecke(kennung: str) -> QuerschnittsanalyseEintrag
```

Eine Blechverbunddecke nach Vorgabe -- fuenf offene Rippen aus SE 350 G
unter 140 mm C30/37, ohne Betonstahl --, das Endfeld einer durchlaufenden
Decke unter gleichmaessiger Last (SIA 264:2014, 5.4). Im Feld Biegung,
Querkraft und Laengsschub, mit L/d_p ueber 26; an der Stuetze traegt
nichts Zug -- das Blech zaehlt dort nicht --, der Widerstand ist null;
Druck mit kleinem Moment und reiner Zug, bei dem das Blech zaehlt.

### hinterschnittene_blechdecke

```python
def hinterschnittene_blechdecke(kennung: str) -> QuerschnittsanalyseEintrag
```

Eine Decke von 200 mm auf hinterschnittenen Rippen, oben ⌀10 @ 150 aus
B500B, ein Innenfeld unter zwei Einzellasten (SIA 264:2014, 5.4): `b_0`
ist dann `b_o`, die Schublaenge der Abstand `a`, und `d_p` liegt
ueber 150 mm -- fuer die Querkraft gaelte SIA 262, das sagt ihr Urteil
mit einem Hinweis. An der Stuetze traegt der
Betonstahl; ein Fall mit `M_z` sagt, dass die Decke nur in einer
Richtung traegt.


## Braucht

- [[opencivil.projekt.querschnittsanalyse]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.verbund.blechdecke]]
- [[opencivil.verbund.duebel]]

## Gebraucht von

- [[opencivil.projekt.beispiele]]
