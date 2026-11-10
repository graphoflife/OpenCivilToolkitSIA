"""
opencivil/web/durchstanzdaten.py -- was die Oberflaeche von einer Durchstanzstelle zeichnet.

VERANTWORTUNG:
Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt --, und wo es sie braucht, die
Leisten mit ihren Ankern und dem äusseren Schnitt und der Stahlpilz mit seinen
Stegen und dem Schnitt um ihn, je für sich. Dazu die Zahlen der Legende.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises (:mod:`opencivil.durchstanzen.nachweis`).

Für den Katalog die Wahlen der Maske (:func:`wahlen`): je Stellung ihre
Beschriftung, und welche Felder der Nachweis mit ihr liest -- die Masse je
Lage und Form, die Felder je Näherungsstufe und Lage, die von k_e. Die Maske
zeigt die Vereinigung, so baut sie die Regel nicht nach
(:func:`opencivil.durchstanzen.stelle.eingaben_fuer`).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from opencivil.core.rechenwerk import Loesung
from opencivil.durchstanzen.flaeche import Lage, Stuetzenform
from opencivil.durchstanzen.nachweis import Durchstanzbefund
from opencivil.durchstanzen.pruefung import Leistenpruefung, Pilzbefund
from opencivil.durchstanzen.schnitt import Nachweisschnitt
from opencivil.durchstanzen.stelle import KeArt, Naeherungsstufe, Plattenart, wirksame_stufe
from opencivil.projekt import Aufbau

mm = 1e3


def _punkte(punkte) -> list:
    return [[p[0] * mm, p[1] * mm] for p in punkte]


def wahlen() -> Dict[str, Any]:
    """
    Die Schalter einer Durchstanzstelle mit ihren Stellungen -- und je Lage
    ihre Art: wie die Maske ihre Masse überschreibt, ob sie eine Form hat,
    welche Masse sie je Form liest, was die Liste von ihr zeigt und welche
    Felder jede Näherungsstufe an ihr liest.
    """
    def stellungen(wahl) -> list:
        return [{"wert": w.value, "beschriftung": w.beschriftung} for w in wahl]

    def lage(l: Lage) -> Dict[str, Any]:
        arten = {form: l.flaeche(form) for form in Stuetzenform}
        # Titel, Form und Stufen hängen an der Lage, nicht an der Form.
        art = arten[Stuetzenform.RECHTECK]
        return {
            "wert": l.value, "beschriftung": l.beschriftung, "titel": art.titel,
            "hat_form": art.hat_form,
            "masse": {form.value: list(a.masse) for form, a in arten.items()},
            "kurz": {form.value: a.kurz for form, a in arten.items()},
            "stufen": {st.value: list(wirksame_stufe(art, st).eingaben) for st in Naeherungsstufe},
        }

    return {
        "plattenarten": stellungen(Plattenart),
        "lagen": [lage(l) for l in Lage],
        "formen": stellungen(Stuetzenform),
        "stufen": stellungen(Naeherungsstufe),
        "ke": [{"wert": k.value, "beschriftung": k.beschriftung, "eingaben": list(k.eingaben)}
               for k in KeArt],
    }


def situationen(aufbau: Aufbau, loesung: Loesung) -> Dict[str, Any]:
    """Je Durchstanzstelle, nach Kennung, was die Zeichnung vom Kern braucht."""
    return {kennung: situation(aufbau, kennung, loesung)
            for kennung in aufbau.objekte("durchstanzen")}


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]:
    """Was der Grundriss einer Stelle braucht -- ``None``, wenn ihr Nachweis nicht gelaufen ist."""
    nachweis = aufbau.feld("durchstanzen").get(kennung)
    befund: Optional[Durchstanzbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        return None
    innen = befund.innen
    urteile = [u for u in loesung.urteile if u.raum == nachweis.id]
    massgebend = min(urteile, key=lambda u: u.erfuellungsgrad.si)
    return {
        "umriss": _punkte(befund.umriss),
        "raender": [{"punkt": [p[0] * mm, p[1] * mm], "richtung": richtung}
                    for p, richtung in befund.raender],
        "aussparungen": [_punkte(x) for x in befund.aussparungen],
        "schnitt": _linien(innen.schnitt),
        "d_v": innen.d_v * mm,
        "u": innen.u * mm,
        "k_e": innen.k_e,
        "psi": befund.psi,
        "V_d": innen.V_d_red / 1e3,
        "V_Rd_c": befund.V_Rd_c / 1e3,
        "erfuellt": all(u.erfuellt for u in urteile),
        "grad": massgebend.gradtext(),
        "leisten": _leisten(befund.leisten),
        "pilz": _pilz(befund.pilz),
    }


def _linien(schnitt: Nachweisschnitt) -> list:
    """Die Stücke eines Schnitts fürs Bild, je mit der Angabe, ob es zählt."""
    return [{"punkte": _punkte(l.punkte), "zaehlt": l.zaehlt} for l in schnitt.massgebend.linien]


def _leisten(b: Optional[Leistenpruefung]) -> Optional[Dict[str, Any]]:
    """Die Leisten mit ihren Ankern, der äussere Schnitt um sie und ihre Zahlen -- in mm, kN."""
    if b is None:
        return None
    v = b.vorschlag
    return {
        "name": v.name,
        "durchmesser": v.typ.durchmesser * mm,
        "leisten": [{"wurzel": _punkte([l.wurzel])[0], "anker": _punkte(l.anker(v.radien))}
                    for l in v.leisten],
        "abstaende": [x * mm for x in v.abstaende],
        "aussen": _linien(b.aussen.schnitt),
        "d_v_out": b.aussen.d_v * mm,
        "u_out": b.aussen.u * mm,
        "V_Rd_s": b.V_Rd_s / 1e3,
        "V_Rd_max": b.V_Rd_max / 1e3,
        "V_d_out": b.aussen.V_d_red / 1e3,
        "V_Rd_c_out": b.V_Rd_c_aussen / 1e3,
    }


def _pilz(b: Optional[Pilzbefund]) -> Optional[Dict[str, Any]]:
    """Der Stahlpilz mit seinen Stegen, seiner Fläche und dem Schnitt um sie -- in mm, kN."""
    if b is None:
        return None
    return {
        "name": b.pilz.name,
        "umriss": _punkte(b.umriss),
        "stege": [_punkte(steg) for steg in b.pilz.stege()],
        "schnitt": _linien(b.pruefung.schnitt),
        "d_v": b.pruefung.d_v * mm,
        "V_d": b.pruefung.V_d_red / 1e3,
        "V_Rd_c": b.V_Rd_c / 1e3,
    }
