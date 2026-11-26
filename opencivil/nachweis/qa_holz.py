"""
opencivil/nachweis/qa_holz.py -- die Lastfaelle eines Holzquerschnitts nach SIA 265:2012.

VERANTWORTUNG:
Zwei Nachweise je Lastfall, mit ihrer Herleitung -- gerechnet wird in
:mod:`opencivil.holzbau.gleichungen`:

* **Biegung und Normalkraft** (:class:`HolzBiegungQA`): (6) oder (10) mit
  Normalkraft allein, (14) mit Biegung allein, (21) mit Zug und Biegung,
  (22) mit Druck und Biegung (4.2.1 bis 4.2.4).
* **Schub und Torsion** (:class:`HolzSchubQA`): (23) mit Querkraft allein,
  (24) mit Torsion allein, (25) mit beiden (4.2.5).

Linear, am Bruttoquerschnitt (4.1.2), mit den Werten aus
:class:`~opencivil.nachweis.qa_holz_werte.HolzwerteQA`: die Biegespannung an
der weitesten Faser, die Schubspannung nach Jourawski, die Torsion am
Rechteck. Die Bemessungswerte der Tabellen 6 und 7 gelten mit
``η = η_w·η_t``: η_w der Feuchteklasse der Analyse, η_t = 1.4 in einem
Lastfall, der stossartig ist (2.2.6), sonst 1.

DER ERFUELLUNGSGRAD:
Wie beim Stahl -- die Normalkraft bleibt, die Momente wachsen um ``λ``, bis
die Gleichung aufgeht: ``α = λ``. Ohne Moment, oder wo schon die
Normalkraft allein nicht traegt, steht die Normalkraft gegen ihren
Widerstand. In (25) wachsen Querkraft und Torsion zusammen.

QUERKRAFT IN BEIDEN RICHTUNGEN:
``τ_d = √(τ_y² + τ_z²)`` -- die beiden groessten Schubspannungen, als laegen
sie an derselben Stelle: auf der sicheren Seite (nach Vorgabe, nicht
nachgeschlagen).

WAS FEHLT -- GRAU:
Torsion an einem Querschnitt, der kein Rechteck ist
(:data:`~opencivil.nachweis.qa_holz_werte.TORSION_NUR_RECHTECK`).

VORZEICHEN:
N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links. Die Gleichungen nehmen
Betraege.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import AbstractSet, Dict, List, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.holzbau import gleichungen as gl
from opencivil.material.holz import REFERENZ_ETA, eta_t, zugglied_grund
from opencivil.nachweis.qa_holz_werte import (
    DRUCK, TORSION_NUR_RECHTECK, ZUG, HolzwerteQA, beiwert, kennwert, stoffbezuege,
)
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse

REFERENZ_BIEGUNG = "SIA 265:2012, 4.2.1–4.2.4"
REFERENZ_SCHUB = "SIA 265:2012, 4.2.5"

#: Der Erfuellungsgrad -- derselbe Ansatz wie beim Stahl, eine Seite in der Formelsammlung.
ERFUELLUNGSGRAD = r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}"

#: Die Gleichungen ohne Zahlen, je mit ihrem Titel und ihrem Namen in der
#: Formelsammlung -- f_d steht fuer η·f_d der Tabelle.
_MOMENTE = r"\frac{\sigma_{m,y,d}}{f_{m,y,d}} + \frac{\sigma_{m,z,d}}{f_{m,z,d}}"
ANSAETZE = {
    "(6)": (r"\sigma_{t,0,d} \le f_{t,0,d}", "Zug allein", "Zug im Holz"),
    "(10)": (r"\sigma_{c,0,d} \le f_{c,0,d}", "Druck allein, ohne Knicken",
             "Druck im Holz, ohne Knicken"),
    "(14)": (_MOMENTE + r" \le 1", "Biegung, ohne Normalkraft", "Biegung im Holz"),
    "(21)": (r"\frac{\sigma_{t,0,d}}{f_{t,0,d}} + " + _MOMENTE + r" \le 1", "Biegung und Zug",
             "Biegung und Zug im Holz"),
    "(22)": (r"\left(\frac{\sigma_{c,0,d}}{f_{c,0,d}}\right)^2 + " + _MOMENTE + r" \le 1",
             "Biegung und Druck", "Biegung und Druck im Holz"),
    "(23)": (r"\tau_d \le f_{v,d}", "Schub aus Querkraft", "Schub aus Querkraft im Holz"),
    "(24)": (r"\tau_{tor,d} \le f_{v,d}", "Schub aus Torsion", "Schub aus Torsion im Holz"),
    "(25)": (r"\frac{\tau_{tor,d}}{f_{v,d}} + \left(\frac{\tau_d}{f_{v,d}}\right)^2 \le 1",
             "Schub aus Querkraft und Torsion", "Schub aus Querkraft und Torsion im Holz"),
    "(29)": (r"\sigma_{c,0,d} \le k_c \cdot f_{c,0,d}", "Knicken unter zentrischem Druck",
             "Knicken eines Holzstabs unter Druck"),
    "(37)": (r"\frac{\sigma_{c,0,d}}{k_c \cdot f_{c,0,d}} + \frac{\sigma_{m,d}}{k_m \cdot f_{m,d}} "
             r"\le 1", "Knicken mit Biegung, je Achse", "Knicken und Biegung eines Holzstabs"),
    "(38)": (r"\sigma_{m,d} \le k_m \cdot f_{m,d}", "Kippen", "Kippen eines Holzträgers"),
}

#: Die Zeilen der Einwirkung: je Groesse des Lastfalls ihr Name und ihre Einheit.
_EINWIRKUNG = {"N": ("N_Ed", "kN"), "M_y": ("M_y,Ed", "kNm"), "M_z": ("M_z,Ed", "kNm"),
               "V_z": ("V_z,Ed", "kN"), "V_y": ("V_y,Ed", "kN"), "T": ("T_Ed", "kNm")}


def bezuege(analyse: Querschnittsanalyse, werte: HolzwerteQA) -> List[Eingabebezug]:
    """``A``, die Werte des Holzquerschnitts und die Kennwerte des Holzes."""
    return ([Eingabebezug("A", analyse.id_von("A"))] + werte.als_eingaben()
            + stoffbezuege(werte.stoff))


def einwirkung(p: Protokoll, analyse: Querschnittsanalyse, fall: Lastfall,
               groessen: Sequence[str]) -> None:
    """Die Einwirkung als Tabelle -- je Groesse, die zaehlt, eine Zeile; einachsig ohne M_z, V_y."""
    einachsig = analyse.biegung.einachsig
    zeilen = [[_EINWIRKUNG[g][0], Mathe(fest(getattr(fall, g) / 1e3, 1)), _EINWIRKUNG[g][1]]
              for g in groessen if not (einachsig and g in ("M_z", "V_y"))]
    p.tabelle(kopf=["Einwirkung", "Wert", ""], zeilen=zeilen, titel="Einwirkung",
              ausrichtung="lrl")


def ansaetze(p: Protokoll, gleichungen: AbstractSet[str]) -> None:
    """Die Gleichungen, die die Faelle brauchen, ohne Zahlen -- in der Folge der Norm."""
    for g, (latex, titel, name) in ANSAETZE.items():
        if g in gleichungen:
            p.ansatz(latex, titel=f"{g}: {titel}", referenz=gl.REFERENZEN[g], name=name)


def bemessungswerte(p: Protokoll) -> None:
    """Wie die Bemessungswerte der Tabellen in die Gleichungen kommen."""
    p.ansatz(r"f_d = \eta \cdot f_{d,\mathrm{Tab}} \qquad \eta = \eta_w \cdot \eta_t",
             titel="Die Bemessungswerte der Tabellen 6 und 7 gelten für Feuchteklasse 1 und "
                   "ohne stossartige Einwirkung",
             referenz=REFERENZ_ETA, name="Bemessungswerte des Holzes")


def _bruch(oben: str, *unten: float) -> str:
    """``\\frac{oben}{η · … · f}`` mit Zahlen: η mit zwei Stellen, die Festigkeit einer."""
    teile = [fest(u, 3 if i else 2) for i, u in enumerate(unten[:-1])] + [fest(unten[-1], 1)]
    return rf"\frac{{{oben}}}{{{r' \cdot '.join(teile)}}}"


# ===========================================================================
# Biegung und Normalkraft
# ===========================================================================


@dataclass
class _Fall:
    """Ein Lastfall am Querschnitt, in N/mm² -- was Gleichung und Herleitung teilen."""

    N: float
    """In N, positiv Zug."""

    M: Dict[str, float]
    """Je Achse das Moment in Nm, das zaehlt -- auch null."""

    eta: float
    sigma_N: float
    """Positiv Zug."""

    sigma_m: Dict[str, float] = field(default_factory=dict)
    """Je Achse der Betrag an der weitesten Faser."""

    f_m: Dict[str, float] = field(default_factory=dict)
    """Je Achse ``k_h·f_m,d`` -- ohne η."""

    biegung: Optional[gl.Biegung] = None


class HolzBiegungQA(Nachweis):
    """Biegung und Normalkraft eines Holzquerschnitts, je Lastfall -- siehe Dateikopf."""

    THEMA = "Holzquerschnitt"
    LANGNAME = "Biegung und Normalkraft"
    ART = "M-N"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 werte: HolzwerteQA, stossartig: AbstractSet[str] = frozenset()) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.werte = werte
        self.stossartig = frozenset(stossartig)
        """Die Namen der Lastfaelle, die stossartig sind -- mit η_t = 1.4."""

        basis = f"{analyse.id}.nachweis.holz"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Biegung und Normalkraft – {f.name}",
                             REFERENZ_BIEGUNG)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=bezuege(analyse, werte),
                         titel=f"Biegung und Normalkraft – {analyse.name}",
                         referenz=REFERENZ_BIEGUNG, abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        p.erklaerung(
            "Je Lastfall die Spannungen am Bruttoquerschnitt, linear: aus der Normalkraft "
            "σ = N/A, aus jedem Moment σ_m = M/W. Dann die Gleichung, die der Lastfall braucht. "
            "Die Normalkraft bleibt, die Momente wachsen um λ, bis die Gleichung aufgeht.")
        faelle = [(fall, self._rechnen(e, fall)) for fall in self.lastfaelle]
        bemessungswerte(p)
        ansaetze(p, {x.biegung.gleichung for _, x in faelle if x.biegung is not None})
        p.ansatz(ERFUELLUNGSGRAD,
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")
        urteile = [self._ein_fall(p, e, fall, x) for fall, x in faelle]
        return Ausfuehrung({}, urteile)

    def _rechnen(self, e: Eingaben, fall: Lastfall) -> _Fall:
        """Spannungen und Gleichung eines Lastfalls -- ohne Herleitung."""
        stoff = self.werte.stoff
        M_y, M_z = self.analyse.biegung.wirkt(fall.M_y, fall.M_z)
        eta = e.g("eta_w").si * eta_t(fall.name in self.stossartig)
        x = _Fall(N=fall.N, M={"y": M_y, "z": M_z}, eta=eta,
                  sigma_N=fall.N / (e.g("A").si * 1e6))
        for a in self.werte.achsen:
            x.sigma_m[a] = abs(x.M[a]) * 1e3 / (e.g(f"W_{a}").si * 1e9)
            k_h = e.g("k_h").si if self.werte.brettschicht and a == "y" else 1.0
            x.f_m[a] = k_h * kennwert(e, stoff, "f_m_d").groesse.si / 1e6
        f = {k: eta * kennwert(e, stoff, k).groesse.si / 1e6 for k in ("f_t_0_d", "f_c_0_d")}
        x.biegung = gl.biegung_normalkraft(
            x.sigma_N, x.sigma_m.get("y", 0.0), x.sigma_m.get("z", 0.0), f_t=f["f_t_0_d"],
            f_c=f["f_c_0_d"], f_m_y=eta * x.f_m["y"], f_m_z=eta * x.f_m.get("z", 1.0))
        return x

    def _ein_fall(self, p: Protokoll, e: Eingaben, fall: Lastfall, x: _Fall) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        einwirkung(p, self.analyse, fall, ("N", "M_y", "M_z"))
        b = x.biegung
        if b is None:
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        eta = beiwert(p, werte, e["eta_w"], fall.name in self.stossartig)
        stoff = self.werte.stoff
        zug = x.N > 0.0
        if zug and zugglied_grund(stoff):
            p.hinweis(zugglied_grund(stoff))
        glieder = []
        if x.N:
            glieder.append(self._normalspannung(p, e, werte, x, zug))
        momente = [self._biegespannung(p, e, werte, x, a) for a in self.werte.achsen
                   if x.sigma_m[a] > 0.0]
        referenz = gl.REFERENZEN[b.gleichung]
        N_Ed = werte.kraft("N_Ed", "N_{Ed}", x.N)
        if b.nur_normalkraft:
            links = glieder[0]
            if b.m == 0.0:
                zeichen = r"\le" if b.n <= 1.0 else ">"
                p.gleichung(rf"{links} = {fest(b.n, 3)} {zeichen} 1",
                            titel=f"{b.gleichung}: Normalkraft allein", referenz=referenz)
                text = f"{b.gleichung}, Normalkraft allein."
            else:
                p.gleichung(rf"\lambda = 0: \quad {links} = {fest(b.n, 3)} > 1",
                            titel="Schon die Normalkraft allein trägt nicht", referenz=referenz)
                text = f"{b.gleichung}: schon N_Ed allein überschreitet die Gleichung."
            v = Vergleich(N_Ed, self._normalkraftwiderstand(p, e, werte, eta, zug))
            v.zeile(p, d_grad)
            return self.urteil(d_grad, fall.name, v, text)
        mit_lambda = [rf"\lambda \cdot {m}" for m in momente]
        p.gleichung(rf"{' + '.join(glieder + mit_lambda)} = 1 \quad\Rightarrow\quad "
                    rf"\lambda = {fest(b.alpha, 3)}",
                    titel=f"{b.gleichung}: wie weit die Momente wachsen dürfen", referenz=referenz)
        betrag = math.hypot(x.M["y"], x.M["z"])
        M_Ed = werte.moment("M_Ed", "M_{Ed}", betrag)
        M_Rd = werte.moment("M_Rd", "M_{Rd}", b.alpha * betrag)
        p.formel(M_Rd, r"@lam \cdot @M", {"lam": werte.zahl("lambda", r"\lambda", b.alpha),
                                          "M": M_Ed},
                 titel="Widerstand in der Richtung der Einwirkung")
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        bei = f"bei N_Ed = {x.N / 1e3:.1f} kN" if x.N else "ohne Normalkraft"
        return self.urteil(d_grad, fall.name, v, f"{b.gleichung}, {bei}.")

    # -- Spannungen ------------------------------------------------------------------

    def _normalspannung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, x: _Fall,
                        zug: bool) -> str:
        """σ = |N|/A in die Herleitung -- und ihr Glied mit Zahlen, in (22) im Quadrat."""
        art = "t" if zug else "c"
        sigma = werte.spannung("sigma_N", rf"\sigma_{{{art},0,d}}", abs(x.sigma_N) * 1e6,
                               "Normalspannung", stellen=2)
        p.formel(sigma, r"\frac{@N}{@A}",
                 {"N": werte.kraft("N_betrag", r"|N_{Ed}|", abs(x.N)), "A": e["A"]},
                 titel="Zugspannung" if zug else "Druckspannung", name="Normalspannung im Holz")
        f = kennwert(e, self.werte.stoff, f"f_{art}_0_d").groesse.si / 1e6
        bruch = _bruch(fest(abs(x.sigma_N), 2), x.eta, f)
        return rf"\left({bruch}\right)^2" if x.biegung.gleichung == "(22)" else bruch

    def _biegespannung(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, x: _Fall,
                       a: str) -> str:
        """σ_m = |M|/W um ``a`` in die Herleitung -- und ihr Glied, mit Zahlen."""
        sigma = werte.spannung(f"sigma_m_{a}", rf"\sigma_{{m,{a},d}}", x.sigma_m[a] * 1e6,
                               f"Biegespannung um {a}", stellen=2)
        p.formel(sigma, r"\frac{@M}{@W}",
                 {"M": werte.moment(f"M_{a}_betrag", rf"|M_{{{a},Ed}}|", abs(x.M[a])),
                  "W": e[f"W_{a}"]},
                 titel=f"Biegespannung um {a}, an der weitesten Faser",
                 name="Biegespannung im Holz")
        f_m_d = kennwert(e, self.werte.stoff, "f_m_d").groesse.si / 1e6
        k_h = x.f_m[a] / f_m_d
        nenner = (x.eta, k_h, f_m_d) if self.werte.brettschicht and a == "y" else (x.eta, f_m_d)
        return _bruch(fest(x.sigma_m[a], 2), *nenner)

    def _normalkraftwiderstand(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                               eta: Wert, zug: bool) -> Wert:
        """``η f A`` -- mit dem Zeichen der Normalkraft, wie die Kennzahlen."""
        kurz = "f_t_0_d" if zug else "f_c_0_d"
        f, A = kennwert(e, self.werte.stoff, kurz), e["A"]
        si = eta.groesse.si * f.groesse.si * A.groesse.si
        R = werte.kraft("N_Rd", "N_{Rd}^{+}" if zug else "N_{Rd}^{-}", si if zug else -si)
        vorlage, name = ZUG if zug else DRUCK
        p.formel(R, vorlage, {"eta": eta, "f_t" if zug else "f_c": f, "A": A},
                 titel="Zugwiderstand" if zug else "Druckwiderstand, ohne Knicken",
                 referenz=gl.REFERENZ_6 if zug else gl.REFERENZ_10, name=name)
        return R


# ===========================================================================
# Schub und Torsion
# ===========================================================================


class HolzSchubQA(Nachweis):
    """Schub aus Querkraft und Torsion eines Holzquerschnitts, je Lastfall -- siehe Dateikopf."""

    THEMA = "Holzquerschnitt"
    LANGNAME = "Schub und Torsion"
    ART = "V+T"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 werte: HolzwerteQA, stossartig: AbstractSet[str] = frozenset()) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.werte = werte
        self.stossartig = frozenset(stossartig)
        basis = f"{analyse.id}.nachweis.holz_v"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{V,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Schub und Torsion – {f.name}", REFERENZ_SCHUB)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=bezuege(analyse, werte),
                         titel=f"Schub und Torsion – {analyse.name}", referenz=REFERENZ_SCHUB,
                         abschnitt=analyse.abschnitt)

    def _schub(self, fall: Lastfall) -> Dict[str, float]:
        """Je Richtung die Querkraft in N, die zaehlt -- einachsig nur z."""
        return {"z": fall.V_z, "y": self.analyse.biegung.querkraft_y(fall.V_y)}

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        p.erklaerung(
            "Je Lastfall die Schubspannung aus Querkraft nach Jourawski, τ = V/A_V, und aus "
            "Torsion am Rechteck, τ_tor = T/W_T. Dann die Gleichung, die der Lastfall braucht; "
            "mit beidem wachsen Querkraft und Torsion zusammen um λ.")
        bemessungswerte(p)
        gleichungen = set()
        for fall in self.lastfaelle:
            v, t = any(self._schub(fall).values()), bool(fall.T)
            if t and not self.werte.holz.rechteck:
                continue
            if v or t:
                gleichungen.add("(25)" if v and t else "(23)" if v else "(24)")
        ansaetze(p, gleichungen)
        if any(fall.V_y and fall.V_z for fall in self.lastfaelle) \
                and not self.analyse.biegung.einachsig:
            p.annahme("Mit Querkraft in y und in z zählt τ_d = √(τ_y² + τ_z²), als lägen "
                      "die beiden grössten Schubspannungen an derselben Stelle – nach Vorgabe, "
                      "nicht nachgeschlagen.")
        urteile = [self._ein_fall(p, e, fall) for fall in self.lastfaelle]
        return Ausfuehrung({}, urteile)

    def _ein_fall(self, p: Protokoll, e: Eingaben, fall: Lastfall) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        einwirkung(p, self.analyse, fall, ("V_z", "V_y", "T"))
        V = {r: v for r, v in self._schub(fall).items() if v}
        if not V and not fall.T:
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        if fall.T and not self.werte.holz.rechteck:
            p.hinweis(TORSION_NUR_RECHTECK)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, TORSION_NUR_RECHTECK)
        eta = beiwert(p, werte, e["eta_w"], fall.name in self.stossartig)
        f_v_d = kennwert(e, self.werte.stoff, "f_v_d")
        f_v = werte.spannung("f_v", r"\eta f_{v,d}", eta.groesse.si * f_v_d.groesse.si,
                             "Schubfestigkeit im Lastfall", stellen=2)
        p.formel(f_v, r"@eta \cdot @f", {"eta": eta, "f": f_v_d},
                 titel="Schubfestigkeit, mit η", referenz=REFERENZ_ETA,
                 name="Schubfestigkeit des Holzes im Lastfall")
        tau = self._querkraft(p, e, werte, V)
        tau_tor = self._torsion(p, e, werte, fall.T) if fall.T else None
        s = gl.schub_torsion(tau.groesse.si / 1e6 if tau else 0.0,
                             tau_tor.groesse.si / 1e6 if tau_tor else 0.0, f_v.groesse.si / 1e6)
        referenz = gl.REFERENZEN[s.gleichung]
        fv = f_v.groesse.si / 1e6
        if s.gleichung == "(25)":
            t_glied = (rf"\lambda \cdot \frac{{{fest(tau_tor.groesse.si / 1e6, 2)}}}"
                       rf"{{{fest(fv, 2)}}}")
            v_glied = (rf"\lambda^2 \cdot \left(\frac{{{fest(tau.groesse.si / 1e6, 2)}}}"
                       rf"{{{fest(fv, 2)}}}\right)^2")
            p.gleichung(rf"{t_glied} + {v_glied} = 1 \quad\Rightarrow\quad "
                        rf"\lambda = {fest(s.alpha, 3)}",
                        titel="(25): wie weit Querkraft und Torsion zusammen wachsen dürfen",
                        referenz=referenz)
            R = werte.spannung("tau_Rd", r"\tau_{Rd}", s.alpha * tau.groesse.si,
                               "Schubspannung aus Querkraft, bis (25) aufgeht", stellen=2)
            p.formel(R, r"@lam \cdot @tau",
                     {"lam": werte.zahl("lambda", r"\lambda", s.alpha), "tau": tau},
                     titel="So weit darf τ_d wachsen, mit der Torsion zusammen",
                     name="Schubwiderstand neben Torsion im Holz")
            v = Vergleich(tau, R)
            text = "(25), Querkraft und Torsion zusammen."
        else:
            E = tau if s.gleichung == "(23)" else tau_tor
            v = Vergleich(E, f_v)
            v.bedingung(p, titel=f"{s.gleichung}: {ANSAETZE[s.gleichung][1]}")
            text = f"{s.gleichung}, {ANSAETZE[s.gleichung][1]}."
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, text)

    def _querkraft(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte,
                   V: Dict[str, float]) -> Optional[Wert]:
        """τ je Richtung, mit beiden ihre Resultierende -- ``None`` ohne Querkraft."""
        taus: Dict[str, Wert] = {}
        for r, V_r in V.items():
            taus[r] = werte.spannung(f"tau_{r}", rf"\tau_{{{r},d}}",
                                     abs(V_r) / e.g(f"A_V_{r}").si, f"Schubspannung aus V_{r}",
                                     stellen=2)
            p.formel(taus[r], r"\frac{@V}{@A}",
                     {"V": werte.kraft(f"V_{r}_betrag", rf"|V_{{{r},Ed}}|", abs(V_r)),
                      "A": e[f"A_V_{r}"]},
                     titel=f"Schubspannung aus V_{r}, nach Jourawski",
                     name="Schubspannung aus Querkraft im Holz")
        if len(taus) < 2:
            return next(iter(taus.values()), None)
        tau = werte.spannung("tau_d", r"\tau_d", math.hypot(*(t.groesse.si for t in taus.values())),
                             "Schubspannung aus beiden Querkräften", stellen=2)
        p.formel(tau, r"\sqrt{@ty^2 + @tz^2}", {"ty": taus["y"], "tz": taus["z"]},
                 titel="Beide Querkräfte zusammen", name="Schubspannung aus zwei Querkräften")
        return tau

    def _torsion(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, T: float) -> Wert:
        tau = werte.spannung("tau_tor", r"\tau_{tor,d}", abs(T) / e.g("W_T").si,
                             "Schubspannung aus Torsion", stellen=2)
        p.formel(tau, r"\frac{@T}{@W}",
                 {"T": werte.moment("T_betrag", r"|T_{Ed}|", abs(T)), "W": e["W_T"]},
                 titel="Schubspannung aus Torsion, in der Mitte der langen Seite",
                 name="Schubspannung aus Torsion im Holz")
        return tau
