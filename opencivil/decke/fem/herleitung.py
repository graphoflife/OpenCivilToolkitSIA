"""
opencivil/decke/fem/herleitung.py -- wie die FEM einer Decke ihre Rechnung aufschreibt.

VERANTWORTUNG:
Die Herleitung der FEM, so dass man sieht, was gerechnet ist: die Decke in
Tabellen -- Platten mit ihrer Steifigkeit, Linienlager, Stützen, Träger
mit ihrer Biegesteifigkeit, Lasten je Lastfall und die Kombinationen --,
das Netz, je Fall die Last und was die Lager davon tragen, und die
Meldungen. Dann die Ansätze -- die Momente der Platte nach Kirchhoff, die
Querkräfte aus ihnen, der Träger in der Platte, die Fliessbedingung -- und
je Lastfall und Kombination: was jedes Lager trägt, die grössten
Schnittkräfte und die grösste Durchbiegung, die Biegewiderstände, die die
Platte verlangt, und Moment und Querkraft jedes Trägers.

Die Tabellen, die beide Verfahren gleich haben, schreibt
:mod:`opencivil.decke.herleitung`. Die grössten Werte kommen von den
Knoten (:func:`~opencivil.decke.fem.auswertung.proben`), wie im Bild.

EINHEITEN:
wie in der Streifenmethode; dazu ``D`` in MNm, ``EI`` in MNm² und die
Durchbiegung in mm.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from opencivil.core.latex import Mathe, fest
from opencivil.core.protokoll import Protokoll
from opencivil.decke import geometrie as geo
from opencivil.decke.fem import auswertung
from opencivil.decke.fem.element import steifigkeit_der_platte
from opencivil.decke.fem.rechnung import Femergebnis, Femfall
from opencivil.decke.herleitung import (
    FLIESSBEDINGUNG, SCHNITTKRAEFTE, als_ort, faelle, lagerkraefte, lasten, linienlager, schnittkraefte,
    widerstaende, zahl,
)
from opencivil.decke.modell import Decke

if TYPE_CHECKING:
    from opencivil.decke.werk import Deckenbefund, Deckensystem

#: Was die FEM annimmt.
ANNAHME = (
    "FEM: die ganze Platte linear elastisch und ungerissen, mit E_cm und ν_c ihres Betons "
    "(SIA 262:2025, 4.1.4.1.1 und 4.1.4.1.3; ν_c nach 3.1.2.3.5), als dünne Platte nach Kirchhoff "
    "aus Dreiecken DKT (Batoz, Bathe und Ho 1980). Die Lager halten, wie sie gezeichnet sind: ein "
    "Linienlager die Höhe und, eingespannt, die Drehung quer zu ihm; eine Stütze nur ihren Punkt. "
    "Ein Träger mit Höhe ist ein Balken in der Mittelebene der Platte, ohne Torsionssteifigkeit; "
    "ohne Höhe trägt an seiner Stelle nur die Platte. Umgelagert wird nichts.")

#: Die Momente der Platte aus ihrer Krümmung (:mod:`~opencivil.decke.fem.element`).
PLATTE = (
    r"\begin{aligned} & D = \frac{E_{cm} \cdot h^3}{12 \cdot (1 - \nu_c^2)} \\ "
    r"& m_x = -D \cdot \left(\frac{\partial^2 w}{\partial x^2} + \nu_c \cdot \frac{\partial^2 w}{\partial y^2}\right)"
    r" \qquad m_y = -D \cdot \left(\frac{\partial^2 w}{\partial y^2} + \nu_c \cdot "
    r"\frac{\partial^2 w}{\partial x^2}\right) \\ "
    r"& m_{xy} = -D \cdot (1 - \nu_c) \cdot \frac{\partial^2 w}{\partial x \, \partial y} \end{aligned}")

#: Die Querkräfte aus dem Gefälle der Momente (:mod:`~opencivil.decke.fem.rechnung`).
QUERKRAEFTE = (
    r"v_x = \frac{\partial m_x}{\partial x} + \frac{\partial m_{xy}}{\partial y} \qquad "
    r"v_y = \frac{\partial m_{xy}}{\partial x} + \frac{\partial m_y}{\partial y} \qquad "
    r"v_0 = \sqrt{v_x^2 + v_y^2}")

#: Ein Träger in der Platte (:mod:`~opencivil.decke.fem.system`, :mod:`~opencivil.decke.fem.auswertung`).
TRAEGER = (
    r"\begin{aligned} & EI = E_{cm} \cdot b \cdot \frac{(h + h_T)^3 - h^3}{12} \\ "
    r"& M = M_{\mathrm{Balken}} + b \cdot \bar{m}_t \qquad V = V_{\mathrm{Balken}} + b \cdot \bar{v}_t "
    r"\end{aligned}")

#: Wie die Kraft längs eines Linienlagers verteilt ist, in der FEM (:mod:`~opencivil.decke.fem.rechnung`).
LAENGS = (
    "Längs eines Linienlagers gehört zu jedem Knoten das Stück bis zur Mitte der Kanten daneben; was er "
    "trägt, verteilt sich gleichmässig darüber, ausgeglichen mit seinen Nachbarn mitten im Lager. An den "
    "Enden, an einer Ecke und wo ein anderes Lager anstösst, greift die Kraft im Punkt an.")

#: Wo die grössten Werte gesucht sind.
WO = ("Gesucht an jedem Knoten des Netzes: über ein Dreieck ist jede Grösse linear, das Grösste liegt "
      "also an einer Ecke.")

#: Die Grössen der Platte im Bericht, mit der Durchbiegung.
GROESSEN = (*SCHNITTKRAEFTE, ("w", "w", "mm", 1e3))


def schreiben(p: Protokoll, system: "Deckensystem", befund: "Deckenbefund") -> None:
    """Die ganze Herleitung einer Decke nach der FEM -- nichts davon geht in den Befund ein, also still gar keine."""
    if p.still:
        return
    decke = befund.gerechnet
    p.annahme(ANNAHME)
    _platten(p, system, decke)
    linienlager(p, decke)
    _lager(p, decke, befund.ergebnis)
    lasten(p, decke)
    for m in befund.meldungen:
        (p.warnung if m.fehler else p.hinweis)(m.text)
    e = befund.ergebnis
    if e is None or e.netz is None:
        return
    p.text(f"Das Netz hat {len(e.netz.knoten)} Knoten und {len(e.netz.dreiecke)} Dreiecke, ihre Seiten "
           f"höchstens {fest(decke.netzweite, 2)} m lang. Es folgt den Rändern der Platten, den "
           "Linienlagern, den Trägern und den Linienlasten; jede Stütze ist einer seiner Knoten.")
    faelle(p, e, ausser="auf einem Teil, der sich frei bewegen könnte")
    if not e.faelle:
        return
    _ansaetze(p, e)
    for f in e.faelle:
        _fall(p, e, f)


def _platten(p: Protokoll, system: "Deckensystem", decke: Decke) -> None:
    zeilen = []
    for platte in decke.platten:
        beton = system.betone.get(platte.name)
        zeilen.append([
            platte.name, Mathe(fest(abs(geo.flaeche(list(platte.ecken))), 2)),
            Mathe(fest(platte.h * 1e3, 0)), beton.name if beton is not None else "–",
            Mathe(fest(platte.E / 1e6, 0)) if platte.E else "–", Mathe(fest(platte.nu, 2)),
            Mathe(fest(steifigkeit_der_platte(platte.E, platte.h, platte.nu) / 1e6, 1)) if platte.E else "–",
            Mathe(fest(platte.wichte * platte.h / 1e3, 2)) if platte.wichte else "–",
        ])
    if zeilen:
        p.tabelle(["Platte", Mathe(r"A\ [\mathrm{m}^{2}]"), Mathe(r"h\ [\mathrm{mm}]"), "Beton",
                   Mathe(r"E_{cm}\ [\mathrm{N/mm}^{2}]"), Mathe(r"\nu_c"), Mathe(r"D\ [\mathrm{MNm}]"),
                   Mathe(r"g_k\ [\mathrm{kN/m}^{2}]")], zeilen, titel="Platten")
        p.text("Das Eigengewicht je m² ist ρ · g · h, mit der Dichte des Stahlbetons und g = 10 m/s².")


def _lager(p: Protokoll, decke: Decke, e: Optional[Femergebnis]) -> None:
    """Stützen als Punkte, Träger mit der Biegesteifigkeit ihres Balkens -- wie das System sie rechnet."""
    if decke.stuetzen:
        p.tabelle(["Stütze", "Ort", Mathe(r"b_x \times b_y\ [\mathrm{mm}]")],
                  [[s.name, als_ort(s.ort), f"{fest(s.bx * 1e3, 0)} × {fest(s.by * 1e3, 0)}"]
                   for s in decke.stuetzen], titel="Stützen")
        p.text("Eine Stütze hält die Platte in ihrer Mitte, als Punkt; ihr Querschnitt zählt dabei nicht.")
    eigene = [u for u in decke.traeger if not u.von_selbst]
    if eigene:
        zeilen = []
        for u in eigene:
            EI = sorted({fest(b.EI / 1e6, 1) for b in (e.system.balken if e and e.system else ())
                         if b.traeger == u.name})
            steif = ("in der Platte" if u.hoehe <= 0.0 else "–" if not EI
                     else Mathe(EI[0] if len(EI) == 1 else f"{EI[0]} \\ldots {EI[-1]}"))
            zeilen.append([u.name, als_ort(u.a), als_ort(u.b), Mathe(fest(u.breite, 2)),
                           Mathe(fest(u.hoehe * 1e3, 0)), steif])
        p.tabelle(["Träger", "von", "bis", Mathe(r"b\ [\mathrm{m}]"), Mathe(r"h_T\ [\mathrm{mm}]"),
                   Mathe(r"EI\ [\mathrm{MNm}^{2}]")], zeilen, titel="Träger")


def _ansaetze(p: Protokoll, e: Femergebnis) -> None:
    """Die Platte, ihre Querkräfte, die Träger und die Fliessbedingung -- je einmal, was die Decke braucht."""
    decke = e.decke
    p.ansatz(PLATTE, titel="Die Momente der Platte aus ihrer Krümmung, nach Kirchhoff",
             name="Momente der Platte nach Kirchhoff")
    p.text("w ist die Durchbiegung, nach unten positiv; m_x > 0 zieht unten. Im Dreieck DKT ändern sich "
           "die Neigungen von w quadratisch, die Krümmungen und Momente also linear. An jedem Knoten gilt "
           "das Mittel der Dreiecke um ihn, nach ihrer Fläche – ausser über ein Lager, einen Träger, eine "
           "Linienlast oder die Fuge zweier verschieden steifer Platten hinweg: dort behält jede Seite "
           "ihren Wert (nach Vorgabe, nicht nachgeschlagen).")
    p.ansatz(QUERKRAEFTE, titel="Die Querkräfte aus dem Gefälle der Momente",
             name="Querkräfte aus den Momenten der Platte")
    p.text("Das Gefälle der gemittelten Momente je Dreieck gibt die Querkräfte, an den Knoten ebenso "
           "gemittelt. An einem Rand, einem Lager und einer Stütze sind sie mit einem groben Netz "
           "ungenauer als im Feld.")
    if decke.traeger:
        p.ansatz(TRAEGER, titel="Ein Träger: Balken in der Mittelebene und Platte über seine Breite b",
                 name="Träger in der Platte")
        p.text("Der Balken ist so steif wie das Rechteck b × (h + h_T) ohne den Teil, den die Platte schon "
               "trägt. M und V des Trägers sind die des Balkens und die der Platte über seine Breite: "
               "b mal das Mittel von m_t und v_t quer zu ihm, in seiner Richtung (nach Vorgabe, nicht "
               "nachgeschlagen).")
    p.ansatz(FLIESSBEDINGUNG, titel="Erforderliche Biegewiderstände, linearisierte Fliessbedingung",
             referenz="SIA 262:2025, 4.3.2.6, (34)", name="Linearisierte Fliessbedingung")
    if decke.stuetzen:
        p.hinweis("Eine Stütze hält als Punkt: über ihr wachsen die Momente mit feinerem Netz ohne Grenze, "
                  "und ihre Werte dort hängen von der Netzweite ab.")


def _fall(p: Protokoll, e: Femergebnis, f: Femfall) -> None:
    """Ein Lastfall oder eine Kombination: Lager, Platte, Biegewiderstände, Träger."""
    kombination = any(k.name == f.name for k in e.decke.kombinationen)
    p.titel(f"{'Kombination' if kombination else 'Lastfall'} «{f.name}»", ebene=3)
    if not f.summe:
        p.text("Ohne Last.")
        return
    lagerkraefte(p, e, f, LAENGS)
    proben = auswertung.proben(e, f)
    if proben:
        schnittkraefte(p, proben, GROESSEN, WO)
        widerstaende(p, proben, titel="Erforderliche Biegewiderstände")
    _traeger(p, e, f)


def _traeger(p: Protokoll, e: Femergebnis, f: Femfall) -> None:
    """Je Träger das kleinste und das grösste Moment und die grösste Querkraft, über seine ganze Breite."""
    zeilen: List[list] = []
    for u in e.decke.traeger:
        v = auswertung.traeger(e, f, u)
        if not v.proben:
            continue
        (u_klein, m_klein), (u_gross, m_gross) = v.extreme("M")
        (u_vk, v_klein), (u_vg, v_gross) = v.extreme("V")
        u_v, v_max = (u_vg, v_gross) if abs(v_gross) >= abs(v_klein) else (u_vk, v_klein)
        zeilen.append([u.name, *(zahl(x) for x in (fest(m_klein / 1e3, 1), _stelle(u_klein, m_klein),
                                                    fest(m_gross / 1e3, 1), _stelle(u_gross, m_gross),
                                                    fest(v_max / 1e3, 1), _stelle(u_v, v_max)))])
    if zeilen:
        p.tabelle(["Träger", Mathe(r"M_{\min}\ [\mathrm{kNm}]"), Mathe(r"u\ [\mathrm{m}]"),
                   Mathe(r"M_{\max}\ [\mathrm{kNm}]"), Mathe(r"u\ [\mathrm{m}]"),
                   Mathe(r"V\ [\mathrm{kN}]"), Mathe(r"u\ [\mathrm{m}]")], zeilen,
                  titel="Träger, über ihre ganze Breite")
        p.text("u misst längs des Trägers ab seinem Anfang. V ist die Querkraft mit dem grössten Betrag, "
               "positiv, wo das Moment längs u wächst.")


def _stelle(u: float, wert: float) -> str:
    """Wo ein Wert eines Trägers liegt -- ausser er steht als null da."""
    return fest(u, 2) if fest(wert / 1e3, 1) != "0.0" else "–"
