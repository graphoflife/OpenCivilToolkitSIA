"""
opencivil/nachweis/qa_stahl.py -- die Lastfaelle eines Stahlquerschnitts nach SIA 263:2013.

VERANTWORTUNG:
Zwei Nachweise je Lastfall, mit ihrer Herleitung -- gerechnet wird in
:mod:`opencivil.stahlbau.widerstand`:

* **Biegung und Normalkraft** (:class:`StahlBiegungQA`): die Klasse im
  Lastfall, dann plastisch in den Klassen 1 und 2, nach (54) in Klasse 3 und
  am wirksamen Querschnitt nach (60) in Klasse 4 -- mit dem, was eine grosse
  Querkraft den Blechen nimmt.
* **Querkraft** (:class:`StahlQuerkraftQA`): je Richtung ``V_Ed ≤ V_Rd``, in
  einem Querschnitt aus Rundrohren die Resultierende. ``V_Rd`` lesen beide
  aus den Kennzahlen (:mod:`opencivil.nachweis.qa_stahl_kennzahlen`).

Was in der Herleitung steht, ist im plastischen Fall die **Probe**, wie beim
Stahlbeton (:mod:`opencivil.nachweis.schiefe_biegung`): die Nulllinie, die
Kraft jedes Teils mit ihrem Angriffspunkt und die Summen ``N``, ``M_y`` und
``M_z`` -- sie gehen von Hand. In den Klassen 3 und 4 die lineare
Gleichung mit ihren Zahlen.

WAS FEHLT -- GRAU:
* Torsion: SIA 263 regelt in 5.1 bis 5.3 keinen Torsionswiderstand des
  Querschnitts. Ein ``T_Ed`` steht in der Einwirkung, nachgewiesen wird es
  nicht (nach Vorgabe, nicht nachgeschlagen).
* Querkraft ohne Profil: frei gezeichnete Flaechen tragen keine.
* Ein Rundrohr der Klasse 4: SIA 263 nennt dafuer keine mitwirkende Breite.
* Knicken und Kippen gehoeren dem Stab.

VORZEICHEN:
N > 0 Zug; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt der
Analyse.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.einheiten import CM3, MIO_MM4, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.qa_stahl_kennzahlen import KennzahlenStahlQA
from opencivil.nachweis.qa_stahl_werte import (
    ELASTISCH, ROHR_KLASSE_4, WIDERSTANDSMOMENT, Stahlwerte, breiten, klassen, stoffbezuege,
)
from opencivil.querschnitt.analyse import Lastfall, Querschnittsanalyse
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.plastisch import Block, Linie, Zustand
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import schub
from opencivil.stahlbau import widerstand as wd
from opencivil.stahlbau.querschnitt import Stahlquerschnitt

#: Warum es mit diesem N keinen plastischen Zustand gibt.
JENSEITS = ("Die Normalkraft liegt jenseits dessen, was der Querschnitt ganz gezogen oder ganz "
            "gedrückt aufnimmt – es gibt keinen Zustand mit diesem N.")

#: Warum Torsion nicht nachgewiesen wird -- siehe Dateikopf.
OHNE_TORSION = ("Torsion weist das Werkzeug beim Stahlquerschnitt nicht nach: SIA 263 nennt in "
                "5.1 bis 5.3 keinen Torsionswiderstand des Querschnitts (nach Vorgabe, nicht "
                "nachgeschlagen).")

#: Warum ohne Profil keine Querkraft getragen wird.
OHNE_PROFIL = "Querkraft tragen nur Profile – der Querschnitt hat keines."

#: Der Name von (54) und (60) in der Formelsammlung: als Ansatz dieselbe Gleichung.
LINEAR = "Lineares Zusammenwirken im Stahlquerschnitt"


def _bezuege(analyse: Querschnittsanalyse, stahl: Stahlquerschnitt,
             kennzahlen: KennzahlenStahlQA) -> List[Eingabebezug]:
    """Schwerpunkt, Kennwerte der Staehle und die Querkraftwiderstaende der Kennzahlen."""
    return ([Eingabebezug("y_S", analyse.id_von("y_S")), Eingabebezug("z_S", analyse.id_von("z_S"))]
            + stoffbezuege(stahl)
            + [Eingabebezug(f"V_{r}_Rd", kennzahlen.d[f"V_{r}_Rd"].id)
               for r in kennzahlen.richtungen])


def querkraefte(e: Eingaben, stahl: Stahlquerschnitt, kennzahlen: KennzahlenStahlQA,
                analyse: Querschnittsanalyse, fall: Lastfall) -> List[wd.Querkraft]:
    """
    Die Querkraefte des Lastfalls mit ihren Widerstaenden, in N -- wie sie
    zaehlen. ``kennzahlen`` traegt ``V_Rd`` je Richtung -- auch die des
    Verbunds (:mod:`opencivil.nachweis.qa_verbund_kennzahlen`).
    """
    V_Rd = {r: e.g(f"V_{r}_Rd").si for r in kennzahlen.richtungen}
    return wd.querkraefte(stahl, analyse.biegung.querkraft_y(fall.V_y), fall.V_z, V_Rd)


def einwirkung(p: Protokoll, analyse: Querschnittsanalyse, fall: Lastfall, *,
               torsion: str = OHNE_TORSION) -> None:
    """
    Die Einwirkung als Tabelle -- je Groesse, die zaehlt, eine Zeile;
    einachsig ohne M_z und V_y. Mit ``T_Ed`` der Satz ``torsion``, warum es
    nicht nachgewiesen wird.
    """
    biegung = analyse.biegung
    zeilen = [["N_Ed", Mathe(fest(fall.N / 1e3, 1)), "kN"]]
    zeilen += [[f"M_{a},Ed", Mathe(fest(m / 1e3, 1)), "kNm"]
               for a, m in biegung.momente(fall.M_y, fall.M_z)]
    zeilen.append(["V_z,Ed", Mathe(fest(fall.V_z / 1e3, 1)), "kN"])
    if not biegung.einachsig:
        zeilen.append(["V_y,Ed", Mathe(fest(fall.V_y / 1e3, 1)), "kN"])
    if fall.T:
        zeilen.append(["T_Ed", Mathe(fest(fall.T / 1e3, 1)), "kNm"])
    p.tabelle(kopf=["Einwirkung", "Wert", ""], zeilen=zeilen, titel="Einwirkung",
              ausrichtung="lrl")
    if fall.T:
        p.hinweis(torsion)


class StahlBiegungQA(Nachweis):
    """Biegung und Normalkraft eines Stahlquerschnitts, je Lastfall -- siehe Dateikopf."""

    THEMA = "Stahlquerschnitt"
    LANGNAME = "Biegung und Normalkraft"
    ART = "M-N"

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 kennzahlen: KennzahlenStahlQA) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.kennzahlen = kennzahlen
        self.stahl = kennzahlen.stahl
        basis = f"{analyse.id}.nachweis.stahl"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Biegung und Normalkraft – {f.name}",
                             wd.REFERENZ_PLASTISCH)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=_bezuege(analyse, self.stahl, kennzahlen),
                         titel=f"Biegung und Normalkraft – {analyse.name}",
                         referenz="SIA 263:2013, 5.1–5.3", abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        sw = Stahlwerte(self.stahl, e, self.analyse.wahl)
        bezug = (e.g("y_S").si * 1e3, e.g("z_S").si * 1e3)
        faelle = [(fall, self._rechnen(e, sw, bezug, fall)) for fall in self.lastfaelle]
        self._ansatz(p, {x.klasse for _, x in faelle if x is not None and not x.ohne_moment
                         and not x.rohr_klasse_4})
        urteile = [self._ein_fall(p, sw, bezug, fall, x) for fall, x in faelle]
        return Ausfuehrung({}, urteile)

    def _rechnen(self, e: Eingaben, sw: Stahlwerte, bezug: Tuple[float, float],
                 fall: Lastfall) -> Optional[wd.Fall]:
        """Der Lastfall am Querschnitt -- ``None`` ohne Normalkraft und Moment."""
        M_y, M_z = self.analyse.biegung.wirkt(fall.M_y, fall.M_z)
        if fall.N == 0.0 and self.analyse.biegung.betrag(M_y, M_z) * 1e3 <= wd.KEIN_MOMENT:
            return None
        kraefte = querkraefte(e, self.stahl, self.kennzahlen, self.analyse, fall)
        return wd.rechnen(self.stahl, sw.f, sw.eps, fall.N, M_y * 1e3, M_z * 1e3, kraefte,
                          bezug, self.analyse.biegung)

    def _ansatz(self, p: Protokoll, klassen_: set) -> None:
        p.erklaerung(
            "Je Lastfall zuerst die Klasse: jedes Blech jedes Profils, plastisch an der "
            "Nulllinie, an der der Querschnitt bei N_Ed versagt, elastisch an den Spannungen, "
            "bei denen (54) gerade aufgeht. Dann der Widerstand nach der Klasse – plastisch, "
            "elastisch nach (54) oder am wirksamen Querschnitt nach (60). Die Normalkraft "
            "bleibt, das Moment wächst in seiner Richtung, bis der Widerstand erreicht ist.")
        p.annahme("Die Klasse je Lastfall aus diesen beiden Zuständen – nach Vorgabe, nicht "
                  "nachgeschlagen: die Norm sagt nicht, bei welcher Laststufe α und ψ gelten.")
        p.ansatz(r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}",
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")
        linear = (r"\frac{|N_{Ed}|}{N_{Rd}} + \frac{|\lambda M_{y,Ed} + e_z N_{Ed}|}{M_{y,Rd}} + "
                  r"\frac{|\lambda M_{z,Ed} + e_y N_{Ed}|}{M_{z,Rd}} \le 1")
        if 3 in klassen_:
            p.ansatz(linear, titel="Klasse 3, (54): elastisch, bis die erste Faser fliesst – mit "
                                   "e, wo der Schwerpunkt neben dem Bezugspunkt liegt",
                     referenz=wd.REFERENZ_54, name=LINEAR)
        if 4 in klassen_:
            p.ansatz(linear, titel="Klasse 4, (60) als Widerstände: am wirksamen Querschnitt, "
                                   "e vom Schwerpunkt seiner Fläche bei Druck",
                     referenz=wd.REFERENZ_60, name=LINEAR)

    def _ein_fall(self, p: Protokoll, sw: Stahlwerte, bezug: Tuple[float, float],
                  fall: Lastfall, x: Optional[wd.Fall]) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        einwirkung(p, self.analyse, fall)
        if x is None:
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        minderung(p, werte, x.querkraefte, x.abgemindert, self.stahl,
                  referenz=wd.REFERENZ_QUERKRAFT)
        _, wer = klassen(p, x.zustaende, x.freie, "Bleche im Lastfall")
        p.wert(werte.zahl("klasse", r"\mathrm{QK}", float(x.klasse), stellen=0),
               titel=f"Querschnittsklasse – massgebend {wer}" if wer else "Querschnittsklasse",
               referenz="SIA 263:2013, 4.3.1.3; Tabellen 5a und 5b")
        N_Ed = werte.kraft("N_Ed", "N_{Ed}", fall.N)

        if x.rohr_klasse_4:
            p.hinweis(ROHR_KLASSE_4)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, ROHR_KLASSE_4)
        if x.ohne_moment:
            return self._normalkraft(p, werte, sw, x, N_Ed, d_grad, fall)
        M_Ed = werte.moment("M_Ed", "M_{Ed}", x.moment / 1e3)
        if x.klasse <= 2:
            return self._plastisch(p, werte, sw, x, bezug, N_Ed, M_Ed, d_grad, fall)
        if x.klasse == 4:
            self._wirksam(p, werte, sw, x, bezug)
        return self._linear(p, werte, x, N_Ed, M_Ed, d_grad, fall)

    # -- Reine Normalkraft ---------------------------------------------------------------

    def _normalkraft(self, p: Protokoll, werte: Zwischenwerte, sw: Stahlwerte, x: wd.Fall,
                     N_Ed: Wert, d_grad: WertDef, fall: Lastfall) -> NachweisUrteil:
        zug = x.N > 0.0
        if x.klasse == 4:
            breiten(p, x.wirksam.druck, "Mitwirkende Breiten bei Druck")
            N_Rd = werte.kraft("N_Rd", "N_{Rd}^{-}", -x.wirksam.widerstaende.N_druck)
            p.wert(N_Rd, titel="Druckwiderstand am wirksamen Querschnitt",
                   referenz=wd.REFERENZ_55)
        else:
            w = x.elastisch
            N_Rd = werte.kraft("N_Rd", "N_{Rd}^{+}" if zug else "N_{Rd}^{-}",
                               w.N_zug if zug else -w.N_druck)
            p.wert(N_Rd, titel=f"{'Zug' if zug else 'Druck'}widerstand, {self._wie(sw)}",
                   referenz="SIA 263:2013, 5.1.2.1, (38)")
        v = Vergleich(N_Ed, N_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, "Reine Normalkraft.")

    @staticmethod
    def _wie(sw: Stahlwerte) -> str:
        return "Σ f_y A/γ_M1" if sw.mit_gamma else "Σ f_y A"

    # -- Plastisch -------------------------------------------------------------------------

    def _plastisch(self, p: Protokoll, werte: Zwischenwerte, sw: Stahlwerte, x: wd.Fall,
                   bezug: Tuple[float, float], N_Ed: Wert, M_Ed: Wert, d_grad: WertDef,
                   fall: Lastfall) -> NachweisUrteil:
        pl = x.plastisch
        if pl is None:
            p.text(JENSEITS)
            zug = x.N > 0.0
            N_Rd = werte.kraft("N_Rd", "N_{Rd}^{+}" if zug else "N_{Rd}^{-}",
                               x.elastisch.N_zug if zug else -x.elastisch.N_druck)
            v = Vergleich(N_Ed, N_Rd)
            v.zeile(p, d_grad)
            return self.urteil(d_grad, fall.name, v, "N_Ed jenseits der reinen Normalkraft.")
        p.erklaerung(
            "Plastisch, Klasse 1 oder 2: jeder Teil ganz gezogen oder ganz gedrückt, getrennt an "
            "einer geraden Nulllinie – ein Spannungszustand im Gleichgewicht, der nirgends f_y "
            "überschreitet. Gesucht ist die Nulllinie mit N = N_Ed, deren Moment in die Richtung "
            "der Einwirkung zeigt; nachgewiesen wird ihre Probe.")
        M_Rd = probe(p, werte, x.abgemindert.stahl.starr(sw.f).bloecke(pl.linie),
                     [t.name for t in self.stahl.teile], bezug, self.analyse.biegung, pl,
                     titel="Kräfte im plastischen Zustand – je Teil und Zone, mit f_y je "
                           "Baustahl", referenz=wd.REFERENZ_PLASTISCH)
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v,
                           f"Plastisch, Klasse {x.klasse}, bei N_Ed = {x.N / 1e3:.1f} kN.")

    # -- (54) und (60) -----------------------------------------------------------------------

    def _wirksam(self, p: Protokoll, werte: Zwischenwerte, sw: Stahlwerte, x: wd.Fall,
                 bezug: Tuple[float, float]) -> None:
        """Der wirksame Querschnitt der Klasse 4: bei Druck und zu jeder Seite, die zaehlt."""
        w = x.wirksam
        p.erklaerung(
            "Klasse 4: (60) am wirksamen Querschnitt – A_eff und die Verschiebung e_N seines "
            "Schwerpunkts bei reinem Druck, W_eff bei reiner Biegung zur Seite, die das Moment "
            "zieht. Bei Zug zählt der ganze Querschnitt.")
        if x.N < 0.0:
            if w.druck:
                breiten(p, w.druck, "Mitwirkende Breiten bei Druck")
            p.wert(werte.flaeche("A_eff", "A_{eff}", w.A_eff * 1e-6, "Wirksame Fläche"),
                   titel="Wirksame Fläche bei Druck", referenz=wd.REFERENZ_55)
            mitte = w.widerstaende.druck
            for achse, i in (("y", 0), ("z", 1)):
                e_N = mitte[i] - bezug[i]
                if abs(e_N) > 1e-6:
                    p.wert(werte.laenge(f"e_N{achse}", f"e_{{N,{achse}}}", e_N * 1e-3),
                           titel=f"Verschiebung des Schwerpunkts in {achse}")
        for seite in self._seiten(x):
            g = w.biegung[seite]
            if g.breiten:
                breiten(p, g.breiten, f"Mitwirkende Breiten bei Biegung, {seite.beschriftung}")
            kurz = seite.value
            I = werte.wert(f"I_eff_{kurz}", r"I_{eff}", Groesse.aus_si(g.I * 1e-12, MIO_MM4),
                           beschreibung="Wirksames Trägheitsmoment")
            z = werte.laenge(f"z_{kurz}", "z", g.abstand * 1e-3, "Weiteste Faser")
            W = werte.wert(f"W_eff_{kurz}", r"W_{eff}", Groesse.aus_si(g.I / g.abstand * 1e-9, CM3),
                           beschreibung="Wirksames Widerstandsmoment")
            p.formel(W, r"\frac{@I}{@z}", {"I": I, "z": z},
                     titel=f"Wirksames Widerstandsmoment, {seite.beschriftung}",
                     name=WIDERSTANDSMOMENT)
            vorlage, eingaben = sw.formel(g.gruppe, "@W")
            p.formel(werte.moment(f"M_eff_{kurz}", rf"M_{{{_achse(seite)},Rd}}^{{{seite.zeichen}}}",
                                  w.widerstaende.M[seite] / 1e3),
                     vorlage, {**eingaben, "W": W}, titel=f"Widerstand, {seite.beschriftung}",
                     referenz=wd.REFERENZ_60, name=ELASTISCH)

    def _seiten(self, x: wd.Fall) -> List[Zugseite]:
        """Die Seiten, die die Momente bei ``λ`` ziehen -- ihr ``W_eff`` zaehlt in (60)."""
        faktor = x.alpha if x.alpha is not None else 0.0
        seiten = []
        for g in x.glieder:
            if faktor * g.a + g.b == 0.0:
                continue
            plus = faktor * g.a + g.b > 0.0
            seiten.append({("y", True): Zugseite.UNTEN, ("y", False): Zugseite.OBEN,
                           ("z", True): Zugseite.LINKS, ("z", False): Zugseite.RECHTS}
                          [(g.achse, plus)])
        return seiten

    def _linear(self, p: Protokoll, werte: Zwischenwerte, x: wd.Fall, N_Ed: Wert, M_Ed: Wert,
                d_grad: WertDef, fall: Lastfall) -> NachweisUrteil:
        """(54) in Klasse 3, (60) in Klasse 4 -- als Widerstaende geschrieben, mit ``λ``."""
        vier = x.klasse == 4
        w = x.wirksam.widerstaende if vier else x.elastisch
        referenz = wd.REFERENZ_60 if vier else wd.REFERENZ_54
        N_Rd = w.N_zug if x.N >= 0.0 else w.N_druck
        faktor = x.alpha if x.alpha is not None else 0.0
        teile = [rf"\frac{{{fest(abs(x.N) / 1e3, 1)}}}{{{fest(N_Rd / 1e3, 1)}}}"] if x.N else []
        teile += [t for t in (glied_text(g, faktor, x.alpha is not None) for g in x.glieder) if t]
        links = " + ".join(teile)
        if x.alpha is None:
            p.gleichung(rf"\lambda = 0: \quad {links} = {fest(1.0 / x.alpha_N, 3)} > 1",
                        titel="Schon die Normalkraft allein trägt nicht", referenz=referenz)
            R = werte.kraft("N_Rd_lin", r"N_{Ed}/(\ldots)", x.N * x.alpha_N)
            v = Vergleich(N_Ed, R)
            v.zeile(p, d_grad)
            return self.urteil(d_grad, fall.name, v,
                               f"Klasse {x.klasse}: schon N_Ed allein überschreitet "
                               f"{'(60)' if vier else '(54)'}.")
        p.gleichung(rf"{links} = 1 \quad\Rightarrow\quad \lambda = {fest(faktor, 3)}",
                    titel="Wie weit das Moment wachsen darf", referenz=referenz)
        M_Rd = werte.moment("M_Rd", "M_{Rd}", faktor * x.moment / 1e3)
        p.formel(M_Rd, r"@lam \cdot @M", {"lam": werte.zahl("lambda", r"\lambda", faktor),
                                          "M": M_Ed},
                 titel="Widerstand in der Richtung der Einwirkung")
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v,
                           f"Klasse {x.klasse}, {'(60)' if vier else '(54)'}, "
                           f"bei N_Ed = {x.N / 1e3:.1f} kN.")


def minderung(p: Protokoll, werte: Zwischenwerte, kraefte: Sequence[wd.Querkraft],
              abgemindert: wd.Abgemindert, stahl: Stahlquerschnitt, *, referenz: str) -> None:
    """Was grosse Querkraft den Blechen nimmt, in denen sie steht -- im Stahl wie im Verbund."""
    for q in kraefte:
        if q.V_Ed == 0.0:
            continue
        kurz = "V" if q.resultierend else f"V_{q.richtung}"
        V_Ed = werte.kraft(f"{kurz}_Ed", q.symbol("Ed"), abs(q.V_Ed), "Querkraft, Betrag")
        V_Rd = werte.kraft(f"{kurz}_Rd", q.symbol("Rd"), q.V_Rd, "Querkraftwiderstand")
        if q.gewicht == 0.0:
            p.text(f"{q.name.capitalize()}: {V_Ed.formatiert()} kN ≤ 0.5 · "
                   f"{V_Rd.formatiert()} kN – sie mindert nichts.")
            continue
        p.formel(werte.zahl(f"rho_{kurz}", rf"\rho_{{{q.richtung}}}" if not q.resultierend
                            else r"\rho", q.gewicht),
                 r"\left(\frac{@V}{@R}\right)^2", {"V": V_Ed, "R": V_Rd},
                 titel=f"{q.name.capitalize()} über der Hälfte von V_Rd: was die Bleche, in "
                       f"denen sie steht, für Normalkraft und Biegung verlieren",
                 referenz=referenz, name="Minderung durch grosse Querkraft")
    if abgemindert.weg:
        namen = sorted({f"{stahl.teile[i].flaeche.name}: {blech}" for i, blech in abgemindert.weg})
        p.text("Gemindert: " + ", ".join(namen) + ". Ein Teil eines Blechs zählt mit "
               "1 − ρ; in den Tabellen steht, was die Querkraft nimmt, mit negativer Kraft.")
        p.annahme("Dieselbe Minderung für jedes Profil und jede Richtung, auch für die "
                  "Normalkraft, und in den Klassen 3 und 4 statt der Vergleichsspannung – "
                  "nach Vorgabe, nicht nachgeschlagen.")


def krafttabelle(p: Protokoll, werte: Zwischenwerte, bloecke: Sequence[Block],
                 namen: Sequence[str], linie: Linie, *, titel: str) -> None:
    """
    Die Nulllinie und je Teil und Zone die Kraft mit Angriffspunkt, dazu
    ihre Summe ``N`` -- der Anfang der Probe eines plastischen Zustands, im
    Stahl wie im Verbund. ``namen`` je Teil, auf den ein Block zeigt.
    """
    n, v_l = linie.n, linie.v
    p.text(f"Nulllinie: Zugrichtung n = ({n[0]:.3f}; {n[1]:.3f}), "
           f"{math.degrees(math.atan2(n[1], n[0])):.1f}° gegen die y-Achse; gezogen ist, wo "
           f"n_y y + n_z z > {v_l:.1f} mm.")
    p.tabelle(
        kopf=["Teil", "Zone", Mathe(r"F\ [\mathrm{kN}]"), Mathe(r"y\ [\mathrm{mm}]"),
              Mathe(r"z\ [\mathrm{mm}]")],
        zeilen=[[f"{namen[b.teil]}{', ' + b.was if b.was else ''}", b.zone,
                 Mathe(fest(b.F / 1e3, 1)), Mathe(fest(b.punkt[0], 1)),
                 Mathe(fest(b.punkt[1], 1))] for b in bloecke],
        titel=titel, ausrichtung="llrrr")
    p.formel(werte.kraft("N_int", "N_{Rd}", sum(b.F for b in bloecke)), r"\sum F_i", {},
             titel="Probe: Normalkraft")


def momentsummen(bloecke: Sequence[Block], bezug: Tuple[float, float]) -> Dict[str, float]:
    """Je Achse das Moment der Bloecke um ``bezug``, in Nm: ``M_y = -Σ F (z - z_S)``."""
    y_S, z_S = bezug
    return {"y": -sum(b.F * (b.punkt[1] - z_S) for b in bloecke) / 1e3,
            "z": -sum(b.F * (b.punkt[0] - y_S) for b in bloecke) / 1e3}


#: Wie die Probe das Moment um eine Achse schreibt.
MOMENT_UM = {"y": r"-\sum F_i \cdot (z_i - z_S)", "z": r"-\sum F_i \cdot (y_i - y_S)"}


def probe(p: Protokoll, werte: Zwischenwerte, bloecke: Sequence[Block], namen: Sequence[str],
          bezug: Tuple[float, float], biegung: Biegung, pl: Zustand, *, titel: str,
          referenz: str, symbol: str = "M_{Rd}") -> Wert:
    """
    Die Probe eines plastischen Zustands -- im Stahl wie im Verbund: die
    Nulllinie, je Teil und Zone die Kraft mit Angriffspunkt, die Summen
    ``N``, ``M_y`` und ``M_z``. Zurueck kommt der Widerstand ``symbol`` in
    der Richtung der Einwirkung, einachsig ``M_y``.
    """
    krafttabelle(p, werte, bloecke, namen, pl.linie, titel=titel)
    summen = momentsummen(bloecke, bezug)
    momente = {}
    for achse, M in biegung.momente(summen["y"], summen["z"]):
        momente[achse] = werte.moment(f"M_{achse}_int", f"M_{{{achse},Rd}}", M)
        p.formel(momente[achse], MOMENT_UM[achse], {}, titel=f"Probe: Moment um {achse}")
    M_Rd = werte.moment("M_Rd", symbol, biegung.betrag(pl.M_y, pl.M_z) / 1e3)
    if biegung.einachsig:
        if abs(pl.M_z) > 1e-3 * max(abs(pl.M_y), 1.0):
            p.text(f"Einachsig: nachgewiesen wird M_y. Das M_z = {pl.M_z / 1e6:.1f} kNm, das "
                   f"der unsymmetrische Querschnitt dabei weckt, wird übergangen.")
    else:
        p.formel(M_Rd, r"\sqrt{@My^{2} + @Mz^{2}}", {"My": momente["y"], "Mz": momente["z"]},
                 titel="Widerstand in der Richtung der Einwirkung", referenz=referenz)
    return M_Rd


def glied_text(g: wd.Glied, faktor: float, mit_lambda: bool) -> str:
    """
    Ein Glied von (54) oder (60) -- und von (62) und (63) im Stab
    (:mod:`opencivil.nachweis.qa_stahl_stabilitaet`) -- als Bruch mit Zahlen:
    ohne den Anteil mit ``λ``, wo ``mit_lambda`` falsch ist; leer, wo nichts
    bleibt.
    """
    innen = rf"\lambda \cdot {fest(g.a / 1e6, 1)}" if mit_lambda and g.a != 0.0 else ""
    if abs(g.b) > 1e-6 * max(abs(g.a), 1.0):
        innen = (rf"{innen} {'+' if g.b >= 0.0 else '-'} {fest(abs(g.b) / 1e6, 1)}" if innen
                 else fest(g.b / 1e6, 1))
    return rf"\frac{{|{innen}|}}{{{fest(g.widerstand(faktor) / 1e6, 1)}}}" if innen else ""


def _achse(seite: Zugseite) -> str:
    return "y" if seite.um_y else "z"


class StahlQuerkraftQA(Nachweis):
    """Die Querkraft eines Stahlquerschnitts, je Lastfall -- siehe Dateikopf."""

    THEMA = "Stahlquerschnitt"
    LANGNAME = "Querkraft"
    ART = "V"
    REFERENZ = schub.REFERENZ_SCHUB

    def __init__(self, analyse: Querschnittsanalyse, lastfaelle: Sequence[Lastfall],
                 kennzahlen: KennzahlenStahlQA) -> None:
        self.analyse = analyse
        self.lastfaelle = list(lastfaelle)
        self.kennzahlen = kennzahlen
        self.stahl = kennzahlen.stahl
        basis = f"{analyse.id}.nachweis.stahl_v"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{V,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Querkraft – {f.name}", self.REFERENZ)
            for f in self.lastfaelle}
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=_bezuege(analyse, self.stahl, kennzahlen),
                         titel=f"Querkraft – {analyse.name}", referenz=self.REFERENZ,
                         abschnitt=analyse.abschnitt)

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel(self.LANGNAME)
        p.erklaerung(
            "Je Richtung die Querkraft gegen den Widerstand der Profile aus den Kennzahlen. "
            "In einem Querschnitt aus Rundrohren zählt die Resultierende: ein Rundrohr trägt "
            "in jeder Richtung gleich.")
        urteile = [self._ein_fall(p, e, fall) for fall in self.lastfaelle]
        return Ausfuehrung({}, urteile)

    def _ein_fall(self, p: Protokoll, e: Eingaben, fall: Lastfall) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        V_y = self.analyse.biegung.querkraft_y(fall.V_y)
        if V_y == 0.0 and fall.V_z == 0.0:
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        kraefte = querkraefte(e, self.stahl, self.kennzahlen, self.analyse, fall)
        if not kraefte:
            p.hinweis(OHNE_PROFIL)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, OHNE_PROFIL)
        if kraefte[0].resultierend:
            p.formel(werte.kraft("V_Ed", "V_{Ed}", kraefte[0].V_Ed),
                     r"\sqrt{@Vy^{2} + @Vz^{2}}",
                     {"Vy": werte.kraft("V_y_Ed", "V_{y,Ed}", V_y),
                      "Vz": werte.kraft("V_z_Ed", "V_{z,Ed}", fall.V_z)},
                     titel="Resultierende Querkraft im Rundrohr")
        massgebend: Optional[Vergleich] = None
        for q in (q for q in kraefte if q.V_Ed != 0.0):
            kurz = "V" if q.resultierend else f"V_{q.richtung}"
            v = Vergleich(werte.kraft(f"{kurz}_Ed_betrag", q.symbol("Ed"), abs(q.V_Ed)),
                          werte.kraft(f"{kurz}_Rd", q.symbol("Rd"), q.V_Rd))
            v.bedingung(p, titel=q.name.capitalize())
            if massgebend is None or v.grad < massgebend.grad:
                massgebend = v
        massgebend.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, massgebend, "Je Richtung gegen V_Rd der Profile.")
