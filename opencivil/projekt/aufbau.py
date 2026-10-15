"""
opencivil/projekt/aufbau.py -- aus der Beschreibung ein Rechenwerk.

VERANTWORTUNG:
:func:`aufbauen` macht aus einem :class:`Projekt` Baustoffe, Querschnitte,
Nachweise und Balkensysteme und meldet sie in einem :class:`Rechenwerk` an.
Heraus kommt ein :class:`Aufbau` -- das Werk samt allen Nachweisobjekten und
Systemen, nach Bauteil und Art abgelegt, damit Schnittstelle,
Zwischenspeicher und Bewehrungssuche sie wiederfinden.

Die Beschreibung selbst rechnet nichts; hier wird sie zum ersten Mal
Rechnung. Darum stehen auch die Pruefungen hier, die erst beim Bauen
auffallen koennen -- ein Verweis auf ein geloeschtes Material, eine Platte
ohne Bewehrung.

DIE BAUTEILARTEN:
Platte, Querschnittsanalyse und Balkensystem haben je einen Steckbrief
(:class:`Bauteilart`) in :data:`BAUTEILE` -- Liste in der Datei, Klasse der
Eintraege, Vorsilbe der Kennungen, Namensraum, Baufunktion. Wer alle
Bauteile durchgeht, geht diese Liste durch; eine neue Art kommt dort dazu
und nirgends sonst. Gebaut wird je Eintrag ein :class:`Bauteil`, das seine
Nachweise, Ziele und Bezuege selbst fuehrt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple,
)

from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, KN_PRO_M, M, MM, Groesse,
)
from opencivil.core.berechnung import Nachweis, NachweisUrteil
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.gleichungen.blatt import Gleichungsblatt
from opencivil.material.basis import Baustoff
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl
from opencivil.nachweis.biegung_normalkraft import (
    BiegungNormalkraft, Erfuellungsart, Schnittgroessen,
)
from opencivil.nachweis.duktilitaet import Duktilitaet
from opencivil.nachweis.knicken import Knickfall, Knicken
from opencivil.nachweis.fehlende_bewehrung import (
    Ausgefallen, FehlendeBewehrung,
)
from opencivil.nachweis.mindestbewehrung import (
    Rissnormalkraft, ZwaengungBiegung,
)
from opencivil.nachweis.spannungsbegrenzung import (
    Gebrauchsfall, GrenzeAusRissbreite, GrenzeGegenFliessen,
    Spannungsbegrenzung,
)
from opencivil.nachweis import dehnungsfaecher
from opencivil.nachweis.sproedes_versagen import SproedesVersagen
from opencivil.nachweis.querkraft import Querkraft, Querkraftfall
from opencivil.querschnitt.platte import (
    Bewehrungslage, Plattenquerschnitt, Richtung,
)
from opencivil.projekt.eintraege import (
    Gebrauchsliste, KnickEintrag, KombinationEintrag, MaterialEintrag, SpannungsfallEintrag,
    abgeleiteter_fallname,
)
from opencivil.projekt.balkensystem import BalkensystemEintrag, StabquerschnittEintrag
from opencivil.projekt.lesen import ProjektFehler, schalter_aus
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.nachweis.qa_gebrauch import (
    RissnormalkraftQA, SpannungsbegrenzungQA, ZwaengungBiegungQA,
)
from opencivil.nachweis.qa_knicken import KnickenQA, QAKnickfall
from opencivil.nachweis.richtungsnachweise import DuktilitaetQA, SproedesVersagenQA
from opencivil.nachweis.schiefe_biegung import SchiefeBiegung
from opencivil.nachweis.schubwandnachweis import Schubwandnachweis
from opencivil.querschnitt.analyse import Flaechenteil, Lastfall, Querschnittsanalyse
from opencivil.querschnitt.geometrie import GeometrieFehler
from opencivil.querschnitt.schnittanalyse import Zugseite
from opencivil.stabwerk.rechnung import Balkensystem, Stabquerschnitt

if TYPE_CHECKING:
    from opencivil.projekt.projekt import Projekt


# ===========================================================================
# Aufbau
# ===========================================================================


@dataclass
class Aufbau:
    """Was beim Zusammenbauen eines Projekts entsteht."""

    werk: Rechenwerk
    schnell: bool = False
    """Fuer die Bewehrungssuche gebaut -- siehe :func:`aufbauen`."""

    teile: Dict[str, "Bauteil"] = field(default_factory=dict)
    """Jedes Bauteil nach Kennung, in der Reihenfolge von :data:`BAUTEILE` und der Beschreibung."""

    baustoffe: Dict[str, Baustoff] = field(default_factory=dict)
    querschnitte: Dict[str, Plattenquerschnitt] = field(default_factory=dict)
    nachweise: Dict[str, BiegungNormalkraft] = field(default_factory=dict)
    """
    Schluessel ist ``<querschnitt>.x``.

    Die Richtung steht noch im Schluessel, obwohl es nur eine gibt -- sie sagt
    dem Leser einer Wert-ID, welcher Querschnitt gemeint ist, und die
    Wert-IDs in abgelegten Berichten sollen nicht bei jeder Umstellung
    wechseln.
    """

    querkraft: Dict[str, Querkraft] = field(default_factory=dict)
    duktilitaet: Dict[str, Duktilitaet] = field(default_factory=dict)
    """Schluessel ist die Querschnittskennung -- ein Nachweis je Platte."""

    rissnormalkraft: Dict[str, Rissnormalkraft] = field(default_factory=dict)
    """Schluessel ist ``<querschnitt>.x``."""

    sproede: Dict[str, SproedesVersagen] = field(default_factory=dict)
    """Mindestbewehrung gegen sproedes Versagen, je ``<querschnitt>.x``."""

    zwaengung_biegung: Dict[str, ZwaengungBiegung] = field(default_factory=dict)
    """Zwaengung auf Biegung, je ``<querschnitt>.x``."""

    spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    """Stahlspannung gegen Fliessen unter haeufiger Einwirkung, je ``<querschnitt>.x``."""

    spannung_riss: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    """Stahlspannung aus der Rissbreite unter quasi-staendiger Einwirkung, je ``<querschnitt>.x``."""

    knicken: Dict[str, Knicken] = field(default_factory=dict)
    """Nachweis am verformten System, je Querschnitt -- nur in x-Richtung."""

    fehlende: Dict[str, FehlendeBewehrung] = field(default_factory=dict)
    """
    Je Richtung ohne Bewehrung, fuer die dennoch Einwirkungen angegeben sind.

    Sie rechnen nichts; sie sorgen dafuer, dass in der Zusammenfassung eine
    Zeile mit Erfuellungsgrad null steht statt gar nichts.
    """

    spannungsfaelle: Dict[str, List["SpannungsfallEintrag"]] = field(
        default_factory=dict)
    """
    Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als
    Nachweis. Sie laufen nicht im Rechenwerk: sie haben kein Ziel, das jemand
    anderes brauchen koennte, und nichts haengt von ihnen ab.
    """

    blaetter: Dict[str, Gleichungsblatt] = field(default_factory=dict)
    """Die Blätter analytischer Gleichungen, nach Kennung."""

    querschnittsanalysen: Dict[str, Any] = field(default_factory=dict)
    """Die gezeichneten Querschnitte, nach Kennung -- Bauteile wie die Platten."""

    qa_biegung: Dict[str, SchiefeBiegung] = field(default_factory=dict)
    """Biegung und Normalkraft je Querschnittsanalyse, nach ihrer Kennung."""

    qa_schub: Dict[str, Schubwandnachweis] = field(default_factory=dict)
    """Querkraft und Torsion je Querschnittsanalyse."""

    qa_duktilitaet: Dict[str, DuktilitaetQA] = field(default_factory=dict)
    qa_sproede: Dict[str, SproedesVersagenQA] = field(default_factory=dict)
    qa_rissnormalkraft: Dict[str, RissnormalkraftQA] = field(default_factory=dict)
    qa_zwaengung_biegung: Dict[str, ZwaengungBiegungQA] = field(default_factory=dict)
    qa_spannung_riss: Dict[str, SpannungsbegrenzungQA] = field(default_factory=dict)
    qa_spannung: Dict[str, SpannungsbegrenzungQA] = field(default_factory=dict)
    """Die Gebrauchsnachweise je Querschnittsanalyse, wie bei der Platte."""

    qa_knicken: Dict[str, KnickenQA] = field(default_factory=dict)
    """Knicken je Querschnittsanalyse -- je Fall in seiner Richtung."""

    balkensysteme: Dict[str, Balkensystem] = field(default_factory=dict)
    """Die Balkensysteme, nach Kennung -- Bauteile ohne Nachweise, mit ihrem Ergebnis."""

    warnungen: List[str] = field(default_factory=list)

    #: Die Felder, in denen die Nachweise stehen -- die eine Stelle, an der
    #: ein neuer Nachweis eingetragen wird. Alle sind nach Kennung
    #: geschluesselt (``q1`` oder ``q1.x``) und alle tragen Nachweise mit
    #: ``d_ausnutzung``. Ihre Reihenfolge ist die der Herleitung: in ihr
    #: rechnet ein Bauteil seine Nachweise (:meth:`Bauteil.ziele`).
    NACHWEISFELDER = ("nachweise", "querkraft", "duktilitaet", "fehlende",
                      "rissnormalkraft", "sproede", "zwaengung_biegung",
                      "spannung_riss", "spannung", "knicken",
                      "qa_biegung", "qa_schub", "qa_duktilitaet", "qa_sproede",
                      "qa_rissnormalkraft", "qa_zwaengung_biegung", "qa_spannung_riss",
                      "qa_spannung", "qa_knicken")

    def nachweise_je_feld(self):
        """Alle Nachweise, Feld fuer Feld und in der Reihenfolge der Liste."""
        for feld in self.NACHWEISFELDER:
            yield feld, getattr(self, feld)

    def alle_nachweise(self):
        """Jeden Nachweis einmal, in derselben Reihenfolge wie im Protokoll."""
        for _, eintraege in self.nachweise_je_feld():
            yield from eintraege.values()

    def alle_nachweisziele(self) -> List[str]:
        """Jeden Nachweis als Ziel -- auch einen ohne Lastfall, der nur fuer sein Bild rechnet."""
        return [n.id for n in self.alle_nachweise()]

    def eintragen(self, teil: "Bauteil", feld: str, schluessel: str,
                  nachweis: Nachweis) -> None:
        """
        Einen Nachweis anmelden: im Rechenwerk, in seinem Feld und bei seinem
        Bauteil -- ausser er ist ganz still, und es wird schnell gerechnet.

        Den schnellen Weg nimmt nur die Bewehrungssuche, und die zaehlt
        stille Urteile nicht (:func:`bewehrungssuche.bewerte`). Ein ganz
        stiller Nachweis kann ihr Ergebnis also nicht aendern, er kostet
        nur Zeit -- und bei der Stahlspannung, die immer mitlaeuft, ist
        das der groessere Teil der ganzen Rechnung. Exakt und nicht
        genaehert: gezaehlt wird dasselbe wie vorher.

        Jeder Nachweis geht hier durch, auch die, die nie still sind -- ein
        Weg zum Anmelden, nicht zwei.
        """
        if feld not in self.NACHWEISFELDER:
            # Sonst waere der Nachweis angemeldet, aber kein Ziel: niemand
            # rechnete ihn, und er fehlte in jeder Tabelle -- still.
            raise ValueError(
                f"'{feld}' steht nicht in Aufbau.NACHWEISFELDER. Ein Nachweis "
                f"in diesem Feld waere kein Ziel und fehlte still.")
        if self.schnell and nachweis.still:
            return
        self.werk.registriere(nachweis)
        getattr(self, feld)[schluessel] = nachweis
        teil.nachweise.append((feld, nachweis))

    def bauteile(self) -> List["Bauteil"]:
        """
        Jedes Bauteil, in der Reihenfolge von :data:`BAUTEILE` und der
        Beschreibung: erst die Platten, dann die Querschnittsanalysen, dann
        die Balkensysteme -- sie lesen Werte der beiden anderen.

        Die eine Stelle, die diese Reihenfolge festlegt -- fuer die Rechenziele,
        den Zwischenspeicher und die Zusammenfassung.
        """
        return list(self.teile.values())

    def bauteil(self, kennung: str) -> "Bauteil":
        try:
            return self.teile[kennung]
        except KeyError:
            raise ProjektFehler(f"Ein Bauteil '{kennung}' gibt es im Aufbau nicht.") from None

    def bauteil_von(self, nachweis: Nachweis) -> "Bauteil":
        """Das Bauteil, bei dem ein Nachweis angemeldet ist."""
        for teil in self.teile.values():
            if any(n is nachweis for _, n in teil.nachweise):
                return teil
        raise ProjektFehler(f"Der Nachweis '{nachweis.id}' gehoert zu keinem Bauteil.")

    def ziele_von(self, kennung: str) -> List[str]:
        """Die Rechenziele eines einzelnen Bauteils -- siehe :meth:`Bauteil.ziele`."""
        return self.bauteil(kennung).ziele()

    def ziele_je_bauteil(self) -> List[Tuple[str, List[str]]]:
        """
        Die Rechenziele Bauteil fuer Bauteil, in der Reihenfolge von
        :meth:`bauteile`.

        Die Oberflaeche geht darueber, um je Bauteil zwischenzuspeichern
        (:func:`opencivil.web.dienst._stromabwaerts`); :meth:`alle_ziele`
        haengt sie aneinander. Vorher bildete jede der beiden die Folge
        selbst, und dass sie gleich war, stand nur im Docstring.
        """
        return [(b.kennung, self.ziele_von(b.kennung)) for b in self.bauteile()]

    def alle_ziele(self) -> List[str]:
        """
        Was ein vollstaendiger Lauf rechnet, in der Reihenfolge der Herleitung:
        erst die Baustoffe, dann Platte fuer Platte ihre Eckwerte und
        Nachweise. Wer ohne Oberflaeche rechnet, bekommt so denselben Bericht.
        """
        ziele = self.materialziele()
        for _, eigene in self.ziele_je_bauteil():
            ziele += eigene
        return ziele + self.blattziele()

    def blattziele(self) -> List[str]:
        """Die Blätter zuletzt -- sie lesen Werte der Platten, nie umgekehrt."""
        return [b.id for b in self.blaetter.values()]

    def berichtsziele(self) -> List[str]:
        """
        Was im Bericht steht: Nachweise, was die Bauteile sonst rechnen, Blätter
        -- ohne die Baustoffkennwerte, die niemand braucht.
        """
        return (self.alle_nachweisziele()
                + [z for teil in self.bauteile() for z in teil.weitere_ziele]
                + self.blattziele())

    def urteile_von(self, kennung: str, urteile: Iterable[NachweisUrteil],
                    ) -> List[NachweisUrteil]:
        """
        Die Urteile eines Bauteils -- erkannt an den Nachweisen, die bei ihm
        angemeldet sind.

        Nicht am Namen: den Anzeigetext zu zerlegen hat schon einmal die
        Nachweise mehrerer Platten in dieselbe Tabelle gepackt.
        """
        eigene = {n.id for _, n in self.bauteil(kennung).nachweise}
        return [u for u in urteile if u.raum in eigene]

    def materialziele(self) -> List[str]:
        """
        Saemtliche Kennwerte aller Materialien -- Beton zuerst, dann Betonstahl.

        Gehoert zum Regellauf: ein Material, das noch keine Platte verwendet,
        waere sonst nie Ziel und bliebe ungerechnet -- im Editor staenden dann
        leere Felder, obwohl die Sorte alles hergibt.

        Die Reihenfolge bestimmt zugleich den Aufbau der Herleitung: der Loeser
        arbeitet die Ziele der Reihe nach ab, und das Protokoll folgt ihm. So
        stehen im Bericht erst die Baustoffe und dann die Bauteile.
        """
        nach_art = {"beton": [], "betonstahl": []}
        for stoff in self.baustoffe.values():
            nach_art.setdefault(stoff.art.value, []).extend(
                d.id for d in stoff.definitionen.values())
        return nach_art["beton"] + nach_art["betonstahl"]


@dataclass
class Bauteil:
    """
    Ein gebautes Bauteil und was zu ihm gehoert. Wem ein Nachweis gehoert,
    steht hier -- niemand muss es aus einer Kennung wie «q1.x» zurueckgewinnen.
    """

    kennung: str
    name: str
    art: "Bauteilart"
    objekt: Any
    """Der Plattenquerschnitt, die Querschnittsanalyse oder das Balkensystem."""

    nachweise: List[Tuple[str, Nachweis]] = field(default_factory=list)
    """Feld im :class:`Aufbau` und Nachweis, angemeldet ueber :meth:`Aufbau.eintragen`."""

    weitere_ziele: List[str] = field(default_factory=list)
    """Was es ausser seinen Nachweisen rechnet -- ein Balkensystem seine Querschnitte und sich."""

    bezuege: Tuple[str, ...] = ()
    """Die Bauteile, deren Werte es liest: Platten und Analysen, aus denen ein System Querschnitte nimmt."""

    @property
    def raum(self) -> str:
        """Der Namensraum seiner Werte und Urteile."""
        return self.objekt.id

    def im_feld(self, feld: str) -> List[Nachweis]:
        """Seine Nachweise in einem Feld des :class:`Aufbau`, in der Folge der Anmeldung."""
        return [n for f, n in self.nachweise if f == feld]

    def ziele(self) -> List[str]:
        """
        Was ein Lauf fuer dieses Bauteil rechnet: die Nachweise in der Folge
        von :attr:`Aufbau.NACHWEISFELDER`, dann die weiteren Ziele.
        """
        folge = {feld: i for i, feld in enumerate(Aufbau.NACHWEISFELDER)}
        return ([n.id for _, n in sorted(self.nachweise, key=lambda e: folge[e[0]])]
                + self.weitere_ziele)


def aufbauen(projekt: "Projekt", *, schnell: bool = False) -> Aufbau:
    """
    Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

    Wirft :class:`ProjektFehler`, wenn die Beschreibung nicht stimmig ist --
    etwa wenn ein Querschnitt auf ein geloeschtes Material verweist.

    Mit ``schnell`` lassen Nachweise teure Nebenrechnungen weg, die das
    Urteil nicht aendern -- die Suche nach der Knickgrenzkraft und die
    genaue Resistenzlinie --, und ganz stille Nachweise entstehen gar
    nicht erst. Gedacht fuer das Bewehrungswerkzeug, das hundertfach
    rechnet und nur wissen muss, ob es aufgeht. Fuer eine Herleitung ist
    das nichts: dort soll die Zahl stehen, die auch in der Tabelle steht.
    """
    projekt.pruefen()
    werk = Rechenwerk()
    aufbau = Aufbau(werk=werk, schnell=schnell)

    # Nur wenn mehrere Materialien derselben Art vorkommen, braucht es
    # Indizes an den Symbolen -- sonst waere f_{cd,C30/37} bloss Ballast.
    je_art: Dict[str, int] = {}
    for m in projekt.materialien:
        je_art[m.art] = je_art.get(m.art, 0) + 1
    for eintrag in projekt.materialien:
        index = eintrag.anzeigename if je_art[eintrag.art] > 1 else ""
        aufbau.baustoffe[eintrag.kennung] = _baustoff(eintrag, index)

    # Auch im schnellen Aufbau jedes Bauteil: die Formelsammlung entsteht aus
    # ihm. Die Bewehrungssuche loest nur Nachweisziele, ein System kostet sie
    # also nur das Anmelden.
    for art in BAUTEILE:
        for eintrag in getattr(projekt, art.liste):
            aufbau.teile[eintrag.kennung] = art.bauen(art, eintrag, aufbau)

    # Die Bewehrungssuche braucht keine Blätter -- sie liest nur Urteile.
    if not schnell:
        for eintrag in projekt.gleichungen:
            blatt = Gleichungsblatt(eintrag)
            werk.registriere(blatt)
            aufbau.blaetter[eintrag.kennung] = blatt

    for baustoff in aufbau.baustoffe.values():
        baustoff.ins_rechenwerk(werk)

    _ueberschreibungen_setzen(projekt, werk, aufbau)
    return aufbau


def _platte(art: "Bauteilart", eintrag: QuerschnittEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Eine Platte: der Querschnitt und alle Nachweise, die an ihm haengen.

    Nachgewiesen wird nur die Tragrichtung x. Die y-Lagen stehen im
    Querschnitt -- sie tragen zum Bewehrungsgehalt bei und druecken die
    statische Hoehe von x nach innen --, aber kein Nachweis fragt nach ihnen.
    Vorher lief hier alles doppelt, einmal je Richtung, und die Haelfte der
    Tabelle handelte von einer Richtung, fuer die niemand Schnittgroessen
    hatte.
    """
    querschnitt = _querschnitt(eintrag, aufbau.baustoffe, praefix=f"{art.raum}.{eintrag.kennung}")
    aufbau.querschnitte[eintrag.kennung] = querschnitt
    querschnitt.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, querschnitt)
    schnell = aufbau.schnell

    richtung = Richtung.X
    kennung_x = f"{eintrag.kennung}.x"
    aktiv = [k for k in eintrag.kombinationen if k.aktiv]

    if richtung not in querschnitt.richtungen_mit_bewehrung:
        if aktiv:
            # Ohne Bewehrung laesst sich hier nichts aufstellen. Der
            # Nachweis entfiel frueher stillschweigend; wer eine Einwirkung
            # angegeben hatte, fand sie nirgends wieder.
            aufbau.eintragen(teil, "fehlende", kennung_x, FehlendeBewehrung(
                querschnitt, richtung, _ausgefallene(aktiv, richtung)))
        if eintrag.knickfaelle:
            aufbau.warnungen.append(
                f"Platte '{eintrag.name}': ohne x-Bewehrung kein Knicknachweis.")
    else:
        # Der M-N-Nachweis entsteht auch ohne Schnittgroessen: seine
        # Eckwerte gehoeren dem Querschnitt, nicht der Einwirkung, und der
        # Nachweis gegen sproedes Versagen haelt M_Rd(N=0) dagegen. Ohne die
        # Vergleichslinie, wenn schnell gerechnet wird: sie kostet fast die
        # ganze Zeit dieses Nachweises und wird allein im Diagramm gebraucht.
        # Wer schnell rechnet, sucht eine Bewehrung und sieht dabei kein
        # Diagramm an.
        nachweis = BiegungNormalkraft(
            querschnitt, [_kombination(k) for k in aktiv], richtung,
            wahl=eintrag.tragsicherheit_wahl.wahl, mit_vergleich=not schnell,
            schritte=dehnungsfaecher.SCHRITTE_SUCHE if schnell else dehnungsfaecher.SCHRITTE)
        aufbau.eintragen(teil, "nachweise", kennung_x, nachweis)

        _lagennachweise(eintrag, querschnitt, richtung, nachweis, aufbau, teil)
        _spannungsnachweise(eintrag, querschnitt, richtung, aufbau, teil)

        # Auch ohne V_Ed: dann still, nur fuer das Diagramm.
        aufbau.eintragen(teil, "querkraft", kennung_x, Querkraft(
            querschnitt,
            [Querkraftfall(name=k.name,
                           V_Ed=Groesse(k.V_Ed, KN_PRO_M),
                           M_Ed=Groesse(k.M_Ed, KNM),
                           N_Ed=Groesse(k.N_Ed, KN))
             for k in aktiv if k.V_Ed],
            richtung, nachweis))

        knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
        if knickfaelle:
            aufbau.eintragen(teil, "knicken", eintrag.kennung, Knicken(
                querschnitt, [_knickfall(k) for k in knickfaelle],
                nachweis, verformung=eintrag.knicken_wahl_verformung.wahl,
                widerstand=eintrag.knicken_wahl_widerstand.wahl, schnell=schnell))

    aktive = [s for s in eintrag.spannungsfaelle if s.aktiv]
    if aktive:
        aufbau.spannungsfaelle[eintrag.kennung] = aktive

    if not eintrag.kombinationen:
        aufbau.warnungen.append(
            f"Platte '{eintrag.name}': keine Schnittgrössen → kein "
            f"Tragsicherheitsnachweis.")
    return teil


def _querschnittsanalyse(art: "Bauteilart", eintrag: QuerschnittsanalyseEintrag,
                         aufbau: Aufbau) -> Bauteil:
    """
    Ein gezeichneter Querschnitt: das Bauteil und seine Nachweise.

    Biegung und Normalkraft immer -- ihre Eckwerte gehoeren dem Querschnitt.
    Querkraft und Torsion, sobald ein Lastfall sie hat oder die
    Laengszugkraft zaehlt. Duktilitaet, sproedes Versagen und die Zwaengungen
    immer, still, wenn ausgeschaltet -- wie bei der Platte. Ebenso die
    Stahlspannungen, sobald es Lastfaelle gibt (:func:`_qa_spannungsnachweise`),
    und das Knicken, sobald ein Fall eingeschaltet ist.
    """
    analyse = _analyse(eintrag, aufbau.baustoffe, praefix=f"{art.raum}.{eintrag.kennung}")
    aufbau.querschnittsanalysen[eintrag.kennung] = analyse
    analyse.ins_rechenwerk(aufbau.werk)
    teil = Bauteil(eintrag.kennung, eintrag.name, art, analyse)

    kN, kNm = 1e3, 1e3
    lastfaelle = [
        Lastfall(name=l.name, N=l.N_Ed * kN, M_y=l.M_y_Ed * kNm, M_z=l.M_z_Ed * kNm,
                 V_y=l.V_y_Ed * kN, V_z=l.V_z_Ed * kN, T=l.T_Ed * kNm)
        for l in eintrag.lastfaelle if l.aktiv]

    schub = None
    if any(l.V_z or l.T or (l.V_y and not eintrag.einachsig) for l in lastfaelle) \
            or (eintrag.laengszugkraft and lastfaelle):
        schub = Schubwandnachweis(analyse, lastfaelle, einachsig=eintrag.einachsig,
                                  mit_laengszug=eintrag.laengszugkraft)
        aufbau.eintragen(teil, "qa_schub", eintrag.kennung, schub)
    aufbau.eintragen(teil, "qa_biegung", eintrag.kennung, SchiefeBiegung(
        analyse, lastfaelle, einachsig=eintrag.einachsig,
        laengszug=schub if eintrag.laengszugkraft else None))

    duktilitaet = DuktilitaetQA(analyse, einachsig=eintrag.einachsig,
                                grenze=eintrag.x_d_max)
    duktilitaet.still = not eintrag.duktilitaet
    aufbau.eintragen(teil, "qa_duktilitaet", eintrag.kennung, duktilitaet)
    sproede = SproedesVersagenQA(analyse, einachsig=eintrag.einachsig)
    sproede.still = not eintrag.sproede
    aufbau.eintragen(teil, "qa_sproede", eintrag.kennung, sproede)

    zwang = RissnormalkraftQA(analyse, anforderung=eintrag.rissanforderung,
                              begrenzt=eintrag.zwaengung_begrenzt)
    zwang.still = not eintrag.zwaengung
    aufbau.eintragen(teil, "qa_rissnormalkraft", eintrag.kennung, zwang)
    biegung = ZwaengungBiegungQA(analyse, einachsig=eintrag.einachsig,
                                 anforderung=eintrag.rissanforderung,
                                 kriechzahl=eintrag.zwaengung_biegung_kriechzahl)
    biegung.still = not eintrag.zwaengung_biegung
    aufbau.eintragen(teil, "qa_zwaengung_biegung", eintrag.kennung, biegung)
    _qa_spannungsnachweise(eintrag, analyse, aufbau, teil)

    knickfaelle = [k for k in eintrag.knickfaelle if k.aktiv]
    if knickfaelle:
        aufbau.eintragen(teil, "qa_knicken", eintrag.kennung, KnickenQA(
            analyse, [_knickfall(k, QAKnickfall, richtung=Zugseite(k.richtung))
                      for k in knickfaelle],
            verformung=eintrag.knicken_wahl_verformung.wahl,
            widerstand=eintrag.knicken_wahl_widerstand.wahl, schnell=aufbau.schnell))

    aktive = [s for s in eintrag.spannungsfaelle if s.aktiv]
    if aktive:
        aufbau.spannungsfaelle[eintrag.kennung] = aktive
    return teil


def _balkensystem(art: "Bauteilart", eintrag: BalkensystemEintrag, aufbau: Aufbau) -> Bauteil:
    """
    Ein Balkensystem: das Stabwerk der Beschreibung, seine Querschnitte
    aufgeloest. Hart scheitert nur ein Verweis, den es nicht gibt -- ein
    Material, eine Platte, eine Querschnittsanalyse --; was dem System selbst
    fehlt, steht in seinen Meldungen, und der Rest des Projekts rechnet.
    """
    wo = f"Balkensystem '{eintrag.name}'"
    modell = eintrag.modell()
    stoffe: Dict[str, Baustoff] = {}
    for _, material in modell.paare.values():
        stoff = aufbau.baustoffe.get(material)
        if stoff is None:
            raise ProjektFehler(f"{wo}: das Material '{material}' gibt es im Projekt nicht.")
        stoffe[material] = stoff
    system = Balkensystem(
        name=eintrag.name, kennung=eintrag.kennung, praefix=f"{art.raum}.{eintrag.kennung}",
        system=modell.system, paare=modell.paare, meldungen=modell.meldungen,
        querschnitte=[_stabquerschnitt(q, aufbau, wo) for q in eintrag.querschnitte],
        stoffe=stoffe)
    aufbau.balkensysteme[eintrag.kennung] = system
    system.ins_rechenwerk(aufbau.werk)
    return Bauteil(eintrag.kennung, eintrag.name, art, system,
                   weitere_ziele=system.ziele(), bezuege=tuple(system.bezuege))


def _stabquerschnitt(q: StabquerschnittEintrag, aufbau: Aufbau, wo: str) -> Stabquerschnitt:
    """Woher A und I eines Querschnitts kommen -- die Platte oder Analyse dazu muss es geben."""
    if q.art == "vorlage":
        vorlage = q.stabvorlage()
        return Stabquerschnitt(q.kennung, q.name, q.art, vorlage=vorlage,
                               masse=q.masse_mit_vorgaben(), herkunft=vorlage.name,
                               fehler=q.fehler() or "")
    if q.art == "kennwerte":
        return Stabquerschnitt(q.kennung, q.name, q.art, masse=dict(q.masse),
                               herkunft="von Hand", fehler=q.fehler() or "")
    if q.art == "platte":
        platte = aufbau.querschnitte.get(q.bezug)
        if platte is None:
            raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Platte "
                                f"'{q.bezug}', die es im Projekt nicht gibt.")
        return Stabquerschnitt(q.kennung, q.name, q.art, bezug=q.bezug,
                               quelle={"b": platte.id_von("b"), "h": platte.id_von("h")},
                               herkunft=f"Platte «{platte.name}»")
    analyse = aufbau.querschnittsanalysen.get(q.bezug)
    if analyse is None:
        raise ProjektFehler(f"{wo}: der Querschnitt «{q.name}» nimmt die Querschnittsanalyse "
                            f"'{q.bezug}', die es im Projekt nicht gibt.")
    return Stabquerschnitt(q.kennung, q.name, q.art, bezug=q.bezug,
                           quelle={"A": analyse.id_von("A"), "I": analyse.id_von("I_y")},
                           herkunft=f"Querschnittsanalyse «{analyse.name}»")


def _analyse(eintrag: QuerschnittsanalyseEintrag, baustoffe: Mapping[str, Baustoff],
             *, praefix: str) -> Querschnittsanalyse:
    """
    Aus der Beschreibung das Bauteil -- und aus jedem Fehler der Zeichnung
    einen Satz, der die Analyse nennt.
    """
    wo = f"Querschnittsanalyse '{eintrag.name}'"

    def stoff(kennung: str, was: str, art: str) -> Baustoff:
        gefunden = baustoffe.get(kennung)
        if gefunden is None and not kennung:
            # Kein Material angegeben -- wie bei den Lagen der Platte gilt
            # dann das erste dieser Art im Projekt.
            gefunden = next((s for s in baustoffe.values() if s.art.value == art), None)
        if gefunden is None:
            raise ProjektFehler(f"{wo}: {was} verweist auf das Material '{kennung}', "
                                f"das es nicht (mehr) gibt.")
        if gefunden.art.value != art:
            raise ProjektFehler(f"{wo}: {was} braucht einen "
                                f"{'Beton' if art == 'beton' else 'Betonstahl'}, "
                                f"'{gefunden.name}' ist keiner.")
        return gefunden

    elemente = eintrag.elemente()
    if elemente.fehler:
        # Ein Element ohne Lage laesst sich nicht rechnen -- und es still
        # wegzulassen hiesse, mit einem anderen Querschnitt zu rechnen.
        raise ProjektFehler(f"{wo}: {elemente.fehler[0]['text']}")
    flaechen = [Flaechenteil(name=f["name"], kennung=f["kennung"], punkte=f["punkte"],
                             stoff=stoff(f["material"], f["name"], "beton")
                             if f["material"] else None)
                for f in elemente.polygone]
    staebe = [{**s, "stahl": stoff(s["stahl"], s["name"], "betonstahl")}
              for s in elemente.staebe]
    linien = [{**l, "stahl": stoff(l["stahl"], l["name"], "betonstahl")}
              for l in elemente.linien]
    waende = [{**w, "stahl": stoff(w["stahl"], w["name"], "betonstahl")
               if w["durchmesser"] > 0 else None}
              for w in elemente.waende]
    wahl = {baustoffe[w.material].id: (w.satz, w.betongesetz)
            for w in eintrag.werkstoffwahl if w.material in baustoffe}
    try:
        return Querschnittsanalyse(
            name=eintrag.name, praefix=praefix,
            flaechen=flaechen, staebe=staebe, linien=linien, waende=waende,
            alpha_min=eintrag.alpha_min, alpha_max=eintrag.alpha_max, k_c=eintrag.k_c,
            wahl=wahl)
    except GeometrieFehler as fehler:
        raise ProjektFehler(f"{wo}: {fehler}") from None


def _lagennachweise(eintrag: QuerschnittEintrag, querschnitt: Plattenquerschnitt,
                    richtung: Richtung, nachweis: BiegungNormalkraft,
                    aufbau: Aufbau, teil: Bauteil) -> None:
    """
    Die Nachweise je x-Lage: sproedes Versagen, Zwaengung auf Biegung und
    auf Normalkraft, Duktilitaet.

    Die beiden x-Lagen, von unten nach oben. Beide werden gerechnet; in die
    Zusammenfassung kommt die unguenstigere. Ausgeschaltet heisst still --
    gerechnet wird trotzdem, damit ein Hinweis stehen kann.
    """
    lagen = [l.nummer for l in querschnitt.lagen if l.richtung is richtung]
    if not lagen:
        return
    kennung_x = f"{eintrag.kennung}.x"

    # Die vier Schalter durch denselben Leser wie beim Einlesen. Wer eine
    # alte Beschreibung im Speicher haelt, traegt dort noch eine Liste -- und
    # `[False, False, False, False]` ist als Wahrheit *wahr*. Der Nachweis
    # stuende dann eingeschaltet da, obwohl jeder einzelne Haken aus ist.
    sproede = SproedesVersagen(querschnitt, richtung, lagen, nachweis)
    sproede.still = not schalter_aus(eintrag.sproede)
    aufbau.eintragen(teil, "sproede", kennung_x, sproede)

    biegung = ZwaengungBiegung(
        querschnitt, richtung, lagen,
        anforderung=eintrag.rissanforderung,
        kriechzahl=eintrag.zwaengung_biegung_kriechzahl)
    biegung.still = not schalter_aus(eintrag.zwaengung_biegung)
    aufbau.eintragen(teil, "zwaengung_biegung", kennung_x, biegung)

    zwang = Rissnormalkraft(
        querschnitt, richtung,
        anforderung=eintrag.rissanforderung,
        begrenzt=eintrag.zwaengung_begrenzt)
    zwang.still = not schalter_aus(eintrag.zwaengung)
    aufbau.eintragen(teil, "rissnormalkraft", kennung_x, zwang)

    duktilitaet = Duktilitaet(querschnitt, lagen, grenze=eintrag.x_d_max)
    duktilitaet.still = not schalter_aus(eintrag.duktilitaet)
    aufbau.eintragen(teil, "duktilitaet", eintrag.kennung, duktilitaet)


def _spannungsnachweise(eintrag: QuerschnittEintrag,
                        querschnitt: Plattenquerschnitt, richtung: Richtung,
                        aufbau: Aufbau, teil: Bauteil) -> None:
    """
    Die Stahlspannung, zweimal: aus der Rissbreite unter quasi-staendiger
    Einwirkung (bei jeder Anforderung) und gegen Fliessen unter haeufiger
    (nur bei erhoehter und hoher). Welche wann gilt, weiss die Grenze selbst.
    """
    for feld, liste, grenze in (
            ("spannung_riss", eintrag.quasistaendig, GrenzeAusRissbreite),
            ("spannung", eintrag.haeufig, GrenzeGegenFliessen)):
        if not grenze.gilt_bei(eintrag.rissanforderung):
            continue
        faelle, laute = _gebrauchsfaelle(
            eintrag.kombinationen, liste,
            lambda name, k, faktor: Gebrauchsfall(name=name, M_Ed=Groesse(faktor * k.M_Ed, KNM),
                                                   N_Ed=Groesse(faktor * k.N_Ed, KN)))
        if not faelle:
            continue
        spannung = Spannungsbegrenzung(
            faelle, grenze=grenze(querschnitt, richtung, eintrag.rissanforderung),
            wahl=liste.wahl.wahl)
        spannung.stillstellen([f.name for f in faelle], laute)
        aufbau.eintragen(teil, feld, f"{eintrag.kennung}.x", spannung)


def _qa_spannungsnachweise(eintrag: QuerschnittsanalyseEintrag,
                           analyse: Querschnittsanalyse, aufbau: Aufbau,
                           teil: Bauteil) -> None:
    """Die Stahlspannungen des gezeichneten Querschnitts -- wie bei der Platte, je Grenze."""
    kN = 1e3
    for feld, liste, grenze in (
            ("qa_spannung_riss", eintrag.quasistaendig, GrenzeAusRissbreite),
            ("qa_spannung", eintrag.haeufig, GrenzeGegenFliessen)):
        if not grenze.gilt_bei(eintrag.rissanforderung):
            continue
        faelle, laute = _gebrauchsfaelle(
            eintrag.lastfaelle, liste,
            lambda name, l, faktor: Lastfall(name=name, N=faktor * l.N_Ed * kN,
                                             M_y=faktor * l.M_y_Ed * kN,
                                             M_z=faktor * l.M_z_Ed * kN))
        if not faelle:
            continue
        spannung = SpannungsbegrenzungQA(
            analyse, faelle, grenze=grenze, anforderung=eintrag.rissanforderung,
            wahl=liste.wahl.wahl, einachsig=eintrag.einachsig)
        spannung.stillstellen([f.name for f in faelle], laute)
        aufbau.eintragen(teil, feld, eintrag.kennung, spannung)


def _knickfall(k: KnickEintrag, klasse: type = Knickfall, **mehr: Any) -> Knickfall:
    """Ein Knickfall aus seiner Beschreibung -- kN, kNm und m; ``mehr`` fuer die Analyse."""
    return klasse(name=k.name, N_Ed=Groesse(k.N_Ed, KN), M_Ed_1=Groesse(k.M_Ed_1, KNM),
                  laenge=Groesse(k.laenge, M), knicklaenge=Groesse(k.knicklaenge, M), **mehr)


def _baustoff(eintrag: MaterialEintrag, symbol_index: str) -> Baustoff:
    bauer = {"beton": beton, "betonstahl": betonstahl}[eintrag.art]
    roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
    # Jeder Kennwert dieser beiden Baustoffe ist seiner Natur nach positiv:
    # Festigkeiten, Moduln, Dehnungen, Teilsicherheitsbeiwerte. Eine Null
    # oder ein negativer Wert liefert keine falsche Zahl, sondern gar keine
    # -- gamma_c = 0 endete in einem ZeroDivisionError, ein negatives f_ck
    # in einer komplexen Wurzel. Beides kam als Absturzmeldung beim
    # Benutzer an.
    for topf, wie in ((eintrag.abweichungen, "abweichender Wert"),
                      (eintrag.ueberschreibungen, "überschriebener Wert")):
        for kurzname, zahl in topf.items():
            if zahl <= 0.0:
                raise ProjektFehler(
                    f"'{eintrag.anzeigename}': {kurzname} muss grösser als null "
                    f"sein, angegeben ist {zahl:g} ({wie}).")
    abweichungen = {
        kurzname: Groesse(zahl, roh.definition(kurzname).einheit)
        for kurzname, zahl in eintrag.abweichungen.items()
        if kurzname in roh.definitionen
    }
    return bauer(
        eintrag.sorte,
        name=eintrag.anzeigename,
        praefix=f"{eintrag.art}.{eintrag.kennung}",
        abweichungen=abweichungen,
        symbol_index=symbol_index,
    )


def _querschnitt(
    eintrag: QuerschnittEintrag, baustoffe: Mapping[str, Baustoff], *, praefix: str
) -> Plattenquerschnitt:
    beton_stoff = baustoffe.get(eintrag.beton)
    if beton_stoff is None:
        raise ProjektFehler(
            f"Platte '{eintrag.name}' verweist auf das Material "
            f"'{eintrag.beton}', das es nicht (mehr) gibt.")
    eintrag.masse_pruefen()

    lagen: List[Bewehrungslage] = []
    for nummer, lage in enumerate(eintrag.lagen, start=1):
        stahl = baustoffe.get(lage.stahl)
        if stahl is None and lage.vorhanden:
            raise ProjektFehler(
                f"Die {nummer}. Lage von '{eintrag.name}' verweist auf den Stahl "
                f"'{lage.stahl}', den es nicht (mehr) gibt.")
        lagen.append(Bewehrungslage(
            nummer=nummer,
            richtung=eintrag.richtung_von(nummer),
            stahl=stahl or next(iter(
                s for s in baustoffe.values() if s.art.value == "betonstahl"), None),
            grund=lage.grund.als_posten(),
            zulage=lage.zulage.als_posten(),
            unguenstig=lage.unguenstig,
        ))

    if not any(l.vorhanden for l in lagen):
        raise ProjektFehler(
            f"Platte '{eintrag.name}': ohne Bewehrung lässt sich kein "
            f"Widerstand bestimmen.")

    buegel = eintrag.querkraftbewehrung
    buegel.pruefen(f"Platte '{eintrag.name}'")
    buegelstahl = baustoffe.get(buegel.stahl)
    if buegelstahl is None and buegel.stahl:
        raise ProjektFehler(
            f"Die Querkraftbewehrung von '{eintrag.name}' verweist auf den "
            f"Stahl '{buegel.stahl}', den es nicht (mehr) gibt.")
    if buegelstahl is None:
        # Kein Stahl angegeben -- wie bei den Lagen gilt dann der erste im
        # Projekt. Eine Beschreibung aus der Zeit vor den Buegeln nennt
        # keinen, und daran soll der ganze Lauf nicht scheitern.
        buegelstahl = next(
            (s for s in baustoffe.values() if s.art.value == "betonstahl"), None)
    if buegel.vorhanden and buegelstahl is None:
        raise ProjektFehler(
            f"Die Querkraftbewehrung von '{eintrag.name}' braucht einen "
            f"Betonstahl, im Projekt gibt es aber keinen.")

    return Plattenquerschnitt(
        name=eintrag.name,
        h=Groesse(eintrag.h, MM),
        b=Groesse(eintrag.b, MM),
        beton=beton_stoff,
        lagen=lagen,
        ueberdeckung_unten=Groesse(eintrag.ueberdeckung_unten, MM),
        ueberdeckung_oben=Groesse(eintrag.ueberdeckung_oben, MM),
        d_max=Groesse(eintrag.d_max, MM),
        einlagenhoehe=Groesse(eintrag.einlagenhoehe, MM),
        k_c=Groesse(eintrag.k_c, EINHEITSLOS),
        kriechzahl=Groesse(eintrag.kriechzahl, EINHEITSLOS),
        querkraftbewehrung=(buegel.als_bewehrung(buegelstahl)
                            if buegel.vorhanden else None),
        praefix=praefix,
    )


def _gebrauchsfaelle(
    kombinationen: Sequence[Any], liste: Gebrauchsliste,
    fall: Callable[[str, Any, float], Any],
) -> Tuple[List[Any], List[str]]:
    """
    Die Lastfaelle eines Stahlspannungsnachweises -- und welche laut sind.

    Einmal fuer die haeufigen, einmal fuer die quasi-staendigen; beide
    Listen werden gleich gebildet und unterscheiden sich nur im Anteil.
    ``fall(name, eintrag, faktor)`` macht aus einem Eintrag -- einer
    Kombination der Tragsicherheit oder einem eigenen Fall -- den Fall des
    Nachweises: bei der Platte einen :class:`Gebrauchsfall`, beim
    gezeichneten Querschnitt einen :class:`Lastfall`.

    Die eigens angegebenen, und zusaetzlich die Tragsicherheitsfaelle mit
    ``liste.anteil`` Prozent. Beides nebeneinander: der Anteil ist eine bequeme
    Abschaetzung, deckt aber nicht den Fall ab, den es nur unter
    Gebrauchslast gibt. Wer einen solchen kennt, soll ihn dazustellen
    koennen, ohne die Abschaetzung fuer alle anderen aufzugeben.

    Die abgeleiteten Faelle entstehen auch dann, wenn
    ``liste.aus_tragsicherheit`` aus ist
    -- dann eben still. Sie ganz wegzulassen hiesse, den Nachweis erst auf
    Verlangen zu fuehren; so steht wenigstens ein Hinweis da, wenn die
    Abschaetzung nicht aufgeht.

    **Was das kostet.** Jeder Fall ist ein Gleichgewicht am gerissenen
    Querschnitt, also ein Durchlauf des Faserloesers -- rund 8 ms.
    Gemessen an der Beispielplatte mit drei Kombinationen: der
    quasi-staendige Nachweis laeuft immer und hebt die ganze Rechnung von
    27 auf 52 ms; bei erhoehter Anforderung kommt der haeufige dazu, 79 ms.
    Die Bewehrungssuche zahlt davon nichts, solange beide still sind --
    im schnellen Aufbau entstehen ganz stille Nachweise gar nicht (2.5
    statt 29 ms je Bewertung bei erhoehter Anforderung). Wer die Zeit
    auch in der Anzeige zurueckhaben will, kommt nicht an dieser Stelle
    weiter, sondern am Loeser.

    Die Rechnung steht hier und nicht in der Oberflaeche: dort waere sie
    eine zweite Wahrheit.
    """
    abgeleitet = [fall(abgeleiteter_fallname(k.name, liste.anteil), k, liste.anteil / 100.0)
                  for k in kombinationen if k.aktiv]
    eigen = [fall(h.name, h, 1.0) for h in liste.faelle if h.aktiv]
    laute = [f.name for f in eigen]
    if liste.aus_tragsicherheit:
        laute += [f.name for f in abgeleitet]
    return abgeleitet + eigen, laute


def _ausgefallene(
    kombinationen: Sequence[KombinationEintrag], richtung: Richtung
) -> List[Ausgefallen]:
    """
    Welche Nachweise in dieser unbewehrten Richtung ausfallen.

    Je Kombination der M-N-Nachweis, und wo eine Querkraft angegeben ist,
    auch der Querkraftnachweis: ohne Bewehrung gibt es keine statische
    Hoehe, also auch keinen Querkraftwiderstand. Beide Zeilen gehoeren in
    die Tabelle -- eine davon wegzulassen hiesse, die Luecke nur zur
    Haelfte zu schliessen.
    """
    r = richtung.value
    # Erst alle M-N, dann alle Querkraft -- dieselbe Folge wie bei den
    # Richtungen, die wirklich gerechnet werden. Zeilen derselben Art
    # gehoeren beieinander.
    return [
        Ausgefallen(
            art="M-N", langname=BiegungNormalkraft.THEMA,
            fall=k.name,
            symbol=f"M_{{Rd,{r}}}",
            einwirkung_symbol=f"M_{{Ed,{r}}}",
            einwirkung=Groesse(k.M_Ed, KNM), einheit=KNM)
        for k in kombinationen
    ] + [
        Ausgefallen(
            art="V", langname=Querkraft.THEMA, fall=k.name,
            symbol=f"V_{{Rd,{r}}}",
            einwirkung_symbol=f"V_{{Ed,{r}}}",
            einwirkung=Groesse(abs(k.V_Ed), KN_PRO_M), einheit=KN_PRO_M)
        for k in kombinationen if k.V_Ed
    ]


def _kombination(eintrag: KombinationEintrag) -> Schnittgroessen:
    try:
        art = Erfuellungsart(eintrag.art)
    except ValueError:
        raise ProjektFehler(
            f"Unbekannter Massstab '{eintrag.art}'. Möglich sind: "
            f"{', '.join(a.value for a in Erfuellungsart)}.") from None
    return Schnittgroessen(
        name=eintrag.name,
        M_Ed=Groesse(eintrag.M_Ed, KNM),
        N_Ed=Groesse(eintrag.N_Ed, KN),
        art=art,
    )


def _ueberschreibungen_setzen(projekt: "Projekt", werk: Rechenwerk,
                              aufbau: Aufbau) -> None:
    for eintrag in projekt.materialien:
        baustoff = aufbau.baustoffe[eintrag.kennung]
        for kurzname, zahl in eintrag.ueberschreibungen.items():
            if kurzname not in baustoff.definitionen:
                aufbau.warnungen.append(
                    f"Material '{baustoff.name}': Kennwert '{kurzname}' unbekannt "
                    f"→ Überschreibung übergangen.")
                continue
            definition = baustoff.definition(kurzname)
            werk.setze(definition.id, Groesse(zahl, definition.einheit))



# ===========================================================================
# Die Bauteilarten
# ===========================================================================


@dataclass(frozen=True)
class Bauteilart:
    """
    Der Steckbrief einer Bauteilart: was ausserhalb ihres Eintrags und ihrer
    Baufunktion von ihr bekannt sein muss. Eine neue Art kommt in
    :data:`BAUTEILE` dazu und nirgends sonst.
    """

    name: str
    """Wie sie im Aufbau, im Bericht und in der Oberflaeche heisst: ``platte``."""

    liste: str
    """Ihre Liste im :class:`Projekt` und in der Datei: ``querschnitte``."""

    eintrag: type
    """Die Klasse ihrer Eintraege -- sie liest einen Eintrag aus der Datei."""

    vorsilbe: str
    """Womit ihre Kennungen beginnen: ``q`` fuer q1, q2 ..."""

    raum: str
    """Womit ihre Namensraeume beginnen: ``querschnitt`` fuer querschnitt.q1."""

    bereich: str
    """Wie ihr Abschnitt in der Formelsammlung heisst."""

    bauen: Callable[["Bauteilart", Any, Aufbau], Bauteil]
    """Aus dem Eintrag das Bauteil -- Objekt und Nachweise, angemeldet im Werk."""


PLATTE = Bauteilart("platte", "querschnitte", QuerschnittEintrag, "q",
                    "querschnitt", "Platte", _platte)
ANALYSE = Bauteilart("querschnittsanalyse", "querschnittsanalysen",
                     QuerschnittsanalyseEintrag, "a", "querschnittsanalyse",
                     "Querschnittsanalyse", _querschnittsanalyse)
BALKENSYSTEM = Bauteilart("balkensystem", "balkensysteme", BalkensystemEintrag, "r",
                          "balkensystem", "Balkensysteme", _balkensystem)

#: Die Bauteilarten, in der Reihenfolge von Baum, Bericht und Rechnung -- ein
#: Balkensystem liest Werte der Platten und Analysen, also kommt es zuletzt.
#: Wer alle Bauteile durchgeht (Lesen, Kennungen, Aufbau, Zwischenspeicher,
#: Erkennen einer Datei), geht diese Liste durch.
BAUTEILE: Tuple[Bauteilart, ...] = (PLATTE, ANALYSE, BALKENSYSTEM)
