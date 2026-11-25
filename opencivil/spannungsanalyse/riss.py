"""
opencivil/spannungsanalyse/riss.py -- wo eine Linie reisst.

VERANTWORTUNG:
Der Riss einer Linie -- fuer die Platte und den gezeichneten Querschnitt
dieselbe Rechnung und dieselbe Herleitung (:class:`Bruttoriss`). Gerechnet
wird am ungerissenen Bruttoquerschnitt, ohne Stahl, wie beim sproeden
Versagen (:mod:`opencivil.nachweis.rissgroessen`)::

    M_Riss(N) = (f_ct,eff - N/A) · W        W zur Ecke, die unter reiner Biegung zuerst reisst
    N_Riss(M) = (f_ct,eff,t - σ_M) · A      σ_M aus M, an der Ecke, die zuerst reisst

Unter reiner Biegung mit dem Deviationsmoment ``I_yz``, «einachsig» mit
``W = I/v``. ``f_ct,eff`` mit ``k_t`` fuer ein Drittel der Tiefe, unter Zug
fuer die rissaktive Dicke; der Beton der Ecke gibt ``f_ctm``. Die Platte ist
ein Rechteck ``b × h`` und immer einachsig: ``A = b·h``, ``W = b·h²/6``.

Was nur das Paar weiss, schreibt es selbst: woher ``A`` und ``I`` kommen --
aus der Querschnittsanalyse oder aus ``b`` und ``h`` -- und welche Dicke
unter Zug reisst: beim gezeichneten Querschnitt die kleinere Abmessung
``min(h; b)``, bei der Platte ihre Dicke ``h``, denn ihr Streifen ``b`` ist
keine Abmessung der Platte
(:func:`~opencivil.nachweis.rissgroessen.rissaktive_dicke`). Bis 2026-11-21
rechnete die Platte ihren Riss selbst, in ``b`` und ``h``:
``M_Riss(N) = M_Riss - N·h/6`` -- dieselben Zahlen, aber eine zweite
Rechnung, und ihre Herleitung nannte ``M_Riss``, ohne es herzuleiten.

NACH VORGABE:
Der Bruttoquerschnitt ohne Stahl, wie beim sproeden Versagen. Der ungerissene
Zustand daneben rechnet mit Stahl und Kriechzahl und ist darum steifer; beim
Rissmoment steht sein Rand etwas unter ``f_ct,eff``. SIA 262:2025 laesst den
Querschnitt reissen, wenn der Beton ``f_ctm`` oder eine Fraktile erreicht,
ohne ``k_t`` (4.2.1.14), und rechnet ihn ungerissen mit dem Stahl
(4.1.4.1.4) -- Entscheid des Benutzers offen (``notizbuch/Notizen/TODO.md``).
Das Rissmoment nimmt ``k_t`` fuer ein Drittel der Tiefe, auch unter Zug; die
Rissnormalkraft die ganze rissaktive Dicke. Beim selben N und M reissen die
beiden Linien darum nicht am selben Punkt.

EINHEITEN:
SI-Basis wie im ganzen Querschnittsmodul.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple

from opencivil.core.einheiten import MIO_MM3, MIO_MM4, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.nachweis.querschnittsloeser import Faserloeser
from opencivil.nachweis.rissgroessen import (
    MOMENTENTEILER, Bruttoquerschnitt, Rissmoment, Rissnormalkraft, beiwert_dicke,
    protokoll_ecke, protokoll_spannung_ungerissen, protokoll_widerstandsmoment,
    protokoll_zugfestigkeit, rissnormalkraft,
)
from opencivil.querschnitt.gesetzwahl import Rechenart, Rechenwahl
from opencivil.querschnitt.zugseite import Zugseite

if TYPE_CHECKING:
    from opencivil.core.wert import Wert
    from opencivil.spannungsanalyse.linie import Linie


class Bruttoriss:
    """
    Der Riss eines Paars am Bruttoquerschnitt: Rechnung und Herleitung, dazu
    der reine Betonquerschnitt des aequivalenten Moduls -- derselbe
    Querschnitt.

    Das Paar gibt den Bruttoquerschnitt (``brutto``) mit seinem Rissmoment
    unter reiner Biegung (``riss``), seine Flaeche ``A``, die rissaktive
    Dicke unter Zug (``t_zug``), die Zugseite (``seite``), den gerissenen
    Loeser (``gerissen``) und seine Wahl (``wahl``) -- und zwei Stuecke
    Herleitung, die nur es kennt: :meth:`herleitung_bruttoquerschnitt` und
    :meth:`herleitung_dicke_unter_zug`.
    """

    brutto: Bruttoquerschnitt
    riss: Rissmoment
    A: float
    t_zug: float
    seite: Zugseite
    gerissen: Faserloeser
    wahl: Rechenwahl

    #: Was die Erklaerung der festen Nulllinie ueber das Moment um die andere
    #: Achse sagt -- beim gezeichneten Querschnitt ist «einachsig» eine Wahl;
    #: an der Platte, einem Rechteck, entsteht keines.
    ZUR_ANDEREN_ACHSE = ""

    #: Welche Dicke unter Zug reisst, in Worten.
    DICKE_UNTER_ZUG = ""

    # -- Die Rechnung ------------------------------------------------------------

    @property
    def art(self) -> Rechenart:
        """
        Die Rechenart des Betons der Ecke, die zuerst reisst: seine Kennwerte
        und sein Gesetz zeigt die Herleitung. Die Platte hat nur ihn.
        """
        return self.wahl.art_von(self.riss.ecke.stoff)

    @property
    def betone(self) -> Tuple[Any, ...]:
        """Die Betone des Querschnitts, jeder einmal -- aus den Ecken des Bruttoquerschnitts."""
        return tuple({e.stoff.id: e.stoff for e in self.brutto.ecken}.values())

    @property
    def einachsig(self) -> bool:
        """Ob die Nulllinie parallel zur Achse der Biegung bleibt, statt zu kippen."""
        return self.brutto.biegung.einachsig

    @property
    def I(self) -> float:
        """Das Traegheitsmoment um die Achse der Biegung, m⁴."""
        return self.brutto.I_y if self.seite.um_y else self.brutto.I_z

    @property
    def W(self) -> float:
        """Das Widerstandsmoment zur Ecke, die unter reiner Biegung zuerst reisst, m³."""
        return self.riss.W

    @property
    def M_Riss(self) -> float:
        """Das Rissmoment ohne Normalkraft, in Nm."""
        return self.riss.M_Riss

    @property
    def k_t_zug(self) -> float:
        """``k_t`` fuer die rissaktive Dicke unter Zug."""
        return beiwert_dicke(self.t_zug)

    def rissmoment_bei(self, N: float) -> float:
        """``M_Riss(N) = (f_ct,eff - N/A)·W`` in Nm, N Zug positiv -- Druck hebt es, Zug senkt es."""
        return self.M_Riss - N * self.W / self.A

    def rissnormalkraft(self, M: float) -> Rissnormalkraft:
        """Die Rissnormalkraft beim Moment ``M`` -- an der Ecke, die zuerst reisst."""
        M_y, M_z = self.seite.moment
        return rissnormalkraft(self.brutto, M * M_y, M * M_z, k_t=self.k_t_zug, A=self.A)

    def rissnormalkraft_bei(self, M: float) -> float:
        """``N_Riss(M) = (f_ct,eff,t - σ_M)·A`` in N -- ein Moment senkt sie, gleich in welche Richtung."""
        return self.rissnormalkraft(M).N_Riss

    @property
    def I_c(self) -> float:
        """
        Der reine Betonquerschnitt fuer den aequivalenten Modul: ``I`` -- kippt
        die Nulllinie, ``I - I_yz²/I_quer``
        (:mod:`opencivil.spannungsanalyse.schnitt`, «Der aequivalente Modul»).
        """
        if self.einachsig:
            return self.I
        b = self.brutto
        return self.I - b.I_yz ** 2 / (b.I_z if self.seite.um_y else b.I_y)

    @property
    def A_c(self) -> float:
        """Dasselbe fuer die Normalkraft: ``A``."""
        return self.A

    # -- Was nur das Paar weiss --------------------------------------------------

    def herleitung_bruttoquerschnitt(self, p: Protokoll, w: Zwischenwerte,
                                     ein: Callable[[str], "Wert"],
                                     h: "Wert") -> Tuple["Wert", "Wert"]:
        """``A`` und ``I`` als Werte der Herleitung -- woher sie kommen, weiss das Paar."""
        raise NotImplementedError

    def herleitung_dicke_unter_zug(self, p: Protokoll, w: Zwischenwerte, h: "Wert") -> "Wert":
        """Die rissaktive Dicke unter Zug, ``t`` -- wie das Paar sie misst."""
        raise NotImplementedError

    # -- Die Herleitung ----------------------------------------------------------

    def herleitung_riss(self, p: Protokoll, w: Zwischenwerte, linie: "Linie",
                        ein: Callable[[str], "Wert"], h: "Wert") -> Tuple["Wert", "Wert"]:
        """
        Wo die Linie reisst: das Rissmoment bei N oder die Rissnormalkraft bei
        M, am Bruttoquerschnitt. Zurueck kommen dessen ``A`` und ``I``, wie die
        Herleitung sie nennt -- auf sie bezieht sich der aequivalente Modul.
        """
        if self.einachsig:
            oben, unten = self.seite.raender
            p.erklaerung(
                f"Die Nulllinie bleibt parallel zur Achse der Biegung: gezogen wird der "
                f"Rand {unten}, gedrückt der Rand {oben}. {self.ZUR_ANDEREN_ACHSE}Am "
                f"Bruttoquerschnitt reisst der gezogene Rand, wenn N/A + M/W = f_ct,eff; "
                f"W gehört zu diesem Rand, v_z ist sein Abstand vom Schwerpunkt.")
            A, I = self.herleitung_bruttoquerschnitt(p, w, ein, h)
            v = w.laenge("v_z", "v_z", self.gerissen.unten,
                         "Abstand des gezogenen Rands vom Schwerpunkt")
            W = w.wert("W", "W", Groesse.aus_si(self.W, MIO_MM3), stellen=2)
            p.formel(W, r"\frac{@I}{@v}", {"I": I, "v": v},
                     titel="Widerstandsmoment zum gezogenen Rand")
        else:
            p.erklaerung(
                "Unter reiner Biegung kippt die Nulllinie, bis kein Moment um die andere "
                "Achse bleibt. Am ungerissenen Bruttoquerschnitt hängt die Spannung dann "
                "auch vom Deviationsmoment I_yz ab, und es reisst die Ecke zuerst, die ihre "
                "Zugfestigkeit zuerst erreicht – bei einem unsymmetrischen Querschnitt eine "
                "Ecke, nicht der ganze Rand.")
            protokoll_spannung_ungerissen(p, self.brutto.biegung)
            A, I = self.herleitung_bruttoquerschnitt(p, w, ein, h)
            # Gekippt gehoert W zu einer Ecke -- es steht beim Rissmoment.
            v = W = None
        if linie.art.ueber_moment:
            self._herleitung_rissmoment(p, w, linie, ein, h, A, W)
        else:
            self._herleitung_rissnormalkraft(p, w, linie, ein, h, A, I, v)
        return A, I

    def _herleitung_rissmoment(self, p: Protokoll, w: Zwischenwerte, linie: "Linie",
                               ein: Callable[[str], "Wert"], h: "Wert", A: "Wert",
                               W: Optional["Wert"]) -> None:
        """Das Rissmoment bei der Normalkraft der Linie."""
        ecke = self.riss.ecke
        if not self.einachsig:
            protokoll_ecke(p, ecke)
            W = protokoll_widerstandsmoment(p, w, self.brutto, ecke, self.W, *self.seite.moment)
        f_ct_eff = protokoll_zugfestigkeit(
            p, w, k_t=self.riss.k_t, f_ct_eff=self.riss.f_ct_eff, h=h,
            f_ctm=ein(ecke.stoff.id_von("f_ctm")), teiler=MOMENTENTEILER,
            titel="Beiwert für die Tiefe in Biegerichtung")
        p.formel(w.moment("M_Riss_N", "M_{Riss}(N)", linie.riss),
                 r"\left(@f - \frac{@N}{@A}\right) \cdot @W",
                 {"f": f_ct_eff, "N": w.kraft("N", "N", linie.fest), "A": A, "W": W},
                 titel="Rissmoment bei der Normalkraft")

    def _herleitung_rissnormalkraft(self, p: Protokoll, w: Zwischenwerte, linie: "Linie",
                                    ein: Callable[[str], "Wert"], h: "Wert", A: "Wert",
                                    I: "Wert", v: Optional["Wert"]) -> None:
        """Die Rissnormalkraft beim Moment der Linie."""
        p.erklaerung(
            "Dieselbe Rissbedingung, nach der Normalkraft aufgelöst. Unter Zug gilt "
            f"k_t für die rissaktive Dicke t, {self.DICKE_UNTER_ZUG} – "
            "nicht für h/3 wie beim Rissmoment. Ein negatives Moment zieht den anderen "
            "Rand: dann gilt dessen Abstand.")
        t = self.herleitung_dicke_unter_zug(p, w, h)
        M = linie.fest
        zug = self.rissnormalkraft(M)
        f_ct_eff = protokoll_zugfestigkeit(
            p, w, k_t=self.k_t_zug, f_ct_eff=zug.f_ct_eff, h=t,
            f_ctm=ein(zug.ecke.stoff.id_von("f_ctm")), teiler=1,
            titel="Beiwert für die rissaktive Dicke")
        N_Riss = w.kraft("N_Riss_M", "N_{Riss}(M)", linie.riss)
        M_wert = w.moment("M", "M", M)
        if self.einachsig:
            rand = v if M >= 0.0 else w.laenge(
                "v_d", "v_d", self.gerissen.oben,
                "Abstand des gedrückten Rands vom Schwerpunkt, negativ")
            p.formel(N_Riss, r"\left(@f - \frac{@M \cdot @v}{@I}\right) \cdot @A",
                     {"f": f_ct_eff, "M": M_wert, "v": rand, "I": I, "A": A},
                     titel="Rissnormalkraft beim Moment")
            return
        sigma = w.spannung("sigma_M", r"\sigma_M", zug.sigma_M, "aus dem Moment allein", stellen=2)
        if M != 0.0 and zug.sigma_M > 0.0:
            # Das Moment zieht die Ecke: σ_M = |M|/W, mit W in der Richtung,
            # in die es zieht.
            M_y, M_z = self.seite.moment
            protokoll_ecke(p, zug.ecke)
            W = protokoll_widerstandsmoment(
                p, w, self.brutto, zug.ecke, abs(M) / zug.sigma_M,
                *((M_y, M_z) if M > 0.0 else (-M_y, -M_z)))
            p.formel(sigma, r"\frac{\left|@M\right|}{@W}", {"M": M_wert, "W": W},
                     titel="Spannung aus dem Moment an der Ecke, die zuerst reisst")
        else:
            p.wert(sigma, titel="Spannung aus dem Moment an der Ecke, die zuerst reisst")
        p.formel(N_Riss, r"\left(@f - @sigma\right) \cdot @A",
                 {"f": f_ct_eff, "sigma": sigma, "A": A}, titel="Rissnormalkraft beim Moment")

    # -- Der reine Betonquerschnitt des Moduls ------------------------------------

    def herleitung_traegheit(self, p: Protokoll, w: Zwischenwerte, I: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des Moduls ueber dem Moment: der Bruttoquerschnitt."""
        bezug = w.wert("I_c", "I_c", Groesse.aus_si(self.I_c, MIO_MM4), stellen=1)
        if self.einachsig:
            p.erklaerung(f"Der reine Betonquerschnitt ist der Bruttoquerschnitt, um die "
                         f"Achse der Biegung: I_c = {I.symbol.replace('_', '')}.")
            p.wert(bezug, titel="Reiner Betonquerschnitt")
            return bezug
        b = self.brutto
        quer = w.wert("I_quer", "I_z" if self.seite.um_y else "I_y",
                      Groesse.aus_si(b.I_z if self.seite.um_y else b.I_y, MIO_MM4), stellen=1)
        p.erklaerung(
            "Der reine Betonquerschnitt ist der Bruttoquerschnitt. Unter reiner Biegung "
            "kippt auch seine Nulllinie, und senkrecht zur Achse der Biegung krümmt er "
            "sich darum stärker, als I allein sagt: wie ein Querschnitt mit I_c. Sonst "
            "zeigte ein ungerissener unsymmetrischer Querschnitt schon seiner Form wegen "
            "einen kleineren Modul.")
        p.formel(bezug, r"@I - \frac{@Iyz^{2}}{@quer}",
                 {"I": I, "Iyz": w.wert("Iyz", "I_{yz}", Groesse.aus_si(b.I_yz, MIO_MM4), 1),
                  "quer": quer},
                 titel="Reiner Betonquerschnitt, Nulllinie gekippt")
        return bezug

    def herleitung_flaeche(self, p: Protokoll, w: Zwischenwerte, A: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des Moduls ueber der Normalkraft: der Bruttoquerschnitt."""
        bezug = w.flaeche("A_c", "A_c", self.A)
        p.erklaerung(f"Der reine Betonquerschnitt ist der Bruttoquerschnitt: A_c = {A.symbol}.")
        p.wert(bezug, titel="Reiner Betonquerschnitt")
        return bezug
