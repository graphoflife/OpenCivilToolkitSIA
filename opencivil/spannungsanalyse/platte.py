"""
opencivil/spannungsanalyse/platte.py -- das Paar einer Platte.

VERANTWORTUNG:
Die beiden Loeser einer Tragrichtung, gerissen und ungerissen, und was die
Herleitung nur von der Platte weiss (:class:`Loeserpaar`, ein
:class:`~opencivil.spannungsanalyse.linie.Paar`). Die Loeser sind die jedes
Querschnitts: die Platte als Rechteck mit Staeben
(:meth:`~opencivil.nachweis.rechenwahl.Gesetze.loeser`). Den Riss rechnet
sie wie der gezeichnete Querschnitt, am Bruttoquerschnitt -- dem Rechteck
``b × h`` (:class:`~opencivil.spannungsanalyse.riss.Bruttoriss`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Tuple

from opencivil.core.einheiten import MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.nachweis.querschnittsloeser import Faserloeser
from opencivil.nachweis.rechenwahl import Betonkennwerte, gesetze, staehle, stahllagen
from opencivil.nachweis.rissgroessen import (
    Bruttoquerschnitt, Rissmoment, bruttoquerschnitt_rechteck, rissaktive_dicke, rissmoment,
)
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenarten, Rechenwahl
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.linie import (
    SUCHE_DER_ANALYSEN, FesteNulllinie, Grenzzustand, Zustaende,
)
from opencivil.spannungsanalyse.riss import Bruttoriss

if TYPE_CHECKING:
    from opencivil.core.wert import Wert


# ===========================================================================
# Die Loeser einer Platte
# ===========================================================================


@dataclass(frozen=True)
class Loeserpaar(Bruttoriss):
    """
    Die beiden Loeser einer Tragrichtung -- gerissen und nicht.

    Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
    andere -- Hoehe, Breite, Lagen, Stahlgesetz, Grenzen -- ist dasselbe, und
    das muss es sein: sonst verglichen die beiden Zustaende zwei verschiedene
    Querschnitte. Dazu, was zum Riss und zum Fliessen gehoert, und womit
    gerechnet wird.
    """

    gerissen: Faserloeser
    ungerissen: Faserloeser
    h: float
    b: float
    """Hoehe und Breite des Streifens, m."""

    brutto: Bruttoquerschnitt
    """Das Rechteck ``b × h`` ohne Stahl -- an ihm reisst die Platte."""

    riss: Rissmoment
    """Das Rissmoment unter reiner Biegung, ohne Normalkraft."""

    staehle: Tuple[Any, ...] = ()
    """
    Die Staehle der Lagen, jeder einmal -- fuer die Fliessdehnung in der
    Herleitung. Fliessen beginnt, wo die erste Lage die Fliessdehnung ihres
    eigenen Stahls erreicht (:attr:`Stahlgesetz.eps_yd` der Lage).
    """

    wahl: Rechenwahl = Rechenwahl(arten=Rechenarten.alle(Rechenart.PARABEL))
    """Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart."""

    ids: Mapping[str, str] = field(default_factory=dict)
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung."""

    E_cm: float = 0.0
    """Der Modul des Betons -- daran misst sich der aequivalente Modul."""

    #: Ein positives Moment zieht unten.
    seite = Zugseite.UNTEN

    DICKE_UNTER_ZUG = "die Dicke der Platte"

    def ebenen(self) -> Zustaende:
        """Die Ebenen der Platte: ein Rechteck, die Nulllinie bleibt parallel zur Achse."""
        return Zustaende(FesteNulllinie(self.gerissen), FesteNulllinie(self.ungerissen))

    @property
    def A(self) -> float:
        """Die Flaeche des Rechtecks, ``b·h``."""
        return self.b * self.h

    @property
    def t_zug(self) -> float:
        """Die rissaktive Dicke unter Zug: die ganze Dicke der Platte."""
        return rissaktive_dicke(h=self.h, zug=True)

    # -- Was die Herleitung nur von der Platte weiss --------------------------

    #: Wo die Mitteldehnung gilt -- dort greift N an.
    bezugsort = "auf halber Höhe"

    def tiefe(self, w: Zwischenwerte, ein: Callable[[str], "Wert"]) -> "Wert":
        """Die Dicke, ueber die die Linie laeuft -- ein Wert der Platte."""
        return ein("h")

    def herleitung_bruttoquerschnitt(self, p: Protokoll, w: Zwischenwerte,
                                     ein: Callable[[str], "Wert"],
                                     h: "Wert") -> Tuple["Wert", "Wert"]:
        """Das Rechteck ``b × h`` des Streifens, ohne Stahl: ``A`` und ``I`` aus b und h."""
        A = w.flaeche("A", "A", self.A, "Fläche des Bruttoquerschnitts")
        p.formel(A, r"@b \cdot @h", {"b": ein("b"), "h": h},
                 titel="Bruttoquerschnitt: Fläche", name="Fläche eines Rechtecks")
        I = w.wert("I", "I", Groesse.aus_si(self.I, MIO_MM4), stellen=1)
        p.formel(I, r"\frac{@b \cdot \left(@h\right)^{3}}{12}", {"b": ein("b"), "h": h},
                 titel="Bruttoquerschnitt: Trägheitsmoment",
                 name="Flächenträgheitsmoment eines Rechtecks")
        return A, I

    def herleitung_dicke_unter_zug(self, p: Protokoll, w: Zwischenwerte, h: "Wert") -> "Wert":
        """
        Unter Zug reisst die ganze Dicke, ``t = h``: der Streifen ``b`` ist keine
        Abmessung der Platte (:func:`~opencivil.nachweis.rissgroessen.rissaktive_dicke`).
        Ein Satz statt einer Formel -- ``t`` steht fuer ``h``, wie bisher.
        """
        p.erklaerung("Der Streifen b ist keine Abmessung der Platte: in ihrer Ebene ist "
                     "sie unbegrenzt. Darum ist t = h.")
        return h

    def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: "Grenzzustand",
                                   oben: "Wert", unten: "Wert", h: "Wert") -> None:
        """Die Dehnung, ueber die die N-eps-Linie laeuft, am Ende -- auf halber Hoehe."""
        p.formel(w.dehnung("eps_mu", r"\varepsilon_{m,u}", bruch.verformung),
                 r"\frac{@eps_oben + @eps_unten}{2}",
                 {"eps_oben": oben, "eps_unten": unten},
                 titel="Grösste Dehnung auf halber Höhe")


def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float],
               wahl: Rechenwahl = Rechenwahl(arten=Rechenarten.alle(Rechenart.PARABEL)),
               ) -> Optional[Loeserpaar]:
    """
    Das Loeserpaar einer Platte in einer Richtung -- ``None`` ohne Bewehrung.

    ``wert`` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
    ``wahl`` sagt, womit gerechnet wird: Kriechzahl, Wertesatz, Rechenart --
    die Gesetze dazu baut :func:`~opencivil.nachweis.rechenwahl.gesetze`.

    Stand frueher in der Schnittstelle zur Oberflaeche. Dort war sie ohne
    Oberflaeche nicht erreichbar, und ein Test baute sie als eigene Kopie
    nach -- er pruefte seine Kopie statt der echten.
    """
    posten = querschnitt.posten_in_richtung(richtung)
    if not posten:
        return None
    lagen = stahllagen(posten, wahl, wert)
    beton = querschnitt.beton
    # Die Zugfestigkeit unter ihrer eigenen ID, wie beim gezeichneten
    # Querschnitt: die Herleitung des Risses liest sie vom Beton der Ecke.
    f_ctm_id = beton.id_von("f_ctm")
    ids = {
        "h": querschnitt.id_von("h"), "b": querschnitt.id_breite(richtung),
        "E_cm": beton.id_von("E_cm"), "f_c": beton.id_von(wahl.satz(beton).beton),
        "eps_c1d": beton.id_von("eps_c1d"), "eps_c2d": beton.id_von("eps_c2d"),
        f_ctm_id: f_ctm_id,
    }
    h, b = wert(ids["h"]), wert(ids["b"])
    w = Betonkennwerte(f_c=wert(ids["f_c"]), E_c=wert(ids["E_cm"]),
                       eps_c1d=wert(ids["eps_c1d"]), eps_c2d=wert(ids["eps_c2d"]),
                       name=beton.name)
    # Gesucht wird im Fenster der Gesetze, wie in jedem Loeser der Platte;
    # seine Grenzen tragen ihre Namen, und die Bilder nennen damit, welche
    # massgebend ist.
    gerissen = gesetze(wahl, w).loeser(h=h, b=b, lagen=lagen, suche=SUCHE_DER_ANALYSEN)
    # Derselbe Querschnitt ungerissen: nur das Betongesetz ist ein anderes.
    ungerissen = gesetze(wahl, w, ungerissen=True).loeser(
        h=h, b=b, lagen=lagen, suche=SUCHE_DER_ANALYSEN)
    brutto = bruttoquerschnitt_rechteck(h=h, b=b, stoff=beton, f_ctm=wert(f_ctm_id))
    return Loeserpaar(
        gerissen=gerissen, ungerissen=ungerissen, h=h, b=b,
        brutto=brutto, riss=rissmoment(brutto, *Loeserpaar.seite.moment),
        staehle=tuple(staehle(posten)),
        wahl=wahl, ids=ids, E_cm=w.E_c)
