"""
opencivil/spannungsanalyse.py -- den Querschnitt ansehen, ohne ihn nachzuweisen.

VERANTWORTUNG:
Vier Auswertungen am selben Faserintegral, das auch die Nachweise benutzen:

1. **Aus Schnittgroessen** -- ``N`` und ``M`` hinein, Dehnungsebene und
   Spannungsverteilung heraus.
2. **Aus Dehnungen** -- Randdehnungen hinein, Spannungen und Schnittgroessen
   heraus. Die Umkehrung von 1, und ohne Suche: die Ebene steht ja schon da.
3. **Momenten-Kruemmungs-Linie** -- eine Normalkraft hinein, der Verlauf
   ``M(chi)`` von null bis zum Bruch heraus.
4. **Normalkraft-Dehnungs-Linie** -- ein Moment hinein, der Verlauf
   ``N(eps_m)`` von null bis zum Bruch auf Zug heraus.

KEIN NACHWEIS:
Hier wird nichts gegen etwas gehalten. Es gibt keinen Erfuellungsgrad und kein
Urteil -- das ist der Unterschied zu allem anderen in diesem Werkzeug und der
Grund, warum die Auswertungen nicht im :class:`Rechenwerk` stehen. Sie
beantworten eine Frage, die man beim Entwerfen stellt: *was passiert
eigentlich im Querschnitt?*

JE ANALYSE GEWAEHLT (:class:`~opencivil.projekt.SpannungsfallEintrag`):
* die Kriechzahl -- ohne Angabe die der Platte;
* der Wertesatz -- Bemessung (``f_cd``, ``f_yd``) oder charakteristisch
  (``f_ck``, ``f_yk``), siehe :class:`Werkstoffsatz`;
* das Betongesetz -- Parabel-Rechteck mit ``E_c,eff`` oder der
  Spannungsblock 0.85·x.
Moduln und Grenzdehnungen sind in beiden Wertesaetzen dieselben, wie ueberall
im Werkzeug.

DIE BEIDEN LINIEN:
Unter dem Riss ist der Querschnitt ungerissen (Zustand I) und deutlich
steifer, als die Nachweise ihn rechnen -- dort wird der Beton auf Zug
grundsaetzlich nicht angesetzt. Beim Riss springt die Verformung bei
derselben Kraft vom ungerissenen auf den gerissenen Wert (Zustand II), im
Bild ein waagrechtes Stueck. Darueber gilt Zustand II bis zum Bruch. Beide
Zustaende rechnet derselbe Loeser, nur mit verschiedenem Betongesetz.

Den gerissenen Teil rechnet die Linie ueber die Verformung -- die Kruemmung
bzw. die Dehnung --, nicht ueber die Kraft. Nach dem Fliessen waechst die
Kraft kaum noch, die Verformung aber stark; ueber die Kraft gerechnet laegen
dort kaum Punkte, und die Suche nach einer Ebene zu einer Kraft nahe am
Widerstand ist die heikelste ueberhaupt.

DAS ENDE:
Die Linie endet bei der groessten Verformung, zu der es noch ein
Gleichgewicht gibt. Dort ist die erste Grenzdehnung erreicht: der Beton am
gedrueckten Rand bei ``-eps_c2d``, der Stahl einer Lage bei ``eps_ud``, der
ganz gedrueckte Querschnitt im Punkt C bei ``-eps_c1d``. Dieselben Grenzen
wie im Dehnungsfaecher der genauen M-N-Linie
(:mod:`opencivil.nachweis.dehnungsfaecher`). Bis 2026-10-09 endete die M-chi-
Linie stattdessen dort, wo die Suche des Loesers aufgab -- an der Platte des
Beispiels bei chi = 0.040 1/m statt 0.057 1/m, und ``eps_ud`` galt am
Betonrand statt am Stahl.

Gezeigt wird der Querschnitt, nicht das Bauteil: die Mitwirkung des Betons
zwischen den Rissen (Zugversteifung) steckt nicht darin. Mit welcher Regel
eine Linie des Bauteils zu rechnen waere, ist offen (TODO.md).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Tuple,
)

from opencivil.core.protokoll import Protokoll, StillesProtokoll, Zwischenwerte
from opencivil.nachweis.querschnittsloeser import (
    Querschnittsloeser, Stahllage, Werkstoffsatz, beton_nichtlinear,
    stahl_bilinear, wirksamer_modul,
)
from opencivil.nachweis.sproedes_versagen import (
    beiwert_dicke, protokoll_zugfestigkeit, rissmoment,
)
from opencivil.querschnitt.fasern import Dehnungsgrenze
from opencivil.querschnitt.platte import Richtung
from opencivil.querschnitt.werkstoffgesetz import BLOCKANTEIL, Betongesetz, Spannungsblock

if TYPE_CHECKING:
    from opencivil.core.rechenwerk import Loesung
    from opencivil.core.wert import Wert
    from opencivil.projekt import Aufbau

#: Punkte ueber die Hoehe, mit denen Dehnung und Spannung gezeichnet werden.
#: Die Betonspannung hat am Nulldurchgang einen Knick; 41 Punkte zeigen ihn,
#: ohne dass die Kurve eckig wird.
STUETZSTELLEN = 41

#: Punkte des gerissenen Teils einer Linie -- vor dem Fliessen ein Drittel,
#: danach der Rest, denn dort waechst die Verformung am staerksten.
KURVENPUNKTE = 40

#: Punkte des ungerissenen Teils. Er ist beinahe gerade.
PUNKTE_UNGERISSEN = 10

#: Unter diesem Thema steht in der Formelsammlung, wie die Linien entstehen.
THEMA = "Spannung-Dehnung-Analyse"


class Analyseart(str, Enum):
    """Welche der vier Fragen gestellt wird."""

    SCHNITTGROESSEN = "schnittgroessen"
    DEHNUNGEN = "dehnungen"
    MOMENT_KRUEMMUNG = "moment_kruemmung"
    NORMALKRAFT_DEHNUNG = "normalkraft_dehnung"

    @property
    def beschriftung(self) -> str:
        return {
            Analyseart.SCHNITTGROESSEN: "Aus N und M",
            Analyseart.DEHNUNGEN: "Aus Randdehnungen",
            Analyseart.MOMENT_KRUEMMUNG: "Momenten-Krümmungs-Linie",
            Analyseart.NORMALKRAFT_DEHNUNG: "Normalkraft-Dehnungs-Linie",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer die Auswahl in der Zeile."""
        return {
            Analyseart.SCHNITTGROESSEN: "N, M",
            Analyseart.DEHNUNGEN: "ε oben/unten",
            Analyseart.MOMENT_KRUEMMUNG: "M–χ",
            Analyseart.NORMALKRAFT_DEHNUNG: "N–ε",
        }[self]


# ===========================================================================
# Das Bild eines Querschnitts
# ===========================================================================

@dataclass(frozen=True)
class Faserpunkt:
    """Eine Stelle ueber die Hoehe, mit dem, was dort geschieht."""

    z: float
    """
    Abstand von der **Oberkante**, in m.

    Dieselbe Achse, die der Loeser und der Lagenaufbau benutzen: dort ist
    ``z`` der Abstand von der gedrueckten Randfaser bei positivem Moment, und
    fuer eine Platte ist das die Oberkante. Die 1. Lage liegt damit bei
    ``z = h - Randabstand`` und die 4. bei ``z = Randabstand``. Wer hier
    umdrehte, bekaeme ein Bild, das zum Nachweis nicht passt.
    """

    eps: float
    sigma: float
    """in Pa, Zug positiv."""


@dataclass(frozen=True)
class Stahlpunkt(Faserpunkt):
    """Dasselbe fuer eine Bewehrungslage."""

    nummer: int
    a_s: float
    kraft: float
    """``sigma * a_s`` in N -- was die Lage traegt."""


@dataclass
class Querschnittsbild:
    """Dehnungsebene, Spannungen und die daraus entstehenden Schnittgroessen."""

    eps_m: float
    chi: float
    N: float
    M: float
    beton: List[Faserpunkt] = field(default_factory=list)
    stahl: List[Stahlpunkt] = field(default_factory=list)
    konvergiert: bool = True
    hinweis: str = ""

    @property
    def nulllinie(self) -> Optional[float]:
        """
        Wo die Dehnung null wird, von der Oberkante aus.

        ``None``, wenn der ganze Querschnitt auf einer Seite liegt -- dann
        gibt es keine Nulllinie, und eine hinzurechnen hiesse, eine Zahl zu
        zeigen, die es nicht gibt.
        """
        if not self.beton or abs(self.chi) < 1e-12:
            return None
        oben, unten = self.beton[0], self.beton[-1]
        if (oben.eps > 0.0) == (unten.eps > 0.0):
            return None
        return oben.z - oben.eps / self.chi


def _bild(loeser: Querschnittsloeser, eps_m: float, chi: float) -> Querschnittsbild:
    """Dehnungen und Spannungen zu einer gegebenen Ebene -- ohne jede Suche."""
    kraefte = loeser.kraefte(eps_m, chi)
    halb = loeser.h / 2.0

    beton = []
    for i in range(STUETZSTELLEN):
        z = loeser.h * i / (STUETZSTELLEN - 1)    # von oben nach unten
        eps = eps_m + chi * (z - halb)
        beton.append(Faserpunkt(z=z, eps=eps, sigma=loeser.beton(eps)))

    stahl = []
    for lage in loeser.lagen:
        eps = eps_m + chi * (lage.z - halb)
        sigma = loeser.stahl(eps)
        stahl.append(Stahlpunkt(z=lage.z, eps=eps, sigma=sigma,
                                nummer=lage.nummer, a_s=lage.a_s,
                                kraft=sigma * lage.a_s))

    return Querschnittsbild(eps_m=eps_m, chi=chi, N=kraefte.N, M=kraefte.M,
                            beton=beton, stahl=stahl)


def aus_schnittgroessen(loeser: Querschnittsloeser, *,
                        N: float, M: float) -> Querschnittsbild:
    """
    Die Dehnungsebene zu ``N`` und ``M``, samt allem, was darauf steht.

    Gesucht wird mit demselben Verfahren wie in den Nachweisen. Findet sich
    keine Ebene, kommt das Bild leer zurueck und sagt warum -- geraten wird
    nicht.
    """
    ebene = loeser.loese(N_Ed=N, M_Ed=M)
    if not ebene.konvergiert:
        return Querschnittsbild(
            eps_m=0.0, chi=0.0, N=N, M=M, konvergiert=False,
            hinweis=("Zu dieser Kombination gibt es keine Gleichgewichtslage: "
                     "der Querschnitt nimmt sie nicht auf."))
    return _bild(loeser, ebene.eps_m, ebene.chi)


def aus_dehnungen(loeser: Querschnittsloeser, *,
                  eps_oben: float, eps_unten: float) -> Querschnittsbild:
    """
    Der umgekehrte Weg: die Ebene ist gegeben, gesucht sind die Kraefte.

    Hier gibt es nichts zu suchen -- aus den beiden Randdehnungen folgen
    Mitteldehnung und Kruemmung unmittelbar, und das Faserintegral liefert
    Normalkraft und Moment in einem Durchgang.
    """
    # z laeuft von der Oberkante nach unten, also ist die Randdehnung unten
    # die bei z = h und die obere die bei z = 0.
    eps_m = 0.5 * (eps_oben + eps_unten)
    chi = (eps_unten - eps_oben) / loeser.h if loeser.h > 0 else 0.0
    bild = _bild(loeser, eps_m, chi)
    aussen = max(abs(eps_oben), abs(eps_unten))
    if aussen > max(loeser.eps_druck, loeser.eps_zug):
        bild.hinweis = (
            f"Die Randdehnung liegt ausserhalb dessen, wofür die "
            f"Werkstoffgesetze gelten (−{loeser.eps_druck * 1e3:.1f} ‰ bis "
            f"+{loeser.eps_zug * 1e3:.1f} ‰). Jenseits davon geben sie null "
            f"zurück, und die Spannungen unten sind keine Aussage mehr.")
    return bild


# ===========================================================================
# Die Loeser einer Platte
# ===========================================================================


def beton_ungerissen(*, E_c: float) -> Callable[[float], float]:
    """
    Beton linear in beiden Richtungen -- der ungerissene Vergleichszustand.

    Ohne Abminderung im Zug und ohne Abbruch bei ``f_ct``. Das ist Absicht:
    gebraucht wird die *Steifigkeit* des ungerissenen Querschnitts, und wo er
    reisst, sagt das Rissmoment -- oberhalb davon gilt die Linie gerissen,
    dieser Zustand steht dort nur noch zum Vergleich. Ein Gesetz, das bei
    ``f_ct`` abfiele, waere ausserdem nicht mehr monoton, und die Bisektion
    des Loesers braucht Monotonie.
    """
    def sigma(eps: float) -> float:
        return E_c * eps
    return sigma


def grenzen_des_faechers(h: float, lagen: List[Stahllage], *, eps_c1d: float,
                         eps_c2d: float, eps_ud: float,
                         ) -> Tuple[List[Dehnungsgrenze], Tuple[str, ...]]:
    """
    Die Grenzdehnungen des Dehnungsfaechers, samt Namen.

    Der Beton an beiden Raendern bis ``-eps_c2d``; im Punkt C, im Abstand
    ``h·(1 - eps_c1d/eps_c2d)`` vom gedrueckten Rand, bis ``-eps_c1d`` --
    das zaehlt erst, wenn der ganze Querschnitt gedrueckt ist; jede Stahllage
    bis ``±eps_ud``. So begrenzt :mod:`opencivil.nachweis.dehnungsfaecher` die
    genaue M-N-Linie, und so endet darum auch jede Linie hier.
    """
    halb = h / 2.0
    z_c = h * (1.0 - eps_c1d / eps_c2d)
    paare = [
        (Dehnungsgrenze(arm=-halb, eps_min=-eps_c2d, eps_max=math.inf), "Beton am oberen Rand"),
        (Dehnungsgrenze(arm=halb, eps_min=-eps_c2d, eps_max=math.inf), "Beton am unteren Rand"),
        (Dehnungsgrenze(arm=z_c - halb, eps_min=-eps_c1d, eps_max=math.inf), "Beton im Punkt C"),
        (Dehnungsgrenze(arm=halb - z_c, eps_min=-eps_c1d, eps_max=math.inf), "Beton im Punkt C"),
    ] + [(Dehnungsgrenze(arm=l.z - halb, eps_min=-eps_ud, eps_max=eps_ud),
          f"Stahl der {l.nummer}. Lage") for l in lagen]
    return [g for g, _ in paare], tuple(n for _, n in paare)


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

    eps_y: float = math.inf
    """Wo der Stahl zu fliessen beginnt: ``f_s / E_s``."""

    satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG
    gesetz: str = "parabel"
    phi: float = 0.0
    phi_eigen: bool = False
    """Ob die Kriechzahl die der Analyse ist -- sonst die der Platte."""

    grenznamen: Tuple[str, ...] = ()
    """Je Grenze des gerissenen Loesers, was sie ist -- fuer «massgebend»."""

    ids: Mapping[str, str] = field(default_factory=dict)
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung."""

    def rissmoment_bei(self, N: float) -> float:
        """
        Das Rissmoment bei der Normalkraft ``N`` (Zug positiv), in Nm.

        Am Bruttoquerschnitt reisst der Rand, wenn ``N/A + M/W = f_ct,eff``.
        Mit ``A = b·h`` und ``W = b·h²/6`` -- denselben Werten, mit denen
        :func:`~opencivil.nachweis.sproedes_versagen.rissmoment` das
        Rissmoment ohne Normalkraft rechnet -- ist das
        ``M_Riss(N) = M_Riss(0) - N·h/6``. Druck hebt es, Zug senkt es.

        Annahme, nicht nachgeschlagen (TODO.md): der Bruttoquerschnitt ohne
        Stahl, wie beim spröden Versagen. Der ungerissene Zustand daneben
        rechnet mit Stahl und Kriechzahl und ist darum steifer; beim
        Rissmoment steht sein Rand etwas unter ``f_ct,eff``.

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
        wie unter Biegung. Nach Vorgabe, nicht nachgeschlagen (TODO.md). Bis
        2026-10-09 galt das ``f_ct,eff`` des Rissmoments, mit ``t = h/3`` --
        am Beispiel 829 statt 757 kN.
        """
        h, b = self.gerissen.h, self.gerissen.b
        return self.f_ct_eff_zug * b * h - 6.0 * abs(M) / h


def loeserpaar(querschnitt, richtung: Richtung, wert: Callable[[str], float],
               *, satz: Werkstoffsatz = Werkstoffsatz.BEMESSUNG,
               gesetz: str = "parabel", phi: Optional[float] = None,
               ) -> Optional[Loeserpaar]:
    """
    Das Loeserpaar einer Platte in einer Richtung -- ``None`` ohne Bewehrung.

    ``wert`` liefert zu einer Wert-ID die Zahl in SI, aus einer Loesung.
    ``satz`` sagt, mit welchen Festigkeiten die Werkstoffgesetze rechnen,
    ``gesetz`` welches der Beton hat -- ``parabel`` oder ``block`` --, und
    ``phi`` die Kriechzahl; ohne sie gilt die der Platte.

    Stand frueher in der Schnittstelle zur Oberflaeche. Dort war sie ohne
    Oberflaeche nicht erreichbar, und ein Test baute sie als eigene Kopie
    nach -- er pruefte seine Kopie statt der echten.
    """
    posten = querschnitt.posten_in_richtung(richtung)
    if not posten:
        return None
    lagen = [Stahllage(a_s=wert(as_id), z=wert(z_id), nummer=lage.nummer)
             for lage, _, _, as_id, z_id in posten]
    stahl = posten[0][0].stahl
    beton = querschnitt.beton
    ids = {
        "h": querschnitt.id_von("h"), "b": querschnitt.id_breite(richtung),
        "E_cm": beton.id_von("E_cm"), "f_c": beton.id_von(satz.beton),
        "eps_c1d": beton.id_von("eps_c1d"), "eps_c2d": beton.id_von("eps_c2d"),
        "f_ctm": beton.id_von("f_ctm"),
        "E_s": stahl.id_von("E_s"), "f_s": stahl.id_von(satz.stahl),
        "eps_ud": stahl.id_von("eps_ud"),
    }
    if phi is None:
        ids["phi"] = querschnitt.id_von("kriechzahl")
    kriechzahl = wert(ids["phi"]) if phi is None else phi
    h, b = wert(ids["h"]), wert(ids["b"])
    E_c_eff = wirksamer_modul(wert(ids["E_cm"]), kriechzahl)
    f_c = wert(ids["f_c"])
    eps_c1d, eps_c2d, eps_ud = wert(ids["eps_c1d"]), wert(ids["eps_c2d"]), wert(ids["eps_ud"])
    block = gesetz == "block"
    grenzen, namen = grenzen_des_faechers(h, lagen, eps_c1d=eps_c1d, eps_c2d=eps_c2d,
                                          eps_ud=eps_ud)
    gemeinsam = dict(
        h=h, b=b, lagen=lagen, grenzen=grenzen, eps_druck=eps_c2d, eps_zug=eps_ud,
        stahl=stahl_bilinear(E_s=wert(ids["E_s"]), f_sd=wert(ids["f_s"]), eps_ud=eps_ud))
    gerissen = Querschnittsloeser(
        beton=(Spannungsblock(f_cd=f_c, eps_c2d=eps_c2d) if block
               else beton_nichtlinear(f_cd=f_c, E_c=E_c_eff, eps_c1d=eps_c1d, eps_c2d=eps_c2d)),
        gemittelt=block, **gemeinsam)
    ungerissen = Querschnittsloeser(beton=beton_ungerissen(E_c=E_c_eff), **gemeinsam)
    f_ctm = wert(ids["f_ctm"])
    k_t_zug = beiwert_dicke(h)
    return Loeserpaar(
        gerissen=gerissen, ungerissen=ungerissen,
        M_Riss=rissmoment(h=h, b=b, f_ctm=f_ctm).M_Riss,
        k_t_zug=k_t_zug, f_ct_eff_zug=k_t_zug * f_ctm,
        eps_y=wert(ids["f_s"]) / wert(ids["E_s"]),
        satz=satz, gesetz=gesetz, phi=kriechzahl, phi_eigen=phi is not None,
        grenznamen=namen, ids=ids)


# ===========================================================================
# Momenten-Kruemmungs- und Normalkraft-Dehnungs-Linie
# ===========================================================================


@dataclass(frozen=True)
class Linienpunkt:
    """
    Ein Punkt einer Linie: die Kraft -- ``M`` bzw. ``N`` --, die Verformung,
    die dort gilt -- ``chi`` bzw. ``eps_m`` --, und beide Zustaende zum
    Vergleich.
    """

    kraft: float
    verformung: float
    """Was gilt: ungerissen bis zum Riss, darueber gerissen."""

    gerissen: bool
    verformung_I: Optional[float]
    """Ungerissen -- ``None``, wenn der Zustand dort keine Loesung hat."""

    verformung_II: Optional[float]
    """Gerissen, ohne Zugfestigkeit des Betons."""


@dataclass(frozen=True)
class Eckpunkt:
    """Ein benannter Punkt einer Linie."""

    kraft: float
    verformung: float


@dataclass(frozen=True)
class Grenzzustand(Eckpunkt):
    """Das Ende einer Linie -- und welche Grenzdehnung es bestimmt."""

    eps_oben: float = 0.0
    eps_unten: float = 0.0
    massgebend: str = ""


@dataclass
class Linie:
    """
    ``M(chi)`` bei festgehaltener Normalkraft oder ``N(eps_m)`` bei
    festgehaltenem Moment -- welche, sagt :attr:`art`.
    """

    art: Analyseart
    fest: float
    """Was festgehalten wird: ``N`` in N oder ``M`` in Nm."""

    riss: float
    """Die Kraft, bei der der Querschnitt reisst: ``M_Riss(N)`` oder ``N_Riss(M)``."""

    punkte: List[Linienpunkt] = field(default_factory=list)
    bruch: Optional[Grenzzustand] = None
    fliessen: Optional[Eckpunkt] = None
    """Wo der Stahl der am staerksten gezogenen Lage zu fliessen beginnt."""

    hinweis: str = ""

    def hinweisen(self, satz: str) -> None:
        """Einen Satz vor die bisherigen Hinweise stellen."""
        self.hinweis = " ".join(filter(None, [satz, self.hinweis]))

    @property
    def tragfaehig(self) -> bool:
        return self.bruch is not None and self.bruch.kraft > 0.0

    @property
    def sprung(self) -> Optional[Tuple[Linienpunkt, Linienpunkt]]:
        """Die beiden Punkte des Risses: vor und nach dem Reissen, bei derselben Kraft."""
        for vor, nach in zip(self.punkte, self.punkte[1:]):
            if not vor.gerissen and nach.gerissen:
                return vor, nach
        return None


@dataclass(frozen=True)
class _Weg:
    """
    Wie eine Linie laeuft -- der einzige Unterschied zwischen M-chi und N-eps.

    ``ebene`` fuehrt von einer Verformung zur gerissenen Ebene ``(eps_m,
    chi)`` oder zu ``None``, wo es kein Gleichgewicht gibt; ``kraft`` liest
    aus der Ebene die Kraft der Linie; ``verformung_bei`` sucht zu einer Kraft
    die Verformung, mit einem der beiden Loeser.
    """

    ebene: Callable[[float], Optional[Tuple[float, float]]]
    kraft: Callable[[Tuple[float, float]], float]
    verformung_bei: Callable[[Querschnittsloeser, float], Optional[float]]
    obergrenze: float
    """Eine Verformung, ueber der es sicher kein Gleichgewicht mehr gibt."""


def _grenze(gut: Callable[[float], bool], unten: float, oben: float) -> float:
    """Wo ``gut`` endet, zwischen ``unten`` (gut) und ``oben`` -- durch Halbieren."""
    if gut(oben):
        return oben
    for _ in range(60):
        if oben - unten <= 1e-12 * max(1.0, abs(oben)):
            break
        mitte = 0.5 * (unten + oben)
        if gut(mitte):
            unten = mitte
        else:
            oben = mitte
    return unten


def _massgebend(paar: Loeserpaar, eps_m: float, chi: float) -> str:
    """Welche Grenzdehnung die Ebene erreicht -- die mit dem kleinsten Abstand."""
    bester, abstand = ("", 0.0), math.inf
    for g, name in zip(paar.gerissen.grenzen.grenzen, paar.grenznamen):
        eps = eps_m + chi * g.arm
        for grenze in (g.eps_min, g.eps_max):
            if math.isfinite(grenze) and abs(eps - grenze) < abstand:
                bester, abstand = (name, grenze), abs(eps - grenze)
    name, grenze = bester
    return f"{name} bei {grenze * 1e3:.2f} ‰".replace("-", "−")


def _linie(paar: Loeserpaar, weg: _Weg, art: Analyseart, fest: float,
           riss: float) -> Linie:
    """
    Die Linie von null bis zum Bruch: ungerissen bis ``riss``, dort der
    Sprung, darueber gerissen -- ueber die Verformung gerechnet, mit dem
    Fliessbeginn als Punkt der Linie.
    """
    linie = Linie(art=art, fest=fest, riss=riss)
    start = weg.verformung_bei(paar.gerissen, 0.0)
    if start is None:
        return linie

    def gut(verformung: float) -> bool:
        return weg.ebene(verformung) is not None

    oben = weg.obergrenze
    while gut(oben) and oben < 1.0:
        oben *= 2.0
    ende = _grenze(gut, start, oben)
    ebene = weg.ebene(ende)
    if ebene is None:
        return linie
    eps_m, chi = ebene
    halb = paar.gerissen.h / 2.0
    linie.bruch = Grenzzustand(
        kraft=weg.kraft(ebene), verformung=ende, eps_oben=eps_m - chi * halb,
        eps_unten=eps_m + chi * halb, massgebend=_massgebend(paar, eps_m, chi))
    kraft_u = linie.bruch.kraft
    if kraft_u <= 0.0:
        return linie

    def kraftpunkte(bis: float) -> List[Linienpunkt]:
        punkte = []
        for i in range(PUNKTE_UNGERISSEN + 1):
            kraft = bis * i / PUNKTE_UNGERISSEN
            v_I = weg.verformung_bei(paar.ungerissen, kraft)
            if v_I is not None:
                punkte.append(Linienpunkt(kraft=kraft, verformung=v_I, gerissen=False,
                                          verformung_I=v_I,
                                          verformung_II=weg.verformung_bei(paar.gerissen, kraft)))
        return punkte

    if riss >= kraft_u:
        # Ungerissen bis zum Bruch: reisst er, traegt er den Riss nicht.
        linie.punkte = kraftpunkte(kraft_u)
        return linie

    arme = [l.z - halb for l in paar.gerissen.lagen]

    def fliesst(verformung: float) -> bool:
        e = weg.ebene(verformung)
        return e is not None and max(e[0] + e[1] * a for a in arme) >= paar.eps_y

    anfang, risskraft = start, None
    if riss > 0.0:
        linie.punkte = kraftpunkte(riss)
        nach_riss = weg.verformung_bei(paar.gerissen, riss)
        if nach_riss is not None:
            anfang, risskraft = nach_riss, riss

    stellen: List[float] = []
    if not fliesst(anfang) and fliesst(ende):
        bei = _grenze(lambda v: not fliesst(v), anfang, ende)
        e = weg.ebene(bei)
        linie.fliessen = Eckpunkt(kraft=weg.kraft(e), verformung=bei)
        vorher = KURVENPUNKTE // 3
        stellen = ([anfang + (bei - anfang) * i / vorher for i in range(vorher)]
                   + [bei + (ende - bei) * i / (KURVENPUNKTE - vorher)
                      for i in range(KURVENPUNKTE - vorher + 1)])
    else:
        stellen = [anfang + (ende - anfang) * i / KURVENPUNKTE for i in range(KURVENPUNKTE + 1)]
        if fliesst(anfang) and riss > 0.0:
            linie.hinweisen("Der Stahl fliesst schon, wenn der Querschnitt reisst.")
        elif not fliesst(ende):
            linie.hinweisen("Bis zum Bruch fliesst kein Stahl: der Beton versagt zuerst.")

    for verformung in stellen:
        e = weg.ebene(verformung)
        if e is None:
            continue
        # Der erste Punkt nach dem Sprung: zu seiner Kraft wurde die
        # Verformung gesucht, also traegt er sie -- genau, nicht bis auf die
        # Schranke der Suche.
        kraft = risskraft if verformung == anfang and risskraft is not None else weg.kraft(e)
        linie.punkte.append(Linienpunkt(
            kraft=kraft, verformung=verformung, gerissen=True,
            verformung_I=weg.verformung_bei(paar.ungerissen, kraft),
            verformung_II=verformung))
    if paar.gesetz == "block":
        linie.hinweisen(
            f"Mit dem Spannungsblock trägt der Beton unter "
            f"{1.0 - BLOCKANTEIL:.2f}·ε_c2d nichts: über dem Riss ist die Linie "
            f"weicher als der Querschnitt, ihr Ende ist der Widerstand mit dem Block.")
    return linie


def moment_kruemmung(paar: Loeserpaar, *, N: float) -> Linie:
    """
    Die Momenten-Kruemmungs-Linie bei der Normalkraft ``N`` (Zug positiv):
    ungerissen bis ``M_Riss(N)``, dort der Sprung, darueber gerissen bis zum
    Bruch.
    """
    gerissen = paar.gerissen

    def ebene(chi: float) -> Optional[Tuple[float, float]]:
        eps_m = gerissen.mitteldehnung(chi, N)
        return None if eps_m is None else (eps_m, chi)

    def verformung_bei(loeser: Querschnittsloeser, M: float) -> Optional[float]:
        e = loeser.loese(N_Ed=N, M_Ed=M)
        return e.chi if e.konvergiert else None

    weg = _Weg(ebene=ebene, kraft=lambda e: gerissen.kraefte(*e).M,
               verformung_bei=verformung_bei,
               obergrenze=gerissen.grenzen.kruemmungsgrenze(positiv=True))
    linie = _linie(paar, weg, Analyseart.MOMENT_KRUEMMUNG, N, paar.rissmoment_bei(N))
    if linie.bruch is None or not linie.tragfaehig:
        linie.hinweis = (
            "Schon ohne Moment gibt es keine Gleichgewichtslage – die "
            "Normalkraft allein übersteigt, was der Querschnitt aufnimmt.")
    elif linie.riss >= linie.bruch.kraft:
        linie.hinweisen(
            "Das Rissmoment liegt über dem Biegewiderstand: bis zum Bruch bleibt "
            "der Querschnitt ungerissen, und reisst er, trägt er das Rissmoment "
            "nicht. Bei N = 0 prüft genau das der Nachweis gegen sprödes Versagen.")
    elif linie.riss <= 0.0:
        linie.hinweisen("Schon die Zugkraft allein reisst den Querschnitt auf: die "
                        "ganze Linie gilt gerissen.")
    return linie


def normalkraft_dehnung(paar: Loeserpaar, *, M: float) -> Linie:
    """
    Die Normalkraft-Dehnungs-Linie beim Moment ``M``, auf Zug: ungerissen
    bis ``N_Riss(M)``, dort der Sprung, darueber gerissen bis zum Bruch.
    Die Dehnung ist die auf halber Hoehe -- dort greift ``N`` an.
    """
    gerissen = paar.gerissen

    def ebene(eps_m: float) -> Optional[Tuple[float, float]]:
        chi = gerissen.kruemmung(eps_m, M)
        return None if chi is None else (eps_m, chi)

    def verformung_bei(loeser: Querschnittsloeser, N: float) -> Optional[float]:
        e = loeser.loese(N_Ed=N, M_Ed=M)
        return e.eps_m if e.konvergiert else None

    obergrenze = max(g.eps_max for g in gerissen.grenzen.grenzen if math.isfinite(g.eps_max))
    weg = _Weg(ebene=ebene, kraft=lambda e: gerissen.kraefte(*e).N,
               verformung_bei=verformung_bei, obergrenze=obergrenze)
    linie = _linie(paar, weg, Analyseart.NORMALKRAFT_DEHNUNG, M, paar.rissnormalkraft_bei(M))
    if linie.bruch is None or not linie.tragfaehig:
        linie.hinweis = (
            "Schon ohne Normalkraft gibt es keine Gleichgewichtslage – das "
            "Moment allein übersteigt, was der Querschnitt aufnimmt.")
    elif linie.riss >= linie.bruch.kraft:
        linie.hinweisen(
            "Die Rissnormalkraft liegt über dem Zugwiderstand: bis zum Bruch bleibt "
            "der Querschnitt ungerissen, und reisst er, trägt er die Rissnormalkraft "
            "nicht.")
    elif linie.riss <= 0.0:
        linie.hinweisen("Schon das Moment allein reisst den Querschnitt auf: die "
                        "ganze Linie gilt gerissen.")
    return linie


# ===========================================================================
# Herleitung -- fuer die Formelsammlung
# ===========================================================================


def _herleitung(p: Protokoll, fall, paar: Loeserpaar, linie: Linie,
                werte: Mapping[str, "Wert"], raum: str) -> None:
    """
    Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
    Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet.
    """
    ab = len(p.bloecke)
    w = Zwischenwerte(f"{raum}.analyse.{re.sub(r'[^0-9A-Za-z]+', '_', fall.name)}")
    momente = linie.art is Analyseart.MOMENT_KRUEMMUNG

    def ein(name: str) -> "Wert":
        return werte[paar.ids[name]]

    p.titel(f"{THEMA}: {fall.name}", raum=raum)
    p.erklaerung(
        "Eine Spannung-Dehnung-Analyse hält nichts gegen etwas: sie zeigt, was "
        "der Querschnitt tut. Gerechnet wird mit dem Faserintegral der Nachweise "
        "und mit der Kriechzahl, dem Wertesatz und dem Betongesetz, die die "
        "Analyse wählt. Ohne eigene Kriechzahl gilt die der Platte.")
    phi = (ein("phi") if "phi" in paar.ids
           else w.zahl("phi", r"\varphi", paar.phi, stellen=2))
    E_c_eff = w.spannung("E_c_eff", "E_{c,eff}", wirksamer_modul(ein("E_cm").groesse.si, paar.phi))
    p.formel(E_c_eff, r"\frac{@E_cm}{1 + @phi}", {"E_cm": ein("E_cm"), "phi": phi},
             titel="Wirksamer Elastizitätsmodul")

    p.erklaerung(
        "Ungerissen (Zustand I) trägt der Beton Druck und Zug, linear mit E_c,eff "
        "und ohne Grenze: gebraucht wird hier die Steifigkeit, und wo der "
        "Querschnitt reisst, sagt die Rissbedingung am Bruttoquerschnitt. Gerissen "
        "(Zustand II) trägt er keinen Zug mehr, und im Druck gilt das gewählte "
        "Betongesetz.")
    p.ansatz(r"\sigma_c = E_{c,eff} \cdot \varepsilon_c",
             titel="Beton ungerissen, in Druck und Zug")
    eps_c1d, eps_c2d = ein("eps_c1d"), ein("eps_c2d")
    if paar.gesetz == "block":
        p.ansatz(Spannungsblock(f_cd=0.0, eps_c2d=eps_c2d.groesse.si).latex(),
                 titel=f"Beton gerissen: Spannungsblock {BLOCKANTEIL}·x")
        p.erklaerung(
            "Der Spannungsblock ist ein Modell für den Bruch: unter "
            "(1 − 0.85)·ε_c2d trägt der Beton darin nichts. Über dem Riss ist die "
            "Linie mit ihm darum weicher als der Querschnitt; ihr Ende ist der "
            "Widerstand mit dem Block.")
    else:
        k_sigma = w.zahl("k_sigma", r"k_{\sigma}", E_c_eff.groesse.si / (400.0 * ein("f_c").groesse.si),
                         stellen=2)
        p.formel(k_sigma, r"\frac{@E_c_eff}{400 \cdot @f_c}",
                 {"E_c_eff": E_c_eff, "f_c": ein("f_c")},
                 titel="Beiwert der Parabel, mit dem wirksamen Modul")
        p.ansatz(Betongesetz(f_cd=0.0, eps_c1d=eps_c1d.groesse.si,
                             eps_c2d=eps_c2d.groesse.si, k_sigma=0.0).latex(),
                 titel="Beton gerissen: Parabel-Rechteck")
    if paar.satz is Werkstoffsatz.CHARAKTERISTISCH:
        p.text("Mit charakteristischen Werten: f_ck statt f_cd, f_yk statt f_yd.")

    h = ein("h")
    if momente:
        p.erklaerung(
            "Am Bruttoquerschnitt reisst der Rand, wenn N/A + M/W = f_ct,eff. Mit "
            "A = b·h und W = b·h²/6 hebt Druck das Rissmoment, Zug senkt es. Beim "
            "Rissmoment springt die Krümmung bei demselben Moment vom ungerissenen "
            "auf den gerissenen Wert.")
        p.formel(w.moment("M_Riss_N", "M_{Riss}(N)", linie.riss),
                 r"@M_Riss - @N \cdot \frac{@h}{6}",
                 {"M_Riss": w.moment("M_Riss", "M_{Riss}", paar.M_Riss),
                  "N": w.kraft("N", "N", linie.fest), "h": h},
                 titel="Rissmoment bei der Normalkraft")
    else:
        p.erklaerung(
            "Dieselbe Rissbedingung, nach der Normalkraft aufgelöst: beim Moment M "
            "reisst der Querschnitt, wenn die Zugkraft N_Riss erreicht. Unter Zug "
            "reisst die ganze Dicke, darum gilt k_t für t = h und nicht für h/3 wie "
            "beim Rissmoment. Bei N_Riss springt die Dehnung bei derselben Kraft vom "
            "ungerissenen auf den gerissenen Wert.")
        f_ct_eff = protokoll_zugfestigkeit(
            p, w, k_t=paar.k_t_zug, f_ct_eff=paar.f_ct_eff_zug, h=h,
            f_ctm=ein("f_ctm"), teiler=1, referenz="SIA 262:2025, 4.4.2")
        p.formel(w.kraft("N_Riss_M", "N_{Riss}(M)", linie.riss),
                 r"@f_ct_eff \cdot @b \cdot @h - \frac{6 \cdot \left|@M\right|}{@h}",
                 {"f_ct_eff": f_ct_eff, "b": ein("b"), "h": h,
                  "M": w.moment("M", "M", linie.fest)},
                 titel="Rissnormalkraft beim Moment")

    p.erklaerung(
        "Der Fliessbeginn ist der Punkt, an dem die am stärksten gezogene Lage die "
        "Fliessdehnung erreicht. Danach wächst die Kraft nur noch wenig: die "
        "Druckzone wird kleiner, der Hebelarm grösser, und der Beton füllt sein "
        "Gesetz, bis eine Grenzdehnung erreicht ist. Im Bild heisst die Kraft beim "
        "Fliessbeginn M_Rd bzw. N_Rd, am Ende M_Rd,u bzw. N_Rd,u; mit "
        "charakteristischen Werten Rk statt Rd.")
    p.formel(w.dehnung("eps_y", r"\varepsilon_{y}", paar.eps_y),
             r"\frac{@f_s}{@E_s}", {"f_s": ein("f_s"), "E_s": ein("E_s")},
             titel="Dehnung bei Fliessbeginn")
    p.erklaerung(
        "Den gerissenen Teil rechnet die Linie über die Verformung, nicht über die "
        "Kraft: zu jeder Krümmung (bei der N-ε-Linie: zu jeder Dehnung) wird die "
        "Ebene gesucht, die die festgehaltene Grösse trägt. Sie endet bei der "
        "grössten Verformung, zu der es noch ein Gleichgewicht gibt – dort ist die "
        "erste Grenzdehnung erreicht. Es sind dieselben Grenzen wie im "
        "Dehnungsfächer der genauen M-N-Linie.")
    p.ansatz(r"\varepsilon_{c,Rand} \ge -\varepsilon_{c2d} \qquad "
             r"-\varepsilon_{ud} \le \varepsilon_{s,i} \le \varepsilon_{ud} \qquad "
             r"\varepsilon\left(z_C\right) \ge -\varepsilon_{c1d}, \quad "
             r"z_C = h \cdot \left(1 - \frac{\varepsilon_{c1d}}{\varepsilon_{c2d}}\right)",
             titel="Grenzdehnungen am Ende der Linie")
    if linie.bruch is not None:
        b = linie.bruch
        oben = w.dehnung("eps_oben", r"\varepsilon_{oben}", b.eps_oben)
        unten = w.dehnung("eps_unten", r"\varepsilon_{unten}", b.eps_unten)
        if momente:
            p.formel(w.kruemmung("chi_u", r"\chi_{u}", b.verformung),
                     r"\frac{@eps_unten - @eps_oben}{@h}",
                     {"eps_unten": unten, "eps_oben": oben, "h": h},
                     titel="Grösste Krümmung")
        else:
            p.formel(w.dehnung("eps_mu", r"\varepsilon_{m,u}", b.verformung),
                     r"\frac{@eps_oben + @eps_unten}{2}",
                     {"eps_oben": oben, "eps_unten": unten},
                     titel="Grösste Dehnung auf halber Höhe")
        p.text(f"Massgebend: {b.massgebend}.")
    p.herkunft_stempeln(THEMA, ab=ab)


# ===========================================================================
# Die Analysen einer Platte
# ===========================================================================


@dataclass
class Analyse:
    """Ein Spannungsfall der Beschreibung -- und was die Auswertung ergab."""

    fall: Any
    """Der :class:`SpannungsfallEintrag`, wie er in der Beschreibung steht."""

    art: Analyseart
    richtung: Richtung
    h: float = 0.0
    """Plattendicke in m -- fuer das Bild."""

    bild: Optional[Querschnittsbild] = None
    kurve: Optional[Linie] = None
    """Die M-chi- oder N-eps-Linie."""

    paar: Optional[Loeserpaar] = None
    """Womit gerechnet wurde -- Kriechzahl, Wertesatz, Betongesetz."""

    hinweis: str = ""
    """Warum es nichts auszuwerten gab, falls es nichts gab."""

    @property
    def moeglich(self) -> bool:
        return self.bild is not None or self.kurve is not None


def auswerten(fall, art: Analyseart, paar: Loeserpaar) -> Tuple[
        Optional[Querschnittsbild], Optional[Linie]]:
    """Die eine der vier Fragen stellen, die dieser Fall stellt -- in SI."""
    if art is Analyseart.DEHNUNGEN:
        return aus_dehnungen(paar.gerissen, eps_oben=fall.eps_oben / 1e3,
                             eps_unten=fall.eps_unten / 1e3), None
    if art is Analyseart.MOMENT_KRUEMMUNG:
        return None, moment_kruemmung(paar, N=fall.N_Ed * 1e3)
    if art is Analyseart.NORMALKRAFT_DEHNUNG:
        return None, normalkraft_dehnung(paar, M=fall.M_Ed * 1e3)
    return aus_schnittgroessen(paar.gerissen, N=fall.N_Ed * 1e3,
                               M=fall.M_Ed * 1e3), None


def analysen(aufbau: "Aufbau", loesung: "Loesung",
             protokoll: Optional[Protokoll] = None) -> Dict[str, List[Analyse]]:
    """
    Die Auswertungen am Querschnitt, je Platte.

    Kein Nachweis: hier steht kein Erfuellungsgrad und kein Urteil, sondern
    eine Antwort auf die Frage, was im Querschnitt geschieht. Gerechnet wird
    trotzdem mit demselben Faserintegral und denselben Werkstoffgesetzen wie
    in den Nachweisen -- ein zweites Modell daneben waere eine zweite
    Wahrheit ueber denselben Querschnitt.

    Mit ``protokoll`` schreibt jede Linie dorthin, wie sie entstand -- daraus
    sammelt die Formelsammlung ihr Thema.
    """
    p = protokoll if protokoll is not None else StillesProtokoll()

    def wert(kid: str) -> float:
        return loesung.werte[kid].groesse.si

    ergebnis: Dict[str, List[Analyse]] = {}
    for kennung, faelle in aufbau.spannungsfaelle.items():
        querschnitt = aufbau.querschnitte.get(kennung)
        if querschnitt is None:
            continue
        paare: Dict[tuple, Optional[Loeserpaar]] = {}
        liste: List[Analyse] = []
        for fall in faelle:
            try:
                richtung = Richtung(fall.richtung)
            except ValueError:
                richtung = Richtung.X
            satz = Werkstoffsatz(fall.werkstoffsatz)
            schluessel = (richtung, satz, fall.betongesetz, fall.kriechzahl)
            if schluessel not in paare:
                try:
                    paare[schluessel] = loeserpaar(querschnitt, richtung, wert, satz=satz,
                                                   gesetz=fall.betongesetz,
                                                   phi=fall.kriechzahl)
                except KeyError:
                    # Ein Wert dieser Richtung wurde nicht gerechnet -- dann
                    # gibt es fuer sie keinen Querschnitt zum Auswerten.
                    paare[schluessel] = None
            paar = paare[schluessel]
            analyse = Analyse(fall=fall, art=Analyseart(fall.art), richtung=richtung, paar=paar)
            if paar is None:
                analyse.hinweis = (
                    f"In {richtung.beschriftung} liegt keine Bewehrung – ohne "
                    f"sie gibt es keinen Querschnitt zum Auswerten.")
            else:
                analyse.h = paar.gerissen.h
                analyse.bild, analyse.kurve = auswerten(fall, analyse.art, paar)
                if analyse.kurve is not None:
                    _herleitung(p, fall, paar, analyse.kurve, loesung.werte, querschnitt.id)
            liste.append(analyse)
        ergebnis[kennung] = liste
    return ergebnis
