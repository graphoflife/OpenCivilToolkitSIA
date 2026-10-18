"""
opencivil/projekt/aufbau/kern.py -- was alle Bauteilarten beim Bauen teilen.

VERANTWORTUNG:
Der :class:`Aufbau`, in dem das Gebaute nach Feld und Kennung liegt, das
:class:`Bauteil` mit seinen Nachweisen und Zielen, und was mehr als eine
Bauteilart braucht: die Baustoffe aus den Materialien
(:func:`baustoff_bauen`, :func:`material`, :func:`ueberschreibungen_setzen`),
die beiden Stahlspannungen (:func:`spannungsnachweise`) und den Knickfall
(:func:`knickfall`) -- Platte und gezeichneter Querschnitt rufen dieselben.

Was nur eine Art braucht, steht bei ihr: :mod:`~opencivil.projekt.aufbau.platte`,
:mod:`~opencivil.projekt.aufbau.querschnittsanalyse`,
:mod:`~opencivil.projekt.aufbau.balkensystem` und
:mod:`~opencivil.projekt.aufbau.grundbruch`. Bis 2026-10-17 stand alles in
einer Datei ``aufbau.py`` von ueber tausend Zeilen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

from opencivil.core.einheiten import KN, KNM, M, Groesse
from opencivil.core.berechnung import Nachweis, NachweisUrteil
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.core.wert import Kennzahl
from opencivil.material.basis import Baustoff
from opencivil.material.beton import beton
from opencivil.material.betonstahl import betonstahl
from opencivil.nachweis.biegung_normalkraft import BiegungNormalkraft
from opencivil.nachweis.duktilitaet import Duktilitaet
from opencivil.nachweis.knicken import Knickfall, Knicken
from opencivil.nachweis.fehlende_bewehrung import FehlendeBewehrung
from opencivil.nachweis.mindestbewehrung import Rissnormalkraft, ZwaengungBiegung
from opencivil.nachweis.spannungsbegrenzung import Spannungsbegrenzung, Stahlspannungsort
from opencivil.nachweis.spannungsgrenzen import GrenzeAusRissbreite, GrenzeGegenFliessen
from opencivil.nachweis.verformung import Verformung
from opencivil.nachweis.kennzahlen import Plattenkennzahlen
from opencivil.nachweis.sproedes_versagen import SproedesVersagen
from opencivil.nachweis.querkraft import Querkraft
from opencivil.querschnitt.platte import Plattenquerschnitt
from opencivil.projekt.eintraege import (
    Gebrauchsliste, KnickEintrag, MaterialEintrag, SpannungsfallEintrag, abgeleiteter_fallname,
)
from opencivil.geotechnik.grundbruch import Fundament, Gleiten, Grundbruch
from opencivil.projekt.lesen import ProjektFehler
from opencivil.nachweis.qa_gebrauch import RissnormalkraftQA, ZwaengungBiegungQA
from opencivil.nachweis.qa_knicken import KnickenQA
from opencivil.nachweis.richtungsnachweise import DuktilitaetQA, SproedesVersagenQA
from opencivil.nachweis.schiefe_biegung import SchiefeBiegung
from opencivil.nachweis.schubwandnachweis import Schubwandnachweis
from opencivil.stabwerk.rechnung import Balkensystem

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart
    from opencivil.projekt.projekt import Projekt


# ===========================================================================
# Aufbau
# ===========================================================================


@dataclass
class Aufbau:
    """Was beim Zusammenbauen eines Projekts entsteht."""

    werk: Rechenwerk
    schnell: bool = False
    """Fuer die Bewehrungssuche gebaut -- siehe :func:`~opencivil.projekt.aufbau.aufbauen`."""

    teile: Dict[str, "Bauteil"] = field(default_factory=dict)
    """
    Jedes Bauteil nach Kennung, in der Reihenfolge von
    :data:`~opencivil.projekt.aufbau.BAUTEILE` und der Beschreibung.
    """

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

    verformung: Dict[str, Verformung] = field(default_factory=dict)
    """Die Durchbiegung je Verformungsfall, je Querschnitt -- nur in x-Richtung."""

    kennzahlen: Dict[str, Plattenkennzahlen] = field(default_factory=dict)
    """Die Kennzahlen je Platte mit x-Bewehrung -- immer gerechnet."""

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
    qa_spannung_riss: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    qa_spannung: Dict[str, Spannungsbegrenzung] = field(default_factory=dict)
    """Die Gebrauchsnachweise je Querschnittsanalyse, wie bei der Platte."""

    qa_knicken: Dict[str, KnickenQA] = field(default_factory=dict)
    """Knicken je Querschnittsanalyse -- je Fall in seiner Richtung."""

    balkensysteme: Dict[str, Balkensystem] = field(default_factory=dict)
    """Die Balkensysteme, nach Kennung -- Bauteile ohne Nachweise, mit ihrem Ergebnis."""

    grundbrueche: Dict[str, Fundament] = field(default_factory=dict)
    """Die Fundamente der Grundbruchnachweise, nach Kennung."""

    grundbruch: Dict[str, Grundbruch] = field(default_factory=dict)
    gleiten: Dict[str, Gleiten] = field(default_factory=dict)
    """Grundbruch und Gleiten je Fundament."""

    warnungen: List[str] = field(default_factory=list)

    #: Die Felder, in denen die Nachweise stehen -- die eine Stelle, an der
    #: ein neuer Nachweis eingetragen wird. Alle sind nach Kennung
    #: geschluesselt (``q1`` oder ``q1.x``) und alle tragen Nachweise mit
    #: ``d_ausnutzung``. Ihre Reihenfolge ist die der Herleitung: in ihr
    #: rechnet ein Bauteil seine Nachweise (:meth:`Bauteil.ziele`).
    NACHWEISFELDER = ("nachweise", "querkraft", "duktilitaet", "fehlende",
                      "rissnormalkraft", "sproede", "zwaengung_biegung",
                      "spannung_riss", "spannung", "verformung", "knicken",
                      "qa_biegung", "qa_schub", "qa_duktilitaet", "qa_sproede",
                      "qa_rissnormalkraft", "qa_zwaengung_biegung", "qa_spannung_riss",
                      "qa_spannung", "qa_knicken", "grundbruch", "gleiten")

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
        Jedes Bauteil, in der Reihenfolge von :data:`~opencivil.projekt.aufbau.BAUTEILE` und der
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
        return ziele

    def berichtsziele(self) -> List[str]:
        """
        Was im Bericht steht: Nachweise und was die Bauteile sonst rechnen --
        ohne die Baustoffkennwerte, die niemand braucht.
        """
        return (self.alle_nachweisziele()
                + [z for teil in self.bauteile() for z in teil.weitere_ziele])

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

    kennzahlen: List[Kennzahl] = field(default_factory=list)
    """
    Was es beschreibt, gleich welche Lastfaelle es gibt, in der Folge der
    Zusammenfassung -- jede so, wie ihr Erzeuger sie nennt.
    """

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


# ===========================================================================
# Was mehr als eine Bauteilart braucht
# ===========================================================================


def baustoff_bauen(eintrag: MaterialEintrag, symbol_index: str) -> Baustoff:
    bauer = {"beton": beton, "betonstahl": betonstahl}[eintrag.art]
    roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
    # Jeder Kennwert dieser beiden Baustoffe ist seiner Natur nach positiv:
    # Festigkeiten, Moduln, Dehnungen, Teilsicherheitsbeiwerte. Eine Null
    # oder ein negativer Wert liefert keine falsche Zahl, sondern gar keine
    # -- gamma_c = 0 endete in einem ZeroDivisionError, ein negatives f_ck
    # in einer komplexen Wurzel. Beides kam als Absturzmeldung beim
    # Benutzer an.
    #
    # Ein Kennwert, den es nicht gibt, ist ein Tippfehler: bis 2026-10-16 fiel
    # eine Abweichung «fck» still weg, und gerechnet wurde mit der Sorte.
    for topf, wie in ((eintrag.abweichungen, "abweichender Wert"),
                      (eintrag.ueberschreibungen, "überschriebener Wert")):
        for kurzname, zahl in topf.items():
            if kurzname not in roh.definitionen:
                raise ProjektFehler(
                    f"'{eintrag.anzeigename}': einen Kennwert '{kurzname}' gibt es nicht "
                    f"({wie}). Möglich sind: {', '.join(roh.definitionen)}.")
            if zahl <= 0.0:
                raise ProjektFehler(
                    f"'{eintrag.anzeigename}': {kurzname} muss grösser als null "
                    f"sein, angegeben ist {zahl:g} ({wie}).")
    abweichungen = {
        kurzname: Groesse(zahl, roh.definition(kurzname).einheit)
        for kurzname, zahl in eintrag.abweichungen.items()
    }
    return bauer(
        eintrag.sorte,
        name=eintrag.anzeigename,
        praefix=f"{eintrag.art}.{eintrag.kennung}",
        abweichungen=abweichungen,
        symbol_index=symbol_index,
    )


def material(baustoffe: Mapping[str, Baustoff], kennung: str, art: str, wer: str) -> Baustoff:
    """
    Das Material, auf das ein Eintrag zeigt: es muss es geben, und es muss
    von dieser Art sein. Ohne Angabe gilt nicht «das erste im Projekt» -- bis
    2026-10-16 bekamen Buegel und Staebe ohne Stahl still den ersten.
    """
    gefunden = baustoffe.get(kennung)
    if gefunden is None:
        raise ProjektFehler(
            f"{wer} verweist auf das Material '{kennung}', das es nicht (mehr) gibt."
            if kennung else f"{wer} hat kein Material.")
    if gefunden.art.value != art:
        raise ProjektFehler(f"{wer} braucht einen "
                            f"{'Beton' if art == 'beton' else 'Betonstahl'}, "
                            f"'{gefunden.name}' ist keiner.")
    return gefunden


def ueberschreibungen_setzen(projekt: "Projekt", werk: Rechenwerk,
                              aufbau: Aufbau) -> None:
    """Die von Hand ueberschriebenen Kennwerte -- dass es sie gibt, prueft ``baustoff_bauen``."""
    for eintrag in projekt.materialien:
        baustoff = aufbau.baustoffe[eintrag.kennung]
        for kurzname, zahl in eintrag.ueberschreibungen.items():
            definition = baustoff.definition(kurzname)
            werk.setze(definition.id, Groesse(zahl, definition.einheit))


def spannungsnachweise(eintrag, ort: Stahlspannungsort, kombinationen: Sequence[Any],
                        fall: Callable[[str, Any, float], Any], *, praefix: str, kennung: str,
                        aufbau: Aufbau, teil: Bauteil) -> None:
    """
    Die Stahlspannung, zweimal: aus der Rissbreite unter quasi-staendiger
    Einwirkung (bei jeder Anforderung) und gegen Fliessen unter haeufiger
    (nur bei erhoehter und hoher). Welche wann gilt, weiss die Grenze selbst.

    Fuer die Platte und den gezeichneten Querschnitt dieselbe Schleife: ``ort``
    sagt, wo gemessen wird, ``fall`` macht die Faelle
    (:func:`_gebrauchsfaelle`), ``praefix`` das Feld des Aufbaus -- «qa_»
    beim gezeichneten Querschnitt. Bis 2026-10-17 stand sie zweimal da.
    """
    for feld, liste, grenze in (
            ("spannung_riss", eintrag.quasistaendig, GrenzeAusRissbreite),
            ("spannung", eintrag.haeufig, GrenzeGegenFliessen)):
        if not grenze.gilt_bei(eintrag.rissanforderung):
            continue
        faelle, laute = _gebrauchsfaelle(kombinationen, liste, fall)
        if not faelle:
            continue
        spannung = Spannungsbegrenzung(ort, faelle, grenze=grenze,
                                       anforderung=eintrag.rissanforderung,
                                       wahl=liste.wahl.wahl)
        spannung.stillstellen([f.name for f in faelle], laute)
        aufbau.eintragen(teil, f"{praefix}{feld}", kennung, spannung)


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
    Nachweises: bei der Platte einen
    :class:`~opencivil.nachweis.spannungsbegrenzung.Gebrauchsfall`, beim
    gezeichneten Querschnitt einen :class:`~opencivil.querschnitt.analyse.Lastfall`.

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


def knickfall(k: KnickEintrag, klasse: type = Knickfall, **mehr: Any) -> Knickfall:
    """Ein Knickfall aus seiner Beschreibung -- kN, kNm und m; ``mehr`` fuer die Analyse."""
    return klasse(name=k.name, N_Ed=Groesse(k.N_Ed, KN), M_Ed_1=Groesse(k.M_Ed_1, KNM),
                  laenge=Groesse(k.laenge, M), knicklaenge=Groesse(k.knicklaenge, M), **mehr)
