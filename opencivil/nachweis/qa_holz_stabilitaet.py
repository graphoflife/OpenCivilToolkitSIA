"""
opencivil/nachweis/qa_holz_stabilitaet.py -- Knicken und Kippen eines Holzstabs nach SIA 265:2012.

VERANTWORTUNG:
Je Stabilitaetsfall der Querschnittsanalyse ein Nachweis mit seiner
Herleitung, je Hauptachse fuer sich (4.2.8.5) -- gerechnet wird in
:mod:`opencivil.holzbau.gleichungen`:

* Knicken um eine Achse, wo der Stab gedrueckt ist und um sie eine
  Knicklaenge hat: die Schlankheit ``λ = L_K/i``, die relative nach (34) mit
  ``f_c,0,k`` und ``E_0,05`` aus Anhang B, ``k_c`` nach (30) und (31);
* Kippen um die starke Achse, wo ein Moment um sie wirkt und die Kipplaenge
  ``L_D`` nicht null ist: ``σ_m,crit`` nach (41), ``λ_rel,m`` nach (40),
  ``k_m`` nach (39);
* je Achse (29) mit Druck allein, (37) mit Druck und Biegung, (38) mit
  Biegung allein.

Der Erfuellungsgrad wie in der Tragsicherheit
(:mod:`opencivil.nachweis.qa_holz`): die Normalkraft bleibt, die Momente
wachsen um ``λ``; massgebend ist die Achse mit dem kleineren. Ohne Moment
steht die Druckkraft gegen den Knickwiderstand.

NACH VORGABE, NICHT NACHGESCHLAGEN:
* ``λ_rel`` und ``σ_m,crit`` mit den Werten aus Anhang B, ohne η_w: die
  Feuchteklasse mindert die Steifigkeit dort nicht.
* ``k_h`` gilt beim Brettschichtholz auch in (37) und (38), wie im
  Querschnitt.
* ψ zaehlt nicht: (37) und (38) nehmen das groesste Moment im Stab, wie es
  eingegeben ist.

WAS GRAU STEHT:
Kippen eines Querschnitts, der kein Rechteck ist: (41) gilt fuer das
Rechteck ``b × h`` (:data:`KIPPEN_NUR_RECHTECK`).

VORZEICHEN:
N < 0 Druck; M_y > 0 zieht unten, M_z > 0 links. Die Gleichungen nehmen
Betraege.
"""

from __future__ import annotations

import math
from typing import AbstractSet, Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.holzbau import gleichungen as gl
from opencivil.holzbau.querschnitt import starke_achse
from opencivil.material.holz import eta_t
from opencivil.nachweis.qa_holz import ERFUELLUNGSGRAD, ansaetze, bemessungswerte
from opencivil.nachweis.qa_holz_werte import (
    KENNWERTE, KENNWERTE_STAB, HolzwerteQA, beiwert, kennwert, stoffbezuege,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.biegung import Biegung
from opencivil.stahlbau.stabilitaet import Stabfall

#: Warum ein Querschnitt, der kein Rechteck ist, beim Kippen grau steht.
KIPPEN_NUR_RECHTECK = ("Kippen weist das Werkzeug beim Holz nur für ein Rechteck nach, mit (41). "
                       "Ist der Stab seitlich gehalten, gilt die Kipplänge L_D = 0.")

#: Was ein Fall sagt, in dem weder Knicken noch Kippen zaehlt.
NICHTS_ZU_PRUEFEN = ("Kein Knicken und kein Kippen: der Stab ist nicht gedrückt, wo er eine "
                     "Knicklänge hat, und kein Moment um die starke Achse wirkt über eine "
                     "Kipplänge.")

REFERENZ = "SIA 265:2012, 4.2.8; 4.2.9"


class HolzStabilitaetQA(Nachweis):
    """Knicken und Kippen eines Holzstabs, je Fall -- siehe Dateikopf."""

    THEMA = "Knicken und Kippen eines Holzstabs"
    LANGNAME = "Knicken und Kippen"
    ART = "Stab"

    def __init__(self, analyse: Querschnittsanalyse, faelle: Sequence[Stabfall],
                 werte: HolzwerteQA, stossartig: AbstractSet[str] = frozenset()) -> None:
        self.analyse = analyse
        self.faelle = list(faelle)
        self.werte = werte
        self.stossartig = frozenset(stossartig)
        basis = f"{analyse.id}.nachweis.holz_stab"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Knicken und Kippen – {f.name}", REFERENZ)
            for f in self.faelle}
        bezuege = ([Eingabebezug(k, analyse.id_von(k)) for k in ("A", "I_y", "I_z")]
                   + werte.als_eingaben() + stoffbezuege(werte.stoff, *KENNWERTE, *KENNWERTE_STAB))
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()), bezuege=bezuege,
                         titel=f"Knicken und Kippen – {analyse.name}", referenz=REFERENZ,
                         abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        p.erklaerung(
            "Der Stab hat den gezeichneten Querschnitt. Je Achse für sich: wo er gedrückt ist "
            "und eine Knicklänge hat, mindert k_c die Druckfestigkeit; um die starke Achse, wo "
            "ein Moment über eine Kipplänge wirkt, mindert k_m die Biegefestigkeit. Dann (37) "
            "mit Druck, (38) ohne. Die Normalkraft bleibt, die Momente wachsen um λ, bis die "
            "Gleichung aufgeht.")
        p.annahme("Die relative Schlankheit beim Knicken und beim Kippen mit f_c,0,k, f_m,k und "
                  "E_0,05 aus Anhang B, ohne η_w; beim Brettschichtholz mindert k_h auch in (37) "
                  "und (38) – nach Vorgabe, nicht nachgeschlagen.")
        bemessungswerte(p)
        ansaetze(p, self._gleichungen(e))
        p.ansatz(ERFUELLUNGSGRAD,
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")
        urteile = [self._ein_fall(p, e, fall) for fall in self.faelle]
        return Ausfuehrung({}, urteile)

    def _gleichungen(self, e: Eingaben) -> set:
        """Welche Gleichungen die Faelle brauchen -- fuer die Ansaetze vorweg."""
        kipp = self._kippachse(e)
        gleichungen = set()
        for fall in self.faelle:
            M = self._momente(fall)
            for a in ("y", "z"):
                if fall.N < 0.0 and fall.knicklaenge(a) > 0.0:
                    gleichungen.add("(37)" if M[a] else "(29)")
                elif a == kipp and fall.L_D > 0.0 and M[a]:
                    gleichungen.add("(38)")
        return gleichungen

    def _kippachse(self, e: Eingaben) -> str:
        """Um welche Achse der Stab kippen kann: die starke."""
        return starke_achse(e.g("I_y").si, e.g("I_z").si)

    def _momente(self, fall: Stabfall) -> Dict[str, float]:
        """Je Achse das Moment in Nm, das zaehlt -- einachsig ohne M_z."""
        return dict(zip(("y", "z"), self.analyse.biegung.wirkt(fall.M_y, fall.M_z)))

    # -- Ein Fall ---------------------------------------------------------------

    def _ein_fall(self, p: Protokoll, e: Eingaben, fall: Stabfall) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        _einwirkung(p, self.analyse.biegung, fall)
        M = self._momente(fall)
        if fall.N == 0.0 and not any(M.values()):
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        kipp = self._kippachse(e)
        kippt = fall.L_D > 0.0 and M[kipp] != 0.0
        if kippt and not self.werte.holz.rechteck:
            p.hinweis(KIPPEN_NUR_RECHTECK)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, KIPPEN_NUR_RECHTECK)
        knickt = {a: fall.N < 0.0 and fall.knicklaenge(a) > 0.0 for a in ("y", "z")}
        achsen = [a for a in ("y", "z") if knickt[a] or (kippt and a == kipp)]
        if not achsen:
            p.text(NICHTS_ZU_PRUEFEN)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, NICHTS_ZU_PRUEFEN)
        if any(M[a] and fall.psi(a) != 1.0 for a in ("y", "z")):
            p.text("ψ zählt beim Holz nicht: (37) und (38) nehmen das grösste Moment im Stab, "
                   "wie es oben steht.")
        r = _Herleitung(p, e, werte, self.werte, beiwert(p, werte, e["eta_w"],
                                                         fall.name in self.stossartig),
                        fall, M, eta_t(fall.name in self.stossartig))
        ergebnisse = [r.achse(a, knickt[a], kippt and a == kipp) for a in achsen]
        return self._urteil(p, werte, r, d_grad, fall, min(ergebnisse, key=lambda x: x[1].alpha))

    def _urteil(self, p: Protokoll, werte: Zwischenwerte, r: "_Herleitung", d_grad: WertDef,
                fall: Stabfall, massgebend: Tuple[str, gl.Stabachse]) -> NachweisUrteil:
        """Der Vergleich der massgebenden Achse: die Momente gegen ihren Widerstand, ohne Druck."""
        a, x = massgebend
        N_Ed = werte.kraft("N_Ed", "N_{Ed}", fall.N)
        bei = f", bei N_Ed = {fall.N / 1e3:.1f} kN" if fall.N else ""
        if x.nur_druck:
            if x.biegung:
                p.text(f"Um {a} trägt schon die Druckkraft allein nicht: so weit müsste sie "
                       f"kleiner sein.")
            v = Vergleich(N_Ed, r.knickwiderstand(a, fall.N * x.alpha))
            v.zeile(p, d_grad)
            return self.urteil(d_grad, fall.name, v, f"{x.gleichung} um {a}{bei}.")
        M_Ed = werte.moment(f"M_{a}_Ed", rf"M_{{{a},Ed}}", abs(r.M[a]))
        M_Rd = werte.moment(f"M_{a}_Rd", rf"M_{{{a},Rd}}", x.alpha * abs(r.M[a]))
        p.formel(M_Rd, r"@lam \cdot @M", {"lam": werte.zahl("lambda", r"\lambda", x.alpha),
                                          "M": M_Ed},
                 titel="Widerstand in der Richtung der Einwirkung")
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, f"{x.gleichung} um {a}{bei}.")


def _einwirkung(p: Protokoll, biegung: Biegung, fall: Stabfall) -> None:
    """Die Einwirkung und der Stab als Tabelle -- einachsig ohne M_z."""
    zeilen = [["N_Ed", Mathe(fest(fall.N / 1e3, 1)), "kN"]]
    zeilen += [[f"M_{achse},Ed", Mathe(fest(M / 1e3, 1)), "kNm"]
               for achse, M in biegung.momente(fall.M_y, fall.M_z)]
    zeilen += [["L_K,y", Mathe(fest(fall.L_K_y, 2)), "m"],
               ["L_K,z", Mathe(fest(fall.L_K_z, 2)), "m"],
               ["L_D", Mathe(fest(fall.L_D, 2)), "m"]]
    p.tabelle(kopf=["Einwirkung und Stab", "Wert", ""], zeilen=zeilen,
              titel="Einwirkung und Stab – eine Länge null heisst gehalten", ausrichtung="lrl")


class _Herleitung:
    """Die Herleitung eines Falls, Achse fuer Achse -- mit den Werten, die die Achsen teilen."""

    def __init__(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, holz: HolzwerteQA,
                 eta: Wert, fall: Stabfall, M: Dict[str, float], eta_t_: float) -> None:
        self.p, self.e, self.werte, self.holz, self.eta, self.fall, self.M = (
            p, e, werte, holz, eta, fall, M)
        self.eta_zahl = e.g("eta_w").si * eta_t_
        self.sigma_c: Optional[Wert] = None
        if fall.N < 0.0:
            self.sigma_c = werte.spannung("sigma_c", r"\sigma_{c,0,d}", -fall.N / e.g("A").si,
                                          "Druckspannung", stellen=2)
            p.formel(self.sigma_c, r"\frac{@N}{@A}",
                     {"N": werte.kraft("N_betrag", r"|N_{Ed}|", -fall.N), "A": e["A"]},
                     titel="Druckspannung", name="Normalspannung im Holz")
        self.k_c: Dict[str, Wert] = {}

    def kennwert(self, kurz: str) -> Wert:
        return kennwert(self.e, self.holz.stoff, kurz)

    def zahl(self, kurz: str) -> float:
        """Ein Kennwert des Holzes in N/mm²."""
        return self.kennwert(kurz).groesse.si / 1e6

    # -- Je Achse --------------------------------------------------------------------

    def achse(self, a: str, knickt: bool, kippt: bool) -> Tuple[str, gl.Stabachse]:
        """Knicken, Kippen und die Gleichung um ``a`` -- ihr Ergebnis mit der Achse."""
        p = self.p
        p.titel(f"Um {a}", ebene=4)
        k_c = self._knicken(a) if knickt else 1.0
        k_m = self._kippen(a) if kippt else 1.0
        sigma_m = self._biegespannung(a)
        f_m = self.zahl("f_m_d") * (self.e.g("k_h").si if self._mit_k_h(a) else 1.0)
        sigma_c = self.sigma_c.groesse.si / 1e6 if self.sigma_c is not None and knickt else 0.0
        x = gl.stabachse(sigma_c, sigma_m, f_c=self.eta_zahl * self.zahl("f_c_0_d"),
                         f_m=self.eta_zahl * f_m, k_c_=k_c, k_m_=k_m)
        self._gleichung(a, x, sigma_c, sigma_m, k_c, k_m)
        return a, x

    def _mit_k_h(self, a: str) -> bool:
        return self.holz.brettschicht and a == "y"

    def _biegespannung(self, a: str) -> float:
        """σ_m um ``a`` in N/mm², in die Herleitung -- null ohne Moment."""
        if not self.M[a]:
            return 0.0
        sigma = self.werte.spannung(f"sigma_m_{a}", rf"\sigma_{{m,{a},d}}",
                                    abs(self.M[a]) / self.e.g(f"W_{a}").si,
                                    f"Biegespannung um {a}", stellen=2)
        self.p.formel(sigma, r"\frac{@M}{@W}",
                      {"M": self.werte.moment(f"M_{a}_betrag", rf"|M_{{{a},Ed}}|",
                                              abs(self.M[a])),
                       "W": self.e[f"W_{a}"]},
                      titel=f"Biegespannung um {a}, an der weitesten Faser",
                      name="Biegespannung im Holz")
        return sigma.groesse.si / 1e6

    def _knicken(self, a: str) -> float:
        p, werte, e = self.p, self.werte, self.e
        i = werte.laenge(f"i_{a}", rf"i_{a}", math.sqrt(e.g(f"I_{a}").si / e.g("A").si),
                         "Trägheitsradius")
        p.formel(i, r"\sqrt{\frac{@I}{@A}}", {"I": e[f"I_{a}"], "A": e["A"]},
                 titel=f"Trägheitsradius um {a}", name="Trägheitsradius")
        L = werte.laenge(f"L_K_{a}", rf"L_{{K,{a}}}", self.fall.knicklaenge(a) * 1e-3,
                         "Knicklänge")
        lam = werte.zahl(f"lam_{a}", rf"\lambda_{a}", L.groesse.si / i.groesse.si,
                         "Schlankheit", stellen=1)
        p.formel(lam, r"\frac{@L}{@i}", {"L": L, "i": i}, titel=f"Schlankheit um {a}",
                 referenz=gl.REFERENZ_SCHLANKHEIT, name="Schlankheit eines Holzstabs")
        rel = gl.lambda_rel(lam.groesse.zahl, self.zahl("f_c_0_k"), self.zahl("E_0_05"))
        lam_rel = werte.zahl(f"lam_rel_{a}", rf"\lambda_{{rel,{a}}}", rel,
                             "Relative Schlankheit beim Knicken")
        p.formel(lam_rel, r"\frac{@lam}{\pi} \cdot \sqrt{\frac{@f}{@E}}",
                 {"lam": lam, "f": self.kennwert("f_c_0_k"), "E": self.kennwert("E_0_05")},
                 titel=f"Relative Schlankheit um {a}", referenz=gl.REFERENZ_LAMBDA,
                 name="Relative Schlankheit beim Knicken von Holz")
        k_c = self.k_c[a] = werte.zahl(f"k_c_{a}", rf"k_{{c,{a}}}",
                                       gl.k_c(rel, self.holz.art.beta_c), "Knickbeiwert")
        if rel <= gl.LAMBDA_0:
            p.wert(k_c, titel=f"λ_rel,{a} nicht über 0.3: der Stab knickt nicht, k_c = 1",
                   referenz=gl.REFERENZ_K_C)
            return 1.0
        beta = werte.zahl("beta_c", r"\beta_c", self.holz.art.beta_c,
                          "Beiwert der Geradheit", stellen=1)
        k = werte.zahl(f"k_{a}", rf"k_{a}", 0.5 * (1.0 + beta.groesse.zahl * (rel - gl.LAMBDA_0)
                                                    + rel * rel), "Hilfswert beim Knicken")
        p.formel(k, r"0.5 \cdot \left(1 + @beta \cdot \left(@lam - 0.3\right) + @lam^2\right)",
                 {"beta": beta, "lam": lam_rel},
                 titel=f"Hilfswert um {a}, β_c für {self.holz.art.value}",
                 referenz=gl.REFERENZ_K_C, name="Hilfswert beim Knicken von Holz")
        p.formel(k_c, r"\frac{1}{@k + \sqrt{@k^2 - @lam^2}}", {"k": k, "lam": lam_rel},
                 titel=f"Knickbeiwert um {a}", referenz=gl.REFERENZ_K_C,
                 name="Knickbeiwert des Holzes")
        return k_c.groesse.zahl

    def _kippen(self, a: str) -> float:
        p, werte, holz = self.p, self.werte, self.holz.holz
        b = werte.laenge("b_D", "b", holz.breite(a) * 1e-3, "Breite des Rechtecks")
        h = werte.laenge("h_D", "h", holz.hoehe(a) * 1e-3, "Höhe des Rechtecks")
        L = werte.laenge("L_D", "a", self.fall.L_D, "Abstand der seitlichen Halterungen")
        krit = werte.spannung("sigma_crit", r"\sigma_{m,crit}",
                              gl.sigma_m_crit(L.groesse.si * 1e3, b.groesse.si * 1e3,
                                              h.groesse.si * 1e3, self.zahl("E_0_05")) * 1e6,
                              "Kippspannung", stellen=1)
        p.formel(krit, r"\frac{0.75 \cdot @E \cdot @b^2}{@a \cdot @h}",
                 {"E": self.kennwert("E_0_05"), "b": b, "a": L, "h": h},
                 titel=f"Kippspannung des Rechtecks, Biegung um {a}", referenz=gl.REFERENZ_KIPPEN,
                 name="Kippspannung eines Rechtecks aus Holz")
        rel = gl.lambda_rel_m(self.zahl("f_m_k"), krit.groesse.si / 1e6)
        lam = werte.zahl("lam_rel_m", r"\lambda_{rel,m}", rel, "Relative Schlankheit beim Kippen")
        p.formel(lam, r"\sqrt{\frac{@f}{@s}}", {"f": self.kennwert("f_m_k"), "s": krit},
                 titel="Relative Schlankheit beim Kippen", referenz=gl.REFERENZ_KIPPEN,
                 name="Relative Schlankheit beim Kippen von Holz")
        k_m = werte.zahl("k_m", "k_m", gl.k_m(rel), "Kippbeiwert")
        if rel <= 0.75:
            p.wert(k_m, titel="λ_rel,m nicht über 0.75: der Stab kippt nicht, k_m = 1",
                   referenz=gl.REFERENZ_K_M)
        elif rel <= 1.4:
            p.formel(k_m, r"1.56 - 0.75 \cdot @lam", {"lam": lam},
                     titel="λ_rel,m zwischen 0.75 und 1.4", referenz=gl.REFERENZ_K_M,
                     name="Kippbeiwert des Holzes")
        else:
            p.formel(k_m, r"\frac{1}{@lam^2}", {"lam": lam}, titel="λ_rel,m über 1.4",
                     referenz=gl.REFERENZ_K_M, name="Kippbeiwert des Holzes")
        return k_m.groesse.zahl

    # -- Gleichung und Widerstand --------------------------------------------------------

    def _gleichung(self, a: str, x: gl.Stabachse, sigma_c: float, sigma_m: float,
                   k_c: float, k_m: float) -> None:
        """(37) oder (38) um ``a`` mit Zahlen -- und wie weit die Momente wachsen duerfen."""
        eta = fest(self.eta_zahl, 2)
        glieder: List[str] = []
        if sigma_c:
            glieder.append(rf"\frac{{{fest(sigma_c, 2)}}}{{{fest(k_c, 3)} \cdot {eta} \cdot "
                           rf"{fest(self.zahl('f_c_0_d'), 1)}}}")
        if sigma_m:
            k_h = rf"{fest(self.e.g('k_h').si, 3)} \cdot " if self._mit_k_h(a) else ""
            glieder.append(rf"{'' if x.nur_druck else r'\lambda \cdot '}"
                           rf"\frac{{{fest(sigma_m, 2)}}}{{{fest(k_m, 3)} \cdot {eta} \cdot "
                           rf"{k_h}{fest(self.zahl('f_m_d'), 1)}}}")
        links = " + ".join(glieder)
        referenz = gl.REFERENZEN[x.gleichung]
        if not x.nur_druck:
            self.p.gleichung(rf"{links} = 1 \quad\Rightarrow\quad \lambda = {fest(x.alpha, 3)}",
                             titel=f"{x.gleichung} um {a}: wie weit die Momente wachsen dürfen",
                             referenz=referenz)
            return
        wert = x.druck + x.biegung
        zeichen = r"\le" if wert <= 1.0 else ">"
        titel = (f"{x.gleichung} um {a}: die Druckkraft allein" if x.biegung == 0.0
                 else f"{x.gleichung} um {a}: schon die Druckkraft allein trägt nicht")
        self.p.gleichung(rf"{links} = {fest(wert, 3)} {zeichen} 1", titel=titel,
                         referenz=referenz)

    def knickwiderstand(self, a: str, si: float) -> Wert:
        """
        ``N_K,Rd = -k_c η f_c,0,d A`` um ``a``, mit dem Zeichen der Druckkraft
        -- ``si`` ist dasselbe, aus dem Erfuellungsgrad der Achse.
        """
        R = self.werte.kraft(f"N_K_Rd_{a}", rf"N_{{K,{a},Rd}}", si, "Knickwiderstand")
        self.p.formel(R, r"-@k \cdot @eta \cdot @f_c \cdot @A",
                      {"k": self.k_c[a], "eta": self.eta, "f_c": self.kennwert("f_c_0_d"),
                       "A": self.e["A"]},
                      titel=f"Knickwiderstand um {a}", referenz=gl.REFERENZ_29,
                      name="Knickwiderstand eines Holzstabs")
        return R
