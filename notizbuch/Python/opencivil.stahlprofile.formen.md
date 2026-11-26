---
erzeugt: 03d784f18c40
art: modul
tags: [modul]
---
> [!abstract] opencivil/stahlprofile/formen.py
> die Formen der Stahlprofile, mit ihren Formeln.
> Paket [[opencivil.stahlprofile]] · [Quelltext](../../opencivil/stahlprofile/formen.py)

## VERANTWORTUNG

Je Form eines Walzprofils oder Rohrs die Masse und die Formeln fuer `A`,
`I_y`, `I_z` und `I_T` -- als Vorlage in Zeichen und als Rechnung, wie
bei den Vorlagen der Stabquerschnitte ([[opencivil.stabwerk.querschnitte]]),
deren [[opencivil.stabwerk.querschnitte#Stabvorlage|Stabvorlage]] sie sind. Welche Groessen es gibt, sagt die
Profiltabelle ([[opencivil.stahlprofile.tabelle]]). Dazu je Form ihr
Umriss: das Bild im Balkensystem, die Flaeche in der Querschnittsanalyse
([[opencivil.stahlprofile.lage]]).


## DIE FORMEN

I-Profil (IPE, HEA, HEB, HEM), U-Profil mit parallelen Flanschen (UPE),
U-Profil mit geneigten Flanschen (UNP), kaltgefertigtes Rechteckrohr (RRK)
und Rundrohr (ROR).


## ACHSEN

Das Profil steht: der Steg senkrecht, beim U der Ruecken links. `y` ist
die waagrechte Achse durch den Schwerpunkt -- die starke --, `z` die
senkrechte. `e_y` ist der Abstand des Schwerpunkts vom Ruecken des U.


## DIE FORMELN

nach Vorgabe, nicht nachgeschlagen
Die Formeln der I- und UPE-Profile und der Rohre sind die der Tabelle des
Benutzers («Festigkeitsnachweise I-Standardprofile Stahl», 2019-04-15), mit
denselben gerundeten Beiwerten der Ausrundungen ([[opencivil.stahlprofile.formen#Konstanten|ZWICKEL]]). Beim UNP
hat die Tabelle nur Werte, keine Formeln: gerechnet wird mit geneigten
Flanschen als Trapezen und den Ecken wie beim rechten Winkel. Das trifft
die Werte der Tabelle auf 0.6 % (A, I_y) und 1.4 % (e_y, I_z); das I_T des
UNP rechnet wie beim UPE, mit t_f und r_1.


## EINHEITEN

Masse in mm, `A` in cm², die Traegheitsmomente in cm⁴ -- wie in der
Tabelle, damit sich vergleichen laesst.

## Inhalt

### _zwickel

```python
def _zwickel(r: str, abstand: str) -> str
```

Ein Zwickel mit Radius `@r`, um eine Achse im `abstand` seines Schwerpunkts.

### _u_torsion

```python
def _u_torsion(form: str, r: str) -> Tuple[Kennformel, Kennformel]
```

`d_K` und `I_T` eines U -- beim UPE mit `r`, beim UNP mit `r_1`:
zwei Flansche mit einem freien Ende, der Steg dazwischen, und je Knoten
der Kreis, der hineinpasst.

### _rohr_traegheit

```python
def _rohr_traegheit(achse, quer: str, laengs: str) -> Kennformel
```

`I_y` oder `I_z` eines Rechteckrohrs: `quer` steht senkrecht zur
Achse, `laengs` laeuft mit ihr. Aussen fehlen vier Zwickel mit `r_o`,
innen kommen vier mit `r_i` hinzu -- das Loch hat runde Ecken.

### ausgerundet

```python
def ausgerundet(ecken: Sequence[Punkt], radien: Sequence[float]) -> List[Punkt]
```

Das Vieleck `ecken` -- jede Ecke mit einem Radius durch einen Bogen
ersetzt, der beide Kanten beruehrt. Ob die Ecke aussen liegt oder innen,
ob die Kanten im rechten Winkel stehen oder nicht: der Bogen liegt im
Winkel zwischen ihnen.

### _u_umriss

```python
def _u_umriss(h: float, b: float, t_w: float, t_1: float, t_2: float, r_1: float, r_2: float) -> List[List[Punkt]]
```

Ein U, der Ruecken links -- am Steg `t_1` dick, an der Spitze `t_2`.

### _in_cm

```python
def _in_cm(f: Kennformel) -> Kennformel
```

Eine Formel der Vorlagen, in den Einheiten der Profile: Flaechen in cm², Momente in cm⁴.


## Konstanten

- `ZWICKEL = (0.2146, 0.2234, 0.00755)` – Der Zwickel zwischen zwei Kanten im rechten Winkel und einem Viertelkreis mit Radius r, gerundet wie in der Tabelle: Flaeche 0.2146 r² (1 - π/4), Abstand des Schwerpunkts von jeder Kante 0.2234 r ((10 - 3π)/(12 - 3π)), Traegheitsmoment um den eigenen Schwerpunkt 0.00755 r⁴ (1/3 - π/16 - 1/(3(12 - 3π))) -- um beide Achsen dasselbe.
- `BOGENECKEN = 12` – Je Viertelkreis eines Umrisses so viele Ecken. Die Querschnittsanalyse rechnet mit dem Umriss ([[opencivil.stahlprofile.lage|lage]]): mit 12 trifft er A und I der Tabelle bei den I- und UPE-Profilen auf 0.06 %, beim RRK auf 0.33 % -- mit 6, wie bis 2026-11-26 fuer das Bild, waren es 0.24 % und 1.3 %.
- `ROHRECKEN = 96` – So viele Ecken hat der Umriss eines Rundrohrs -- doppelt so viele wie ein Kreis der Vorlagen ([[opencivil.querschnitt.vorlagen#Konstanten|KREISECKEN]]): A trifft dann die Tabelle auf 0.08 %, I auf 0.15 %.
- `_RRK = 'kaltgefertigten Rechteckrohrs'`
- `_I = 'I-Profils'`
- `I_PROFIL = Stabvorlage(schluessel='i_profil', name='I-Profil', masse=(Mass('h', …` – I-Profil -- IPE, HEA, HEB, HEM: Steg und zwei gleiche Flansche, vier Ausrundungen r.
- `_UPE = 'U-Profils mit parallelen Flanschen'`
- `U_PARALLEL = Stabvorlage(schluessel='u_parallel', name='U-Profil mit parallelen Fl…` – U-Profil mit parallelen Flanschen -- UPE: Steg ueber die ganze Hoehe, zwei Ausrundungen r.
- `_UNP = 'U-Profils mit geneigten Flanschen'`
- `U_GENEIGT = Stabvorlage(schluessel='u_geneigt', name='U-Profil mit geneigten Flan…` – U-Profil mit geneigten Flanschen -- UNP: die Flansche innen um `p` geneigt, `t_f` gilt im Abstand `c` vom Ruecken; am Steg die Ausrundung `r_1`, an der Spitze die Rundung `r_2`.
- `RECHTECKROHR_KALT = Stabvorlage(schluessel='rechteckrohr_kalt', name='Rechteckrohr, kaltg…` – Rechteckrohr, kaltgefertigt -- RRK: Wand `t` ringsum, die Ecken aussen mit `r_o`, innen mit `r_i` gerundet; `h` steht senkrecht.
- `RUNDROHR = Stabvorlage(schluessel='rundrohr', name='Rundrohr', masse=KREISRING.m…` – Rundrohr -- ROR: aussen `D`, Wand `t`; die Formeln und Seiten des Kreisrings, nur in cm² und cm⁴, der Umriss feiner ([[opencivil.stahlprofile.formen#Konstanten|ROHRECKEN]]).
- `PROFILFORMEN = (I_PROFIL, U_PARALLEL, U_GENEIGT, RECHTECKROHR_KALT, RUNDROHR)`

## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.querschnitt.vorlagen]]
- [[opencivil.stabwerk.querschnitte]]

## Gebraucht von

- [[opencivil.nachweis.qa_stahl_stabilitaet]]
- [[opencivil.stahlbau.stabilitaet]]
- [[opencivil.stahlprofile.tabelle]]

## Formeln aus diesem Modul

- [[Dicke des geneigten Flanschs am Steg]]
- [[Dicke des geneigten Flanschs an der Spitze]]
- [[Fläche eines I-Profils]]
- [[Fläche eines kaltgefertigten Rechteckrohrs]]
- [[Fläche eines U-Profils mit geneigten Flanschen]]
- [[Fläche eines U-Profils mit parallelen Flanschen]]
- [[Flächenträgheitsmoment eines I-Profils um y]]
- [[Flächenträgheitsmoment eines I-Profils um z]]
- [[Flächenträgheitsmoment eines kaltgefertigten Rechteckrohrs um y]] · `_rohr_traegheit`
- [[Flächenträgheitsmoment eines kaltgefertigten Rechteckrohrs um z]] · `_rohr_traegheit`
- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um y]]
- [[Flächenträgheitsmoment eines U-Profils mit geneigten Flanschen um z]]
- [[Flächenträgheitsmoment eines U-Profils mit parallelen Flanschen um y]]
- [[Flächenträgheitsmoment eines U-Profils mit parallelen Flanschen um z]]
- [[Kreis im Knoten eines I-Profils]]
- [[Schwerpunkt eines U-Profils mit geneigten Flanschen]]
- [[Schwerpunkt eines U-Profils mit parallelen Flanschen]]
- [[Torsionsträgheitsmoment eines I-Profils]]
