"""
opencivil/web/durchstanzdaten.py -- was die Oberflaeche von einer Durchstanzstelle zeichnet.

VERANTWORTUNG:
Je Durchstanzstelle der Grundriss, wie der Kern ihn gerechnet hat, in mm:
der Umriss der gestützten Fläche, die Plattenränder, die Aussparungen und
der Nachweisschnitt -- je Stück, ob es zählt --, und wo es sie braucht, die
Leisten mit ihren Ankern und dem äusseren Schnitt und der Stahlpilz mit seinen
Stegen und dem Schnitt um ihn, je für sich. Die Plattenbereiche mit ihrer
Dicke, an jeder Stufe ihr Schnitt, je in seiner Farbe (:data:`STUFENFARBEN`),
und wo er ohne sie nicht hält, die Leisten an ihr; dazu der Schnitt durch
verschiedene Dicken. Dazu die Legende unter dem Bild
(:mod:`opencivil.web.anzeige`): die Schnitte mit ihren Zahlen und das Urteil.
Gezeichnet wird in der Oberflaeche, gerechnet nichts: die Linien kommen aus
dem Befund des Nachweises (:mod:`opencivil.durchstanzen.nachweis`).

Wo es an der Stütze Durchstanzbewehrung braucht, auch eine Leiste in der Ansicht
(:func:`_ansicht`): längs geschnitten, mit Platte, Zugbewehrung, Stütze und
Pilz, den Elementen und dem Bereich, in dem sie zählen -- in mm, x ab dem
Rand der gestützten Fläche, z ab der Druckseite.

Für den Katalog die Wahlen der Maske (:func:`wahlen`): je Stellung ihre
Beschriftung, und welche Felder der Nachweis mit ihr liest -- die festen, die
Masse je Lage und Form, die Felder je Näherungsstufe und Lage, die von k_e.
Die Maske zeigt die Vereinigung, so baut sie die Regel nicht nach
(:func:`opencivil.durchstanzen.stelle.eingaben_fuer`). Dazu die beiden
Seiten, auf denen die Stufe eines Plattenbereichs liegen kann, und wie die
Kennungen der Polygone im Grundriss beginnen.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from opencivil.core.einheiten import EINHEITSLOS, KN, MM, Groesse
from opencivil.core.latex import Mathe
from opencivil.core.nachweis import OHNE_EINWIRKUNG, NachweisUrteil
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.durchstanzen import weg
from opencivil.durchstanzen.bereiche import Plattenbereich, Seite
from opencivil.durchstanzen.bewehrung import BEREICH_VON, Leiste
from opencivil.durchstanzen.flaeche import Lage, Stuetzenform
from opencivil.durchstanzen.mit_bewehrung import Platz
from opencivil.durchstanzen.nachweis import Durchstanzbefund, Stufenbefund
from opencivil.durchstanzen.pruefung import Leistenpruefung
from opencivil.durchstanzen.schnitt import Nachweisschnitt, Punkt
from opencivil.durchstanzen.stelle import (
    NACH_DEN_MASSEN, VOR_DEN_MASSEN, Durchstanzstelle, KeArt, Naeherungsstufe, Plattenart,
    wirksame_stufe,
)
from opencivil.durchstanzen.systeme import Durchstanzsystem
from opencivil.querschnitt.platte import Richtung
from opencivil.projekt import Aufbau
from opencivil.projekt.durchstanzen import VORSILBEN
from opencivil.web.anzeige import masszahl, punkte, urteil, zahl, zahlformel, zeile

#: Die Farben der Schnitte an den Stufen, der Reihe nach -- im Bild die Klassen
#: «ds-stufe-0» bis «ds-stufe-2» (web/css/80-skizzen.css).
STUFENFARBEN = ("grün", "türkis", "braun")

#: Die Farbe des Schnitts durch verschiedene Dicken -- im Bild «ds-weg».
WEGFARBE = "blau"


def wahlen() -> Dict[str, Any]:
    """
    Die Schalter einer Durchstanzstelle mit ihren Stellungen -- und je Lage
    ihre Art: wie die Maske ihre Masse überschreibt, ob sie eine Form hat,
    welche Masse sie je Form liest, was die Liste von ihr zeigt und welche
    Felder jede Näherungsstufe an ihr liest. Dazu, was der Nachweis an jeder
    Stelle liest (``fest``).
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
        "plattenarten": [{**s, "umgeschaltet": w.umgeschaltet}
                         for w, s in zip(Plattenart, stellungen(Plattenart))],
        "fest": [*VOR_DEN_MASSEN, *NACH_DEN_MASSEN],
        "lagen": [lage(l) for l in Lage],
        "formen": stellungen(Stuetzenform),
        "stufen": stellungen(Naeherungsstufe),
        "systeme": stellungen(Durchstanzsystem),
        "ke": [{"wert": k.value, "beschriftung": k.beschriftung, "eingaben": list(k.eingaben)}
               for k in KeArt],
        "seiten": [{"wert": s.value, "beschriftung": s.beschriftung,
                    "titel": f"{s.titel} ({s.figur})"} for s in Seite],
        "vorsilben": VORSILBEN,
    }


def situation(aufbau: Aufbau, kennung: str, loesung: Loesung) -> Optional[Dict[str, Any]]:
    """Was der Grundriss einer Stelle braucht -- ``None``, wenn ihr Nachweis nicht gelaufen ist."""
    nachweis = aufbau.feld("durchstanzen").get(kennung)
    befund: Optional[Durchstanzbefund] = (
        loesung.befunde.get(nachweis.id) if nachweis is not None else None)
    if befund is None:
        return None
    urteile = [u for u in loesung.urteile if u.raum == nachweis.id]
    pilz = befund.pilz
    return {
        "umriss": punkte(befund.umriss, MM),
        "raender": [{"punkt": punkte([p], MM)[0], "richtung": richtung}
                    for p, richtung in befund.raender],
        "aussparungen": [punkte(x, MM) for x in befund.aussparungen],
        "schnitt": _linien(befund.innen.schnitt),
        "d_v": zahl(befund.innen.d_v, MM),
        "leisten": _leisten(befund.leisten),
        "pilz": None if pilz is None else {
            "umriss": punkte(pilz.umriss, MM),
            "stege": [punkte(steg, MM) for steg in pilz.pilz.stege()],
            "schnitt": _linien(pilz.pruefung.schnitt),
        },
        "bereiche": [{"name": b.name, "punkte": punkte(b.ecken, MM), "h": zahl(b.h, MM),
                      "seite": b.seite.value} for b in nachweis.stelle.bereiche],
        "stufen": [{"name": x.stufe.bereich.name, "farbe": i % len(STUFENFARBEN),
                    "schnitt": _linien(x.stufe.pruefung.schnitt), "leisten": _leisten(x.leisten)}
                   for i, x in enumerate(_mit_schnitt(befund))],
        "weg": [] if befund.weg is None else _linien(befund.weg.schnitt.last.schnitt),
        "ansicht": (None if befund.leisten is None
                    else _ansicht(befund, nachweis.stelle, loesung.werte)),
        "legende": _legende(befund, urteile, nachweis.stelle.bereiche),
    }


def _leisten(pruefung: Optional[Leistenpruefung]) -> Optional[Dict[str, Any]]:
    """Eine Durchstanzbewehrung im Grundriss: je Leiste Ansatz und Anker, der äussere Schnitt."""
    if pruefung is None:
        return None
    v = pruefung.vorschlag
    return {"leisten": [{"wurzel": punkte([l.wurzel], MM)[0],
                         "anker": punkte(l.anker(v.radien), MM)} for l in v.leisten],
            "aussen": _linien(pruefung.aussen.schnitt)}


def _mit_schnitt(befund: Durchstanzbefund) -> List[Stufenbefund]:
    """Die Stufen, die einen eigenen Schnitt haben -- in der Reihe ihrer Farben."""
    return [x for x in befund.stufen if x.stufe.pruefung is not None]


def _ansicht(befund: Durchstanzbefund, stelle: Durchstanzstelle,
             werte: Dict[str, Wert]) -> Dict[str, Any]:
    """
    Eine Leiste in der Ansicht, längs geschnitten: die mit den meisten
    Elementen, unter ihnen die, die am ehesten nach rechts läuft. Die Stütze
    steht, wo die Linie der Leiste ihren Rand trifft -- mit einem Stahlpilz
    vor dem Rand der gestützten Fläche --, ihre Achse, wo die Linie ihr am
    nächsten kommt. Eine Lage der Zugbewehrung läuft «längs», wenn sie eher
    in Richtung der Leiste liegt; die andere steht im Bild als Punkte. Steht
    die Leiste in einem Plattenbereich, ist ``h`` seine Dicke, und rechts
    kommt seine Stufe ins Bild, wo sie nahe genug liegt (:func:`_stufe`).
    """
    b, platz = befund.leisten, befund.platz
    v, system = b.vorschlag, b.vorschlag.system
    leiste = max(v.leisten, key=lambda l: (len(l.anker(v.radien)), l.richtung[0]))
    radien = v.radien[:len(leiste.anker(v.radien))]
    (wx, wy), (ux, uy) = leiste.wurzel, leiste.richtung
    eingabe = {n: zahl(werte[stelle.id_von(n)].groesse.si, MM) for n in ("c", "c_v")}
    h = platz.h.groesse.si
    nach_x = abs(ux) >= abs(uy)
    d_v = b.innen.d_v
    stufe = _stufe(platz, leiste, werte[stelle.id_von("h")].groesse.si,
                   max(radien[-1], d_v) + h)
    zeilen = [
        zeile(f"Die {system.LEISTE} mit den meisten {system.ELEMENTEN}, längs geschnitten, "
              f"massstäblich bis auf die {system.ENDEN}: {system.ELEMENT} ",
              Mathe(rf"\varnothing {Groesse.aus_si(v.typ.durchmesser, MM).formatiert(0)}"),
              f" aus {system.STAHL}, ", zahlformel("h_A", v.h_A, MM, 0), "."),
        zeile("Hinterlegt, wo sie zählen: von ", zahlformel(rf"{BEREICH_VON:g} \cdot d_v",
                                                            BEREICH_VON * d_v, MM, 0),
              " bis ", zahlformel("d_v", d_v, MM, 0),
              f" vom Rand der gestützten Fläche – {v.anrechenbar} je {system.LEISTE} "
              f"(Gleichung (68))."),
    ]
    if befund.pilz is not None:
        zeilen.append(zeile(f"Links der Stahlpilz {befund.pilz.pilz.name}: an ihm setzen die "
                            f"{system.LEISTEN} an."))
    if platz.innerhalb:
        bereich = platz.innerhalb[0]
        wo = (f"rechts seine Stufe, dahinter {stufe['h']:.0f} mm" if stufe is not None
              else "seine Stufe liegt weiter draussen")
        zeilen.append(zeile(f"Die {system.LEISTE} steht in {bereich.titel}, {_mm(h)} mm dick; "
                            f"{wo}. Von der Stufe bleibt sie c_nom weg."))
    return {
        "form": system.FORM, "druckseite": stelle.plattenart.druckseite,
        **eingabe, "h": zahl(h, MM), "stufe": stufe,
        "h_A": zahl(v.h_A, MM), "durchmesser": zahl(v.typ.durchmesser, MM),
        "radien": [zahl(r, MM) for r in radien],
        "zaehlt": [zahl(BEREICH_VON * d_v, MM), zahl(d_v, MM)],
        "lagen": [{"tiefe": zahl(l.tiefe, MM), "durchmesser": zahl(l.durchmesser, MM),
                   "abstand": zahl(l.abstand, MM), "laengs": (l.richtung is Richtung.X) == nach_x}
                  for l in befund.lagen],
        "stuetze": {"rand": zahl(-_bis_zum_umriss((wx, wy), (-ux, -uy), befund.umriss), MM),
                    "achse": zahl(-(wx * ux + wy * uy), MM)},
        "pilz": None if befund.pilz is None else {"hoehe": zahl(befund.pilz.pilz.h, MM)},
        "legende": zeilen,
    }


def _stufe(platz: Platz, leiste: Leiste, h_platte: float,
           sichtbar: float) -> Optional[Dict[str, Any]]:
    """
    Die Stufe des Bereichs, in dem die Leiste steht, in mm: wie weit sie
    längs der Leiste vom Rand der gestützten Fläche liegt, wie dick die
    Platte dahinter ist und um wie viel Druck- und Zugseite dort
    zurückspringen -- die Seite des Bereichs (Figur 24a, 24c). ``None``, wo
    die Leiste in keinem Bereich steht oder die Stufe weiter als
    ``sichtbar`` (m) liegt. Nur fürs Bild.
    """
    if not platz.innerhalb:
        return None
    bereich = platz.innerhalb[0]
    x = _bis_zum_umriss(leiste.wurzel, leiste.richtung, bereich.ecken)
    if x > sichtbar:
        return None
    h = h_platte if platz.jenseits is None else platz.jenseits.h
    mehr = bereich.h - h
    druck = mehr if bereich.seite is Seite.STUETZE else 0.0
    return {"x": zahl(x, MM), "h": zahl(h, MM), "druck": zahl(druck, MM),
            "zug": zahl(mehr - druck, MM)}


def _mm(laenge: float) -> str:
    """Eine Länge in ganzen mm, für Sätze der Legende."""
    return Groesse.aus_si(laenge, MM).formatiert(0)


def _bis_zum_umriss(p: Punkt, r: Punkt, umriss: Sequence[Punkt]) -> float:
    """
    Wie weit der Strahl von ``p`` in Richtung ``r`` läuft, bis er den Umriss
    trifft -- null, wenn ``p`` auf ihm liegt oder der Strahl ihn verfehlt. Nur
    fürs Bild.
    """
    treffer = []
    for (ax, ay), (bx, by) in zip(umriss, (*umriss[1:], umriss[0])):
        ex, ey = bx - ax, by - ay
        nenner = r[0] * ey - r[1] * ex
        if abs(nenner) < 1e-12:
            continue
        t = ((ax - p[0]) * ey - (ay - p[1]) * ex) / nenner
        s = ((ax - p[0]) * r[1] - (ay - p[1]) * r[0]) / nenner
        if t >= -1e-9 and -1e-9 <= s <= 1.0 + 1e-9:
            treffer.append(max(t, 0.0))
    return min(treffer, default=0.0)


def _linien(schnitt: Nachweisschnitt) -> list:
    """Die Stücke eines Schnitts fürs Bild, je mit der Angabe, ob es zählt."""
    return [{"punkte": punkte(l.punkte, MM), "zaehlt": l.zaehlt}
            for l in schnitt.massgebend.linien]


def _legende(befund: Durchstanzbefund, urteile: Sequence[NachweisUrteil],
             bereiche: Sequence[Plattenbereich] = ()) -> List[list]:
    """
    Die Zeilen unter dem Bild: der Schnitt und was von ihm nicht zählt; ohne
    Bewehrung der Vergleich mit seinem Urteil, sonst was ohne sie fehlt, der
    Pilz und die Leisten mit ihren Schnitten -- und das Urteil über alle. Passt
    kein Produkt, sagt die letzte Zeile das statt eines Grads, mit jedem Grund
    einmal: die Nachweise mit Bewehrung sind dann nicht geführt
    (:attr:`NachweisUrteil.offen`). Ohne Stützenkraft steht statt des
    Vergleichs der Satz aller Nachweise ohne Einwirkung. Mit Plattenbereichen
    je Stufe ihr Schnitt und, wo sie welche hat, ihre Leisten, und die Zahlen
    stehen je Schnitt.
    """
    innen, b, pilz = befund.innen, befund.leisten, befund.pilz
    gefuehrt = [u for u in urteile if not u.offen]
    zeilen = [
        zeile("Nachweisschnitt im Abstand ", zahlformel("d_v/2", innen.d_v / 2, MM, 0),
              " um die gestützte Fläche; wirksam ",
              Mathe(rf"u = k_e \cdot u_{{red}} = {masszahl(innen.u, MM, 0)}"), " mit ",
              zahlformel("k_e", innen.k_e, EINHEITSLOS, 2), "."),
        zeile("Gestrichelt, was nicht zählt: weiter als ", Mathe(r"1.5 \cdot d_v"),
              " von den Ecken grosser Stützen und entlang von Wänden, und was hinter "
              "Aussparungen liegt."),
    ]
    if bereiche:
        zeilen += _stufenzeilen(befund)
    if befund.ohne_einwirkung:
        zeilen.append(zeile(OHNE_EINWIRKUNG))
        return zeilen
    if befund.stufen or befund.weg is not None:
        zeilen += [zeile("Um die Stütze ", Mathe(f"V_d = {_kraft(innen.V_d_red)}"), ", ",
                         Mathe(f"V_{{Rd,c}} = {_kraft(befund.V_Rd_c)}"), "."),
                   *_schnittzeilen(befund)]
    elif b is None and pilz is None and gefuehrt:
        zeilen.append(zeile(*urteil(f"V_d = {_kraft(innen.V_d_red)}", r"\le",
                                    f"V_{{Rd,c}} = {_kraft(befund.V_Rd_c)}", *_gesamt(gefuehrt)),
                            "."))
        return zeilen
    else:
        zeilen.append(zeile("Ohne Bewehrung ",
                            Mathe(f"V_{{Rd,c}} = {_kraft(befund.V_Rd_c)} < "
                                  f"V_d = {_kraft(innen.V_d_red)}"), "."))
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
        zeilen += _leistenzeilen(b, "Durchstanzbewehrung",
                                 f"vom Rand {'des Pilzes' if pilz is not None else 'der Stütze'}")
    for x in befund.stufen:
        if x.leisten is not None:
            bereich = x.stufe.bereich
            zeilen += _leistenzeilen(
                x.leisten, f"Durchstanzbewehrung an der Stufe von {bereich.titel}",
                "von der Stufe", f",{bereich.name}")
    offen = [u for u in urteile if u.offen]
    if offen:
        gruende = " ".join(dict.fromkeys(u.hinweis for u in offen))
        zeilen.append(zeile(f"{gruende} Die Nachweise mit Durchstanzbewehrung sind darum nicht "
                            "geführt."))
    return [*zeilen, _gesamtzeile(urteile)] if gefuehrt else zeilen


def _leistenzeilen(b: Leistenpruefung, titel: str, vom: str, ix: str = "") -> List[list]:
    """
    Was die Legende von einer Durchstanzbewehrung sagt: Produkt und Abstände
    ``vom`` Rand ihrer gestützten Fläche, der äussere Schnitt und was sie
    trägt -- ``ix`` hängt an den Zeichen, «,B1» an der Stufe von Bereich B1.
    """
    v = b.vorschlag
    abstaende = r"\,/\,".join(Groesse.aus_si(x, MM).formatiert(0) for x in v.abstaende)
    return [
        zeile(f"{titel}: {v.name} im Abstand ", Mathe(rf"{abstaende}\,\mathrm{{mm}}"), f" {vom}."),
        zeile("Äusserer Schnitt (orange) im Abstand ",
              zahlformel(rf"0.5 \cdot d_{{v,out{ix}}}", b.aussen.d_v / 2, MM, 0),
              f" um die äussersten {v.system.ELEMENT}: ",
              zahlformel(f"u_{{out{ix}}}", b.aussen.u, MM, 0), ", ",
              Mathe(f"V_{{d,out{ix}}} = {_kraft(b.aussen.V_d_red)}"), ", ",
              Mathe(f"V_{{Rd,c,out{ix}}} = {_kraft(b.V_Rd_c_aussen)}"), "."),
        zeile(Mathe(f"V_{{Rd,s{ix}}} = {_kraft(b.V_Rd_s)}"), ", ",
              Mathe(f"V_{{Rd,max{ix}}} = {_kraft(b.V_Rd_max)}"), "."),
    ]


def _schnittzeilen(befund: Durchstanzbefund) -> List[list]:
    """Die Zahlen an den Stufen und am Schnitt durch verschiedene Dicken."""
    zeilen = []
    for x in _mit_schnitt(befund):
        name = x.stufe.bereich.name
        zeilen.append(zeile(
            f"An der Stufe von {x.stufe.bereich.titel} ",
            Mathe(f"V_{{d,{name}}} = {_kraft(x.stufe.pruefung.V_d_red)}"), ", ",
            Mathe(f"V_{{Rd,c,{name}}} = {_kraft(x.V_Rd_c)}"), "."))
    if befund.weg is not None:
        zeilen.append(zeile(
            f"Am Schnitt {weg.NAME} ",
            Mathe(f"V_{{d,W}} = {_kraft(befund.weg.schnitt.last.V_d_red)}"), ", ",
            Mathe(f"V_{{Rd,c,W}} = {_kraft(befund.weg.V_Rd_c)}"), "."))
    return zeilen


def _gesamtzeile(urteile: Sequence[NachweisUrteil]) -> list:
    """
    Das Urteil über alle geführten Nachweise, mit dem kleinsten Grad. Liessen
    sich nicht alle führen, sagt die Zeile davor warum, und hier steht «die
    übrigen» -- bis 2026-11-28 stand dann «Alle Nachweise erfüllt».
    """
    gefuehrt = [u for u in urteile if not u.offen]
    erfuellt, grad = _gesamt(gefuehrt)
    text = ("Nicht alle Nachweise erfüllt" if not erfuellt
            else "Die übrigen Nachweise erfüllt" if len(gefuehrt) < len(urteile)
            else "Alle Nachweise erfüllt")
    return zeile(f"{text}, kleinstes ", Mathe(rf"\alpha = {grad}"), ".")


def _stufenzeilen(befund: Durchstanzbefund) -> List[list]:
    """
    Was die Plattenbereiche im Bild sind: getönt mit ihrer Dicke, an jeder
    Stufe ihr Schnitt in seiner Farbe -- oder warum sie keinen hat -- und der
    Schnitt durch verschiedene Dicken.
    """
    zeilen = [zeile("Getönt die Plattenbereiche mit ihrer Dicke; an der Stütze gilt ",
                    zahlformel("d", befund.d, MM, 0), ".")]
    farben = {id(x): STUFENFARBEN[i % len(STUFENFARBEN)]
              for i, x in enumerate(_mit_schnitt(befund))}
    for x in befund.stufen:
        st, b = x.stufe, x.stufe.bereich
        if st.pruefung is None:
            zeilen.append(zeile(f"An der Stufe von {b.titel} kein eigener Schnitt: innerhalb ist "
                                "kein Platz für ihn."))
            continue
        wo = "ausserhalb" if b.seite is Seite.STUETZE else "innerhalb"
        zeilen.append(zeile(f"Schnitt an der Stufe von {b.titel} ({farben[id(x)]}) im Abstand ",
                            zahlformel("d_v/2", st.d / 2, MM, 0), f" {wo} des Bereichs, mit ",
                            zahlformel("d_v", st.d, MM, 0), " der dünneren Platte."))
    if befund.weg is not None:
        zeilen.append(zeile(f"Schnitt {weg.NAME} ({WEGFARBE}): der schwächste um die Stütze; "
                            "jedes Stück zählt mit ", Mathe(r"k_r \cdot d_v"), " seiner Stelle."))
    return zeilen


def _gesamt(urteile: Sequence[NachweisUrteil]) -> Tuple[bool, str]:
    """Ob alle geführten Urteile aufgehen, und ihr kleinster Grad in LaTeX."""
    return (all(u.erfuellt for u in urteile),
            min(urteile, key=lambda u: u.erfuellungsgrad.si).gradtext(latex=True))


def _kraft(si_wert: float) -> str:
    """Eine Kraft der Legende: kN mit einer Stelle."""
    return masszahl(si_wert, KN, 1)
