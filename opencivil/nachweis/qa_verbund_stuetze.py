"""
opencivil/nachweis/qa_verbund_stuetze.py -- eine Verbundstuetze nach SIA 264:2014, 5.3.

VERANTWORTUNG:
Je Stabilitaetsfall der Querschnittsanalyse ein Nachweis mit seiner
Herleitung; gerechnet wird in :mod:`opencivil.verbund.stuetze`. Vorweg,
einmal fuer alle Faelle, der Querschnitt als Stuetze (:class:`_Querschnitt`):
seine Art nach Tabelle 7, was 5.3.1 und 5.3.2 von ihm verlangen, je
Werkstoff Flaeche, Festigkeit und Traegheitsmomente, ``N_pl,Rd``, ``δ`` und
``N_pl,Rk``. Dann je Fall (:class:`_Fall`) ``E_c,eff``, die Achse ohne
Moment nach (15), die mit Moment nach (25) -- zweiachsig linear.

DER ERFUELLUNGSGRAD:
Je Nachweis der Widerstand durch die Einwirkung, massgebend der kleinste:
(15) ``χ_K N_pl,Rd/|N_Ed|``, (25) ``0.9 μ_d M_pl,Rd/M_Ed,II``, zweiachsig
``0.9/Σ``. Wo ``|N_Ed|`` ``N_cr,eff`` erreicht, knickt die Stuetze aus:
``N_cr,eff/|N_Ed|``.

WAS FEHLT -- GRAU:
Ein Querschnitt, den Tabelle 7 nicht kennt, und was
:attr:`~opencivil.verbund.stuetze.Stuetze.fehlt` und
:attr:`~opencivil.verbund.stuetze.Ergebnis.fehlt` nennen.

VORZEICHEN:
N < 0 Druck; M_y > 0 zieht unten, M_z > 0 links.
"""

from __future__ import annotations

from typing import Dict, Optional, Sequence, Tuple

from opencivil.core.berechnung import Ausfuehrung, Eingaben
from opencivil.core.einheiten import MIO_MM4, MNM2, Groesse
from opencivil.core.latex import Mathe, als_text, fest
from opencivil.core.nachweis import (
    NICHT_FUEHRBAR, OHNE_EINWIRKUNG, UNBESCHRAENKT, Nachweis, NachweisUrteil, Vergleich,
    grad_def,
)
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert, WertDef
from opencivil.material.basis import Baustoffart
from opencivil.nachweis.qa_stahl_stabilitaet import ABMINDERUNG
from opencivil.nachweis.qa_verbund_kennzahlen import ANSATZ_14, NAME_14, REFERENZ_14, verbund_von
from opencivil.nachweis.qa_verbund_werte import (
    BETON_FAKTOR, MODUL, SPANNUNG, Verbundwerte, stoffbezuege,
)
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.biegung import Biegung
from opencivil.stahlbau import stabilitaet as st
from opencivil.verbund import stuetze as vs

REFERENZ = "SIA 264:2014, 5.3"

ERKLAERUNG = (
    "Die Stütze hat den gezeichneten Querschnitt und ist an ihren Enden seitlich unverschieblich "
    "gehalten. Vorweg der Querschnitt: seine Art nach Tabelle 7, was 5.3.1 und 5.3.2 von ihm "
    "verlangen und was er plastisch trägt. Je Fall knickt die Achse ohne Moment nach (15): die "
    "Normalkraft gegen χ_K N_pl,Rd. Um die Achse mit Moment wächst es nach (24), dazu kommt die "
    "Ersatzimperfektion der Tabelle 7; (25) hält das Moment 2. Ordnung gegen μ_d M_pl,Rd aus "
    "rechteckigen Spannungsblöcken. Zweiachsig zählen beide Achsen linear zusammen.")

ANNAHME = (
    f"Doppelsymmetrisch heisst: je Werkstoff liegt der Schwerpunkt höchstens "
    f"{vs.SYMMETRIE_VERSATZ:g} mm neben der Mitte des Profils, und |I_yz| erreicht höchstens "
    f"{100.0 * vs.SYMMETRIE_I_YZ:g} % von √(I_y I_z). Die Theorie 2. Ordnung gilt immer, auch wo "
    f"(21) sie erliesse; die Imperfektion wächst mit ω = 1 und wirkt zweiachsig in beiden Achsen "
    f"zugleich. μ_d höchstens 1: ob das Moment aus der Normalkraft selbst entsteht, weiss das "
    f"Werkzeug nicht. Zweiachsig gilt die Grenze von (25) für die Summe – nach Vorgabe, nicht "
    f"nachgeschlagen.")

#: (14) im gefuellten Rohr, mit 1.0 statt 0.85 (5.3.2.5) -- eine eigene Formel.
ANSATZ_ROHR = r"N_{pl,Rd} = A_a\, f_{yd} + A_c\, 1.0\, f_{cd} + A_s\, f_{sd}"
NAME_ROHR = "Plastischer Normalkraftwiderstand eines gefüllten Rohrs"

#: Was ein Fall ohne Druck sagt.
NICHT_GEDRUECKT = ("Nicht gedrückt: die Stütze knickt nicht. Biegung allein weist die "
                   "Tragsicherheit je Lastfall nach.")

#: Das Kuerzel je Art, an den Zeichen der Gruppen: A_a, I_c, E_s.
_KUERZEL = {Baustoffart.BAUSTAHL: "a", Baustoffart.BETON: "c", Baustoffart.BETONSTAHL: "s"}


def _nulllinie(lage: Optional[float]) -> str:
    """Wo die Nulllinie liegt, in Worten -- von der Mitte zur gezogenen oder gedrueckten Seite."""
    if lage is None:
        return "N_Ed übersteigt N_pl,Rd, der Querschnitt trägt nichts mehr"
    seite = "gezogenen" if lage >= 0.0 else "gedrückten"
    return f"die Nulllinie {abs(lage):.1f} mm von der Mitte zur {seite} Seite"


class VerbundStuetzeQA(Nachweis):
    """Eine Verbundstuetze, je Fall -- siehe Dateikopf. ``kriechzahl`` ist ``φ(t,t_0)``."""

    THEMA = "Verbundstütze"
    ART = "Stab"

    def __init__(self, analyse: Querschnittsanalyse, faelle: Sequence[st.Stabfall],
                 kriechzahl: float) -> None:
        self.analyse = analyse
        self.faelle = list(faelle)
        self.kriechzahl = kriechzahl
        self.verbund = verbund_von(analyse)
        basis = f"{analyse.id}.nachweis.verbund_stuetze"
        self.d_ausnutzung: Dict[str, WertDef] = {
            f.name: grad_def(f"{basis}.{f.kennung}.erfuellungsgrad",
                             rf"\alpha_{{eff,{als_text(f.name)}}}",
                             f"Erfüllungsgrad Verbundstütze – {f.name}", REFERENZ)
            for f in self.faelle}
        moduln = [g.stoff.bezug(MODUL[g.stoff.art]) for g in self.verbund.gruppen
                  if g.stoff.art is not Baustoffart.BAUSTAHL]
        super().__init__(basis, ausgaben=list(self.d_ausnutzung.values()),
                         bezuege=stoffbezuege(self.verbund) + moduln,
                         titel=f"Verbundstütze – {analyse.name}", referenz=REFERENZ,
                         abschnitt=analyse.abschnitt)

    # -- Pruefen ----------------------------------------------------------------

    def pruefe(self, e: Eingaben, p: Protokoll):
        p.titel("Verbundstütze")
        p.erklaerung(ERKLAERUNG)
        art, grund = vs.querschnittsart(self.verbund)
        if art is None:
            return self._grau(p, grund)
        p.annahme(ANNAHME)
        faktor = vs.ROHR_FAKTOR if art is vs.Art.ROHR else BETON_FAKTOR
        werte = Verbundwerte(self.verbund, e, self.analyse.wahl, beton_faktor=faktor)
        gruppen = range(len(self.verbund.gruppen))
        stuetze = vs.Stuetze(
            self.verbund, art,
            vs.Festigkeiten(tuple(werte.zug), tuple(werte.druck), tuple(werte.druck_k),
                            tuple(werte.E(g) for g in gruppen)),
            eps=werte.eps[self.verbund.stahl.teile[0].gruppe], hochfest=werte.hochfest)
        q = _Querschnitt(p, werte, stuetze, self.id)
        if stuetze.fehlt:
            return self._grau(p, stuetze.fehlt)
        return Ausfuehrung({}, [self._ein_fall(p, q, fall) for fall in self.faelle])

    def _grau(self, p: Protokoll, grund: str) -> Ausfuehrung:
        """Jeder Fall grau, mit demselben Grund: er liegt am Querschnitt."""
        p.hinweis(grund)
        return Ausfuehrung({}, [self.urteil(self.d_ausnutzung[f.name], f.name, NICHT_FUEHRBAR,
                                            grund) for f in self.faelle])

    # -- Ein Fall ---------------------------------------------------------------

    def _ein_fall(self, p: Protokoll, q: "_Querschnitt", fall: st.Stabfall) -> NachweisUrteil:
        d_grad = self.d_ausnutzung[fall.name]
        p.titel(fall.name, ebene=3)
        _einwirkung(p, self.analyse.biegung, fall)
        M = vs.momente(self.analyse.biegung.wirkt(fall.M_y, fall.M_z))
        if fall.N >= 0.0:
            text = NICHT_GEDRUECKT if any(M.values()) else OHNE_EINWIRKUNG
            p.text(text)
            return self.urteil(d_grad, fall.name, UNBESCHRAENKT, text)
        x = vs.rechnen(q.s, fall, self.kriechzahl, M)
        if x.fehlt:
            p.hinweis(x.fehlt)
            return self.urteil(d_grad, fall.name, NICHT_FUEHRBAR, x.fehlt)
        r = _Fall(p, Zwischenwerte(f"{self.id}.{fall.kennung}"), q, x, self.kriechzahl)
        name, _ = x.massgebend
        v = r.vergleiche[name]
        v.zeile(p, d_grad)
        return self.urteil(d_grad, fall.name, v, f"{name}, bei N_Ed = {fall.N / 1e3:.1f} kN.")


def _einwirkung(p: Protokoll, biegung: Biegung, fall: st.Stabfall) -> None:
    """Die Einwirkung und die Stuetze als Tabelle -- einachsig ohne M_z."""
    zeilen = [["N_Ed", Mathe(fest(fall.N / 1e3, 1)), "kN"],
              ["N_G,Ed/N_Ed", Mathe(fest(100.0 * fall.staendig, 0)), "%"]]
    for achse, M in biegung.momente(fall.M_y, fall.M_z):
        zeilen.append([f"M_{achse},Ed", Mathe(fest(M / 1e3, 1)), "kNm"])
        if M:
            zeilen.append([f"ψ_{achse}", Mathe(fest(fall.psi(achse), 2)), ""])
    zeilen += [["L_K,y", Mathe(fest(fall.L_K_y, 2)), "m"],
               ["L_K,z", Mathe(fest(fall.L_K_z, 2)), "m"],
               ["L", Mathe(fest(fall.L, 2)), "m"]]
    p.tabelle(kopf=["Einwirkung und Stütze", "Wert", ""], zeilen=zeilen,
              titel="Einwirkung 1. Ordnung, ohne Imperfektion; eine Knicklänge null heisst "
                    "gehalten", ausrichtung="lrl")


class _Querschnitt:
    """Der Querschnitt als Stuetze, vorweg fuer alle Faelle -- mit den Werten, die sie lesen."""

    def __init__(self, p: Protokoll, werte: Verbundwerte, s: vs.Stuetze, basis: str) -> None:
        self.p, self.werte, self.s = p, werte, s
        self.z = Zwischenwerte(f"{basis}.querschnitt")
        je_art: Dict[Baustoffart, int] = {}
        for w in s.werkstoffe:
            je_art[w.art] = je_art.get(w.art, 0) + 1
        zaehler: Dict[Baustoffart, int] = {}
        self.kuerzel: Dict[int, str] = {}
        for w in s.werkstoffe:
            zaehler[w.art] = zaehler.get(w.art, 0) + 1
            nummer = f",{zaehler[w.art]}" if je_art[w.art] > 1 else ""
            self.kuerzel[w.gruppe] = f"{_KUERZEL[w.art]}{nummer}"
        self.E: Dict[int, Wert] = {w.gruppe: werte.wert(w.gruppe, MODUL[w.art])
                                   for w in s.werkstoffe}
        self.I: Dict[Tuple[int, str], Wert] = {
            (w.gruppe, a): self.z.wert(f"I_{a}_{w.gruppe}", rf"I_{{{self.kuerzel[w.gruppe]},{a}}}",
                                       Groesse.aus_si(w.I(a) * 1e-12, MIO_MM4),
                                       beschreibung=f"Trägheitsmoment von {w.name} um {a}")
            for w in s.werkstoffe for a in ("y", "z")}
        self._art()
        self._tabelle()
        self._normalkraft()

    def _art(self) -> None:
        p, s = self.p, self.s
        p.text(f"{s.lage.beschreibung}, {s.art.value}: so kennt Tabelle 7 den Querschnitt "
               f"({vs.REFERENZ_ART}).")
        if not s.unsymmetrisch:
            p.text("Doppelsymmetrisch: je Werkstoff liegt der Schwerpunkt in der Mitte des "
                   "Profils, und I_yz ist null.")
        h, b = s.masse
        p.text(f"Über alles h × b = {h:.0f} × {b:.0f} mm, h/b = {s.hb:.2f} – zulässig von "
               f"{vs.HB_AB:g} bis {vs.HB_BIS:g} ({vs.REFERENZ_HB}).")
        if s.beulen is None:
            p.text("Ganz einbetoniert: das lokale Beulen braucht keinen Nachweis (5.3.1.7).")
        else:
            zeichen, wert, grenze, wie = s.beulen
            p.text(f"Gegen das lokale Beulen: {zeichen} = {wert:.1f}, höchstens {wie} = "
                   f"{grenze:.1f} mit ε = {s.eps:.3f} ({vs.REFERENZ_BEULEN}).")

    def _tabelle(self) -> None:
        p, s, f = self.p, self.s, self.s.f
        einheit = r"\ [10^6\,\mathrm{mm}^4]"
        p.tabelle(
            kopf=["Werkstoff", Mathe(r"A\ [\mathrm{mm}^2]"), Mathe("f_d" + SPANNUNG),
                  Mathe("f_k" + SPANNUNG), Mathe("E" + SPANNUNG), Mathe("I_y" + einheit),
                  Mathe("I_z" + einheit)],
            zeilen=[[w.name, Mathe(fest(w.A, 0)), Mathe(fest(f.druck[w.gruppe], 1)),
                     Mathe(fest(f.druck_k[w.gruppe], 1)), Mathe(fest(f.E[w.gruppe], 0)),
                     Mathe(fest(w.I_y / 1e6, 1)), Mathe(fest(w.I_z / 1e6, 1))]
                    for w in s.werkstoffe],
            titel="Je Werkstoff, um die Mitte des Profils", ausrichtung="lrrrrrr")
        beton = (f"im gefüllten Rohr mit {vs.ROHR_FAKTOR:.1f} f_ck (5.3.2.5)"
                 if s.art is vs.Art.ROHR else f"mit {BETON_FAKTOR:g} f_ck")
        p.text(f"f_d gedrückt mit der Wahl der Tragsicherheit, f_k mit γ = 1; der Beton {beton}, "
               f"ohne die Fläche von Profil und Stäben.")
        if s.anteil_s < 1.0:
            p.text(f"Der Betonstahl hat ρ_s = {100.0 * s.rho_s:.1f} % der Betonfläche und zählt "
                   f"mit höchstens {100.0 * vs.BEWEHRUNG_BIS:g} % ({vs.REFERENZ_BEWEHRUNG}): mit "
                   f"dem Anteil {s.anteil_s:.3f}, in N_pl, M_pl und EI.")

    def _normalkraft(self) -> None:
        p, s, z = self.p, self.s, self.z
        rohr = s.art is vs.Art.ROHR
        referenz = vs.REFERENZ_N_PL_ROHR if rohr else REFERENZ_14
        if rohr:
            p.ansatz(ANSATZ_ROHR, titel="Plastischer Normalkraftwiderstand, Teil für Teil – der "
                                        "Beton im gefüllten Rohr mit 1.0",
                     referenz=referenz, name=NAME_ROHR)
        else:
            p.ansatz(ANSATZ_14, titel="Plastischer Normalkraftwiderstand, Teil für Teil",
                     referenz=referenz, name=NAME_14)
        self.N_pl_Rd = z.kraft("N_pl_Rd", r"N_{pl,Rd}", s.N_pl(),
                               "Plastischer Normalkraftwiderstand")
        p.wert(self.N_pl_Rd, titel="Plastischer Normalkraftwiderstand: Σ f_d A",
               referenz=referenz)
        N_a = z.kraft("N_pl_a", r"N_{pl,a,Rd}", s.N_a, "Normalkraftwiderstand des Profils")
        p.wert(N_a, titel="Das Profil allein: A_a f_yd")
        p.formel(z.zahl("delta", r"\delta", s.delta, "Querschnittsparameter"),
                 r"\frac{@Na}{@Npl}", {"Na": N_a, "Npl": self.N_pl_Rd},
                 titel=f"Querschnittsparameter, von {vs.DELTA_AB:g} bis {vs.DELTA_BIS:g}",
                 referenz=vs.REFERENZ_DELTA, name="Querschnittsparameter einer Verbundstütze")
        self.N_pl_Rk = z.kraft("N_pl_Rk", r"N_{pl,Rk}", s.N_pl(charakteristisch=True),
                               "Plastischer Normalkraftwiderstand mit γ = 1")
        p.wert(self.N_pl_Rk, titel="Dasselbe mit γ = 1, für die Schlankheit: Σ f_k A",
               referenz=vs.REFERENZ_N_PL_K)

    def steifigkeit(self, achse: str, E_c: Dict[int, Wert],
                    beton: float) -> Tuple[str, Dict[str, Wert]]:
        """
        ``Σ E I`` um ``achse`` als Vorlage mit ihren Werten -- der Beton mit
        ``beton · E_c,eff``, der Betonstahl mit seinem Anteil (5.3.2.2).
        """
        glieder, eingaben = [], {}
        for w in self.s.werkstoffe:
            k = self.kuerzel[w.gruppe].replace(",", "")
            vor = (rf"{beton:g} \cdot " if w.art is Baustoffart.BETON else
                   rf"{fest(self.s.anteil_s, 3)} \cdot " if self.s.zaehlt(w) < 1.0 else "")
            glieder.append(rf"{vor}@E{k} \cdot @I{k}")
            eingaben[f"E{k}"] = E_c[w.gruppe] if w.art is Baustoffart.BETON else self.E[w.gruppe]
            eingaben[f"I{k}"] = self.I[(w.gruppe, achse)]
        return " + ".join(glieder), eingaben


class _Fall:
    """Die Herleitung eines Falls -- je Achse, mit den Vergleichen, die er fuehrt."""

    def __init__(self, p: Protokoll, werte: Zwischenwerte, q: _Querschnitt, x: vs.Ergebnis,
                 kriechzahl: float) -> None:
        self.p, self.werte, self.q, self.x = p, werte, q, x
        self.vergleiche: Dict[str, Vergleich] = {}
        self.N_Ed = werte.kraft("N_Ed", "N_{Ed}", x.N)
        self.N = werte.kraft("N_betrag", r"|N_{Ed}|", abs(x.N), "Druckkraft")
        self.E_c = self._kriechen(kriechzahl)
        self.alpha_M = werte.zahl("alpha_M", r"\alpha_M", x.alpha_M, "Grenze in (25)", stellen=1)
        for k in x.knicken.values():
            self._knicken(k)
        teile = {a: self._biegung(b) for a, b in x.biegung.items()}
        if len(teile) > 1 and all(teile.values()):
            self._zweiachsig(teile)

    def _kriechen(self, kriechzahl: float) -> Dict[int, Wert]:
        """(19) je Beton."""
        p, werte, x = self.p, self.werte, self.x
        anteil = werte.zahl("anteil_G", r"N_{G,Ed}/N_{Ed}", x.fall.staendig,
                            "Ständiger Anteil der Normalkraft", stellen=2)
        phi = werte.zahl("phi", r"\varphi", kriechzahl, "Kriechzahl", stellen=2)
        E_c = {}
        for w in self.q.s.der_art(Baustoffart.BETON):
            k = self.q.kuerzel[w.gruppe]
            E_c[w.gruppe] = werte.spannung(f"E_c_eff_{w.gruppe}", rf"E_{{{k},eff}}",
                                           x.E_c[w.gruppe] * 1e6,
                                           "Wirksamer Elastizitätsmodul des Betons")
            p.formel(E_c[w.gruppe], r"\frac{@E}{1 + @r \cdot @phi}",
                     {"E": self.q.E[w.gruppe], "r": anteil, "phi": phi},
                     titel=f"Wirksamer Elastizitätsmodul von {w.name}, mit dem Kriechen",
                     referenz=vs.REFERENZ_E_C,
                     name="Wirksamer Elastizitätsmodul des Betons einer Verbundstütze")
        return E_c

    def _steifigkeit(self, kennung: str, symbol: str, si: float) -> Wert:
        """Eine Biegesteifigkeit, ``si`` in N mm²."""
        return self.werte.wert(kennung, symbol, Groesse.aus_si(si * 1e-6, MNM2),
                               beschreibung="Biegesteifigkeit")

    # -- Die Achse ohne Moment -------------------------------------------------------

    def _knicken(self, k: vs.Knicken) -> None:
        p, werte, q, a = self.p, self.werte, self.q, k.achse
        p.titel(f"Knicken um {a}", ebene=4)
        if k.gehalten:
            p.text(f"Gehalten, L_K,{a} = 0: kein Knicken um {a}, χ_K = 1.")
            N_K = q.N_pl_Rd
        else:
            vorlage, eingaben = q.steifigkeit(a, self.E_c, vs.BETON_LAMBDA)
            EI = self._steifigkeit(f"EI_{a}", rf"(EI)_{{eff,\lambda,{a}}}", k.EI)
            p.formel(EI, vorlage, eingaben, titel=f"Biegesteifigkeit um {a}, für die Schlankheit",
                     referenz=vs.REFERENZ_EI,
                     name="Biegesteifigkeit einer Verbundstütze für die Schlankheit")
            L = werte.laenge(f"L_K_{a}", rf"L_{{K,{a}}}", k.L_K * 1e-3, "Knicklänge")
            N_cr = werte.kraft(f"N_cr_{a}", rf"N_{{cr,{a}}}", k.N_cr, "Kritische Normalkraft")
            p.formel(N_cr, r"\frac{\pi^2 \cdot @EI}{@L^2}", {"EI": EI, "L": L},
                     titel=f"Kritische Normalkraft um {a}", referenz=vs.REFERENZ_N_CR,
                     name="Kritische Normalkraft einer Verbundstütze")
            lam = werte.zahl(f"lam_{a}", rf"\bar{{\lambda}}_{{{a}}}", k.lam, "Bezogene Schlankheit")
            p.formel(lam, r"\sqrt{\frac{@NRk}{@Ncr}}", {"NRk": q.N_pl_Rk, "Ncr": N_cr},
                     titel=f"Bezogene Schlankheit um {a}, höchstens {vs.LAMBDA_BIS:g}",
                     referenz=vs.REFERENZ_LAMBDA, name="Bezogene Schlankheit einer Verbundstütze")
            alpha = werte.zahl(f"alpha_K_{a}", rf"\alpha_{{K,{a}}}", st.ALPHA_K[k.kurve],
                               "Imperfektionsbeiwert der Knickspannungskurve", stellen=2)
            p.wert(alpha, titel=f"Kurve {k.kurve}: {k.grund}",
                   referenz=f"{vs.REFERENZ_KURVE}; SIA 263:2013, Tabelle 8")
            phi = werte.zahl(f"phi_K_{a}", rf"\Phi_{{K,{a}}}", k.phi, "Beiwert beim Knicken")
            p.formel(phi,
                     r"0.5 \cdot \left(1 + @alpha \cdot \left(@lam - 0.2\right) + @lam^2\right)",
                     {"alpha": alpha, "lam": lam}, titel=f"Beiwert um {a}",
                     referenz=st.REFERENZ_KNICKEN, name="Beiwert Φ beim Knicken")
            chi = werte.zahl(f"chi_K_{a}", rf"\chi_{{K,{a}}}", k.chi, "Abminderung beim Knicken")
            p.formel(chi, r"\min\left(1;\ \frac{1}{@Phi + \sqrt{@Phi^2 - @lam^2}}\right)",
                     {"Phi": phi, "lam": lam}, titel=f"Abminderung um {a}",
                     referenz=st.REFERENZ_KNICKEN, name=ABMINDERUNG)
            N_K = werte.kraft(f"N_K_{a}", rf"N_{{K,{a},Rd}}", k.N_K_Rd, "Knickwiderstand")
            p.formel(N_K, r"@chi \cdot @Npl", {"chi": chi, "Npl": q.N_pl_Rd},
                     titel=f"Knickwiderstand um {a}", referenz=vs.REFERENZ_15,
                     name="Knickwiderstand einer Verbundstütze")
        self.vergleiche[f"(15) um {a}"] = Vergleich(
            self.N_Ed, werte.kraft(f"N_K_Rd_{a}", rf"N_{{K,{a},Rd}}", -N_K.groesse.si))

    # -- Die Achse mit Moment ---------------------------------------------------------

    def _biegung(self, b: vs.Biegeachse) -> Optional[Tuple[Wert, Wert, Wert]]:
        """
        Die Achse mit Moment, bis ``M_Ed,II``, ``μ_d`` und ``M_pl,Rd`` -- die
        gibt sie zurueck, oder ``None``, wo die Stuetze ausknickt.
        """
        p, werte, x, a = self.p, self.werte, self.x, b.achse
        p.titel(f"Biegung um {a}", ebene=4)
        M = werte.moment(f"M_{a}_betrag", rf"|M_{{{a},Ed}}|", b.M * 1e-3, "Moment 1. Ordnung")
        M_II = werte.moment(f"M_II_{a}", rf"M_{{{a},Ed,II}}", b.M_II * 1e-3,
                            "Moment nach Theorie 2. Ordnung")
        if b.gehalten:
            p.text(f"Gehalten, L_K,{a} = 0: das Moment wächst nicht, ohne Imperfektion – "
                   f"M_{a},Ed,II = |M_{a},Ed| = {b.M / 1e6:.1f} kNm.")
        elif not self._zweite_ordnung(b, M, M_II):
            return None
        mu, M_pl = self._interaktion(b)
        if len(x.biegung) == 1:
            M_Rd = werte.moment(f"M_Rd_{a}", rf"M_{{{a},Rd}}", x.alpha_M * b.mu * b.M_pl * 1e-3,
                                "Widerstand nach (25)")
            hoch = ", S420 oder S460: 0.8" if x.alpha_M == vs.ALPHA_M_HOCHFEST else ""
            p.formel(M_Rd, r"@alpha \cdot @mu \cdot @M",
                     {"alpha": self.alpha_M, "mu": mu, "M": M_pl},
                     titel=f"Widerstand um {a} nach (25){hoch}", referenz=vs.REFERENZ_25,
                     name="Widerstand einer Verbundstütze nach (25)")
            self.vergleiche[f"(25) um {a}"] = Vergleich(M_II, M_Rd)
        return M_II, mu, M_pl

    def _zweite_ordnung(self, b: vs.Biegeachse, M: Wert, M_II: Wert) -> bool:
        """(22) bis (24) und die Imperfektion -- falsch, wo die Stuetze ausknickt."""
        p, werte, q, x, a = self.p, self.werte, self.q, self.x, b.achse
        vorlage, eingaben = q.steifigkeit(a, self.E_c, vs.BETON_D)
        EI = self._steifigkeit(f"EI_d_{a}", rf"(EI)_{{eff,d,{a}}}", b.EI_d)
        p.formel(EI, rf"{vs.BEIWERT_D:g} \cdot \left({vorlage}\right)", eingaben,
                 titel=f"Bemessungssteifigkeit um {a}", referenz=vs.REFERENZ_EI_D,
                 name="Bemessungssteifigkeit einer Verbundstütze")
        L = werte.laenge("L", "L", x.fall.L, "Länge der Stütze")
        N_cr = werte.kraft(f"N_cr_eff_{a}", rf"N_{{cr,eff,{a}}}", b.N_cr_eff,
                           "Kritische Normalkraft für die Bemessung")
        p.formel(N_cr, r"\frac{\pi^2 \cdot @EI}{@L^2}", {"EI": EI, "L": L},
                 titel=f"Kritische Normalkraft um {a}, mit der Länge der Stütze",
                 referenz=vs.REFERENZ_N_CR_EFF,
                 name="Kritische Normalkraft einer Verbundstütze")
        if b.knickt_aus:
            p.text(f"|N_Ed| erreicht N_cr,eff,{a}: die Stütze knickt aus, k wächst ohne Grenze.")
            self.vergleiche[f"(24) um {a}: N_Ed erreicht N_cr,eff"] = Vergleich(
                self.N_Ed, werte.kraft(f"N_cr_eff_{a}_druck", rf"N_{{cr,eff,{a}}}", -b.N_cr_eff))
            return False
        psi = werte.zahl(f"psi_{a}", rf"\psi_{{{a}}}", b.psi, "Verhältnis der Endmomente",
                         stellen=2)
        omega = werte.zahl(f"omega_{a}", rf"\omega_{{{a}}}", b.omega,
                           "Beiwert der Momentenverteilung", stellen=2)
        p.formel(omega, r"\max\left(0.4;\ 0.6 + 0.4 \cdot @psi\right)", {"psi": psi},
                 titel=f"Beiwert der Momentenverteilung um {a}", referenz=st.REFERENZ_OMEGA,
                 name="Beiwert ω der Momentenverteilung")
        k = werte.zahl(f"k_{a}", rf"k_{{{a}}}", b.k, "Vergrösserungsfaktor")
        p.formel(k, r"\max\left(1;\ \frac{@omega}{1 - @N / @Ncr}\right)",
                 {"omega": omega, "N": self.N, "Ncr": N_cr},
                 titel=f"Vergrösserungsfaktor um {a}", referenz=vs.REFERENZ_K,
                 name="Vergrösserungsfaktor einer Verbundstütze")
        k_0 = werte.zahl(f"k_0_{a}", rf"k_{{0,{a}}}", b.k_0,
                         "Vergrösserungsfaktor der Imperfektion")
        p.formel(k_0, r"\frac{1}{1 - @N / @Ncr}", {"N": self.N, "Ncr": N_cr},
                 titel=f"Dasselbe für die Imperfektion, mit ω = 1", referenz=vs.REFERENZ_K,
                 name="Vergrösserungsfaktor der Imperfektion einer Verbundstütze")
        kurve, _, _ = q.s.kurve(a)
        e_0 = werte.laenge(f"e_0_{a}", rf"e_{{0,{a}}}", b.e_0 * 1e-3, "Ersatzimperfektion")
        p.formel(e_0, rf"\frac{{@L}}{{{b.nenner:g}}}", {"L": L},
                 titel=f"Ersatzimperfektion um {a}: Kurve {kurve}, L/{b.nenner:g}",
                 referenz=vs.REFERENZ_E_0, name="Ersatzimperfektion einer Verbundstütze")
        p.formel(M_II, r"@k \cdot @M + @k0 \cdot @N \cdot @e",
                 {"k": k, "M": M, "k0": k_0, "N": self.N, "e": e_0},
                 titel=f"Moment nach Theorie 2. Ordnung um {a}", referenz=vs.REFERENZ_K,
                 name="Moment 2. Ordnung einer Verbundstütze")
        return True

    def _interaktion(self, b: vs.Biegeachse) -> Tuple[Wert, Wert]:
        """
        ``M_pl,Rd``, ``M_pl,N,Rd`` und ``μ_d`` (Figur 7) -- zurueck gibt es
        ``μ_d`` und ``M_pl,Rd``.
        """
        p, werte, a = self.p, self.werte, b.achse
        seite = st.seite_von(a, self.x.fall.M_y if a == "y" else self.x.fall.M_z)
        M_pl = werte.moment(f"M_pl_{a}", rf"M_{{pl,{a},Rd}}", b.M_pl * 1e-3,
                            "Plastischer Biegewiderstand")
        p.wert(M_pl, titel=f"Plastischer Biegewiderstand um {a}, {seite.beschriftung}: "
                           f"{_nulllinie(b.lage[0])}", referenz=vs.REFERENZ_MU)
        M_N = werte.moment(f"M_pl_N_{a}", rf"M_{{pl,N,{a},Rd}}", b.M_pl_N * 1e-3,
                           "Plastischer Biegewiderstand bei N_Ed")
        p.wert(M_N, titel=f"Dasselbe bei N_Ed: {_nulllinie(b.lage[1])}", referenz=vs.REFERENZ_MU)
        mu = werte.zahl(f"mu_d_{a}", rf"\mu_{{d,{a}}}", b.mu, "Beiwert der Interaktion")
        p.formel(mu, r"\min\left(1;\ \frac{@MN}{@M}\right)", {"MN": M_N, "M": M_pl},
                 titel=f"Beiwert der Interaktion um {a}, höchstens 1", referenz=vs.REFERENZ_MU,
                 name="Beiwert μ_d einer Verbundstütze")
        return mu, M_pl

    def _zweiachsig(self, teile: Dict[str, Tuple[Wert, Wert, Wert]]) -> None:
        """5.3.5: beide Achsen linear -- gegen die Grenze von (25)."""
        summe = self.werte.zahl("summe", r"\sum \frac{M_{Ed,II}}{\mu_d\, M_{pl,Rd}}", self.x.summe,
                                "Ausnutzung, zweiachsig")
        eingaben = {f"{k}{a}": w for a, t in teile.items() for k, w in zip(("M", "mu", "P"), t)}
        self.p.formel(summe, r"\frac{@My}{@muy \cdot @Py} + \frac{@Mz}{@muz \cdot @Pz}", eingaben,
                      titel="Zweiachsig: beide Achsen linear zusammen",
                      referenz=f"{vs.REFERENZ_ZWEIACHSIG}; {vs.REFERENZ_25}",
                      name="Zweiachsige Biegung einer Verbundstütze")
        self.vergleiche["(25) zweiachsig"] = Vergleich(summe, self.alpha_M)
