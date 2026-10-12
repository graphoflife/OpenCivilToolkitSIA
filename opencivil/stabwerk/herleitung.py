"""
opencivil/stabwerk/herleitung.py -- wie ein Balkensystem seine Rechnung aufschreibt.

VERANTWORTUNG:
Die Herleitung der Steifigkeitsmethode, so dass man sie von Hand
nachrechnen kann: das System in Tabellen, die Ansaetze -- Steifigkeitsmatrix
eines Stabs, Drehung, Bettung, arbeitsgleiche Lasten, Gleichungssystem --,
die Matrizen mit Zahlen, solange sie klein genug sind, und je Lastfall und
Kombination die Verschiebungen der Knoten, die Kraefte an den Stabenden, die
Lagerkraefte, die Extremwerte und die Gleichgewichtsprobe.

WIE VIEL MIT ZAHLEN:
Die Matrix jedes Stabs bis :data:`STAEBE_MIT_MATRIX` Teilstaebe, die
Gesamtmatrix bis :data:`UNBEKANNTE_MIT_MATRIX` Unbekannte. Darueber stuende
eine Wand aus Zahlen, die niemand nachrechnet; die Tabellen gibt es immer.

EINHEITEN:
Laengen in m, Verschiebungen in mm, Drehungen in mrad, Kraefte in kN,
Momente in kNm -- in den Matrizen kN und m. Die Schnittgroessen mit den
Vorzeichen der Baustatik (:mod:`~opencivil.stabwerk.verlauf`).
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Dict, List, Sequence, Tuple

from opencivil.core.latex import Mathe, fest, text_latex
from opencivil.core.protokoll import Protokoll
from opencivil.stabwerk import stab as st
from opencivil.stabwerk.matrix import dicht
from opencivil.stabwerk.modell import FEST, Stablast
from opencivil.stabwerk.system import UNBESTIMMT, Fall

if TYPE_CHECKING:
    from opencivil.stabwerk.rechnung import Balkensystem

#: Bis zu so vielen Teilstaeben steht die Matrix jedes einzelnen mit Zahlen da.
STAEBE_MIT_MATRIX = 6

#: Bis zu so vielen Unbekannten stehen Gesamtmatrix, Lastvektor und Loesung mit Zahlen da.
UNBEKANNTE_MIT_MATRIX = 12

#: Was die Steifigkeit annimmt -- nach Vorgabe, nicht nachgeschlagen.
ANNAHME = ("Steifigkeit nach Vorgabe, nicht nachgeschlagen: E_cm für Beton und E_s für "
           "Betonstahl, am ungerissenen Bruttoquerschnitt, ohne Schubverformung; "
           "Gleichgewicht am unverformten System (Theorie 1. Ordnung).")

#: Das Gleichungssystem in Zeichen.
GLEICHUNGSSYSTEM_LATEX = (
    r"\mathbf{K} = \sum_{\text{Stäbe}} \mathbf{T}^{\mathsf{T}} \cdot \mathbf{k} \cdot "
    r"\mathbf{T} \qquad \mathbf{K} \cdot \mathbf{x} = \mathbf{F}"
)

#: Von den Kraeften an den Stabenden zu den Schnittgroessen laengs des Stabs.
SCHNITTGROESSEN_LATEX = (
    r"N(0) = -s_{u,a} \qquad V(0) = s_{v,a} \qquad M(0) = -s_{\theta,a} \qquad "
    r"\frac{\mathrm{d}N}{\mathrm{d}x} = -p_x \qquad \frac{\mathrm{d}V}{\mathrm{d}x} = p_y "
    r"\qquad \frac{\mathrm{d}M}{\mathrm{d}x} = V - m"
)

#: Die Biegelinie aus Moment und Normalkraft.
BIEGELINIE_LATEX = r"v'' = \frac{M}{EI} \qquad u' = \frac{N}{EA}"


def schreiben(p: Protokoll, system: "Balkensystem") -> None:
    """Die ganze Herleitung eines gerechneten Systems."""
    e = system.ergebnis
    p.annahme(ANNAHME)
    _staebe(p, system)
    _lager(p, system)
    for m in e.meldungen:
        (p.warnung if m.fehler else p.hinweis)(m.text)
    if e.K is None:
        return
    _ansaetze(p, system)
    _unbekannte(p, system)
    if not e.faelle:
        return
    for fall in e.faelle:
        _fall(p, system, fall)


# ===========================================================================
# Das System
# ===========================================================================


def _staebe(p: Protokoll, system: "Balkensystem") -> None:
    modell = system.gerechnet
    knoten = {k.name: k for k in modell.knoten}
    name = {q.kennung: q.name for q in system.querschnitte}
    zeilen = []
    for stab in modell.staebe:
        a, b = knoten.get(stab.a), knoten.get(stab.b)
        if a is None or b is None:
            continue
        L = math.hypot(b.x - a.x, b.z - a.z)
        alpha = math.degrees(math.atan2(b.z - a.z, b.x - a.x))
        paar = system.paare.get(stab.name)
        steif = paar is not None and stab.traegt
        gelenke = {(True, True): "beide", (True, False): "Anfang",
                   (False, True): "Ende"}.get((stab.gelenk_a, stab.gelenk_b), "–")
        zeilen.append([
            stab.name, f"{stab.a} – {stab.b}", Mathe(fest(L, 3)), Mathe(fest(alpha, 1)),
            name[paar[0]] if paar is not None else ("kein Stab" if not stab.traegt else "–"),
            Mathe(fest(stab.EA / 1e6, 0)) if steif else "–",
            Mathe(fest(stab.EI / 1e3, 0)) if steif else "–",
            gelenke if stab.traegt else "–",
            _linienlager(stab.quer, stab.laengs),
        ])
    if zeilen:
        p.tabelle(["Stab", "Knoten", Mathe(r"L\ [\mathrm{m}]"), Mathe(r"\alpha\ [°]"),
                   "Querschnitt", Mathe(r"EA\ [\mathrm{MN}]"), Mathe(r"EI\ [\mathrm{kNm}^{2}]"),
                   "Gelenk", "Linienlager"], zeilen, titel="Stäbe")


def _halt(wert, einheit: str, faktor: float = 1e3) -> str:
    if wert is None:
        return "frei"
    if wert == FEST:
        return "fest"
    return f"Feder {wert / faktor:g} {einheit}"


def _linienlager(quer, laengs) -> str:
    teile = [f"{richtung} {_halt(wert, 'kN/m²').replace('Feder', 'Bettung')}"
             for richtung, wert in (("quer", quer), ("längs", laengs)) if wert is not None]
    return ", ".join(teile) or "–"


def _lager(p: Protokoll, system: "Balkensystem") -> None:
    lager = system.gerechnet.lager
    if not lager:
        return
    p.tabelle(["Lager", "Knoten", Mathe("x"), Mathe("z"), Mathe(r"\varphi")],
              [[l.name, l.knoten, _halt(l.x, "kN/m"), _halt(l.z, "kN/m"),
                _halt(l.phi, "kNm/rad")] for l in lager], titel="Lager")


def _ansaetze(p: Protokoll, system: "Balkensystem") -> None:
    e, modell = system.ergebnis, system.gerechnet
    p.ansatz(st.STEIFIGKEIT_LATEX, titel="Steifigkeitsmatrix eines Stabs, in seinen Achsen",
             name="Steifigkeitsmatrix eines Stabs")
    p.ansatz(st.DREHUNG_LATEX, titel="Von den Achsen des Systems in die des Stabs",
             name="Drehung in die Achsen des Stabs")
    if any(t.k_quer or t.k_laengs for t in e.teilstaebe):
        p.ansatz(st.BETTUNG_LATEX, titel="Bettung eines Stabs, quer und längs",
                 name="Bettung eines Stabs")
    if any(isinstance(l, Stablast) for f in modell.lastfaelle for l in f.lasten):
        p.ansatz(st.LASTEN_LATEX, titel="Arbeitsgleiche Knotenkräfte der Lasten auf einem Stab",
                 name="Arbeitsgleiche Knotenkräfte")
    p.ansatz(GLEICHUNGSSYSTEM_LATEX, titel="Gesamtsteifigkeitsmatrix und Gleichungssystem",
             name="Gleichungssystem der Steifigkeitsmethode")
    if any(t.gelenk_a or t.gelenk_b for t in e.teilstaebe):
        p.text("Ein Gelenk gibt dem Stabende eine eigene Drehung als Unbekannte; der Knoten "
               "dreht sich unabhängig davon.")
    unbestimmt = e.unbestimmt()
    if unbestimmt:
        p.hinweis(f"{UNBESTIMMT}: {', '.join(unbestimmt)}. Alle Stäbe sind dort gelenkig "
                  f"angeschlossen; die Drehung ist gestrichen und null gesetzt.")
    if len(e.teilstaebe) <= STAEBE_MIT_MATRIX:
        for t in e.teilstaebe:
            p.gleichung(rf"\mathbf{{k}}_{{\text{{{text_latex(_teilname(system, t))}}}}} = "
                        + _matrix(t.k, 1e-3),
                        titel=f"Steifigkeitsmatrix {_teilname(system, t)}, L = {t.L:.3f} m "
                              f"(kN, m)")
    p.ansatz(SCHNITTGROESSEN_LATEX, titel="Schnittgrössen aus den Kräften an den Stabenden",
             name="Schnittgrössen längs eines Stabs")
    p.ansatz(BIEGELINIE_LATEX, titel="Biegelinie und Längsverschiebung",
             name="Biegelinie eines Stabs")


def _teilname(system: "Balkensystem", teil) -> str:
    """Der Name eines Teilstabs: der seines Stabs -- mit Nummer, wenn dieser geteilt ist."""
    stuecke = sum(1 for t in system.ergebnis.teilstaebe if t.stab.name == teil.stab.name)
    return teil.stab.name if stuecke == 1 else f"{teil.stab.name}.{teil.nummer + 1}"


def _unbekannte(p: Protokoll, system: "Balkensystem") -> None:
    e = system.ergebnis
    n = len(e.unbekannte)
    if n > UNBEKANNTE_MIT_MATRIX:
        p.text(f"{n} Unbekannte.")
        return
    p.text(f"{n} Unbekannte: " + ", ".join(f"{i + 1}. {u}" for i, u in enumerate(e.unbekannte))
           + ".")
    p.gleichung(r"\mathbf{K} = " + _matrix(dicht(e.K), 1e-3),
                titel="Gesamtsteifigkeitsmatrix (kN, m)")


# ===========================================================================
# Je Fall
# ===========================================================================


def _fall(p: Protokoll, system: "Balkensystem", fall: Fall) -> None:
    modell = system.gerechnet
    p.titel(f"{'Kombination' if fall.kombination else 'Lastfall'} «{fall.name}»", ebene=3)
    if fall.kombination:
        k = next(k for k in modell.kombinationen if k.name == fall.name)
        p.text(" + ".join(f"{beiwert:g} · {lf}" for lf, beiwert in k.faktoren.items())
               or "Keine Beiwerte – die Kombination ist leer.")
    e = system.ergebnis
    if len(e.unbekannte) <= UNBEKANNTE_MIT_MATRIX:
        p.gleichung(r"\mathbf{F} = " + _matrix([[f] for f in fall.F], 1e-3)
                    + r" \qquad \mathbf{x} = \mathbf{K}^{-1} \cdot \mathbf{F} = "
                    + _matrix([[x] for x in fall.x], 1.0),
                    titel="Lastvektor (kN, kNm) und Lösung (m, rad)")
    _verschiebungen(p, system, fall)
    verlaeufe = system.verlaeufe(fall.name)
    _stabenden(p, verlaeufe)
    _lagerkraefte(p, system, fall)
    _extremwerte(p, verlaeufe)
    _gleichgewicht(p, fall)


def _verschiebungen(p: Protokoll, system: "Balkensystem", fall: Fall) -> None:
    orte = system.ergebnis.orte
    zeilen = []
    for k in system.gerechnet.knoten:
        ort = orte.get(k.name)
        if ort is None:
            continue
        ux, uz, phi = fall.verschiebungen[k.name]
        zeilen.append([k.name, Mathe(fest(ux * 1e3, 2)), Mathe(fest(uz * 1e3, 2)),
                       "nicht bestimmbar" if ort.drehung == "unbestimmt"
                       else Mathe(fest(phi * 1e3, 3))])
    p.tabelle(["Knoten", Mathe(r"u_x\ [\mathrm{mm}]"), Mathe(r"u_z\ [\mathrm{mm}]"),
               Mathe(r"\varphi\ [\mathrm{mrad}]")], zeilen, titel="Verschiebungen der Knoten")


def _stabenden(p: Protokoll, verlaeufe) -> None:
    zeilen = []
    for name, v in verlaeufe.items():
        a, b = v.bei(0.0), v.bei(v.L, links=True)
        zeilen.append([name] + [Mathe(fest(w[g] / 1e3, 1)) for w in (a, b)
                                for g in ("N", "V", "M")])
    kopf = ["Stab"] + [Mathe(rf"{g}_{{{ende}}}\ [\mathrm{{{einheit}}}]")
                       for ende in ("a", "b")
                       for g, einheit in (("N", "kN"), ("V", "kN"), ("M", "kNm"))]
    p.tabelle(kopf, zeilen, titel="Schnittgrössen an den Stabenden")


def _lagerkraefte(p: Protokoll, system: "Balkensystem", fall: Fall) -> None:
    orte = system.ergebnis.orte
    lager_an: Dict[str, List[str]] = {}
    for l in system.gerechnet.lager:
        lager_an.setdefault(l.knoten, []).append(l.name)
    zeilen = []
    for name, (rx, rz, rm) in fall.lagerkraefte.items():
        ort = orte[name]
        if ort.knoten:
            wo = (", ".join(lager_an[ort.knoten]) + f" ({ort.knoten})"
                  if ort.knoten in lager_an else ort.knoten)
        else:
            wo = f"{ort.stab} bei {ort.stelle:.3f} m"
        zeilen.append([wo, Mathe(fest(rx / 1e3, 1)), Mathe(fest(rz / 1e3, 1)),
                       Mathe(fest(rm / 1e3, 1))])
    for stab, werte in fall.linienlast.items():
        zeilen.append([f"{stab}: Lasten geradewegs ins Linienlager"]
                      + [Mathe(fest(w / 1e3, 1)) for w in werte])
    for stab, werte in fall.bettung.items():
        zeilen.append([f"{stab}: Bettung, Summe"] + [Mathe(fest(w / 1e3, 1)) for w in werte])
    if zeilen:
        p.tabelle(["Lager", Mathe(r"R_x\ [\mathrm{kN}]"), Mathe(r"R_z\ [\mathrm{kN}]"),
                   Mathe(r"M\ [\mathrm{kNm}]")], zeilen, titel="Lagerkräfte, auf das Tragwerk")
        if fall.linienlast or fall.bettung:
            p.text("Bei Linienlagern und Bettung steht die Summe; ihr Moment um den Ursprung.")


def _extremwerte(p: Protokoll, verlaeufe) -> None:
    zeilen = []
    massgebend: Tuple[float, str, float, float] = (0.0, "", 0.0, 0.0)
    for name, v in verlaeufe.items():
        for groesse, einheit, faktor, stellen in (("N", "kN", 1e-3, 1), ("V", "kN", 1e-3, 1),
                                                  ("M", "kNm", 1e-3, 1), ("w", "mm", 1e3, 2)):
            extrem = v.extrem(groesse)
            (x0, klein), (x1, gross) = extrem.kleinst, extrem.groesst
            zeilen.append([name, Mathe(groesse),
                           Mathe(f"{fest(klein * faktor, stellen)}\\ \\mathrm{{{einheit}}}"),
                           Mathe(fest(x0, 2)),
                           Mathe(f"{fest(gross * faktor, stellen)}\\ \\mathrm{{{einheit}}}"),
                           Mathe(fest(x1, 2))])
            if groesse == "w":
                for x, w in ((x0, klein), (x1, gross)):
                    if abs(w) > abs(massgebend[0]):
                        massgebend = (w, name, x, v.L)
    p.tabelle(["Stab", "Grösse", "kleinst", Mathe(r"x\ [\mathrm{m}]"), "grösst",
               Mathe(r"x\ [\mathrm{m}]")], zeilen, titel="Extremwerte")
    w, name, x, L = massgebend
    if name and abs(w) > 0.0:
        p.text(f"Grösste Durchbiegung gegen die Sehne: {name}, w = {w * 1e3:.2f} mm bei "
               f"x = {x:.2f} m, L/w = {L / abs(w):.0f}.")


def _gleichgewicht(p: Protokoll, fall: Fall) -> None:
    """Lasten und Lagerkraefte zusammen -- null bis auf Rundung."""
    lasten, rest = fall.lastsumme, fall.gleichgewicht
    zeilen = []
    for i, (summe, einheit) in enumerate(((r"\sum F_x", "kN"), (r"\sum F_z", "kN"),
                                          (r"\sum M_0", "kNm"))):
        zeilen.append([Mathe(summe), Mathe(fest(lasten[i] / 1e3, 3)),
                       Mathe(fest((rest[i] - lasten[i]) / 1e3, 3)),
                       Mathe(fest(rest[i] / 1e3, 3)), einheit])
    p.tabelle(["", "Lasten", "Lager", "Summe", ""], zeilen,
              titel="Gleichgewichtsprobe (Moment um den Ursprung)")


# ===========================================================================
# Zahlen
# ===========================================================================


def _zahl(x: float) -> str:
    """Vier gueltige Ziffern -- ab einer Million und unter einem Tausendstel mit Zehnerpotenz."""
    if abs(x) < 1e-12:
        return "0"
    hoch = math.floor(math.log10(abs(x)))
    if -3 <= hoch < 6:
        return fest(x, max(0, 3 - hoch))
    mantisse = round(x / 10.0 ** hoch, 3)
    if abs(mantisse) >= 10.0:
        mantisse, hoch = mantisse / 10.0, hoch + 1
    return rf"{fest(mantisse, 3)} \cdot 10^{{{hoch}}}"


def _matrix(zeilen: Sequence[Sequence[float]], faktor: float) -> str:
    inhalt = r" \\ ".join(" & ".join(_zahl(w * faktor) for w in zeile) for zeile in zeilen)
    return rf"\begin{{bmatrix}} {inhalt} \end{{bmatrix}}"
