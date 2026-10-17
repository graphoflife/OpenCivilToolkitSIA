"""
opencivil/spannungsanalyse.py -- den Querschnitt ansehen, ohne ihn nachzuweisen.

VERANTWORTUNG:
Sechs Auswertungen am selben Faserintegral, das auch die Nachweise benutzen:

1. **Aus Schnittgroessen** -- ``N`` und ``M`` hinein, Dehnungsebene und
   Spannungsverteilung heraus.
2. **Aus Dehnungen** -- Randdehnungen hinein, Spannungen und Schnittgroessen
   heraus. Die Umkehrung von 1, und ohne Suche: die Ebene steht ja schon da.
3. **Momenten-Kruemmungs-Linie** -- eine Normalkraft hinein, der Verlauf
   ``M(chi)`` von null bis zum Bruch heraus.
4. **Normalkraft-Dehnungs-Linie** -- ein Moment hinein, der Verlauf
   ``N(eps_m)`` von null bis zum Bruch auf Zug heraus.
5. **Aequivalenter E-Modul ueber dem Moment** -- die Linie aus 3,
   umgerechnet in den Modul, den ein reiner, ungerissener, elastischer
   Betonquerschnitt braeuchte, um sich gleich stark zu kruemmen.
6. **Aequivalenter E-Modul ueber der Normalkraft** -- dasselbe aus der
   Linie in 4, fuer die Dehnung.

KEIN NACHWEIS:
Hier wird nichts gegen etwas gehalten. Es gibt keinen Erfuellungsgrad und kein
Urteil -- das ist der Unterschied zu allem anderen in diesem Werkzeug und der
Grund, warum die Auswertungen nicht im :class:`Rechenwerk` stehen. Sie
beantworten eine Frage, die man beim Entwerfen stellt: *was passiert
eigentlich im Querschnitt?*

JE ANALYSE GEWAEHLT:
Jede Analyse (:class:`~opencivil.projekt.SpannungsfallEintrag`) waehlt als
:class:`~opencivil.nachweis.rechenwahl.Rechenwahl`

* die Kriechzahl;
* der Wertesatz -- Bemessung (``f_cd``, ``f_yd``) oder charakteristisch
  (``f_ck``, ``f_yk``), siehe :class:`Werkstoffsatz`;
* die Rechenart -- die 0.85·x-Vereinfachung oder praezise ohne Vereinfachung,
  die Parabel mit ``E_c,eff``. Die Handrechnung gibt es hier nicht
  (:data:`~opencivil.nachweis.rechenwahl.FASERARTEN`): eine Linie rechnet die
  Normalkraft Ebene fuer Ebene genau, ein Polygon aus Eckpunkten haette dort
  nichts zu suchen.

Moduln und Grenzdehnungen sind in beiden Wertesaetzen dieselben, wie ueberall
im Werkzeug.

DIE BEIDEN LINIEN:
Unter dem Riss ist der Querschnitt ungerissen (Zustand I) und deutlich
steifer, als die Nachweise ihn rechnen -- dort wird der Beton auf Zug
grundsaetzlich nicht angesetzt. Beim Riss springt die Verformung bei
derselben Kraft vom ungerissenen auf den gerissenen Wert (Zustand II), im
Bild ein waagrechtes Stueck. Darueber gilt Zustand II bis zum Bruch. Beide
Zustaende rechnet derselbe Loeser, nur mit verschiedenem Betongesetz.

Die Zugfestigkeit des Betons zaehlt nur bis zum Riss: der ungerissene
Zustand steht zum Vergleich darum nur bis ``M_Riss`` bzw. ``N_Riss`` da,
nicht darueber hinaus -- dort haette der Beton Zug ohne Grenze (Benutzer,
2026-10-12). Der gerissene Zustand steht zum Vergleich auf der ganzen Linie.

DIE NAMEN AN DER LINIE:
Ihr Ende heisst ``M_Rd`` bzw. ``N_Rd`` (``R_k`` mit charakteristischen
Werten), wie der Widerstand der Tragsicherheit: bei derselben Rechenwahl ist
es dieselbe Zahl, bis auf die Schranke der Suche. Der Fliessbeginn heisst
``M_y`` bzw. ``N_y``, wie seine Kruemmung ``chi_y``. Bis 2026-10-12 hiess er
``M_Rd`` und das Ende ``M_Rd,u`` -- und wer im Bild nach dem Widerstand
suchte, fand den Fliessbeginn.

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
eine Linie des Bauteils zu rechnen waere, ist offen
(``notizbuch/Notizen/TODO.md``).

PLATTE UND GEZEICHNETER QUERSCHNITT:
Die Fragen selbst -- Bild, Linie, Modul -- kennen nur einen
:class:`~opencivil.nachweis.querschnittsloeser.Faserloeser` und ein Paar
daraus: gerissen und ungerissen, dazu Riss, Bezugsflaeche des Moduls und
Rechenwahl. Hier steht das Paar der Platte (:class:`Loeserpaar`); das des
gezeichneten Querschnitts, je Zugseite, steht in
:mod:`opencivil.querschnitt.schnittanalyse`.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Tuple, Union,
)

from opencivil.core.einheiten import MIO_MM4, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll, StillesProtokoll, Zwischenwerte
from opencivil.core.wahl import Wahl
from opencivil.core.wert import kennung_aus
from opencivil.nachweis import dehnungsfaecher
from opencivil.material.basis import mit_index
from opencivil.nachweis.querschnittsloeser import (
    Ebene, Faserloeser, Querschnittsloeser, Werkstoffsatz, wirksamer_modul,
)
from opencivil.nachweis.rechenwahl import (
    Betonkennwerte, Rechenart, Rechenwahl, betongesetz, gesetze, stahllagen, staehle,
)
from opencivil.nachweis.sproedes_versagen import (
    beiwert_dicke, protokoll_zugfestigkeit, rissmoment,
)
from opencivil.querschnitt.platte import Richtung
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.querschnitt.werkstoffgesetz import (
    BLOCKANTEIL, K_SIGMA_LATEX, K_SIGMA_SEITE, RUNDUNG, BetonUngerissen,
)

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


class Analyseart(Wahl):
    """Welche der sechs Fragen gestellt wird."""

    SCHNITTGROESSEN = "schnittgroessen"
    DEHNUNGEN = "dehnungen"
    MOMENT_KRUEMMUNG = "moment_kruemmung"
    NORMALKRAFT_DEHNUNG = "normalkraft_dehnung"
    MOMENT_EMODUL = "moment_emodul"
    NORMALKRAFT_EMODUL = "normalkraft_emodul"

    @property
    def beschriftung(self) -> str:
        return {
            Analyseart.SCHNITTGROESSEN: "Aus N und M",
            Analyseart.DEHNUNGEN: "Aus Randdehnungen",
            Analyseart.MOMENT_KRUEMMUNG: "Momenten-Krümmungs-Linie",
            Analyseart.NORMALKRAFT_DEHNUNG: "Normalkraft-Dehnungs-Linie",
            Analyseart.MOMENT_EMODUL: "Äquivalenter E-Modul über dem Moment",
            Analyseart.NORMALKRAFT_EMODUL: "Äquivalenter E-Modul über der Normalkraft",
        }[self]

    @property
    def kurz(self) -> str:
        """Fuer die Auswahl in der Zeile."""
        return {
            Analyseart.SCHNITTGROESSEN: "N, M",
            Analyseart.DEHNUNGEN: "ε oben/unten",
            Analyseart.MOMENT_KRUEMMUNG: "M–χ",
            Analyseart.NORMALKRAFT_DEHNUNG: "N–ε",
            Analyseart.MOMENT_EMODUL: "M–E_eq",
            Analyseart.NORMALKRAFT_EMODUL: "N–E_eq",
        }[self]

    @property
    def linie(self) -> Optional["Analyseart"]:
        """
        Die Linie, auf der diese Frage laeuft: M-chi oder N-eps -- der Modul
        ist dieselbe Linie, umgerechnet. ``None`` fuer die beiden Bilder.
        """
        return {
            Analyseart.MOMENT_KRUEMMUNG: Analyseart.MOMENT_KRUEMMUNG,
            Analyseart.MOMENT_EMODUL: Analyseart.MOMENT_KRUEMMUNG,
            Analyseart.NORMALKRAFT_DEHNUNG: Analyseart.NORMALKRAFT_DEHNUNG,
            Analyseart.NORMALKRAFT_EMODUL: Analyseart.NORMALKRAFT_DEHNUNG,
        }.get(self)

    @property
    def modul(self) -> bool:
        """Ob gefragt ist, welchen E-Modul ein reiner Betonquerschnitt braeuchte."""
        return self in (Analyseart.MOMENT_EMODUL, Analyseart.NORMALKRAFT_EMODUL)


# ===========================================================================
# Das Bild eines Querschnitts
# ===========================================================================

@dataclass(frozen=True)
class Faserpunkt:
    """Eine Stelle ueber die Hoehe, mit dem, was dort geschieht."""

    z: float
    """
    Abstand vom **oberen Rand**, in m -- dem gedrueckten bei positivem Moment.

    Dieselbe Achse, die der Loeser und der Lagenaufbau benutzen. Fuer eine
    Platte ist es die Oberkante: die 1. Lage liegt bei ``z = h -
    Randabstand`` und die 4. bei ``z = Randabstand``. Wer hier umdrehte,
    bekaeme ein Bild, das zum Nachweis nicht passt. Beim gezeichneten
    Querschnitt der Rand gegenueber der Zugseite.
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

    name: str = ""
    """Wie die Lage heisst -- «2. Lage Grundbewehrung», «Linie 1»."""


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


def _bild(loeser: Faserloeser, eps_m: float, chi: float) -> Querschnittsbild:
    """Dehnungen und Spannungen zu einer gegebenen Ebene -- ohne jede Suche."""
    kraefte = loeser.kraefte(eps_m, chi)
    oben = loeser.oben

    beton = []
    for i in range(STUETZSTELLEN):
        z = loeser.h * i / (STUETZSTELLEN - 1)    # von oben nach unten
        eps = eps_m + chi * (z + oben)
        beton.append(Faserpunkt(z=z, eps=eps, sigma=loeser.betonspannung(z + oben, eps)))

    stahl = []
    for lage, stab in zip(loeser.lagen, loeser.querschnitt.staebe):
        eps = eps_m + chi * (lage.z + oben)
        sigma = stab.gesetz(eps)
        stahl.append(Stahlpunkt(z=lage.z, eps=eps, sigma=sigma,
                                nummer=lage.nummer, a_s=lage.a_s,
                                kraft=sigma * lage.a_s, name=lage.text))

    return Querschnittsbild(eps_m=eps_m, chi=chi, N=kraefte.N, M=kraefte.M,
                            beton=beton, stahl=stahl)


def aus_schnittgroessen(loeser: Faserloeser, *, N: float, M: float,
                        art: Rechenart) -> Querschnittsbild:
    """
    Die Dehnungsebene zu ``N`` und ``M``, samt allem, was darauf steht.

    Gesucht wird mit demselben Verfahren wie in den Nachweisen. Findet sich
    keine Ebene, kommt das Bild leer zurueck und sagt warum -- geraten wird
    nicht. Verfehlt die Suche ihre Ebene, sagt es die Rechenart ``art``
    (:attr:`Rechenart.ohne_ebene`).
    """
    ebene = loeser.loese(N_Ed=N, M_Ed=M)
    if not ebene.konvergiert:
        return Querschnittsbild(
            eps_m=0.0, chi=0.0, N=N, M=M, konvergiert=False,
            hinweis=(art.ohne_ebene if ebene.verfehlt else
                     "Zu dieser Kombination gibt es keine Gleichgewichtslage: "
                     "der Querschnitt nimmt sie nicht auf."))
    return _bild(loeser, ebene.eps_m, ebene.chi)


def aus_dehnungen(loeser: Faserloeser, *,
                  eps_oben: float, eps_unten: float) -> Querschnittsbild:
    """
    Der umgekehrte Weg: die Ebene ist gegeben, gesucht sind die Kraefte.

    Hier gibt es nichts zu suchen -- aus den beiden Randdehnungen folgen
    Mitteldehnung und Kruemmung unmittelbar, und das Faserintegral liefert
    Normalkraft und Moment in einem Durchgang.
    """
    # z laeuft vom oberen Rand nach unten, also ist die Randdehnung unten die
    # bei z = h und die obere die bei z = 0. Die Mitteldehnung gilt am Arm
    # null: bei der Platte auf halber Hoehe, beim gezeichneten Querschnitt im
    # Schwerpunkt.
    chi = (eps_unten - eps_oben) / loeser.h if loeser.h > 0 else 0.0
    eps_m = eps_oben - chi * loeser.oben
    bild = _bild(loeser, eps_m, chi)
    # Druck und Zug je gegen ihre eigene Grenze: −5 ‰ liegt jenseits des
    # Betons, auch wenn der Stahl bis 45 ‰ reicht. Bis 2026-10-16 stand hier
    # das Groessere der beiden, und der Hinweis blieb aus.
    if (min(eps_oben, eps_unten) < -(loeser.eps_druck + RUNDUNG)
            or max(eps_oben, eps_unten) > loeser.eps_zug + RUNDUNG):
        bild.hinweis = (
            f"Die Randdehnung liegt ausserhalb dessen, wofür die "
            f"Werkstoffgesetze gelten (−{loeser.eps_druck * 1e3:.1f} ‰ bis "
            f"+{loeser.eps_zug * 1e3:.1f} ‰). Jenseits davon geben sie null "
            f"zurück, und die Spannungen unten sind keine Aussage mehr.")
    return bild


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
               *, wahl: Rechenwahl = Rechenwahl(art=Rechenart.PARABEL),
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
    E_c_eff = wirksamer_modul(wert(ids["E_cm"]), wahl.kriechzahl)
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
    ungerissen = g.loeser(h=h, b=b, lagen=lagen, beton=BetonUngerissen(E_c=E_c_eff),
                          **fenster)
    f_ctm = wert(ids["f_ctm"])
    k_t_zug = beiwert_dicke(h)
    return Loeserpaar(
        gerissen=gerissen, ungerissen=ungerissen,
        M_Riss=rissmoment(h=h, b=b, f_ctm=f_ctm).M_Riss,
        k_t_zug=k_t_zug, f_ct_eff_zug=k_t_zug * f_ctm,
        staehle=tuple(staehle(posten)),
        wahl=wahl, grenznamen=namen, ids=ids, E_cm=w.E_cm)


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
    """
    Ungerissen -- ``None`` ueber dem Riss, wo der Beton dafuer Zug ohne
    Grenze braeuchte, und wo der Zustand keine Loesung hat.
    """

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
    verformung_bei: Callable[[Faserloeser, float], Optional[float]]
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
    g = paar.gerissen
    linie.bruch = Grenzzustand(
        kraft=weg.kraft(ebene), verformung=ende, eps_oben=eps_m + chi * g.oben,
        eps_unten=eps_m + chi * g.unten, massgebend=_massgebend(paar, eps_m, chi))
    kraft_u = linie.bruch.kraft
    if kraft_u <= 0.0:
        return linie

    def kraftpunkte(bis: float) -> List[Linienpunkt]:
        punkte = []
        for i in range(PUNKTE_UNGERISSEN + 1):
            # Der letzte genau bei ``bis``: bis * 10 / 10 liegt sonst eine
            # Rundung darueber, beim Riss also schon jenseits des Risses.
            kraft = bis if i == PUNKTE_UNGERISSEN else bis * i / PUNKTE_UNGERISSEN
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

    arme = [(l.z + g.oben, l.stahl.eps_yd) for l in g.lagen]

    def fliesst(verformung: float) -> bool:
        # Jede Lage an der Fliessdehnung ihres eigenen Stahls.
        e = weg.ebene(verformung)
        return e is not None and any(e[0] + e[1] * a >= eps_y for a, eps_y in arme)

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
        # Ungerissen nur bis zum Riss: darueber haette der Beton Zug ohne
        # Grenze. Der erste Punkt nach dem Sprung traegt genau die Risskraft.
        linie.punkte.append(Linienpunkt(
            kraft=kraft, verformung=verformung, gerissen=True,
            verformung_I=(weg.verformung_bei(paar.ungerissen, kraft)
                          if kraft <= riss else None),
            verformung_II=verformung))
    if paar.wahl.art.mit_block:
        linie.hinweisen(
            f"Mit der {BLOCKANTEIL}·x-Vereinfachung trägt der Beton unter "
            f"{1.0 - BLOCKANTEIL:.2f}·ε_c2d nichts: über dem Riss ist die Linie "
            f"weicher als der Querschnitt, ihr Ende ist der Widerstand der "
            f"Vereinfachung. Die Kriechzahl wirkt bei ihr nur auf den "
            f"ungerissenen Teil.")
    return linie


def _durchlaufen(e: Ebene) -> bool:
    """
    Ob eine Linie die Ebene nimmt: gefunden -- oder verfehlt an einem Sprung
    des Spannungsblocks (:attr:`Ebene.verfehlt`). Eine Linie fragt nach der
    Verformung, bei der ihre Kraft einen Wert durchlaeuft; am Sprung ist das
    seine Stelle, auch wenn dort keine Ebene die Kraft genau erzeugt. Ein
    Nachweis dagegen braucht die Ebene selbst.
    """
    return e.konvergiert or e.verfehlt


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

    def verformung_bei(loeser: Faserloeser, M: float) -> Optional[float]:
        e = loeser.loese(N_Ed=N, M_Ed=M)
        return e.chi if _durchlaufen(e) else None

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
    Die Dehnung ist die am Arm null -- dort greift ``N`` an: bei der Platte
    auf halber Hoehe, beim gezeichneten Querschnitt im Schwerpunkt.
    """
    gerissen = paar.gerissen

    def ebene(eps_m: float) -> Optional[Tuple[float, float]]:
        chi = gerissen.kruemmung(eps_m, M)
        return None if chi is None else (eps_m, chi)

    def verformung_bei(loeser: Faserloeser, N: float) -> Optional[float]:
        e = loeser.loese(N_Ed=N, M_Ed=M)
        return e.eps_m if _durchlaufen(e) else None

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
# Der aequivalente E-Modul
# ===========================================================================

#: Unter diesem Anteil der groessten Kraft der Linie gilt eine Kraft als null --
#: der erste Punkt einer gerissen beginnenden Linie traegt null bis auf die
#: Schranke des Loesers.
NULLKRAFT = 1e-6


@dataclass(frozen=True)
class Modulpunkt:
    """
    Ein Punkt der Linie des aequivalenten Moduls: die laufende Kraft und der
    Modul, der dort gilt -- dazu beide Zustaende zum Vergleich, wie bei der
    Linie, aus der er stammt.
    """

    kraft: float
    modul: Optional[float]
    """In Pa; ``None``, wo er nichts sagt."""

    gerissen: bool
    modul_I: Optional[float]
    modul_II: Optional[float]


@dataclass
class Modullinie:
    """
    Der aequivalente E-Modul ueber dem Moment oder ueber der Normalkraft.

    Der Modul, den ein reiner Betonquerschnitt braeuchte -- ungerissen, ohne
    Stahl, elastisch --, um sich unter der laufenden Kraft gleich stark zu
    kruemmen bzw. zu dehnen wie der bewehrte Querschnitt::

        E_eq = M / (I_c · (chi - chi_0))       I_c = b·h³/12
        E_eq = N / (A_c · (eps_m - eps_0))     A_c = b·h

    Gezaehlt wird ab dem Zustand ohne laufende Kraft -- ``chi_0`` bei M = 0
    unter der festen Normalkraft, ``eps_0`` bei N = 0 unter dem festen
    Moment --, nach Vorgabe (2026-10-11). Was die festgehaltene Kraft allein
    verformt, kann ein gerader, ungerissener Betonquerschnitt nicht abbilden:
    bei unsymmetrischer Bewehrung kruemmt schon eine Normalkraft, und ein
    gerissener Querschnitt dehnt sich schon unter dem Moment allein. Ab null
    gezaehlt, ergaebe das nahe null Ausreisser -- am Beispiel bei M = 30 kNm
    und N = 16 kN 99 500 N/mm², fast das Dreifache von E_cm. Ist die feste
    Kraft null, ist es genau ``M = E·I·chi`` bzw. ``N = E·A·eps``.

    Umgerechnet wird jeder Punkt der :class:`Linie`; gerechnet wird nichts
    Neues. So kann diese Linie nichts anderes zeigen als die M-chi- oder
    N-eps-Linie daneben.
    """

    art: Analyseart
    linie: Linie
    """Die M-chi- oder N-eps-Linie, aus der umgerechnet wird."""

    bezug: float
    """``I_c`` in m⁴ bzw. ``A_c`` in m² -- der reine Betonquerschnitt."""

    null: float
    """Die Verformung ohne laufende Kraft: ``chi_0`` bzw. ``eps_0``."""

    E_cm: float
    """Zum Vergleich: ``E_eq/E_cm`` ist der Faktor, um den man E_cm abmindert."""

    punkte: List[Modulpunkt] = field(default_factory=list)

    def modul(self, kraft: float, verformung: float) -> Optional[float]:
        """``Kraft / (Bezug · (Verformung − null))`` -- ``None``, wo das nichts sagt."""
        aenderung = verformung - self.null
        if kraft == 0.0 or aenderung == 0.0:
            return None
        return kraft / (self.bezug * aenderung)

    @property
    def ungerissen(self) -> Optional[float]:
        """Der Modul des ungerissenen Teils -- dort ist der Querschnitt linear."""
        return next((p.modul for p in reversed(self.punkte)
                     if not p.gerissen and p.modul is not None), None)

    @property
    def riss(self) -> Optional[float]:
        """Der Modul gleich nach dem Riss, bei derselben Kraft."""
        sprung = self.linie.sprung
        return None if sprung is None else self.modul(sprung[1].kraft, sprung[1].verformung)

    @property
    def fliessen(self) -> Optional[float]:
        f = self.linie.fliessen
        return None if f is None else self.modul(f.kraft, f.verformung)

    @property
    def ende(self) -> Optional[float]:
        """Der Modul am Ende der Linie -- beim Bruch, oder ungerissen, wenn sie es bleibt."""
        return next((p.modul for p in reversed(self.punkte) if p.modul is not None), None)


def aequivalenter_modul(linie: Linie, *, I_c: float, A_c: float, E_cm: float) -> Modullinie:
    """
    Die M-chi- oder N-eps-Linie als Linie des aequivalenten Moduls -- siehe
    :class:`Modullinie`. Beide Vergleichszustaende zaehlen ab ihrer eigenen
    Verformung ohne laufende Kraft. ``I_c`` und ``A_c`` sind der reine
    Betonquerschnitt, an dem sich der Modul misst.
    """
    momente = linie.art is Analyseart.MOMENT_KRUEMMUNG
    art = Analyseart.MOMENT_EMODUL if momente else Analyseart.NORMALKRAFT_EMODUL
    bezug = I_c if momente else A_c
    if not linie.punkte:
        return Modullinie(art, linie, bezug, 0.0, E_cm)

    # Der erste Punkt ist der Zustand ohne laufende Kraft -- ungerissen bei
    # null, oder gerissen bis auf die Schranke des Loesers.
    massstab = max(abs(p.kraft) for p in linie.punkte) or 1.0
    erster = linie.punkte[0]
    ohne = abs(erster.kraft) <= NULLKRAFT * massstab
    null, null_I, null_II = ((erster.verformung, erster.verformung_I, erster.verformung_II)
                             if ohne else (0.0, 0.0, 0.0))
    modul = Modullinie(art, linie, bezug, null, E_cm)

    def geteilt(kraft: float, verformung: Optional[float],
                ab: Optional[float]) -> Optional[float]:
        if verformung is None or ab is None or kraft == 0.0 or verformung == ab:
            return None
        return kraft / (bezug * (verformung - ab))

    for p in (linie.punkte[1:] if ohne else linie.punkte):
        modul.punkte.append(Modulpunkt(
            kraft=p.kraft, modul=geteilt(p.kraft, p.verformung, null), gerissen=p.gerissen,
            modul_I=geteilt(p.kraft, p.verformung_I, null_I),
            modul_II=geteilt(p.kraft, p.verformung_II, null_II)))

    # Bei null ist der Modul null durch null. Ungerissen ist der Querschnitt
    # linear: dort gilt der Wert des naechsten Punkts genau, und die Linie
    # beginnt bei null statt beim ersten Schritt.
    if ohne and not erster.gerissen and modul.punkte and not modul.punkte[0].gerissen:
        naechster = modul.punkte[0]
        modul.punkte.insert(0, Modulpunkt(
            kraft=0.0, modul=naechster.modul, gerissen=False,
            modul_I=naechster.modul_I, modul_II=naechster.modul_II))
    return modul


# ===========================================================================
# Herleitung -- fuer die Formelsammlung
# ===========================================================================


def herleitung(p: Protokoll, fall, paar, linie: Linie,
                werte: Mapping[str, "Wert"], raum: str,
                modul: Optional[Modullinie] = None) -> None:
    """
    Wie die Linie entstand -- mit den Zahlen dieses Falls, und ohne sie in der
    Formelsammlung, die daraus «Spannung-Dehnung-Analyse» bildet. Mit
    ``modul`` dazu, wie aus ihr der aequivalente E-Modul wird.

    ``paar`` ist das Loeserpaar einer Platte oder eines gezeichneten
    Querschnitts. Was nur die Art des Bauteils weiss -- die Tiefe, der Riss,
    die Dehnung am Ende, der reine Betonquerschnitt --, schreibt es selbst
    (``tiefe``, ``herleitung_riss``, ``herleitung_dehnung_am_ende``,
    ``herleitung_bezug``); der Rest ist derselbe Text.
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
        "und mit der Kriechzahl, dem Wertesatz und der Rechenart, die die "
        "Analyse wählt.")
    wahl = paar.wahl
    phi = w.zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
    E_c_eff = w.spannung("E_c_eff", "E_{c,eff}",
                         wirksamer_modul(ein("E_cm").groesse.si, wahl.kriechzahl))
    p.formel(E_c_eff, r"\frac{@E_cm}{1 + @phi}", {"E_cm": ein("E_cm"), "phi": phi},
             titel="Wirksamer Elastizitätsmodul")

    p.erklaerung(
        "Ungerissen (Zustand I) trägt der Beton Druck und Zug, linear mit E_c,eff "
        "– bis zum Riss: wo der Querschnitt reisst, sagt die Rissbedingung am "
        "Bruttoquerschnitt, und nur dort zählt die Zugfestigkeit. Darüber gilt "
        "der ungerissene Zustand nicht mehr, auch nicht zum Vergleich. Gerissen "
        "(Zustand II) trägt der Beton keinen Zug, und im Druck gilt das Gesetz der "
        "gewählten Rechenart.")
    # Die Gesetze, wie die Loeser sie rechnen -- aus derselben Stelle
    # (:func:`~opencivil.nachweis.rechenwahl.betongesetz`); sie schreiben sich selbst.
    ungerissen = BetonUngerissen(E_c=E_c_eff.groesse.si)
    f_c = ein("f_c")
    gerissen = betongesetz(wahl, f_c=f_c.groesse.si, E_cm=ein("E_cm").groesse.si,
                           eps_c1d=ein("eps_c1d").groesse.si, eps_c2d=ein("eps_c2d").groesse.si)
    p.ansatz(ungerissen.latex(), titel="Beton ungerissen, in Druck und Zug",
             name=ungerissen.seite)
    if wahl.art.mit_block:
        p.ansatz(gerissen.latex(f_c.symbol),
                 titel=f"Beton gerissen: Spannungsblock {BLOCKANTEIL}·x", name=gerissen.seite)
        p.erklaerung(
            "Der Spannungsblock ist ein Modell für den Bruch: unter "
            "(1 − 0.85)·ε_c2d trägt der Beton darin nichts. Über dem Riss ist die "
            "Linie mit ihm darum weicher als der Querschnitt; ihr Ende ist der "
            "Widerstand der 0.85·x-Vereinfachung. Ein Modul hängt an ihm nicht: "
            "die Kriechzahl wirkt nur auf den ungerissenen Teil.")
    else:
        k = w.zahl("k_sigma", r"k_{\sigma}", gerissen.k_sigma, stellen=2)
        p.formel(k, K_SIGMA_LATEX, {"E_c": E_c_eff, "f_c": f_c},
                 titel="Beiwert der Parabel, mit dem wirksamen Modul", name=K_SIGMA_SEITE)
        p.erklaerung(
            "Unter 1 rechnet die Parabel k_σ nicht: dort hätte ihr Nenner im "
            "ansteigenden Ast eine Nullstelle. So weit kommt es mit dem kriechweichen "
            "Modul und charakteristischen Werten; mit k_σ = 1 ist der Beton bis f_c "
            "bei ε_c1d linear.")
        p.ansatz(gerissen.latex(f_c.symbol), titel="Beton gerissen: Parabel-Rechteck",
                 name=gerissen.seite)
    if wahl.satz is Werkstoffsatz.CHARAKTERISTISCH:
        p.text("Mit charakteristischen Werten: f_ck statt f_cd, f_yk statt f_yd.")

    h = paar.tiefe(w, ein)
    paar.herleitung_riss(p, w, linie, ein, h)

    p.erklaerung(
        "Der Fliessbeginn ist der Punkt, an dem die am stärksten gezogene Lage die "
        "Fliessdehnung erreicht. Danach wächst die Kraft nur noch wenig: die "
        "Druckzone wird kleiner, der Hebelarm grösser, und der Beton füllt sein "
        "Gesetz, bis eine Grenzdehnung erreicht ist. Im Bild heisst die Kraft beim "
        "Fliessbeginn M_y bzw. N_y, am Ende M_Rd bzw. N_Rd – mit "
        "charakteristischen Werten Rk statt Rd. Das Ende ist der Widerstand der "
        "Tragsicherheit, wenn sie dieselbe Rechenwahl trifft.")
    # Je Stahl seine Fliessdehnung -- unten und oben duerfen verschiedene liegen.
    for stahl in paar.staehle:
        f_s, E_s = werte[stahl.id_von(wahl.satz.stahl)], werte[stahl.id_von("E_s")]
        name, symbol = (("eps_y", r"\varepsilon_{y}") if len(paar.staehle) == 1 else
                        (f"eps_y_{kennung_aus(stahl.id)}",
                         mit_index(r"\varepsilon_{y}", stahl.symbol_index)))
        p.formel(w.dehnung(name, symbol, f_s.groesse.si / E_s.groesse.si),
                 r"\frac{@f_s}{@E_s}", {"f_s": f_s, "E_s": E_s},
                 titel="Dehnung bei Fliessbeginn", name=FLIESSDEHNUNG)
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
            paar.herleitung_dehnung_am_ende(p, w, b, oben, unten)
        p.text(f"Massgebend: {b.massgebend}.")
    if modul is not None:
        _herleitung_modul(p, w, modul,
                          bezug=lambda: paar.herleitung_bezug(p, w, momente, ein, h),
                          bezugsort=paar.bezugsort)
    p.herkunft_stempeln(THEMA, ab=ab)


def _herleitung_modul(p: Protokoll, w: Zwischenwerte, modul: Modullinie, *,
                      bezug: Callable[[], "Wert"], bezugsort: str) -> None:
    """
    Der aequivalente Modul: der reine Betonquerschnitt, die Formel und der
    Modul an den Ecken der Linie -- jede Zeile mit Kraft und Verformung, also
    von Hand nachzurechnen. ``bezug`` schreibt den reinen Betonquerschnitt
    hin, wie ihn die Art des Bauteils kennt, und gibt ihn zurueck;
    ``bezugsort`` sagt, wo die Mitteldehnung gilt.
    """
    momente = modul.art is Analyseart.MOMENT_EMODUL
    p.erklaerung(
        "Der äquivalente E-Modul ist der Modul, den ein reiner Betonquerschnitt "
        "bräuchte – ungerissen, ohne Stahl, elastisch –, um sich unter der laufenden "
        "Kraft gleich stark zu verformen wie der bewehrte Querschnitt. Gezählt wird "
        "ab dem Zustand ohne laufende Kraft: was die festgehaltene Kraft allein "
        "verformt, kann ein solcher Querschnitt nicht abbilden. Ist sie null, ist es "
        "genau M = E·I·χ bzw. N = E·A·ε.")
    if momente:
        bezug()
        p.ansatz(r"E_{eq} = \frac{M}{I_c \cdot \left(\chi - \chi_0\right)}",
                 titel="Äquivalenter E-Modul über dem Moment")
        p.wert(w.kruemmung("chi_0", r"\chi_0", modul.null),
               titel="Krümmung ohne Moment, unter der festen Normalkraft")
        kopf = [Mathe(r"M\ [\mathrm{kNm}]"), Mathe(r"\chi - \chi_0\ [\mathrm{m}^{-1}]")]
        verformung = lambda v: f"{v - modul.null:.5f}"
    else:
        bezug()
        p.ansatz(r"E_{eq} = \frac{N}{A_c \cdot \left(\varepsilon_m - \varepsilon_0\right)}",
                 titel="Äquivalenter E-Modul über der Normalkraft")
        p.wert(w.dehnung("eps_0", r"\varepsilon_0", modul.null, stellen=4),
               titel=f"Dehnung {bezugsort} ohne Normalkraft, unter dem festen Moment")
        kopf = [Mathe(r"N\ [\mathrm{kN}]"), Mathe(r"\varepsilon_m - \varepsilon_0\ [‰]")]
        verformung = lambda v: f"{(v - modul.null) * 1e3:.4f}"

    linie = modul.linie
    ecken: List[Tuple[str, float, float]] = []
    if linie.sprung is not None:
        vor, nach = linie.sprung
        ecken += [("ungerissen, beim Riss", vor.kraft, vor.verformung),
                  ("gerissen, beim Riss", nach.kraft, nach.verformung)]
    elif linie.punkte and not linie.punkte[-1].gerissen:
        ecken.append(("ungerissen", linie.punkte[-1].kraft, linie.punkte[-1].verformung))
    if linie.fliessen is not None:
        ecken.append(("Fliessbeginn", linie.fliessen.kraft, linie.fliessen.verformung))
    if linie.punkte and linie.punkte[-1].gerissen:
        ecken.append(("Ende", linie.punkte[-1].kraft, linie.punkte[-1].verformung))
    zeilen = []
    for name, kraft, v in ecken:
        E = modul.modul(kraft, v)
        if E is None:
            continue
        zeilen.append([name, Mathe(f"{kraft / 1e3:.1f}"), Mathe(verformung(v)),
                       Mathe(f"{E / 1e6:.0f}"), Mathe(f"{E / modul.E_cm:.3f}")])
    if zeilen:
        p.tabelle(kopf=["Punkt", *kopf, Mathe(r"E_{eq}\ [\mathrm{N/mm^2}]"),
                        Mathe(r"E_{eq}/E_{cm}")],
                  zeilen=zeilen, titel="Der äquivalente Modul an den Ecken der Linie",
                  ausrichtung="lrrrr")


# ===========================================================================
# Die Analysen einer Platte
# ===========================================================================


@dataclass
class Analyse:
    """Ein Spannungsfall der Beschreibung -- und was die Auswertung ergab."""

    fall: Any
    """Der :class:`SpannungsfallEintrag`, wie er in der Beschreibung steht."""

    art: Analyseart
    richtung: Any
    """Die Tragrichtung einer Platte (:class:`Richtung`) oder die Zugseite eines
    gezeichneten Querschnitts (:class:`~opencivil.querschnitt.schnittanalyse.Zugseite`)."""

    richtung_text: str = ""
    """Wie sie neben dem Titel steht -- «x», «Zug unten»."""

    h: float = 0.0
    """Die Tiefe in m -- fuer das Bild: die Dicke der Platte, beim gezeichneten
    Querschnitt die Ausdehnung des Betons in Zugrichtung."""

    bild: Optional[Querschnittsbild] = None
    kurve: Optional[Union[Linie, "Modullinie"]] = None
    """Die M-chi- oder N-eps-Linie -- oder der aequivalente Modul daraus."""

    paar: Any = None
    """Womit gerechnet wurde -- das Loeserpaar mit Kriechzahl, Wertesatz,
    Betongesetz: :class:`Loeserpaar` bei der Platte, sonst das des
    gezeichneten Querschnitts."""

    hinweis: str = ""
    """Warum es nichts auszuwerten gab, falls es nichts gab."""

    @property
    def moeglich(self) -> bool:
        return self.bild is not None or self.kurve is not None


def auswerten(fall, art: Analyseart, paar) -> Tuple[
        Optional[Querschnittsbild], Optional[Union[Linie, Modullinie]]]:
    """
    Die eine der sechs Fragen stellen, die dieser Fall stellt -- in SI. ``paar``
    ist das Loeserpaar einer Platte oder eines gezeichneten Querschnitts:
    beide haben ``gerissen`` und ``ungerissen``, den Riss und den reinen
    Betonquerschnitt ``I_c``, ``A_c``.
    """
    if art is Analyseart.DEHNUNGEN:
        return aus_dehnungen(paar.gerissen, eps_oben=fall.eps_oben / 1e3,
                             eps_unten=fall.eps_unten / 1e3), None
    if art.linie is Analyseart.MOMENT_KRUEMMUNG:
        linie = moment_kruemmung(paar, N=fall.N_Ed * 1e3)
    elif art.linie is Analyseart.NORMALKRAFT_DEHNUNG:
        linie = normalkraft_dehnung(paar, M=fall.M_Ed * 1e3)
    else:
        return aus_schnittgroessen(paar.gerissen, N=fall.N_Ed * 1e3,
                                   M=fall.M_Ed * 1e3, art=paar.wahl.art), None
    if art.modul:
        return None, aequivalenter_modul(linie, I_c=paar.I_c, A_c=paar.A_c, E_cm=paar.E_cm)
    return None, linie


def analysen(aufbau: "Aufbau", loesung: "Loesung",
             protokoll: Optional[Protokoll] = None) -> Dict[str, List[Analyse]]:
    """
    Die Auswertungen am Querschnitt, je Platte und je gezeichnetem Querschnitt.

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
            richtung = Richtung(fall.richtung)
            wahl = fall.wahl
            schluessel = (richtung, wahl)
            if schluessel not in paare:
                try:
                    paare[schluessel] = loeserpaar(querschnitt, richtung, wert, wahl=wahl)
                except KeyError:
                    # Ein Wert dieser Richtung wurde nicht gerechnet -- dann
                    # gibt es fuer sie keinen Querschnitt zum Auswerten.
                    paare[schluessel] = None
            paar = paare[schluessel]
            analyse = Analyse(fall=fall, art=Analyseart(fall.art), richtung=richtung,
                              richtung_text=richtung.value, paar=paar)
            if paar is None:
                analyse.hinweis = (
                    f"In {richtung.beschriftung} liegt keine Bewehrung – ohne "
                    f"sie gibt es keinen Querschnitt zum Auswerten.")
            else:
                analyse.h = paar.gerissen.h
                analyse.bild, analyse.kurve = auswerten(fall, analyse.art, paar)
                if isinstance(analyse.kurve, Modullinie):
                    herleitung(p, fall, paar, analyse.kurve.linie, loesung.werte,
                                querschnitt.id, modul=analyse.kurve)
                elif analyse.kurve is not None:
                    herleitung(p, fall, paar, analyse.kurve, loesung.werte, querschnitt.id)
            liste.append(analyse)
        ergebnis[kennung] = liste
    # Die gezeichneten Querschnitte, je Zugseite -- dort gebaut. Erst hier
    # geladen: jenes Modul baut auf diesem.
    from opencivil.querschnitt import schnittanalyse
    ergebnis.update(schnittanalyse.analysen(aufbau, loesung, p))
    return ergebnis
