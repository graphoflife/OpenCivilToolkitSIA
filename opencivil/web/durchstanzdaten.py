"""
opencivil/web/durchstanzdaten.py -- was die Oberflaeche von einer Durchstanzstelle zeichnet.

VERANTWORTUNG:
Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt --, und wo es sie braucht, die
Leisten mit ihren Ankern und dem äusseren Schnitt und der Stahlpilz mit seinen
Stegen und dem Schnitt um ihn, je für sich. Dazu die Legende unter dem Bild
(:mod:`opencivil.web.anzeige`): die Schnitte mit ihren Zahlen und das Urteil.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises (:mod:`opencivil.durchstanzen.nachweis`).

Für den Katalog die Wahlen der Maske (:func:`wahlen`): je Stellung ihre
Beschriftung, und welche Felder der Nachweis mit ihr liest -- die Masse je
Lage und Form, die Felder je Näherungsstufe und Lage, die von k_e. Die Maske
zeigt die Vereinigung, so baut sie die Regel nicht nach
(:func:`opencivil.durchstanzen.stelle.eingaben_fuer`).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from opencivil.core.einheiten import EINHEITSLOS, KN, MM, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.rechenwerk import Loesung
from opencivil.durchstanzen.flaeche import Lage, Stuetzenform
from opencivil.durchstanzen.nachweis import Durchstanzbefund
from opencivil.durchstanzen.schnitt import Nachweisschnitt
from opencivil.durchstanzen.stelle import KeArt, Naeherungsstufe, Plattenart, wirksame_stufe
from opencivil.projekt import Aufbau
from opencivil.web.anzeige import masszahl, punkte, urteil, zahl, zahlformel, zeile


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



def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]:
    """Was der Grundriss einer Stelle braucht -- ``None``, wenn ihr Nachweis nicht gelaufen ist."""
    nachweis = aufbau.feld("durchstanzen").get(kennung)
    befund: Optional[Durchstanzbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        return None
    urteile = [u for u in loesung.urteile if u.raum == nachweis.id]
    leisten, pilz = befund.leisten, befund.pilz
    return {
        "umriss": punkte(befund.umriss, MM),
        "raender": [{"punkt": punkte([p], MM)[0], "richtung": richtung}
                    for p, richtung in befund.raender],
        "aussparungen": [punkte(x, MM) for x in befund.aussparungen],
        "schnitt": _linien(befund.innen.schnitt),
        "d_v": zahl(befund.innen.d_v, MM),
        "leisten": None if leisten is None else {
            "leisten": [{"wurzel": punkte([l.wurzel], MM)[0],
                         "anker": punkte(l.anker(leisten.vorschlag.radien), MM)}
                        for l in leisten.vorschlag.leisten],
            "aussen": _linien(leisten.aussen.schnitt),
        },
        "pilz": None if pilz is None else {
            "umriss": punkte(pilz.umriss, MM),
            "stege": [punkte(steg, MM) for steg in pilz.pilz.stege()],
            "schnitt": _linien(pilz.pruefung.schnitt),
        },
        "legende": _legende(befund, urteile),
    }


def _linien(schnitt: Nachweisschnitt) -> list:
    """Die Stücke eines Schnitts fürs Bild, je mit der Angabe, ob es zählt."""
    return [{"punkte": punkte(l.punkte, MM), "zaehlt": l.zaehlt}
            for l in schnitt.massgebend.linien]


def _legende(befund: Durchstanzbefund, urteile) -> List[list]:
    """
    Die Zeilen unter dem Bild: der Schnitt und was von ihm nicht zählt; ohne
    Bewehrung der Vergleich mit seinem Urteil, sonst was ohne sie fehlt, der
    Pilz und die Leisten mit ihren Schnitten -- und das Urteil über alle.
    """
    innen, b, pilz = befund.innen, befund.leisten, befund.pilz
    erfuellt = all(u.erfuellt for u in urteile)
    grad = min(urteile, key=lambda u: u.erfuellungsgrad.si).gradtext(latex=True)
    zeilen = [
        zeile("Nachweisschnitt im Abstand ", zahlformel("d_v/2", innen.d_v / 2, MM, 0),
              " um die gestützte Fläche; wirksam ",
              Mathe(rf"u = k_e \cdot u_{{red}} = {masszahl(innen.u, MM, 0)}"), " mit ",
              zahlformel("k_e", innen.k_e, EINHEITSLOS, 2), "."),
        zeile("Gestrichelt, was nicht zählt: weiter als ", Mathe(r"1.5 \cdot d_v"),
              " von den Ecken grosser Stützen und entlang von Wänden, und was hinter "
              "Aussparungen liegt."),
    ]
    if b is None and pilz is None:
        zeilen.append(zeile(*urteil(f"V_d = {_kraft(innen.V_d_red)}", r"\le",
                                    f"V_{{Rd,c}} = {_kraft(befund.V_Rd_c)}", erfuellt, grad), "."))
        return zeilen
    zeilen.append(zeile("Ohne Bewehrung ",
                        Mathe(f"V_{{Rd,c}} = {_kraft(befund.V_Rd_c)} < V_d = {_kraft(innen.V_d_red)}"),
                        "."))
    if pilz is not None:
        zeilen += [
            zeile(f"Stahlpilz: {pilz.pilz.name}. Seine gestützte Fläche reicht bis an die Enden "
                  "der Stege; der Schnitt um sie (violett) liegt ",
                  zahlformel("d_{v,P}/2", pilz.pruefung.d_v / 2, MM, 0),
                  " weit aussen. Den Widerstand des Pilzes selbst bestätigt der Hersteller."),
            zeile("Um den Pilz ohne Bewehrung: ",
                  Mathe(f"V_{{d,P}} = {_kraft(pilz.pruefung.V_d_red)}"), ", ",
                  Mathe(f"V_{{Rd,c,P}} = {_kraft(pilz.V_Rd_c)}"), "."),
        ]
    if b is not None:
        v = b.vorschlag
        abstaende = r"\,/\,".join(Groesse.aus_si(x, MM).formatiert(0) for x in v.abstaende)
        zeilen += [
            zeile(f"Durchstanzbewehrung: {v.name}, Anker ",
                  Mathe(rf"\varnothing {Groesse.aus_si(v.typ.durchmesser, MM).formatiert(0)}"),
                  " im Abstand ", Mathe(rf"{abstaende}\,\mathrm{{mm}}"),
                  f" vom Rand {'des Pilzes' if pilz is not None else 'der Stütze'}."),
            zeile("Äusserer Schnitt (orange) im Abstand ",
                  zahlformel(r"0.5 \cdot d_{v,out}", b.aussen.d_v / 2, MM, 0),
                  " um die äussersten Anker: ", zahlformel("u_{out}", b.aussen.u, MM, 0), ", ",
                  Mathe(f"V_{{d,out}} = {_kraft(b.aussen.V_d_red)}"), ", ",
                  Mathe(f"V_{{Rd,c,out}} = {_kraft(b.V_Rd_c_aussen)}"), "."),
            zeile(Mathe(f"V_{{Rd,s}} = {_kraft(b.V_Rd_s)}"), ", ",
                  Mathe(f"V_{{Rd,max}} = {_kraft(b.V_Rd_max)}"), "."),
        ]
    zeilen.append(zeile(f"{'Alle Nachweise erfüllt' if erfuellt else 'Nicht alle Nachweise erfüllt'}"
                        ", kleinstes ", Mathe(rf"\alpha = {grad}"), "."))
    return zeilen


def _kraft(si_wert: float) -> str:
    """Eine Kraft der Legende: kN mit einer Stelle."""
    return masszahl(si_wert, KN, 1)
