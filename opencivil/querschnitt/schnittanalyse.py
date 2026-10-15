"""
opencivil/querschnitt/schnittanalyse.py -- Spannung-Dehnung-Analyse am gezeichneten Querschnitt.

VERANTWORTUNG:
Die sechs Fragen der Spannung-Dehnung-Analyse an einen gezeichneten
Querschnitt: aus N und M, aus Randdehnungen, die M-χ- und die N-ε-Linie und
der aequivalente E-Modul darueber. Gerechnet wird mit denselben Funktionen
wie bei der Platte (:mod:`opencivil.spannungsanalyse`); hier steht, wie der
Querschnitt zu ihnen kommt -- das Loeserpaar je Zugseite -- und was seine
Herleitung anders schreibt.

JE ZUGSEITE:
Eine Analyse waehlt die Seite, die ein positives Moment zieht: unten, oben,
links oder rechts (:class:`Zugseite`). Die Nulllinie bleibt parallel zur
Achse, wie in der einachsigen Tragsicherheit. Das Moment um die andere
Achse, das ein unsymmetrischer Querschnitt dabei weckt, zaehlt nicht -- ein
L-Querschnitt drehte seine Nulllinie in Wirklichkeit. Die Platte rechnet
immer so.

``eps_m`` ist die Dehnung im Schwerpunkt des Bruttoquerschnitts, und die
Momente beziehen sich auf ihn, wie in den Lastfaellen. «Oben» heisst der
Rand gegenueber der Zugseite, «unten» der auf ihr: bei Zug links ist oben
der rechte Rand.

WOMIT GERECHNET WIRD:
Je Analyse eine Rechenwahl wie bei der Platte -- Kriechzahl, Wertesatz,
Rechenart --, fuer jeden Werkstoff des Querschnitts dieselbe. Die
Werkstoffwahl der Tragsicherheit gilt hier nicht. Staebe in derselben Tiefe,
aus demselben Stahl, werden zu einer Lage: sie haben dieselbe Dehnung.
Zerlegt wird in so viele Streifen wie die Platte in Fasern (:data:`FASERN`),
dazu die Grenzen an jeder Ecke: eine Linie rechnet viele Ebenen, und mit den
200 Streifen der Tragsicherheit dauerte sie dreimal so lang -- fuer ein
M_Rd, das sich um zwei Zehntelpromille aendert.

DER RISS:
Am ungerissenen Bruttoquerschnitt, ohne Stahl, wie beim sproeden Versagen::

    M_Riss(N) = (f_ct,eff - N/A) · W          W = I / v_z
    N_Riss(M) = (f_ct,eff,t - M·v/I) · A      v am Rand, den M zieht

``I`` ist das Traegheitsmoment um die Achse der Biegung, ``v_z`` der
Abstand des gezogenen Rands vom Schwerpunkt. ``f_ct,eff`` mit ``k_t`` fuer
ein Drittel der Tiefe, unter Zug fuer die ganze -- die Regeln der Platte,
uebertragen; der Beton am gezogenen Rand gibt ``f_ctm``. Nach Vorgabe,
nicht nachgeschlagen (``notizbuch/Notizen/TODO.md``). Bei der Platte ist
``W/A = h/6`` -- dieselbe Formel.

DER AEQUIVALENTE MODUL:
Bezogen auf den Bruttoquerschnitt: ``I`` um die Achse der Biegung bzw.
``A``. Bei der Platte sind es ``b·h³/12`` und ``b·h``.

EINHEITEN:
SI-Basis wie im ganzen Querschnittsmodul.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Callable, Dict, List, Mapping, Optional, Tuple

from opencivil.core.einheiten import MIO_MM3, MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.nachweis.querschnittsloeser import (
    FASERN, Faserloeser, Stahllage, bilinear, wirksamer_modul,
)
from opencivil.nachweis.rechenwahl import Rechenwahl, betongesetz
from opencivil.nachweis.sproedes_versagen import (
    MOMENTENTEILER, beiwert_dicke, protokoll_zugfestigkeit,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse, Stabgruppe
from opencivil.querschnitt.fasern import Faserquerschnitt, Stab
from opencivil.querschnitt.interaktion import Querschnitt, Werkstoff
from opencivil.querschnitt.werkstoffgesetz import Stahlgesetz
from opencivil.spannungsanalyse import (
    Analyse, Analyseart, Grenzzustand, Linie, auswerten, beton_ungerissen, herleitung,
)

if TYPE_CHECKING:
    from opencivil.core.rechenwerk import Loesung
    from opencivil.core.wert import Wert
    from opencivil.projekt import Aufbau


class Zugseite(str, Enum):
    """Die Seite, die ein positives Moment zieht -- und die Richtung, die dazu gehoert."""

    UNTEN = "unten"
    OBEN = "oben"
    LINKS = "links"
    RECHTS = "rechts"

    @property
    def beschriftung(self) -> str:
        return f"Zug {self.value}"

    @property
    def psi(self) -> float:
        """Die Zugrichtung als Winkel, wie :class:`~opencivil.querschnitt.interaktion.Querschnitt` sie nimmt."""
        return {Zugseite.UNTEN: -math.pi / 2.0, Zugseite.OBEN: math.pi / 2.0,
                Zugseite.LINKS: math.pi, Zugseite.RECHTS: 0.0}[self]

    @property
    def um_y(self) -> bool:
        """Ob die Biegung um die y-Achse geht -- Zug unten oder oben."""
        return self in (Zugseite.UNTEN, Zugseite.OBEN)

    @property
    def raender(self) -> Tuple[str, str]:
        """Wie die beiden Raender heissen: der gedrueckte und der gezogene."""
        return {Zugseite.UNTEN: ("oben", "unten"), Zugseite.OBEN: ("unten", "oben"),
                Zugseite.LINKS: ("rechts", "links"),
                Zugseite.RECHTS: ("links", "rechts")}[self]


# ===========================================================================
# Der Querschnitt je Zugseite
# ===========================================================================


def _werkstoffe(analyse: Querschnittsanalyse, wert: Callable[[str], float],
                wahl: Rechenwahl, *, ungerissen: bool,
                ) -> Tuple[List[Werkstoff], Dict[str, int], Dict[int, Stahlgesetz]]:
    """
    Die Werkstoffe zu einer Rechenwahl -- jeder Beton mit dem Gesetz der Wahl
    oder, ``ungerissen``, linear in Druck und Zug mit ``E_cm/(1+phi)``; jeder
    Stahl bilinear im Wertesatz der Wahl. Die Grenzen sind die des
    Dehnungsfaechers, in beiden Zustaenden dieselben.
    """
    satz = wahl.satz
    liste: List[Werkstoff] = []
    index: Dict[str, int] = {}
    staehle: Dict[int, Stahlgesetz] = {}
    for stoff in analyse.baustoffe:
        w = lambda k: abs(wert(stoff.id_von(k)))
        if stoff.art is Baustoffart.BETON:
            E_cm, eps_c1d, eps_c2d = w("E_cm"), w("eps_c1d"), w("eps_c2d")
            gesetz = (beton_ungerissen(E_c=wirksamer_modul(E_cm, wahl.kriechzahl)) if ungerissen
                      else betongesetz(wahl, f_c=w(satz.beton), E_cm=E_cm,
                                       eps_c1d=eps_c1d, eps_c2d=eps_c2d))
            liste.append(Werkstoff(stoff.name, gesetz, -eps_c2d, math.inf,
                                   c_punkt=(eps_c1d, eps_c2d), verdraengbar=True))
        else:
            stahl = Stahlgesetz(E_s=w("E_s"), f_yd=w(satz.stahl),
                                f_yd_druck=w(satz.stahl_druck), eps_ud=w("eps_ud"))
            liste.append(Werkstoff(stoff.name, bilinear(stahl), -stahl.eps_ud, stahl.eps_ud))
            staehle[len(liste) - 1] = stahl
        index[stoff.id] = len(liste) - 1
    return liste, index, staehle


def _betonspannung(r, gesetze: Mapping[int, Callable[[float], float]]
                   ) -> Callable[[float, float], float]:
    """
    Die Spannung des Betons an einer Stelle, fuer das Bild: in jedem Streifen
    der Beton mit der groessten Breite dort. Liegen zwei Betone in derselben
    Tiefe, zeigt das Bild den, der dort ueberwiegt.
    """
    streifen: Dict[float, Tuple[float, float, int]] = {}
    for gruppe, w in zip(r.fasern.gruppen, r.gruppen_werkstoff):
        if w not in gesetze:
            continue
        for arm, flaeche, dicke in zip(gruppe.arme, gruppe.flaechen, gruppe.dicken):
            da = streifen.get(arm)
            if da is None or flaeche > da[1]:
                streifen[arm] = (dicke, flaeche, w)
    liste = sorted((arm, dicke, w) for arm, (dicke, _, w) in streifen.items())

    def spannung(arm: float, eps: float) -> float:
        _, _, w = min(liste, key=lambda s: max(0.0, abs(arm - s[0]) - s[1] / 2.0))
        return gesetze[w](eps)
    return spannung


def _loeser(q: Querschnitt, seite: Zugseite, herkunft: List[Stabgruppe],
            staehle: Mapping[int, Stahlgesetz], namen: Mapping[int, str]) -> Faserloeser:
    """
    Der Querschnitt in einer Zugrichtung als :class:`Faserloeser`. Staebe in
    derselben Tiefe, aus demselben Stahl und im selben Beton werden eine Lage
    -- sie haben dieselbe Dehnung, und das Bild zeigt sie als eine.
    """
    r = q.richtung(seite.psi)
    oben, unten = r.beton
    gruppen: Dict[tuple, List[Tuple[Stab, str]]] = {}
    for b, stab, element in zip(q.bewehrung, r.fasern.staebe, herkunft):
        schluessel = (round(stab.arm, 9), b.werkstoff, b.verdraengt, stab.dicke)
        gruppen.setdefault(schluessel, []).append((stab, element.name))
    staebe: List[Stab] = []
    lagen: List[Stahllage] = []
    for nummer, (schluessel, liste) in enumerate(sorted(gruppen.items(), key=lambda kv: kv[0][0]),
                                                 start=1):
        erster = liste[0][0]
        flaeche = sum(s.flaeche for s, _ in liste)
        staebe.append(Stab(arm=erster.arm, flaeche=flaeche, gesetz=erster.gesetz,
                           verdraengt=erster.verdraengt, dicke=erster.dicke))
        werkstoff = schluessel[1]
        lagen.append(Stahllage(
            a_s=flaeche, z=erster.arm - oben, stahl=staehle[werkstoff],
            sorte=namen[werkstoff], nummer=nummer,
            text=", ".join(dict.fromkeys(name for _, name in liste))))
    betone = {i: w for i, w in enumerate(q.werkstoffe) if w.c_punkt is not None}
    return Faserloeser(
        querschnitt=Faserquerschnitt(r.fasern.gruppen, staebe), grenzen=r.grenzen,
        oben=oben, unten=unten, lagen=lagen,
        beton=_betonspannung(r, {i: w.gesetz for i, w in betone.items()}),
        eps_druck=min(-w.eps_min for w in betone.values()),
        eps_zug=min((s.eps_ud for s in staehle.values()), default=math.inf))


@dataclass(frozen=True)
class Schnittpaar:
    """
    Die beiden Loeser eines gezeichneten Querschnitts in einer Zugrichtung --
    gerissen und ungerissen, wie das :class:`~opencivil.spannungsanalyse.Loeserpaar`
    der Platte. Dazu der Riss am Bruttoquerschnitt und was die Herleitung
    braucht.
    """

    gerissen: Faserloeser
    ungerissen: Faserloeser
    seite: Zugseite
    wahl: Rechenwahl
    grenznamen: Tuple[str, ...]

    querschnitt: Querschnitt
    """Der gerissene Querschnitt im Bruchzustand -- derselbe, aus dem ``gerissen`` stammt."""

    A: float
    """Flaeche des Bruttoquerschnitts, m²."""

    I: float
    """Traegheitsmoment um die Achse der Biegung, m⁴."""

    v_oben: float
    v_unten: float
    """Die Raender, vom Schwerpunkt in Zugrichtung gemessen: der gedrueckte (negativ) und der gezogene."""

    k_t: float
    f_ct_eff: float
    """Fuer das Rissmoment: ``k_t`` fuer ein Drittel der Tiefe, ``k_t·f_ctm``."""

    k_t_zug: float
    f_ct_eff_zug: float
    """Fuer die Rissnormalkraft: ``k_t`` fuer die ganze Tiefe."""

    E_cm: float
    """Der Modul des Betons am gezogenen Rand -- daran misst sich der aequivalente Modul."""

    staehle: Tuple[Baustoff, ...] = ()
    ids: Mapping[str, str] = field(default_factory=dict)
    """Kurzname -> Wert-ID der Eingaben, fuer die Herleitung: der Beton am gezogenen Rand und A, I."""

    @property
    def W(self) -> float:
        """Das Widerstandsmoment zum gezogenen Rand, m³."""
        return self.I / self.v_unten

    @property
    def M_Riss(self) -> float:
        """Das Rissmoment ohne Normalkraft."""
        return self.f_ct_eff * self.W

    def rissmoment_bei(self, N: float) -> float:
        """``M_Riss(N) = (f_ct,eff - N/A)·W`` -- Druck hebt es, Zug senkt es."""
        return self.M_Riss - N * self.W / self.A

    def rissnormalkraft_bei(self, M: float) -> float:
        """
        ``N_Riss(M) = (f_ct,eff,t - M·v/I)·A`` -- ``v`` am Rand, den ``M`` zieht:
        der gezogene bei positivem Moment, der gedrueckte bei negativem.
        """
        zieht = max(M * self.v_unten, M * self.v_oben)
        return (self.f_ct_eff_zug - zieht / self.I) * self.A

    @property
    def I_c(self) -> float:
        return self.I

    @property
    def A_c(self) -> float:
        return self.A

    # -- Was die Herleitung nur vom gezeichneten Querschnitt weiss -----------

    #: Wo die Mitteldehnung gilt -- dort greift N an.
    bezugsort = "im Schwerpunkt"

    def tiefe(self, w: Zwischenwerte, ein: Callable[[str], "Wert"]) -> "Wert":
        """Die Ausdehnung des Betons in Zugrichtung -- aus der Zeichnung, kein Wert des Rechenwerks."""
        return w.laenge("h", "h", self.gerissen.h, "Ausdehnung des Betons in Zugrichtung")

    def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: Linie,
                        ein: Callable[[str], "Wert"], h: "Wert") -> None:
        """Der Riss am Bruttoquerschnitt: Widerstandsmoment, Zugfestigkeit, Risskraft."""
        oben, unten = self.seite.raender
        A, I = ein("A"), ein("I")
        v = w.laenge("v_z", "v_z", self.v_unten,
                      "Abstand des gezogenen Rands vom Schwerpunkt")
        p.erklaerung(
            f"Die Nulllinie bleibt parallel zur Achse der Biegung: gezogen wird der "
            f"Rand {unten}, gedrückt der Rand {oben}. Das Moment um die andere Achse, "
            f"das ein unsymmetrischer Querschnitt dabei weckt, zählt nicht. Am "
            f"Bruttoquerschnitt reisst der gezogene Rand, wenn N/A + M/W = f_ct,eff; "
            f"W gehört zu diesem Rand, v_z ist sein Abstand vom Schwerpunkt.")
        W = w.wert("W", "W", Groesse.aus_si(self.W, MIO_MM3), stellen=2)
        p.formel(W, r"\frac{@I}{@v}", {"I": I, "v": v},
                 titel="Widerstandsmoment zum gezogenen Rand")
        if linie.art is Analyseart.MOMENT_KRUEMMUNG:
            f_ct_eff = protokoll_zugfestigkeit(
                p, w, k_t=self.k_t, f_ct_eff=self.f_ct_eff, h=h, f_ctm=ein("f_ctm"),
                teiler=MOMENTENTEILER, referenz="SIA 262:2025, 4.4.1.3",
                titel="Beiwert für die Tiefe in Biegerichtung")
            p.formel(w.moment("M_Riss_N", "M_{Riss}(N)", linie.riss),
                     r"\left(@f - \frac{@N}{@A}\right) \cdot @W",
                     {"f": f_ct_eff, "N": w.kraft("N", "N", linie.fest), "A": A, "W": W},
                     titel="Rissmoment bei der Normalkraft")
            return
        p.erklaerung(
            "Dieselbe Rissbedingung, nach der Normalkraft aufgelöst. Unter Zug "
            "reisst die ganze Tiefe, darum gilt k_t für t = h und nicht für h/3 wie "
            "beim Rissmoment. Ein negatives Moment zieht den anderen Rand: dann "
            "gilt dessen Abstand.")
        f_ct_eff = protokoll_zugfestigkeit(
            p, w, k_t=self.k_t_zug, f_ct_eff=self.f_ct_eff_zug, h=h, f_ctm=ein("f_ctm"),
            teiler=1, referenz="SIA 262:2025, 4.4.2",
            titel="Beiwert für die Tiefe in Biegerichtung")
        M = linie.fest
        rand = v if M >= 0.0 else w.laenge(
            "v_d", "v_d", self.v_oben, "Abstand des gedrückten Rands vom Schwerpunkt, negativ")
        p.formel(w.kraft("N_Riss_M", "N_{Riss}(M)", linie.riss),
                 r"\left(@f - \frac{@M \cdot @v}{@I}\right) \cdot @A",
                 {"f": f_ct_eff, "M": w.moment("M", "M", M), "v": rand, "I": I, "A": A},
                 titel="Rissnormalkraft beim Moment")

    def herleitung_dehnung_am_ende(self, p: Protokoll, w: Zwischenwerte, bruch: Grenzzustand,
                                   oben: "Wert", unten: "Wert") -> None:
        """Die Dehnung im Schwerpunkt am Ende -- dort greift N an."""
        p.formel(w.dehnung("eps_mu", r"\varepsilon_{m,u}", bruch.verformung),
                 r"@eps_oben + \left(@eps_unten - @eps_oben\right) \cdot \frac{@v}{@h}",
                 {"eps_oben": oben, "eps_unten": unten,
                  "v": w.laenge("v_o", "v_o", -self.v_oben,
                                "Abstand des oberen Rands vom Schwerpunkt"),
                  "h": w.laenge("h", "h", self.gerissen.h,
                                "Ausdehnung des Betons in Zugrichtung")},
                 titel="Grösste Dehnung im Schwerpunkt")

    def herleitung_bezug(self, p: Protokoll, w: Zwischenwerte, momente: bool,
                         ein: Callable[[str], "Wert"], h: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des aequivalenten Moduls: der Bruttoquerschnitt."""
        if momente:
            bezug = w.wert("I_c", "I_c", Groesse.aus_si(self.I, MIO_MM4), stellen=1)
            p.erklaerung(f"Der reine Betonquerschnitt ist der Bruttoquerschnitt, um die "
                         f"Achse der Biegung: I_c = {ein('I').symbol.replace('_', '')}.")
        else:
            bezug = w.flaeche("A_c", "A_c", self.A)
            p.erklaerung("Der reine Betonquerschnitt ist der Bruttoquerschnitt: A_c = A.")
        p.wert(bezug, titel="Reiner Betonquerschnitt")
        return bezug


def querschnitt_nach_wahl(analyse: Querschnittsanalyse, wert: Callable[[str], float],
                          wahl: Rechenwahl, *, ungerissen: bool = False,
                          ) -> Tuple[Querschnitt, List[Stabgruppe], Dict[int, Stahlgesetz]]:
    """
    Der gezeichnete Querschnitt mit den Gesetzen einer Rechenwahl -- dazu je
    Bewehrung ihr Element und je Stahl sein Gesetz, nach dem Index des
    Werkstoffs. ``wert`` liefert zu einer Wert-ID die Zahl in SI. Zerlegt in
    so viele Streifen, wie die Platte Fasern hat (:data:`FASERN`).
    """
    werkstoffe, index, staehle = _werkstoffe(analyse, wert, wahl, ungerissen=ungerissen)
    teile, bewehrung, herkunft = analyse.geometrie(lambda stoff: index[stoff.id])
    q = Querschnitt(werkstoffe=werkstoffe, teile=teile, bewehrung=bewehrung,
                    bezug=(wert(analyse.id_von("y_S")), wert(analyse.id_von("z_S"))),
                    streifen=FASERN)
    return q, herkunft, staehle


def schnittpaar(analyse: Querschnittsanalyse, seite: Zugseite, wert: Callable[[str], float],
                wahl: Rechenwahl) -> Optional[Schnittpaar]:
    """
    Das Loeserpaar eines gezeichneten Querschnitts in einer Zugrichtung --
    ``None`` ohne Bewehrung. ``wert`` liefert zu einer Wert-ID die Zahl in SI,
    aus einer Loesung.
    """
    if not analyse.gruppen:
        return None
    zustaende = []
    for ungerissen in (False, True):
        q, herkunft, staehle = querschnitt_nach_wahl(analyse, wert, wahl, ungerissen=ungerissen)
        namen = {i: w.name for i, w in enumerate(q.werkstoffe)}
        zustaende.append((q, _loeser(q, seite, herkunft, staehle, namen)))
    (q, gerissen), (_, ungerissen) = zustaende
    r = q.richtung(seite.psi)

    # Der Beton am gezogenen Rand: er gibt f_ctm und E_cm.
    sy, sz = q.bezug
    n = r.n
    ecke, stoff = max(analyse.beton_ecken, key=lambda es: n[0] * (es[0][0] * 1e-3 - sy)
                      + n[1] * (es[0][1] * 1e-3 - sz))
    I_id = analyse.id_von("I_y" if seite.um_y else "I_z")
    ids = {"E_cm": stoff.id_von("E_cm"), "f_c": stoff.id_von(wahl.satz.beton),
           "eps_c1d": stoff.id_von("eps_c1d"), "eps_c2d": stoff.id_von("eps_c2d"),
           "f_ctm": stoff.id_von("f_ctm"), "A": analyse.id_von("A"), "I": I_id}
    f_ctm = abs(wert(ids["f_ctm"]))
    tiefe = gerissen.h
    k_t, k_t_zug = beiwert_dicke(tiefe / MOMENTENTEILER), beiwert_dicke(tiefe)
    stahlstoffe = tuple({g.stahl.id: g.stahl for g in analyse.gruppen}.values())
    return Schnittpaar(
        gerissen=gerissen, ungerissen=ungerissen, seite=seite, wahl=wahl,
        grenznamen=r.grenznamen, querschnitt=q, A=wert(ids["A"]), I=wert(I_id),
        v_oben=gerissen.oben, v_unten=gerissen.unten,
        k_t=k_t, f_ct_eff=k_t * f_ctm, k_t_zug=k_t_zug, f_ct_eff_zug=k_t_zug * f_ctm,
        E_cm=abs(wert(ids["E_cm"])), staehle=stahlstoffe, ids=ids)


# ===========================================================================
# Die Analysen der gezeichneten Querschnitte
# ===========================================================================


def analysen(aufbau: "Aufbau", loesung: "Loesung",
             protokoll: Protokoll) -> Dict[str, List[Analyse]]:
    """
    Die Auswertungen je gezeichnetem Querschnitt -- wie
    :func:`opencivil.spannungsanalyse.analysen` je Platte, und von dort
    gerufen. Mit ``protokoll`` schreibt jede Linie ihre Herleitung.
    """
    def wert(kid: str) -> float:
        return loesung.werte[kid].groesse.si

    ergebnis: Dict[str, List[Analyse]] = {}
    for kennung, faelle in aufbau.spannungsfaelle.items():
        analyse = aufbau.querschnittsanalysen.get(kennung)
        if analyse is None:
            continue
        paare: Dict[tuple, Optional[Schnittpaar]] = {}
        liste: List[Analyse] = []
        for fall in faelle:
            seite = Zugseite(fall.richtung)
            wahl = Rechenwahl.aus(fall.kriechzahl, fall.werkstoffsatz, fall.rechenart)
            schluessel = (seite, wahl)
            if schluessel not in paare:
                try:
                    paare[schluessel] = schnittpaar(analyse, seite, wert, wahl)
                except KeyError:
                    # Ein Wert wurde nicht gerechnet -- etwa, weil ein
                    # Baustoff fehlt. Dann gibt es nichts auszuwerten.
                    paare[schluessel] = None
            paar = paare[schluessel]
            eintrag = Analyse(fall=fall, art=Analyseart(fall.art), richtung=seite,
                              richtung_text=seite.beschriftung, paar=paar)
            if paar is None:
                eintrag.hinweis = ("Der Querschnitt hat keine Bewehrung – ohne sie gibt "
                                   "es nichts zum Auswerten.")
            else:
                eintrag.h = paar.gerissen.h
                eintrag.bild, eintrag.kurve = auswerten(fall, eintrag.art, paar)
                kurve = eintrag.kurve
                if kurve is not None:
                    linie = kurve if isinstance(kurve, Linie) else kurve.linie
                    herleitung(protokoll, fall, paar, linie, loesung.werte, analyse.id,
                               modul=None if isinstance(kurve, Linie) else kurve)
            liste.append(eintrag)
        ergebnis[kennung] = liste
    return ergebnis
