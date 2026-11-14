"""
opencivil/web/pfahldaten.py -- was die Oberflaeche von einem Pfahl zeichnet.

VERANTWORTUNG:
Je Pfahl die Zahlen der Situationszeichnung, in den Einheiten der Anzeige:
die Mantelreibung je Stück und der Spitzendruck, wie der äussere Widerstand
sie gerechnet hat. Dazu die Legende unter dem Bild
(:mod:`opencivil.web.anzeige`): Mantel und Fuss, die Bemessungswerte beider
Nachweise auf Druck und auf Zug, quer je Kombination, und der Fall, der
entscheidet. Masse, Schichten und Grundwasser liest die Oberflaeche aus dem
Eintrag.

Und je Kombination die Verläufe über die Tiefe, wie die Steifigkeit sie
gerechnet hat (:func:`verlaeufe`), mit dem Satz, der unter ihnen steht --
neben dem Bettungsdruck der Erdwiderstand, den er nicht übersteigen darf.

Gerechnet wird hier nichts: alles steht in den Befunden.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from opencivil.core.einheiten import KN, KNM, KPA, MM, MRAD
from opencivil.core.latex import Mathe, fest
from opencivil.core.rechenwerk import Loesung
from opencivil.pfahl.aussen import Aussenbefund
from opencivil.pfahl.innen import Innenbefund
from opencivil.pfahl.quer import Querbefund
from opencivil.pfahl.steifigkeit import GAMMA_E, Pfahlsteifigkeit, Steifigkeitsbefund
from opencivil.projekt import Aufbau
from opencivil.web.anzeige import zahl, zahlformel, zeile

#: Die Verläufe über die Tiefe: Feld des Befunds und Einheit der Anzeige.
VERLAEUFE = (("N", KN), ("w", MM), ("y", MM), ("theta", MRAD), ("M", KNM), ("V", KN),
             ("p", KPA))


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Pfahls braucht. Ohne Kombination gibt es keinen
    Nachweis und keinen Befund -- dann zeichnet sie nur den Pfahl im Boden.
    """
    nachweise = [aufbau.feld(f).get(kennung) for f in ("pfahl_aussen", "pfahl_innen")]
    if any(n is None for n in nachweise):
        return {"stuecke": [], "q_b": None,
                "legende": [zeile("Ohne Kombination kein Nachweis.")]}
    aussen: Optional[Aussenbefund] = loesung.befunde.get(nachweise[0].id)
    innen: Optional[Innenbefund] = loesung.befunde.get(nachweise[1].id)
    if aussen is None or innen is None:
        return {"stuecke": [], "q_b": None, "legende": [zeile("Nicht gerechnet.")]}
    quer = aufbau.feld("pfahl_quer").get(kennung)
    raeume = {n.id for n in [*nachweise, quer] if n is not None}
    urteile = [u for u in loesung.urteile if u.raum in raeume and not u.still]
    return {
        "stuecke": [{"z_o": s.stueck.z_o, "z_u": s.stueck.z_u, "q_s": zahl(s.q_s, KPA)}
                    for s in aussen.stuecke],
        "q_b": zahl(aussen.q_b, KPA),
        "legende": _legende(aussen, innen, _querbefund(aufbau, kennung, loesung), urteile),
        **verlaeufe(aufbau, kennung, loesung),
    }


def _querbefund(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Querbefund]:
    """Was der äussere Widerstand quer ergab -- ``None``, wo keine Kombination quer belastet."""
    nachweis = aufbau.feld("pfahl_quer").get(kennung)
    return loesung.befunde.get(nachweis.id) if nachweis is not None else None


def verlaeufe(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Je Kombination Setzung, Normalkraft und -- wo quer gerechnet ist --
    Verschiebung, Verdrehung, Moment, Querkraft und Bettungsdruck über die
    Tiefe ab Terrain, dazu der Satz darunter. Leer ohne Steifigkeit.
    """
    befund: Optional[Steifigkeitsbefund] = loesung.befunde.get(
        Pfahlsteifigkeit.kennung(aufbau.bauteil(kennung).objekt))
    if befund is None:
        return {"verlaeufe": [], "verlaufslegende": []}
    quer = _querbefund(aufbau, kennung, loesung)
    faelle = quer.faelle if quer is not None else {}
    kopf = "eingespannt" if befund.eingespannt else "frei drehbar"
    legende = [
        zeile("Tragsicherheit, mit ", Mathe(rf"E_{{s,d}} = E_{{s,k}} / {fest(GAMMA_E, 1)}"),
              f"; der Kopf {kopf}. Die Tiefe z ab Terrain, die Querkraft H",
              " in Richtung von y, das Moment dreht wie H über dem Kopf."),
    ]
    if faelle:
        legende.append(zeile("Neben p gestrichelt der Erdwiderstand ",
                             Mathe(r"p_{E,d} / D"), ", den der Bettungsdruck nirgends "
                             "übersteigen darf -- so weit er ins Bild fällt."))
    return {
        "verlaeufe": [{"name": v.name, "z": v.z,
                       **{feld: [zahl(x, einheit) for x in getattr(v, feld)]
                          for feld, einheit in VERLAEUFE if getattr(v, feld) is not None},
                       **({"p_grenze": [zahl(x, KPA) for x in faelle[v.name].grenze]}
                          if v.name in faelle else {})}
                      for v in befund.verlaeufe],
        "verlaufslegende": legende,
    }


def _legende(aussen: Aussenbefund, innen: Innenbefund, quer: Optional[Querbefund],
             urteile: List[Any]) -> List[list]:
    """Mantel und Fuss, die Bemessungswerte, quer je Kombination, der entscheidende Fall."""
    kn = lambda zeichen, si: zahlformel(zeichen, si, KN, 0)
    if aussen.aus_versuch:
        herkunft = zeile("Aus dem Versuch ", kn("R_{a,k}", aussen.R_ak), " auf Druck und ",
                         kn("R_{a,k,Z}", aussen.R_ak_zug), " auf Zug.")
    else:
        herkunft = zeile("Mantel ", kn("R_{s,k}", aussen.R_s), " und Fuss ",
                         kn("R_{b,k}", aussen.R_b), ": ", kn("R_{a,k}", aussen.R_ak),
                         ". Rechts der Achse die Mantelreibung ", Mathe("q_{s,k}"),
                         " je Stück, unten der Spitzendruck ", Mathe("q_{b,k}"), ".")
    zeilen = [
        herkunft,
        zeile("Auf Druck ", kn("R_{a,d}", aussen.R_ad), " und ", kn("R_{i,d}", innen.R_id),
              ", auf Zug ", kn("R_{a,d,Z}", aussen.R_ad_zug), " und ",
              kn("R_{i,d,Z}", innen.R_id_zug), "."),
    ]
    mit_querkraft = [(name, f) for name, f in (quer.faelle.items() if quer else ())
                     if f.R_trd is not None]
    if mit_querkraft:
        teile: List[Any] = []
        for name, f in mit_querkraft:
            teile += ["; " if teile else "Quer, ", f"in «{name}» ", kn("R_{tr,d}", f.R_trd),
                      f" ({f.bruch.was})"]
        zeilen.append(zeile(*teile, "."))
    if urteile:
        u = min(urteile, key=lambda x: x.erfuellungsgrad.si)
        zeilen.append(zeile(f"Massgebend: {u.langname}, {u.fall} – "
                            f"{'erfüllt' if u.erfuellt else 'nicht erfüllt'}, ",
                            Mathe(rf"\alpha = {u.gradtext(latex=True)}"), "."))
    return zeilen
