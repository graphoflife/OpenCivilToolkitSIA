"""
opencivil/web/balkendaten.py -- was die Oberflaeche von einem Balkensystem zeigt.

VERANTWORTUNG:
Aus dem Befund eines gerechneten Systems, eben oder im Raum
(:class:`~opencivil.stabwerk.rechnung.Systembefund`), die Daten fuer die
Oberflaeche, in den Einheiten der Anzeige -- kN, kNm, mm, mrad, Stellen in m:

* mit jeder Rechnung eine knappe Uebersicht (:func:`uebersicht`): die
  Meldungen mit den Elementen, die sie betreffen, die Knoten ohne
  Drehsteifigkeit, und je Fall die Extremwerte je Stab, die Grenzwerte
  ueber alle (:func:`~opencivil.stabwerk.verlauf.grenzwerte`) und die
  Lagerkraefte;
* auf Anfrage die Verlaeufe eines Falls fuer die Bilder (:func:`verlauf`):
  je Stab seine Lage und Proben der Schnittgroessen und der Verschiebung,
  je Knoten seine Verschiebung und Drehung -- oder dass seine Drehung nicht
  bestimmbar ist --, und die groesste Verschiebung;
* je Querschnitt sein Umriss fuer das Bildchen in seiner Zeile
  (:func:`umrisse`);
* je Linie ihre Achsen, eben und im Raum (:func:`stabachsen`), fuer die
  gestrichelte Faser, die Zugseite und die Lasten in den Richtungen des
  Stabs -- die Oberflaeche legt sie nicht selbst.

EBEN UND IM RAUM IN EINER FORM:
Was sich unterscheidet -- die Achsen, die Groessen, die Lagerkraefte --,
steht je einmal in einer :class:`Darstellung` (:data:`EBEN`, :data:`RAUM`);
welche gilt, sagt die Art der Rechnung. Eine Lage oder Verschiebung ist eine
Liste mit einer Zahl je Achse des Systems -- ``[x, z]`` in der Ebene,
``[x, y, z]`` im Raum --, die Drehung eines Knotens eine Liste mit einer Zahl
je Drehachse. Ein Stab hat seine Achsen im System: ``x`` laengs, ``z`` zur
gestrichelten Faser, im Raum dazu ``y`` (:mod:`opencivil.stabwerk3d.stab`) --
dorthin traegt ein Bild einen positiven Wert auf. In der Ebene steht ``y``
jedes Stabs senkrecht auf ihr, wie ``y`` des Systems: ein Stab zeigt dort
die Achsen, die heissen wie die des Systems.

Die Verlaeufe sind gross; mit jeder Rechnung mitgeliefert, machten sie jede
Eingabe langsamer, auch wenn niemand die Bilder ansieht -- dasselbe wie bei
den Diagrammen der Querschnittsanalyse. Gerechnet wird hier nichts, nur
umgerechnet und in Listen gelegt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from opencivil.core.einheiten import KN, KNM, KN_PRO_M, MM, MRAD
from opencivil.stabwerk import art
from opencivil.stabwerk.rechnung import Stabwerksrechnung, Systembefund
from opencivil.stabwerk.system import SUMMEN, UNBESTIMMT, Fall
from opencivil.stabwerk.verlauf import IN_DER_EBENE, Grenzwert, grenzwerte
from opencivil.stabwerk3d.raum import TOLERANZ, Vektor
from opencivil.web.anzeige import Anzeigegroesse, zahl

#: Wie viele Stuecke ein Stab im Bild mindestens hat -- dazu jede Grenze und jeder Extremwert.
PROBEN_JE_STAB = 24


@dataclass(frozen=True)
class Darstellung:
    """Was eben und im Raum verschieden ist -- die Form der Daten bleibt dieselbe."""

    achsen: Tuple[str, ...]
    """Die Achsen des Systems, in der Folge der Koordinaten."""

    drehachsen: Tuple[Optional[str], ...]
    """
    Um welche Achse sich ein Knoten dreht, in der Folge des Rechenkerns --
    in der Ebene um keine, die einen Namen hat: die Drehung liegt in ihr.
    """

    groessen: Dict[str, Anzeigegroesse]
    """
    Was die Proben eines Stabs je Stelle tragen, ausser ``x`` und der
    Verschiebung -- und wovon die Uebersicht je Stab und Fall den kleinsten
    und den groessten Wert hat.
    """

    schnittgroessen: Tuple[str, ...]
    """Welche der ``groessen`` Schnittgroessen sind -- die Zusammenfassung zeigt sie."""

    durchbiegungen: Tuple[Tuple[str, str], ...]
    """Die Durchbiegungen gegen die Sehne, je mit der Achse des Stabs, in die sie positiv zeigt."""

    felder: Dict[str, str] = field(default_factory=dict)
    """Je Groesse ihr Feld im Verlauf, wo es anders heisst (:data:`~opencivil.stabwerk.verlauf.IN_DER_EBENE`)."""

    def feld(self, groesse: str) -> str:
        return self.felder.get(groesse, groesse)

    def lage(self, v: Any) -> Dict[str, Any]:
        """Anfang und Achsen eines Stabs im System, aus seinem Verlauf -- in den Achsen der Darstellung."""
        return {"anfang": [v.anfang["xyz".index(a)] for a in self.achsen],
                "achsen": self.stabachsen(v.achsen)}

    def stabachsen(self, achsen: Tuple[Vektor, Vektor, Vektor]) -> Dict[str, List[float]]:
        """
        Die Achsen ``(x, y, z)`` eines Stabs im System, die die Darstellung
        zeigt, in ihren Koordinaten -- in der Ebene x und z (siehe Dateikopf).
        """
        i = ["xyz".index(a) for a in self.achsen]
        return {a: [achsen["xyz".index(a)][k] for k in i] for a in self.achsen}

    @property
    def drehungen(self) -> Tuple[str, ...]:
        """Wie die Drehungen eines Knotens heissen: ``φ``, im Raum ``φ_x``, ``φ_y``, ``φ_z``."""
        return tuple("φ" if a is None else f"φ_{a}" for a in self.drehachsen)

    def _lagerwerte(self):
        """
        Je Wert einer Lagerkraft, in der Folge des Rechenkerns, seine
        Groesse, seine Achse und ob er ein Moment ist: erst je Achse eine
        Kraft, dann je Drehachse ein Moment.
        """
        for a in self.achsen:
            yield Anzeigegroesse(f"R_{a}", KN), a, False
        for a in self.drehachsen:
            yield Anzeigegroesse("M" if a is None else f"M_{a}", KNM), a, True

    @property
    def lagerkraefte(self) -> Tuple[Anzeigegroesse, ...]:
        """Die Werte einer Lagerkraft, in der Folge des Rechenkerns."""
        return tuple(g for g, _, _ in self._lagerwerte())

    def als_dict(self) -> Dict[str, Any]:
        """Fuer den Katalog: Namen, Zeichen, Einheiten und Stellen."""
        return {"achsen": list(self.achsen),
                "groessen": {feld: g.als_dict() for feld, g in self.groessen.items()},
                "schnittgroessen": list(self.schnittgroessen),
                "durchbiegungen": [{"feld": feld, "achse": achse}
                                   for feld, achse in self.durchbiegungen],
                "drehungen": list(self.drehungen),
                # Je Wert dazu, wohin er im Bild zeigt: eine Kraft entlang
                # ihrer Achse, ein Moment um seine -- in der Ebene ohne.
                "lagerkraefte": [{**g.als_dict(), "achse": achse, "moment": moment}
                                 for g, achse, moment in self._lagerwerte()]}


#: Das 2D-Balkensystem.
EBEN = Darstellung(
    achsen=("x", "z"),
    drehachsen=(None,),
    groessen={"N": Anzeigegroesse("N", KN), "V": Anzeigegroesse("V", KN),
              "M": Anzeigegroesse("M", KNM), "w": Anzeigegroesse("w", MM, stellen=2),
              "phi": Anzeigegroesse("φ", MRAD, r"\varphi", 2)},
    schnittgroessen=("N", "V", "M"),
    durchbiegungen=(("w", "z"),),
    felder=IN_DER_EBENE,
)

#: Das 3D-Balkensystem.
RAUM = Darstellung(
    achsen=("x", "y", "z"),
    drehachsen=("x", "y", "z"),
    groessen={**{g: Anzeigegroesse(g, KN) for g in ("N", "V_y", "V_z")},
              **{g: Anzeigegroesse(g, KNM) for g in ("T", "M_y", "M_z")},
              **{g: Anzeigegroesse(g, MM, stellen=2) for g in ("f_y", "f_z")}},
    schnittgroessen=("N", "V_y", "V_z", "T", "M_y", "M_z"),
    durchbiegungen=(("f_y", "y"), ("f_z", "z")),
)

#: Welche Darstellung zu welcher Art der Rechnung gehoert.
_DARSTELLUNGEN = {art.EBENE: EBEN, art.RAUM: RAUM}


def _darstellung(befund: Systembefund) -> Darstellung:
    return _DARSTELLUNGEN[befund.ergebnis.art]


def uebersicht(befund: Optional[Systembefund]) -> Dict[str, Any]:
    """
    Was die Oberflaeche nach jeder Rechnung von einem System weiss -- ohne
    die Verlaeufe. Ohne Befund lief es nicht, etwa weil ein Baustoff fehlt.
    """
    if befund is None:
        return {"gerechnet": False}
    e = befund.ergebnis
    d = _darstellung(befund)
    return {
        "gerechnet": True,
        "gueltig": e.gueltig,
        "meldungen": [{"text": m.text, "elemente": list(m.elemente), "fehler": m.fehler}
                      for m in e.meldungen],
        "unbestimmt": e.unbestimmt(),
        "unbestimmt_text": UNBESTIMMT,
        "summen_text": SUMMEN,
        "beweglich": list(e.beweglich),
        "unbekannte": len(e.unbekannte),
        "faelle": [_fall(befund, d, f) for f in e.faelle],
        # Das Eigengewicht je Stab in kN/m -- das Zeichenfenster zeigt es im
        # Lastfall, der es bekommt; gewaehlt und geloescht wird es nicht.
        "eigengewicht": {stab: zahl(g, KN_PRO_M) for stab, g in befund.eigengewicht.items()},
    }


def _fall(befund: Systembefund, d: Darstellung, fall: Fall) -> Dict[str, Any]:
    """
    Je Stab und Groesse der kleinste, der groesste und der massgebende Wert
    als ``[x, Wert]``, je Groesse dieselben ueber alle Staebe mit dem Stab --
    und die Lagerkraefte.
    """
    verlaeufe = befund.verlaeufe(fall.name)
    staebe: Dict[str, Dict[str, Any]] = {name: {} for name in verlaeufe}
    grenzen = {}
    for groesse, anzeige in d.groessen.items():
        extreme = {name: v.extrem(d.feld(groesse)) for name, v in verlaeufe.items()}
        for name, e in extreme.items():
            staebe[name][groesse] = {wo: [x, anzeige.zahl(w)] for wo, (x, w) in (
                ("kleinst", e.kleinst), ("groesst", e.groesst), ("massgebend", e.massgebend))}
        g = grenzwerte(extreme)
        grenzen[groesse] = {wo: _grenzwert(w, anzeige) for wo, w in (
            ("kleinst", g.kleinst), ("groesst", g.groesst), ("massgebend", g.massgebend))}
    return {
        "name": fall.name,
        "kombination": fall.kombination,
        "staebe": staebe,
        "grenzen": grenzen,
        # Dieselben Zeilen wie in der Herleitung -- mit den Summen von
        # Linienlager und Bettung, sonst gingen die Kraefte nicht auf.
        "lagerkraefte": [
            {"wo": k.wo, "knoten": k.knoten, "summe": k.summe,
             **{g.zeichen: g.zahl(w) for g, w in zip(d.lagerkraefte, k.werte)}}
            for k in befund.lagerkraefte(fall)],
    }


def _grenzwert(w: Grenzwert, anzeige: Anzeigegroesse) -> Dict[str, Any]:
    return {"stab": w.stab, "x": w.x, "wert": anzeige.zahl(w.wert)}


def verlauf(befund: Systembefund, name: str) -> Dict[str, Any]:
    """
    Die Bilder eines Falls: je Stab die Proben, je Knoten Verschiebung und
    Drehung, und die groesste Verschiebung in mm -- genau, nicht aus den
    Proben (:meth:`~opencivil.stabwerk.verlauf.Stabverlauf.groesste_verschiebung`).
    """
    d = _darstellung(befund)
    fall = befund.ergebnis.fall(name)
    verlaeufe = befund.verlaeufe(name)
    staebe = {}
    for stab, v in verlaeufe.items():
        staebe[stab] = {
            "L": v.L, **d.lage(v),
            "proben": [{"x": w["x"], **{g: a.zahl(w[d.feld(g)]) for g, a in d.groessen.items()},
                        "u": [zahl(w[f"u{achse}"], MM) for achse in d.achsen]}
                       for w in v.proben(PROBEN_JE_STAB)],
        }
    unbestimmt = set(befund.ergebnis.unbestimmt())
    n = len(d.achsen)
    knoten = {}
    for ort in befund.ergebnis.orte.values():
        if not ort.knoten:
            continue
        werte = fall.verschiebungen[ort.name]
        offen = ort.knoten in unbestimmt
        knoten[ort.knoten] = {"lage": [getattr(ort, achse) for achse in d.achsen],
                              "u": [zahl(u, MM) for u in werte[:n]],
                              "phi": None if offen else [zahl(p, MRAD) for p in werte[n:]],
                              "unbestimmt": offen}
    groesste = max(v.groesste_verschiebung()[1] for v in verlaeufe.values())
    return {"fall": name, "kombination": fall.kombination, "staebe": staebe,
            "knoten": knoten, "groesste_verschiebung": zahl(groesste, MM),
            "unbestimmt_text": UNBESTIMMT}


def faelle(befund: Optional[Systembefund]) -> List[str]:
    """Die Namen der gerechneten Faelle, Lastfaelle zuerst."""
    return [f.name for f in befund.ergebnis.faelle] if befund is not None else []


def umrisse(system: Stabwerksrechnung, loesung: Any) -> Dict[str, List[List[List[float]]]]:
    """
    Je Querschnitt eines Systems sein Umriss in mm, fuer das Bildchen in
    seiner Zeile (Benutzer, 2026-10-24) -- ihn kennt jeder Querschnitt selbst
    (:meth:`~opencivil.stabwerk.stabquerschnitt.Stabquerschnitt.umriss`).
    Ein Querschnitt, der nicht geht, hat keinen.
    """
    return {q.kennung: [[[round(y, 1), round(z, 1)] for y, z in p]
                        for p in ([] if q.fehler else q.umriss(loesung))]
            for q in system.querschnitte}


def stabachsen(rechnung: Stabwerksrechnung) -> Dict[str, Dict[str, List[float]]]:
    """
    Je Linie eines Systems ihre Achsen, wie der Rechenkern sie legt
    (:attr:`~opencivil.stabwerk.art.Art.achsen`) -- auch ohne Rechnung, auch
    fuer eine Linie ohne Stab, in den Koordinaten der Zeichnung
    (:meth:`Darstellung.stabachsen`). Eine Linie ohne Laenge hat keine.
    """
    systemart = rechnung.ART
    d = _DARSTELLUNGEN[systemart]
    system = systemart.im_raum(rechnung.system)
    knoten = {k.name: k for k in system.knoten}
    heraus = {}
    for s in system.staebe:
        a, b = knoten.get(s.a), knoten.get(s.b)
        if a is None or b is None or math.dist((a.x, a.y, a.z), (b.x, b.y, b.z)) <= TOLERANZ:
            continue
        heraus[s.name] = d.stabachsen(systemart.achsen(a, b, s.drehung)[1])
    return heraus
