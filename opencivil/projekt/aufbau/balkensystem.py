"""
opencivil/projekt/aufbau/balkensystem.py -- ein Balkensystem wird Rechnung.

VERANTWORTUNG:
Aus einem :class:`~opencivil.projekt.balkensystem.BalkensystemEintrag` das
Stabwerk in SI mit seinen Meldungen (:func:`modell_von`) und daraus die
Rechnung mit aufgeloesten Materialien und Querschnitten (:func:`bauen`). Ein
Material ist ein Beton oder Baustahl des Projekts oder ein eigenes. Die Art eines
Querschnitts wird hier aufgeloest, einmal: je Art eine Klasse
(:mod:`~opencivil.stabwerk.stabquerschnitt`). Ein Querschnitt kann eine
Platte oder eine Querschnittsanalyse des Projekts nehmen; die muessen dann
schon gebaut sein -- darum kommt das Balkensystem in
:data:`~opencivil.projekt.aufbau.BAUTEILE` nach ihnen. Von dort kommt auch
das Material einer Linie «gemäss Querschnitt»: der Beton der Platte oder
der Analyse.

GETEILT MIT DEM RAUM:
Was das 3D-Balkensystem (:mod:`~opencivil.projekt.aufbau.balkensystem3d`)
gleich macht, steht hier und wird dort benutzt: die :class:`Uebersetzung`
prueft Faelle und Kennungen und uebersetzt Stabfelder, Lager und Lasten;
:func:`stabwerk_bauen` loest Materialien und Querschnitte auf;
:func:`form_von` macht aus einer Vorlage, einem Profil oder Kennwerten von
Hand die Form eines Querschnitts.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.einheiten import Einheit, Groesse
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.projekt.balkensystem import (
    EINHEIT_DER_FEDER, EINHEIT_DER_LAST, MATERIAL_DES_QUERSCHNITTS, BalkensystemEintrag,
    Profilachse, Querschnittsart, StabmaterialEintrag, StabquerschnittEintrag,
)
from opencivil.projekt.lesen import ProjektFehler
from opencivil.projekt.staebe import StabquerschnittBasis
from opencivil.spannungsanalyse.modul import ModulAusAnalyse, ModulAusPlatte, Modulfrage
from opencivil.stabwerk.profiltabelle import PROFILE
from opencivil.stabwerk.rechnung import Balkensystem, Materialkennwert, Stabmaterial
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



class Uebersetzung:
    """
    Was ein Stabwerk in der Ebene und eines im Raum gleich in SI uebersetzen
    und pruefen: Kennungen, Faelle, Querschnitte, Paare aus Querschnitt und
    Material, Lager, Federn, Lasten und Kombinationen -- in dieser Folge
    melden sie, was nicht stimmt. Was der Raum anders macht, baut die
    Funktion ``modell_von`` des Systems mit den Klassen ihres Rechenkerns.

    Ein Stab ohne Querschnitt oder Material -- oder mit einem Material,
    das es im System nicht gibt --, ein Querschnitt mit unmoeglichen
    Massen und eine Feder ohne Steifigkeit sind Fehler, die die Meldungen
    nennen: gerechnet wird dann nicht -- und nicht etwa mit einem Stab
    weniger. Ob ein Material traegt, weiss erst der Aufbau: er kennt die
    Materialien des Projekts. Eine Last, deren Lastfall es nicht gibt, und ein
    Beiwert dafuer bleiben mit einem Hinweis weg.
    """

    def __init__(self, eintrag: Any, einheit_der_feder: Mapping[str, Einheit],
                 weitere_stoffe: Sequence[str] = ()) -> None:
        """``weitere_stoffe``: was eine Linie als Material nehmen kann, ohne dass es im System steht."""
        self.eintrag = eintrag
        self.einheit_der_feder = einheit_der_feder
        self.meldungen: List[Meldung] = list(faelle_pruefen(eintrag.lastfaelle,
                                                            eintrag.kombinationen))
        for was, liste in (("Knoten", eintrag.knoten), ("Linien", eintrag.linien),
                           ("Lager", eintrag.lager), ("Lasten", eintrag.alle_lasten()),
                           ("Materialien", eintrag.stabmaterialien),
                           ("Querschnitte", eintrag.querschnitte),
                           ("Lastfälle", eintrag.lastfaelle),
                           ("Kombinationen", eintrag.kombinationen)):
            self.meldungen.extend(doppelte_kennungen(was, liste))
        self.querschnitte = {q.kennung: q for q in eintrag.querschnitte}
        self.stoffe = {m.kennung for m in eintrag.stabmaterialien} | set(weitere_stoffe)
        self.unmoeglich = set()
        for q in eintrag.querschnitte:
            grund = q.fehler()
            if grund:
                self.unmoeglich.add(q.kennung)
                self.melden(f"Querschnitt «{q.name}»: {grund}", q.kennung,
                            *[l.kennung for l in eintrag.linien
                              if l.stab and l.querschnitt == q.kennung])
        self.paare: Dict[str, Tuple[str, str]] = {}
        self.lasten: Dict[str, List[Any]] = {lf.kennung: [] for lf in eintrag.lastfaelle}

    def melden(self, text: str, *elemente: str, fehler: bool = True) -> None:
        self.meldungen.append(Meldung(text, tuple(elemente), fehler))

    def halt(self, teil: Any, richtung: str) -> Halt:
        """Wie ein Lager oder eine Linie in ``richtung`` haelt -- die Feder im Feld ``k_<richtung>``."""
        art, k = getattr(teil, richtung), getattr(teil, f"k_{richtung}")
        if art == "frei":
            return FREI
        if art == "fest":
            return FEST
        if k <= 0.0:
            self.melden(f"{teil.kennung}: eine Feder braucht eine Steifigkeit grösser als null.",
                        teil.kennung)
            return FREI
        return feder(Groesse(k, self.einheit_der_feder[f"k_{richtung}"]).si)

    def stab(self, l: Any) -> Dict[str, Any]:
        """
        Was ein Stab des Rechenkerns von seiner Linie hat, Linienlager
        inbegriffen -- und, wenn sie ein Stab ist, ihr Paar aus Querschnitt
        und Material, geprueft.
        """
        if l.stab:
            q = self.querschnitte.get(l.querschnitt)
            if q is None:
                self.melden(f"{l.kennung} ist ein Stab, hat aber "
                            + (f"keinen Querschnitt «{l.querschnitt}»." if l.querschnitt
                               else "keinen Querschnitt."), l.kennung)
            elif q.kennung in self.unmoeglich:
                pass
            elif not l.material:
                self.melden(f"{l.kennung} ist ein Stab, hat aber kein Material.", l.kennung)
            elif l.material not in self.stoffe:
                self.melden(f"{l.kennung} nimmt das Material «{l.material}», das es im System "
                            f"nicht gibt.", l.kennung)
            else:
                self.paare[l.kennung] = (q.kennung, l.material)
        return dict(name=l.kennung, a=l.von, b=l.bis, traegt=l.stab,
                    gelenk_a=l.gelenk_anfang, gelenk_b=l.gelenk_ende,
                    **{r: self.halt(l, r) for r in self.eintrag.LINIENLAGER})

    def lager(self, klasse: type) -> List[Any]:
        """Die Lager, je Richtung gehalten wie beschrieben."""
        return [klasse(name=a.kennung, knoten=a.knoten,
                       **{r: self.halt(a, r) for r in self.eintrag.LAGERFELDER})
                for a in self.eintrag.lager]

    def stablasten(self, klasse: type) -> None:
        """Die Lasten auf den Linien, in SI -- verteilt ueber die ganze Linie, einzeln an ihrer Stelle."""
        for l in self.eintrag.linien:
            for last in l.lasten:
                if last.lastfall not in self.lasten:
                    self.meldungen.append(ohne_lastfall(last.kennung or l.kennung))
                    continue
                einheit = EINHEIT_DER_LAST[last.art]
                von = 0.0 if last.verteilt else last.stelle / 100.0 * self.eintrag.laenge(l)
                self.lasten[last.lastfall].append(klasse(
                    stab=l.kennung, art=last.art,
                    wert_a=Groesse(last.wert_a, einheit).si,
                    wert_b=None if last.wert_b is None else Groesse(last.wert_b, einheit).si,
                    richtung=last.richtung, von=von, bis=None,
                    projiziert=last.projiziert))

    def knotenlasten(self, last_von: Callable[[Any, float], Any]) -> None:
        """Die Lasten an den Knoten -- ``last_von`` macht aus einer und ihrem Wert in SI die des Rechenkerns."""
        for p in self.eintrag.knotenlasten:
            if p.lastfall not in self.lasten:
                self.meldungen.append(ohne_lastfall(p.kennung))
                continue
            self.lasten[p.lastfall].append(last_von(p, Groesse(p.wert, EINHEIT_DER_LAST[p.art]).si))

    def modell(self, system: type, knoten: type, staebe: List[Any], lager: List[Any]) -> Modell:
        """Das Modell, mit den Kombinationen -- ``system`` und ``knoten`` die Klassen des Rechenkerns."""
        e = self.eintrag
        faktoren, hinweise = beiwerte(e.kombinationen, e.lastfaelle)
        self.meldungen.extend(hinweise)
        eigen = [lf for lf in e.lastfaelle if lf.eigengewicht]
        return Modell(
            system=system(
                knoten=[knoten(k.kennung, *(getattr(k, a) for a in e.ACHSEN)) for k in e.knoten],
                staebe=staebe, lager=lager,
                lastfaelle=[Lastfall(lf.name, self.lasten[lf.kennung]) for lf in e.lastfaelle],
                kombinationen=[Kombination(name, je_fall) for name, je_fall in faktoren]),
            paare=self.paare, meldungen=self.meldungen,
            eigengewicht=eigen[0].name if eigen else None)


def modell_von(eintrag: BalkensystemEintrag) -> Modell:
    """Das Stabwerk zum Rechnen, in SI (:mod:`opencivil.stabwerk.modell`) -- siehe :class:`Uebersetzung`."""
    u = Uebersetzung(eintrag, EINHEIT_DER_FEDER, weitere_stoffe=(MATERIAL_DES_QUERSCHNITTS,))
    staebe = [Stab(**u.stab(l)) for l in eintrag.linien]
    lager = u.lager(Lager)
    u.stablasten(Stablast)
    u.knotenlasten(_knotenlast)
    return u.modell(System, Knoten, staebe, lager)


def _knotenlast(p: Any, wert: float) -> Knotenlast:
    """Ein Moment, eine Kraft waagrecht nach rechts oder senkrecht nach unten."""
    if p.art == "moment":
        return Knotenlast(p.knoten, M=wert)
    if p.richtung is Lastrichtung.WAAGRECHT:
        return Knotenlast(p.knoten, Fx=wert)
    return Knotenlast(p.knoten, Fz=-wert)



def bauen(art: "Bauteilart", eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Balkensystem: das Stabwerk der Beschreibung, seine Materialien und
    Querschnitte aufgeloest. Hart scheitert nur ein Verweis, den es nicht
    gibt -- ein Beton, eine Platte, eine Querschnittsanalyse --; was dem
    System selbst fehlt, steht in seinen Meldungen, und der Rest des
    Projekts rechnet.
    """
    modell = modell_von(eintrag)
    querschnitte = [_stabquerschnitt(q, aufbau, eintrag.wo) for q in eintrag.querschnitte]
    return stabwerk_bauen(Balkensystem, art, eintrag, aufbau, modell, querschnitte)


def stabwerk_bauen(klasse: type, art: "Bauteilart", eintrag: Any, aufbau: Aufbau, modell: Modell,
                   querschnitte: List[Stabquerschnitt]) -> Bauteil:
    """Die Rechnung eines Stabwerks der Klasse ``klasse`` -- in der Ebene und im Raum."""
    paare, meldungen = _paare(eintrag, modell, aufbau, klasse.MATERIALKENNWERTE)
    system = klasse(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        system=modell.system, paare=paare, meldungen=meldungen, querschnitte=querschnitte,
        eigengewicht=modell.eigengewicht)
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag.kennung, eintrag.name, art, system,
                   weitere_ziele=system.ziele(), bezuege=tuple(system.bezuege))


def form_von(q: StabquerschnittBasis, wo: str,
             achse: Optional[Profilachse] = None) -> Stabquerschnitt:
    """
    Ein Querschnitt nach Vorlage, als Stahlprofil oder von Hand -- in der
    Ebene und im Raum. Ein Profil biegt sich in der Ebene um ``achse``, im
    Raum um beide.
    """
    if q.art is Querschnittsart.VORLAGE:
        vorlage = q.stabvorlage()
        return NachVorlage(kennung=q.kennung, name=q.name, herkunft=vorlage.name,
                           fehler=q.fehler() or "", vorlage=vorlage,
                           masse=q.masse_mit_vorgaben())
    if q.art is Querschnittsart.PROFIL:
        profil = PROFILE.get(q.profil)
        if profil is None:
            raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt das Profil "
                                f"«{q.profil}», das es in der Tabelle nicht gibt.")
        form = NachVorlage(kennung=q.kennung, name=q.name, herkunft=q.profil,
                           fehler=q.fehler() or "", vorlage=profil.form, masse=dict(profil.masse))
        return form if achse is None else replace(
            form, herkunft=f"{q.profil}, {achse.beschriftung}", traegheit=achse.traegheit)
    return VonHand(kennung=q.kennung, name=q.name, herkunft="von Hand",
                   fehler=q.fehler() or "", masse=dict(q.masse))


def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt:
    """
    Woher A und I eines Querschnitts kommen -- hier wird seine Art
    aufgeloest. Die Platte oder Analyse dazu muss es geben.
    """
    if not q.art.aus_bauteil:
        return form_von(q, wo, q.achse)
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


def _paare(eintrag: Any, modell: Modell, aufbau: Aufbau, kennwerte: Sequence[Materialkennwert]
           ) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]:
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
            material, grund = _stabmaterial(materialien[kennung], aufbau, eintrag.wo,
                                            kennwerte)
            if grund:
                grund = f"{stab} nimmt das Material {kennung}, aber {grund}"
        if material is None:
            meldungen.append(Meldung(grund, (stab, q, kennung), True))
            continue
        paare[stab] = (q, material)
    return paare, meldungen


def _baustoff(kennung: str, aufbau: Aufbau, wo: str) -> Baustoff:
    """Ein Material des Projekts -- einen Verweis ins Leere gibt es nicht."""
    stoff = aufbau.baustoffe.get(kennung)
    if stoff is None:
        raise ProjektFehler(f"{wo}: das Material '{kennung}' gibt es im Projekt nicht.")
    return stoff


def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau, wo: str,
                  kennwerte: Sequence[Materialkennwert]) -> Tuple[Optional[Stabmaterial], str]:
    """
    Ein Material des Systems, aufgeloest: ein Beton oder Baustahl des
    Projekts oder ein eigenes mit den ``kennwerte`` von Hand. Traegt es
    nicht, ist es ``None``, und der zweite Teil sagt warum -- klein
    beginnend, er folgt auf ein «aber».
    """
    if m.art == "eigen":
        return Stabmaterial(m.kennung, m.name or m.kennung,
                            werte={k.kurzname: getattr(m, k.kurzname) for k in kennwerte}), ""
    art = Baustoffart(m.art)
    if not m.stoff:
        return None, f"bei ihm ist kein {art.beschriftung} gewählt."
    stoff = _baustoff(m.stoff, aufbau, wo)
    if stoff.art is not art:
        return None, f"«{stoff.name}» ist kein {art.beschriftung}."
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
