"""
opencivil/nachweis/qa_kennzahlen.py -- was ein gezeichneter Querschnitt aufnimmt, ohne Einwirkung.

VERANTWORTUNG:
Die Kennzahlen des gezeichneten Querschnitts, wie die der Platte
(:mod:`opencivil.nachweis.kennzahlen`) -- gerechnet immer, ob es Lastfaelle
gibt oder nicht (Benutzer, 2026-10-23):

* das Bewehrungsmass: die Laengsbewehrung je Kubikmeter Beton, wie bei der
  Platte ohne Buegel;
* je Zugseite der Momentenwiderstand bei ``N = 0`` -- unten, oben, links,
  rechts, einachsig nur unten und oben;
* der Zug- und der Druckwiderstand bei gleichmaessiger Dehnung: dieselben
  Grenzen, gegen die der M-N-Nachweis reine Normalkraft haelt;
* je Zugseite mit Bewehrung die bezogene Druckzonenhoehe ``x/d`` bei
  ``N = 0``;
* mit Schubwaenden der Widerstand gegen ``V_z``, ``V_y`` und ``T`` je
  allein: so weit laesst sich die Last steigern, bis die erste Wand ihren
  Widerstand erreicht. Was die Waende nicht tragen koennen, steht nicht da.

WAS DIE PLATTE HAT UND DIESER NICHT:
Die Hoehe der Distanzhalter und die Vergroesserungsfaktoren gehoeren den
Lagen der Platte und ihrem Verformungsnachweis; ein gezeichneter
Querschnitt hat weder Lagen noch einen Verformungsnachweis. Einen
Querkraftwiderstand ohne Buegel rechnet die Platte je Meter; hier traegt
Querkraft nur, was als Schubwand gezeichnet ist.

NICHTS ZWEIMAL:
Gerechnet wird mit der Rechenwahl der Tragsicherheit, am selben
Bruchzustand wie Duktilitaet und sproedes Versagen
(:meth:`~opencivil.querschnitt.biegung.Biegung.bei_reiner_biegung`); x und d
misst :meth:`~opencivil.querschnitt.interaktion.Querschnitt.druckzone`, die
Grenzen der Normalkraft
:meth:`~opencivil.querschnitt.interaktion.Querschnitt.normalkraft_grenzen`.
Die Schubwaende verteilen und widerstehen wie im Nachweis
(:mod:`opencivil.querschnitt.schubwaende`); die Verteilung ist linear in
der Last, darum genuegt je Richtung eine Einheitslast.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingabebezug, Eingaben, Prozedur
from opencivil.core.einheiten import EINHEITSLOS, KG_PRO_M3, KN, KNM, Groesse
from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Kennzahl, Wert, WertDef
from opencivil.material.betonstahl import STAHLDICHTE
from opencivil.querschnitt import schubwaende as sw
from opencivil.querschnitt.analyse import Querschnittsanalyse
from opencivil.querschnitt.biegung import Biegung
from opencivil.querschnitt.zugseite import Zugseite

#: Woher die Widerstaende stammen -- ihre Erklaerung unter dem Querschnitt.
BRUCH = "N_Ed = 0, Dehnungsfächer mit der Rechenwahl der Tragsicherheit"

#: Die Lasten, gegen die die Schubwaende einzeln widerstehen: Kurzname,
#: Komponente der Verteilung, Zeichen, Einheit, Beschriftung.
SCHUB = (
    ("V_z_Rd", "V_z", "V_{z,Rd}", KN, "Querkraftwiderstand in z"),
    ("V_y_Rd", "V_y", "V_{y,Rd}", KN, "Querkraftwiderstand in y"),
    ("T_Rd", "T", "T_{Rd}", KNM, "Torsionswiderstand"),
)


def _achse(seite: Zugseite) -> str:
    """Um welche Achse ein Moment diese Seite zieht: y fuer unten und oben, sonst z."""
    return "y" if seite.um_y else "z"


def _getragen(analyse: Querschnittsanalyse) -> List[str]:
    """
    Welche Lasten die Schubwaende tragen koennen -- das haengt allein an ihrer
    Lage, nicht an den Festigkeiten: V_y bei lauter senkrechten Waenden
    nicht, Torsion nicht ohne Zelle und ohne drei Waende, die sich nicht in
    einem Punkt treffen. Einachsig zaehlt V_y nicht.
    """
    if not analyse.waende:
        return []
    waende = analyse.schubwaende(f_sd=lambda _: 0.0, f_cd=lambda _: 0.0, k_c=0.0)
    modell = sw.zellen(waende)
    bezug = (analyse.brutto.y_S * 1e-3, analyse.brutto.z_S * 1e-3)
    getragen = []
    for _, last, _, _, _ in SCHUB:
        einheit = _einheit(last, analyse.biegung)
        if not any(einheit.values()):
            continue
        try:
            sw.verteilen(waende, modell, **einheit, bezug=bezug)
        except sw.WandFehler:
            continue
        getragen.append(last)
    return getragen


def _einheit(last: str, biegung: Biegung) -> Dict[str, float]:
    """
    Eine Einheitslast in dieser Richtung -- 1 N oder 1 Nm, die anderen null;
    so, wie sie wirkt: einachsig ist ``V_y`` null.
    """
    einheit = {k: (1.0 if k == last else 0.0) for k in ("V_y", "V_z", "T")}
    return {**einheit, "V_y": biegung.querkraft_y(einheit["V_y"])}


class KennzahlenQA(Prozedur):
    """Die Kennzahlen eines gezeichneten Querschnitts -- siehe Dateikopf."""

    THEMA = "Kennzahlen"

    def __init__(self, analyse: Querschnittsanalyse) -> None:
        self.analyse = analyse
        basis = f"{analyse.id}.kennzahlen"
        #: Je Kurzname die Definition -- zum Belegen.
        self.d: Dict[str, WertDef] = {}
        #: Dieselben, wie sie unter dem Querschnitt stehen, in dieser Folge.
        self.kennzahlen: List[Kennzahl] = []

        def dazu(kurz: str, symbol: str, einheit, beschreibung: str, beschriftung: str,
                 erklaerung: str, *, stellen: int = 1) -> None:
            definition = WertDef(id=f"{basis}.{kurz}", symbol=symbol, einheit=einheit,
                                 beschreibung=beschreibung, stellen=stellen)
            self.d[kurz] = definition
            self.kennzahlen.append(Kennzahl(definition, beschriftung, erklaerung))

        dazu("bewehrungsmass", r"\mu_s", KG_PRO_M3, "Bewehrungsmass je Kubikmeter Beton",
             "Bewehrungsmass",
             f"Stahldichte {STAHLDICHTE:g} kg/m³ – Längsbewehrung, ohne Bügel", stellen=0)
        for seite in analyse.zugseiten:
            dazu(f"M_Rd_{seite.value}",
                 rf"M_{{{_achse(seite)},Rd}}^{{{seite.zeichen}}}(N_{{Ed}} = 0)", KNM,
                 f"Momentenwiderstand bei N_Ed = 0, {seite.beschriftung}",
                 f"Momentenwiderstand, {seite.beschriftung}", BRUCH)
        gleichmaessig = "gleichmässige Dehnung – wie der M-N-Nachweis bei reiner Normalkraft"
        dazu("N_Rd_zug", r"N_{Rd}^{+}", KN, "Zugwiderstand bei gleichmässiger Dehnung",
             "Zugwiderstand", gleichmaessig)
        dazu("N_Rd_druck", r"N_{Rd}^{-}", KN, "Druckwiderstand bei gleichmässiger Dehnung",
             "Druckwiderstand", gleichmaessig)
        # Ein x/d nur, wo auf der gezogenen Seite Bewehrung liegt: ohne sie
        # gibt es kein d.
        self.bewehrt = [s for s in analyse.zugseiten if self._bewehrt(s)]
        for seite in self.bewehrt:
            dazu(f"x_d_{seite.value}",
                 rf"\left(x/d\right)_{{{_achse(seite)}}}^{{{seite.zeichen}}}", EINHEITSLOS,
                 f"Bezogene Druckzonenhöhe bei N_Ed = 0, {seite.beschriftung}",
                 f"Bezogene Druckzonenhöhe, {seite.beschriftung}",
                 "N_Ed = 0 – wie im Nachweis der Duktilität", stellen=3)
        self.getragen = _getragen(analyse)
        for kurz, last, symbol, einheit, beschriftung in SCHUB:
            if last in self.getragen:
                dazu(kurz, symbol, einheit, f"{beschriftung} der Schubwände, allein",
                     beschriftung,
                     "Schubwände bei der günstigsten Neigung, allein und mit N_Ed = 0 – "
                     "bis die erste Wand ihren Widerstand erreicht")

        bezuege = (list(analyse.grundbezuege()) + analyse.schubbezuege()
                   + [Eingabebezug(k, analyse.id_von(k)) for k in ("A", "A_s")])
        super().__init__(basis, ausgaben=list(self.d.values()), bezuege=bezuege,
                         titel=f"Kennzahlen – {analyse.name}", abschnitt=analyse.abschnitt)

    def _bewehrt(self, seite: Zugseite) -> bool:
        """
        Ob auf der gezogenen Seite des Schwerpunkts Bewehrung liegt -- an der
        Zeichnung entschieden, damit feststeht, welche Kennzahlen es gibt. Eine
        verschmierte Linie zaehlt mit ihren Enden.
        """
        b = self.analyse.brutto
        n = (math.cos(seite.psi), math.sin(seite.psi))
        punkte = [p for g in self.analyse.bewehrungselemente for p in (g.punkte or (g.von, g.bis))]
        return any((p[0] - b.y_S) * n[0] + (p[1] - b.z_S) * n[1] > 0.0 for p in punkte)

    # -- Rechnen ------------------------------------------------------------

    def rechne(self, e: Eingaben, p: Protokoll) -> Dict[str, Groesse]:
        p.titel("Kennzahlen")
        p.erklaerung(
            "Was der Querschnitt aufnimmt, ohne Bezug auf einen Lastfall: das "
            "Bewehrungsmass, die Widerstände bei N = 0 und bei reiner "
            "Normalkraft, die bezogene Druckzonenhöhe und, mit Schubwänden, "
            "der Widerstand gegen Querkraft und Torsion je allein. Gerechnet "
            "wird mit der Rechenwahl der Tragsicherheit.")
        werte = Zwischenwerte(self.id)
        ergebnis: Dict[str, Groesse] = {}
        self._bewehrungsmass(e, p, ergebnis)
        q, _ = self.analyse.interaktion(e)
        self._biegung(p, werte, ergebnis, q)
        if self.getragen:
            self._schub(e, p, ergebnis)
        return ergebnis

    def _belegen(self, ergebnis: Dict[str, Groesse], kurz: str, si: float) -> Wert:
        definition = self.d[kurz]
        wert = definition.belegen(Groesse.aus_si(si, definition.einheit))
        ergebnis[definition.id] = wert.groesse
        return wert

    def _bewehrungsmass(self, e: Eingaben, p: Protokoll, ergebnis: Dict[str, Groesse]) -> None:
        # Stahlvolumen je Betonvolumen: A_s * L * rho / (A * L) -- die Laenge
        # kuerzt sich heraus.
        mass = e.g("A_s").si * STAHLDICHTE / e.g("A").si
        p.formel(self._belegen(ergebnis, "bewehrungsmass", mass),
                 rf"\frac{{@A_s \cdot {STAHLDICHTE:g}\,\mathrm{{kg}}/\mathrm{{m}}^{{3}}}}{{@A}}",
                 {"A_s": e["A_s"], "A": e["A"]},
                 titel="Bewehrungsmass je Kubikmeter Beton, ohne Bügel",
                 name="Bewehrungsmass des gezeichneten Querschnitts")

    def _biegung(self, p: Protokoll, werte: Zwischenwerte, ergebnis: Dict[str, Groesse],
                 q) -> None:
        p.titel("Biegung und Normalkraft", ebene=3)
        for seite in self.analyse.zugseiten:
            punkt = self.analyse.biegung.bei_reiner_biegung(q, seite)
            betrag = 0.0 if punkt is None else self.analyse.biegung.betrag(punkt.M_y, punkt.M_z)
            p.wert(self._belegen(ergebnis, f"M_Rd_{seite.value}",
                                 betrag if seite.positiv else -betrag),
                   titel=f"Momentenwiderstand bei N_Ed = 0, {seite.beschriftung}")
            if seite not in self.bewehrt:
                continue
            x, d = (0.0, 0.0) if punkt is None else q.druckzone(punkt)
            if d <= 0.0:
                # Nur, wenn die Nulllinie im Bruch anders liegt als am
                # Schwerpunkt gedacht: dann zieht kein Stab.
                p.text(f"{seite.beschriftung}: kein gezogener Stab → x/d null.")
                self._belegen(ergebnis, f"x_d_{seite.value}", 0.0)
                continue
            p.formel(self._belegen(ergebnis, f"x_d_{seite.value}", x / d), r"\frac{@x}{@d}",
                     {"x": werte.laenge(f"x_{seite.value}", "x", x),
                      "d": werte.laenge(f"d_{seite.value}", "d", d)},
                     titel=f"Bezogene Druckzonenhöhe bei N_Ed = 0, {seite.beschriftung}",
                     name="Bezogene Druckzonenhöhe")

        zug, druck = q.normalkraft_grenzen()
        p.wert(self._belegen(ergebnis, "N_Rd_zug", zug),
               titel="Reiner Zug, gleichmässig gedehnt")
        p.wert(self._belegen(ergebnis, "N_Rd_druck", druck),
               titel="Reiner Druck, gleichmässig gedehnt")

    def _schub(self, e: Eingaben, p: Protokoll, ergebnis: Dict[str, Groesse]) -> None:
        p.titel("Querkraft und Torsion der Schubwände", ebene=3)
        p.erklaerung(
            "Jede Last allein, ohne Normalkraft, auf die Schubwände verteilt wie im "
            "Nachweis. Die Verteilung ist linear: eine Wand mit dem Widerstand "
            "v_Rd, auf die je Einheitslast der Schubfluss q₁ fällt, trägt v_Rd/q₁. "
            "Massgebend ist die Wand, die zuerst ihren Widerstand erreicht.")
        waende = self.analyse.schubwaende_mit(e)
        modell = sw.zellen(waende)
        bezug = (e.g("y_S").si, e.g("z_S").si)
        alpha_min, alpha_max = self.analyse.neigungsgrenzen(e)
        widerstaende = [sw.widerstand(w, alpha_min=alpha_min, alpha_max=alpha_max,
                                      zugkraft=False) for w in waende]
        for kurz, last, symbol, einheit, beschriftung in SCHUB:
            if last not in self.getragen:
                continue
            v = sw.verteilen(waende, modell, **_einheit(last, self.analyse.biegung),
                             bezug=bezug)
            self._eine_last(p, ergebnis, kurz, symbol, einheit, beschriftung,
                            waende, modell, v, widerstaende)

    def _eine_last(self, p: Protokoll, ergebnis: Dict[str, Groesse], kurz: str, symbol: str,
                   einheit, beschriftung: str, waende: Sequence[sw.Wand],
                   modell: sw.Zellenmodell, v: sw.Verteilung,
                   widerstaende: Sequence[sw.Wandwiderstand]) -> None:
        # Gezeigt je Einheit der Anzeige: q₁ in kN/m je kN (je kNm).
        anzeige = einheit.faktor
        zeilen = []
        massgebend: Optional[Tuple[float, sw.Wand]] = None
        for i, (w, r) in enumerate(zip(waende, widerstaende)):
            fluss = max((abs(q) for s, q in zip(modell.stuecke, v.fluss) if s.wand == i),
                        default=0.0)
            # Ein Fluss unter einem Millionstel ist Rundungsrauschen der Verteilung.
            traegt = r.v_Rd / fluss if fluss > 1e-9 else math.inf
            zeilen.append([w.name, Mathe(fest(fluss * anzeige / 1e3, 3)), Mathe(f"{r.alpha}"),
                           Mathe(fest(r.v_Rd / 1e3, 1)),
                           Mathe("\\infty" if math.isinf(traegt) else fest(traegt / anzeige, 1))])
            if massgebend is None or traegt < massgebend[0]:
                massgebend = (traegt, w)
        p.tabelle(
            kopf=["Wand", Mathe(rf"|q_1|\ [\mathrm{{kN/m}}\ \text{{je}}\ {einheit.latex}]"),
                  Mathe(r"\alpha\ [{}^{\circ}]"), Mathe(r"v_{Rd}\ [\mathrm{kN/m}]"),
                  Mathe(rf"v_{{Rd}}/|q_1|\ [{einheit.latex}]")],
            zeilen=zeilen, ausrichtung="lrrrr", titel=f"{beschriftung}: je Wand")
        wert, wand = massgebend
        p.wert(self._belegen(ergebnis, kurz, wert),
               titel=f"{beschriftung}, allein – massgebend {wand.name}")
