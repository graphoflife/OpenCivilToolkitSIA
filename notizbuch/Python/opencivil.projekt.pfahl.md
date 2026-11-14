---
erzeugt: df58d97b3220
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/pfahl.py
> ein Einzelpfahl, wie die Oberflaeche ihn beschreibt.
> Paket [[opencivil.projekt]] · [Quelltext](../../opencivil/projekt/pfahl.py)

## VERANTWORTUNG

Der [[opencivil.projekt.pfahl#PfahlEintrag|PfahlEintrag]]: Art und Masse des Pfahls, sein Querschnitt, die
Schichten des Baugrunds, das Grundwasser, worauf der äussere Widerstand
beruht, und die Normalkräfte am Kopf -- als speicherbare Datenklasse.
Gerechnet wird in [[opencivil.pfahl]].


## DIE VORGABEN

Gesetzt, damit sich gleich etwas rechnen lässt, aus keiner Quelle: ein
Bohrpfahl mit D = 900 mm und L = 10 m, der Kopf 1 m unter Terrain, das
Grundwasser am Terrain, auf der sicheren Seite wie beim Grundbruch; zwölf
Stäbe ⌀ 20 mit einer Wendel ⌀ 10 und 75 mm Überdeckung, dem grössten Wert
von SIA 267:2013, 9.6.3.2.6. Eine Schicht, 20 m Kies mit φ'_k = 30° und
K = 0.5, etwa K_0 = 1 − sin φ'_k (Kap. 2.7), und δ = φ'_k, wie das Buch
für raue Pfähle sagt (Kap. 12.5); undrainiert α = 0.6, sein Wert für
Bohrpfähle in weichem Ton. η_a = 0.7 und η_i = 0.8 sind die Grenzwerte der
Norm für eine Berechnung und ohne Prüfung der Integrität. Der Mikropfahl
hat ein Rohr 114.3 × 10 mm ohne Abrostung, bis jemand eine angibt.

Die Namen der Schichten müssen nicht verschieden sein, wie bei der Setzung:
die Werte tragen die Nummer der Schicht.

## Inhalt

### PfahlschichtEintrag

```python
@dataclass
class PfahlschichtEintrag(Beschreibung)
```

Eine Schicht des Baugrunds, vom Terrain an nach unten -- siehe [[opencivil.pfahl.boden#Pfahlschicht|Pfahlschicht]].

- `name: str`
- `d: float = bereich(20.0, heisst='Dicke d', einheit=M, ueber=0.0)`
- `gamma: float = bereich(20.0, heisst='Raumlast γ', einheit=KN_PRO_M3, ueber=0.0)`
- `verhalten: Verhalten = Verhalten.DRAINIERT`
- `phi_k: float = bereich(30.0, heisst="φ'_k", einheit=GRAD, ab=0.0, unter=90.0)`
- `c_k: float = bereich(0.0, heisst="c'_k", einheit=KPA, ab=0.0)`
- `s_u: float = bereich(50.0, heisst='s_u,k', einheit=KPA, ab=0.0)`
- `mantel: Mantel = Mantel.RECHNEN`
- `q_s: float = bereich(50.0, heisst='q_s,k', einheit=KPA, ab=0.0)`
- `K: float = bereich(0.5, heisst='K', ab=0.0)`
- `delta_faktor: float = bereich(1.0, heisst="δ/φ'_k", ab=0.0, bis=1.0)` – Höchstens eins: zwischen Pfahl und Boden reibt es nie stärker als im Boden -- nach Vorgabe, nicht nachgeschlagen.
- `alpha: float = bereich(0.6, heisst='α', ab=0.0, bis=1.0)` – Höchstens eins: die Adhäsion erreicht höchstens die Scherfestigkeit -- nach Vorgabe, nicht nachgeschlagen.

### PfahlkombinationEintrag

```python
@dataclass
class PfahlkombinationEintrag(Beschreibung)
```

Eine Einwirkung auf den Pfahlkopf: die Normalkraft in kN, Druck positiv.

- `name: str`
- `N_Ed: float = bereich(1000.0, heisst='Normalkraft N_Ed, Druck positiv', einheit=KN)`
- `aktiv: bool = True` – Ob die Kombination gerechnet wird. Ausgeschaltet bleibt sie stehen.

### PfahlEintrag

```python
@dataclass
class PfahlEintrag(BauteilEintrag)
```

Ein Einzelpfahl in seinem Baugrund, mit seinen Einwirkungen -- siehe Dateikopf.

- `BEZEICHNUNG = 'Pfahl'`
- `kennung: str`
- `name: str`
- `art: Pfahlart = Pfahlart.BOHRPFAHL`
- `beton: str = ''` – Kennung des Betons -- nur beim Bohrpfahl.
- `stahl: str = ''` – Kennung des Stahls: die Längsbewehrung des Bohrpfahls, das Tragglied des Mikropfahls.
- `D: float = bereich(900.0, heisst='Durchmesser D', einheit=MM, ueber=0.0)`
- `L: float = bereich(10.0, heisst='Länge L', einheit=M, ueber=0.0)`
- `t_K: float = bereich(1.0, heisst='Tiefe des Kopfs t_K', einheit=M, ab=0.0)`
- `t_w: float = bereich(0.0, heisst='Tiefe des Grundwassers t_w', einheit=M, ab=0.0)`
- `gamma_w: float = bereich(10.0, heisst='γ_w', einheit=KN_PRO_M3, ab=0.0)`
- `grundlage: Grundlage = Grundlage.BERECHNUNG`
- `eta_a: float = bereich(0.7, heisst='η_a', ueber=0.0, bis=1.0)` – Höchstens der Grenzwert der Grundlage -- das prüft [[opencivil.projekt.pfahl#PfahlEintrag.regeln|regeln]].
- `R_ak: float = bereich(1000.0, heisst='R_a,k auf Druck', einheit=KN, ab=0.0)`
- `R_ak_zug: float = bereich(500.0, heisst='R_a,k auf Zug', einheit=KN, ab=0.0)`
- `spitze: Spitze = Spitze.RECHNEN`
- `abscheren: Abscheren = Abscheren.OERTLICH`
- `q_b: float = bereich(2000.0, heisst='q_b,k', einheit=KPA, ab=0.0)`
- `eta_i: float = bereich(0.8, heisst='η_i', ueber=0.0, bis=ETA_I_HOECHSTENS)`
- `n: int = bereich(12, heisst='Zahl der Stäbe n', ab=1)`
- `phi_l: float = bereich(20.0, heisst='⌀ der Stäbe', einheit=MM, ueber=0.0)`
- `c: float = bereich(75.0, heisst='Überdeckung c', einheit=MM, ab=0.0)`
- `phi_w: float = bereich(10.0, heisst='⌀ der Wendel', einheit=MM, ab=0.0)`
- `tragglied: Tragglied = Tragglied.ROHR`
- `d_a: float = bereich(114.3, heisst='Aussendurchmesser d_a', einheit=MM, ueber=0.0)`
- `t_r: float = bereich(10.0, heisst='Wanddicke t', einheit=MM, ueber=0.0)`
- `dt: float = bereich(0.0, heisst='Abrostung Δt', einheit=MM, ab=0.0)`
- `beschreibung: str = ''` – Freier Text -- geht in keine Rechnung ein.
- `schichten: List[PfahlschichtEintrag] = field(default_factory=list)` – Vom Terrain an nach unten.
- `kombinationen: List[PfahlkombinationEintrag] = field(default_factory=list)`

#### PfahlEintrag.neu

```python
@classmethod
def neu(cls, kennung: str, name: str) -> 'PfahlEintrag'
```

Ein frischer Pfahl, wie die Oberflaeche ihn anlegt: mit einer Schicht und einer Kombination.

#### PfahlEintrag.materialien

```python
def materialien(self) -> List[str]
```

Die Materialien, die der Pfahl braucht: der Beton nur beim Bohrpfahl.

#### PfahlEintrag.bohrpfahl

```python
@property
def bohrpfahl(self) -> bool
```

#### PfahlEintrag.schicht

```python
def schicht(self, name: str, **felder: Any) -> PfahlschichtEintrag
```

Eine Schicht unten anfügen -- Dicke in m, Raumlast in kN/m³, Winkel in
Grad, Spannungen in kPa; `verhalten` und `mantel` als Wort, wie in
der Datei: `verhalten="undrainiert"`.

#### PfahlEintrag.kombination

```python
def kombination(self, name: str, *, N_Ed: float) -> PfahlkombinationEintrag
```

Eine Kombination anfügen -- N_Ed in kN, Druck positiv.

#### PfahlEintrag.regeln

```python
def regeln(self, wo: str) -> None
```

Hält auf, was mehrere Felder zusammen unmöglich machen, bevor daraus
ein Widerstand wird. Wie beim Grundbruch vor dem Rechnen und nicht
beim Öffnen: eine Datei mit einem zu kurzen Baugrund soll sich öffnen
und korrigieren lassen.

#### PfahlEintrag._baugrund

```python
def _baugrund(self, wo: str) -> None
```

Was die Rechnung aus den Schichten braucht.

#### PfahlEintrag._bewehrung

```python
def _bewehrung(self, wo: str) -> None
```

Die Längsstäbe müssen im Kreis Platz haben, ohne sich zu berühren.

#### PfahlEintrag._tragglied

```python
def _tragglied(self, wo: str) -> None
```

Das Tragglied muss nach der Abrostung noch Stahl haben und im Verpresskörper liegen.


## Braucht

- [[opencivil.core.einheiten]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.pfahl]]
- [[opencivil.projekt.eintraege]]
- [[opencivil.projekt.lesen]]

## Gebraucht von

- [[opencivil.projekt]]
- [[opencivil.projekt.aufbau]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.projekt.projekt]]
