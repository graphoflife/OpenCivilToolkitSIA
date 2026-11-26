"""
opencivil/decke/herleitung.py -- wie eine Decke ihre Rechnung aufschreibt.

VERANTWORTUNG:
Die Herleitung der Streifenmethode, so dass man sie von Hand nachvollziehen
kann: die Decke in Tabellen -- Platten, Linienlager, Stützen, Unterzüge,
Lasten je Lastfall und die Kombinationen --, die Streifen je Richtung, in
welcher Reihenfolge die Träger rechnen, wie die Last auf die Richtungen
geht, je Fall die Last und was die Lager davon tragen, und die Meldungen.
Dann die Ansätze -- trägt eine Platte schief zu x und y, mit einem Hinweis
zur Fliessbedingung -- und je Lastfall und Kombination: jeder Träger mit Last,
Lagerkräften und Momenten, was jedes Lager trägt, die grössten
Schnittkräfte der Platte, die Biegewiderstände, die sie verlangt, und die
Lastverteilelemente.

DIESELBEN ZAHLEN WIE IM BILD:
Die grössten Schnittkräfte und Biegewiderstände kommen von den Proben des
Falls (:func:`~opencivil.decke.feld.proben`), wie in den Bildern.

GLEICHE TRÄGER IN EINER ZEILE:
Tragen nebeneinander liegende Träger dasselbe -- im Kolloquium 4 achtzehn
Feldstreifen in x --, stehen sie in einer Zeile, «x1 … x18». Was sie
unterscheidet, ist nur ihr Ort quer; ``s`` misst längs.

EINHEITEN:
Längen in m, Dicken und Stützen in mm, Winkel in Grad gegen x, E in N/mm²,
Gewichte und Flächenlasten in kN/m², Linienlasten in kN/m, Kräfte in kN.
Die Träger je Meter ihrer Breite: Lasten und Lagerkräfte in kN/m, Momente
in kNm/m, wie die Schnittkräfte der Platte.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.decke import feld
from opencivil.decke import geometrie as geo
from opencivil.decke.aufteilung import GANZ_AB
from opencivil.decke.modell import Aufteilung, Decke, Flaechenlast, Last, Linienlast, Punktlast
from opencivil.decke.rechnung import Ergebnis, Fallergebnis, lagerverlauf, spitzen
from opencivil.decke.streifen import Streifen, Traeger, Zerlegung, richtungen_der_platte
from opencivil.stabwerk.verlauf import extremwerte

if TYPE_CHECKING:
    from opencivil.decke.werk import Deckenbefund, Deckensystem

#: Was die Streifenmethode annimmt.
ANNAHME = (
    "Streifenmethode (Stahlbeton II, 7.2 Platten, Folien 27 bis 39): jede Last geht in Streifen "
    "zweier Richtungen zu den Lagern; die Streifen selbst tragen ohne Drillmoment. Das ist eine "
    "Gleichgewichtslösung nach der statischen Methode und damit ein unterer Grenzwert der "
    "Traglast (SIA 262:2025, 4.1.4.2.2) – für die Tragsicherheit (4.1.4.2.1), und nur, wenn das "
    "Verformungsvermögen gesichert ist (4.1.4.2.4). Statisch unbestimmte Streifen sind elastisch "
    "gelöst, mit E_cm · h³/12 je Meter der ungerissenen Platte (4.1.4.1.3); ein Unterzug trägt "
    "als Flächenlager mit gleichmässiger Pressung über seine Breite (Folie 33).")

#: Die automatische Aufteilung in Worten -- die Regel steht in :mod:`~opencivil.decke.aufteilung`.
AUTOMATISCH = (
    "Automatisch, nach Folie 31 verallgemeinert: je Zelle zweier Feldstreifen trägt die Richtung, "
    "die Lager hat. Tragen beide, geht die Last zum nahen Rand, wenn sie näher als ein Viertel der "
    "kürzeren Spannweite an einem Lager liegt, nahe zweier Ränder je zur Hälfte. Sonst geht sie "
    "mehr in die kürzere Spannweite: bei gleichen je zur Hälfte, ab dem Verhältnis "
    f"{fest(GANZ_AB, 1)} ganz, dazwischen geradlinig. Ein Kragarm zählt doppelt (nach Vorgabe; "
    "die Norm lässt jede Aufteilung zu, die im Gleichgewicht ist, SIA 262:2025, 4.1.4.2.2).")

#: Der Anteil in die kürzere Spannweite fern der Lager (:func:`~opencivil.decke.aufteilung.in_der_mitte`).
MITTE = (r"\alpha_{\mathrm{kurz}} = \min\left(1;\ \frac{1}{2} + \frac{1}{2} \cdot "
         r"\frac{l_{\mathrm{lang}} / l_{\mathrm{kurz}} - 1}{" + fest(GANZ_AB, 1) + r" - 1}\right)")


#: Vom Streifen zur Platte -- die Transformation der Folie 14, rückwärts gelesen (:mod:`~opencivil.decke.feld`).
STREIFEN_IN_XY = (
    r"\begin{aligned} & m = \frac{M}{b} \qquad m_x = m \cdot \cos^2\varphi \qquad "
    r"m_y = m \cdot \sin^2\varphi \qquad m_{xy} = m \cdot \sin\varphi \cdot \cos\varphi \\ "
    r"& v = \frac{V}{b} \qquad v_x = v \cdot \cos\varphi \qquad v_y = v \cdot \sin\varphi "
    r"\qquad v_0 = \sqrt{v_x^2 + v_y^2} \end{aligned}")

#: Ein Flächenlager drückt gleichmässig über seine Breite (Folie 33).
FLAECHENLAGER = r"p_{\mathrm{Lager}} = \frac{R}{l}"

#: Die linearisierte Fliessbedingung, ``k = k' = 1`` (:func:`~opencivil.decke.feld.widerstaende`).
FLIESSBEDINGUNG = (
    r"\begin{aligned} & m_{xu} \ge m_x + |m_{xy}| \qquad m_{yu} \ge m_y + |m_{xy}| \\ "
    r"& m'_{xu} \ge -m_x + |m_{xy}| \qquad m'_{yu} \ge -m_y + |m_{xy}| \end{aligned}")

#: Trägt eine Platte schief zu x und y -- nach den Platten, die es tun.
SCHIEF = (
    "{platten} schief zu x und y: ihre Streifen geben Drillmomente m_xy, bei 45° halb so gross wie "
    "das Moment des Streifens. Die linearisierte Fliessbedingung gilt nur näherungsweise und nur, "
    "solange die Drillmomente mässig bleiben (SIA 262:2025, 4.3.2.6); wo die Hauptmomente deutlich "
    "schräg zur Bewehrung in x und y stehen, gehört das eigens in die Bemessung (4.3.2.5).")

#: Was ein Lastverteilelement zusätzlich braucht (:class:`~opencivil.decke.feld.Lastverteilelement`).
LASTVERTEILELEMENT = (
    r"\begin{aligned} & m'_{xu} \ge \frac{Q}{8} \cdot \frac{l_x}{l_y} \qquad "
    r"m_{xu} \ge \left(\frac{1}{2\pi} - \frac{1}{8}\right) \cdot Q \cdot \frac{l_x}{l_y} \\ "
    r"& m'_{yu} \ge \frac{Q}{8} \cdot \frac{l_y}{l_x} \qquad "
    r"m_{yu} \ge \left(\frac{1}{2\pi} - \frac{1}{8}\right) \cdot Q \cdot \frac{l_y}{l_x} \end{aligned}")

#: Die Schnittkräfte der Platte im Bericht: je Grösse ihr Zeichen und ihre Einheit.
SCHNITTKRAEFTE = (("m_x", "m_x", "kNm/m"), ("m_y", "m_y", "kNm/m"), ("m_xy", "m_{xy}", "kNm/m"),
                  ("v_x", "v_x", "kN/m"), ("v_y", "v_y", "kN/m"), ("v_0", "v_0", "kN/m"))

#: Die Biegewiderstände: Feld von :class:`~opencivil.decke.feld.Widerstaende`, Zeichen, Bedeutung.
WIDERSTAENDE = (("mxu", "m_{xu}", "unten, in x"), ("myu", "m_{yu}", "unten, in y"),
                ("mxu_oben", "m'_{xu}", "oben, in x"), ("myu_oben", "m'_{yu}", "oben, in y"))


def schreiben(p: Protokoll, system: "Deckensystem", befund: "Deckenbefund") -> None:
    """Die ganze Herleitung einer Decke -- nichts davon geht in den Befund ein, also still gar keine."""
    if p.still:
        return
    p.annahme(ANNAHME)
    _platten(p, system, befund.gerechnet)
    _lager(p, befund.gerechnet, befund.ergebnis)
    _lasten(p, befund.gerechnet)
    for m in befund.meldungen:
        (p.warnung if m.fehler else p.hinweis)(m.text)
    e = befund.ergebnis
    if e is None or e.aufteilungen is None:
        return
    _streifen(p, e)
    _aufteilung(p, befund.gerechnet)
    _faelle(p, e)
    if not e.faelle:
        return
    _ansaetze(p, e)
    zellen = feld.zellen_von(e)
    for f in e.faelle:
        _fall(p, e, f, zellen)


def _ort(punkt: geo.Punkt) -> str:
    return f"({fest(punkt[0], 2)}, {fest(punkt[1], 2)})"


def _platten(p: Protokoll, system: "Deckensystem", decke: Decke) -> None:
    zeilen = []
    for platte in decke.platten:
        beton = system.betone.get(platte.name)
        r1, r2 = (math.degrees(w) for w in platte.richtungen)
        zeilen.append([
            platte.name, Mathe(fest(abs(geo.flaeche(list(platte.ecken))), 2)),
            Mathe(fest(platte.h * 1e3, 0)), beton.name if beton is not None else "–",
            Mathe(fest(platte.E / 1e6, 0)) if platte.E else "–",
            Mathe(fest(platte.wichte * platte.h / 1e3, 2)) if platte.wichte else "–",
            Mathe(f"{fest(r1, 1)},\\ {fest(r2, 1)}"),
        ])
    if zeilen:
        p.tabelle(["Platte", Mathe(r"A\ [\mathrm{m}^{2}]"), Mathe(r"h\ [\mathrm{mm}]"), "Beton",
                   Mathe(r"E_{cm}\ [\mathrm{N/mm}^{2}]"), Mathe(r"g_k\ [\mathrm{kN/m}^{2}]"),
                   Mathe(r"\varphi_1,\ \varphi_2\ [°]")], zeilen, titel="Platten")
        p.text("Das Eigengewicht je m² ist ρ · g · h, mit der Dichte des Stahlbetons und "
               "g = 10 m/s².")


def _lager(p: Protokoll, decke: Decke, e: Optional[Ergebnis]) -> None:
    ja = {True: "ja", False: "nein"}
    if decke.linienlager:
        p.tabelle(["Linienlager", "von", "bis", Mathe(r"L\ [\mathrm{m}]"), "vertikal", "eingespannt"],
                  [[l.name, _ort(l.a), _ort(l.b), Mathe(fest(math.dist(l.a, l.b), 2)),
                    ja[l.vertikal], ja[l.eingespannt]] for l in decke.linienlager],
                  titel="Linienlager")
    if decke.stuetzen:
        bereiche = e.zerlegung.stuetzenbereiche if e is not None and e.zerlegung else {}
        zeilen = []
        for s in decke.stuetzen:
            bereich = bereiche.get(s.name)
            if bereich:
                lx = geo.bereich(bereich, (1.0, 0.0))
                ly = geo.bereich(bereich, (0.0, 1.0))
                masse = f"{fest(lx[1] - lx[0], 2)} × {fest(ly[1] - ly[0], 2)}"
            else:
                masse = "–"
            zeilen.append([s.name, _ort(s.ort), f"{fest(s.bx * 1e3, 0)} × {fest(s.by * 1e3, 0)}",
                           masse, "von Hand" if s.lx is not None else "von selbst"])
        p.tabelle(["Stütze", "Ort", Mathe(r"b_x \times b_y\ [\mathrm{mm}]"),
                   Mathe(r"l_x \times l_y\ [\mathrm{m}]"), "Stützenbereich"], zeilen, titel="Stützen")
    if decke.unterzuege:
        p.tabelle(["Unterzug", "von", "bis", Mathe(r"b\ [\mathrm{m}]"), "Stufe"],
                  [[u.name, _ort(u.a), _ort(u.b), Mathe(fest(u.breite, 2)), str(u.stufe)]
                   for u in decke.unterzuege], titel="Versteckte Unterzüge")


def _lasten(p: Protokoll, decke: Decke) -> None:
    """Die Lasten je Lastfall, wie sie beschrieben sind, und die Beiwerte der Kombinationen."""
    zeilen = []
    for lf in decke.lastfaelle:
        if lf.eigengewicht:
            zeilen.append([lf.name, "Eigengewicht", "jede Platte", Mathe(r"\rho \cdot g \cdot h")])
        zeilen.extend([lf.name, *_last(last)] for last in lf.lasten)
    if zeilen:
        p.tabelle(["Lastfall", "Last", "wo", "Wert"], zeilen, titel="Lasten, nach unten positiv")
    leer = [f"«{lf.name}»" for lf in decke.lastfaelle if not (lf.lasten or lf.eigengewicht)]
    if leer:
        p.text(f"Ohne Last: {', '.join(leer)}.")
    for k in decke.kombinationen:
        p.text(f"Kombination «{k.name}»: "
               + (" + ".join(f"{beiwert:g} · «{lf}»" for lf, beiwert in k.faktoren.items())
                  or "keine Beiwerte – sie ist leer."))


def _last(last: Last) -> list:
    """Name, Ort und Wert einer Last für die Tabelle."""
    if isinstance(last, Flaechenlast):
        wo = ("die ganze Platte" if last.platte
              else f"A = {fest(abs(geo.flaeche(list(last.ecken))), 2)} m²")
        return [last.name, wo, Mathe(f"{fest(last.wert / 1e3, 2)}" + r"\ \mathrm{kN/m^{2}}")]
    if isinstance(last, Linienlast):
        return [last.name, f"{_ort(last.a)} – {_ort(last.b)}",
                Mathe(f"{fest(last.wert / 1e3, 2)}" + r"\ \mathrm{kN/m}")]
    return [last.name, f"{_ort(last.ort)}, verteilt über {fest(last.lx, 2)} × {fest(last.ly, 2)} m",
            Mathe(f"{fest(last.wert / 1e3, 1)}" + r"\ \mathrm{kN}")]


def _streifen(p: Protokoll, e: Ergebnis) -> None:
    z = e.zerlegung
    zeilen = []
    for r in z.richtungen:
        feld = z.feldstreifen(r)
        if not feld:
            continue
        breiten = [s.breite for s in feld]
        zeilen.append([r.name, Mathe(fest(math.degrees(r.winkel), 1)), str(len(feld)),
                       Mathe(f"{fest(min(breiten), 3)} \\ldots {fest(max(breiten), 3)}"),
                       f"{feld[0].name} … {feld[-1].name}"])
    p.tabelle(["Richtung", Mathe(r"\varphi\ [°]"), "Feldstreifen", Mathe(r"b\ [\mathrm{m}]"), "Namen"],
              zeilen, titel="Streifen")
    p.text(f"Je Richtung sind die Streifen höchstens {fest(e.decke.streifenbreite, 2)} m breit; "
           "geteilt wird an jeder Ecke einer Platte, jedem Rand eines Unterzugs und Stützenbereichs "
           "und jedem Ende eines Linienlagers.")
    if z.unterzuege:
        reihe = [f"{u.name} (Stufe {u.stufe})" for u in sorted(z.unterzuege, key=lambda s: s.stufe)]
        p.text("Gerechnet wird von unten nach oben: zuerst die Feldstreifen, dann die Unterzüge, "
               "jeder nach denen tieferer Stufe: " + ", ".join(reihe) + ". Was ein Träger an "
               "Lagerkraft abgibt, ist die Last dessen, auf dem er liegt.")


def _aufteilung(p: Protokoll, decke: Decke) -> None:
    if decke.aufteilung is Aufteilung.FEST:
        p.text(f"Aufteilung fest: {fest(decke.anteil * 100.0, 0)} % der Last in Richtung 1, "
               f"{fest((1.0 - decke.anteil) * 100.0, 0)} % in Richtung 2.")
    else:
        p.text(AUTOMATISCH)
        p.gleichung(MITTE, titel="Fern der Lager, in die kürzere Spannweite")
    if decke.zonen:
        p.tabelle(["Zone", Mathe(r"A\ [\mathrm{m}^{2}]"), "in Richtung 1", "in Richtung 2"],
                  [[zone.name, Mathe(fest(abs(geo.flaeche(list(zone.ecken))), 2)),
                    f"{fest(zone.anteil * 100.0, 0)} %", f"{fest((1.0 - zone.anteil) * 100.0, 0)} %"]
                   for zone in decke.zonen], titel="Zonen – sie gehen der Aufteilung vor")
    richtungen = {richtungen_der_platte(pl)[0].name + " / " + richtungen_der_platte(pl)[1].name
                  for pl in decke.platten}
    if len(richtungen) > 1:
        p.text("Die Platten tragen in verschiedenen Richtungen: "
               + "; ".join(sorted(richtungen)) + ". Die Aufteilung gilt je Platte in ihren zwei Richtungen.")


def _faelle(p: Protokoll, e: Ergebnis) -> None:
    """Je Lastfall und Kombination die Last und was die Lager tragen -- die Probe --, und die Meldungen der Fälle."""
    if not e.faelle:
        return
    p.tabelle(["Fall", Mathe(r"Q\ [\mathrm{kN}]"), Mathe(r"Q_{\mathrm{daneben}}\ [\mathrm{kN}]"),
               Mathe(r"Q_{\mathrm{nicht\ getragen}}\ [\mathrm{kN}]"), Mathe(r"\sum R\ [\mathrm{kN}]")],
              [[f.name, *(Mathe(fest(w / 1e3, 1)) for w in (f.summe, f.daneben, f.nicht_getragen, f.lagerkraft))]
               for f in e.faelle], titel="Last und Lagerkräfte je Fall")
    p.text("Die Lager tragen die ganze Last ausser dem, was neben den Platten liegt oder auf einem "
           "Streifen, der nicht trägt.")
    for m in e.fallmeldungen():
        (p.warnung if m.fehler else p.hinweis)(m.text)


# ===========================================================================
# Ansätze und je Fall
# ===========================================================================


def _ansaetze(p: Protokoll, e: Ergebnis) -> None:
    """Wie aus den Trägern die Platte wird -- je einmal, was die Decke braucht."""
    decke = e.decke
    p.ansatz(STREIFEN_IN_XY, titel="Vom Streifen zur Platte: je Meter, in den Achsen x und y",
             referenz="Stahlbeton II, 7.2 Platten, Folie 14", name="Schnittkräfte eines Streifens in x und y")
    p.text("Ein Streifen der Breite b in der Richtung φ gegen x trägt mit M und V; je Meter sind das "
           "m und v. An einer Stelle zählen alle Streifen über ihr: je Richtung ein Feldstreifen und "
           "jeder Unterzug, in dessen Fläche sie liegt.")
    if decke.unterzuege or decke.stuetzen:
        p.ansatz(FLAECHENLAGER, titel="Ein Flächenlager drückt gleichmässig über seine Breite l",
                 referenz="Stahlbeton II, 7.2 Platten, Folie 33", name="Pressung eines Flächenlagers")
        p.text("Ein Unterzug oder Stützenbereich trägt einen Streifen nicht in einem Punkt: seine "
               "Lagerkraft R drückt gleichmässig über die Breite l, die beide teilen. Beim Unterzug "
               "wird diese Pressung zu seiner Last.")
    p.ansatz(FLIESSBEDINGUNG, titel="Erforderliche Biegewiderstände, linearisierte Fliessbedingung",
             referenz="SIA 262:2025, 4.3.2.6, (34)", name="Linearisierte Fliessbedingung")
    schief = [f"«{pl.name}»" for pl in decke.platten if any(r.schief for r in richtungen_der_platte(pl))]
    if schief:
        p.hinweis(SCHIEF.format(platten=(f"Die Platte {schief[0]} trägt" if len(schief) == 1
                                         else f"Die Platten {', '.join(schief)} tragen")))
    if decke.stuetzen or any(isinstance(l, Punktlast) for lf in decke.lastfaelle for l in lf.lasten):
        p.ansatz(LASTVERTEILELEMENT, titel="Was ein Lastverteilelement l_x × l_y zusätzlich braucht",
                 referenz="Stahlbeton II, 7.2 Platten, Folie 38", name="Lastverteilelement")
        p.text("Über einer Stütze nehmen die Streifen die Stützenkraft Q als gleichmässige Pressung "
               "im Stützenbereich ab; damit sie als Punkt hineinpasst, braucht der Bereich die "
               "Widerstände oben. Unter einer Einzellast Q tauschen oben und unten.")


def _fall(p: Protokoll, e: Ergebnis, f: Fallergebnis, zellen: Sequence[Sequence[geo.Punkt]]) -> None:
    """Ein Lastfall oder eine Kombination: Träger, Lager, Platte, Biegewiderstände, Lastverteilelemente."""
    kombination = any(k.name == f.name for k in e.decke.kombinationen)
    p.titel(f"{'Kombination' if kombination else 'Lastfall'} «{f.name}»", ebene=3)
    if not f.traeger:
        p.text("Nichts trägt in diesem Fall.")
        return
    _traeger(p, e, f)
    _lagerkraefte(p, e, f)
    proben = feld.proben(e, f, zellen)
    if proben:
        _schnittkraefte(p, proben)
        _widerstaende(p, proben)
    _lastverteilelemente(p, e, f)


def _traeger(p: Protokoll, e: Ergebnis, f: Fallergebnis) -> None:
    """Jeder Träger, je Meter seiner Breite -- gleiche Feldstreifen nebeneinander in einer Zeile."""
    zeilen: List[Tuple[List[str], Tuple[str, ...], Optional[Tuple[str, int]]]] = []
    for streifen, stueck, t in _reihe(e.zerlegung):
        r = f.traeger.get(t.name)
        if r is None:
            # Ein Träger ohne Last steht nicht da -- und trennt seine Nachbarn.
            if zeilen:
                zeilen[-1] = (*zeilen[-1][:2], None)
            continue
        b = streifen.breite
        m = extremwerte(r.stuecke, lambda t: t.M)
        (s_klein, m_klein), (s_gross, m_gross) = m.kleinst, m.groesst
        lager = " · ".join(f"{k.auflager.name} {fest(k.F / b / 1e3, 1)}" for k in r.lagerkraefte)
        werte = (fest(b, 3), fest(t.L, 2), fest(r.last / b / 1e3, 1), lager,
                 *_mit_stelle(m_klein / b, t.s0 + s_klein), *_mit_stelle(m_gross / b, t.s0 + s_gross))
        # Zusammen nur gleich gezählte Stücke von Feldstreifen derselben Richtung; ein Unterzug steht für sich.
        gruppe = (streifen.richtung.name, stueck) if streifen.stufe == 0 else None
        if zeilen and gruppe is not None and zeilen[-1][1:] == (werte, gruppe):
            zeilen[-1][0].append(t.name)
        else:
            zeilen.append(([t.name], werte, gruppe))
    p.tabelle(["Träger", Mathe(r"b\ [\mathrm{m}]"), Mathe(r"L\ [\mathrm{m}]"),
               Mathe(r"Q/b\ [\mathrm{kN/m}]"), "Lager [kN/m]", Mathe(r"m_{\min}\ [\mathrm{kNm/m}]"),
               Mathe(r"s\ [\mathrm{m}]"), Mathe(r"m_{\max}\ [\mathrm{kNm/m}]"), Mathe(r"s\ [\mathrm{m}]")],
              [[namen[0] if len(namen) == 1 else f"{namen[0]} … {namen[-1]}", *map(_zahl, werte[:3]),
                werte[3], *map(_zahl, werte[4:])] for namen, werte, _ in zeilen],
              titel="Träger, je Meter ihrer Breite")
    p.text("Q ist die Last auf dem Träger, mit dem, was tiefere Träger in ihn geben. s misst längs der "
           "Richtung φ des Trägers, s = x · cos φ + y · sin φ: in x ist s = x, in y ist s = y. "
           "Nebeneinander liegende Träger, die dasselbe tragen, stehen in einer Zeile.")


def _reihe(z: Zerlegung) -> List[Tuple[Streifen, int, Traeger]]:
    """
    Die Träger in der Reihe der Zerlegung, je mit der Nummer ihres Stücks
    im Streifen -- nur je Richtung der Feldstreifen erst alle ersten Stücke,
    dann alle zweiten: so steht x1.2 neben x2.2 statt hinter x1.1.
    """
    reihe: List[Tuple[Streifen, int, Traeger]] = []
    for r in z.richtungen:
        feldstreifen = z.feldstreifen(r)
        for stueck in range(max((len(s.traeger) for s in feldstreifen), default=0)):
            reihe += [(s, stueck, s.traeger[stueck]) for s in feldstreifen if stueck < len(s.traeger)]
    return reihe + [(u, stueck, t) for u in z.unterzuege for stueck, t in enumerate(u.traeger)]


def _mit_stelle(m: float, s: float) -> Tuple[str, str]:
    """Ein Moment in kNm/m und wo es liegt -- ausser es steht als null da."""
    wert = fest(m / 1e3, 1)
    return wert, fest(s, 2) if wert != "0.0" else "–"


def _zahl(text: str):
    """Eine Zahl als Formel, damit ihr Minus eines ist; der Strich bleibt Text."""
    return text if text == "–" else Mathe(text)


def _lagerkraefte(p: Protokoll, e: Ergebnis, f: Fallergebnis) -> None:
    """Was jedes Lager trägt; längs eines Linienlagers die Spitze und, eingespannt, die des Moments."""
    eingespannt = any(l.eingespannt for l in e.decke.linienlager)
    zeilen = []
    for s in e.decke.stuetzen:
        zeilen.append([f"{s.name} · Stütze", Mathe(fest(f.stuetzenkraft(s.name) / 1e3, 1)), "–"]
                      + (["–"] if eingespannt else []))
    for l in e.decke.linienlager:
        r_max, m_max = spitzen(lagerverlauf(l, f.linienlager.get(l.name, ())))
        zeilen.append([f"{l.name} · Linienlager", Mathe(fest(f.wandkraft(l.name) / 1e3, 1)),
                       Mathe(fest(r_max / 1e3, 1))]
                      + ([Mathe(fest(m_max / 1e3, 1)) if l.eingespannt else "–"] if eingespannt else []))
    if not zeilen:
        return
    p.tabelle(["Lager", Mathe(r"F\ [\mathrm{kN}]"), Mathe(r"r_{\max}\ [\mathrm{kN/m}]")]
              + ([Mathe(r"m_{\max}\ [\mathrm{kNm/m}]")] if eingespannt else []),
              zeilen, titel="Lagerkräfte")
    p.text("Längs eines Linienlagers gibt jeder Träger seine Kraft gleichmässig über das Stück ab, über "
           "das er geht; wo zwei dasselbe Stück tragen, zählen beide. r_max ist der Wert mit dem grössten "
           "Betrag."
           + (" Ebenso m_max, das Moment, das ein eingespanntes Lager hält, mit dem Vorzeichen der Platte: "
              "negativ, wo es oben zieht. Liegt Platte zu beiden Seiten, hält es nur den Unterschied "
              "ihrer Momente; dann gilt das Vorzeichen der Seite, die stärker zieht." if eingespannt else ""))


def _schnittkraefte(p: Protokoll, proben: Sequence[feld.Probe]) -> None:
    """Die grössten und kleinsten Schnittkräfte der Platte, mit Ort."""
    zeilen = []
    for groesse, zeichen, einheit in SCHNITTKRAEFTE:
        (ort_klein, klein), (ort_gross, gross) = feld.extrem(proben, lambda k, g=groesse: k.groesse(g))
        zeilen.append([Mathe(zeichen), Mathe(f"{fest(klein / 1e3, 1)}\\ \\mathrm{{{einheit}}}"),
                       _ort_von(ort_klein, klein), Mathe(f"{fest(gross / 1e3, 1)}\\ \\mathrm{{{einheit}}}"),
                       _ort_von(ort_gross, gross)])
    p.tabelle(["Grösse", "kleinst", "Ort", "grösst", "Ort"], zeilen, titel="Schnittkräfte der Platte, je Meter")
    p.text("Gesucht am Schwerpunkt jeder Zelle der Bilder und an den Stellen, an denen ein Träger "
           "springt oder Querkraft oder Last null werden. Momente positiv mit Zug unten.")


def _widerstaende(p: Protokoll, proben: Sequence[feld.Probe]) -> None:
    """Die grössten erforderlichen Biegewiderstände, mit Ort."""
    zeilen = []
    for feldname, zeichen, wo in WIDERSTAENDE:
        _, (ort, wert) = feld.extrem(proben, lambda k, n=feldname: getattr(feld.widerstaende(k), n))
        zeilen.append([Mathe(zeichen), wo, Mathe(fest(wert / 1e3, 1) + r"\ \mathrm{kNm/m}"), _ort_von(ort, wert)])
    p.tabelle(["Widerstand", "Seite", "erforderlich", "Ort"], zeilen,
              titel="Erforderliche Biegewiderstände, ohne Lastverteilelemente")


def _ort_von(ort: geo.Punkt, wert: float) -> str:
    """Wo ein Wert liegt -- ausser er steht als null da: das ist er an vielen Orten."""
    return _ort(ort) if fest(wert / 1e3, 1) != "0.0" else "–"


def _lastverteilelemente(p: Protokoll, e: Ergebnis, f: Fallergebnis) -> None:
    """Je Stütze und Einzellast, was ihr Bereich zusätzlich braucht."""
    elemente = feld.lastverteilelemente(e, f)
    if not elemente:
        return
    zeilen = []
    for l in elemente:
        (oben_x, unten_x), (oben_y, unten_y) = l.zusatz()
        zeilen.append([f"{l.name} · {'Stütze' if l.art == 'stuetze' else 'Einzellast'}",
                       Mathe(fest(l.Q / 1e3, 1)), Mathe(f"{fest(l.lx, 2)} \\times {fest(l.ly, 2)}"),
                       *(Mathe(fest(w / 1e3, 1)) for w in (-oben_x, unten_x, -oben_y, unten_y))])
    p.tabelle(["Element", Mathe(r"Q\ [\mathrm{kN}]"), Mathe(r"l_x \times l_y\ [\mathrm{m}]"),
               *(Mathe(f"{m}\\ [\\mathrm{{kNm/m}}]") for m in ("m'_{xu}", "m_{xu}", "m'_{yu}", "m_{yu}"))],
              zeilen, titel="Lastverteilelemente: was der Bereich zusätzlich braucht")
