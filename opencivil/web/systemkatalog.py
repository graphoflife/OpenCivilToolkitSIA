"""
opencivil/web/systemkatalog.py -- was die Oberflaeche an einem Balkensystem waehlen laesst.

VERANTWORTUNG:
Der Katalog eines Balkensystems, eben und im Raum aus derselben Funktion
(:func:`katalog`): Querschnitte -- Vorlagen, Stahlprofile, Arten --,
Materialien, Lasten und ihre Richtungen, Lager und Linienlager, die
Diagramme und wie die Ergebnisse heissen. Beide haben dieselben Schluessel;
was eine Art anders hat, sagen ihre Beschreibung -- Achsen, Lagerfelder,
Linienlager, die Wahl jedes Feldes, die Einheiten der Federn --, ihre
Rechnung -- die Kennwerte von Querschnitt und Material -- und die
Darstellung ihrer Ergebnisse (:mod:`opencivil.web.balkendaten`). Bis
2026-11-15 stand der Katalog des 2D-Balkensystems in :mod:`opencivil.web.api`.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Dict

from opencivil.projekt.balkensystem import EINHEIT_DER_LAST, HALT
from opencivil.projekt.lesen import katalogname, wahl_von
from opencivil.projekt.staebe import MATERIAL_DES_QUERSCHNITTS
from opencivil.stabwerk.modell import Lastart
from opencivil.stabwerk import querschnitte as stabquerschnitte
from opencivil.stabwerk.rechnung import stoffkennwerte
from opencivil.web.balkendaten import Darstellung

#: Wie ein Diagramm heisst -- kurz im Schalter, lang ueber dem Diagramm --,
#: welches Feld der Proben es zeigt und zu welcher Achse des Stabs ein
#: positiver Wert aufgetragen wird: zur Faser, an der ein positives Moment
#: zieht, die Querkraft wie ihr Moment. Ohne Achse die, die im Bild laenger
#: ist -- bei N und T gibt es keine Seite.
_DIAGRAMME = {
    "M": ("M", "Moment M", "M", "z"),
    "V": ("V", "Querkraft V", "V", "z"),
    "N": ("N", "Normalkraft N", "N", None),
    "verdrehung": ("Verdrehung", "Verdrehung φ", "phi", "z"),
    "M_y": ("M_y", "Moment M_y", "M_y", "z"),
    "M_z": ("M_z", "Moment M_z", "M_z", "y"),
    "V_y": ("V_y", "Querkraft V_y", "V_y", "y"),
    "V_z": ("V_z", "Querkraft V_z", "V_z", "z"),
    "T": ("T", "Torsionsmoment T", "T", None),
    "verschiebung": ("Verschiebung", "Verschiebung", None, None),
    "lagerkraefte": ("Lager", "Lagerkräfte", None, None),
}

#: Wie ein Linienlager heisst -- im Fenster, kurz in der Liste, als Zeichen
#: seiner Bettung --, was sein Schalter erklaert und in welcher Achse des
#: Stabs es haelt: quer in der Ebene zur gestrichelten Faser, in z.
_LINIENLAGER = {
    "quer": ("Lager quer", "quer", "⊥",
             "Quer zur Linie, auf der Seite der gestrichelten Faser: fest – der Stab biegt "
             "sich nicht –, oder gebettet", "z"),
    "quer_y": ("Lager quer y", "quer y", "⊥y", "Quer zur Linie, in y des Stabs: fest oder gebettet", "y"),
    "quer_z": ("Lager quer z", "quer z", "⊥z",
               "Quer zur Linie, in z des Stabs – zur gestrichelten Faser: fest oder gebettet", "z"),
    "laengs": ("Lager längs", "längs", "∥", "Längs der Linie: fest oder gebettet", "x"),
}


def _zeichen(feld: str) -> str:
    """Wie eine Richtung eines Lagers heisst: ``x``, ``φ``, ``φ_y``."""
    return feld.replace("phi", "φ")


def _hat_feld(cls: type, feld: str) -> bool:
    return any(f.name == feld for f in dataclasses.fields(cls))


def _lastart(art: Lastart) -> Dict[str, Any]:
    """Eine Art einer Last auf einem Stab: wie sie heisst, ob sie verteilt liegt, ob sie eine Kraft ist, ihre Einheit."""
    return {"wert": art.value, "beschriftung": art.beschriftung, "verteilt": art.verteilt,
            "kraft": art.kraft, "einheit": EINHEIT_DER_LAST[art].beschriftung}


def katalog(eintrag: type, rechnung: type, darstellung: Darstellung) -> Dict[str, Any]:
    """
    Der Katalog einer Art von Balkensystem: ``eintrag`` ihre Beschreibung
    (eine :class:`~opencivil.projekt.staebe.MitStaeben`), ``rechnung`` die
    Klasse, die sie rechnet, ``darstellung`` wie ihre Ergebnisse gezeigt werden.
    """
    querschnittsarten = wahl_von(eintrag.QUERSCHNITT, "art")
    aus_bauteil = [a.value for a in querschnittsarten if a.aus_bauteil]
    return {
        "achsen": list(eintrag.ACHSEN),
        "laufrichtungen": [list(r) for r in eintrag.LAUFRICHTUNGEN],
        # Unter welchem Namen die Vorlagen und Feldangaben der Teile stehen.
        "klassen": {rolle: katalogname(getattr(eintrag, rolle.upper()))
                    for rolle in ("knoten", "linie", "lager", "stablast", "knotenlast",
                                  "material", "querschnitt", "diagramm")},
        "vorlagen": [
            {"schluessel": v.schluessel, "name": v.name,
             "masse": [m.als_dict() for m in v.masse],
             "skizze": [[[round(y, 1), round(z, 1)] for y, z in umriss]
                        for umriss in v.umriss(v.vorgaben())]}
            for v in stabquerschnitte.VORLAGEN
        ],
        # Um welche Achse sich ein Profil biegt -- nur in der Ebene; im Raum
        # dreht der Winkel β der Linie den Querschnitt.
        "profilachsen": ([{"wert": a.value, "beschriftung": a.kurz, "titel": a.beschriftung}
                          for a in wahl_von(eintrag.QUERSCHNITT, "achse")]
                         if _hat_feld(eintrag.QUERSCHNITT, "achse") else []),
        # Woher die Kennwerte eines Stabs kommen. Der kurze Name steht im
        # Schalter, der lange in seinem Titel; ob die Art ein Material
        # mitbringt, sagt, ob eine Linie es «gemäss Querschnitt» nehmen kann.
        "querschnittsarten": [
            {"wert": a.value, "beschriftung": a.beschriftung, "kurz": a.kurz,
             "bringt_material": a.aus_bauteil}
            for a in querschnittsarten
        ],
        # Die Kennwerte eines Querschnitts von Hand, wie die Rechnung sie nimmt.
        "kennwerte": [{"kurz": k.kurzname, "beschriftung": k.beschreibung,
                       "angabe": k.bereich.angabe()} for k in rechnung.KENNWERTE],
        # Je Art, aus der ein Stab sein kann -- Beton und Baustahl des
        # Projekts --, die Kennwerte, die er nimmt; die Tabelle der
        # Materialien zeigt sie gesperrt. Ein eigenes Material hat sie von Hand.
        "stabkennwerte": {art.value: dict(k) for art, k in
                          stoffkennwerte(rechnung.MATERIALKENNWERTE).items()},
        "materialkennwerte": [{"kurz": k.kurzname, "zeichen": k.symbol.replace(r"\rho", "ρ"),
                               "beschreibung": k.beschreibung}
                              for k in rechnung.MATERIALKENNWERTE],
        # Welches E ein Stab hat, der das Material seines Querschnitts
        # nimmt -- und bei welchen Arten: bei einem aus einem Bauteil.
        "e_module": [
            {"wert": "e0", "beschriftung": "E₀ = E_cm",
             "titel": "E_cm des Betons, den der Querschnitt mitbringt", "arten": aus_bauteil},
            {"wert": "e_eq", "beschriftung": "E_eq",
             "titel": "Der äquivalente E-Modul der Platte oder Querschnittsanalyse bei N und M",
             "arten": aus_bauteil},
        ],
        # Was als Material einer Linie heisst: das ihres Querschnitts.
        "material_des_querschnitts": MATERIAL_DES_QUERSCHNITTS,
        # Was ein Diagramm der Statik-Analyse zeigt -- kurz im Schalter,
        # lang ueber dem Diagramm, mit dem Feld der Proben und der Achse.
        "diagrammgroessen": [{"wert": wert, "beschriftung": _DIAGRAMME[wert][0],
                              "titel": _DIAGRAMME[wert][1], "feld": _DIAGRAMME[wert][2],
                              "achse": _DIAGRAMME[wert][3]}
                             for wert in wahl_von(eintrag.DIAGRAMM, "groesse")],
        "lastarten": [_lastart(a) for a in wahl_von(eintrag.STABLAST, "art")],
        # An einem Knoten wie dieselbe Last auf einem Stab, mit eigenem Namen.
        "knotenlastarten": [{**_lastart(a.auf_stab), "wert": a.value, "beschriftung": a.beschriftung,
                             "auf_stab": a.auf_stab.value}
                            for a in wahl_von(eintrag.KNOTENLAST, "art")],
        # Je Richtung einer Last: im System mit ihrem Vektor, sonst die
        # Achse des Stabs, in der sie liegt.
        "richtungen": [{"wert": r.value, "beschriftung": r.beschriftung,
                        "im_system": r.im_system, "stabachse": r.stabachse,
                        "vektor": list(r.systemvektor) if r.im_system else None}
                       for r in wahl_von(eintrag.STABLAST, "richtung")],
        "knotenrichtungen": [r.value for r in wahl_von(eintrag.KNOTENLAST, "richtung")],
        "halt": list(HALT),
        "lagerfelder": [{"feld": f, "zeichen": _zeichen(f)} for f in eintrag.LAGERFELDER],
        "lagerarten": [{"wert": art, **dict(zip(eintrag.LAGERFELDER, halt))}
                       for art, halt in eintrag.LAGERARTEN.items()],
        "linienlager": [dict(zip(("beschriftung", "kurz", "zeichen", "titel", "achse"), _LINIENLAGER[f]),
                             feld=f)
                        for f in eintrag.LINIENLAGER],
        # Wie die Ergebnisse heissen: Zeichen, Einheit, Stellen.
        "ergebnisse": darstellung.als_dict(),
    }
