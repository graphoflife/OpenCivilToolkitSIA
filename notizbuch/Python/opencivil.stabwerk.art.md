---
erzeugt: 4dd61d4c038a
art: modul
tags: [modul]
---
> [!abstract] opencivil/stabwerk/art.py
> eben oder im Raum: was die beiden Balkensysteme unterscheidet.
> Paket [[opencivil.stabwerk]] · [Quelltext](../../opencivil/stabwerk/art.py)

## VERANTWORTUNG

Der Rechenkern ([[opencivil.stabwerk.system|system]]) rechnet jedes System im
Raum. Was ein ebenes von einem raeumlichen unterscheidet, steht hier, je
einmal in einer [[opencivil.stabwerk.art#Art|Art]] ([[opencivil.stabwerk.art#Konstanten|EBENE]], [[opencivil.stabwerk.art#Konstanten|RAUM]]) – und wie aus
einem ebenen System eines im Raum wird.


## DIE EBENE

Ein ebenes System liegt in der x-z-Ebene und bleibt darin. Ein Ort
verschiebt sich nur in x und z und dreht sich nur um `-y`, im
Gegenuhrzeigersinn; ein Stab biegt sich nur in dieser Ebene und traegt
keine Torsion. Seine Achse y ist `-y` des Systems, z zeigt zur
gestrichelten Faser ([[opencivil.stabwerk3d.stab#achsen_eben|achsen_eben]]):
`N`, `V_z` und `M_y` sind damit `N`, `V` und `M` von Hand.


## AUS DER EBENE IN DEN RAUM

Ein Knoten `(x, z)` liegt bei `(x, 0, z)`; `EI` wird `EI_y`,
`EI_z` und `GI_T` bleiben null, und ein Linienlager quer haelt in z des
Stabs. Ein Lager haelt die Drehung um y. Eine Kraft bleibt, wohin sie
zeigt – quer heisst quer in z des Stabs –, ein Moment im
Gegenuhrzeigersinn dreht um `-y`.

## Inhalt

### Art

```python
@dataclass(frozen=True)
class Art
```

Was ein ebenes System von einem im Raum unterscheidet – siehe Dateikopf.

- `verschiebungen: Tuple[Tuple[str, Vektor], ...]` – Die Achsen des Systems, entlang derer sich ein Ort verschieben kann, mit Namen – in der Folge der Ergebnisse.
- `drehungen: Tuple[Tuple[str, Vektor], ...]` – Die Achsen, um die er sich drehen kann – in der Ebene eine ohne Namen, `-y`.
- `raeumlich: bool` – Ob ein Stab sich auch in seiner x-y-Ebene biegt und Torsion traegt.
- `steifigkeiten: Tuple[str, ...]` – Die Steifigkeiten, die ein tragender Stab braucht – Felder seines Modells.
- `ohne_steifigkeit: str` – Was die Meldung sagt, wenn eine davon nicht groesser als null ist.
- `gelenk: str` – Wie die Drehung eines Stabendes am Gelenk heisst – mit `{stab}`, `{ende}` und `{achse}`.
- `achsen: Callable[[Any, Any, float], Tuple[float, Tuple[Vektor, Vektor, Vektor]]]` – Laenge und Achsen eines Stabs von `a` nach `b` mit seinem Drehwinkel.
- `im_raum: Callable[[Any], System]` – Ein System dieser Art als eines im Raum.

#### Art.werte

```python
def werte(self, kraft: Sequence[float], moment: Sequence[float]) -> Werte
```

Eine Verschiebung und eine Drehung – oder Kraft und Moment – in den Achsen der Art.

### _im_raum

```python
def _im_raum(system: eben.System) -> System
```

Ein ebenes System als eines im Raum, in der x-z-Ebene – siehe
Dateikopf. Was die Ebene nicht kennt, bleibt null; die [[opencivil.stabwerk.art#Konstanten|EBENE]]
rechnet es nicht.

### _last_im_raum

```python
def _last_im_raum(last: eben.Last) -> Any
```

Eine Last der Ebene im Raum. Ein Moment im Gegenuhrzeigersinn dreht um
`-y` des Systems – an einem Stab um sein `y`, das in der Ebene
`-y` ist ([[opencivil.stabwerk3d.stab#achsen_eben|achsen_eben]]).


## Konstanten

- `Werte = Tuple[float, ...]` – Was der Kern je Ort oder Lager abgibt: Verschiebungen, dann Drehungen – oder Kraefte, dann Momente.
- `_RICHTUNG_IM_RAUM = {eben.Lastrichtung.SENKRECHT: Richtung.SENKRECHT, eben.Lastrichtung.W…` – Je Richtung einer Kraft in der Ebene die im Raum: quer heisst dort quer in z des Stabs.
- `RAUM = Art(verschiebungen=tuple(zip('xyz', ACHSEN)), drehungen=tuple(zip('xy…` – Ein System im Raum.
- `EBENE = Art(verschiebungen=(('x', ACHSEN[0]), ('z', ACHSEN[2])), drehungen=((…` – Ein System in der x-z-Ebene – Drehungen im Gegenuhrzeigersinn, um `-y`.

## Braucht

- [[opencivil.stabwerk.modell]]
- [[opencivil.stabwerk3d.modell]]
- [[opencivil.stabwerk3d.raum]]
- [[opencivil.stabwerk3d.stab]]

## Gebraucht von

- [[opencivil.stabwerk.rechnung]]
- [[opencivil.stabwerk.system]]
- [[opencivil.stabwerk3d.rechnung]]
- [[opencivil.web.balkendaten]]
