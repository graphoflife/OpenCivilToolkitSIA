"""
opencivil/spannungsanalyse/riss.py -- wo eine Linie reisst.

VERANTWORTUNG:
Der Riss einer Linie -- fuer die Platte und den gezeichneten Querschnitt
dieselbe Rechnung und dieselbe Herleitung (:class:`Bruttoriss`), und was ein
Paar aus Stahlbeton sonst in die Herleitung schreibt: den wirksamen Modul,
die Gesetze des Betons, die Fliessdehnungen und die Grenzdehnungen
(:meth:`Bruttoriss.herleitung_gesetze`) -- bis 2026-11-26 stand das in
:mod:`opencivil.spannungsanalyse.herleitung`, fuer jedes Paar. Gerechnet
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

from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional, Tuple

from opencivil.core.einheiten import MIO_MM3, Groesse
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import kennung_aus
from opencivil.material.basis import mit_index
from opencivil.material.betonstahl import FLIESSDEHNUNG
from opencivil.nachweis.querschnittsloeser import Faserloeser
from opencivil.nachweis.rissgroessen import (
    MOMENTENTEILER, REFERENZ_VORSPANNUNG, Bruttoquerschnitt, Rissmoment, Rissnormalkraft,
    beiwert_dicke, protokoll_ecke, protokoll_spannung_ungerissen, protokoll_traegheit,
    protokoll_vorspannung, protokoll_widerstandsmoment, protokoll_zugfestigkeit, rissnormalkraft,
)
from opencivil.querschnitt.gesetzwahl import (
    REFERENZ_KRIECHEN, Rechenart, Rechenwahl, Werkstoffsatz, arten_text, betongesetz,
    wirksamer_modul,
)
from opencivil.querschnitt.werkstoffgesetz import BetonUngerissen
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.spannungsanalyse.linie import Modulbezug

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
    Loeser (``gerissen``), seine Wahl (``wahl``), den Modul ``E_cm`` des
    Betons, die Staehle seiner Lagen (``staehle``) und die Wert-IDs der
    Herleitung (``ids``) -- und Stuecke Herleitung, die nur es kennt:
    :meth:`tiefe`, :meth:`herleitung_bruttoquerschnitt` und
    :meth:`herleitung_dicke_unter_zug`.
    """

    brutto: Bruttoquerschnitt
    riss: Rissmoment
    A: float
    t_zug: float
    seite: Zugseite
    gerissen: Faserloeser
    wahl: Rechenwahl
    E_cm: float
    staehle: Tuple[Any, ...]
    ids: Mapping[str, str]

    #: Woraus die Flaeche ist, fuer das Bild.
    flaeche = "Beton"

    #: Was eine Linie sagt, die bis zum Bruch nicht fliesst.
    OHNE_FLIESSEN = "Bis zum Bruch fliesst kein Stahl: der Beton versagt zuerst."

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
    def rechenart(self) -> str:
        """Die Rechenart je Beton in Worten (:func:`~opencivil.querschnitt.gesetzwahl.arten_text`)."""
        return arten_text(self.wahl, self.betone)

    #: In den Analysen rechnet der ungerissene Teil immer mit ``E_cm/(1+phi)``:
    #: die Kriechzahl wirkt bei jeder Rechenart.
    mit_kriechzahl = True

    @property
    def beschriftung(self) -> str:
        """Die Wahl in Worten, mit der Rechenart je Beton (:meth:`~opencivil.querschnitt.gesetzwahl.Rechenwahl.beschriftung`)."""
        return self.wahl.beschriftung(self.betone)

    @property
    def modulbezug(self) -> Modulbezug:
        """
        Der reine Betonquerschnitt, ungerissen und ohne Stahl, mit ``E_cm``:
        der Bruttoquerschnitt (:meth:`~opencivil.nachweis.rissgroessen.Bruttoquerschnitt.traegheit`).
        """
        return Modulbezug(
            I=self.brutto.traegheit(self.seite.um_y), A=self.A, E=self.E_cm,
            zeichen="E_{cm}", text="E_cm",
            erklaerung=("Der äquivalente E-Modul ist der Modul, den ein reiner "
                        "Betonquerschnitt bräuchte – ungerissen, ohne Stahl, elastisch –, um "
                        "sich unter der laufenden Kraft gleich stark zu verformen wie der "
                        "bewehrte Querschnitt."),
            hinweis=("E_eq: der E-Modul, den der reine Betonquerschnitt – ungerissen, ohne "
                     "Stahl, elastisch – bräuchte, um sich gleich stark zu verformen; gezählt "
                     "ab dem Zustand ohne laufende Kraft."))

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
    def vorgespannt(self) -> bool:
        """Ob Spannglieder mit Vordehnung den Beton druecken -- sie verschieben den Riss."""
        return self.brutto.vorspannung is not None

    # -- Was nur das Paar weiss --------------------------------------------------

    def tiefe(self, w: Zwischenwerte, ein: Callable[[str], "Wert"]) -> "Wert":
        """Die Tiefe ``h``, ueber die die Linie laeuft -- wie das Paar sie misst."""
        raise NotImplementedError

    def herleitung_bruttoquerschnitt(self, p: Protokoll, w: Zwischenwerte,
                                     ein: Callable[[str], "Wert"],
                                     h: "Wert") -> Tuple["Wert", "Wert"]:
        """``A`` und ``I`` als Werte der Herleitung -- woher sie kommen, weiss das Paar."""
        raise NotImplementedError

    def herleitung_dicke_unter_zug(self, p: Protokoll, w: Zwischenwerte, h: "Wert") -> "Wert":
        """Die rissaktive Dicke unter Zug, ``t`` -- wie das Paar sie misst."""
        raise NotImplementedError

    # -- Die Herleitung ----------------------------------------------------------

    def herleitung_gesetze(self, p: Protokoll, w: Zwischenwerte, linie: "Linie",
                           ein: Callable[[str], "Wert"], werte: Mapping[str, "Wert"]
                           ) -> Tuple["Wert", "Wert", "Wert"]:
        """
        Was ein Paar aus Stahlbeton vor dem Ende der Linie schreibt: den
        wirksamen Modul, den Beton ungerissen und gerissen, wie die Loeser ihn
        rechnen -- aus derselben Stelle
        (:func:`~opencivil.querschnitt.gesetzwahl.betongesetz`) --, den Riss
        (:meth:`herleitung_riss`), die Fliessdehnung jedes Stahls und die
        Grenzdehnungen. Zurueck die Tiefe und ``A``, ``I`` des
        Bruttoquerschnitts.
        """
        wahl = self.wahl
        phi = w.zahl("phi", r"\varphi", wahl.kriechzahl, stellen=2)
        E_c_eff = w.spannung("E_c_eff", "E_{c,eff}",
                             wirksamer_modul(ein("E_cm").groesse.si, wahl.kriechzahl))
        p.formel(E_c_eff, r"\frac{@E_cm}{1 + @phi}", {"E_cm": ein("E_cm"), "phi": phi},
                 titel="Wirksamer Elastizitätsmodul", referenz=REFERENZ_KRIECHEN)

        p.erklaerung(
            "Ungerissen (Zustand I) trägt der Beton Druck und Zug, linear mit E_c,eff "
            "– bis zum Riss: wo der Querschnitt reisst, sagt die Rissbedingung am "
            "Bruttoquerschnitt, und nur dort zählt die Zugfestigkeit. Darüber gilt "
            "der ungerissene Zustand nicht mehr, auch nicht zum Vergleich. Gerissen "
            "(Zustand II) trägt der Beton keinen Zug, und im Druck gilt das Gesetz der "
            "gewählten Rechenart.")
        beton = {"f_c": ein("f_c"), "E_c": E_c_eff, "eps_c1d": ein("eps_c1d"),
                 "eps_c2d": ein("eps_c2d")}
        BetonUngerissen(E_c=E_c_eff.groesse.si).protokoll(p, beton, titel="Ungerissen (Zustand I)")
        betongesetz(wahl, self.art, f_c=beton["f_c"].groesse.si, E_c=ein("E_cm").groesse.si,
                    eps_c1d=beton["eps_c1d"].groesse.si, eps_c2d=beton["eps_c2d"].groesse.si
                    ).protokoll(p, beton, titel="Gerissen (Zustand II)", basis=w.basis)
        if wahl.arten.einheitlich is None:
            p.text("Die Betone rechnen je mit ihrer Rechenart; gezeigt ist das Gesetz "
                   "des Betons, der zuerst reisst.")
        if self.art.mit_block:
            p.erklaerung(
                "Der Spannungsblock ist ein Modell für den Bruch: unter "
                "(1 − 0.85)·ε_c2d trägt der Beton darin nichts. Über dem Riss ist die "
                "Linie mit ihm darum weicher als der Querschnitt; ihr Ende ist der "
                "Widerstand der 0.85·x-Vereinfachung. Ein Modul hängt an ihm nicht: "
                "die Kriechzahl wirkt nur auf den ungerissenen Teil.")
        else:
            p.erklaerung(
                "Unter 1 rechnet die Parabel k_σ nicht: dort hätte ihr Nenner im "
                "ansteigenden Ast eine Nullstelle. So weit kommt es mit dem kriechweichen "
                "Modul und charakteristischen Werten; mit k_σ = 1 ist der Beton bis f_c "
                "bei ε_c1d linear.")
        satz = wahl.saetze.einheitlich
        if satz is Werkstoffsatz.CHARAKTERISTISCH:
            p.text("Mit charakteristischen Werten: f_ck statt f_cd, f_yk statt f_yd.")
        elif satz is None:
            p.text("Mit gemischten Werten: jeder Baustoff rechnet mit seinem Wertesatz, wie "
                   "gewählt. Ein Widerstand heisst darum weder Rd noch Rk, sondern schlicht R.")

        h = self.tiefe(w, ein)
        A, I = self.herleitung_riss(p, w, linie, ein, h)

        p.erklaerung(
            "Der Fliessbeginn ist der Punkt, an dem die am stärksten gezogene Lage die "
            "Fliessdehnung erreicht. Danach wächst die Kraft nur noch wenig: die "
            "Druckzone wird kleiner, der Hebelarm grösser, und der Beton füllt sein "
            "Gesetz, bis eine Grenzdehnung erreicht ist. Im Bild heisst die Kraft beim "
            "Fliessbeginn M_y bzw. N_y, am Ende M_Rd bzw. N_Rd – mit "
            "charakteristischen Werten Rk statt Rd. Das Ende ist der Widerstand der "
            "Tragsicherheit, wenn sie dieselbe Rechenwahl trifft.")
        # Je Stahl seine Fliessdehnung -- unten und oben duerfen verschiedene liegen.
        for stahl in self.staehle:
            f_s, E_s = werte[stahl.id_von(wahl.satz(stahl).stahl)], werte[stahl.id_von("E_s")]
            name, symbol = (("eps_y", r"\varepsilon_{y}") if len(self.staehle) == 1 else
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
        return h, A, I

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
        vorspannung = _Abzug(protokoll_vorspannung(p, w, self.brutto, ecke, ein))
        p.formel(w.moment("M_Riss_N", "M_{Riss}(N)", linie.riss),
                 rf"\left(@f{vorspannung.vorlage} - \frac{{@N}}{{@A}}\right) \cdot @W",
                 {"f": f_ct_eff, "N": w.kraft("N", "N", linie.fest), "A": A, "W": W,
                  **vorspannung.werte},
                 titel="Rissmoment bei der Normalkraft", referenz=vorspannung.referenz)

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
        vorspannung = _Abzug(protokoll_vorspannung(p, w, self.brutto, zug.ecke, ein))
        if self.einachsig:
            # Es reisst der Rand, den M zieht -- mit Vorspannung auch der
            # andere, wenn sie ihn schon zieht. Ohne Moment zaehlt der Rand nicht.
            gezogen = zug.sigma_M > 0.0 if M != 0.0 else True
            rand = v if (M >= 0.0) == gezogen else w.laenge(
                "v_d", "v_d", self.gerissen.oben,
                "Abstand des gedrückten Rands vom Schwerpunkt, negativ")
            p.formel(N_Riss,
                     rf"\left(@f{vorspannung.vorlage} - \frac{{@M \cdot @v}}{{@I}}\right) \cdot @A",
                     {"f": f_ct_eff, "M": M_wert, "v": rand, "I": I, "A": A,
                      **vorspannung.werte},
                     titel="Rissnormalkraft beim Moment", referenz=vorspannung.referenz)
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
        p.formel(N_Riss, rf"\left(@f{vorspannung.vorlage} - @sigma\right) \cdot @A",
                 {"f": f_ct_eff, "sigma": sigma, "A": A, **vorspannung.werte},
                 titel="Rissnormalkraft beim Moment", referenz=vorspannung.referenz)

    # -- Der reine Betonquerschnitt des Moduls ------------------------------------

    def herleitung_traegheit(self, p: Protokoll, w: Zwischenwerte, I: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des Moduls ueber dem Moment: der Bruttoquerschnitt."""
        if self.einachsig:
            p.erklaerung(f"Der reine Betonquerschnitt ist der Bruttoquerschnitt, um die "
                         f"Achse der Biegung: I_c = {I.symbol.replace('_', '')}.")
        else:
            p.erklaerung(
                "Der reine Betonquerschnitt ist der Bruttoquerschnitt. Unter reiner Biegung "
                "kippt auch seine Nulllinie, und senkrecht zur Achse der Biegung krümmt er "
                "sich darum stärker, als I allein sagt: wie ein Querschnitt mit I_c. Sonst "
                "zeigte ein ungerissener unsymmetrischer Querschnitt schon seiner Form wegen "
                "einen kleineren Modul.")
        return protokoll_traegheit(p, w, self.brutto, self.seite.um_y, I, name="I_c",
                                   symbol="I_c", titel="Reiner Betonquerschnitt")

    def herleitung_flaeche(self, p: Protokoll, w: Zwischenwerte, A: "Wert") -> "Wert":
        """Der reine Betonquerschnitt des Moduls ueber der Normalkraft: der Bruttoquerschnitt."""
        bezug = w.flaeche("A_c", "A_c", self.A)
        p.erklaerung(f"Der reine Betonquerschnitt ist der Bruttoquerschnitt: A_c = {A.symbol}.")
        p.wert(bezug, titel="Reiner Betonquerschnitt")
        return bezug


class _Abzug:
    """Was die Vorspannung in eine Rissbedingung schreibt -- ohne sie nichts."""

    def __init__(self, sigma_p: Optional["Wert"]) -> None:
        self.vorlage = "" if sigma_p is None else " - @sp"
        self.werte = {} if sigma_p is None else {"sp": sigma_p}
        self.referenz = None if sigma_p is None else REFERENZ_VORSPANNUNG
