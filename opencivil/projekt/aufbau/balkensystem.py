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
:func:`stabquerschnitt_von` loest die Art eines Querschnitts auf -- eine
Vorlage, ein Profil oder Kennwerte von Hand (:func:`form_von`), eine Platte
oder eine Querschnittsanalyse.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from opencivil.core.einheiten import Groesse
from opencivil.material.basis import Baustoff, Baustoffart
from opencivil.projekt.balkensystem import (
    EINHEIT_DER_LAST, BalkensystemEintrag, Knotenlastart, Profilachse, StabmaterialEintrag,
)
from opencivil.projekt.lesen import ProjektFehler, als_groesse
from opencivil.projekt.staebe import (
    MATERIAL_DES_QUERSCHNITTS, Querschnittsart, StabquerschnittBasis, aufgezaehlt,
)
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
from opencivil.projekt.aufbau.kern import (
    Aufbau, Bauteil, Grund, Unfertiges, materialgrund, stoffe_von,
)

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
        return not any(m.haelt_an for m in self.meldungen)



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

    def __init__(self, eintrag: Any, weitere_stoffe: Sequence[str] = ()) -> None:
        """``weitere_stoffe``: was eine Linie als Material nehmen kann, ohne dass es im System steht."""
        self.eintrag = eintrag
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

    def melden(self, text: str, *elemente: str, fehler: bool = True, unfertig: bool = False) -> None:
        self.meldungen.append(Meldung(text, tuple(elemente), fehler, unfertig))

    def halt(self, teil: Any, richtung: str) -> Halt:
        """
        Wie ein Lager oder eine Linie in ``richtung`` haelt -- die Feder im
        Feld ``k_<richtung>``, in dessen Einheit.
        """
        art, k = getattr(teil, richtung), als_groesse(teil, f"k_{richtung}")
        if art == "frei":
            return FREI
        if art == "fest":
            return FEST
        if k.si <= 0.0:
            self.melden(f"{teil.kennung}: eine Feder braucht eine Steifigkeit grösser als null.",
                        teil.kennung)
            return FREI
        return feder(k.si)

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
                self.melden(f"{l.kennung} ist ein Stab, hat aber noch kein Material.", l.kennung,
                            fehler=False, unfertig=True)
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
            self.lasten[p.lastfall].append(last_von(p, Groesse(p.wert, p.art.einheit).si))

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
    u = Uebersetzung(eintrag, weitere_stoffe=(MATERIAL_DES_QUERSCHNITTS,))
    staebe = [Stab(**u.stab(l)) for l in eintrag.linien]
    lager = u.lager(Lager)
    u.stablasten(Stablast)
    u.knotenlasten(_knotenlast)
    return u.modell(System, Knoten, staebe, lager)


def _knotenlast(p: Any, wert: float) -> Knotenlast:
    """Ein Moment, eine Kraft waagrecht nach rechts oder senkrecht nach unten."""
    if p.art is Knotenlastart.MOMENT:
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
    querschnitte = [stabquerschnitt_von(q, aufbau, eintrag.wo, q.achse)
                    for q in eintrag.querschnitte]
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
    return Bauteil(eintrag, art, system,
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
            raise ProjektFehler(f"der Querschnitt «{q.name}» nimmt das Profil "
                                f"«{q.profil}», das es in der Tabelle nicht gibt.", wo=wo)
        form = NachVorlage(kennung=q.kennung, name=q.name, herkunft=q.profil,
                           fehler=q.fehler() or "", vorlage=profil.form, masse=dict(profil.masse))
        return form if achse is None else replace(
            form, herkunft=f"{q.profil}, {achse.beschriftung}", traegheit=achse.traegheit)
    return VonHand(kennung=q.kennung, name=q.name, herkunft="von Hand",
                   fehler=q.fehler() or "", masse=dict(q.kennwerte))


def stabquerschnitt_von(q: StabquerschnittBasis, aufbau: Aufbau, wo: str,
                        achse: Optional[Profilachse] = None) -> Stabquerschnitt:
    """
    Woher die Kennwerte eines Querschnitts kommen -- hier wird seine Art
    aufgeloest, in der Ebene und im Raum. Die Platte oder Analyse dazu muss
    es geben; ist noch keine gewaehlt oder fehlt ihr noch etwas
    (:attr:`Aufbau.unfertige`), rechnet er nicht, und die Meldung sagt es. Ein Profil biegt sich in der Ebene um ``achse``, im Raum um
    beide (:func:`form_von`).
    """
    if not q.art.aus_bauteil:
        return form_von(q, wo, achse)
    platte = q.art is Querschnittsart.PLATTE
    klasse = AusPlatte if platte else AusAnalyse
    if not q.bezug:
        return klasse(kennung=q.kennung, name=q.name, herkunft=q.art.kurz, bezug="",
                      fehler=q.fehler() or "")
    welche = q.art.bauteil
    bauteil = (aufbau.querschnitte if platte else aufbau.querschnittsanalysen).get(q.bezug)
    if bauteil is None:
        unfertig = aufbau.unfertige.get(q.bezug)
        if unfertig is None:
            raise ProjektFehler(f"der Querschnitt «{q.name}» nimmt die {welche} "
                                f"'{q.bezug}', die es im Projekt nicht gibt.", wo=wo)
        # Es gibt sie, nur fehlt ihr noch etwas: der Stab rechnet nicht, das
        # Projekt schon.
        return klasse(kennung=q.kennung, name=q.name, herkunft=f"{welche} «{unfertig.name}»",
                      bezug=q.bezug, fehler=_rechnet_nicht(welche, unfertig))
    if platte:
        return AusPlatte(kennung=q.kennung, name=q.name, herkunft=f"Platte «{bauteil.name}»",
                         bezug=q.bezug,
                         quelle={"b": bauteil.id_von("b"), "h": bauteil.id_von("h")},
                         eq=_modulfrage(q, ModulAusPlatte(bauteil),
                                        stoffe_von(aufbau, bauteil.baustoffe)))
    analyse = bauteil
    return AusAnalyse(kennung=q.kennung, name=q.name,
                      herkunft=f"Querschnittsanalyse «{analyse.name}»", bezug=q.bezug,
                      quelle={"I": analyse.id_von("I_y"),
                              **{k: analyse.id_von(k) for k in ("A", "I_y", "I_z", "I_T", "I_yz")}},
                      eq=_modulfrage(q, ModulAusAnalyse(analyse),
                                     stoffe_von(aufbau, analyse.baustoffe)),
                      flaechen=tuple(f.punkte for f in analyse.flaechen))


def _rechnet_nicht(welche: str, unfertig: Unfertiges) -> str:
    """Der Satz zu einer Platte oder Analyse, der noch etwas fehlt -- klein beginnend."""
    return f"die {welche} «{unfertig.name}» rechnet nicht ({unfertig.grund})."


def _modulfrage(q: StabquerschnittBasis, quelle,
                stoffe: Mapping[str, Baustoff]) -> Optional[Modulfrage]:
    """
    Die Frage nach dem E_eq eines Querschnitts -- nur, wenn er es nehmen soll;
    mit den Werten je Material der Platte oder Analyse, aus der er kommt.
    """
    if q.e_modul != "e_eq":
        return None
    return Modulfrage(quelle, q.eq.N, q.eq.M, q.eq.wahl(stoffe))


def _paare(eintrag: Any, modell: Modell, aufbau: Aufbau, kennwerte: Sequence[Materialkennwert]
           ) -> Tuple[Dict[str, Tuple[str, Stabmaterial]], List[Meldung]]:
    """
    Je tragenden Stab sein Querschnitt und sein Material, aufgeloest --
    «gemäss Querschnitt» wird zum Beton der Platte oder Analyse. Traegt das
    Material nicht, sagt es eine Meldung, und das System rechnet nicht: eine
    je Material, mit allen Staeben, die es nehmen -- bis 2026-11-19 eine je
    Stab, und ein geloeschter Beton gab so viele gleiche Zeilen wie Staebe.
    «gemäss Querschnitt» heisst je Querschnitt etwas anderes.
    """
    querschnitte = {q.kennung: q for q in eintrag.querschnitte}
    materialien = {m.kennung: m for m in eintrag.stabmaterialien}
    paare: Dict[str, Tuple[str, Stabmaterial]] = {}
    meldungen = list(modell.meldungen)
    aufgeloest: Dict[Tuple[Optional[str], str], Tuple[Optional[Stabmaterial], Optional[Grund]]] = {}
    ohne: Dict[Tuple[Optional[str], str], List[Tuple[str, str]]] = {}
    for stab, (q, kennung) in modell.paare.items():
        gemaess = kennung == MATERIAL_DES_QUERSCHNITTS
        schluessel = (q if gemaess else None, kennung)
        if schluessel not in aufgeloest:
            aufgeloest[schluessel] = (_material_des_querschnitts(querschnitte[q], aufbau) if gemaess
                                      else _stabmaterial(materialien[kennung], aufbau, kennwerte))
        material = aufgeloest[schluessel][0]
        if material is None:
            ohne.setdefault(schluessel, []).append((stab, q))
            continue
        paare[stab] = (q, material)
    for schluessel, staebe in ohne.items():
        gemaess, kennung = schluessel
        namen = [stab for stab, _ in staebe]
        wer = f"{namen[0]} nimmt" if len(namen) == 1 else f"{aufgezaehlt(namen)} nehmen"
        was = ("das Material gemäss Querschnitt" if gemaess
               else _stabmaterialname(materialien[kennung], aufbau))
        grund = aufgeloest[schluessel][1]
        meldungen.append(Meldung(f"{wer} {was}, aber {grund.text}",
                                 (*namen, *dict.fromkeys(q for _, q in staebe), kennung),
                                 fehler=grund.falsch, unfertig=not grund.falsch))
    return paare, meldungen


def _stabmaterial(m: StabmaterialEintrag, aufbau: Aufbau,
                  kennwerte: Sequence[Materialkennwert]) -> Tuple[Optional[Stabmaterial], Optional[Grund]]:
    """
    Ein Material des Systems, aufgeloest: ein Beton oder Baustahl des
    Projekts oder ein eigenes mit den ``kennwerte`` von Hand. Traegt es
    nicht, ist es ``None``, und der zweite Teil sagt warum -- klein
    beginnend, er folgt auf ein «aber». Ob es den Stoff gibt und ob er von
    der Art ist, sagt dieselbe Regel wie bei jedem Bauteil
    (:func:`materialgrund`); bis 2026-11-19 hielt ein geloeschter das ganze
    System an, und das Zeichenfenster bekam nur einen Fehler.
    """
    if m.art == "eigen":
        return Stabmaterial(m.kennung, m.name or m.kennung,
                            werte={k.kurzname: getattr(m, k.kurzname) for k in kennwerte}), None
    if not m.stoff:
        return None, Grund("es ist noch keiner gewählt.")
    stoff = aufbau.baustoffe.get(m.stoff)
    grund = materialgrund(m.stoff, None if stoff is None else (stoff.art.value, stoff.name), m.art)
    if grund:
        return None, Grund(f"{grund.text}.", grund.falsch)
    return Stabmaterial(m.kennung, stoff.name, stoff=stoff), None


def _stabmaterialname(m: StabmaterialEintrag, aufbau: Aufbau) -> str:
    """
    Wie eine Meldung ein Material des Systems nennt: wie die Liste der
    Materialien -- ein eigenes mit seinem Namen, eines des Projekts mit dem
    Namen des Stoffs. Gibt es den Stoff nicht, nur seine Art; die Kennung
    sieht der Benutzer nirgends (bis 2026-11-19 «das Material M1»).
    """
    if m.art == "eigen":
        return f"das Material «{m.name or m.kennung}»"
    stoff = aufbau.baustoffe.get(m.stoff)
    return f"«{stoff.name}»" if stoff is not None else f"einen {Baustoffart(m.art).beschriftung} des Projekts"


def _material_des_querschnitts(q: StabquerschnittBasis,
                               aufbau: Aufbau) -> Tuple[Optional[Stabmaterial], Optional[Grund]]:
    """
    Das Material, das ein Querschnitt mitbringt: der Beton einer Platte, das
    eine Material der Flaechen einer Analyse. Sonst ``None``, und der zweite
    Teil sagt, warum.
    """
    if not q.art.aus_bauteil:
        return None, Grund(f"«{q.name}» ist "
                           f"{'nach Vorlage' if q.art is Querschnittsart.VORLAGE else 'von Hand'} und "
                           f"bringt keines mit – das tut nur eine Platte oder Querschnittsanalyse.",
                           falsch=True)
    unfertig = aufbau.unfertige.get(q.bezug)
    if unfertig is not None:
        return None, Grund(_rechnet_nicht(q.art.bauteil, unfertig))
    if q.art is Querschnittsart.PLATTE:
        platte = aufbau.querschnitte.get(q.bezug)
        stoffe = [platte.beton] if platte is not None else []
    else:
        analyse = aufbau.querschnittsanalysen.get(q.bezug)
        if analyse is None:
            return None, Grund(f"bei «{q.name}» ist noch keine Querschnittsanalyse gewählt.")
        stoffe = list({id(f.stoff): f.stoff for f in analyse.flaechen if f.stoff is not None}.values())
        if len(stoffe) > 1:
            return None, Grund(f"die Flächen von «{q.name}» sind aus "
                               f"{' und '.join(s.name for s in stoffe)} – das Material von Hand "
                               f"wählen.", falsch=True)
    if not stoffe:
        return None, Grund(f"«{q.name}» bringt keines mit.")
    return Stabmaterial(MATERIAL_DES_QUERSCHNITTS, stoffe[0].name, stoff=stoffe[0],
                        vom_querschnitt=True), None
