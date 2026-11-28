"""
opencivil/mauerwerk/nachweise.py -- die Nachweise einer Wand: Normalkraft und Teilflächen.

VERANTWORTUNG:
Je Pfeiler und Kombination die Normalkraft mit Knicken und Ausmitte
(:class:`Normalkraft`), je Sturzauflager und Kombination die Pressung unter
ihm (:class:`Teilflaechen`) -- nach SIA 266:2015. Beide lesen den Befund der
Wand (:class:`~opencivil.mauerwerk.werk.Wandbefund`): ihre Werte, ihre
Pfeiler und was die Kombinationen ihnen geben. Rechnet die Wand nicht, ist
jede Stelle nicht führbar, und der Grund sagt, warum.

DIE NORMALKRAFT (4.3.1.3, Gl. (11)):
N_xd am Fuss des Pfeilers gegen N_xRd = k_N · l_w · t_w · f_xd, mit der
Breite des Pfeilers als l_w. k_N kommt aus der Rechnung nach Theorie
2. Ordnung (:mod:`~opencivil.mauerwerk.knicken`): am Kopf greift die
Normalkraft mit der Ausmitte der Lasten an, M_d / N_Ld, wo er sich drehen
kann, am Fuss mit der Vorgabe e_u; ein eingespannter Rand dreht sich nicht.
Drücken die Lasten am Kopf nicht, lässt sich der Nachweis nicht führen:
unbewehrtes Mauerwerk trägt keinen Zug (4.1.2). h_Ed nach Gl. (8)
steht zur Auskunft daneben: nach h_w / h_Ed ordnet Figur 19.

Trägt der Pfeiler in einer Kombination auch Schub, und steht die
Normalkraft quer zur Wand ausmittig, gilt Gl. (17) (4.3.3.1): l_w wird zur
gedrückten Länge l_2 = l_w − 2 · M_z2d / N_xd (:func:`gedrueckte_laenge`).
Den Schub selbst weist :mod:`~opencivil.mauerwerk.schub` nach.

DIE TEILFLÄCHEN (4.2.1.2, Gl. (4)):
Unter jedem Auflager eines Sturzes R_d gegen R_Rd = k_m · f_xd · A_0 mit
A_0 = a · t_w. Das Auflager endet am Rand der Öffnung, und der Sturz ist so
breit wie die Wand (nach Vorgabe, nicht nachgeschlagen): die Fläche A_1 mit
demselben Schwerpunkt ist A_0 selbst, also k_m = 1.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Befundbezug, Eingaben
from opencivil.core.einheiten import M, Groesse
from opencivil.core.latex import als_text
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Fallausgang, Fallbefund, Teilnachweis,
    Vergleich, grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef, kennung_aus
from opencivil.mauerwerk import knicken
from opencivil.mauerwerk.lasten import Abtrag
from opencivil.mauerwerk.modell import Halterung, Pfeiler

if TYPE_CHECKING:
    from opencivil.mauerwerk.werk import Mauerwerkswand, Wandbefund

#: Wo die Regeln der Teilflächen stehen.
REFERENZ_TEILFLAECHE = "SIA 266:2015, 4.2.1.2, Gl. (4), Figur 2"
REFERENZ_H_ED = "SIA 266:2015, 4.3.1.2, Gl. (8)"
REFERENZ_GL_17 = "SIA 266:2015, 4.3.3.1, Gl. (17)"

#: Unter diesem Betrag in SI ist eine Kraft, ein Moment oder eine Ausmitte null.
NULL = 1e-9


@dataclass(frozen=True)
class Stelle:
    """Wo ein Nachweis urteilt: an einem Pfeiler oder Sturzauflager, in einer Kombination."""

    ort: str
    """«P1» oder «O1 links»."""

    kombination: str

    @property
    def name(self) -> str:
        return f"{self.ort} – {self.kombination}"

    @property
    def kennung(self) -> str:
        return kennung_aus(self.name)


@dataclass(kw_only=True)
class Stellenausgang(Fallausgang):
    """Wie eine Stelle ausging -- und welche, für das Bild der Wand."""

    stelle: Stelle
    knicken: Optional[knicken.Knickergebnis] = None
    """Bei der Normalkraft, was die Rechnung nach Theorie 2. Ordnung fand."""


class Wandnachweis(Teilnachweis):
    """
    Was beide Nachweise teilen: je Stelle ein Erfüllungsgrad, der Befund der
    Wand als Eingang, und die Stellen, an denen nicht geführt werden kann.
    """

    FELD: str = ""
    """Wie der Nachweis im Aufbau und in seinen Kennungen heisst."""

    def __init__(self, wand: "Mauerwerkswand", stellen: Sequence[Stelle]) -> None:
        if not stellen:
            raise ValueError(f"Der Nachweis «{self.LANGNAME}» braucht mindestens eine Stelle.")
        self.wand = wand
        self.stellen = list(stellen)
        basis = f"{wand.id}.nachweis.{self.FELD}"
        self.d_ausnutzung: Dict[str, WertDef] = {
            s.name: grad_def(f"{basis}.{s.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{self.ART},{als_text(s.name)}}}",
                             f"Erfüllungsgrad {self.LANGNAME} – {s.name}")
            for s in self.stellen}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         befunde=[Befundbezug("wand", wand.rechnung.id)],
                         titel=f"{self.LANGNAME} – {wand.name}", abschnitt=wand.abschnitt())

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        befund: Wandbefund = e.befund("wand")
        p.titel(self.LANGNAME)
        if not befund.bereit:
            erste = next(m for m in befund.alle_meldungen if m.haelt_an)
            grund = f"Die Wand rechnet nicht: {erste.text}"
            p.hinweis(grund)
            return self.je_teil(p, self.stellen,
                                lambda s: Stellenausgang(stelle=s, begruendung=grund),
                                befund=Fallbefund())
        self.ansatz(p, befund)
        return self.je_teil(p, self.stellen, lambda s: self.stelle(p, befund, s),
                            befund=Fallbefund())

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        """Was für jede Stelle gilt, einmal vor ihnen."""

    def stelle(self, p: Protokoll, befund: "Wandbefund", s: Stelle) -> Stellenausgang:
        """Eine Stelle gerechnet und aufgeschrieben."""
        raise NotImplementedError

    @staticmethod
    def vergleichen(p: Protokoll, E: Wert, R: Wert, definition: WertDef) -> Vergleich:
        """Einwirkung ``E`` gegen Widerstand ``R``, in die Herleitung geschrieben."""
        v = Vergleich(E, R)
        v.bedingung(p, "Einwirkung gegen Widerstand")
        v.zeile(p, definition)
        return v

    @staticmethod
    def satz(v: Vergleich, namen: Sequence[str]) -> str:
        """«N_xRd = 812.3 kN ≥ N_xd = 600.0 kN.» -- ``namen`` die von Einwirkung und Widerstand."""
        return (f"{namen[1]} = {v.widerstand.formatiert()} kN {'≥' if v.erfuellt else '<'} "
                f"{namen[0]} = {v.einwirkung.formatiert()} kN.")


def ohne_einwirkung(p: Protokoll, s: Stelle) -> Stellenausgang:
    p.text(OHNE_EINWIRKUNG)
    return Stellenausgang(stelle=s, ausgang=UNBESCHRAENKT, begruendung=OHNE_EINWIRKUNG)


class Normalkraft(Wandnachweis):
    """Siehe Dateikopf."""

    LANGNAME = "Normalkraft"
    ART = "N"
    FELD = "normalkraft"

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        p.erklaerung(
            "Unter der Normalkraft biegt sich eine Wand aus, und die Ausmitte wächst. Der "
            "Pfeiler hält, solange er sich im Gleichgewicht verformen kann, ohne dass die "
            "Ausmitte irgendwo die Grenze der Figur 4 überschreitet. Die grösste Normalkraft, "
            "bei der das gerade noch gilt, ist k_N · l_w · t_w · f_xd.")
        p.ansatz(r"\chi_y \cdot \frac{h_{Ed}^{2}}{t_w} = 4.1 \cdot \tan\left(2.4 \cdot "
                 r"\frac{e_z}{t_w}\right) \cdot \left[1 + \tan^{2}\left(2.4 \cdot "
                 r"\frac{e_z}{t_w}\right)\right] \qquad h_{Ed} = \pi \cdot "
                 r"\sqrt{\frac{B_{yd}}{N_{xd}}} \qquad B_{yd} = E_{xd} \cdot "
                 r"\frac{l_w \cdot t_w^{3}}{12}",
                 titel="Krümmung der Wand unter der Ausmitte e_z, bis e_z = 0.375 · t_w",
                 referenz=knicken.REFERENZ_FIGUR_3, name="Krümmung einer Wand aus Mauerwerk")
        p.ansatz(r"\left|e_z\right| \le \min\left[0.375 \cdot t_w;\ \frac{t_w}{2} \cdot "
                 r"\left(1 - \frac{N_{xd}}{l_w \cdot t_w \cdot f_{xd}}\right)\right]",
                 titel="Die Ausmitte der verformten Wand, nirgends grösser",
                 referenz=knicken.REFERENZ_GRENZE,
                 name="Grenze der Ausmitte einer Wand aus Mauerwerk")
        p.ansatz(r"e_z(x) = e_u + \left(e_o - e_u\right) \cdot \frac{x}{h_w} + w(x) \qquad "
                 r"w''(x) = -\chi_y\left(e_z(x)\right) \qquad w(0) = w(h_w) = 0",
                 titel="Gleichgewicht der verformten Wand: Ausmitte der Last und Auslenkung w")
        p.text(f"Ein eingespannter Rand dreht sich nicht: dort ist w' = 0, und seine Ausmitte "
               f"folgt aus dem Gleichgewicht. Die Wand ist in {knicken.TEILE} gleiche Stücke "
               f"geteilt; die Normalkraft wächst in Schritten, die Ausmitten der Lasten bleiben, "
               f"bis die Wand kein Gleichgewicht mehr findet oder ihre Ausmitte die Grenze "
               f"erreicht.")
        p.annahme("B_yd = E_xd · I_y wie in Gl. (8) und Figur 5, ohne den Faktor "
                  "√(1 − N_x/(2 · A_x · f_xk)) der Figur 3; die Normalkraft über die ganze Höhe "
                  "so gross wie am Fuss; ein Gelenk, das sich bei e_z = 0.375 · t_w weiter "
                  "drehen könnte, zählt nicht – nach Vorgabe, nicht nachgeschlagen, die beiden "
                  "letzten auf der sicheren Seite.")
        if befund.wand.kopf is Halterung.EINGESPANNT:
            p.text("Der Kopf ist eingespannt: das Moment der Ausmitten der Lasten nimmt die "
                   "Einspannung auf.")

    def stelle(self, p: Protokoll, befund: "Wandbefund", s: Stelle) -> Stellenausgang:
        pf = pfeiler_von(befund, s.ort)
        a = befund.kombinationen[s.kombination]
        zw = Zwischenwerte(f"{self.id}.{s.kennung}")
        p.titel(f"{self.LANGNAME} – {s.name}", ebene=3)
        N = zw.kraft("N_xd", "N_{xd}", a.N[pf.name], "Normalkraft am Fuss des Pfeilers")
        p.wert(N, titel="Normalkraft am Fuss des Pfeilers, aus dem Lastabtrag")
        if N.groesse.si == 0.0:
            return ohne_einwirkung(p, s)
        ohne_druck = zug(p, s, pf, a)
        if ohne_druck is not None:
            return ohne_druck
        w = befund.werte
        t, h = befund.t, befund.wand.flaeche.hoehe
        l_w = zw.laenge("l_w", "l_w", pf.b, "Breite des Pfeilers", stellen=0)
        t_w = zw.laenge("t_w", "t_w", t, "Dicke der Wand", stellen=0)
        h_w = zw.wert("h_w", "h_w", Groesse.aus_si(h, M), 2, "Höhe der Wand")
        f_xd = zw.spannung("f_xd", "f_{xd}", w.f_xd * 1e6, "Druckfestigkeit der Wand", stellen=2)
        E_xd = zw.spannung("E_xd", "E_{xd}", w.E_xd * 1e6, "Elastizitätsmodul der Wand")
        e_o, e_u = ausmitten(p, zw, befund, a, pf)
        l, schub = l_w, abs(a.V[pf.name]) > NULL and ausmittig(e_o, e_u)
        if schub:
            p.text("Der Pfeiler trägt auch Schub, und die Normalkraft steht quer zur Wand "
                   "ausmittig: statt Gl. (11) gilt Gl. (17), mit der gedrückten Länge l_2 statt "
                   "l_w (4.3.3.1).")
            l = gedrueckte_laenge(p, zw, a, pf, N, l_w)
            if l.groesse.si <= 0.0:
                p.text("l_2 ≤ 0: die Resultierende liegt ausserhalb des Pfeilers – er kippt.")
                N_xRd = zw.kraft("N_xRd", "N_{xRd}", 0.0, "Normalkraftwiderstand des Pfeilers")
                v = self.vergleichen(p, N, N_xRd, self.d_ausnutzung[s.name])
                return Stellenausgang(stelle=s, ausgang=v,
                                      begruendung=self.satz(v, ("N_xd", "N_xRd")))
        h_Ed = zw.wert("h_Ed", "h_{Ed}", Groesse.aus_si(math.pi * math.sqrt(
            w.E_xd * 1e6 * l.groesse.si * t ** 3 / (12.0 * N.groesse.si)), M), 2,
            "Bezugswert der Knicklänge")
        p.formel(h_Ed, r"\pi \cdot \sqrt{\frac{@E \cdot @l \cdot @t^{3}}{12 \cdot @N}}",
                 {"E": E_xd, "l": l, "t": t_w, "N": N},
                 referenz=REFERENZ_GL_17 if schub else REFERENZ_H_ED,
                 name="Bezugswert der Knicklänge einer Wand")
        p.text(f"h_w / h_Ed = {h / h_Ed.groesse.si:.2f} – die Schlankheit, nach der Figur 19 "
               f"ordnet.")
        erg = knicken_unter(befund, l.groesse.si, N.groesse.si, e_o, e_u)
        k_N = zw.zahl("k_N", "k_N", erg.k_N, "Beiwert der Normalkraft nach Theorie 2. Ordnung")
        p.wert(k_N, titel="Beiwert der Normalkraft, gerechnet nach Theorie 2. Ordnung",
               referenz=knicken.REFERENZ_FIGUR_3)
        p.text(_grenze_text(erg, k_N.formatiert(), h, t))
        N_xRd = zw.kraft("N_xRd", "N_{xRd}", erg.k_N * l.groesse.si * t * w.f_xd * 1e6,
                         "Normalkraftwiderstand des Pfeilers")
        p.formel(N_xRd, r"@k \cdot @l \cdot @t \cdot @f",
                 {"k": k_N, "l": l, "t": t_w, "f": f_xd},
                 referenz=REFERENZ_GL_17 if schub else knicken.REFERENZ_K_N,
                 name="Normalkraftwiderstand eines Pfeilers aus Mauerwerk")
        if erg.bei_n_d is not None:
            z = erg.bei_n_d
            p.text(f"Unter N_xd ist die Ausmitte {_wo(z.hoehe, h)} am grössten, "
                   f"{abs(z.e_max) * t * 1e3:.0f} mm.")
        v = self.vergleichen(p, N, N_xRd, self.d_ausnutzung[s.name])
        return Stellenausgang(stelle=s, ausgang=v, begruendung=self.satz(v, ("N_xd", "N_xRd")),
                              knicken=erg)



def zug(p: Protokoll, s: Stelle, pf: Pfeiler, a: Abtrag) -> Optional[Stellenausgang]:
    """
    Nicht führbar, wenn die Lasten am Kopf nicht drücken -- sonst ``None``.
    Mit dem Eigengewicht ist N nie kleiner als N_L: das schliesst einen Zug
    am Fuss ein.
    """
    N_L, M_d = a.N_L[pf.name], a.M[pf.name]
    if N_L >= -NULL and (abs(N_L) > NULL or abs(M_d) <= NULL):
        return None
    grund = (f"Am Kopf des Pfeilers {pf.name} drücken die Lasten nicht: unbewehrtes Mauerwerk "
             f"trägt keinen Zug (SIA 266:2015, 4.1.2) – der Nachweis lässt sich nicht führen.")
    p.warnung(grund)
    return Stellenausgang(stelle=s, ausgang=NICHT_FUEHRBAR, begruendung=grund)


def ausmitten(p: Protokoll, zw: Zwischenwerte, befund: "Wandbefund", a: Abtrag,
              pf: Pfeiler) -> Tuple[Optional[Wert], Optional[Wert]]:
    """
    Die Ausmitten quer zur Wand am Kopf, M_d / N_Ld, und am Fuss, die
    Vorgabe e_u -- je ``None``, wo der Rand eingespannt ist.
    """
    e_o = _kopf(p, zw, befund, a.M[pf.name], a.N_L[pf.name])
    e_u = None
    if befund.e_u is not None:
        e_u = zw.laenge("e_u", "e_u", befund.e_u, "Ausmitte am Fuss", stellen=0)
        p.wert(e_u, titel="Ausmitte am Fuss, Vorgabe der Wand")
    return e_o, e_u


def ausmittig(e_o: Optional[Wert], e_u: Optional[Wert]) -> bool:
    """Ob die Normalkraft quer zur Wand ausmittig steht, an einem Rand, der sich drehen kann."""
    return any(e is not None and abs(e.groesse.si) > NULL for e in (e_o, e_u))


def knicken_unter(befund: "Wandbefund", l: float, N: float, e_o: Optional[Wert],
                  e_u: Optional[Wert]) -> knicken.Knickergebnis:
    """k_N der Wand und ihr Zustand unter ``N`` auf der Länge ``l`` in m (:mod:`.knicken`)."""
    w, t = befund.werte, befund.t
    return knicken.k_N(befund.wand.flaeche.hoehe / t,
                       None if e_u is None else e_u.groesse.si / t,
                       None if e_o is None else e_o.groesse.si / t, w.E_xd / w.f_xd,
                       N / (l * t * w.f_xd * 1e6))


def gedrueckte_laenge(p: Protokoll, zw: Zwischenwerte, a: Abtrag, pf: Pfeiler, N: Wert,
                      l_w: Wert) -> Wert:
    """
    l_2 = l_w − 2 · M_z2d / N_xd: so lang ist der Pfeiler am Fuss gedrückt,
    wenn die Resultierende um M_z2d / N_xd neben seiner Mitte steht. Der
    Betrag von M_z2d, denn es zählt nicht, nach welcher Seite.
    """
    M_z = zw.moment("M_z2d", "M_{z2d}", abs(a.M_z[pf.name]),
                    "Moment in der Wandebene am Fuss, Betrag", stellen=2)
    p.wert(M_z, titel="Moment in der Wandebene am Fuss des Pfeilers, aus dem Lastabtrag – sein "
                      "Betrag")
    l_2 = zw.laenge("l_2", "l_2", pf.b - 2.0 * M_z.groesse.si / N.groesse.si,
                    "Gedrückte Länge am Fuss", stellen=0)
    p.formel(l_2, r"@l - \frac{2 \cdot @M}{@N}", {"l": l_w, "M": M_z, "N": N},
             referenz=REFERENZ_GL_17, name="Gedrückte Länge am Fuss eines Pfeilers")
    return l_2


def _kopf(p: Protokoll, zw: Zwischenwerte, befund: "Wandbefund", M_d: float,
          N_L: float) -> Optional[Wert]:
    """Die Ausmitte der Lasten am Kopf, M_d / N_Ld -- ``None``, wo er eingespannt ist."""
    if befund.wand.kopf is Halterung.EINGESPANNT:
        return None
    if abs(N_L) <= NULL:
        p.text("Am Kopf greifen keine Lasten an, nur das Eigengewicht, mittig: e_o = 0.")
        return zw.laenge("e_o", "e_o", 0.0, "Ausmitte am Kopf")
    M = zw.moment("M_d", "M_d", M_d, "Moment der Ausmitten am Kopf", stellen=2)
    p.wert(M, titel="Moment der Ausmitten der Lasten am Kopf, aus dem Lastabtrag")
    N = zw.kraft("N_Ld", "N_{Ld}", N_L, "Normalkraft aus den Lasten, ohne Eigengewicht")
    p.wert(N, titel="Normalkraft aus den Lasten allein, ohne das Eigengewicht der Wand, "
                    "aus dem Lastabtrag")
    e_o = zw.laenge("e_o", "e_o", M_d / N_L, "Ausmitte am Kopf")
    p.formel(e_o, r"\frac{@M}{@N}", {"M": M, "N": N},
             titel="Ausmitte am Kopf – sie bleibt, wenn die Lasten wachsen")
    return e_o


def _wo(hoehe: float, h: float) -> str:
    """Wo in der Wand -- ``hoehe`` als Anteil ab dem Fuss: «am Kopf», «1.35 m über dem Fuss»."""
    if hoehe <= 0.0:
        return "am Fuss"
    if hoehe >= 1.0:
        return "am Kopf"
    return f"{hoehe * h:.2f} m über dem Fuss"


def _grenze_text(erg: knicken.Knickergebnis, k: str, h: float, t: float) -> str:
    """Was k_N begrenzt, als Satz -- ``k`` ist k_N, wie es dasteht."""
    if erg.grund == knicken.DRUCK:
        return ("k_N = 1: bis zur vollen Druckfestigkeit des Querschnitts findet die Wand ein "
                "Gleichgewicht (Gl. (7)).")
    z = erg.grenzzustand
    if erg.grund == knicken.AUSMITTE:
        if z is None or erg.k_N == 0.0:
            return ("Schon die Ausmitte der Lasten liegt über der Grenze der Figur 4: der "
                    "Pfeiler trägt keine Normalkraft.")
        return (f"Bei k_N = {k} erreicht die Ausmitte {_wo(z.hoehe, h)} mit "
                f"{abs(z.e_max) * t * 1e3:.0f} mm die Grenze nach Gl. (6) und Figur 4.")
    if erg.k_N == 0.0:
        return "Schon unter der kleinsten Last findet die Wand kein Gleichgewicht."
    return f"Über k_N = {k} findet die Wand kein Gleichgewicht mehr: sie knickt."


def pfeiler_von(befund: "Wandbefund", name: str) -> Pfeiler:
    return next(pf for pf in befund.pfeiler if pf.name == name)


class Teilflaechen(Wandnachweis):
    """Siehe Dateikopf."""

    LANGNAME = "Teilflächenpressung"
    ART = "TF"
    FELD = "teilflaechen"

    def ansatz(self, p: Protokoll, befund: "Wandbefund") -> None:
        p.erklaerung(
            "Ein Sturz liegt an seinen Enden auf dem Mauerwerk auf und drückt es dort auf der "
            "Fläche A_0 = a · t_w. Liegt die Fläche mitten in einer grösseren, verteilt sich der "
            "Druck, und das Mauerwerk trägt mehr; am Rand der Öffnung kann er das nicht.")
        p.annahme("Der Sturz ist so breit wie die Wand, und sein Auflager endet am Rand der "
                  "Öffnung: die Fläche A_1 mit demselben Schwerpunkt ist A_0 selbst – nach "
                  "Vorgabe, nicht nachgeschlagen.")

    def stelle(self, p: Protokoll, befund: "Wandbefund", s: Stelle) -> Stellenausgang:
        o_name, seite = s.ort.rsplit(" ", 1)
        o = next(x for x in befund.wand.oeffnungen if x.name == o_name)
        zw = Zwischenwerte(f"{self.id}.{s.kennung}")
        p.titel(f"{self.LANGNAME} – {s.name}", ebene=3)
        R = zw.kraft("R_d", "R_d", befund.kombinationen[s.kombination].R[(o_name, seite)],
                     "Kraft des Sturzauflagers")
        p.wert(R, titel="Kraft des Sturzauflagers, aus dem Lastabtrag")
        if R.groesse.si <= 0.0:
            return ohne_einwirkung(p, s)
        a = zw.laenge("a", "a", o.a, "Auflagerlänge des Sturzes", stellen=0)
        t_w = zw.laenge("t_w", "t_w", befund.t, "Dicke der Wand", stellen=0)
        A_0 = zw.flaeche("A_0", "A_0", o.a * befund.t, "Fläche des Auflagers")
        p.formel(A_0, r"@a \cdot @t", {"a": a, "t": t_w}, titel="Fläche des Auflagers")
        A_1 = zw.flaeche("A_1", "A_1", o.a * befund.t, "Fläche mit demselben Schwerpunkt")
        p.wert(A_1, titel="Fläche mit demselben Schwerpunkt: am Rand der Öffnung A_0 selbst")
        k_m = zw.zahl("k_m", "k_m", min(1.5, 0.5 * (1.0 + math.sqrt(A_1.groesse.si
                                                                     / A_0.groesse.si))),
                      "Beiwert der Teilflächenpressung", stellen=2)
        p.formel(k_m, r"\min\left[0.5 \cdot \left(1 + \sqrt{\frac{@A_1}{@A_0}}\right);\ "
                      r"1.5\right]", {"A_1": A_1, "A_0": A_0},
                 referenz=REFERENZ_TEILFLAECHE,
                 name="Beiwert der Teilflächenpressung im Mauerwerk")
        f_xd = zw.spannung("f_xd", "f_{xd}", befund.werte.f_xd * 1e6,
                           "Druckfestigkeit der Wand", stellen=2)
        R_Rd = zw.kraft("R_Rd", "R_{Rd}", k_m.groesse.si * f_xd.groesse.si * A_0.groesse.si,
                        "Widerstand des Auflagers")
        p.formel(R_Rd, r"@k \cdot @f \cdot @A", {"k": k_m, "f": f_xd, "A": A_0},
                 referenz=REFERENZ_TEILFLAECHE, name="Widerstand eines Sturzauflagers")
        v = self.vergleichen(p, R, R_Rd, self.d_ausnutzung[s.name])
        return Stellenausgang(stelle=s, ausgang=v, begruendung=self.satz(v, ("R_d", "R_Rd")))
