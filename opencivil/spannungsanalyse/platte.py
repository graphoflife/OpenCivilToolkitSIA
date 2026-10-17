"""
opencivil/spannungsanalyse/platte.py -- das Paar einer Platte.

VERANTWORTUNG:
Die beiden Querschnittsloeser einer Tragrichtung, gerissen und ungerissen,
dazu Riss, Bezugsflaeche des Moduls und was die Herleitung nur von der
Platte weiss (:class:`Loeserpaar`, ein :class:`~opencivil.spannungsanalyse.linie.Paar`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Tuple

from opencivil.core.einheiten import MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.nachweis import dehnungsfaecher
from opencivil.nachweis.querschnittsloeser import Querschnittsloeser
from opencivil.nachweis.rechenwahl import Betonkennwerte, gesetze, staehle, stahllagen
from opencivil.nachweis.sproedes_versagen import (
    beiwert_dicke, protokoll_zugfestigkeit, rissmoment,
)
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl
from opencivil.querschnitt.platte import Richtung
from opencivil.spannungsanalyse.art import Analyseart
from opencivil.spannungsanalyse.linie import Grenzzustand, Linie

if TYPE_CHECKING:
    from opencivil.core.wert import Wert


# ===========================================================================
# Die Loeser einer Platte
# ===========================================================================


@dataclass(frozen=True)
class Loeserpaar:
    """
    Die beiden Querschnittsloeser einer Tragrichtung -- gerissen und nicht.

    Sie unterscheiden sich in genau einem Stueck, dem Betongesetz. Alles
    andere -- Hoehe, Breite, Lagen, Stahlgesetz, Grenzen -- ist dasselbe, und
    das muss es sein: sonst verglichen die beiden Zustaende zwei verschiedene
    Querschnitte. Dazu, was zum Riss und zum Fliessen gehoert, und womit
    gerechnet wird.
    """

    gerissen: Querschnittsloeser
    ungerissen: Querschnittsloeser
    M_Riss: float
    """Das Rissmoment ohne Normalkraft -- mit ``k_t`` fuer ein Drittel der Dicke."""

    k_t_zug: float = 1.0
    f_ct_eff_zug: float = 0.0
    """Fuer die Rissnormalkraft: ``k_t`` fuer die ganze Dicke und ``k_t·f_ctm``."""

    staehle: Tuple[Any, ...] = ()
    """
    Die Staehle der Lagen, jeder einmal -- fuer die Fliessdehnung in der
    Herleitung. Fliessen beginnt, wo die erste Lage die Fliessdehnung ihres
    eigenen Stahls erreicht (:attr:`Stahlgesetz.eps_yd` der Lage).
    """

    wahl: Rechenwahl = Rechenwahl(art=Rechenart.PARABEL)
    """Womit gerechnet wird -- Kriechzahl, Wertesatz, Rechenart."""

    grenznamen: Tuple[str, ...] = ()
    """Je Grenze des gerissenen Loesers, was sie ist -- fuer «massgebend»."""

    ids: Mapping[str, str] = field(default_factory=dict)
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung."""

    E_cm: float = 0.0
    """Der Modul des Betons -- daran misst sich der aequivalente Modul."""

    def rissmoment_bei(self, N: float) -> float:
        """
        Das Rissmoment bei der Normalkraft ``N`` (Zug positiv), in Nm.

        Am Bruttoquerschnitt reisst der Rand, wenn ``N/A + M/W = f_ct,eff``.
        Mit ``A = b·h`` und ``W = b·h²/6`` -- denselben Werten, mit denen
        :func:`~opencivil.nachweis.sproedes_versagen.rissmoment` das
        Rissmoment ohne Normalkraft rechnet -- ist das
        ``M_Riss(N) = M_Riss(0) - N·h/6``. Druck hebt es, Zug senkt es.

        Annahme, nicht nachgeschlagen (``notizbuch/Notizen/TODO.md``): der
        Bruttoquerschnitt ohne Stahl, wie beim spröden Versagen. Der
        ungerissene Zustand daneben rechnet mit Stahl und Kriechzahl und ist
        darum steifer; beim Rissmoment steht sein Rand etwas unter
        ``f_ct,eff``.

        ``f_ct,eff`` mit ``k_t`` fuer ein Drittel der Dicke, auch unter Zug:
        Biegung bleibt bei ``h/3``, nach Vorgabe. Die Rissnormalkraft nimmt die
        ganze Dicke (:meth:`rissnormalkraft_bei`); beim selben N und M reissen
        die beiden Linien darum nicht am selben Punkt.
        """
        return self.M_Riss - N * self.gerissen.h / 6.0

    def rissnormalkraft_bei(self, M: float) -> float:
        """
        Die Zugkraft, bei der der Querschnitt mit dem Moment ``M`` reisst, in N.

        Am Bruttoquerschnitt reisst der Rand, wenn ``N/A + |M|/W = f_ct,eff``,
        also ``N_Riss(M) = f_ct,eff·b·h - 6·|M|/h``. Das Vorzeichen des
        Moments zaehlt nicht -- der Querschnitt ist oben wie unten derselbe.

        ``f_ct,eff`` mit ``k_t = 1/(1 + 0.5·t)`` fuer die ganze Dicke,
        ``t = h``: unter Zug reisst der ganze Querschnitt, nicht ein Drittel
        wie unter Biegung. Nach Vorgabe, nicht nachgeschlagen
        (``notizbuch/Notizen/TODO.md``). Bis 2026-10-09 galt das ``f_ct,eff``
        des Rissmoments, mit ``t = h/3`` -- am Beispiel 829 statt 757 kN.
        """
        h, b = self.gerissen.h, self.gerissen.b
        return self.f_ct_eff_zug * b * h - 6.0 * abs(M) / h

    @property
    def I_c(self) -> float:
        """Der reine Betonquerschnitt fuer den aequivalenten Modul: ``b·h³/12``."""
        return self.gerissen.b * self.gerissen.h ** 3 / 12.0

    @property
    def A_c(self) -> float:
        """Dasselbe fuer die Normalkraft: ``b·h``."""
        return self.gerissen.b * self.gerissen.h

    # -- Was die Herleitung nur von der Platte weiss --------------------------

    #: Wo die Mitteldehnung gilt -- dort greift N an.
    bezugsort = "auf halber Höhe"

    def tiefe(self, w: Zwischenwerte, ein: Callable[[str], "Wert"]) -> "Wert":
        """Die Dicke, ueber die die Linie laeuft -- ein Wert der Platte."""
        return ein("h")

    def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: Linie,
                        ein: Callable[[str], "Wert"], h: "Wert") -> None:
        """Wo die Linie reisst: das Rissmoment bei N, oder die Rissnormalkraft bei M."""
        if linie.art is Analyseart.MOMENT_KRUEMMUNG:
            p.erklaerung(
                "Am Bruttoquerschnitt reisst der Rand, wenn N/A + M/W = f_ct,eff. Mit "
                "A = b·h und W = b·h²/6 hebt Druck das Rissmoment, Zug senkt es. Beim "
                "Rissmoment springt die Krümmung bei demselben Moment vom ungerissenen "
                "auf den gerissenen Wert.")
            p.formel(w.moment("M_Riss_N", "M_{Riss}(N)", linie.riss),
                     r"@M_Riss - @N \cdot \frac{@h}{6}",
                     {"M_Riss": w.moment("M_Riss", "M_{Riss}", self.M_Riss),
                      "N": w.kraft("N", "N", linie.fest), "h": h},
                     titel="Rissmoment bei der Normalkraft")
            return
        p.erklaerung(
            "Dieselbe Rissbedingung, nach der Normalkraft aufgelöst: beim Moment M "
            "reisst der Querschnitt, wenn die Zugkraft N_Riss erreicht. Unter Zug "
            "reisst die ganze Dicke, darum gilt k_t für t = h und nicht für h/3 wie "
            "beim Rissmoment. Bei N_Riss springt die Dehnung bei derselben Kraft vom "
            "ungerissenen auf den gerissenen Wert.")
        f_ct_eff = protokoll_zugfestigkeit(
            p, w, k_t=self.k_t_zug, f_ct_eff=self.f_ct_eff_zug, h=h,
            f_ctm=ein("f_ctm"), teiler=1, referenz="SIA 262:2025, 4.4.2")
        p.formel(w.kraft("N_Riss_M", "N_{Riss}(M)", linie.riss),
                 r"@f_ct_eff \cdot @b \cdot @h - \frac{6 \cdot \left|@M\right|}{@h}",
                 {"f_ct_eff": f_ct_eff, "b": ein("b"), "h": h,
                  "M": w.moment("M", "M", linie.fest)},
                 titel="Rissnormalkraft beim Moment")

    def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: "Grenzzustand",
                                   oben: "Wert", unten: "Wert") -> None:
        """Die Dehnung, ueber die die N-eps-Linie laeuft, am Ende -- auf halber Hoehe."""
        p.formel(w.dehnung("eps_mu", r"\varepsilon_{m,u}", bruch.verformung),
                 r"\frac{@eps_oben + @eps_unten}{2}",
                 {"eps_oben": oben, "eps_unten": unten},
                 titel="Grösste Dehnung auf halber Höhe")

    def herleitung_bezug(self, p: Protokoll, w: Zwischenwerte, momente: bool,
                         ein: Callable[[str], "Wert"], h: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des aequivalenten Moduls -- ein Rechteck b·h."""
        if momente:
            bezug = w.wert("I_c", "I_c", Groesse.aus_si(self.I_c, MIO_MM4), stellen=1)
            p.formel(bezug, r"\frac{@b \cdot \left(@h\right)^{3}}{12}",
                     {"b": ein("b"), "h": h},
                     titel="Reiner Betonquerschnitt: Flächenmoment",
                     name="Flächenträgheitsmoment eines Rechtecks")
            return bezug
        bezug = w.flaeche("A_c", "A_c", self.A_c)
        p.formel(bezug, r"@b \cdot @h", {"b": ein("b"), "h": h},
                 titel="Reiner Betonquerschnitt: Fläche", name="Fläche eines Rechtecks")
        return bezug


def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float],
               wahl: Rechenwahl = Rechenwahl(art=Rechenart.PARABEL)) -> Optional[Loeserpaar]:
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
    satz = wahl.satz
    lagen = stahllagen(posten, satz, wert)
    beton = querschnitt.beton
    ids = {
        "h": querschnitt.id_von("h"), "b": querschnitt.id_breite(richtung),
        "E_cm": beton.id_von("E_cm"), "f_c": beton.id_von(satz.beton),
        "eps_c1d": beton.id_von("eps_c1d"), "eps_c2d": beton.id_von("eps_c2d"),
        "f_ctm": beton.id_von("f_ctm"),
    }
    h, b = wert(ids["h"]), wert(ids["b"])
    w = Betonkennwerte(f_c=wert(ids["f_c"]), E_cm=wert(ids["E_cm"]),
                       eps_c1d=wert(ids["eps_c1d"]), eps_c2d=wert(ids["eps_c2d"]))
    g = gesetze(wahl, w)
    # Die Grenzen gelten an den Lagen, mit denen gerechnet wird -- in der
    # Handrechnung den zusammengefassten --, jede mit dem eps_ud ihres Stahls.
    grenzen, namen = dehnungsfaecher.grenzen(
        h, [(l.z, l.stahl.eps_ud, f"Stahl der {l.nummer}. Lage") for l in g.lagen(lagen, h)],
        eps_c1d=w.eps_c1d, eps_c2d=w.eps_c2d)
    fenster = dict(grenzen=grenzen, eps_druck=w.eps_c2d)
    gerissen = g.loeser(h=h, b=b, lagen=lagen, **fenster)
    # Derselbe Querschnitt ungerissen: nur das Betongesetz ist ein anderes.
    ungerissen = gesetze(wahl, w, ungerissen=True).loeser(h=h, b=b, lagen=lagen, **fenster)
    f_ctm = wert(ids["f_ctm"])
    k_t_zug = beiwert_dicke(h)
    return Loeserpaar(
        gerissen=gerissen, ungerissen=ungerissen,
        M_Riss=rissmoment(h=h, b=b, f_ctm=f_ctm).M_Riss,
        k_t_zug=k_t_zug, f_ct_eff_zug=k_t_zug * f_ctm,
        staehle=tuple(staehle(posten)),
        wahl=wahl, grenznamen=namen, ids=ids, E_cm=w.E_cm)
