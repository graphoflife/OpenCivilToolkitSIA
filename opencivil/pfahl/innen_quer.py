"""
opencivil/pfahl/innen_quer.py -- der innere Widerstand eines Pfahls quer zu seiner Achse.

VERANTWORTUNG:
Der Nachweis :class:`InnererQuerwiderstand`, je Kombination, die den Pfahl
quer belastet (:meth:`~.pfahl.Pfahl.quer_belastet`): in jeder Tiefe der
Verläufe (:mod:`.steifigkeit`) Moment und Querkraft gegen den Widerstand des
Querschnitts (:mod:`.innen`), beide mal η_i (SIA 267:2013, 9.5.2.4.1, (50))::

    |M(z)| ≤ M_Rd(z) = η_i · M_R,d(N_V(z) / η_i)       (:func:`~.innen.biegewiderstand`)
    |V(z)| ≤ V_Rd(z) = η_i · V_R,d

DIE BIEGUNG:
N_V ist die Normalkraft in derselben Tiefe, Druck positiv. Im Bohrpfahl
zieht das Fachwerk der Querkraft an beiden Gurten, je zur Hälfte, zusammen
F_tVd = |V| · cot α (SIA 262:2025, 4.3.3.4.11, (51)) -- ein Zug in der
Achse: N_V = N − F_tVd, mit dem α der Querkraft. Der Mikropfahl hat kein
Fachwerk: N_V = N.

M_Rd wird an :data:`STUETZSTELLEN` gleich verteilten N_V gerechnet und
dazwischen linear gelesen (:func:`zwischen`): die Fläche der Widerstände ist
konvex, M_Rd in N also konkav -- die Gerade liegt darunter.

DIE QUERKRAFT:
* Bohrpfahl -- das Fachwerk (:func:`~opencivil.querschnitt.fachwerk.fachwerk`)
  mit der Wendel::

      d = D/2 + 2 · r_s / π     bis zum Schwerpunkt der gezogenen Stäbe (4.3.3.4.2)
      z = 0.9 · d               (4.3.3.4.2)
      V_Rd,s = 0.7 · A_sw / s_w · z · f_yd · cot α      (45), 4.3.3.4.4
      V_Rd,c = b_w · z · k_c · f_cd · sin α · cos α     (47)

  α ganzgradig zwischen 30° und 45°, unter Zug ab 40° (4.3.3.3.2, 4.3.3.3.3).
* Mikropfahl -- das Tragglied aus Stahl::

      V_R,d = A_v · f_yd / √3,   A_v = 2 · A / π          (SIA 263:2013, 5.1.4.1, (41))

NACH VORGABE, NICHT NACHGESCHLAGEN (notizbuch/Notizen/TODO.md):
* Gezogen ist die halbe Bewehrung, die Stäbe gleichmässig auf dem Kreis.
* b_w ist die Sehne des Kreises auf der Höhe des Druckgurts -- die kleinste
  Breite zwischen den Gurten.
* α_min = 30° auch unter Druck, wo 4.3.3.3.3 bei bedeutendem Druck 25° zuliesse.
* Die Wendel aus dem Stahl der Längsbewehrung.
* F_tVd als Zug in der Achse, mit dem α der Querkraft.
* A_v = 2 · A / π für Rohr und Vollstab; f_yd nach SIA 262 statt f_y / γ_M1.

EINHEITEN:
SI-Basis.
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Befundbezug, Eingabebezug, Eingaben
from opencivil.core.einheiten import GRAD, M, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import Nachweis, NachweisUrteil, Vergleich, grad_def
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.querkraft_buegel import REFERENZ_DIAGONALE
from opencivil.pfahl.innen import WAHL, Innenbefund, biegewiderstand, querschnitt
from opencivil.pfahl.pfahl import Kombination, Pfahl
from opencivil.pfahl.steifigkeit import Steifigkeitsbefund, Verlauf
from opencivil.querschnitt.analyse import KENNWERTE, werkstoff
from opencivil.querschnitt.fachwerk import beste_neigung, fachwerk
from opencivil.querschnitt.interaktion import Querschnitt
from opencivil.querschnitt.platte import (
    ALPHA_MAX, ALPHA_MIN, K_C, REFERENZ_ALPHA_MAX, REFERENZ_ALPHA_MIN, REFERENZ_K_C,
    druckfeldgrenzen,
)

#: An so vielen Normalkräften wird M_Rd gerechnet, dazwischen linear gelesen.
STUETZSTELLEN = 7

#: Der Hebelarm der inneren Kräfte als Teil der statischen Höhe.
HEBELARM = 0.9
REFERENZ_HEBELARM = "SIA 262:2025, 4.3.3.4.2"

#: Was eine Wendel ohne weiteren Nachweis trägt, als Teil senkrechter Bügel.
WENDEL = 0.7
REFERENZ_WENDEL = "SIA 262:2025, 4.3.3.4.3, (45); 4.3.3.4.4"

REFERENZ_LAENGSZUG = "SIA 262:2025, 4.3.3.4.11, (51)"
REFERENZ_ETA = "SIA 267:2013, 9.5.2.4.1, (50)"
REFERENZ_STAHL = "SIA 263:2013, 5.1.4.1, (41)"

#: Die Ganghöhe der Wendel, die in der Regel nicht überschritten wird.
S_W_REGEL = 0.40
REFERENZ_S_W = "SIA 267:2013, 9.6.3.2.4"

#: Ab diesem Teil des Querkraftwiderstands mindert die Querkraft den
#: Biegewiderstand des Stahls (SIA 263:2013, 5.1.5.1).
SCHUB_BIEGUNG = 0.5

#: Weniger Zug als das, in N, ist Rechenrauschen: am Fuss, der nicht trägt,
#: bleibt statt null ein Millionstel Newton.
RAUSCHEN = 1.0


def gezogen(N: float) -> bool:
    """Ob die Normalkraft ein Zug ist, Druck positiv -- über dem Rauschen."""
    return N < -RAUSCHEN


def stuetzstellen(von: float, bis: float) -> List[float]:
    """:data:`STUETZSTELLEN` Normalkräfte gleich verteilt von ``von`` bis ``bis`` -- eine, wo beide gleich sind."""
    if bis <= von:
        return [von]
    return [von + (bis - von) * i / (STUETZSTELLEN - 1) for i in range(STUETZSTELLEN)]


def zwischen(stellen: Sequence[float], werte: Sequence[float], x: float) -> float:
    """
    Der Wert in x, linear zwischen den Stützstellen -- null, wo einer der
    beiden Nachbarn nichts trägt: dazwischen ist unbekannt, wie viel.
    """
    if len(stellen) == 1:
        return werte[0]
    i = min(max(bisect.bisect_right(stellen, x) - 1, 0), len(stellen) - 2)
    t = (x - stellen[i]) / (stellen[i + 1] - stellen[i])
    a, b = werte[i], werte[i + 1]
    if t <= 0.0 or t >= 1.0:
        return a if t <= 0.0 else b
    return 0.0 if a == 0.0 or b == 0.0 else a + t * (b - a)


def anteil(einwirkung: float, widerstand: float) -> float:
    """|E| / R -- unendlich, wo nichts trägt und doch etwas wirkt."""
    if widerstand > 0.0:
        return abs(einwirkung) / widerstand
    return math.inf if einwirkung != 0.0 else 0.0


@dataclass(frozen=True)
class Schub:
    """Der Querkraftwiderstand für einen Bereich der Normalkraft: V_Rd, mal η_i, und das α des Fachwerks."""

    V_Rd: Wert
    alpha: Optional[Wert] = None
    """Nur beim Bohrpfahl -- der Mikropfahl hat kein Fachwerk."""

    def laengszug(self, V: float) -> float:
        """F_tVd = |V| · cot α (SIA 262:2025, 4.3.3.4.11, (51)), ohne Fachwerk null."""
        return 0.0 if self.alpha is None else abs(V) / math.tan(self.alpha.groesse.si)


@dataclass
class Innenquerfall:
    """In jeder Tiefe der Verläufe M_Rd und V_Rd einer Kombination, in SI -- für das Bild."""

    M_grenze: List[float]
    V_grenze: List[float]


@dataclass
class Innenquerbefund:
    """Je Kombination, nach ihrem Namen, die Grenzen."""

    faelle: Dict[str, Innenquerfall] = field(default_factory=dict)


class InnererQuerwiderstand(Nachweis):
    """Siehe Dateikopf."""

    THEMA = "Innerer Pfahlwiderstand quer"
    ART = "M-N"

    def __init__(self, pfahl: Pfahl, kombinationen: Sequence[Kombination], *,
                 steifigkeit: str, innen: str) -> None:
        self.pfahl = pfahl
        self.kombinationen = [k for k in kombinationen if pfahl.quer_belastet(k)]
        if not self.kombinationen:
            raise ValueError("Der innere Widerstand quer braucht eine Kombination, die den "
                             "Pfahl quer belastet.")
        basis = f"{pfahl.id}.nachweis.innen_quer"
        self.d_biegung: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.biegung",
                             rf"\alpha_{{eff,M,{als_text(k.name)}}}",
                             f"Erfüllungsgrad Biegung im Pfahl – {k.name}")
            for k in self.kombinationen}
        self.d_querkraft: Dict[str, WertDef] = {
            k.name: grad_def(f"{basis}.{k.kennung}.querkraft",
                             rf"\alpha_{{eff,V,{als_text(k.name)}}}",
                             f"Erfüllungsgrad Querkraft im Pfahl – {k.name}")
            for k in self.kombinationen}
        namen = pfahl.kurznamen("Querschnitt") + (["D"] if pfahl.bohrpfahl else [])
        super().__init__(basis, ausgaben=[*self.d_biegung.values(), *self.d_querkraft.values()],
                         bezuege=[Eingabebezug(n, pfahl.id_von(n)) for n in namen]
                         + [s.bezug(k) for s in pfahl.stoffe for k in KENNWERTE[s.art]],
                         befunde=[Befundbezug("steifigkeit", steifigkeit),
                                  Befundbezug("innen", innen)],
                         titel=f"Innerer Widerstand quer – {pfahl.name}",
                         abschnitt=pfahl.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll) -> Ausfuehrung:
        p.titel("Innerer Widerstand quer")
        p.erklaerung(
            "Quer belastet biegt sich der Pfahl: in jeder Tiefe wirken ein Moment und eine "
            "Querkraft, so wie die Steifigkeit sie gerechnet hat. Der Querschnitt muss beide "
            "tragen -- das Moment zusammen mit der Normalkraft in derselben Tiefe, die "
            "Querkraft im Beton mit der Wendel oder im Stahl des Tragglieds. Beide "
            "Widerstände mindert η_i, wie längs.")
        innen: Innenbefund = e.befund("innen")
        steifigkeit: Steifigkeitsbefund = e.befund("steifigkeit")
        verlaeufe = {v.name: v for v in steifigkeit.verlaeufe}
        normalkraefte = [x for k in self.kombinationen for x in verlaeufe[k.name].N]
        werte = Zwischenwerte(self.id)
        p.titel("Querkraftwiderstand", ebene=3)
        if self.pfahl.bohrpfahl:
            bereiche = sorted({gezogen(x) for x in normalkraefte})
            schub = self._fachwerk(e, p, werte, innen, bereiche)
        else:
            schub = dict.fromkeys((False, True), self._tragglied(e, p, werte, innen))
        q = querschnitt(innen.masse, [werkstoff(s, e.si_nach_id(), WAHL)
                                      for s in self.pfahl.stoffe])
        befund = Innenquerbefund()
        urteile: List[NachweisUrteil] = []
        for k in self.kombinationen:
            v = verlaeufe[k.name]
            kw = Zwischenwerte(f"{self.id}.{k.kennung}")
            p.titel(f"Innerer Widerstand quer – {k.name}", ebene=3)
            biegung, M_grenze = self._biegung(e, p, kw, k, v, q, innen, schub)
            querkraft, V_grenze = self._querkraft(p, kw, k, v, schub)
            urteile += [biegung, querkraft]
            befund.faelle[k.name] = Innenquerfall(M_grenze, V_grenze)
        return Ausfuehrung({}, urteile, befund)

    # -- Querkraftwiderstand ----------------------------------------------------

    def _fachwerk(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, innen: Innenbefund,
                  bereiche: Sequence[bool]) -> Dict[bool, Schub]:
        """Der Bohrpfahl: das Fachwerk mit der Wendel, je Bereich der Normalkraft -- Zug: ``True``."""
        p.text("Der Pfahl trägt die Querkraft wie der Steg eines Balkens: schräge "
               "Druckdiagonalen im Beton, die Wendel als Zugglied, die Längsstäbe als Gurt.")
        D = e.g("D").si
        r_s = werte.laenge("r_s", "r_s", innen.masse.r_s, "Radius des Bewehrungskreises")
        p.wert(r_s, titel="Radius des Kreises, auf dem die Längsstäbe liegen -- aus dem inneren "
                          "Widerstand", referenz="")
        d = werte.laenge("d", "d", D / 2.0 + 2.0 * innen.masse.r_s / math.pi,
                         "Statische Höhe des Pfahls")
        p.formel(d, r"\frac{@D}{2} + \frac{2 \cdot @r_s}{\pi}", {"D": e["D"], "r_s": r_s},
                 titel="Statische Höhe: bis zum Schwerpunkt der Stäbe in der gezogenen Hälfte",
                 referenz=REFERENZ_HEBELARM, name="Statische Höhe des Kreisquerschnitts")
        z = werte.laenge("z", "z", HEBELARM * d.groesse.si, "Hebelarm der inneren Kräfte")
        p.formel(z, rf"{fest(HEBELARM, 1)} \cdot @d", {"d": d}, referenz=REFERENZ_HEBELARM,
                 name="Hebelarm der inneren Kräfte")
        gurt = D / 2.0 - d.groesse.si + z.groesse.si
        b_w = werte.laenge("b_w", "b_w", 2.0 * math.sqrt(D ** 2 / 4.0 - gurt ** 2),
                           "Breite des Stegs")
        p.formel(b_w, r"2 \cdot \sqrt{\left(\frac{@D}{2}\right)^{2} - \left(\frac{@D}{2} - @d"
                      r" + @z\right)^{2}}", {"D": e["D"], "d": d, "z": z},
                 titel="Breite des Stegs: die Sehne des Kreises auf der Höhe des Druckgurts, "
                       "die kleinste zwischen den Gurten", referenz="",
                 name="Stegbreite des Kreisquerschnitts")
        A_sw = werte.flaeche("A_sw", "A_{sw}", 2.0 * math.pi * e.g("phi_w").si ** 2 / 4.0,
                             "Querschnitt der Wendel")
        p.formel(A_sw, r"2 \cdot \frac{\pi \cdot @phi^{2}}{4}", {"phi": e["phi_w"]},
                 titel="Querschnitt der Wendel: sie kreuzt den Schnitt zweimal", referenz="",
                 name="Querschnitt der Wendel")
        if e.g("s_w").si > S_W_REGEL:
            p.hinweis(f"Die Wendel steigt mehr als {S_W_REGEL:.2f} m je Gang; in der Regel nicht "
                      f"weiter, am Kopf enger ({REFERENZ_S_W}).")
        k_c = werte.zahl("k_c", "k_c", K_C, "Abminderung der Betondruckfestigkeit in der "
                                            "Druckdiagonalen", stellen=2)
        p.wert(k_c, referenz=REFERENZ_K_C)
        p.annahme("Nach Vorgabe, nicht nachgeschlagen: gezogen ist die halbe Bewehrung, die "
                  "Stäbe gleichmässig auf dem Kreis; b_w ist die Sehne auf der Höhe des "
                  "Druckgurts; die Wendel ist aus dem Stahl der Längsbewehrung; α_min = 30° "
                  "auch unter Druck. Die Querkraft zählt in jeder Tiefe, auch dort, wo "
                  "SIA 262:2025, 4.3.3.4.1, nahe dem Kopf die im Abstand z · cot α gelten "
                  "liesse.")
        beton, stahl = self.pfahl.stoffe
        w = {"A": A_sw, "s": e["s_w"], "z": z, "b_w": b_w, "k_c": k_c,
             "f_yd": e[stahl.eingabename("f_yd")], "f_cd": e[beton.eingabename("f_cd")]}
        return {zug: self._neigung(e, p, werte, w, zug=zug, beide=len(bereiche) > 1)
                for zug in bereiche}

    def _neigung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, w: Dict[str, Wert], *,
                 zug: bool, beide: bool) -> Schub:
        """
        Die Neigung mit dem grössten Widerstand, Wendel, Druckdiagonalen und
        V_Rd -- aus den Werten ``w`` des Fachwerks.
        """
        si = {name: x.groesse.si for name, x in w.items()}
        von, bis = druckfeldgrenzen(ALPHA_MIN, ALPHA_MAX, zug)
        punkt = beste_neigung([fachwerk(alpha=a, a_sw_s=WENDEL * si["A"] / si["s"], z=si["z"],
                                        b_w=si["b_w"], f_yd=si["f_yd"], f_cd=si["f_cd"],
                                        k_c=si["k_c"])
                               for a in range(von, bis + 1)])
        wo = (", unter Zug" if zug else ", unter Druck") if beide else ""
        n, i = ("_zug", ",Z") if zug else ("", "")
        alpha = werte.wert(f"alpha{n}", rf"\alpha{'_Z' if zug else ''}",
                           Groesse(punkt.alpha, GRAD), 0, "Neigung der Druckdiagonalen")
        p.wert(alpha, titel=f"Neigung der Druckdiagonalen{wo}: ganzgradig zwischen {von}° und "
                            f"{bis}° die mit dem grössten Widerstand",
               referenz=f"{REFERENZ_ALPHA_MAX}; {REFERENZ_ALPHA_MIN}")
        V_s = werte.kraft(f"V_Rd_s{n}", f"V_{{Rd,s{i}}}", punkt.V_Rd_s, "Widerstand der Wendel")
        p.formel(V_s, rf"{fest(WENDEL, 1)} \cdot \frac{{@A}}{{@s}} \cdot @z \cdot @f_yd \cdot "
                      r"\cot @alpha", {**w, "alpha": alpha},
                 titel=f"Widerstand der Wendel{wo}: 70 % senkrechter Bügel",
                 referenz=REFERENZ_WENDEL, name="Widerstand der Wendel")
        V_c = werte.kraft(f"V_Rd_c{n}", f"V_{{Rd,c{i}}}", punkt.V_Rd_c,
                          "Widerstand der Druckdiagonalen")
        p.formel(V_c, r"@b_w \cdot @z \cdot @k_c \cdot @f_cd \cdot \sin @alpha \cdot \cos @alpha",
                 {**w, "alpha": alpha}, titel=f"Widerstand der Druckdiagonalen{wo}",
                 referenz=REFERENZ_DIAGONALE, name="Widerstand der Druckdiagonalen im Pfahl")
        V_Rd = werte.kraft(f"V_Rd{n}", f"V_{{Rd{i}}}", e.g("eta_i").si * punkt.V_Rd,
                           "Querkraftwiderstand des Pfahls")
        p.formel(V_Rd, r"@eta \cdot \min\left[@s;\ @c\right]",
                 {"eta": e["eta_i"], "s": V_s, "c": V_c}, titel=f"Querkraftwiderstand{wo}",
                 referenz=REFERENZ_ETA, name="Querkraftwiderstand des Pfahls")
        return Schub(V_Rd, alpha)

    def _tragglied(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte,
                   innen: Innenbefund) -> Schub:
        """Der Mikropfahl: das Tragglied aus Stahl fliesst auf Schub."""
        A = werte.flaeche("A", "A", innen.A_s, "Querschnitt des Tragglieds")
        p.wert(A, titel="Querschnitt des Tragglieds nach der Abrostung -- aus dem inneren "
                        "Widerstand", referenz="")
        A_v = werte.flaeche("A_v", "A_v", 2.0 * innen.A_s / math.pi, "Wirksame Schubfläche")
        p.formel(A_v, r"\frac{2 \cdot @A}{\pi}", {"A": A},
                 titel="Wirksame Schubfläche des runden Tragglieds", referenz=REFERENZ_STAHL,
                 name="Wirksame Schubfläche eines Kreisquerschnitts")
        f_yd = e[self.pfahl.stahl.eingabename("f_yd")]
        V_Rd = werte.kraft("V_Rd", "V_{Rd}",
                           e.g("eta_i").si * A_v.groesse.si * f_yd.groesse.si / math.sqrt(3.0),
                           "Querkraftwiderstand des Pfahls")
        p.formel(V_Rd, r"@eta \cdot \frac{@A_v \cdot @f_yd}{\sqrt{3}}",
                 {"eta": e["eta_i"], "A_v": A_v, "f_yd": f_yd},
                 titel="Querkraftwiderstand des Tragglieds: der Stahl fliesst auf Schub bei "
                       "f_yd / √3", referenz=f"{REFERENZ_STAHL}; {REFERENZ_ETA}",
                 name="Querkraftwiderstand des Tragglieds")
        p.annahme("Nach Vorgabe, nicht nachgeschlagen: A_v = 2 · A / π für Rohr und Vollstab "
                  "-- die Norm verlangt die Fläche, die in Richtung der Querkraft trägt; in "
                  "dünnen Ringen mit gleich grossem Schubfluss trägt der Kreis mindestens so "
                  "viel. Dazu f_yd nach SIA 262 statt f_y / γ_M1 nach SIA 263, wie längs.")
        return Schub(V_Rd)

    # -- Je Kombination -----------------------------------------------------------

    def _biegung(self, e: Eingaben, p: Protokoll, werte: Zwischenwerte, k: Kombination,
                 v: Verlauf, q: Querschnitt, innen: Innenbefund,
                 schub: Dict[bool, Schub]) -> Tuple[NachweisUrteil, List[float]]:
        """In jeder Tiefe |M| gegen M_Rd mit der Normalkraft dort -- massgebend die knappste."""
        eta_i = e.g("eta_i").si
        N_V = [N - schub[gezogen(N)].laengszug(V) for N, V in zip(v.N, v.V)]
        stellen = stuetzstellen(min(N_V), max(N_V))
        M_stellen = [biegewiderstand(q, N, eta_i, innen.masse.n) for N in stellen]
        grenze = [zwischen(stellen, M_stellen, x) for x in N_V]
        mit = "N_V" if self.pfahl.bohrpfahl else "N"
        p.tabelle(kopf=[Mathe(rf"{mit}\ [\mathrm{{kN}}]"),
                        Mathe(rf"\eta_i \cdot M_{{Rd}}({mit} / \eta_i)\ [\mathrm{{kNm}}]")],
                  zeilen=[[Mathe(fest(N / 1e3, 0)), Mathe(fest(M_R / 1e3, 1))]
                          for N, M_R in zip(stellen, M_stellen)],
                  titel="Biegewiderstand an Stützstellen der Normalkraft, dazwischen linear: er "
                        "ist in N konkav, die Gerade liegt darunter", ausrichtung="rr")
        j = max(range(len(v.z)), key=lambda i: anteil(v.M[i], grenze[i]))
        z = werte.wert("z_M", "z", Groesse.aus_si(v.z[j], M), 2,
                       "Tiefe unter Terrain, wo das Moment dem Biegewiderstand am nächsten kommt")
        p.wert(z, referenz="")
        N = werte.kraft("N", "N", v.N[j], "Normalkraft dort, Druck positiv")
        p.wert(N, referenz="")
        if self.pfahl.bohrpfahl:
            bereich = schub[gezogen(v.N[j])]
            V = werte.kraft("V_M", r"\left|V\right|", abs(v.V[j]), "Querkraft dort, als Betrag")
            p.wert(V, referenz="")
            F = werte.kraft("F_tVd", "F_{tVd}", bereich.laengszug(v.V[j]),
                            "Längszugkraft aus der Querkraft")
            p.formel(F, r"@V \cdot \cot @alpha", {"V": V, "alpha": bereich.alpha},
                     titel="Längszugkraft aus der Querkraft, je zur Hälfte an beiden Gurten: ein "
                           "Zug in der Achse", referenz=REFERENZ_LAENGSZUG,
                     name="Längszugkraft aus der Querkraft")
            p.formel(werte.kraft("N_V", "N_V", N_V[j], "Normalkraft mit der Längszugkraft"),
                     r"@N - @F", {"N": N, "F": F},
                     titel="Normalkraft, mit der der Querschnitt biegt", referenz="",
                     name="Normalkraft mit der Längszugkraft aus der Querkraft")
        M_Ed = werte.moment("M_Ed", r"\left|M\right|", abs(v.M[j]), "Moment dort, als Betrag")
        p.wert(M_Ed, referenz="")
        M_Rd = werte.moment("M_Rd", "M_{Rd}", grenze[j], "Biegewiderstand dort")
        p.wert(M_Rd, titel=f"Biegewiderstand dort, η_i · M_Rd({mit} / η_i), zwischen den "
                           f"Stützstellen gelesen", referenz=REFERENZ_ETA)
        vergleich = Vergleich(M_Ed, M_Rd)
        vergleich.bedingung(p, "Moment gegen Biegewiderstand")
        vergleich.zeile(p, self.d_biegung[k.name], mit_urteil=True)
        return self.urteil(self.d_biegung[k.name], k.name, vergleich,
                           f"|M| = {M_Ed.formatiert()} kNm "
                           f"{'≤' if vergleich.erfuellt else '>'} M_Rd = {M_Rd.formatiert()} kNm "
                           f"in z = {z.formatiert()} m.",
                           langname="Biegung im Pfahl"), grenze

    def _querkraft(self, p: Protokoll, werte: Zwischenwerte, k: Kombination, v: Verlauf,
                   schub: Dict[bool, Schub]) -> Tuple[NachweisUrteil, List[float]]:
        """In jeder Tiefe |V| gegen V_Rd -- massgebend die knappste."""
        grenze = [schub[gezogen(N)].V_Rd.groesse.si for N in v.N]
        j = max(range(len(v.z)), key=lambda i: anteil(v.V[i], grenze[i]))
        z = werte.wert("z_V", "z", Groesse.aus_si(v.z[j], M), 2,
                       "Tiefe unter Terrain, wo die Querkraft dem Widerstand am nächsten kommt")
        p.wert(z, referenz="")
        V_Ed = werte.kraft("V_Ed", r"\left|V\right|", abs(v.V[j]), "Querkraft dort, als Betrag")
        p.wert(V_Ed, referenz="")
        vergleich = Vergleich(V_Ed, schub[gezogen(v.N[j])].V_Rd)
        vergleich.bedingung(p, "Querkraft gegen Querkraftwiderstand")
        vergleich.zeile(p, self.d_querkraft[k.name], mit_urteil=True)
        if not self.pfahl.bohrpfahl and any(abs(x) > SCHUB_BIEGUNG * g
                                            for x, g in zip(v.V, grenze)):
            p.hinweis("Die Querkraft erreicht mehr als die Hälfte ihres Widerstands: dort ist "
                      "der Biegewiderstand des Stahls abzumindern (SIA 263:2013, 5.1.5.1) -- "
                      "hier nicht berücksichtigt.")
        return self.urteil(self.d_querkraft[k.name], k.name, vergleich,
                           f"|V| = {V_Ed.formatiert()} kN "
                           f"{'≤' if vergleich.erfuellt else '>'} V_Rd = "
                           f"{vergleich.widerstand.formatiert()} kN in z = {z.formatiert()} m.",
                           art="V", langname="Querkraft im Pfahl"), grenze
