"""
opencivil/web/werkstoffkurven.py -- die Spannung-Dehnung-Linie je Material, als JSON.

VERANTWORTUNG:
Was der Reiter «Diagramme» unter «Werkstoffgesetze» zeichnet: je Material
seine Linie, aus denselben Gesetzen, mit denen der Querschnitt rechnet
(:mod:`opencivil.querschnitt.werkstoffgesetz`), in ‰ und N/mm². Welche Art
welche Linie hat, steht in :data:`KURVEN` -- eine neue Materialart ohne
Linie faellt im Test auf, nicht erst beim Rechnen.

Bis 2026-11-26 stand das in :mod:`opencivil.web.diagrammdaten`, das damit
an tausend Zeilen kam.
"""

from __future__ import annotations

from typing import Callable, Dict, Optional

from opencivil.core.einheiten import N_PRO_MM2, PROMILLE
from opencivil.core.rechenwerk import Loesung
from opencivil.material.basis import Baustoffart
from opencivil.material.spannstahl import SPANNSTAHLSORTEN, Erzeugnisart
from opencivil.projekt import Aufbau
from opencivil.querschnitt.werkstoffgesetz import (
    BLOCKANTEIL, Baustahlgesetz, Betongesetz, Holzgesetz, HolzPlastisch, Spannstahlgesetz,
    Spannungsblock, Stahlgesetz,
)
from opencivil.web.anzeige import zahl


def werkstoffgesetze(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Punktfolgen der Spannungs-Dehnungs-Beziehungen, je Material.

    Gerechnet wird mit denselben Gesetzen wie im Nachweis -- die Kurve zeigt
    also genau das, was der Querschnittsintegration zugrunde liegt, und nicht
    eine zweite, nachgebaute Fassung.

    Vorzeichen wie im ganzen Werkzeug: Zug positiv. Der Beton liegt damit im
    dritten Quadranten, der Stahl spannt sich ueber beide.

    Welche Kurve ein Material hat, sagt seine Art (:data:`KURVEN`); fehlt ein
    Kennwert in der Loesung, hat es noch keine. Bis 2026-11-26 galt alles,
    was nicht Beton war, als Betonstahl, und ein Baustahl fiel still weg,
    weil ihm dessen Kennwerte fehlten.

    Ausser Punkten und Marken kann eine Kurve einen ``hinweis`` tragen: was
    das Bild nicht zeigt -- beim Spannstahl der flachere Anstieg der Litzen --,
    und eine ``zweite`` Linie, die ein Schalter zeigt: beim Beton den
    Spannungsblock, beim Holz den Druck elastisch-plastisch.
    """
    ergebnis: Dict[str, dict] = {}

    for kennung, stoff in aufbau.baustoffe.items():
        def wert(kurzname: str) -> Optional[float]:
            eintrag = loesung.werte.get(stoff.definitionen[kurzname].id)
            return eintrag.groesse.si if eintrag else None

        eintrag = KURVEN[stoff.art](wert, stoff.sorte)
        if eintrag:
            eintrag["name"] = stoff.name
            eintrag["art"] = stoff.art.value
            ergebnis[kennung] = eintrag
    return ergebnis


def _betonkurve(wert, sorte: str, schritte: int = 80) -> Optional[dict]:
    """
    Parabel-Rechteck-Beziehung, von null bis zur Bruchdehnung -- mit
    Bemessungswerten, ohne Kriechen, gebaut wie in jeder Rechnung: der
    Beiwert aus ``E_cm`` (:meth:`Betongesetz.mit_modul`).
    """
    f_cd, eps_c1d = wert("f_cd"), wert("eps_c1d")
    eps_c2d, E_cm = wert("eps_c2d"), wert("E_cm")
    if None in (f_cd, eps_c1d, eps_c2d, E_cm):
        return None

    gesetz = Betongesetz.mit_modul(f_c=abs(f_cd), E_c=abs(E_cm), eps_c1d=abs(eps_c1d),
                                   eps_c2d=abs(eps_c2d))
    punkte = []
    for i in range(schritte + 1):
        eps = -abs(eps_c2d) * i / schritte
        punkte.append({"eps": zahl(eps, PROMILLE), "sigma": zahl(gesetz.spannung(eps), N_PRO_MM2)})

    return {
        "punkte": punkte,
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Beton – Parabel-Rechteck-Beziehung",
        "referenz": Betongesetz.REFERENZ,
        "marken": [
            {"eps": zahl(-abs(eps_c1d), PROMILLE), "sigma": zahl(-abs(f_cd), N_PRO_MM2),
             "text": "ε_c1d"},
            {"eps": zahl(-abs(eps_c2d), PROMILLE), "sigma": zahl(-abs(f_cd), N_PRO_MM2),
             "text": "ε_c2d"},
        ],
        "zweite": _spannungsblock(abs(f_cd), abs(eps_c2d)),
    }


def _spannungsblock(f_cd: float, eps_c2d: float) -> dict:
    """
    Der vereinfachte, rechteckige Spannungsverlauf.

    Unterhalb von ``(1 - 0.85) * eps_c2d`` wird keine Spannung angesetzt,
    darueber durchgehend ``f_cd``. Das ist dieselbe Vereinfachung, die auch der
    Handrechnung zugrunde liegt -- dort als Druckzone der Hoehe ``0.85 x``.
    Beide Bilder gehoeren zusammen, und genau deshalb steht die Stufe hier neben
    der Parabel: man sieht, was man aufgibt, wenn man von Hand rechnet.
    """
    block = Spannungsblock(f_cd=f_cd, eps_c2d=eps_c2d)
    ecken = [
        (0.0, 0.0),
        (-block.eps_knick, 0.0),
        (-block.eps_knick, -block.f_cd),
        (-eps_c2d, -block.f_cd),
    ]
    return {
        "punkte": [{"eps": zahl(e, PROMILLE), "sigma": zahl(s, N_PRO_MM2)} for e, s in ecken],
        "titel": "vereinfacht (Spannungsblock)",
        "beschreibung": (
            f"σ = 0 bis {1 - BLOCKANTEIL:.2f}·ε_c2d, darüber f_cd. "
            f"Entspricht der Druckzone {BLOCKANTEIL}·x der Handrechnung."
        ),
    }


def _stahlkurve(wert, sorte: str) -> Optional[dict]:
    """Betonstahl: bilinear, auf Zug und Druck getrennt begrenzt."""
    E_s, f_yd = wert("E_s"), wert("f_yd")
    f_yd_druck, eps_ud = wert("f_yd_druck"), wert("eps_ud")
    if None in (E_s, f_yd, f_yd_druck, eps_ud):
        return None
    return _knickkurve(Stahlgesetz(E_s=E_s, f_yd=f_yd, f_yd_druck=abs(f_yd_druck), eps_ud=abs(eps_ud)),
                       "Betonstahl – bilineare Beziehung")


def _baustahlkurve(wert, sorte: str) -> Optional[dict]:
    """Baustahl: elastisch -- ideal plastisch, in Zug und Druck gleich, mit ``f_yd = f_y / gamma_M1``."""
    E_a, f_yd, eps_ud = wert("E_a"), wert("f_yd"), wert("eps_ud")
    if None in (E_a, f_yd, eps_ud):
        return None
    return _knickkurve(Baustahlgesetz.gleich(E_a, f_yd, eps_ud), "Baustahl – elastisch-plastisch")


def _knickkurve(gesetz: Stahlgesetz, titel: str) -> dict:
    """
    Eine Linie ohne Verfestigung, aus ihrem Gesetz. Fuenf Eckpunkte genuegen
    -- dazwischen ist sie gerade, und mehr Punkte wuerden nur vortaeuschen,
    dass etwas gekruemmt waere.
    """
    f, f_druck, eps_ud = gesetz.f_yd, gesetz.f_yd_druck, gesetz.eps_ud
    eps_yd = gesetz.eps_yd
    ecken = [(-eps_ud, -f_druck), (-f_druck / gesetz.E_s, -f_druck), (0.0, 0.0), (eps_yd, f), (eps_ud, f)]
    return {
        "punkte": [{"eps": zahl(e, PROMILLE), "sigma": zahl(s, N_PRO_MM2)} for e, s in ecken],
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": titel,
        "referenz": gesetz.REFERENZ,
        "marken": [
            {"eps": zahl(eps_yd, PROMILLE), "sigma": zahl(f, N_PRO_MM2), "text": "ε_yd"},
            {"eps": zahl(eps_ud, PROMILLE), "sigma": zahl(f, N_PRO_MM2), "text": "ε_ud"},
        ],
    }


def _spannstahlkurve(wert, sorte: str) -> Optional[dict]:
    """
    Spannstahl: Figur 17, nur auf Zug -- mit dem Modul der Draehte und
    Staebe. Hat die Sorte auch Litzen (Tabelle 7), sagt der Hinweis, dass
    sie flacher ansteigen (195 statt 200 GPa) und wo sie zu fliessen beginnen.
    """
    E_p, E_litze, f_pd, eps_ud = wert("E_p"), wert("E_p_litze"), wert("f_pd"), wert("eps_ud")
    if None in (E_p, E_litze, f_pd, eps_ud):
        return None
    gesetz = Spannstahlgesetz(E_p=E_p, f_pd=f_pd, eps_ud=eps_ud)
    ecken = [(0.0, 0.0), (gesetz.eps_pd, f_pd), (eps_ud, f_pd)]
    litzen = any(e.art is Erzeugnisart.LITZE for e in SPANNSTAHLSORTEN[sorte].erzeugnisse)
    return {
        "punkte": [{"eps": zahl(e, PROMILLE), "sigma": zahl(s, N_PRO_MM2)} for e, s in ecken],
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Spannstahl – bilineare Beziehung",
        "referenz": gesetz.REFERENZ,
        "marken": [
            {"eps": zahl(gesetz.eps_pd, PROMILLE), "sigma": zahl(f_pd, N_PRO_MM2), "text": "ε_pd"},
            {"eps": zahl(eps_ud, PROMILLE), "sigma": zahl(f_pd, N_PRO_MM2), "text": "ε_ud"},
        ],
        "hinweis": (f"Gezeichnet für Drähte und Stäbe, E_p = {zahl(E_p, N_PRO_MM2):.0f} N/mm². "
                    f"Litzen steigen mit E_p = {zahl(E_litze, N_PRO_MM2):.0f} N/mm² flacher an "
                    f"und fliessen ab ε_pd = {zahl(f_pd / E_litze, PROMILLE):.2f} ‰ statt "
                    f"{zahl(gesetz.eps_pd, PROMILLE):.2f} ‰ (SIA 262:2025, 3.3.2.4)."
                    if litzen else ""),
    }


def _holzkurve(wert, sorte: str) -> Optional[dict]:
    """
    Holz: linear bis zum Bruch, auf Zug wie auf Druck (SIA 265:2012,
    3.1.2.1) -- und als zweite Linie der Druck elastisch-plastisch (3.1.2.2),
    bis zur Grenzstauchung nach Vorgabe.
    """
    E, f_t, f_c, eps_cu = wert("E_0_mean"), wert("f_t_0_d"), wert("f_c_0_d"), wert("eps_cu")
    if None in (E, f_t, f_c, eps_cu):
        return None
    linear = Holzgesetz(E=E, f_t=f_t, f_c=f_c)
    plastisch = HolzPlastisch(E=E, f_t=f_t, f_c=f_c, eps_cu=eps_cu)

    def linie(ecken):
        return [{"eps": zahl(e, PROMILLE), "sigma": zahl(s, N_PRO_MM2)} for e, s in ecken]

    return {
        "punkte": linie([(-linear.eps_c, -f_c), (0.0, 0.0), (linear.eps_t, f_t)]),
        "x_titel": "ε [‰]",
        "y_titel": "σ [N/mm²]",
        "titel": "Holz – linear bis zum Bruch",
        "referenz": linear.REFERENZ,
        "marken": [
            {"eps": zahl(linear.eps_t, PROMILLE), "sigma": zahl(f_t, N_PRO_MM2), "text": "ε_t,0,d"},
            {"eps": zahl(-linear.eps_c, PROMILLE), "sigma": zahl(-f_c, N_PRO_MM2), "text": "ε_c,0,d"},
        ],
        "zweite": {
            "punkte": linie([(-plastisch.eps_cu, -f_c), (-plastisch.eps_c, -f_c), (0.0, 0.0),
                             (plastisch.eps_t, f_t)]),
            "titel": "auf Druck elastisch-plastisch",
            "beschreibung": (f"Wo das Bauteil plastisch stauchen kann ({plastisch.REFERENZ}): "
                             f"bei f_c,0,d waagrecht bis ε_cu = "
                             f"{zahl(plastisch.eps_cu, PROMILLE):.2f} ‰."),
        },
    }


#: Je Materialart ihre Spannung-Dehnung-Linie, aus den Kennwerten einer
#: Loesung -- wo es eines gibt, ein Gesetz des Querschnitts -- und der Sorte:
#: beim Spannstahl sagt sie, ob es Litzen gibt.
KURVEN: Dict[Baustoffart, Callable[[Callable[[str], Optional[float]], str], Optional[dict]]] = {
    Baustoffart.BETON: _betonkurve,
    Baustoffart.BETONSTAHL: _stahlkurve,
    Baustoffart.BAUSTAHL: _baustahlkurve,
    Baustoffart.SPANNSTAHL: _spannstahlkurve,
    Baustoffart.HOLZ: _holzkurve,
}
