"""
opencivil/querschnitt/vorlagen.py -- Querschnitte zum Anfangen.

VERANTWORTUNG:
Sieben Vorlagen -- Rechteck, T-Balken, Doppel-T, Trapez, Hohlkasten, Platte
mit Aufbeton und Kreis. Jede kennt ihre Masse samt Vorgabe und ihre Lagen
von Laengsstaeben und baut daraus :class:`Teile` in mm, den Ursprung unten
links: die Polygone, auf Wunsch die Bewehrung und die Schubwaende, und fuer
die Skizze im Zeichenfenster die Masslinien, die Staebe der Linien und je
Lage, was aus ihr wird.

Die Vorlagen stehen nur hier. Die Oberflaeche fragt nach ihnen: ``vorlage``
fuer die Skizze, waehrend man tippt, ``vorlage_einsetzen`` zum Einsetzen.
Vorher stand das Rechteck zweimal da, in Python und in JS.

Was eine Vorlage nicht sagt, kommt aus den Vorgaben der Eintraege -- der
Stahl, die Schnitte einer Schubwand. Eine Vorlage ist ein Anfang, kein
Entwurf.

DIE BEWEHRUNG (Benutzer, 2026-11-27):
Je Lage ein Durchmesser und eine Teilung, beim Kreis Durchmesser und Anzahl.
Die Teilung ist ein Wunsch wie beim Zeichnen einer Stablinie: die Lage wird
eine Stablinie mit Teilung, gerundet auf den naechsten Abstand, der aufgeht
(:func:`~opencivil.querschnitt.geometrie.stablinie`). Die Ueberdeckung c_nom
misst bis zum aeussersten Stab, mit Schubwaenden also bis zum Buegel: die
Achse eines Stabs liegt c_nom + ⌀_b + ⌀/2 vom Rand, ohne Waende c_nom + ⌀/2.
Bei b = 300, c_nom = 35, Buegeln ⌀10 und unten ⌀20 mit s = 100 sind das
55 mm; dazwischen bleiben 190 mm, zwei Felder zu 95 mm, drei Staebe. Bis
2026-11-27 lag jede Achse 50 mm vom Rand («Achsabstand»), mit festen
Staeben: drei ⌀20 unten, zwei ⌀12 oben. So beginnt noch das Rechteck der
Skripte (:func:`rechteck_der_skripte`): auf ihm bauen Skripte und Tests auf.

Die Schubwaende enden auf der Hoehe der Stabachsen -- ohne Bewehrung dort,
wo sie laege. Ihre Buegel haben Durchmesser und Teilung (:data:`BUEGEL`).

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
Im Trapez ist die Schubwand so dick wie die engste Stelle zwischen den
Lagen -- die kleinere Breite gibt den kleineren Widerstand der Druckstrebe.

DAS MASS:
Ein :class:`Mass` steht fuer die Vorlagen hier und die der Stabquerschnitte
(:mod:`opencivil.stabwerk.querschnitte`). Seine Grenze ist ein
:class:`~opencivil.core.bereich.Bereich` wie die eines Feldes: derselbe
Satz, dieselbe Angabe fuer die Maske. Bis 2026-11-20 hatte jede Seite ihre
eigene Klasse, ihren eigenen Satz und im Fenster ihren eigenen Mindestwert --
1 hier, 0 beim Stab.

DIE UMRISSE:
Rechteck, T und Kreis zeichnet auch das Balkensystem fuer seine
Stabquerschnitte (:mod:`opencivil.stabwerk.querschnitte`). Ihre Umrisse und
was an einem T nicht geht, stehen darum hier, einmal fuer beide
(:func:`rechteckpunkte`, :func:`t_punkte`, :func:`t_pruefen`,
:func:`kreispunkte`). Bis 2026-10-25 standen sie in beiden Katalogen, und
ein Steg so breit wie der Flansch galt im einen als T, im anderen nicht.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.core.bereich import Bereich
from opencivil.core.einheiten import EINHEITSLOS, MM, Einheit
from opencivil.querschnitt.geometrie import (
    TOLERANZ, Linienart, stab_liegt_in, stablinie,
)

Punkt = Tuple[float, float]

#: Ecken eines Kreises. Sie liegen auf dem Kreis; was das an Flaeche kostet,
#: rechnet die Geometrie wie bei jedem anderen Polygon.
KREISECKEN = 48


@dataclass(frozen=True)
class Mass:
    """
    Ein Mass einer Vorlage: eine Laenge in mm, wo ``einheit`` nichts anderes
    sagt -- oder, ``ganzzahlig``, eine Anzahl, wie die der Staebe im Kreis.
    Jedes ist groesser als null; was die Masse untereinander verlangen,
    prueft die Vorlage.
    """

    schluessel: str
    symbol: str
    """Wie es in der Skizze heisst -- leer, wo es dort nicht steht."""

    beschriftung: str
    vorgabe: float
    einheit: Einheit = MM
    ganzzahlig: bool = False
    pfeil: float = 0.0
    """Um wie viel ein Pfeil am Feld den Wert aendert -- 0: um 1 bei einer Anzahl, sonst um 10."""

    @property
    def heisst(self) -> str:
        """Wie es an der Maske und in einer Meldung heisst: «Breite b»."""
        return " ".join(filter(None, (self.beschriftung, self.symbol)))

    @property
    def bereich(self) -> Bereich:
        return Bereich(self.heisst, self.einheit, ueber=0.0)

    @property
    def schritt(self) -> float:
        """Um wie viel ein Pfeil am Feld den Wert aendert -- siehe :attr:`pfeil`."""
        return self.pfeil or (1.0 if self.ganzzahlig else 10.0)

    def grund(self, wert: float) -> str:
        """Was an ``wert`` nicht geht, als Satz mit Punkt -- leer, wenn er geht."""
        if not math.isfinite(wert):
            return f"{self.heisst} muss eine Zahl sein, nicht {wert:g}."
        if self.ganzzahlig and not float(wert).is_integer():
            return (f"{self.heisst} muss eine ganze Zahl sein, "
                    f"angegeben ist {self.bereich.zahl(wert)}.")
        return self.bereich.grund(wert)

    def als_dict(self) -> Dict[str, Any]:
        """
        Fuer den Katalog: wie es heisst, seine Vorgabe, der Schritt der
        Pfeile und, was die Maske wie bei einem Feld braucht (``angabe``:
        Einheit, Grenze, Satz, bei einer Anzahl ``ganz``).
        """
        angabe = self.bereich.angabe()
        if self.ganzzahlig:
            angabe["ganz"] = True
        return {"schluessel": self.schluessel, "symbol": self.symbol,
                "beschriftung": self.beschriftung, "heisst": self.heisst,
                "vorgabe": self.vorgabe, "schritt": self.schritt, "angabe": angabe}


@dataclass(frozen=True)
class Lage:
    """
    Eine Lage Laengsstaebe einer Vorlage -- oder ihre Buegel: ein
    Durchmesser und eine Teilung, beim Kreis die Anzahl. ``name`` steht vor
    ihrer Zeile im Fenster und in den Saetzen, die sie betreffen.
    """

    schluessel: str
    name: str
    durchmesser: Mass
    menge: Mass

    @property
    def masse(self) -> Tuple[Mass, Mass]:
        return (self.durchmesser, self.menge)

    def als_dict(self) -> Dict[str, Any]:
        """Fuer den Katalog: Name, die zwei Masse und wie sie in der Zeile heissen -- ⌀ und s oder n."""
        return {"schluessel": self.schluessel, "name": self.name,
                "masse": [m.als_dict() for m in self.masse],
                "kurz": ["⌀", "n" if self.menge.ganzzahlig else "s"]}


def lage(schluessel: str, name: str, durchmesser: float, teilung: float) -> Lage:
    """Eine Lage mit Teilung; ihre Masse heissen nach dem ersten Buchstaben, ⌀_u und s_u."""
    z = schluessel[0]
    return Lage(schluessel, name, Mass(f"d_{z}", f"⌀_{z}", f"Durchmesser {name}", durchmesser),
                Mass(f"s_{z}", f"s_{z}", f"Teilung {name}", teilung))


#: Die Ueberdeckung: vom Rand bis zum aeussersten Stab, mit Schubwaenden bis
#: zum Buegel -- ein Mass jeder Vorlage hier. Vorgabe 35 mm wie bei einer
#: neuen Platte; bis 2026-11-27 stand hier der Achsabstand, 50 mm.
UEBERDECKUNG = Mass("c_nom", "c_nom", "Überdeckung", 35.0)

#: Die Buegel der Schubwaende, Vorgabe wie bei einer neuen Wand
#: (:class:`~opencivil.projekt.querschnittsanalyse.SchubwandEintrag`).
BUEGEL = Lage("buegel", "Bügel", Mass("d_b", "⌀_b", "Bügeldurchmesser", 10.0),
              Mass("s_b", "s_b", "Bügelteilung", 150.0))


@dataclass
class Teile:
    """Was eine Vorlage baut -- in mm, der Ursprung unten links."""

    polygone: List[dict] = field(default_factory=list)
    """Je Polygon ``punkte``, ``aussparung`` und ``stoff``: leer fuer das Material der Vorlage."""

    staebe: List[dict] = field(default_factory=list)
    """Je Stab ``lage`` und ``durchmesser``."""

    stablinien: List[dict] = field(default_factory=list)
    """Je Linie ``von``, ``bis`` und die Felder, die von der Vorgabe abweichen."""

    schubwaende: List[dict] = field(default_factory=list)
    """Je Wand ``von``, ``bis``, ``dicke``, Durchmesser und Teilung ihrer Buegel."""

    bleche: List[dict] = field(default_factory=list)
    """Je Profilblech ``punkte``, seine Linie -- nur in der Skizze einer Blechverbunddecke."""

    masslinien: List[dict] = field(default_factory=list)
    """Nur fuer die Skizze: ``von``, ``bis``, ``text`` und ``seite``
    ('unten', 'oben', 'links', 'rechts') -- wohin sie neben dem Bauteil steht."""

    stabmitten: List[dict] = field(default_factory=list)
    """Nur fuer die Skizze: die Staebe der Linien, je ``lage`` und ``durchmesser``."""

    lagen: Dict[str, str] = field(default_factory=dict)
    """Nur fuer das Fenster: je Lage, was aus ihr wird -- «3 Stäbe, Abstand 95 mm»."""

    def als_dict(self) -> dict:
        return asdict(self)


def masslinie(von: Punkt, bis: Punkt, name: str, wert: float, seite: str) -> dict:
    """Eine Masslinie der Skizze, «b = 300», auf der ``seite`` neben dem Bauteil -- auch fuer ein Stahlprofil."""
    return {"von": von, "bis": bis, "text": f"{name} = {wert:g}", "seite": seite}


def umriss(punkte: Sequence[Punkt], stoff: str = "") -> dict:
    """Ein tragendes Polygon einer Vorlage -- aus ihrem Material oder dem ``stoff``, den sie zur Wahl stellt."""
    return {"punkte": list(punkte), "aussparung": False, "stoff": stoff}


def loch(punkte: Sequence[Punkt]) -> dict:
    """Eine Aussparung einer Vorlage."""
    return {"punkte": list(punkte), "aussparung": True, "stoff": ""}


def kreispunkte(mitte: Punkt, radius: float, ecken: int = KREISECKEN) -> List[Punkt]:
    """
    ``ecken`` Punkte, gleich verteilt auf einem Kreis, der erste rechts, auf
    Tausendstel gerundet: die Ecken eines Kreises als Vieleck -- oder die
    Staebe darin.
    """
    return [(round(mitte[0] + radius * math.cos(2 * math.pi * k / ecken), 3),
             round(mitte[1] + radius * math.sin(2 * math.pi * k / ecken), 3))
            for k in range(ecken)]


def rechteckpunkte(b: float, h: float, y: float = 0.0, z: float = 0.0) -> List[Punkt]:
    """Ein Rechteck ``b`` breit und ``h`` hoch, die Ecke unten links in ``(y, z)``."""
    return [(y, z), (y + b, z), (y + b, z + h), (y, z + h)]


def t_punkte(b: float, h: float, b_w: float, h_f: float) -> List[Punkt]:
    """Ein T, der Flansch oben und mittig ueber dem Steg -- der Ursprung unten links."""
    y0 = (b - b_w) / 2
    return [(y0, 0.0), (y0 + b_w, 0.0), (y0 + b_w, h - h_f), (b, h - h_f), (b, h),
            (0.0, h), (0.0, h - h_f), (y0, h - h_f)]


def t_pruefen(b: float, h: float, b_w: float, h_f: float) -> Optional[str]:
    """
    Was an einem T nicht geht -- ``None``, wenn alles geht. Ein Steg so breit
    wie der Flansch gaebe ein Rechteck mit doppelten Ecken: dafuer gibt es das
    Rechteck.
    """
    if b_w >= b:
        return "Der Steg b_w muss schmaler sein als der Flansch b."
    if h_f >= h:
        return "Der Flansch h_f muss dünner sein als die Höhe h."
    return None


# ===========================================================================
# Wo die Staebe einer Lage liegen
# ===========================================================================


def _stabzahl(punkte: Sequence[Punkt], abstand: float) -> str:
    """Was aus einer Lage wird, in Worten: «3 Stäbe, Abstand 95 mm»."""
    if len(punkte) == 1:
        return "1 Stab"
    return f"{len(punkte)} Stäbe, Abstand {abstand:.0f} mm"


@dataclass(frozen=True)
class Linie:
    """
    Die Achse einer Lage, von links nach rechts: die Staebe nach Teilung wie
    auf einer gezeichneten Stablinie, die Enden besetzt.
    """

    von: Punkt
    bis: Punkt

    @property
    def hat_platz(self) -> bool:
        return self.bis[0] - self.von[0] > TOLERANZ

    def staebe(self, teilung: float) -> Tuple[Tuple[Punkt, ...], float]:
        """Die Stabmitten und ihr Abstand -- die Teilung gerundet, bis sie aufgeht."""
        linie = stablinie(self.von, self.bis, Linienart.TEILUNG, teilung)
        return linie.punkte, linie.teilung

    def einsetzen(self, teile: Teile, durchmesser: float, teilung: float,
                  punkte: Sequence[Punkt]) -> None:
        teile.stablinien.append({"von": self.von, "bis": self.bis, "art": Linienart.TEILUNG.value,
                                 "teilung": teilung, "durchmesser": durchmesser})
        teile.stabmitten.extend({"lage": p, "durchmesser": durchmesser} for p in punkte)


@dataclass(frozen=True)
class Ring:
    """Die Achsen der Staebe eines Kreises: gleich verteilt, der erste rechts."""

    mitte: Punkt
    radius: float

    @property
    def hat_platz(self) -> bool:
        return self.radius > TOLERANZ

    def staebe(self, anzahl: float) -> Tuple[Tuple[Punkt, ...], float]:
        """Die Stabmitten und ihr Abstand, die Sehne zwischen zwei Nachbarn."""
        n = int(anzahl)
        return tuple(kreispunkte(self.mitte, self.radius, n)), 2 * self.radius * math.sin(math.pi / n)

    def einsetzen(self, teile: Teile, durchmesser: float, anzahl: float,
                  punkte: Sequence[Punkt]) -> None:
        teile.staebe.extend({"lage": p, "durchmesser": durchmesser} for p in punkte)


@dataclass
class Form:
    """
    Was eine Form aus ihren Massen zeichnet: ihre Polygone, je Lage, wo ihre
    Staebe liegen, ihre Schubwaende ohne Buegel und die Masslinien.
    """

    polygone: List[dict]
    reihen: Dict[str, Union[Linie, Ring]]
    schubwaende: List[dict] = field(default_factory=list)
    masslinien: List[dict] = field(default_factory=list)


#: Wie weit die Achsen einer Lage vom Rand liegen, nach ihrem Schluessel.
Abstand = Callable[[str], float]


@dataclass(frozen=True)
class Stoff:
    """Ein zweites Material, das eine Vorlage zur Wahl stellt -- der Aufbeton einer Platte."""

    schluessel: str
    beschriftung: str
    titel: str
    arten: Tuple[str, ...]
    """Welche Materialarten es sein darf."""

    def als_dict(self) -> Dict[str, Any]:
        return {**asdict(self), "arten": list(self.arten)}


@dataclass(frozen=True)
class Vorlage:
    """
    Eine Vorlage: ihre Masse, ihre Lagen und wie sie daraus eine Form
    zeichnet. ``pruefen`` sagt, was an den Massen untereinander nicht geht,
    mit dem Abstand der Lagen vom Rand; ob die Staebe im Querschnitt Platz
    haben, prueft :meth:`bauen` fuer alle gleich.
    """

    schluessel: str
    name: str
    masse: Tuple[Mass, ...]
    lagen: Tuple[Lage, ...]
    form: Callable[[Mapping[str, float], Abstand], Form]
    pruefen: Callable[[Mapping[str, float], Abstand], Optional[str]]
    hat_waende: bool = True
    stoffe: Tuple[Stoff, ...] = ()

    @property
    def alle_masse(self) -> Tuple[Mass, ...]:
        """Die Masse der Form, die Ueberdeckung, die der Lagen und die der Buegel."""
        buegel = BUEGEL.masse if self.hat_waende else ()
        return (*self.masse, UEBERDECKUNG, *(m for l in self.lagen for m in l.masse), *buegel)

    def bauen(self, masse: Optional[Mapping[str, float]] = None,
              bewehrung: bool = True, schubwaende: bool = True) -> Teile:
        """
        Die Teile zu diesen Massen -- was fehlt, nach Vorgabe; ``masse``
        traegt auch Ueberdeckung, Lagen und Buegel. Ohne ``bewehrung`` keine
        Staebe und Linien, ohne ``schubwaende`` keine Waende. Passen die
        Masse nicht zueinander oder die Staebe nicht in den Querschnitt, ein
        ``ValueError`` mit dem Grund.
        """
        werte = {m.schluessel: float((masse or {}).get(m.schluessel, m.vorgabe))
                 for m in self.alle_masse}
        for m in self.alle_masse:
            grund = m.grund(werte[m.schluessel])
            if grund:
                raise ValueError(grund)
        waende = schubwaende and self.hat_waende
        buegel = werte[BUEGEL.durchmesser.schluessel] if waende else 0.0

        def abstand(schluessel: str) -> float:
            d = next(l.durchmesser for l in self.lagen if l.schluessel == schluessel)
            return werte[UEBERDECKUNG.schluessel] + buegel + werte[d.schluessel] / 2

        grund = self.pruefen(werte, abstand)
        if grund:
            raise ValueError(grund)
        form = self.form(werte, abstand)
        teile = Teile(polygone=form.polygone, masslinien=form.masslinien)
        if waende:
            teile.schubwaende = [{**w, "durchmesser": buegel,
                                  "teilung": werte[BUEGEL.menge.schluessel]}
                                 for w in form.schubwaende]
        if bewehrung:
            for l in self.lagen:
                self._lage_einsetzen(teile, l, form.reihen[l.schluessel], werte)
        return teile

    def _lage_einsetzen(self, teile: Teile, l: Lage, reihe: Union[Linie, Ring],
                        werte: Mapping[str, float]) -> None:
        """Die Staebe einer Lage -- nur, wenn jeder ganz im Querschnitt liegt und keiner im naechsten."""
        d, menge = werte[l.durchmesser.schluessel], werte[l.menge.schluessel]
        punkte, abstand = reihe.staebe(menge) if reihe.hat_platz else ((), 0.0)
        umrisse = [p["punkte"] for p in teile.polygone]
        traegt = [not p["aussparung"] for p in teile.polygone]
        if not punkte or not all(stab_liegt_in(p, d / 2, umrisse, traegt) for p in punkte):
            raise ValueError(f"Die Stäbe {l.name} passen nicht in den Querschnitt – "
                             "Überdeckung, Bügel oder Durchmesser sind zu gross.")
        if len(punkte) > 1 and abstand < d:
            raise ValueError(f"Die Stäbe {l.name} liegen ineinander – ihr Abstand "
                             f"{abstand:.0f} mm ist kleiner als ihr Durchmesser {d:g} mm.")
        reihe.einsetzen(teile, d, menge, punkte)
        teile.lagen[l.schluessel] = _stabzahl(punkte, abstand)


def rechteck_der_skripte() -> Teile:
    """
    Das Rechteck, mit dem :meth:`~opencivil.projekt.Projekt.querschnittsanalyse`
    eine Analyse beginnt: 300 × 600 mm, drei ⌀20 unten und zwei ⌀12 oben,
    ihre Achsen 50 mm vom Rand, ohne Schubwand. So sah die Vorlage
    «Rechteck» bis 2026-11-27 aus; Skripte und Tests behalten so ihre Zahlen.
    """
    return Teile(
        polygone=[umriss(rechteckpunkte(300.0, 600.0))],
        stablinien=[
            {"von": (50.0, 50.0), "bis": (250.0, 50.0), "art": Linienart.ANZAHL.value,
             "anzahl": 3.0, "durchmesser": 20.0},
            {"von": (50.0, 550.0), "bis": (250.0, 550.0), "art": Linienart.ANZAHL.value,
             "anzahl": 2.0, "durchmesser": 12.0},
        ])


# ===========================================================================
# Die sieben Vorlagen
# ===========================================================================
#
# Jede Form zeichnet aus ihren Massen und dem Abstand ihrer Lagen vom Rand;
# ihr ``pruefen`` sagt, was an den Massen untereinander nicht geht. Ob die
# Staebe Platz haben, prueft :meth:`Vorlage.bauen` fuer alle gleich.

#: Zu niedrig fuer Staebe und Wand: die Achsen oben und unten liegen
#: uebereinander, die Wand dazwischen haette keine Laenge.
ZU_NIEDRIG = "Der Querschnitt ist zu niedrig für Überdeckung, Bügel und Stäbe oben und unten."


def _rechteck(m: Mapping[str, float], a: Abstand) -> Form:
    b, h = m["b"], m["h"]
    au, ao = a("unten"), a("oben")
    return Form(
        polygone=[umriss(rechteckpunkte(b, h))],
        reihen={"unten": Linie((au, au), (b - au, au)),
                "oben": Linie((ao, h - ao), (b - ao, h - ao))},
        # Eine Wand ueber die ganze Breite: der Steg ist der Querschnitt.
        schubwaende=[{"von": (b / 2, au), "bis": (b / 2, h - ao), "dicke": b}],
        masslinien=[masslinie((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links")],
    )


def _rechteck_pruefen(m: Mapping[str, float], a: Abstand) -> Optional[str]:
    return ZU_NIEDRIG if a("unten") + a("oben") >= m["h"] else None


def _tbalken(m: Mapping[str, float], a: Abstand) -> Form:
    b, h, bw, hf = m["b"], m["h"], m["b_w"], m["h_f"]
    y0 = (b - bw) / 2
    au, ao = a("unten"), a("oben")
    return Form(
        polygone=[umriss(t_punkte(b, h, bw, hf))],
        reihen={"unten": Linie((y0 + au, au), (y0 + bw - au, au)),
                "oben": Linie((ao, h - ao), (b - ao, h - ao))},
        # Der Steg bis in die Mitte des Flanschs.
        schubwaende=[{"von": (b / 2, au), "bis": (b / 2, h - hf / 2), "dicke": bw}],
        masslinien=[masslinie((0.0, h), (b, h), "b", b, "oben"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links"),
                    masslinie((y0, 0.0), (y0 + bw, 0.0), "b_w", bw, "unten"),
                    masslinie((b, h - hf), (b, h), "h_f", hf, "rechts")],
    )


def _tbalken_pruefen(m: Mapping[str, float], a: Abstand) -> Optional[str]:
    grund = t_pruefen(m["b"], m["h"], m["b_w"], m["h_f"])
    if grund:
        return grund
    return ZU_NIEDRIG if a("unten") >= m["h"] - m["h_f"] / 2 else None


def _doppel_t_punkte(m: Mapping[str, float]) -> List[Punkt]:
    """Ein I aus zwei Gurten und dem Steg, alle mittig -- der Ursprung unten links."""
    bo, ho, bw, bu, hu, h = (m[k] for k in ("b_o", "h_o", "b_w", "b_u", "h_u", "h"))
    breite = max(bo, bu)
    yo, yw, yu = (breite - bo) / 2, (breite - bw) / 2, (breite - bu) / 2
    return [(yu, 0.0), (yu + bu, 0.0), (yu + bu, hu), (yw + bw, hu), (yw + bw, h - ho),
            (yo + bo, h - ho), (yo + bo, h), (yo, h), (yo, h - ho), (yw, h - ho), (yw, hu),
            (yu, hu)]


def _doppel_t(m: Mapping[str, float], a: Abstand) -> Form:
    bo, ho, bw, bu, hu, h = (m[k] for k in ("b_o", "h_o", "b_w", "b_u", "h_u", "h"))
    breite = max(bo, bu)
    yo, yw, yu = (breite - bo) / 2, (breite - bw) / 2, (breite - bu) / 2
    au, ao = a("unten"), a("oben")
    steg = (hu + h - ho) / 2
    return Form(
        polygone=[umriss(_doppel_t_punkte(m))],
        reihen={"unten": Linie((yu + au, au), (yu + bu - au, au)),
                "oben": Linie((yo + ao, h - ao), (yo + bo - ao, h - ao))},
        # Wie beim T: von den Staeben unten bis in die Mitte des Obergurts.
        schubwaende=[{"von": (breite / 2, au), "bis": (breite / 2, h - ho / 2), "dicke": bw}],
        masslinien=[masslinie((yo, h), (yo + bo, h), "b_o", bo, "oben"),
                    masslinie((yu, 0.0), (yu + bu, 0.0), "b_u", bu, "unten"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links"),
                    masslinie((yo + bo, h - ho), (yo + bo, h), "h_o", ho, "rechts"),
                    masslinie((yu + bu, 0.0), (yu + bu, hu), "h_u", hu, "rechts"),
                    masslinie((yw, steg), (yw + bw, steg), "b_w", bw, "unten")],
    )


def _doppel_t_pruefen(m: Mapping[str, float], a: Abstand) -> Optional[str]:
    if m["b_w"] >= min(m["b_o"], m["b_u"]):
        return "Der Steg b_w muss schmaler sein als beide Gurte."
    if m["h_o"] + m["h_u"] >= m["h"]:
        return "Die Gurte h_o und h_u müssen zusammen dünner sein als die Höhe h."
    return ZU_NIEDRIG if a("unten") >= m["h"] - m["h_o"] / 2 else None


def _trapez(m: Mapping[str, float], a: Abstand) -> Form:
    bo, bu, h = m["b_o"], m["b_u"], m["h"]
    breite = max(bo, bu)
    lu, lo = (breite - bu) / 2, (breite - bo) / 2
    # Die linke Kante: wie weit sie je mm Hoehe nach rechts geht, und wie viel
    # waagrecht ein Abstand quer zu ihr ausmacht.
    neigung = (lo - lu) / h
    quer = math.hypot(lo - lu, h) / h

    def reihe(z: float, ab: float) -> Linie:
        links = lu + neigung * z + ab * quer
        return Linie((links, z), (breite - links, z))

    au, ao = a("unten"), a("oben")
    # Die Wand so dick wie die engste Stelle zwischen den Staeben -- nach
    # Vorgabe, nicht nachgeschlagen (notizbuch/Notizen/TODO.md).
    dicke = min(bu + (bo - bu) * z / h for z in (au, h - ao))
    return Form(
        polygone=[umriss([(lu, 0.0), (lu + bu, 0.0), (lo + bo, h), (lo, h)])],
        reihen={"unten": reihe(au, au), "oben": reihe(h - ao, ao)},
        schubwaende=[{"von": (breite / 2, au), "bis": (breite / 2, h - ao), "dicke": dicke}],
        masslinien=[masslinie((lo, h), (lo + bo, h), "b_o", bo, "oben"),
                    masslinie((lu, 0.0), (lu + bu, 0.0), "b_u", bu, "unten"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links")],
    )


def _hohlkasten(m: Mapping[str, float], a: Abstand) -> Form:
    b, h, t = m["b"], m["h"], m["t"]
    halb = t / 2
    au, ao = a("unten"), a("oben")
    return Form(
        polygone=[umriss(rechteckpunkte(b, h)),
                  loch(rechteckpunkte(b - 2 * t, h - 2 * t, t, t))],
        reihen={"unten": Linie((au, au), (b - au, au)),
                "oben": Linie((ao, h - ao), (b - ao, h - ao))},
        # Die Waende auf den Mittellinien, Ende an Ende: sie umschliessen die
        # Zelle, und die Torsion laeuft um sie herum.
        schubwaende=[
            {"von": (halb, halb), "bis": (b - halb, halb), "dicke": t},
            {"von": (b - halb, halb), "bis": (b - halb, h - halb), "dicke": t},
            {"von": (b - halb, h - halb), "bis": (halb, h - halb), "dicke": t},
            {"von": (halb, h - halb), "bis": (halb, halb), "dicke": t},
        ],
        masslinien=[masslinie((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    masslinie((0.0, 0.0), (0.0, h), "h", h, "links"),
                    masslinie((b - t, h), (b, h), "t", t, "oben")],
    )


def _hohlkasten_pruefen(m: Mapping[str, float], a: Abstand) -> Optional[str]:
    if 2 * m["t"] >= min(m["b"], m["h"]):
        return "Die Wände müssen dünner sein als die halbe Breite und Höhe."
    return None


#: Der Aufbeton einer Platte: ein Beton, der nicht der der Platte sein muss.
AUFBETON = Stoff("aufbeton", "Aufbeton", "Woraus der Aufbeton ist – die Platte darunter aus "
                 "dem Material oben", ("beton",))


def _aufbeton(m: Mapping[str, float], a: Abstand) -> Form:
    b, hu, ho = m["b"], m["h_u"], m["h_o"]
    h = hu + ho
    au, ao = a("unten"), a("oben")
    return Form(
        polygone=[umriss(rechteckpunkte(b, hu)),
                  umriss(rechteckpunkte(b, ho, 0.0, hu), AUFBETON.schluessel)],
        reihen={"unten": Linie((au, au), (b - au, au)),
                "oben": Linie((ao, h - ao), (b - ao, h - ao))},
        masslinien=[masslinie((0.0, 0.0), (b, 0.0), "b", b, "unten"),
                    masslinie((b, 0.0), (b, hu), "h_u", hu, "rechts"),
                    masslinie((b, hu), (b, h), "h_o", ho, "rechts")],
    )


def _kreis(m: Mapping[str, float], a: Abstand) -> Form:
    d = m["D"]
    mitte = (d / 2, d / 2)
    return Form(
        polygone=[umriss(kreispunkte(mitte, d / 2))],
        reihen={"rand": Ring(mitte, d / 2 - a("rand"))},
        masslinien=[masslinie((0.0, 0.0), (d, 0.0), "D", d, "unten")],
    )


def _nichts(m: Mapping[str, float], a: Abstand) -> Optional[str]:
    """Masse, die untereinander nichts verlangen: ob die Staebe Platz haben, prueft das Bauen."""
    return None


def _unten_oben(unten: Tuple[float, float], oben: Tuple[float, float]) -> Tuple[Lage, Lage]:
    """Die Lagen unten und oben, je ⌀ und s nach der Vorgabe ihrer Vorlage."""
    return lage("unten", "unten", *unten), lage("oben", "oben", *oben)


VORLAGEN: Tuple[Vorlage, ...] = (
    Vorlage("rechteck", "Rechteck",
            (Mass("b", "b", "Breite", 300.0), Mass("h", "h", "Höhe", 600.0)),
            _unten_oben((20.0, 100.0), (12.0, 200.0)), _rechteck, _rechteck_pruefen),
    Vorlage("tbalken", "T-Balken",
            (Mass("b", "b", "Flanschbreite", 1200.0), Mass("h", "h", "Höhe", 700.0),
             Mass("b_w", "b_w", "Stegbreite", 300.0), Mass("h_f", "h_f", "Flanschdicke", 200.0)),
            _unten_oben((20.0, 100.0), (12.0, 150.0)), _tbalken, _tbalken_pruefen),
    Vorlage("doppel_t", "Doppel-T",
            (Mass("b_o", "b_o", "Breite Obergurt", 800.0),
             Mass("h_o", "h_o", "Dicke Obergurt", 150.0),
             Mass("b_w", "b_w", "Stegbreite", 200.0),
             Mass("b_u", "b_u", "Breite Untergurt", 500.0),
             Mass("h_u", "h_u", "Dicke Untergurt", 200.0),
             Mass("h", "h", "Höhe", 1000.0)),
            _unten_oben((20.0, 100.0), (12.0, 150.0)), _doppel_t, _doppel_t_pruefen),
    Vorlage("trapez", "Trapez",
            (Mass("b_o", "b_o", "Breite oben", 400.0), Mass("b_u", "b_u", "Breite unten", 300.0),
             Mass("h", "h", "Höhe", 600.0)),
            _unten_oben((20.0, 100.0), (12.0, 150.0)), _trapez, _rechteck_pruefen),
    Vorlage("hohlkasten", "Hohlkasten",
            (Mass("b", "b", "Breite", 1200.0), Mass("h", "h", "Höhe", 800.0),
             Mass("t", "t", "Wanddicke", 200.0)),
            _unten_oben((16.0, 150.0), (16.0, 150.0)), _hohlkasten, _hohlkasten_pruefen),
    Vorlage("aufbeton", "Platte mit Aufbeton",
            (Mass("b", "b", "Breite", 1000.0), Mass("h_u", "h_u", "Dicke unten", 200.0),
             Mass("h_o", "h_o", "Dicke oben", 100.0)),
            _unten_oben((12.0, 150.0), (10.0, 150.0)), _aufbeton, _nichts,
            hat_waende=False, stoffe=(AUFBETON,)),
    Vorlage("kreis", "Kreis",
            (Mass("D", "D", "Durchmesser", 500.0),),
            (Lage("rand", "am Rand", Mass("d", "⌀", "Stabdurchmesser", 16.0),
                  Mass("n", "n", "Anzahl Stäbe", 8.0, EINHEITSLOS, ganzzahlig=True)),),
            _kreis, _nichts, hat_waende=False),
)


def vorlage(schluessel: str) -> Vorlage:
    """Die Vorlage zu einem Schluessel -- ``ValueError``, wenn es sie nicht gibt."""
    for v in VORLAGEN:
        if v.schluessel == schluessel:
            return v
    bekannt = ", ".join(v.schluessel for v in VORLAGEN)
    raise ValueError(f"Keine Vorlage '{schluessel}' (bekannt sind: {bekannt}).")
