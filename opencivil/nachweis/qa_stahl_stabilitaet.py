"""
opencivil/nachweis/qa_stahl_stabilitaet.py -- Knicken und Kippen eines Stahlstabs nach SIA 263:2013.

VERANTWORTUNG:
Je Stabilitaetsfall der Querschnittsanalyse ein Nachweis mit seiner
Herleitung; gerechnet wird in :mod:`opencivil.stahlbau.stabilitaet`. Der
Reihe nach: die Klasse im Fall, die Widerstaende nach ihr, das Knicken je
Achse, das Kippen um die starke Achse, dann das Zusammenwirken -- (50) und
(51) in den Klassen 1 bis 3, (62) und (63) in Klasse 4 -- und der
Erfuellungsgrad wie in der Tragsicherheit: die Normalkraft bleibt, die
Momente wachsen. Ohne Moment steht die Normalkraft gegen den kleineren
Knickwiderstand.

WAS FEHLT -- GRAU:
Was :attr:`~opencivil.stahlbau.stabilitaet.Ergebnis.fehlt` nennt: eine
Knickspannungskurve, wo der Querschnitt nicht aus einem einzigen Profil
besteht und keine gewaehlt ist; das Kippen eines Querschnitts, den Anhang B
nicht kennt; ein Rundrohr der Klasse 4.

VORZEICHEN:
N < 0 Druck; M_y > 0 zieht unten, M_z > 0 links -- um den Schwerpunkt.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from opencivil.core.berechnung import Ausfuehrung, Eingabebezug, Eingaben
from opencivil.core.einheiten import CM3, MIO_MM4, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.nachweis.qa_stahl import glied_text
from opencivil.nachweis.qa_stahl_kennzahlen import REFERENZ_38, REFERENZ_40, REFERENZ_55
from opencivil.nachweis.qa_stahl_werte import (
    ELASTISCH, NORMALKRAFT, PLASTISCH, WIDERSTANDSMOMENT, Stahlwerte, breiten, klassen,
    stoffbezuege,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.zugseite import Zugseite
from opencivil.stahlbau import stabilitaet as st
from opencivil.stahlbau import widerstand as wd
from opencivil.stahlbau.querschnitt import Stahlquerschnitt, normale
from opencivil.stahlprofile.formen import I_PROFIL, RUNDROHR

#: Der Name der Formel, die Knicken und Kippen beide schreiben.
ABMINDERUNG = "Abminderungsfaktor beim Knicken und Kippen"

#: Wie die Klassen rechnen.
_WIE = {1: "plastisch", 2: "plastisch", 3: "elastisch (5.2.9)", 4: "am wirksamen Querschnitt"}


def _seite_der(g: wd.Glied, faktor: float) -> Zugseite:
    """Die Seite, die ein Glied bei ``λ`` zieht."""
    return st.seite_von(g.achse, faktor * g.a + g.b)


class StahlStabilitaetQA(Nachweis):
    """Knicken und Kippen eines Stahlstabs, je Fall -- siehe Dateikopf."""

    THEMA = "Knicken und Kippen"
    ART = "Stab"

    def __init__(self, analyse: Querschnittsanalyse, faelle: Sequence[st.Stabfall],
                 kurven: Dict[str, st.Knickkurve]) -> None:
        self.analyse = analyse
        self.faelle = list(faelle)
        self.kurven = dict(kurven)
        self.stahl = Stahlquerschnitt(analyse.flaechen, analyse.eltern)
        self.profil = st.einzelprofil((f.kennung, f.profil) for f in analyse.flaechen)
        basis = f"{analyse.id}.nachweis.stabilitaet"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Knicken und Kippen – {f.name}", st.REFERENZ_50)
            for f in self.faelle}
        stoffe = {g.stoff.id: g.stoff for g in self.stahl.gruppen}.values()
        bezuege = ([Eingabebezug(k, analyse.id_von(k)) for k in ("y_S", "z_S", "A", "I_y", "I_z")]
                   + [Eingabebezug("I_T", analyse.d_torsion.id)]
                   + stoffbezuege(self.stahl) + [s.bezug("G_a") for s in stoffe])
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()), bezuege=bezuege,
                         titel=f"Knicken und Kippen – {analyse.name}",
                         referenz="SIA 263:2013, 4.5; 5.1.9; 5.1.10; 5.3.9",
                         abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel("Knicken und Kippen")
        sw = Stahlwerte(self.stahl, e, self.analyse.wahl)
        gruppen = range(len(self.stahl.gruppen))
        stab = st.Stab(
            self.stahl, sw.f, [sw.zahl(g, "f_y") for g in gruppen], sw.eps,
            E=sw.zahl(0, "E_a"), G=sw.zahl(0, "G_a"),
            I={"y": e.g("I_y").si * 1e12, "z": e.g("I_z").si * 1e12},
            I_T=e.g("I_T").si * 1e12, bezug=(e.g("y_S").si * 1e3, e.g("z_S").si * 1e3),
            biegung=self.analyse.biegung, kurven=self.kurven, profil=self.profil)
        p.erklaerung(
            "Der Stab hat den gezeichneten Querschnitt. Je Fall zuerst die Klasse bei N_Ed und den "
            "Momenten 1. Ordnung, dann die Widerstände nach ihr: plastisch in den Klassen 1 und "
            "2, elastisch in Klasse 3, am wirksamen Querschnitt in Klasse 4. Je Achse das Knicken "
            "nach der Knickspannungskurve, um die starke Achse das Kippen, dann das "
            "Zusammenwirken. Die Normalkraft bleibt, die Momente wachsen, bis die Gleichung "
            "aufgeht.")
        p.ansatz(r"\alpha_{eff} = \frac{M_{Rd}}{M_{Ed}} \qquad M = \sqrt{M_y^2 + M_z^2}",
                 titel="Erfüllungsgrad bei fester Normalkraft und fester Richtung")
        if stab.profil is not None:
            p.text(f"Der Querschnitt ist ein {stab.profil.name}: daraus kommen die "
                   f"Knickspannungskurven, die nicht gewählt sind, und der Druckgurt.")
        urteile = [self._ein_fall(p, e, sw, stab, fall) for fall in self.faelle]
        return Ausfuehrung({}, urteile)

    # -- Ein Fall ---------------------------------------------------------------

    def _ein_fall(self, p: Protokoll, e: Eingaben, sw: Stahlwerte, stab: st.Stab,
                  fall: st.Stabfall) -> NachweisUrteil:
        werte = Zwischenwerte(f"{self.id}.{fall.kennung}")
        d_grad = self.d_ausnutzung[fall.name]
        biegung = self.analyse.biegung
        p.titel(fall.name, ebene=3)
        _einwirkung(p, biegung, fall)
        if fall.N == 0.0 and not any(biegung.wirkt(fall.M_y, fall.M_z)):
            p.text(OHNE_EINWIRKUNG)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, OHNE_EINWIRKUNG)
        x = st.rechnen(stab, fall)
        if x.fehlt:
            p.hinweis(x.fehlt)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, x.fehlt)
        _, wer = klassen(p, x.x.zustaende, x.x.freie, "Bleche im Fall")
        p.wert(werte.zahl("klasse", r"\mathrm{QK}", float(x.klasse), "Querschnittsklasse",
                          stellen=0),
               titel=f"Querschnittsklasse – massgebend {wer}" if wer else "Querschnittsklasse",
               referenz="SIA 263:2013, 4.3.1.3; Tabellen 5a und 5b")
        r = _Herleitung(p, e, werte, sw, stab, x)
        r.widerstaende()
        for achse in ("y", "z"):
            r.knicken(achse)
        if x.kippen is not None:
            r.kippen()
        if x.g62:
            r.gleichungen_62()
        elif x.mit_moment:
            r.gleichung_50()
            if x.g51 is not None:
                r.gleichung_51()
        if x.alpha_9 is not None:
            r.kippen_allein()
        return self._urteil(p, werte, r, d_grad, fall)

    def _urteil(self, p: Protokoll, werte: Zwischenwerte, r: "_Herleitung", d_grad: WertDef,
                fall: st.Stabfall) -> NachweisUrteil:
        """Der Vergleich: die Momente gegen ihren Widerstand -- ohne Moment die Normalkraft."""
        x = r.x
        N_Ed = werte.kraft("N_Ed", "N_{Ed}", x.N)
        if x.alpha_N is not None:
            p.text("Schon die Normalkraft allein trägt nicht: so weit müsste sie kleiner sein.")
            v = Vergleich(N_Ed, werte.kraft("N_Rd_stab", r"N_{Rd}", x.N * x.alpha_N))
            v.zeile(p, d_grad)
            return self.urteil(
                d_grad, fall.name, v,
                f"Klasse {x.klasse}: schon N_Ed allein überschreitet den Widerstand.")
        if not x.mit_moment:
            if x.g62:
                R = werte.kraft("N_Rd_stab", r"N_{Rd}", x.N * x.alpha)
                text = "Klasse 4, ohne Moment, mit dem Versatz des wirksamen Schwerpunkts."
            else:
                R = werte.kraft("N_K_Rd", r"N_{K,Rd}", -x.N_K_Rd)
                p.wert(R, titel="Der kleinere Knickwiderstand", referenz=st.REFERENZ_KNICKEN)
                text = f"Klasse {x.klasse}, ohne Moment."
            v = Vergleich(N_Ed, R)
            v.zeile(p, d_grad)
            return self.urteil(d_grad, fall.name, v, text)
        M = self.analyse.biegung.betrag(x.M["y"], x.M["z"])
        M_Ed = werte.moment("M_Ed", "M_{Ed}", M / 1e3)
        M_Rd = werte.moment("M_Rd", "M_{Rd}", x.alpha * M / 1e3)
        p.formel(M_Rd, r"@lam \cdot @M", {"lam": werte.zahl("lambda", r"\lambda", x.alpha),
                                          "M": M_Ed},
                 titel="Widerstand in der Richtung der Einwirkung")
        v = Vergleich(M_Ed, M_Rd)
        v.zeile(p, d_grad)
        massgebend = ("(62) und (63)" if x.g62 else
                      "(51)" if x.g51 is not None and x.alpha == x.g51.alpha else "(50)")
        if x.alpha_9 is not None and x.alpha == x.alpha_9:
            massgebend = "Kippen nach (9)"
        bei = f", bei N_Ed = {x.N / 1e3:.1f} kN" if x.N else ""
        return self.urteil(d_grad, fall.name, v,
                           f"Klasse {x.klasse}, massgebend {massgebend}{bei}.")


def _einwirkung(p: Protokoll, biegung: Biegung, fall: st.Stabfall) -> None:
    """Die Einwirkung und der Stab als Tabelle -- einachsig ohne M_z."""
    zeilen = [["N_Ed", Mathe(fest(fall.N / 1e3, 1)), "kN"]]
    for achse, M in biegung.momente(fall.M_y, fall.M_z):
        zeilen.append([f"M_{achse},Ed", Mathe(fest(M / 1e3, 1)), "kNm"])
        if M:
            zeilen.append([f"ψ_{achse}", Mathe(fest(fall.psi(achse), 2)), ""])
    zeilen += [["L_K,y", Mathe(fest(fall.L_K_y, 2)), "m"],
               ["L_K,z", Mathe(fest(fall.L_K_z, 2)), "m"],
               ["L_D", Mathe(fest(fall.L_D, 2)), "m"]]
    p.tabelle(kopf=["Einwirkung und Stab", "Wert", ""], zeilen=zeilen,
              titel="Einwirkung 1. Ordnung, ohne Imperfektionen; eine Länge null heisst gehalten",
              ausrichtung="lrl")


class _Herleitung:
    """Die Herleitung eines Falls -- Schritt fuer Schritt, mit den Werten, die sie teilen."""

    def __init__(self, p: Protokoll, e: Eingaben, werte: Zwischenwerte, sw: Stahlwerte,
                 stab: st.Stab, x: st.Ergebnis) -> None:
        self.p, self.e, self.werte, self.sw, self.stab, self.x = p, e, werte, sw, stab, x
        self.eine = len(stab.stahl.gruppen) == 1
        self.N = werte.kraft("N_betrag", r"|N_{Ed}|", abs(x.N), "Druckkraft")
        self.A: Wert = e["A"]
        self.N_Rd: Optional[Wert] = None
        self.M_Rd: Dict[Zugseite, Wert] = {}
        self.W: Dict[Zugseite, Wert] = {}
        self.N_cr: Dict[str, Wert] = {}
        self.L_K: Dict[str, Wert] = {}
        self.omega: Dict[str, Wert] = {}
        self.M_D: Optional[Wert] = None
        self.M_D_min: Optional[Wert] = None

    # -- Widerstaende -------------------------------------------------------------

    def seiten(self) -> List[Zugseite]:
        """Die Seiten, deren Biegewiderstand eine Gleichung braucht."""
        x = self.x
        achsen = ["y", "z"] if x.g51 is not None else [a for a in ("y", "z") if x.M[a]]
        seiten = [st.seite_von(a, x.M[a]) for a in achsen]
        for g in x.g62:
            faktor = g.alpha if g.alpha is not None and x.mit_moment else 0.0
            seiten += [_seite_der(gl, faktor) for gl in g.glieder]
        return list(dict.fromkeys(seiten))

    def widerstaende(self) -> None:
        p, x, werte, sw = self.p, self.x, self.werte, self.sw
        p.text(f"Widerstände in Klasse {x.klasse}: {_WIE[x.klasse]}.")
        if x.klasse == 4:
            if x.wirksam.druck:
                breiten(p, x.wirksam.druck, "Mitwirkende Breiten bei Druck")
            self.A = werte.flaeche("A_eff", "A_{eff}", x.wirksam.A_eff * 1e-6, "Wirksame Fläche")
        self.N_Rd = werte.kraft("N_Rd", "N_{Rd}", x.rd.N_druck, "Druckwiderstand des Querschnitts")
        referenz = REFERENZ_55 if x.klasse == 4 else REFERENZ_38
        if self.eine:
            vorlage, eingaben = sw.formel(0, "@X")
            p.formel(self.N_Rd, vorlage, {**eingaben, "X": self.A},
                     titel="Druckwiderstand des Querschnitts", referenz=referenz,
                     name=NORMALKRAFT)
        else:
            p.wert(self.N_Rd, titel="Druckwiderstand des Querschnitts, je Baustahl mit seinem f_y",
                   referenz=referenz)
        for seite in self.seiten():
            self._biegung(seite)

    def _biegung(self, seite: Zugseite) -> None:
        """Der Biegewiderstand zu einer Seite, nach der Klasse."""
        p, x, werte, sw, stahl = self.p, self.x, self.werte, self.sw, self.stab.stahl
        achse = "y" if seite.um_y else "z"
        kurz = seite.value
        M_Rd = werte.moment(f"M_Rd_{kurz}", rf"M_{{{achse},Rd}}^{{{seite.zeichen}}}",
                            x.rd.M[seite] / 1e3, "Biegewiderstand des Querschnitts")
        self.M_Rd[seite] = M_Rd
        titel = f"Biegewiderstand, {seite.beschriftung}"
        if not self.eine:
            p.wert(M_Rd, titel=f"{titel}, {_WIE[x.klasse]}, je Baustahl mit seinem f_y")
            return
        n = normale(seite)
        if x.klasse <= 2:
            W_pl = stahl.plastisch(n, stahl.nulllinie(n, sw.f))[0]
            self.W[seite] = werte.wert(f"W_pl_{kurz}", r"W_{pl}", Groesse.aus_si(W_pl * 1e-9, CM3),
                                       beschreibung="Plastisches Widerstandsmoment")
            vorlage, eingaben = sw.formel(0, "@X")
            p.formel(M_Rd, vorlage, {**eingaben, "X": self.W[seite]}, titel=titel,
                     referenz=REFERENZ_40, name=PLASTISCH)
            return
        if x.klasse == 3:
            I, z, symbol = self.e[f"I_{achse}"], max(stahl.elastisch(n).abstaende), r"W_{el}"
        else:
            g = x.wirksam.biegung[seite]
            I = werte.wert(f"I_eff_{kurz}", r"I_{eff}", Groesse.aus_si(g.I * 1e-12, MIO_MM4),
                           beschreibung="Wirksames Trägheitsmoment")
            z, symbol = g.abstand, r"W_{eff}"
        z_w = werte.laenge(f"z_{kurz}", "z", z * 1e-3, "Weiteste Faser")
        self.W[seite] = werte.wert(f"W_{kurz}", symbol,
                                   Groesse.aus_si(I.groesse.si / (z * 1e-3), CM3),
                                   beschreibung="Widerstandsmoment")
        p.formel(self.W[seite], r"\frac{@I}{@z}", {"I": I, "z": z_w},
                 titel=f"Widerstandsmoment, {seite.beschriftung}", name=WIDERSTANDSMOMENT)
        vorlage, eingaben = sw.formel(0, "@W")
        p.formel(M_Rd, vorlage, {**eingaben, "W": self.W[seite]}, titel=titel,
                 referenz=wd.REFERENZ_60 if x.klasse == 4 else wd.REFERENZ_54, name=ELASTISCH)

    # -- Knicken -------------------------------------------------------------------

    def knicken(self, achse: str) -> None:
        p, x, werte, sw = self.p, self.x, self.werte, self.sw
        k = x.knicken[achse]
        if k.gehalten:
            p.text(f"Um {achse}: gehalten, L_K,{achse} = 0 – kein Knicken um {achse}.")
            return
        L = self.L_K[achse] = werte.laenge(f"L_K_{achse}", rf"L_{{K,{achse}}}", k.L_K * 1e-3,
                                           "Knicklänge")
        self.N_cr[achse] = werte.kraft(f"N_cr_{achse}", rf"N_{{cr,{achse}}}", k.N_cr,
                                       "Ideale Knicklast")
        ganz = ", am ganzen Querschnitt" if x.klasse == 4 else ""
        p.formel(self.N_cr[achse], r"\frac{\pi^2 \cdot @E \cdot @I}{@L^2}",
                 {"E": sw.wert(0, "E_a"), "I": self.e[f"I_{achse}"], "L": L},
                 titel=f"Knicklast um {achse}{ganz}",
                 referenz="SIA 263:2013, 4.5.1.4", name="Knicklast nach Euler")
        lam = werte.zahl(f"lam_K_{achse}", rf"\bar{{\lambda}}_{{K,{achse}}}", k.lam,
                         "Schlankheit beim Knicken")
        if self.eine:
            p.formel(lam, r"\sqrt{\frac{@f_y \cdot @A}{@Ncr}}",
                     {"f_y": sw.wert(0, "f_y"), "A": self.A, "Ncr": self.N_cr[achse]},
                     titel=f"Schlankheit um {achse}",
                     referenz=st.REFERENZ_KLASSE_4 if x.klasse == 4 else "SIA 263:2013, 4.5.1.4",
                     name="Schlankheit beim Knicken")
        else:
            N_Rk = werte.kraft("N_Rk", r"N_{Rk}", x.rk.N_druck, "Σ f_y A")
            p.formel(lam, r"\sqrt{\frac{@NRk}{@Ncr}}", {"NRk": N_Rk, "Ncr": self.N_cr[achse]},
                     titel=f"Schlankheit um {achse}, mit Σ f_y A", referenz="SIA 263:2013, 4.5.1.4",
                     name="Schlankheit beim Knicken")
            p.annahme("Mit mehreren Baustählen λ̄_K = √(Σ f_y A/N_cr) – nach Vorgabe, nicht "
                      "nachgeschlagen.")
        alpha = werte.zahl(f"alpha_K_{achse}", rf"\alpha_{{K,{achse}}}", st.ALPHA_K[k.kurve],
                           "Imperfektionsbeiwert der Knickspannungskurve", stellen=2)
        p.wert(alpha, titel=f"Kurve {k.kurve}: {k.grund}",
               referenz=f"{st.REFERENZ_KURVE}; Tabelle 8")
        profil = self.stab.profil
        if (self.stab.kurven[achse] is st.Knickkurve.PROFIL and profil is not None
                and profil.form is RUNDROHR):
            p.annahme("Das Rundrohr gilt als warmgefertigt, Kurve a – nach Vorgabe, nicht "
                      "nachgeschlagen. Für ein kaltgefertigtes Kurve c wählen.")
        phi = werte.zahl(f"phi_K_{achse}", rf"\Phi_{{K,{achse}}}", k.phi, "Beiwert beim Knicken")
        p.formel(phi, r"0.5 \cdot \left(1 + @alpha \cdot \left(@lam - 0.2\right) + @lam^2\right)",
                 {"alpha": alpha, "lam": lam}, titel=f"Beiwert um {achse}",
                 referenz=st.REFERENZ_KNICKEN, name="Beiwert Φ beim Knicken")
        chi = werte.zahl(f"chi_K_{achse}", rf"\chi_{{K,{achse}}}", k.chi,
                         "Abminderung beim Knicken")
        p.formel(chi, r"\min\left(1;\ \frac{1}{@Phi + \sqrt{@Phi^2 - @lam^2}}\right)",
                 {"Phi": phi, "lam": lam}, titel=f"Abminderung um {achse}",
                 referenz=st.REFERENZ_KNICKEN, name=ABMINDERUNG)
        p.formel(werte.kraft(f"N_K_{achse}", rf"N_{{K,{achse},Rd}}", k.N_K_Rd, "Knickwiderstand"),
                 r"@chi \cdot @NRd", {"chi": chi, "NRd": self.N_Rd},
                 titel=f"Knickwiderstand um {achse}", referenz=st.REFERENZ_KNICKEN,
                 name="Knickwiderstand")
        if k.schlankheit > st.SCHLANKHEIT:
            p.hinweis(f"Schlankheit um {achse}: λ_K = L_K/i = {k.schlankheit:.0f}, über 200. "
                      f"Ein Haupttragelement sollte in der Regel nicht so schlank sein, Verbände "
                      f"und Nebentragelemente nicht über 250 ({st.REFERENZ_SCHLANKHEIT}).")

    # -- Kippen --------------------------------------------------------------------

    def kippen(self) -> None:
        p, x, werte, sw = self.p, self.x, self.werte, self.sw
        k = x.kippen
        s = k.achse
        psi = x.fall.psi(s)
        p.text(f"Kippen um die starke Achse {s}, Kipplänge L_D = {x.fall.L_D:.2f} m. Anhang B "
               f"rechnet mit Gabellagern an den Enden des Felds und einer Last in der Stabachse.")
        eta = werte.zahl("eta", r"\eta", k.eta, "Beiwert der Momentenverteilung beim Kippen")
        p.formel(eta, r"1.75 - 1.05 \cdot @psi + 0.3 \cdot @psi^2",
                 {"psi": werte.zahl("psi_D", r"\psi", max(psi, st.PSI_ETA_MIN),
                                    "Verhältnis der Endmomente", stellen=2)},
                 titel="Beiwert der Momentenverteilung", referenz=st.REFERENZ_ETA,
                 name="Beiwert η der Momentenverteilung beim Kippen")
        if psi < st.PSI_ETA_MIN:
            p.annahme(f"ψ = {psi:.2f} liegt unter −0.5, wo (94) endet: η bleibt beim Wert für "
                      f"−0.5 – nach Vorgabe, nicht nachgeschlagen.")
        i_g = self._druckgurt(k.gurt)
        L_D = werte.laenge("L_D", "L_{D}", x.fall.L_D, "Kipplänge")
        L_K = werte.laenge("L_K_D", "L_{K}", k.L_K * 1e-3, "Reduzierte Kipplänge")
        p.formel(L_K, r"\frac{@LD}{\sqrt{@eta}}", {"LD": L_D, "eta": eta},
                 titel="Reduzierte Kipplänge", referenz="SIA 263:2013, Anhang B.5, (93)")
        # In Klasse 3 steht dasselbe W_el schon beim Biegewiderstand.
        W_el = self.W.get(k.seite) if x.klasse == 3 else None
        if W_el is None:
            W_el = werte.wert("W_el_D", r"W_{el}", Groesse.aus_si(k.W_el * 1e-9, CM3),
                              beschreibung="Elastisches Widerstandsmoment, ganzer Querschnitt")
            p.wert(W_el, titel=f"Elastisches Widerstandsmoment um {s}, ganzer Querschnitt")
        s_v = werte.spannung("sigma_Dv", r"\sigma_{Dv}", k.sigma_Dv * 1e6,
                             "Saint-Venant-Anteil der ideellen Kippspannung", stellen=1)
        if x.klasse == 4:
            p.wert(s_v, titel="Ohne den Anteil nach Saint-Venant: der Querschnitt erfüllt Klasse "
                              "3 nicht", referenz="SIA 263:2013, Anhang B.4")
        else:
            p.formel(s_v, r"\frac{@eta \cdot \pi}{@LD \cdot @W} \cdot "
                          r"\sqrt{@G \cdot @K \cdot @E \cdot @I}",
                     {"eta": eta, "LD": L_D, "W": W_el, "G": sw.wert(0, "G_a"),
                      "K": self.e["I_T"], "E": sw.wert(0, "E_a"),
                      "I": self.e[f"I_{st.quer(s)}"]},
                     titel="Saint-Venant-Anteil, mit K = I_T",
                     referenz="SIA 263:2013, Anhang B.4, (92)",
                     name="Saint-Venant-Anteil der Kippspannung")
        s_w = werte.spannung("sigma_Dw", r"\sigma_{Dw}", k.sigma_Dw * 1e6,
                             "Wölbanteil der ideellen Kippspannung", stellen=1)
        p.formel(s_w, r"\frac{\pi^2 \cdot @E}{\left(@LK / @i\right)^2}",
                 {"E": sw.wert(0, "E_a"), "LK": L_K, "i": i_g},
                 titel="Wölbanteil: Knickspannung des Druckgurts nach Euler",
                 referenz="SIA 263:2013, Anhang B.5, (93)", name="Wölbanteil der Kippspannung")
        s_cr = werte.spannung("sigma_cr_D", r"\sigma_{cr,D}", k.sigma_cr * 1e6,
                              "Ideelle Kippspannung", stellen=1)
        p.formel(s_cr, r"\sqrt{@v^2 + @w^2}", {"v": s_v, "w": s_w},
                 titel="Ideelle Kippspannung", referenz="SIA 263:2013, Anhang B.3, (91)")
        M_cr = werte.moment("M_cr", r"M_{cr}", k.M_cr / 1e3, "Ideelles Kippmoment")
        p.formel(M_cr, r"@W \cdot @s", {"W": W_el, "s": s_cr}, titel="Ideelles Kippmoment",
                 referenz="SIA 263:2013, Anhang B.1, (90)")
        lam = werte.zahl("lam_D", r"\bar{\lambda}_{D}", k.lam, "Schlankheit beim Kippen")
        W = self.W.get(k.seite)
        if W is not None:
            p.formel(lam, r"\sqrt{\frac{@W \cdot @f_y}{@Mcr}}",
                     {"W": W, "f_y": sw.wert(0, "f_y"), "Mcr": M_cr},
                     titel="Schlankheit beim Kippen, W nach der Klasse",
                     referenz=st.REFERENZ_KIPPEN, name="Schlankheit beim Kippen")
        else:
            M_Rk = werte.moment("M_Rk", r"M_{Rk}", k.M_Rk / 1e3, "Σ f_y W")
            p.formel(lam, r"\sqrt{\frac{@MRk}{@Mcr}}", {"MRk": M_Rk, "Mcr": M_cr},
                     titel="Schlankheit beim Kippen, mit Σ f_y W", referenz=st.REFERENZ_KIPPEN,
                     name="Schlankheit beim Kippen")
        alpha = werte.zahl("alpha_D", r"\alpha_{D}", st.ALPHA_D_GEWALZT,
                           "Imperfektionsbeiwert beim Kippen", stellen=2)
        p.wert(alpha, titel="Imperfektionsbeiwert eines Walzprofils", referenz=st.REFERENZ_KIPPEN)
        if self.stab.profil is not None and self.stab.profil.form is not I_PROFIL:
            p.annahme("Das Rohr kippt mit dem α_D der Walzprofile – nach Vorgabe, nicht "
                      "nachgeschlagen.")
        phi = werte.zahl("phi_D", r"\Phi_{D}", k.phi, "Beiwert beim Kippen")
        p.formel(phi, r"0.5 \cdot \left(1 + @alpha \cdot \left(@lam - 0.4\right) + @lam^2\right)",
                 {"alpha": alpha, "lam": lam}, titel="Beiwert beim Kippen",
                 referenz=st.REFERENZ_KIPPEN, name="Beiwert Φ beim Kippen")
        chi = werte.zahl("chi_D", r"\chi_{D}", k.chi, "Abminderung beim Kippen")
        p.formel(chi, r"\min\left(1;\ \frac{1}{@Phi + \sqrt{@Phi^2 - @lam^2}}\right)",
                 {"Phi": phi, "lam": lam}, titel="Abminderung beim Kippen",
                 referenz=st.REFERENZ_KIPPEN, name=ABMINDERUNG)
        self.M_D = werte.moment("M_D_Rd", r"M_{D,Rd}", k.M_D_Rd / 1e3, "Kippwiderstand")
        p.formel(self.M_D, r"@chi \cdot @MRd", {"chi": chi, "MRd": self.M_Rd[k.seite]},
                 titel="Kippwiderstand", referenz=st.REFERENZ_KIPPEN, name="Kippwiderstand")
        if x.klasse == 4:
            p.annahme("In Klasse 4 zählt der ganze Druckgurt, obwohl Anhang B.5 nur die "
                      "mitwirkenden Teile zulässt: ohne die übrigen wäre sein Trägheitsradius "
                      "grösser – eine Vereinfachung auf der sicheren Seite.")
        m = x.kippen_min
        if m is not None:
            p.text(f"Zweiachsige Biegung: für (51) mit η = 1 – σ_cr,D = {m.sigma_cr:.1f} N/mm², "
                   f"λ̄_D = {m.lam:.3f}, χ_D = {m.chi:.3f}.")
            self.M_D_min = werte.moment("M_D_Rd_min", r"M_{D,Rd,min}", m.M_D_Rd / 1e3,
                                        "Kippwiderstand für konstantes Moment")
            p.wert(self.M_D_min, titel="Kippwiderstand für konstantes Moment",
                   referenz=st.REFERENZ_51)

    def _druckgurt(self, gurt: st.Druckgurt) -> Wert:
        """Der Druckgurt nach Figur 40 -- sein Traegheitsradius."""
        p, werte = self.p, self.werte
        stege = "beider Stege" if gurt.stege == 2 else "des Stegs"
        p.text(f"Druckgurt: der Flansch {gurt.b:.0f} × {gurt.t_f:.1f} mm und ein Drittel der "
               f"gedrückten Höhe {stege}, {gurt.h_c / 3:.1f} × {gurt.t_w:.1f} mm.")
        p.annahme("Der Druckgurt ohne Ausrundungen, die gedrückte Steghöhe die Hälfte der Höhe "
                  "zwischen den Flanschen" + ("; im Rechteckrohr beide Stege" if gurt.stege == 2
                                              else "") + " – nach Vorgabe, nicht nachgeschlagen.")
        A_g = werte.flaeche("A_g", "A_{g}", gurt.A * 1e-6, "Fläche des Druckgurts")
        I_g = werte.wert("I_g", "I_{g}", Groesse.aus_si(gurt.I * 1e-12, MIO_MM4),
                         beschreibung="Trägheitsmoment des Druckgurts, quer zum Flansch")
        p.wert(A_g, referenz=st.REFERENZ_DRUCKGURT)
        p.wert(I_g, referenz=st.REFERENZ_DRUCKGURT)
        i_g = werte.laenge("i_g", "i_{g}", gurt.i * 1e-3, "Trägheitsradius des Druckgurts")
        p.formel(i_g, r"\sqrt{\frac{@I}{@A}}", {"I": I_g, "A": A_g},
                 titel="Trägheitsradius des Druckgurts", referenz=st.REFERENZ_DRUCKGURT)
        return i_g

    # -- Zusammenwirken -------------------------------------------------------------

    def _omega(self, achse: str) -> Wert:
        """``ω`` um ``achse`` -- beim ersten Mal mit seiner Formel."""
        if achse not in self.omega:
            psi = self.x.fall.psi(achse)
            self.omega[achse] = self.werte.zahl(f"omega_{achse}", rf"\omega_{{{achse}}}",
                                                st.omega(psi), "Beiwert der Momentenverteilung",
                                                stellen=2)
            self.p.formel(self.omega[achse], r"\max\left(0.4;\ 0.6 + 0.4 \cdot @psi\right)",
                          {"psi": self.werte.zahl(f"psi_{achse}", rf"\psi_{{{achse}}}", psi,
                                                  "Verhältnis der Endmomente", stellen=2)},
                          titel=f"Beiwert der Momentenverteilung um {achse}",
                          referenz=st.REFERENZ_OMEGA, name="Beiwert ω der Momentenverteilung")
        return self.omega[achse]

    def gleichung_50(self) -> None:
        p, x = self.p, self.x
        p.ansatz(r"\frac{N_{Ed}}{N_{K,Rd}} + \frac{\omega_y}{1 - N_{Ed}/N_{cr,y}} \cdot "
                 r"\frac{M_{y,Ed}}{M_{y,Rd}} + \frac{\omega_z}{1 - N_{Ed}/N_{cr,z}} \cdot "
                 r"\frac{M_{z,Ed}}{M_{z,Rd}} \le 1",
                 titel="Druck und zweiachsige Biegung im Stab – N_K,Rd das kleinere, M_Rd um die "
                       "starke Achse M_D,Rd", referenz=st.REFERENZ_50,
                 name="Druck und zweiachsige Biegung im Stab")
        if x.klasse == 3:
            p.text("Klasse 3: (50) mit den elastischen Widerständen (5.2.9).")
        n = rf"\frac{{{fest(abs(x.N) / 1e3, 1)}}}{{{fest(x.N_K_Rd / 1e3, 1)}}}"
        if x.alpha_N is not None:
            p.gleichung(rf"{n} = {fest(x.n, 3)} > 1",
                        titel="Schon die Normalkraft allein trägt nicht", referenz=st.REFERENZ_50)
            return
        teile = [n] if x.N else []
        for g in x.glieder:
            self._omega(g.achse)
            rest = "" if g.rest == 1.0 else rf"\frac{{1}}{{{fest(g.rest, 3)}}} \cdot "
            teile.append(rf"{fest(g.omega, 2)} \cdot {rest}\frac{{\lambda \cdot "
                         rf"{fest(abs(g.M_Ed) / 1e6, 1)}}}{{{fest(g.M_Rd / 1e6, 1)}}}")
        p.gleichung(rf"{' + '.join(teile)} = 1 \quad\Rightarrow\quad \lambda = "
                    rf"{fest(x.alpha_50, 3)}", titel="(50): wie weit die Momente wachsen dürfen",
                    referenz=st.REFERENZ_50)
        if any(g.omega < 1.0 for g in x.glieder):
            p.hinweis("Mit ω < 1 gilt (50) im Stab; den Querschnitt am Stabende mit dem grössten "
                      "Moment weist die Tragsicherheit nach – dafür einen Lastfall mit N_Ed und "
                      "diesem Moment anlegen.")

    def gleichung_51(self) -> None:
        p, x, werte = self.p, self.x, self.werte
        g = x.g51
        s, w = g.s, g.w
        p.ansatz(r"\left(\frac{\omega_y M_{y,Ed}}{M_{y,red,Rd}}\right)^{\beta} + "
                 r"\left(\frac{\omega_z M_{z,Ed}}{M_{z,red,Rd}}\right)^{\beta} \le 1",
                 titel="Doppelsymmetrisches I, Knicken aus der Ebene und Kippen nicht verhindert – "
                       "y die starke Achse des Profils", referenz=st.REFERENZ_51,
                 name="Druck und zweiachsige Biegung im doppelsymmetrischen I-Stab")
        beta = werte.zahl("beta", r"\beta", g.beta, "Exponent der Interaktion")
        p.formel(beta, r"\max\left(1;\ 0.4 + \frac{@N}{@NRd} + \frac{@b}{@h - @tf}\right)",
                 {"N": self.N, "NRd": self.N_Rd,
                  "b": werte.laenge("b", "b", g.b * 1e-3, "Breite des Profils"),
                  "h": werte.laenge("h", "h", g.h * 1e-3, "Höhe des Profils"),
                  "tf": werte.laenge("t_f", "t_f", g.t_f * 1e-3, "Dicke des Flanschs")},
                 titel="Exponent der Interaktion", referenz=st.REFERENZ_51,
                 name="Exponent β der Interaktion")
        M_D = self.M_D if self.M_D is not None else self.M_Rd[st.seite_von(s, x.M[s])]
        N_K_min = werte.kraft("N_K_min", r"N_{K,Rd,min}", x.N_K_Rd, "Kleinerer Knickwiderstand")
        p.formel(werte.moment("M_s_red", rf"M_{{{s},red,Rd}}", g.M_s_red / 1e3,
                              "Abgeminderter Widerstand um die starke Achse"),
                 r"\min\left(@MD \cdot \left(1 - \frac{@N}{@NK}\right) \cdot "
                 r"\left(1 - \frac{@N}{@Ncr}\right);\ @omega \cdot @MDe\right)",
                 {"MD": self.M_D_min or M_D, "N": self.N, "NK": N_K_min, "Ncr": self.N_cr[s],
                  "omega": self._omega(s), "MDe": M_D},
                 titel=f"Abgeminderter Widerstand um die starke Achse {s}",
                 referenz=st.REFERENZ_51, name="Abgeminderter Kippwiderstand im Stab")
        p.formel(werte.moment("M_w_red", rf"M_{{{w},red,Rd}}", g.M_w_red / 1e3,
                              "Abgeminderter Widerstand um die schwache Achse"),
                 r"@MRd \cdot \left(1 - \frac{@N}{@NK}\right) \cdot "
                 r"\left(1 - \frac{@N}{@Ncr}\right)",
                 {"MRd": self.M_Rd[st.seite_von(w, x.M[w])], "N": self.N, "NK": N_K_min,
                  "Ncr": self.N_cr[w]},
                 titel=f"Abgeminderter Widerstand um die schwache Achse {w}",
                 referenz=st.REFERENZ_51,
                 name="Abgeminderter Biegewiderstand um die schwache Achse")
        if g.c:
            self._omega(w)
        teile = [rf"\left(\lambda \cdot {fest(t, 3)}\right)^{{{fest(g.beta, 3)}}}"
                 for t in (g.a, g.c) if t]
        p.gleichung(rf"{' + '.join(teile)} = 1 \quad\Rightarrow\quad \lambda = "
                    rf"{fest(g.alpha, 3)}",
                    titel="(51): wie weit die Momente wachsen dürfen – es gilt die günstigere "
                          "von (50) und (51)", referenz=st.REFERENZ_51)

    def kippen_allein(self) -> None:
        x = self.x
        M = abs(x.M[x.kippen.achse])
        self.p.gleichung(rf"\lambda \cdot {fest(M / 1e6, 1)} = {fest(x.kippen.M_D_Rd / 1e6, 1)} "
                         rf"\quad\Rightarrow\quad \lambda = {fest(x.alpha_9, 3)}",
                         titel="Kippen allein nach (9): M_Ed ≤ M_D,Rd", referenz=st.REFERENZ_KIPPEN)

    def gleichungen_62(self) -> None:
        p, x, werte = self.p, self.x, self.werte
        p.ansatz(r"\frac{N_{Ed}}{A_{eff}} + \frac{1}{1 - N_{Ed}/N_{cr,y}} \cdot "
                 r"\frac{M_{y,Ed} + N_{Ed}\,(e_{z} + w_{0,y})}{W_{y,eff}} + "
                 r"\frac{M_{z,Ed} + N_{Ed}\,(e_{y} + w_{0,z})}{W_{z,eff}} \le "
                 r"\frac{f_y}{\gamma_{M1}}",
                 titel="Klasse 4, (62) – in (63) steht der Faktor beim Glied um z",
                 referenz=st.REFERENZ_62, name="Druck und Biegung am wirksamen Querschnitt im Stab")
        for achse, e_N in zip(("y", "z"), x.versatz):
            if abs(e_N) > st.VERSATZ:
                p.wert(werte.laenge(f"e_N{achse}", f"e_{{N,{achse}}}", e_N * 1e-3,
                                    "Versatz des wirksamen Schwerpunkts"),
                       titel=f"Verschiebung des wirksamen Schwerpunkts in {achse}, bei Druck")
        for achse in ("y", "z"):
            k = x.knicken[achse]
            if k.gehalten:
                continue
            p.formel(werte.laenge(f"w_0_{achse}", rf"w_{{0,{achse}}}", x.w_0[achse] * 1e-3,
                                  "Ersatzimperfektion"),
                     r"\frac{@L}{@k}",
                     {"L": self.L_K[achse],
                      "k": werte.zahl(f"k_w0_{achse}", rf"k_{{{achse}}}", st.W0_NENNER[k.kurve],
                                      "Nenner der Ersatzimperfektion", stellen=0)},
                     titel=f"Ersatzimperfektion um {achse}, Kurve {k.kurve}, Spalte EE",
                     referenz="SIA 263:2013, 4.2.3.2, Figur 3", name="Ersatzimperfektion des Stabs")
        p.annahme("Die Stablänge in Figur 3 ist die Knicklänge; χ_D mindert in (62) und (63) den "
                  "Widerstand um die starke Achse – nach Vorgabe, nicht nachgeschlagen.")
        n = rf"\frac{{{fest(abs(x.N) / 1e3, 1)}}}{{{fest(x.rd.N_druck / 1e3, 1)}}}"
        for g in x.g62:
            nummer = "(62)" if g.verstaerkt == "y" else "(63)"
            faktor = f"Widerstand um {g.verstaerkt} mal 1 − N_Ed/N_cr,{g.verstaerkt}"
            if g.alpha is None:
                p.text(f"{nummer}, {faktor}: schon die Normalkraft allein trägt nicht – sie "
                       f"dürfte das {g.alpha_N:.3f}-fache sein.")
                continue
            links = " + ".join([n] + [t for t in (glied_text(gl, g.alpha if x.mit_moment else 0.0,
                                                             x.mit_moment)
                                                  for gl in g.glieder) if t])
            if x.mit_moment:
                p.gleichung(rf"{links} = 1 \quad\Rightarrow\quad \lambda = {fest(g.alpha, 3)}",
                            titel=f"{nummer}, {faktor}: wie weit die Momente wachsen dürfen",
                            referenz=st.REFERENZ_62)
            else:
                p.gleichung(rf"{links} = {fest(wd.nutzung(g.n, g.glieder, 0.0), 3)}",
                            titel=f"{nummer}, {faktor}: ohne Moment – die Normalkraft dürfte das "
                                  f"{g.alpha:.3f}-fache sein", referenz=st.REFERENZ_62)
