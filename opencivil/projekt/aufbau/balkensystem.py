"""
opencivil/projekt/aufbau/balkensystem.py -- ein Balkensystem wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.balkensystem.BalkensystemEintrag` das
Stabwerk in SI mit seinen Meldungen (:func:`modell_von`) und daraus die
Rechnung mit aufgeloesten Materialien und Querschnitten (:func:`bauen`). Ein
Material ist ein Beton des Projekts oder ein eigenes. Die Art eines
Querschnitts wird hier aufgeloest, einmal: je Art eine Klasse
(:mod:`~opencivil.stabwerk.stabquerschnitt`). Ein Querschnitt kann eine
Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen dann
schon gebaut sein -- darum kommt das Balkensystem in
:data:`~opencivil.projekt.aufbau.BAUTEILE` nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from opencivil.core.einheiten import Groesse
from opencivil.material.basis import Baustoff
from opencivil.projekt.balkensystem import (
    EINHEIT_DER_FEDER, EINHEIT_DER_LAST, MATERIAL_DES_QUERSCHNITTS, BalkensystemEintrag,
    Querschnittsart, StabmaterialEintrag, StabquerschnittEintrag,
)
from opencivil.projekt.lesen import ProjektFehler
from opencivil.spannungsanalyse.modul import ModulAusAnalyse, ModulAusPlatte, Modulfrage
from opencivil.stabwerk.rechnung import Balkensystem, Stabmaterial
from opencivil.stabwerk.stabquerschnitt import (
    AusAnalyse, AusPlatte, NachVorlage, Stabquerschnitt, VonHand,
)
from opencivil.stabwerk.modell import (
    FEST, FREI, Halt, Kombination, Knoten, Knotenlast, Lager, Lastfall, Lastrichtung, Stab,
    Stablast, System, feder,
)
from opencivil.stabwerk.system import Meldung

from opencivil.projekt.aufbau.faelle import beiwerte, doppelte_kennungen, faelle_pruefen, ohne_lastfall
from opencivil.projekt.aufbau.kern import Aufbau, Bauteil

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart


@dataclass
class Modell:
    """
    Das Stabwerk der Beschreibung, in N, m und rad -- noch ohne
    Steifigkeiten: ``EA`` und ``EI`` jedes Stabs kommen aus dem Rechenwerk,
    je Paar aus Querschnitt und Material (``paare``). Was sich nicht
    uebersetzen laesst, steht in ``meldungen``, wie die des Rechenkerns.
    """

    system: System
    paare: Dict[str, Tuple[str, str]] = field(default_factory=dict)
    """Je tragenden Stab die Kennungen seines Querschnitts und seines Materials."""

    meldungen: List[Meldung] = field(default_factory=list)

    eigengewicht: Optional[str] = None
    """Der Name des Lastfalls, der das Eigengewicht der Staebe bekommt -- oder keiner."""

    @property
    def gueltig(self) -> bool:
        return not any(m.fehler for m in self.meldungen)



def modell_von(eintrag: BalkensystemEintrag) -> Modell:
    """
    Das Stabwerk zum Rechnen, in SI (:mod:`opencivil.stabwerk.modell`).

    Ein Stab ohne Querschnitt oder Material -- oder mit einem Material,
    das es im System nicht gibt --, ein Querschnitt mit unmoeglichen
    Massen und eine Feder ohne Steifigkeit sind Fehler, die die Meldungen
    nennen: gerechnet wird dann nicht -- und nicht etwa mit einem Stab
    weniger. Ob ein Material traegt, weiss erst der Aufbau: er kennt die
    Betone des Projekts. Eine Last, deren Lastfall es nicht gibt, und ein
    Beiwert dafuer bleiben mit einem Hinweis weg.
    """
    meldungen: List[Meldung] = []

    def melden(text: str, *elemente: str, fehler: bool = True) -> None:
        meldungen.append(Meldung(text, tuple(elemente), fehler))

    meldungen.extend(faelle_pruefen(eintrag.lastfaelle, eintrag.kombinationen))
    eigen = [lf for lf in eintrag.lastfaelle if lf.eigengewicht]
    for was, liste in (("Knoten", eintrag.knoten), ("Linien", eintrag.linien),
                       ("Lager", eintrag.lager), ("Lasten", eintrag.alle_lasten()),
                       ("Materialien", eintrag.stabmaterialien),
                       ("Querschnitte", eintrag.querschnitte), ("Lastfälle", eintrag.lastfaelle),
                       ("Kombinationen", eintrag.kombinationen)):
        meldungen.extend(doppelte_kennungen(was, liste))

    def halt(art: str, k: float, feld: str, wo: str) -> Halt:
        if art == "frei":
            return FREI
        if art == "fest":
            return FEST
        if k <= 0.0:
            melden(f"{wo}: eine Feder braucht eine Steifigkeit grösser als null.", wo)
            return FREI
        return feder(Groesse(k, EINHEIT_DER_FEDER[feld]).si)

    querschnitte = {q.kennung: q for q in eintrag.querschnitte}
    stoffe = {m.kennung for m in eintrag.stabmaterialien} | {MATERIAL_DES_QUERSCHNITTS}
    unmoeglich = set()
    for q in eintrag.querschnitte:
        grund = q.fehler()
        if grund:
            unmoeglich.add(q.kennung)
            melden(f"Querschnitt «{q.name}»: {grund}", q.kennung,
                   *[l.kennung for l in eintrag.linien if l.stab and l.querschnitt == q.kennung])

    staebe, paare = [], {}
    for l in eintrag.linien:
        if l.stab:
            q = querschnitte.get(l.querschnitt)
            if q is None:
                melden(f"{l.kennung} ist ein Stab, hat aber "
                       + (f"keinen Querschnitt «{l.querschnitt}»." if l.querschnitt
                          else "keinen Querschnitt."), l.kennung)
            elif q.kennung in unmoeglich:
                pass
            elif not l.material:
                melden(f"{l.kennung} ist ein Stab, hat aber kein Material.", l.kennung)
            elif l.material not in stoffe:
                melden(f"{l.kennung} nimmt das Material «{l.material}», das es im System "
                       f"nicht gibt.", l.kennung)
            else:
                paare[l.kennung] = (q.kennung, l.material)
        staebe.append(Stab(
            name=l.kennung, a=l.von, b=l.bis, traegt=l.stab,
            gelenk_a=l.gelenk_anfang, gelenk_b=l.gelenk_ende,
            quer=halt(l.quer, l.k_quer, "k_quer", l.kennung),
            laengs=halt(l.laengs, l.k_laengs, "k_laengs", l.kennung)))

    lager = [Lager(name=a.kennung, knoten=a.knoten,
                   x=halt(a.x, a.k_x, "k_x", a.kennung),
                   z=halt(a.z, a.k_z, "k_z", a.kennung),
                   phi=halt(a.phi, a.k_phi, "k_phi", a.kennung))
             for a in eintrag.lager]

    lasten: Dict[str, List[Any]] = {lf.kennung: [] for lf in eintrag.lastfaelle}
    for l in eintrag.linien:
        for last in l.lasten:
            if last.lastfall not in lasten:
                meldungen.append(ohne_lastfall(last.kennung or l.kennung))
                continue
            einheit = EINHEIT_DER_LAST[last.art]
            # Verteilt ueber die ganze Linie, einzeln an ihrer Stelle.
            von = 0.0 if last.verteilt else last.stelle / 100.0 * eintrag.laenge(l)
            lasten[last.lastfall].append(Stablast(
                stab=l.kennung, art=last.art,
                wert_a=Groesse(last.wert_a, einheit).si,
                wert_b=None if last.wert_b is None else Groesse(last.wert_b, einheit).si,
                richtung=last.richtung, von=von, bis=None,
                projiziert=last.projiziert))
    for p in eintrag.knotenlasten:
        if p.lastfall not in lasten:
            meldungen.append(ohne_lastfall(p.kennung))
            continue
        wert = Groesse(p.wert, EINHEIT_DER_LAST[p.art]).si
        if p.art == "moment":
            last = Knotenlast(p.knoten, M=wert)
        elif p.richtung is Lastrichtung.WAAGRECHT:
            last = Knotenlast(p.knoten, Fx=wert)
        else:
            last = Knotenlast(p.knoten, Fz=-wert)
        lasten[p.lastfall].append(last)

    faktoren, hinweise = beiwerte(eintrag.kombinationen, eintrag.lastfaelle)
    meldungen.extend(hinweise)
    kombinationen = [Kombination(name, je_fall) for name, je_fall in faktoren]

    system = System(
        knoten=[Knoten(k.kennung, k.x, k.z) for k in eintrag.knoten],
        staebe=staebe, lager=lager,
        lastfaelle=[Lastfall(lf.name, lasten[lf.kennung]) for lf in eintrag.lastfaelle],
        kombinationen=kombinationen)
    return Modell(system=system, paare=paare, meldungen=meldungen,
                  eigengewicht=eigen[0].name if eigen else None)



def bauen(art: "Bauteilart", eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Balkensystem: das Stabwerk der Beschreibung, seine Materialien und
    Querschnitte aufgeloest. Hart scheitert nur ein Verweis, den es nicht
    gibt -- ein Beton, eine Platte, eine Querschnittsanalyse --; was dem
    System selbst fehlt, steht in seinen Meldungen, und der Rest des
    Projekts rechnet.
    """
    wo = f"Balkensystem '{eintrag.name}'"
    modell = modell_von(eintrag)
    querschnitte = [_stabquerschnitt(q, aufbau, wo) for q in eintrag.querschnitte]
    paare, meldungen = _paare(eintrag, modell, aufbau, wo)
    system = Balkensystem(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        system=modell.system, paare=paare, meldungen=meldungen, querschnitte=querschnitte,
        eigengewicht=modell.eigengewicht)
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag.kennung, eintrag.name, art, system,
                   weitere_ziele=system.ziele(), bezuege=tuple(system.bezuege))


def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt:
    """
    Woher A und I eines Querschnitts kommen -- hier wird seine Art
    aufgeloest. Die Platte oder Analyse dazu muss es geben.
    """
    if q.art is Querschnittsart.VORLAGE:
        vorlage = q.stabvorlage()
        return NachVorlage(kennung=q.kennung, name=q.name, herkunft=vorlage.name,
                           fehler=q.fehler() or "", vorlage=vorlage,
                           masse=q.masse_mit_vorgaben())
    if q.art is Querschnittsart.KENNWERTE:
        return VonHand(kennung=q.kennung, name=q.name, herkunft="von Hand",
                       fehler=q.fehler() or "", masse=dict(q.masse))
    if q.art is Querschnittsart.PLATTE:
        platte = aufbau.querschnitte.get(q.bezug)
        if platte is None:
            raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Platte "
                                f"'{q.bezug}', die es im Projekt nicht gibt.")
        return AusPlatte(kennung=q.kennung, name=q.name, herkunft=f"Platte «{platte.name}»",
                         bezug=q.bezug,
                         quelle={"b": platte.id_von("b"), "h": platte.id_von("h")},
                         eq=_modulfrage(q, ModulAusPlatte(platte)))
    analyse = aufbau.querschnittsanalysen.get(q.bezug)
    if analyse is None and q.bezug in aufbau.leere_analysen:
        # Eine leere Analyse gibt es, nur traegt sie noch nichts: der Stab
        # rechnet nicht, das Projekt schon.
        name = aufbau.leere_analysen[q.bezug]
        return AusAnalyse(kennung=q.kennung, name=q.name,
                          herkunft=f"Querschnittsanalyse «{name}»", bezug=q.bezug,
                          fehler=f"Die Querschnittsanalyse «{name}» ist noch leer.")
    if analyse is None:
        raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Querschnittsanalyse "
                            f"'{q.bezug}', die es im Projekt nicht gibt.")
    return AusAnalyse(kennung=q.kennung, name=q.name,
                      herkunft=f"Querschnittsanalyse «{analyse.name}»", bezug=q.bezug,
                      quelle={"A": analyse.id_von("A"), "I": analyse.id_von("I_y")},
                      eq=_modulfrage(q, ModulAusAnalyse(analyse)),
                      flaechen=tuple(f.punkte for f in analyse.flaechen))


def _modulfrage(q: StabquerschnittEintrag, quelle) -> Optional[Modulfrage]:
    """Die Frage nach dem E_eq eines Querschnitts -- nur, wenn er es nehmen soll."""
    return Modulfrage(quelle, q.eq.N, q.eq.M, q.eq.wahl) if q.e_modul == "e_eq" else None


def _paare(eintrag: BalkensystemEintrag, modell: Modell, aufbau: Aufbau,
           wo: str) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]:
    """
    Je tragenden Stab sein Querschnitt und sein Material, aufgeloest --
    «gemäss Querschnitt» wird zum Beton der Platte oder Analyse. Traegt das
    Material nicht, sagt es eine Meldung, und das System rechnet nicht.
    """
    querschnitte = {q.kennung: q for q in eintrag.querschnitte}
    materialien = {m.kennung: m for m in eintrag.stabmaterialien}
    paare: Dict[str, Tuple[str, Stabmaterial]] = {}
    meldungen = list(modell.meldungen)
    for stab, (q, kennung) in modell.paare.items():
        if kennung == MATERIAL_DES_QUERSCHNITTS:
            material, grund = _material_des_querschnitts(querschnitte[q], aufbau)
            if grund:
                grund = f"{stab} nimmt das Material gemäss Querschnitt, aber {grund}"
        else:
            material, grund = _stabmaterial(materialien[kennung], aufbau, wo)
            if grund:
                grund = f"{stab} nimmt das Material {kennung}, aber {grund}"
        if material is None:
            meldungen.append(Meldung(grund, (stab, q, kennung), True))
            continue
        paare[stab] = (q, material)
    return paare, meldungen


def _beton(kennung: str, aufbau: Aufbau, wo: str) -> Baustoff:
    """Ein Beton des Projekts -- einen Verweis ins Leere gibt es nicht."""
    stoff = aufbau.baustoffe.get(kennung)
    if stoff is None:
        raise ProjektFehler(f"{wo}: das Material '{kennung}' gibt es im Projekt nicht.")
    return stoff


def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau,
                  wo: str) -> Tuple[Optional[Stabmaterial], str]:
    """
    Ein Material des Systems, aufgeloest: ein Beton des Projekts oder ein
    eigenes. Traegt es nicht, ist es ``None``, und der zweite Teil sagt
    warum -- klein beginnend, er folgt auf ein «aber».
    """
    if m.art == "eigen":
        return Stabmaterial(m.kennung, m.name or m.kennung, E=m.E, rho=m.rho), ""
    if not m.beton:
        return None, "bei ihm ist kein Beton gewählt."
    stoff = _beton(m.beton, aufbau, wo)
    if stoff.art.value != "beton":
        return None, (f"«{stoff.name}» ist kein Beton – ein Material des Systems ist ein "
                      f"Beton des Projekts oder ein eigenes.")
    return Stabmaterial(m.kennung, stoff.name, stoff=stoff), ""


def _material_des_querschnitts(q: StabquerschnittEintrag,
                               aufbau: Aufbau) -> Tuple[Optional[Stabmaterial], str]:
    """
    Das Material, das ein Querschnitt mitbringt: der Beton einer Platte, das
    eine Material der Flaechen einer Analyse. Sonst ``None``, und der zweite
    Teil sagt, warum.
    """
    if not q.art.aus_bauteil:
        return None, (f"«{q.name}» ist "
                      f"{'nach Vorlage' if q.art is Querschnittsart.VORLAGE else 'von Hand'} und "
                      f"bringt keines mit – das tut nur eine Platte oder Querschnittsanalyse.")
    if q.art is Querschnittsart.PLATTE:
        platte = aufbau.querschnitte.get(q.bezug)
        stoffe = [platte.beton] if platte is not None else []
    else:
        analyse = aufbau.querschnittsanalysen.get(q.bezug)
        if analyse is None:
            return None, f"die Querschnittsanalyse von «{q.name}» ist noch leer."
        stoffe = list({id(f.stoff): f.stoff for f in analyse.flaechen if f.stoff is not None}.values())
        if len(stoffe) > 1:
            return None, (f"die Flächen von «{q.name}» sind aus "
                          f"{' und '.join(s.name for s in stoffe)} – das Material von Hand wählen.")
    if not stoffe:
        return None, f"«{q.name}» bringt keines mit."
    return Stabmaterial(MATERIAL_DES_QUERSCHNITTS, stoffe[0].name, stoff=stoffe[0],
                        vom_querschnitt=True), ""
