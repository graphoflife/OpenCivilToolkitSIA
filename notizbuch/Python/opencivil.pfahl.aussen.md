---
erzeugt: 1111b76e1804
art: modul
tags: [modul]
---
> [!abstract] opencivil/pfahl/aussen.py
> der äussere Widerstand eines Pfahls längs seiner Achse.
> Paket [[opencivil.pfahl]] · [Quelltext](../../opencivil/pfahl/aussen.py)

## VERANTWORTUNG

Der Nachweis [[opencivil.pfahl.aussen#AeussererWiderstand|AeussererWiderstand]]: je Kombination die Normalkraft am
Kopf gegen den Bemessungswert des äusseren Widerstands, auf Druck oder auf
Zug (SIA 267:2013, 9.5.2.2, 9.5.3.1):

```
R_a,k   = R_b,k + R_s,k         (41)   Druck: Fuss und Mantel
R_a,k,Z = R_s,k                        Zug: nur der Mantel
R_a,d   = η_a · R_a,k / γ_M,a   (42)   γ_M,a = 1.3 auf Druck (43), 1.6 auf Zug (44)
```

R_a,k kommt aus einem Versuch oder aus den Schichten ([[opencivil.pfahl.pfahl#Grundlage|Grundlage]]).


## DER MANTEL (Kap. 12.5)

Je Stück des Mantels ([[opencivil.pfahl.boden#Profil.stuecke|stuecke]]) die Mantelreibung
q_s,k -- drainiert K · σ'_v · tan δ mit δ = k_δ · φ'_k, undrainiert
α · s_u,k, oder eingegeben -- und R_s,k = U · Σ h · q_s,k.


## DER FUSS (Kap. 12.5)

Drainiert q_b,k = (c* · N_c + σ'_v · N_q) · X: N_q und N_c wie beim
Grundbruch (Kap. 9.2.6), beim örtlichen Abscheren mit φ* = 2/3 · φ'_k und
c* = 2/3 · c'_k, sonst mit φ'_k und c'_k; X aus Bild 12.4 nach φ'_k und
der Einbindung h in die Schicht am Fuss. Undrainiert q_b,k = s_u,k · N_c
mit N_c aus Bild 12.5 nach L/D. R_b,k = A_b · q_b,k.


## NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md)

* Die Faktoren des örtlichen Abscherens und dazu η_a und γ_M,a: das Buch
  rechnet mit einer globalen Sicherheit und führt nach dem Abmindern keine
  weitere ein. Hier gilt die Norm, und sie verlangt R_a,d.
* X mit φ'_k, nicht mit φ*.
* Undrainiert ohne die Überlagerung am Fuss: sie hebt sich etwa mit dem
  Gewicht des Pfahls auf, das auch nicht in der Einwirkung steht.
* Auf Zug dieselbe Mantelreibung wie auf Druck.


## EINHEITEN

SI-Basis.

## Inhalt

### Mantelstueck

```python
@dataclass(frozen=True)
class Mantelstueck
```

Was ein Stück des Mantels trägt -- Spannungen in Pa.

- `stueck: Stueck`
- `q_s: float`
- `sigma: Optional[float] = None` – σ'_v in seiner Mitte -- nur, wo die Mantelreibung daraus gerechnet ist.

### Aussenbefund

```python
@dataclass
class Aussenbefund
```

Was ausser den Erfüllungsgraden bleibt -- für Zusammenfassung und Bild, in SI.

- `aus_versuch: bool`
- `stuecke: List[Mantelstueck] = field(default_factory=list)`
- `R_s: float = 0.0`
- `q_b: Optional[float] = None` – Der Spitzendruck -- `None`, wo der Fuss nicht trägt.
- `R_b: float = 0.0`
- `R_ak: float = 0.0`
- `R_ak_zug: float = 0.0`
- `R_ad: float = 0.0`
- `R_ad_zug: float = 0.0`

### AeussererWiderstand

```python
class AeussererWiderstand(Achsnachweis)
```

Siehe Dateikopf.

- `THEMA = 'Äusserer Pfahlwiderstand'`
- `ART = 'R_a'`
- `INDEX = 'a'`
- `TITEL = 'Äusserer Widerstand'`
- `WORT = 'äusserer Widerstand'`

#### AeussererWiderstand.pruefe

```python
def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung
```

#### AeussererWiderstand._mantel

```python
def _mantel(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, profil: Profil, befund: Aussenbefund) -> Wert
```

Je Stück die Mantelreibung, als Tabelle -- und daraus R_s,k.

#### AeussererWiderstand._erddruck_pruefen

```python
def _erddruck_pruefen(self, e: Eingaben, p: Protokoll, stuecke: Sequence[Stueck]) -> None
```

K über K_0: das Buch sieht für Bohrpfähle höchstens etwa K_0 (Kap. 12.5).

#### AeussererWiderstand._bemessung

```python
def _bemessung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, R_ak: Wert, *, druck: bool) -> Wert
```

R_a,d = η_a · R_a,k / γ_M,a (42) -- auf Druck oder auf Zug.


## Konstanten

- `GAMMA_M = {True: (1.3, 'SIA 267:2013, 9.5.2.2.4, (43)'), False: (1.6, 'SIA 267:…` – Die Widerstandsbeiwerte des äusseren axialen Widerstands, auf Druck und auf Zug, mit ihrer Stelle (SIA 267:2013, 9.5.2.2.4).
- `ZUG_WIE_DRUCK = 'Auf Zug trägt nur der Mantel, mit derselben Mantelreibung wie auf Dr…` – Was beide Richtungen annehmen -- siehe Dateikopf.

## Braucht

- [[opencivil.core.berechnung]]
- [[opencivil.core.einheiten]]
- [[opencivil.core.latex]]
- [[opencivil.core.protokoll]]
- [[opencivil.core.wert]]
- [[opencivil.geotechnik.grundbruch]]
- [[opencivil.pfahl.achse]]
- [[opencivil.pfahl.boden]]
- [[opencivil.pfahl.buch]]
- [[opencivil.pfahl.pfahl]]

## Gebraucht von

- [[opencivil.pfahl.uebersicht]]
- [[opencivil.projekt.aufbau.pfahl]]
- [[opencivil.web.pfahldaten]]

## Formeln aus diesem Modul

- [[Äusserer Widerstand auf Druck]] · `AeussererWiderstand._aus_schichten`
- [[Äusserer Widerstand auf Zug]] · `AeussererWiderstand._aus_schichten`
- [[Bemessungswert des äusseren Widerstands]] · `AeussererWiderstand._bemessung`
- [[Einbindung in die tragende Schicht]] · `AeussererWiderstand._fuss_drainiert`
- [[Fläche des Pfahlquerschnitts]] · `AeussererWiderstand._fuss`
- [[Form- und Tiefenfaktor des Pfahlfusses]] · `AeussererWiderstand._fuss_drainiert`
- [[Kohäsion für örtliches Abscheren]] · `AeussererWiderstand._fuss_drainiert`
- [[Mantelreibung drainiert]] · `AeussererWiderstand._mantel`
- [[Mantelreibung undrainiert]] · `AeussererWiderstand._mantel`
- [[Mantelwiderstand]] · `AeussererWiderstand._mantel`
- [[Reibungswinkel für örtliches Abscheren]] · `AeussererWiderstand._fuss_drainiert`
- [[Spitzendruck drainiert]] · `AeussererWiderstand._fuss_drainiert`
- [[Spitzendruck undrainiert]] · `AeussererWiderstand._fuss_undrainiert`
- [[Spitzenwiderstand]] · `AeussererWiderstand._fuss`
- [[Tragfähigkeitsfaktor des Pfahlfusses undrainiert]] · `AeussererWiderstand._fuss_undrainiert`
- [[Umfang des Pfahls]] · `AeussererWiderstand._mantel`
- [[Wirksame Spannung am Pfahlfuss]] · `AeussererWiderstand._fuss_drainiert`
- [[Wirksame Überlagerungsspannung]] · `AeussererWiderstand._mantel`
