"""
opencivil/mauerwerk/herleitung.py -- wie eine Mauerwerkswand ihre Rechnung aufschreibt.

VERANTWORTUNG:
Die Wand in Zahlen: ihre Masse und ihr Mauerwerk, wie sie gemauert und
gehalten ist, die Bemessungswerte, mit denen sie rechnet, ihre Öffnungen
mit den Stürzen darüber, die Pfeiler dazwischen und was die Lastfälle und
Kombinationen ihnen geben (:mod:`~opencivil.mauerwerk.lasten`) -- schiebt
eine Last waagrecht, auch in der Ebene der Wand
(:mod:`~opencivil.mauerwerk.scheibe`), und mit Querlasten, was quer zu ihr
wirkt, die Ersatzkraft des Erdbebens hergeleitet
(:mod:`~opencivil.mauerwerk.querlast`). Zuletzt die Meldungen: rot, was
falsch ist, sonst als Hinweis.

EINHEITEN:
Masse der Wand und Orte in m, die Masse eines Sturzes in mm -- wie in der
Maske; Festigkeiten und Moduln in N/mm², wie im Material; Kräfte in kN,
Momente in kNm. Die Dicke der Wand steht im Kasten ihrer Vorgaben.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Sequence, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.einheiten import KN_PRO_M2, Groesse
from opencivil.core.latex import Mathe, Zelle, fest
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.sprache import aufgezaehlt
from opencivil.mauerwerk.kennwerte import REFERENZ_VERBAND, Wandwerte, quelle
from opencivil.mauerwerk.lasten import SEITEN, Abtrag
from opencivil.mauerwerk.modell import Pfeiler, Wand
from opencivil.mauerwerk.querlast import erdbeben_schreiben
from opencivil.mauerwerk.scheibe import anteile, koepfe

if TYPE_CHECKING:
    from opencivil.mauerwerk.werk import Wandbefund

#: Was die Wand annimmt -- in eigenen Worten nach SIA 266:2015, 4.1.2 und 4.1.4.
ANNAHME = (
    "Eine Wand aus unbewehrtem Mauerwerk nach SIA 266:2015, gezeichnet in der Ansicht. Kohäsion "
    "und Zugfestigkeit des Mauerwerks zählen nicht (4.1.2), und quer zu ihrer Ebene ist die Wand "
    "gehalten (4.1.4). Die Zeichen der Norm: x steht senkrecht zu den Lagerfugen, also lotrecht, "
    "y längs der Wand (Figur 1).")

#: Wie die Lasten zu den Pfeilern kommen, in eigenen Worten (:mod:`.lasten`).
ABTRAG = (
    "Die Lasten gehen lotrecht nach unten. Was über einem Pfeiler liegt, trägt er, samt seinem "
    "eigenen Gewicht. Was über einer Öffnung liegt, trägt ihr Sturz: über einem seiner Auflager "
    "ganz dieses, über der Öffnung als einfacher Balken zwischen den Mitten der Auflager. Seine "
    "Auflagerkräfte gehen weiter nach unten, in den Pfeiler darunter oder auf den nächsten Sturz. "
    "Was unter einer Öffnung liegt, etwa eine Brüstung, geht neben den Pfeilern in den Fuss. Die "
    "Ausmitte einer Last wirkt am Kopf der Pfeiler, die sie tragen; ein Sturz wiegt wie "
    "Mauerwerk. Die Ausmitte am Kopf ist die der Lasten allein: das Eigengewicht kommt erst "
    "darunter dazu.")

#: Woher die Regeln des Lastabtrags kommen.
ABTRAG_ANNAHME = ("Den Lastabtrag in der Wand regelt die Norm nicht; so verteilt das Werkzeug "
                  "die Lasten nach Vorgabe, nicht nachgeschlagen.")

#: Wie die waagrechten Lasten zu den Pfeilern kommen, in eigenen Worten (:mod:`.scheibe`).
SCHEIBE = (
    "Die waagrechten Lasten nimmt die Wand als Scheibe auf. Über den Öffnungen ist sie starr – "
    "Stürze, Mauerwerk und Decke –, und dort greifen die Lasten an. Jeder Pfeiler ist am Fuss "
    "der Wand eingespannt und oben an den starren Teil angeschlossen, am oberen Rand der "
    "höchsten Öffnung neben ihm; Brüstungen zählen nicht. Er wirkt ungerissen, mit E_xd · I auf "
    "Biegung, G_d · A / 1.2 auf Schub und E_xd · A längs. Steht nur ein Pfeiler da, ist er ein "
    "Kragarm; mit mehreren kippt die Wand, und die Pfeiler bekommen dazu Normalkräfte – sie "
    "stehen schon in der Normalkraft am Fuss. Die lotrechten Lasten stehen nicht immer über der "
    "Mitte der Pfeiler, die sie tragen; ihr Moment M_v um diese Mitten gleicht der starre Teil "
    "aus und gibt es den Pfeilern nach ihrer Biegesteifigkeit, je b³, an den Fuss.")

#: Woher die Regeln der Scheibe kommen.
SCHEIBE_ANNAHME = ("Wie die Wand als Scheibe trägt, regelt die Norm nicht; so verteilt das "
                   "Werkzeug die waagrechten Lasten nach Vorgabe, nicht nachgeschlagen.")

#: Wie die Querlasten wirken, in eigenen Worten.
QUER = (
    "Eine Querlast wirkt gleichmässig über die ganze Wand, je m² Ansicht. Die von Hand ist "
    "positiv zur Seite, von der aus man die Ansicht sieht; die des Erdbebens wirkt in beiden "
    "Richtungen und steht als Betrag da. Was sie bewirkt, sagt der Nachweis «Querlast».")

#: Je Wert der Tabelle: Kurzname, Zeichen, Stellen.
ZEILEN = (("f_xd", "f_{xd}", 2), ("f_yd", "f_{yd}", 2), ("E_xd", "E_{xd}", 0), ("G_d", "G_d", 0),
          ("mu_d", r"\mu_d", 2))


def schreiben(p: Protokoll, befund: "Wandbefund", e: Eingaben, basis: str) -> None:
    """
    Die ganze Herleitung -- nichts davon geht in den Befund ein, also still
    gar keine. ``e`` sind die Eingaben der Wand, ``basis`` der Anfang der
    Kennungen ihrer Zwischenwerte.
    """
    if p.still:
        return
    p.annahme(ANNAHME)
    w = befund.wand
    r = w.flaeche
    if r is not None:
        p.tabelle(["Wand", "Mauerwerk", Mathe(r"l_w\ [\mathrm{m}]"), Mathe(r"h_w\ [\mathrm{m}]")],
                  [[w.umrisse[0].name, befund.mauerwerk, Mathe(fest(r.breite, 2)),
                    Mathe(fest(r.hoehe, 2))]], titel="Wand")
    p.text(f"{_gemauert(w)} {_gehalten(w)}")
    _werte(p, befund)
    if w.oeffnungen:
        _oeffnungen(p, w)
    if befund.pfeiler:
        _pfeiler(p, befund.pfeiler)
    if befund.faelle:
        _lasten(p, befund, e, basis)
    for meldung in befund.alle_meldungen:
        (p.warnung if meldung.fehler else p.hinweis)(meldung.text)


def _gemauert(w: Wand) -> str:
    """Wie die Wand gemauert ist, als Satz."""
    return f"{w.mauerung.beschriftung}, die Stossfugen {w.stossfugen.beschriftung} vermauert."


def _gehalten(w: Wand) -> str:
    """Wie ihre Ränder gehalten sind, als Satz."""
    return (f"Kopf {w.kopf.beschriftung}, Fuss {w.fuss.beschriftung}; links "
            f"{w.links.beschriftung}, rechts {w.rechts.beschriftung}.")


def _werte(p: Protokoll, befund: "Wandbefund") -> None:
    """Die Bemessungswerte des Mauerwerks und die der Wand, im Verband mit dem Faktor."""
    w, werte, material = befund.wand, befund.werte, befund.material
    saetze: List[str] = []
    if w.verband:
        saetze.append(f"Für Verbandmauerwerk gelten alle Werte der Tabelle 7 mal "
                      f"{fest(werte.faktor, 2)} ({REFERENZ_VERBAND}); μ_d bleibt.")
    if w.vollfugig:
        saetze.append("Vollfugig vermauert gilt das grössere f_yd der Tabelle 7.")
    if saetze:
        p.text(" ".join(saetze))
    p.tabelle(["", f"Mauerwerk «{befund.mauerwerk}»", "Wand"],
              [_wertzeile(kurz, symbol, stellen, material, werte, w.vollfugig)
               for kurz, symbol, stellen in ZEILEN],
              titel="Bemessungswerte, Festigkeiten und Moduln in N/mm²")


def _wertzeile(kurz: str, symbol: str, stellen: int, material: dict, werte: Wandwerte,
               vollfugig: bool) -> List[Zelle]:
    """Eine Zeile: der Wert des Mauerwerks, der der Wand -- im Verband mit dem Faktor davor."""
    aus = quelle(kurz, vollfugig)
    roh, wand = material[aus], getattr(werte, kurz)
    zeichen = f"{symbol},\\ \\mathrm{{vollfugig}}" if aus != kurz else symbol
    if kurz == "mu_d" or werte.faktor == 1.0:
        zelle = fest(wand, stellen)
    else:
        zelle = rf"{fest(werte.faktor, 2)} \cdot {fest(roh, stellen)} = {fest(wand, stellen)}"
    return [Mathe(zeichen), Mathe(fest(roh, stellen)), Mathe(zelle)]


def _oeffnungen(p: Protokoll, w: Wand) -> None:
    """Je Öffnung ihr Ort, ihre Masse und der Sturz darüber."""
    zeilen = []
    for o in w.oeffnungen:
        r = o.rechteck
        if r is None:
            continue
        zeilen.append([o.name, _von_bis(r.x0, r.x1), _von_bis(r.y0, r.y1), Mathe(fest(r.breite, 2)),
                       Mathe(fest(r.hoehe, 2)), o.sturz.beschriftung,
                       Mathe(fest(o.h_St * 1e3, 0)), Mathe(fest(o.a * 1e3, 0))])
    if zeilen:
        p.tabelle(["Öffnung", "links – rechts [m]", "unten – oben [m]", Mathe(r"b\ [\mathrm{m}]"),
                   Mathe(r"h\ [\mathrm{m}]"), "Sturz", Mathe(r"h_{St}\ [\mathrm{mm}]"),
                   Mathe(r"a\ [\mathrm{mm}]")], zeilen,
                  titel="Öffnungen – über jeder ein Sturz, a ist seine Auflagerlänge")


def _von_bis(von: float, bis: float) -> str:
    """Zwei Masse in m, als Spanne: «1.00 – 2.00»."""
    return f"{fest(von, 2)} – {fest(bis, 2)}"


def _pfeiler(p: Protokoll, pfeiler: List[Pfeiler]) -> None:
    """Je Pfeiler, wo er steht, wie breit er ist und zwischen welchen Öffnungen."""
    def zwischen(e: Pfeiler) -> str:
        links = aufgezaehlt(list(e.links)) if e.links else "Wandende"
        rechts = aufgezaehlt(list(e.rechts)) if e.rechts else "Wandende"
        return "ganze Wand" if not e.links and not e.rechts else f"{links} | {rechts}"

    p.tabelle(["Pfeiler", "links – rechts [m]", Mathe(r"b\ [\mathrm{m}]"), "zwischen"],
              [[e.name, _von_bis(e.x0, e.x1), Mathe(fest(e.b, 2)), zwischen(e)] for e in pfeiler],
              titel="Pfeiler – zwischen den Öffnungen und an den Enden der Wand")


def _lasten(p: Protokoll, befund: "Wandbefund", e: Eingaben, basis: str) -> None:
    """
    Das Eigengewicht je m², dann je Lastfall und Kombination, was Pfeiler
    und Stürze tragen: die Normalkraft am Fuss jedes Pfeilers, an seinem
    Kopf die der Lasten allein und das Moment ihrer Ausmitten, und die
    Kräfte der Sturzauflager.
    """
    p.titel("Lastabtrag", ebene=3)
    p.text(ABTRAG)
    p.annahme(ABTRAG_ANNAHME)
    w = befund.wand
    zw = Zwischenwerte(basis)
    erdbeben = [q for lf in w.lastfaelle for q in lf.querlasten if q.erdbeben]
    g_k = zw.wert("g_k", "g_k", Groesse.aus_si(befund.g_k, KN_PRO_M2), 2,
                  "Eigengewicht der Wand je m² Ansicht")
    if erdbeben or any(lf.eigengewicht for lf in w.lastfaelle):
        p.formel(g_k, r"@rho \cdot @g \cdot @t", {"rho": e["rho"], "g": e["g"], "t": e["t"]},
                 titel="Eigengewicht der Wand je m² Ansicht, aus der Dichte ihres Mauerwerks")
    faelle: Dict[str, Abtrag] = {**befund.faelle, **befund.kombinationen}
    kopf = ["", *faelle]
    p.text("Die Lastfälle charakteristisch, die Kombinationen mit ihren Beiwerten.")
    _tabelle(p, kopf, faelle, [(pf.name, lambda a, n=pf.name: a.N[n]) for pf in befund.pfeiler]
             + ([("neben den Pfeilern", lambda a: a.unten)]
                if any(abs(a.unten) > 1e-9 for a in faelle.values()) else []),
             1e-3, 1, "Normalkraft am Fuss der Pfeiler, Druck positiv, in kN")
    if any(abs(m) > 1e-9 for a in faelle.values() for m in a.M.values()):
        _tabelle(p, kopf, faelle,
                 [(pf.name, lambda a, n=pf.name: a.N_L[n]) for pf in befund.pfeiler],
                 1e-3, 1, "Normalkraft aus den Lasten am Kopf der Pfeiler, ohne Eigengewicht, "
                          "in kN")
        _tabelle(p, kopf, faelle,
                 [(pf.name, lambda a, n=pf.name: a.M[n]) for pf in befund.pfeiler],
                 1e-3, 2, "Moment der Ausmitten am Kopf der Pfeiler, in kNm")
    auflager = [(o.name, s) for o in w.oeffnungen if o.rechteck is not None for s in SEITEN]
    if auflager:
        _tabelle(p, kopf, faelle, [(f"{o} {s}", lambda a, k=(o, s): a.R[k]) for o, s in auflager],
                 1e-3, 1, "Kräfte der Sturzauflager, in kN")
    if any(abs(v) > 1e-9 for a in faelle.values() for v in a.V.values()):
        _scheibe(p, befund, kopf, faelle)
    if any(q.wirkt for lf in w.lastfaelle for q in lf.querlasten):
        p.titel("Quer zur Wand", ebene=3)
        p.text(QUER)
        for q in erdbeben:
            erdbeben_schreiben(p, zw, q, g_k, e["g"])
        _tabelle(p, kopf, faelle, [(name, lesen) for name, lesen in (
            ("von Hand", lambda a: a.p), ("Erdbeben", lambda a: a.p_E))
            if any(abs(lesen(a)) > 1e-9 for a in faelle.values())], 1e-3, 2,
                 "Querlast je m² Wand, in kN/m²")


def _scheibe(p: Protokoll, befund: "Wandbefund", kopf: List[str],
             faelle: Dict[str, Abtrag]) -> None:
    """Was die waagrechten Lasten den Pfeilern geben: Querkraft, Normalkraft und Moment am Fuss."""
    w = befund.wand
    p.titel("In der Ebene der Wand", ebene=3)
    p.text(SCHEIBE)
    p.annahme(SCHEIBE_ANNAHME)
    oben, anteil = koepfe(w.flaeche, w.oeffnungen, befund.pfeiler), anteile(befund.pfeiler)
    p.tabelle(["Pfeiler", Mathe(r"b\ [\mathrm{m}]"), Mathe(r"h_P\ [\mathrm{m}]"),
               Mathe(r"b^3 / \Sigma b^3")],
              [[e.name, Mathe(fest(e.b, 2)), Mathe(fest(oben[e.name] - w.flaeche.y0, 2)),
                Mathe(fest(anteil[e.name], 3))] for e in befund.pfeiler],
              titel="Pfeiler der Scheibe – h_P vom Fuss der Wand bis zum starren Teil, "
                    "dazu ihr Anteil an M_v")
    if any(abs(a.M_v) > 1e-9 for a in faelle.values()):
        _tabelle(p, kopf, faelle, [("M_v", lambda a: a.M_v)], 1e-3, 2,
                 "Moment der lotrechten Lasten um die Mitten der Pfeiler, die sie tragen, "
                 "positiv, wenn sie rechts davon stehen, in kNm")
    namen = [e.name for e in befund.pfeiler]
    _tabelle(p, kopf, faelle, [(n, lambda a, n=n: a.V[n]) for n in namen], 1e-3, 1,
             "Querkraft in der Wandebene, positiv nach rechts, in kN")
    _tabelle(p, kopf, faelle, [(n, lambda a, n=n: a.N_H[n]) for n in namen], 1e-3, 1,
             "Normalkraft aus den waagrechten Lasten, Druck positiv, in kN – schon in der "
             "Normalkraft am Fuss")
    _tabelle(p, kopf, faelle, [(n, lambda a, n=n: a.M_z[n]) for n in namen], 1e-3, 2,
             "Moment in der Wandebene am Fuss der Pfeiler, positiv, wenn es die Resultierende "
             "nach rechts schiebt, in kNm")


def _tabelle(p: Protokoll, kopf: List[str], faelle: Dict[str, Abtrag],
             zeilen: Sequence[Tuple[str, Callable[[Abtrag], float]]], faktor: float, stellen: int,
             titel: str) -> None:
    """Je Zeile ihr Name und je Fall die Zahl, die ``lesen`` aus seinem Abtrag liest, in SI."""
    p.tabelle(kopf, [[name, *(Mathe(fest(lesen(a) * faktor, stellen)) for a in faelle.values())]
                     for name, lesen in zeilen], titel=titel,
              ausrichtung="l" + "r" * len(faelle))
