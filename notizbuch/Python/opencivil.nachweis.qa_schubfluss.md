---
erzeugt: 1d76f80fc769
art: modul
tags: [modul]
---
> [!abstract] opencivil/nachweis/qa_schubfluss.py
> der Schubfluss in den Schnitten eines Querschnitts.
> Paket [[opencivil.nachweis]] · [Quelltext](../../opencivil/nachweis/qa_schubfluss.py)

## VERANTWORTUNG

Je Schnitt ([[opencivil.querschnitt.abtrennen#Schnitt|Schnitt]]) und je
Lastfall des Schubflusses der Schubfluss `v` – die Kraft je Laenge des
Bauteils, die durch den Schnitt geht – und die Schubspannung `τ = v/b_i`
ueber die Laenge `b_i`, auf der er Material von Material trennt
([[opencivil.nachweis.qa_schubfluss#SchubflussQA|SchubflussQA]]). Nur die Einwirkung, ohne Widerstand (Benutzer,
2026-11-27): ob eine Fuge, die Duebel oder eine Naht das tragen, ist eine
andere Frage.


## DIE REGEL

Waechst das Moment laengs des Bauteils um `ΔM = V·Δx`, waechst die Kraft
`F′` im abgetrennten Teil um `ΔF′` – und die kommt durch den Schnitt:

```
v = ΔF′ / Δx
```

`F′` ist das Integral der Spannungen ueber den abgetrennten Teil, mit
den Staeben, Spanngliedern und Stuecken verschmierter Linien, die in ihm
liegen ([[opencivil.nachweis.qa_schubfluss#teilquerschnitt|teilquerschnitt]]). Die Spannungen kommen aus zwei
Dehnungsebenen des ganzen Querschnitts, bei `(N, M)` und bei
`(N, M + ΔM)` ([[opencivil.nachweis.qa_schubfluss#zustaende|zustaende]]): gesucht vom selben Faserloeser wie in
den Spannung-Dehnung-Analysen, im gerissenen Zustand – der Beton traegt
keinen Zug –, mit der Rechenwahl des Falls und der Nulllinie waagrecht.

Elastisch ist das `V·S′/I`. Gerissen, ohne Normalkraft und mit festem
Hebelarm `z` ist es `V/z` mal dem Anteil des abgetrennten Teils an der
Kraft seines Gurts – das `β·V/z` der EN 1992-1-1, 6.2.5 (nicht
nachgeschlagen). Diese Regel gilt auch mit Normalkraft und wo der
Hebelarm mit dem Moment wandert.


## NACH VORGABE, NICHT NACHGESCHLAGEN (`notizbuch/Notizen/TODO.md`)


* `Δx = 10 mm` ([[opencivil.nachweis.qa_schubfluss#Konstanten|DX]]): klein genug, dass sich der Zustand kaum
  aendert, gross genug fuer die Genauigkeit der Suche.
* Die Richtung: `ΔM` hat das Vorzeichen von `M` – das Moment waechst im
  Betrag –, ohne Moment das positive. Gibt es bei `M + ΔM` keine
  Gleichgewichtslage mehr, gilt der Schritt zurueck, `M − ΔM`.
* Angegeben wird der Betrag von `v`: in welche Richtung er laengs geht,
  haengt daran, in welche Richtung das Moment waechst.


## OHNE ERGEBNIS

Ohne Querkraft aendert sich das Moment nicht: `v = 0`. Nimmt der
Querschnitt `N` und `M` nicht auf, gibt es kein `v`: die Zahl ist
nicht bestimmt (NaN), die Tabelle zeigt «–», die Herleitung und der Befund
([[opencivil.nachweis.qa_schubfluss#Schubflussbefund|Schubflussbefund]]) sagen warum. Ein Schnitt, der nichts abtrennt,
rechnet nicht; warum, steht in der Herleitung, unter der Tabelle und an ihm
in der Zeichnung.


## EINHEITEN

SI-Basis; die Schnitte und ihre abgetrennten Teile in mm, wie gezeichnet.

## Inhalt

### Schubflussfall

```python
@dataclass(frozen=True)
class Schubflussfall
```

Ein Lastfall des Schubflusses in SI, mit seiner Rechenwahl am Bauteil.

- `name: str`
- `N: float`
- `V: float` – Die Querkraft in z.
- `M: float` – Das Moment um y, positiv zieht es unten.
- `wahl: Rechenwahl`

### Schubflusszeile

```python
@dataclass(frozen=True)
class Schubflusszeile
```

Eine Zeile der Tabelle: ein Schnitt in einem Fall, mit den Definitionen
seiner Werte – `b_i` gehoert dem Schnitt, `v` und `τ` dem Paar.

- `schnitt: str`
- `fall: str`
- `b_i: WertDef`
- `v: WertDef`
- `tau: WertDef`

### Schubflussbefund

```python
@dataclass(frozen=True)
class Schubflussbefund
```

Was ein Lauf ueber die Werte hinaus festhaelt: je Fall ohne Schubfluss
der Grund, ein Satz – die Tabelle zeigt dort «–», darunter steht er.

- `gruende: Dict[str, str]` – Nach dem Namen des Falls.

### Zustaende

```python
@dataclass(frozen=True)
class Zustaende
```

Die beiden Ebenen eines Falls: bei `M_0 = M` und beim Moment daneben, `M_1`.

- `M_0: float`
- `M_1: float`
- `ebene_0: Dehnungsebene`
- `ebene_1: Dehnungsebene`
- `zurueck: bool` – Ob `M_1` der Schritt zurueck ist, `M − ΔM`: bei `M + ΔM` gab es keine Ebene.

### zustaende

```python
def zustaende(ebenen: FesteNulllinie, fall: Schubflussfall) -> Union[Zustaende, str]
```

Die beiden Ebenen eines Falls (siehe Dateikopf) – oder ein Satz, warum
es sie nicht gibt.

### teilquerschnitt

```python
def teilquerschnitt(q: Querschnitt, herkunft: Sequence[Bewehrungselement], a: Abgetrennt) -> Tuple[Querschnitt, List[str]]
```

Der abgetrennte Teil als Querschnitt, mit den Werkstoffen, dem Bezug und
den Streifen des ganzen, geteilt an seinen eigenen Ecken – so liest er
dieselbe Ebene, und zwei Schnitte, die dieselbe Druckzone abtrennen,
rechnen sie gleich. Dazu die Namen
der Bewehrung in ihm. Ein Stab und ein Spannglied zaehlen mit ihrer
Mitte, auf dem Schnitt zum Rest; eine verschmierte Linie mit ihren
Stuecken im abgetrennten Teil, je mit der Flaeche ihrer Laenge.

### kraft_im_teil

```python
def kraft_im_teil(teil: Querschnitt, ebene: Dehnungsebene) -> float
```

`F′`: was der abgetrennte Teil in dieser Ebene traegt, Zug positiv, in N.

### SchubflussQA

```python
class SchubflussQA(Prozedur)
```

Der Schubfluss je Schnitt und Lastfall – siehe Dateikopf.

- `THEMA = 'Schubfluss'`

#### SchubflussQA.rechne

```python
def rechne(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### SchubflussQA._fall

```python
def _fall(self, p: Protokoll, werte: Zwischenwerte, belegen, fall: Schubflussfall, dx: Wert, breiten: Dict[str, Wert], ebenen: FesteNulllinie, teile: Sequence[Tuple[Querschnitt, List[str]]]) -> Optional[str]
```

Ein Fall in jedem Schnitt – ohne Schubfluss der Grund, sonst nichts.


## Konstanten

- `DX = 0.01` – Wie weit der zweite Zustand laengs des Bauteils vom ersten liegt, in m – nach Vorgabe, nicht nachgeschlagen (siehe Dateikopf).
- `PSI = Zugseite.UNTEN.psi` – Die Nulllinie waagrecht, positives Moment zieht unten: so ist das Moment der Fasern `M_y`.
- `_MM = MM.faktor` – Was in mm steht, in m.
- `VORGABE = 'nach Vorgabe, nicht nachgeschlagen'` – Woher die Regel kommt: keine Norm nennt sie (siehe Dateikopf).
- `KEINE_LAGE = 'Zu N und M gibt es keine Gleichgewichtslage: der Querschnitt nimmt s…` – Warum es zu einem Fall kein `v` gibt, wo der Querschnitt ihn nicht aufnimmt.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.querschnitt.abtrennen]]
- [[opencivil.querschnitt.analyse]]
- [[opencivil.querschnitt.bewehrungselemente]]
- [[opencivil.querschnitt.gesetzwahl]]
- [[opencivil.querschnitt.interaktion]]
- [[opencivil.querschnitt.zugseite]]
- [[opencivil.spannungsanalyse.linie]]
- [[opencivil.spannungsanalyse.schnitt]]

## Gebraucht von

- [[opencivil.projekt.aufbau.querschnittsanalyse]]

## Formeln aus diesem Modul

- [[Schubfluss im Schnitt]] · `SchubflussQA._fall`
- [[Schubfluss im Schnitt]] · `SchubflussQA.rechne`
- [[Schubspannung im Schnitt]] · `SchubflussQA._fall`
- [[Zuwachs des Moments über Δx]] · `SchubflussQA._fall`
