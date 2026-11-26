---
erzeugt: ee3af9da6e2f
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_holz_werte.py
> die Werte eines Holzquerschnitts, einmal fuer alle Nachweise.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_holz_werte.py)

## VERANTWORTUNG

[[opencivil.nachweis.qa_holz_werte#HolzwerteQA|HolzwerteQA]] rechnet, was Kennzahlen
([[opencivil.nachweis.qa_holz_kennzahlen]]), Nachweise je Lastfall
([[opencivil.nachweis.qa_holz]]) und Stab
([[opencivil.nachweis.qa_holz_stabilitaet]]) lesen, und schreibt es
einmal in die Herleitung:

* den Beiwert η_w der Feuchteklasse (SIA 265:2012, Tabelle 4);
* je Achse das Widerstandsmoment bis zur weitesten Faser, beim
  Brettschichtholz den Hoehenbeiwert k_h (3.4.2.3);
* je Richtung einer Querkraft die Schubflaeche `A_V = I·b/S` nach
  Jourawski;
* beim Rechteck das Torsionswiderstandsmoment `W_T`.

Dazu, was die drei sonst teilen: die Kennwerte des Holzes als Eingaben
([[opencivil.nachweis.qa_holz_werte#stoffbezuege|stoffbezuege]]) und der Beiwert eines Falls, `η = η_w·η_t`
([[opencivil.nachweis.qa_holz_werte#beiwert|beiwert]]).


## EIN HOLZ

Gerechnet wird ein Querschnitt aus einem einzigen Holz. Aus mehreren
Hoelzern -- etwa C24 neben GL24h -- verteilten sich die Spannungen nach
ihren Moduln; das rechnet das Werkzeug noch nicht, und die Analyse sagt es
grau ([[opencivil.projekt.aufbau.querschnittsanalyse#ohne_nachweise|ohne_nachweise]]).


## LAMELLEN

Brettschichtholz hat seine Lamellen parallel zu y, nach Vorgabe, nicht
nachgeschlagen: `k_h` gilt fuer die Biegung um y, mit der Hoehe in z. Um z
gilt es nicht (3.4.2.2), und `k_sys` (5.7.2.2) nimmt das Werkzeug nicht.

## Inhalt

### holzstoff

```python
def holzstoff(analyse: Querschnittsanalyse) -> Baustoff
```

Das Holz der Analyse -- es gibt nur eines (siehe Dateikopf).

### holzart

```python
def holzart(stoff: Baustoff) -> Holzart
```

Woraus das Holz ist -- Vollholz oder Brettschichtholz, nach seiner Sorte.

### stoffbezuege

```python
def stoffbezuege(stoff: Baustoff, *kennwerte: str) -> List[Eingabebezug]
```

Die Kennwerte als Eingaben -- ohne Angabe die der Nachweise, [[opencivil.nachweis.qa_holz_werte#Konstanten|KENNWERTE]].

### kennwert

```python
def kennwert(e: Eingaben, stoff: Baustoff, kurz: str) -> Wert
```

Ein Kennwert des Holzes, wie die Nachweise ihn lesen.

### beiwert

```python
def beiwert(p: Protokoll, werte: Zwischenwerte, eta_w: Wert, stossartig: bool) -> Wert
```

`η = η_w·η_t` eines Falls -- ohne stossartige Einwirkung ist `η_t`
eins, und `η` ist `η_w`.

### HolzwerteQA

```python
class HolzwerteQA(Prozedur)
```

Die Werte eines Holzquerschnitts, die seine Nachweise lesen -- siehe Dateikopf.

- `THEMA = 'Holzquerschnitt'`

#### HolzwerteQA.brettschicht

```python
@property
def brettschicht(self) -> bool
```

#### HolzwerteQA.als_eingaben

```python
def als_eingaben(self) -> List[Eingabebezug]
```

Alle Werte als Eingaben eines Nachweises, unter ihrem Kurznamen.

#### HolzwerteQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]
```


## Konstanten

- `KENNWERTE = ('f_m_d', 'f_t_0_d', 'f_c_0_d', 'f_v_d')` – Was die Nachweise je Holz lesen -- die Bemessungswerte der Tabellen 6 und 7.
- `KENNWERTE_STAB = ('f_m_k', 'f_c_0_k', 'E_0_05')` – Was der Stab dazu liest -- Anhang B und die Biegefestigkeit.
- `TORSION_NUR_RECHTECK = 'Torsion weist das Werkzeug beim Holz nur für ein Rechteck nach, die …` – Warum Torsion nur beim Rechteck nachgewiesen wird -- siehe [[opencivil.holzbau.querschnitt]].
- `ZUG = ('@eta \\cdot @f_t \\cdot @A', 'Zugwiderstand eines Holzquerschnitts')` – Die Widerstaende gegen Normalkraft, die Kennzahlen und Nachweise beide schreiben: je Vorlage ein Name in der Formelsammlung. `@eta` ist η_w oder, stossartig, η_w·η_t.
- `DRUCK = ('-@eta \\cdot @f_c \\cdot @A', 'Druckwiderstand eines Holzquerschnit…`
- `K_2 = '\\frac{1 - \\frac{192}{\\pi^5} \\cdot \\frac{@b}{@h} \\sum_{n = 1, 3…` – Die Reihen von Saint-Venant fuer k_2 = β/c, b die kurze Seite.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.holzbau.gleichungen]]
- [[opencivil.holzbau.querschnitt]]
- [[opencivil.material.basis]]
- [[opencivil.material.holz]]
- [[opencivil.nachweis.qa_stahl_werte]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.stabwerk.stabquerschnitt]]

## Gebraucht von

- [[opencivil.nachweis.qa_holz]]
- [[opencivil.nachweis.qa_holz_kennzahlen]]
- [[opencivil.nachweis.qa_holz_stabilitaet]]
- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Beiwert der Bemessungswerte des Holzes]] · `beiwert`
- [[Höhenbeiwert des Brettschichtholzes]] · `HolzwerteQA._biegung`
- [[Schubfläche nach Jourawski]] · `HolzwerteQA._schub`
- [[Schubspannung aus Querkraft nach Jourawski]] · `HolzwerteQA._schub`
- [[Torsionsbeiwert des Rechtecks]] · `HolzwerteQA._torsion`
- [[Torsionswiderstandsmoment des Rechtecks]] · `HolzwerteQA._torsion`
- [[Widerstandsmoment bis zur weitesten Faser]] · `HolzwerteQA._biegung`
