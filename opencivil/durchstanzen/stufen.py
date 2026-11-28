"""
opencivil/durchstanzen/stufen.py -- Plattenbereiche um die Stütze: d an ihr, Schnitte an den Stufen.

VERANTWORTUNG:
Liegt die Stütze in Bereichen mit eigener Dicke (:mod:`.bereiche`), gilt an
ihr deren statische Höhe, und ein Schnitt weiter aussen kann massgebend
sein: an einer Stufe, mit der kleineren statischen Höhe der dünneren Platte
(SIA 262:2025, 4.3.6.2.7). Gerechnet werden alle möglichen Schnitte, es
gilt der schwächste, und jeder hat sein Urteil. Hier steht, welche
statische Höhe an der Stütze und für ψ gilt (:func:`an_der_stuetze`), je
Stufe ihr Schnitt (:class:`Stufe`, :func:`stufen`) und wie die Herleitung
das zeigt -- mit denselben Schritten wie der Schnitt um die Stütze
(:mod:`.herleitung`).

WO DER SCHNITT AN EINER STUFE LIEGT (Figur 24):
In der Mitte des Risses, der durch die Ecke der Stufe läuft, von der
Druckseite schräg zur Zugbewehrung der dünneren Platte; d_v ist das der
dünneren Platte.

- Zur Stütze hin (Figur 24a): der Riss beginnt an der Stufe auf der
  Druckseite -- der Schnitt liegt 0.5·d_v ausserhalb des Bereichs, um seine
  konvexe Hülle (Figur 22c), mit Bögen um ihre Ecken.
- Gegenseite (Figur 24c): der Riss endet an der Stufe auf der Zugseite --
  der Schnitt liegt 0.5·d_v innerhalb des Bereichs, und mindestens 0.5·d_v
  neben der Stütze. Ist dafür kein Platz, gibt es an dieser Stufe keinen
  eigenen Schnitt.

Ein dünnerer Bereich gibt keinen Schnitt an seiner Stufe: jenseits ist die
Platte dicker, und jeder Schnitt dort trägt mehr als der innen.

DIE PLATTENROTATION:
ψ rechnet mit der kleinsten statischen Höhe um die Stütze -- meist der der
Platte ausserhalb der Bereiche: mit ihr dreht sich die Platte am meisten,
das liegt auf der sicheren Seite (Benutzer, 2026-11-27). Dasselbe ψ gilt an
jedem Schnitt; k_r (59) rechnet je Schnitt mit dessen d.

NACH VORGABE, NICHT NACHGESCHLAGEN:
- Ein Bereich zählt an seiner Stufe wie eine grosse gestützte Fläche: von
  einer Geraden des Schnitts zählt nur, was höchstens 1.5·d_v von einer Ecke
  entfernt liegt (Figur 23a) -- zur Stütze hin wie am Stahlpilz, auf der
  Gegenseite an den Ecken des Schnitts selbst.
- Ist ein Bereich auf der Gegenseite dicker, gilt sein d an einem Schnitt
  innen nur, wenn er weiter als d_v über dessen Fläche hinausreicht: sonst
  endete der Riss jenseits der Stufe, wo die Zugbewehrung höher liegt, und
  es gilt das d dort (:meth:`.bereiche.Dicken.wirksam`). Das gilt am
  Schnitt um die Stütze und an jeder Stufe zur Stütze hin.

EINHEITEN:
SI-Basis; Kräfte in N.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Sequence, Tuple

from opencivil.core.berechnung import Eingaben
from opencivil.core.nachweis import Vergleich
from opencivil.core.protokoll import Protokoll, Zwischenwerte
from opencivil.core.wert import Wert
from opencivil.durchstanzen import herleitung
from opencivil.durchstanzen.bereiche import Dicken, Plattenbereich, Seite
from opencivil.durchstanzen.herleitung import Index
from opencivil.durchstanzen.pruefung import KeRegel, Schnittpruefung, beiwert_k_r
from opencivil.durchstanzen.schnitt import (
    ECKENBEREICH, Halbebene, Kandidat, Punkt, Stuetzenflaeche, kandidat_polygon,
    kandidaten_stuetze, nachweisschnitt,
)
from opencivil.querschnitt.geometrie import lage, versetzt
from opencivil.querschnitt.platte import Richtung

#: Wo die Norm die Bereiche regelt.
REFERENZ = "SIA 262:2025, 4.3.6.2.7, Figur 24"


@dataclass(frozen=True)
class Stuetzenhoehe:
    """
    Welche Bereiche die Stütze umschliessen und welche statischen Höhen
    daraus folgen: an der Stütze und für ψ -- siehe Dateikopf.
    """

    um: Tuple[Plattenbereich, ...]
    """Die Bereiche um die Stütze, der innerste zuerst."""

    wirksam: Optional[Plattenbereich]
    """Wessen d an der Stütze gilt -- ``None``: das der Platte."""

    rotation: Optional[Plattenbereich]
    """Wessen d ψ rechnet: das kleinste um die Stütze -- ``None``: das der Platte."""


def an_der_stuetze(dicken: Dicken, stuetze: Stuetzenflaeche) -> Stuetzenhoehe:
    """Was an der Stütze gilt -- siehe :class:`Stuetzenhoehe`."""
    um = dicken.um(stuetze.umriss())
    wirksam = dicken.wirksam(
        um[0] if um else None,
        lambda d, b: b.enthaelt(Stuetzenflaeche(stuetze.kern, stuetze.radius + d).umriss()))
    rotation = min((None, *um), key=lambda b: (dicken.d_von(b), b is not None))
    return Stuetzenhoehe(um, wirksam, rotation)


@dataclass(frozen=True)
class Stufe:
    """
    Eine Stufe um die Stütze, wo der Bereich dicker ist als das, was jenseits
    liegt, und der Schnitt neben ihr -- ``pruefung`` fehlt, wo auf der
    Gegenseite kein Platz für einen ist.
    """

    bereich: Plattenbereich
    jenseits: Optional[Plattenbereich]
    """Was jenseits der Stufe liegt -- ``None``: die Platte."""

    wirksam: Optional[Plattenbereich]
    """Wessen d der Schnitt rechnet -- meist das jenseits der Stufe."""

    d: float
    pruefung: Optional[Schnittpruefung]

    @property
    def index(self) -> Index:
        """Wie ihre Werte heissen: u_{0,B1}, V_{Rd,c,B1}."""
        return Index(self.bereich.name)

    def V_Rd_c(self, psi: float, k_g: float, tau_cd: float) -> float:
        """Der Widerstand an der Stufe, still: k_r (59) mit ihrem d -- für die Kennzahl."""
        return self.pruefung.V_Rd_c(beiwert_k_r(psi, self.d, k_g), tau_cd)


def stufen(dicken: Dicken, hoehe: Stuetzenhoehe, stuetze: Stuetzenflaeche, *,
           raender: Sequence[Halbebene], achse: Punkt, aussparungen: Sequence[Sequence[Punkt]],
           regel: KeRegel, V_d: float, q_d: float) -> Tuple[Stufe, ...]:
    """Die Stufen um die Stütze, die innerste zuerst, je mit ihrem Schnitt -- still."""
    ergebnis = []
    for b in hoehe.um:
        if not dicken.dicker(b):
            continue
        jenseits = dicken.aussen(b)
        if b.seite is Seite.STUETZE:
            huelle = b.huelle
            wirksam = dicken.wirksam(
                jenseits, lambda d, x: x.enthaelt(Stuetzenflaeche(huelle, d).umriss()))
            d = dicken.d_von(wirksam)
            kandidaten = kandidaten_stuetze(Stuetzenflaeche(huelle), d / 2.0, ECKENBEREICH * d,
                                            raender)
        else:
            wirksam = jenseits
            d = dicken.d_von(jenseits)
            kandidat = _innerhalb(b, d, stuetze, raender)
            if kandidat is None:
                ergebnis.append(Stufe(b, jenseits, wirksam, d, None))
                continue
            kandidaten = [kandidat]
        schnitt = nachweisschnitt(kandidaten, d_v=d, achse=achse, aussparungen=aussparungen)
        pruefung = Schnittpruefung(schnitt, d, regel, V_d, q_d)
        ergebnis.append(Stufe(b, jenseits, wirksam, d, pruefung))
    return tuple(ergebnis)


def _innerhalb(bereich: Plattenbereich, d: float, stuetze: Stuetzenflaeche,
               raender: Sequence[Halbebene]) -> Optional[Kandidat]:
    """
    Der Schnitt 0.5·d innerhalb der Stufe auf der Gegenseite (Figur 24c) --
    oder nichts, wo er näher als 0.5·d an die Stütze käme. Seine Geraden
    zählen je 1.5·d von ihren Ecken.
    """
    innen = versetzt(bereich.huelle, d / 2.0)
    if innen is None or not all(lage(p, innen) >= 0 for p in
                                Stuetzenflaeche(stuetze.kern, stuetze.radius + d / 2.0).umriss()):
        return None
    return kandidat_polygon("innerhalb der Stufe", innen, ECKENBEREICH * d, raender)


# ===========================================================================
# Herleitung
# ===========================================================================


@dataclass(frozen=True)
class Bereichswerte:
    """
    Was die Herleitung von den Bereichen um die Stütze zeigt: je Bereich
    seine Dicke als Wert, d an der Stütze und, wo es nicht das der Platte
    ist, d für ψ mit den beiden Lagen.
    """

    dicken: Dict[str, Wert]
    d_S: Wert
    d_psi: Optional[Wert] = None
    lagen_psi: Optional[Dict[Richtung, Wert]] = None


def bereiche_schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, dicken: Dicken,
                       hoehe: Stuetzenhoehe, d: Wert, lagen: Dict[Richtung, Wert]) -> Bereichswerte:
    """
    Die Bereiche um die Stütze, die statische Höhe an ihr und die, mit der
    ψ rechnet. ``d`` und ``lagen`` sind die der Platte.
    """
    p.titel("Plattenbereiche", ebene=3)
    if not hoehe.um:
        p.text("Die Stütze steht in keinem Plattenbereich: an ihr gilt d der Platte.")
        return Bereichswerte({}, d)
    werte = {b.name: w.laenge(f"h_{b.name}", f"h_{{{b.name}}}", b.h, f"Dicke im {b.titel}",
                              stellen=0) for b in hoehe.um}
    for b in hoehe.um:
        jenseits = dicken.aussen(b)
        wo = "die Platte" if jenseits is None else jenseits.titel
        p.wert(werte[b.name], titel=f"Dicke im {b.titel}, Stufe {b.seite.beschriftung}",
               referenz=f"SIA 262:2025, 4.3.6.2.7, {b.seite.figur}")
        mehr = b.h - dicken.h_von(jenseits)
        if abs(mehr) > 1e-9:
            p.text(f"{b.titel} ist {abs(mehr) * 1e3:.0f} mm {'dicker' if mehr > 0 else 'dünner'} "
                   f"als {wo} um ihn.")
    innerster = hoehe.um[0]
    if hoehe.wirksam is not innerster:
        p.erklaerung(
            f"{innerster.titel} ist auf der Gegenseite dicker, reicht aber nicht d_v über die "
            f"Stütze hinaus: der Riss um sie endete jenseits der Stufe, wo die Zugbewehrung "
            f"höher liegt. An der Stütze gilt darum d "
            f"{'der Platte' if hoehe.wirksam is None else 'im ' + hoehe.wirksam.titel} – nach "
            f"Vorgabe, nicht nachgeschlagen.")
    d_S = _d_im(p, w, e, werte, d, hoehe.wirksam, "d_S", "d_S",
                titel="Statische Höhe an der Stütze")
    if hoehe.rotation is None:
        return Bereichswerte(werte, d_S)
    d_psi = d_S if hoehe.rotation is hoehe.wirksam else _d_im(
        p, w, e, werte, d, hoehe.rotation, "d_psi", r"d_{\psi}",
        titel="Statische Höhe für die Plattenrotation")
    lagen_psi = {r: _d_im(p, w, e, werte, lagen[r], hoehe.rotation, f"d_{r.value}_psi",
                          rf"d_{{{r.value},\psi}}", titel=f"Statische Höhe der Lage in {r.value} "
                                                          f"für die Plattenrotation")
                 for r in (Richtung.X, Richtung.Y)}
    return Bereichswerte(werte, d_S, d_psi, lagen_psi)


def _d_im(p: Protokoll, w: Zwischenwerte, e: Eingaben, werte: Dict[str, Wert], d: Wert,
          b: Optional[Plattenbereich], name: str, symbol: str, *, titel: str) -> Wert:
    """d im Bereich ``b``: d der Platte, um den Unterschied der Dicke verschoben."""
    if b is None:
        ergebnis = w.laenge(name, symbol, d.groesse.si)
        p.formel(ergebnis, "@d", {"d": d}, titel=f"{titel}: die der Platte", referenz=REFERENZ)
        return ergebnis
    ergebnis = w.laenge(name, symbol, d.groesse.si + b.h - e.g("h").si)
    p.formel(ergebnis, "@d + @h_B - @h", {"d": d, "h_B": werte[b.name], "h": e["h"]},
             titel=f"{titel}, im {b.titel}: d der Platte, um den Unterschied der Dicke verschoben",
             referenz=REFERENZ, name="Statische Höhe in einem Plattenbereich")
    return ergebnis


def rotation_schreiben(p: Protokoll, hoehe: Stuetzenhoehe) -> None:
    """Der Satz, mit welchem d ψ rechnet -- nur, wo die Stütze in Bereichen steht."""
    if not hoehe.um:
        return
    wo = ("der Platte ausserhalb der Bereiche" if hoehe.rotation is None
          else f"im {hoehe.rotation.titel}, der dünnsten Stelle um die Stütze")
    p.erklaerung(f"ψ rechnet mit d {wo}: mit der kleinsten statischen Höhe dreht sich die Platte "
                 f"am meisten – das liegt auf der sicheren Seite. Dasselbe ψ gilt an jedem "
                 f"Schnitt; k_r rechnet je Schnitt mit dessen d.")


def stufe_schreiben(p: Protokoll, w: Zwischenwerte, e: Eingaben, st: Stufe, *, d: Wert,
                    werte: Bereichswerte, psi: Wert, k_g: Wert, tau_cd: Wert, k_e_stuetze: Wert,
                    last: str, V_d: Optional[Wert] = None) -> Optional[Tuple[Wert, Wert]]:
    """
    Der Schnitt an einer Stufe mit denselben Schritten wie um die Stütze:
    zurück kommen die Querkraft in ihm und sein Widerstand -- oder nichts,
    wo er fehlt. ``d`` ist das d der Platte, ``V_d`` die Stützenkraft, wo es
    nicht die eingegebene ist (die Kennzahl).
    """
    b, ix = st.bereich, st.index
    jenseits = "der Platte" if st.jenseits is None else f"im {st.jenseits.titel}"
    p.titel(f"An der Stufe von {b.titel}", ebene=3)
    if st.pruefung is None:
        p.erklaerung(
            f"{b.titel} ist auf der Gegenseite dicker (Figur 24c), reicht aber nicht d_v über die "
            f"Stütze hinaus: innerhalb seiner Stufe ist kein Platz für einen eigenen Schnitt. Der "
            f"Schnitt um die Stütze rechnet schon mit d {jenseits}.")
        return None
    if b.seite is Seite.STUETZE:
        p.erklaerung(
            f"{b.titel} ist zur Stütze hin dicker, wie ein Stützenkopf (Figur 24a): ausserhalb "
            f"seiner Stufe beginnt ein Riss auf der Druckseite {jenseits}. Der Schnitt liegt "
            f"0.5·d_v ausserhalb des Bereichs, um seine konvexe Hülle, mit d_v der dünneren "
            f"Platte; es gilt der schwächere Schnitt (4.3.6.2.7).")
    else:
        p.erklaerung(
            f"{b.titel} ist auf der Gegenseite dicker, wie eine Vertiefung (Figur 24c): ein Riss "
            f"von der Druckseite endet an der Stufe, an der Zugbewehrung {jenseits}. Der Schnitt "
            f"liegt 0.5·d_v innerhalb des Bereichs, mit d_v der dünneren Platte; es gilt der "
            f"schwächere Schnitt (4.3.6.2.7).")
    d_st = (d if st.wirksam is None
            else _d_im(p, w, e, werte.dicken, d, st.wirksam, ix.name("d"), ix.symbol("d"),
                       titel="Statische Höhe an der Stufe"))
    if st.wirksam is not st.jenseits:
        p.erklaerung(f"Jenseits reicht {st.jenseits.titel} nicht d_v über die Stufe hinaus: der "
                     f"Riss endet dort, wo die Zugbewehrung höher liegt – nach Vorgabe, nicht "
                     f"nachgeschlagen.")
    d_v = w.laenge(ix.name("d_v"), ix.symbol("d", "v"), st.d)
    p.formel(d_v, "@d", {"d": d_st}, titel="Wirksame statische Höhe an der Stufe",
             referenz=f"SIA 262:2025, 4.3.6.2.7, {b.seite.figur}",
             name="Wirksame statische Höhe an einer Stufe")
    a = st.pruefung.auswertung
    u_0 = herleitung.rand(p, w, a, ix=ix,
                          titel="Schnitt an der Stufe, soweit er in der Platte liegt",
                          referenz=f"SIA 262:2025, 4.3.6.2.7, {b.seite.figur}")
    u_red = herleitung.abzuege(
        p, w, a, u_0, ix=ix,
        ecken_text="Der Bereich trägt wie eine grosse gestützte Fläche: von einer Geraden des "
                   "Schnitts zählt nur, was höchstens 1.5·d_v von einer Ecke entfernt liegt – "
                   "nach Vorgabe, nicht nachgeschlagen.",
        ecken_referenz="SIA 262:2025, 4.3.6.2.3, Figur 23a")
    k_e = herleitung.k_e(p, w, st.pruefung, ix=ix, an_der_stuetze=k_e_stuetze)
    u = herleitung.wirksam(p, w, k_e, u_red, ix=ix,
                           titel="Wirksamer Umfang des Schnitts an der Stufe")
    V = herleitung.querkraft(p, w, e, st.pruefung, ix=ix, V_d=V_d,
                             titel_last=f"{last} innerhalb des Schnitts an der Stufe",
                             titel="Querkraft im Schnitt an der Stufe")
    k_r = herleitung.k_r(p, w, psi, d_st, k_g, ix=ix, titel="Beiwert k_r an der Stufe, mit ihrem d")
    V_Rd_c = herleitung.widerstand(p, w, st.pruefung, ix=ix, k_r=k_r, tau_cd=tau_cd, d_v=d_v,
                                   u=u, titel="Durchstanzwiderstand an der Stufe",
                                   referenz="SIA 262:2025, 4.3.6.2.7, (58)")
    return V, V_Rd_c


def vergleich_schreiben(p: Protokoll, st: Stufe, V: Wert, V_Rd_c: Wert) -> Vergleich:
    """Der Vergleich an der Stufe -- sein Urteil gibt der Nachweis."""
    v = Vergleich(V, V_Rd_c)
    v.bedingung(p, f"Querkraft gegen den Widerstand an der Stufe von {st.bereich.titel}")
    return v
