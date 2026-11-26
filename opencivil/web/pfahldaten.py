"""
opencivil/web/pfahldaten.py -- was die Oberflaeche von einem Pfahl zeichnet.

VERANTWORTUNG:
Je Pfahl die Zahlen der Situationszeichnung, in den Einheiten der Anzeige:
die Mantelreibung je Stück und der Spitzendruck, wie der äussere Widerstand
sie gerechnet hat, mit ihren Grössen (:data:`SITUATION`). Dazu die Legende unter dem Bild
(:mod:`opencivil.web.anzeige`): Mantel und Fuss, die Bemessungswerte beider
Nachweise auf Druck und auf Zug, quer je Kombination, und der Fall, der
entscheidet. Masse, Schichten und Grundwasser liest die Oberflaeche aus dem
Eintrag.

Dazu das Bild des Querschnitts (:func:`querschnitt`), auch ohne
Kombination: seine Masse in mm, mit r_s und dem Durchmesser nach der
Abrostung aus denselben Funktionen wie im Nachweis.

Und je Kombination die Verläufe über die Tiefe, wie die Steifigkeit sie
gerechnet hat (:func:`verlaeufe`), mit dem Satz, der unter ihnen steht --
neben Moment und Querkraft der Widerstand des Pfahls, neben dem
Bettungsdruck der Erdwiderstand: die Grenzen, die sie nicht übersteigen
dürfen. Jede Grösse bringt Zeichen, Einheit und Stellen mit
(:data:`VERLAEUFE`); das Bild schreibt keine davon selbst.

Gerechnet wird hier nichts: alles steht in den Befunden.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from opencivil.core.einheiten import KN, KNM, KPA, MM, MRAD
from opencivil.core.latex import Mathe, fest
from opencivil.core.rechenwerk import Loesung
from opencivil.pfahl.aussen import Aussenbefund
from opencivil.pfahl.innen import Innenbefund, bewehrungsradius, nach_abrostung
from opencivil.pfahl.innen_quer import Innenquerbefund
from opencivil.pfahl.pfahl import Pfahl, Pfahlart, Tragglied
from opencivil.pfahl.quer import Querbefund
from opencivil.pfahl.steifigkeit import GAMMA_E, Pfahlsteifigkeit, Steifigkeitsbefund, Verlauf
from opencivil.projekt import Aufbau
from opencivil.web.anzeige import Anzeigegroesse, zahl, zahlformel, zeile

#: Die Verläufe über die Tiefe, in der Folge der Bilder: Feld des Befunds und
#: Grösse der Anzeige. Eine Grenze steht in derselben Einheit wie ihr Verlauf.
VERLAEUFE = (
    ("N", Anzeigegroesse("N", KN, stellen=0)),
    ("w", Anzeigegroesse("w", MM, stellen=2)),
    ("y", Anzeigegroesse("y", MM, stellen=2)),
    ("theta", Anzeigegroesse("θ", MRAD, r"\theta", 2)),
    ("M", Anzeigegroesse("M", KNM)),
    ("V", Anzeigegroesse("V", KN)),
    ("p", Anzeigegroesse("p", KPA, stellen=0)),
)

#: Was die Situationszeichnung aus der Lösung anschreibt.
SITUATION = {"q_s": Anzeigegroesse("q_s,k", KPA, "q_{s,k}"),
             "q_b": Anzeigegroesse("q_b,k", KPA, "q_{b,k}", 0)}


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Dict[str, Any]:
    """
    Was die Zeichnung eines Pfahls braucht. Ohne Kombination gibt es keinen
    Nachweis und keinen Befund -- dann zeichnet sie nur den Pfahl im Boden.
    """
    schnitt = querschnitt(aufbau.bauteil(kennung).objekt)
    nachweise = [aufbau.feld(f).get(kennung) for f in ("pfahl_aussen", "pfahl_innen")]
    if any(n is None for n in nachweise):
        return {"stuecke": [], "q_b": None, "querschnitt": schnitt,
                "legende": [zeile("Ohne Kombination kein Nachweis.")]}
    aussen: Optional[Aussenbefund] = loesung.befunde.get(nachweise[0].id)
    innen: Optional[Innenbefund] = loesung.befunde.get(nachweise[1].id)
    if aussen is None or innen is None:
        return {"stuecke": [], "q_b": None, "querschnitt": schnitt,
                "legende": [zeile("Nicht gerechnet.")]}
    quer = [aufbau.feld(f).get(kennung) for f in ("pfahl_quer", "pfahl_innen_quer")]
    raeume = {n.id for n in [*nachweise, *quer] if n is not None}
    urteile = [u for u in loesung.urteile if u.raum in raeume and not u.still]
    return {
        "stuecke": [{"z_o": s.stueck.z_o, "z_u": s.stueck.z_u, "q_s": SITUATION["q_s"].zahl(s.q_s)}
                    for s in aussen.stuecke],
        "q_b": SITUATION["q_b"].zahl(aussen.q_b),
        "querschnitt": schnitt,
        "groessen": {feld: g.als_dict() for feld, g in SITUATION.items()},
        "legende": _legende(aussen, innen, _befund(aufbau, kennung, loesung, "pfahl_quer"),
                            urteile),
        **verlaeufe(aufbau, kennung, loesung),
    }


def querschnitt(pfahl: Pfahl) -> Dict[str, Any]:
    """
    Was das Bild des Querschnitts braucht, in mm: beim Bohrpfahl
    Durchmesser, Laengsstaebe, Wendel und der Radius r_s ihrer Mitten, beim
    Mikropfahl Verpresskoerper und Tragglied -- ``t`` ``None`` beim
    Vollstab -- mit dem Durchmesser nach der Abrostung. Dazu die Legende.
    """
    p = pfahl
    masse = "Masse in mm, massstäblich."
    if p.art is Pfahlart.BOHRPFAHL:
        beton = p.beton.name if p.beton is not None else "–"
        return {"art": "bohrpfahl", "D": zahl(p.D.si, MM), "n": round(p.n.si),
                "phi_l": zahl(p.phi_l.si, MM), "c": zahl(p.c.si, MM),
                "phi_w": zahl(p.phi_w.si, MM), "s_w": zahl(p.s_w.si, MM),
                "r_s": zahl(bewehrungsradius(p.D.si, p.c.si, p.phi_w.si, p.phi_l.si), MM),
                "legende": [zeile(f"Beton {beton}, Längsbewehrung {p.stahl.name}."), zeile(masse)]}
    rohr = p.tragglied is Tragglied.ROHR
    tragglied = f"Es trägt nur das Tragglied aus {p.stahl.name}"
    if p.dt.si > 0:
        stahl = zeile(f"{tragglied}, aussen um die Abrostung ",
                      zahlformel(r"\Delta t", p.dt.si, MM, 1),
                      " verkleinert: gestrichelt (SIA 267:2013, 9.5.2.4.8).")
    else:
        stahl = zeile(f"{tragglied}; ohne Abrostung, ", Mathe(r"\Delta t = 0"), ".")
    return {"art": "mikropfahl", "D": zahl(p.D.si, MM), "d_a": zahl(p.d_a.si, MM),
            "t": zahl(p.t_r.si, MM) if rohr else None, "dt": zahl(p.dt.si, MM),
            "d_rest": zahl(nach_abrostung(p.d_a.si, p.dt.si), MM),
            "legende": [stahl, zeile(masse)]}


def _befund(aufbau: Aufbau, kennung: str, loesung: Loesung, feld: str) -> Optional[Any]:
    """Der Befund des Nachweises in ``feld`` -- ``None``, wo es ihn nicht gibt."""
    nachweis = aufbau.feld(feld).get(kennung)
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
    aussen: Optional[Querbefund] = _befund(aufbau, kennung, loesung, "pfahl_quer")
    innen: Optional[Innenquerbefund] = _befund(aufbau, kennung, loesung, "pfahl_innen_quer")
    kopf = "eingespannt" if befund.eingespannt else "frei drehbar"
    legende = [
        zeile("Tragsicherheit, mit ", Mathe(rf"E_{{s,d}} = E_{{s,k}} / {fest(GAMMA_E, 1)}"),
              f"; der Kopf {kopf}. Die Tiefe z ab Terrain, die Querkraft H",
              " in Richtung von y, das Moment dreht wie H über dem Kopf."),
    ]
    if aussen is not None and innen is not None:
        legende.append(zeile("Gestrichelt, so weit sie ins Bild fallen, die Grenzen: neben M "
                             "und V der Widerstand des Pfahls mit der Normalkraft in derselben "
                             "Tiefe, neben p der Erdwiderstand ", Mathe(r"p_{E,d} / D"), "."))
    return {"verlaeufe": [_verlauf(v, aussen, innen) for v in befund.verlaeufe],
            "verlaufslegende": legende}


def _verlauf(v: Verlauf, aussen: Optional[Querbefund],
             innen: Optional[Innenquerbefund]) -> Dict[str, Any]:
    """
    Eine Kombination: die Tiefen und je gerechnete Grösse ihre Werte, mit der
    Grenze, wo es eine gibt (sonst ``None``).
    """
    grenzen = _grenzen(v.name, aussen, innen)
    return {"name": v.name, "z": v.z, "groessen": [
        {"feld": feld, **g.als_dict(), "werte": [g.zahl(x) for x in getattr(v, feld)],
         "grenze": [g.zahl(x) for x in grenzen[feld]] if feld in grenzen else None}
        for feld, g in VERLAEUFE if getattr(v, feld) is not None]}


def _grenzen(name: str, aussen: Optional[Querbefund],
             innen: Optional[Innenquerbefund]) -> Dict[str, List[float]]:
    """Die Grenzen einer Kombination neben M, V und p, in SI -- leer, wo sie nicht quer belastet."""
    heraus = {}
    if aussen is not None and name in aussen.faelle:
        heraus["p"] = aussen.faelle[name].grenze
    if innen is not None and name in innen.faelle:
        fall = innen.faelle[name]
        heraus["M"], heraus["V"] = fall.M_grenze, fall.V_grenze
    return heraus


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
