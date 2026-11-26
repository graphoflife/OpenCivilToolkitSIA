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
:mod:`~opencivil.projekt.aufbau.balkensystem`,
:mod:`~opencivil.projekt.aufbau.durchstanzen`,
:mod:`~opencivil.projekt.aufbau.grundbruch`,
:mod:`~opencivil.projekt.aufbau.setzung` und
:mod:`~opencivil.projekt.aufbau.pfahl`. Bis 2026-10-17 stand alles in
einer Datei ``aufbau.py`` von ueber tausend Zeilen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING, Any, Callable, Dict, Iterable, List, Mapping, NamedTuple, Optional, Sequence,
    Tuple,
)

from opencivil.core.bereich import Bereich
from opencivil.core.einheiten import Groesse
from opencivil.core.nachweis import Nachweis, NachweisUrteil
from opencivil.core.rechenwerk import Rechenwerk
from opencivil.core.wert import Kennzahl
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.basis import Baustoff, Baustoffart, KennwertVorlage
from opencivil.nachweis.knicken import Knickfall
from opencivil.nachweis.spannungsbegrenzung import Spannungsbegrenzung, Stahlspannungsort
from opencivil.nachweis.spannungsgrenzen import GrenzeAusRissbreite, GrenzeGegenFliessen
from opencivil.nachweis.kennzahlen import Plattenkennzahlen
from opencivil.querschnitt.gesetzwahl import Rechenwahl
from opencivil.querschnitt.platte import Plattenquerschnitt
from opencivil.projekt.eintraege import (
    Gebrauchsliste, KnickEintrag, MaterialEintrag, SpannungsfallEintrag, abgeleiteter_fallname,
)
from opencivil.geotechnik.fundament import Fundament
from opencivil.geotechnik.setzung import Setzungsfundament
from opencivil.pfahl.pfahl import Pfahl
from opencivil.projekt.lesen import ProjektFehler, als_groesse, anhalten, ort_von
from opencivil.stabwerk.rechnung import Balkensystem
from opencivil.stabwerk3d.rechnung import Balkensystem3d
from opencivil.decke.werk import Deckensystem

if TYPE_CHECKING:
    from opencivil.projekt.aufbau import Bauteilart
    from opencivil.projekt.projekt import Projekt


# ===========================================================================
# Aufbau
# ===========================================================================


class Warnung(NamedTuple):
    """
    Ein Hinweis aus dem Aufbau: ``raum`` ist der Namensraum des Eintrags, dem
    er gilt -- «querschnitt.q1» --, ``text`` der Satz. Am Namensraum grenzt
    die Oberflaeche ihn ein wie alles andere: unter «Aktuelle Seite» stehen
    die Hinweise des gewaehlten Eintrags, unter «Gesamt» alle ausser denen
    der Sandboxen. Bis 2026-11-20 standen alle ueber jeder Herleitung -- mit
    der Sandbox auch ihr «noch nichts gezeichnet», in jedem Projekt.
    """

    raum: str
    text: str


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
    kennzahlen: Dict[str, Plattenkennzahlen] = field(default_factory=dict)
    """Die Kennzahlen je Platte mit x-Bewehrung -- immer gerechnet."""

    spannungsfaelle: Dict[str, List[Tuple["SpannungsfallEintrag", Rechenwahl]]] = field(
        default_factory=dict)
    """
    Je Platte die Auswertungen am Querschnitt -- als Beschreibung, nicht als
    Nachweis, jede mit ihrer Wahl am Bauteil. Sie laufen nicht im Rechenwerk:
    sie haben kein Ziel, das jemand anderes brauchen koennte, und nichts
    haengt von ihnen ab.
    """

    unfertige: Dict[str, "Unfertiges"] = field(default_factory=dict)
    """
    Je Bauteil oder Material, dem noch etwas fehlt, was: eine
    Querschnittsanalyse ohne Zeichnung, eine Platte ohne Bewehrung, ein
    Pfahl ohne Schicht, ein Wert, den der Kern abweist (:meth:`unfertig`).
    Es wird nicht gebaut, aber wer auf es zeigt, soll hoeren, was ihm fehlt,
    und nicht, es gebe es nicht.
    """

    warnungen: List[Warnung] = field(default_factory=list)
    """Was beim Aufbau auffiel, je Eintrag (:meth:`warnen`)."""


    #: Die Felder, in denen die Nachweise stehen -- die eine Stelle, an der
    #: ein neuer Nachweis eingetragen wird. Alle sind nach Kennung
    #: geschluesselt (``q1`` oder ``q1.x`` -- die Richtung steht noch im
    #: Schluessel der Platte, damit Wert-IDs in abgelegten Berichten nicht
    #: wechseln) und alle tragen Nachweise mit ``d_ausnutzung``. Ihre
    #: Reihenfolge ist die der Herleitung: in ihr rechnet ein Bauteil seine
    #: Nachweise (:meth:`Bauteil.ziele`). ``fehlende`` rechnet nichts: eine
    #: Richtung ohne Bewehrung mit Einwirkungen bekommt so eine Zeile mit
    #: Erfuellungsgrad null statt gar keiner.
    NACHWEISFELDER = ("nachweise", "querkraft", "duktilitaet", "fehlende",
                      "rissnormalkraft", "sproede", "zwaengung_biegung",
                      "spannung_riss", "spannung", "verformung", "knicken",
                      "qa_biegung", "qa_schub", "qa_duktilitaet", "qa_sproede",
                      "qa_rissnormalkraft", "qa_zwaengung_biegung", "qa_spannung_riss",
                      "qa_spannung", "qa_knicken", "durchstanzen", "grundbruch", "gleiten",
                      "setzung", "pfahl_aussen", "pfahl_innen", "pfahl_quer",
                      "pfahl_innen_quer", "erdbeben")

    # -- Die Objekte je Bauteilart: Sichten auf die Bauteile --------------
    #
    # Bis 2026-10-25 legte jede Baufunktion ihr Objekt ein zweites Mal ab, in
    # einem Woerterbuch je Art. Jetzt steht es nur im Bauteil.

    def warnen(self, raum: str, text: str) -> None:
        """Ein Hinweis zum Eintrag mit dem Namensraum ``raum`` (:class:`Warnung`)."""
        self.warnungen.append(Warnung(raum, text))

    def unfertig(self, liste: str, eintrag: Any, wo: str, grund: str, *, raum: str) -> None:
        """
        Ein Bauteil oder Material, dem noch etwas fehlt: es rechnet nicht,
        das Projekt schon, und ein Hinweis sagt, was fehlt -- ein unfertiger
        Zustand ist kein Fehler des Projekts (Benutzer, 2026-11-19). Bis
        dahin hielten eine Platte ohne Bewehrung, ein Pfahl ohne Schicht und
        eine halbfertige Zeichnung alles auf. ``liste`` ist seine Liste im
        Projekt; ``grund`` ein Satzteil («noch keine Bewehrung») oder ein
        Satz, ohne Punkt; ``raum`` sein Namensraum, «beton.b1». Eine
        Baufunktion meldet es, indem sie einen :class:`ProjektFehler` wirft
        (:func:`~opencivil.projekt.aufbau.aufbauen`).
        """
        name = getattr(eintrag, "anzeigename", eintrag.name)
        self.unfertige[eintrag.kennung] = Unfertiges(liste, name, wo, grund)
        self.warnen(raum, f"{wo}: {grund} → nichts zu rechnen.")

    def ohne_nachweis(self, teil: "Bauteil", wo: str, grund: str) -> None:
        """
        Ein Bauteil, das gebaut ist, dem aber fuer jeden Nachweis noch etwas
        fehlt -- eine Kombination, eine Schicht. Wie :meth:`unfertig` kein
        Fehler: ``grund`` steht in der Zusammenfassung an seiner Stelle (bis
        2026-11-19 dort nur «Kein Nachweis gerechnet.») und als Warnung in der
        Herleitung. Ein Satzteil ohne Punkt.
        """
        teil.ohne_nachweis = grund
        self.warnen(teil.raum, f"{wo}: {grund} → kein Nachweis.")

    def objekte(self, art: str) -> Dict[str, Any]:
        """
        Die gebauten Objekte einer Bauteilart nach Kennung -- ``art`` ist ihr
        Name. Einen Namen, den keine Art traegt, meldet sie, statt still ein
        leeres Verzeichnis zu geben.
        """
        # Hier und nicht oben: die Steckbriefe bauen auf diesem Modul auf.
        from opencivil.projekt.aufbau import BAUTEILE
        if art not in {a.name for a in BAUTEILE}:
            raise KeyError(f"Eine Bauteilart «{art}» gibt es nicht.")
        return {k: t.objekt for k, t in self.teile.items() if t.art.name == art}

    @property
    def querschnitte(self) -> Dict[str, Plattenquerschnitt]:
        """Die Plattenquerschnitte, nach Kennung."""
        return self.objekte("platte")

    @property
    def querschnittsanalysen(self) -> Dict[str, Any]:
        """Die gezeichneten Querschnitte, nach Kennung."""
        return self.objekte("querschnittsanalyse")

    @property
    def balkensysteme(self) -> Dict[str, Balkensystem]:
        """Die Balkensysteme, nach Kennung -- Bauteile ohne Nachweise, mit ihrem Ergebnis."""
        return self.objekte("balkensystem")

    @property
    def balkensysteme3d(self) -> Dict[str, Balkensystem3d]:
        """Die 3D-Balkensysteme, nach Kennung -- wie die ebenen."""
        return self.objekte("balkensystem3d")

    @property
    def decken(self) -> Dict[str, Deckensystem]:
        """Die Decken, nach Kennung -- Bauteile ohne Nachweise, mit ihrem Ergebnis."""
        return self.objekte("decke")

    @property
    def grundbrueche(self) -> Dict[str, Fundament]:
        """Die Fundamente der Grundbruchnachweise, nach Kennung."""
        return self.objekte("grundbruch")

    @property
    def setzungen(self) -> Dict[str, Setzungsfundament]:
        """Die Fundamente der Setzungsberechnungen, nach Kennung."""
        return self.objekte("setzung")

    @property
    def pfaehle(self) -> Dict[str, Pfahl]:
        """Die Pfähle, nach Kennung."""
        return self.objekte("pfahl")

    def feld(self, feld: str) -> Dict[str, Nachweis]:
        """
        Die Nachweise eines Feldes, nach ihrem Schluessel -- eine Sicht auf
        die Bauteile, in ihrer Folge. Bis 2026-10-25 stand jedes Feld als
        eigenes Woerterbuch im Aufbau, neben den Nachweisen der Bauteile.
        """
        if feld not in self.NACHWEISFELDER:
            raise ValueError(f"'{feld}' steht nicht in Aufbau.NACHWEISFELDER.")
        return {s: n for teil in self.teile.values() for f, s, n in teil.nachweise if f == feld}

    def nachweise_je_feld(self):
        """Alle Nachweise, Feld fuer Feld und in der Reihenfolge der Liste."""
        for feld in self.NACHWEISFELDER:
            yield feld, self.feld(feld)

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
        Einen Nachweis anmelden: im Rechenwerk und bei seinem Bauteil, mit
        Feld und Schluessel -- ausser er ist ganz still, und es wird schnell
        gerechnet.

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
        teil.nachweise.append((feld, schluessel, nachweis))

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
        """Ein gebautes Bauteil -- fuer eines, dem noch etwas fehlt, sagt der Fehler, was."""
        teil = self.teile.get(kennung)
        if teil is not None:
            return teil
        unfertig = self.unfertige.get(kennung)
        if unfertig is not None:
            raise ProjektFehler(f"{unfertig.grund}.", wo=unfertig.wo)
        raise ProjektFehler(f"Ein Bauteil '{kennung}' gibt es im Aufbau nicht.")

    def bauteil_von(self, nachweis: Nachweis) -> "Bauteil":
        """Das Bauteil, bei dem ein Nachweis angemeldet ist."""
        for teil in self.teile.values():
            if any(n is nachweis for _, _, n in teil.nachweise):
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
        eigene = {n.id for _, _, n in self.bauteil(kennung).nachweise}
        return [u for u in urteile if u.raum in eigene]

    def materialziele(self) -> List[str]:
        """
        Saemtliche Kennwerte aller Materialien -- in der Folge der Arten,
        Beton zuerst, dann die Staehle (:data:`~opencivil.material.arten.MATERIALARTEN`).

        Gehoert zum Regellauf: ein Material, das noch keine Platte verwendet,
        waere sonst nie Ziel und bliebe ungerechnet -- im Editor staenden dann
        leere Felder, obwohl die Sorte alles hergibt.

        Die Reihenfolge bestimmt zugleich den Aufbau der Herleitung: der Loeser
        arbeitet die Ziele der Reihe nach ab, und das Protokoll folgt ihm. So
        stehen im Bericht erst die Baustoffe und dann die Bauteile.
        """
        folge = list(MATERIALARTEN)
        stoffe = sorted(self.baustoffe.values(), key=lambda s: folge.index(s.art.value))
        return [d.id for s in stoffe for d in s.definitionen.values()]


@dataclass(frozen=True)
class Unfertiges:
    """
    Ein Bauteil oder Material, dem noch etwas fehlt -- seine Liste im
    Projekt, sein Name, wie es in Meldungen heisst, und was
    (:meth:`Aufbau.unfertig`).
    """

    liste: str
    name: str
    wo: str
    grund: str

    @property
    def meldung(self) -> str:
        """Für wen nach ihm fragt: «Platte 'Decke': noch keine Bewehrung.»"""
        return f"{self.wo}: {self.grund}."


@dataclass
class Bauteil:
    """
    Ein gebautes Bauteil und was zu ihm gehoert. Wem ein Nachweis gehoert,
    steht hier -- niemand muss es aus einer Kennung wie «q1.x» zurueckgewinnen.
    """

    eintrag: Any
    """
    Der Eintrag des Projekts, aus dem es gebaut ist -- fuer ein Bild, das
    nach einem seiner Felder fragt, etwa der Normalkraft der M-V-Kurve.
    """
    art: "Bauteilart"
    objekt: Any
    """Der Plattenquerschnitt, die Querschnittsanalyse oder das Balkensystem."""

    nachweise: List[Tuple[str, str, Nachweis]] = field(default_factory=list)
    """Feld, Schluessel und Nachweis, angemeldet ueber :meth:`Aufbau.eintragen`."""

    weitere_ziele: List[str] = field(default_factory=list)
    """Was es ausser seinen Nachweisen rechnet -- ein Balkensystem seine Querschnitte und sich."""

    kennzahlen: List[Kennzahl] = field(default_factory=list)
    """
    Was es beschreibt, gleich welche Lastfaelle es gibt, in der Folge der
    Zusammenfassung -- jede so, wie ihr Erzeuger sie nennt.
    """

    bezuege: Tuple[str, ...] = ()
    """Die Bauteile, deren Werte es liest: Platten und Analysen, aus denen ein System Querschnitte nimmt."""

    ohne_nachweis: str = ""
    """Warum es keinen seiner Nachweise fuehrt -- leer, wenn nichts fehlt (:meth:`Aufbau.ohne_nachweis`)."""

    @property
    def kennung(self) -> str:
        return self.eintrag.kennung

    @property
    def name(self) -> str:
        return self.eintrag.name

    @property
    def raum(self) -> str:
        """Der Namensraum seiner Werte und Urteile."""
        return self.objekt.id

    def im_feld(self, feld: str) -> List[Nachweis]:
        """Seine Nachweise in einem Feld des :class:`Aufbau`, in der Folge der Anmeldung."""
        return [n for f, _, n in self.nachweise if f == feld]

    def ziele(self) -> List[str]:
        """
        Was ein Lauf fuer dieses Bauteil rechnet: die Nachweise in der Folge
        von :attr:`Aufbau.NACHWEISFELDER`, dann die weiteren Ziele.
        """
        folge = {feld: i for i, feld in enumerate(Aufbau.NACHWEISFELDER)}
        return ([n.id for _, _, n in sorted(self.nachweise, key=lambda e: folge[e[0]])]
                + self.weitere_ziele)


# ===========================================================================
# Was mehr als eine Bauteilart braucht
# ===========================================================================


def kennwertbereich(vorlage: KennwertVorlage) -> Bereich:
    """
    Wo ein Kennwert eines Baustoffs liegen muss: ueber null. Festigkeiten,
    Moduln, Dehnungen, Teilsicherheitsbeiwerte sind ihrer Natur nach
    positiv; eine Null oder ein negativer Wert liefert keine falsche Zahl,
    sondern gar keine -- gamma_c = 0 endete in einem ZeroDivisionError, ein
    negatives f_ck in einer komplexen Wurzel. Beides kam als Absturzmeldung
    beim Benutzer an.

    Der Aufbau prueft damit jede Abweichung und Ueberschreibung
    (:func:`baustoff_bauen`), die Oberflaeche liest dieselbe Grenze aus dem
    Katalog (``materialarten``) und weist eine Null schon am Feld ab. Bis
    2026-11-19 fuehrten die Pfeile dort bis 0.
    """
    return Bereich(vorlage.beschreibung or vorlage.kurzname, vorlage.einheit, ueber=0.0)


def baustoff_bauen(eintrag: MaterialEintrag, symbol_index: str, wo: str) -> Baustoff:
    art = MATERIALARTEN[eintrag.art]
    bauer = art.bauen
    roh = bauer(eintrag.sorte, praefix=f"{eintrag.art}.{eintrag.kennung}")
    vorlagen = {v.kurzname: v for v in art.vorlagen}
    # Ein Kennwert, den es nicht gibt, ist ein Tippfehler: bis 2026-10-16 fiel
    # eine Abweichung «fck» still weg, und gerechnet wurde mit der Sorte.
    for topf, wie in ((eintrag.abweichungen, "abweichender Wert"),
                      (eintrag.ueberschreibungen, "überschriebener Wert")):
        for kurzname, zahl in topf.items():
            if kurzname not in roh.definitionen:
                raise ProjektFehler(
                    f"einen Kennwert '{kurzname}' gibt es nicht "
                    f"({wie}). Möglich sind: {', '.join(roh.definitionen)}.", wo=wo)
            anhalten(kennwertbereich(vorlagen[kurzname]).grund(zahl), wo)
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


def material(baustoffe: Mapping[str, Baustoff], kennung: str, art: str, wo: str,
             feld: str) -> Baustoff:
    """
    Das Material, das ``feld`` des Bauteils ``wo`` waehlt: es muss es geben,
    und es muss von dieser Art sein. Ohne Angabe gilt nicht «das erste im
    Projekt» -- bis 2026-10-16 bekamen Buegel und Staebe ohne Stahl still den
    ersten. ``feld`` heisst wie in der Oberflaeche: was nicht stimmt, steht
    am Bauteil (:meth:`Aufbau.unfertig`), dort genuegt das Feld.
    """
    gefunden = baustoffe.get(kennung)
    grund = materialgrund(kennung, None if gefunden is None
                          else (gefunden.art.value, gefunden.name), art)
    if grund:
        raise ProjektFehler(f"{feld}: {grund.text}.", wo=wo)
    return gefunden


def ohne_kombination(kombinationen: Sequence[Any]) -> str:
    """Warum ein Bauteil mit Einwirkungen keinen Nachweis fuehrt: es hat noch keine, oder jede ist aus."""
    return ("jede Kombination ist ausgeschaltet" if kombinationen
            else "noch keine Kombination – unter «Einwirkungen» eine anlegen")


class Grund(NamedTuple):
    """
    Warum eine Wahl nicht rechnet, klein beginnend. ``falsch``: sie
    widerspricht sich -- etwa ein Stahl, wo ein Beton hingehoert -- und steht
    rot. Sonst fehlt nur etwas, und sie steht grau, auch wo die Rechnung ohne
    sie anhaelt (Benutzer, 2026-11-19).
    """

    text: str
    falsch: bool = False


def materialgrund(kennung: str, gefunden: Optional[Tuple[str, str]], art: str) -> Optional[Grund]:
    """
    Was an der Wahl eines Materials nicht stimmt, ohne Ort -- ``None``, wenn
    sie stimmt. ``gefunden`` sind Art und Name des gewaehlten, ``None``, wenn
    es das nicht gibt. Falsch ist nur die falsche Art; ein geloeschtes oder
    noch nicht gewaehltes fehlt nur. Das geloeschte nennt der Satz nicht beim
    Namen: den kennt das Projekt nicht mehr, und die Kennung steht nirgends,
    wo der Benutzer sie saehe -- bis 2026-11-19 hiess es «das Material 'b9'».
    Die Regel fuer :func:`material` und fuer die Meldungen an der Zeichnung
    (:func:`opencivil.web.zeichengeometrie.geometrie`).
    """
    if gefunden is None:
        return Grund("das gewählte Material gibt es nicht mehr – eines wählen" if kennung
                     else "noch kein Material gewählt")
    if gefunden[0] != art:
        return Grund(f"«{gefunden[1]}» ist kein {Baustoffart(art).beschriftung}", falsch=True)
    return None


def ueberschreibungen_setzen(projekt: "Projekt", werk: Rechenwerk,
                              aufbau: Aufbau) -> None:
    """
    Die von Hand ueberschriebenen Kennwerte -- dass es sie gibt, prueft
    ``baustoff_bauen``. Ein Material, das nicht rechnet, hat keine.
    """
    for eintrag in projekt.materialien:
        baustoff = aufbau.baustoffe.get(eintrag.kennung)
        if baustoff is not None:
            _ueberschreiben(werk, eintrag, baustoff)


def _ueberschreiben(werk: Rechenwerk, eintrag: MaterialEintrag, baustoff: Baustoff) -> None:
    for kurzname, zahl in eintrag.ueberschreibungen.items():
        definition = baustoff.definition(kurzname)
        werk.setze(definition.id, Groesse(zahl, definition.einheit))


def baustoff_im_werk(eintrag: MaterialEintrag, werk: Rechenwerk) -> Optional[Baustoff]:
    """
    Ein Material als Baustoff in ``werk``, mit Abweichungen und
    Ueberschreibungen, wie das Projekt es rechnet -- ohne das Projekt zu
    bauen. ``None``, wenn es nicht rechnet: was ihm fehlt, sagt es selbst.
    Fuer das Zeichenfenster, das zu einem Spannglied schon beim Zeichnen
    seine Spannkraft nennt (:mod:`opencivil.web.zeichengeometrie`).
    """
    try:
        baustoff = baustoff_bauen(eintrag, "", ort_von(eintrag))
    except ProjektFehler:
        return None
    baustoff.ins_rechenwerk(werk)
    _ueberschreiben(werk, eintrag, baustoff)
    return baustoff


def stoffe_von(aufbau: Aufbau, baustoffe: Iterable[Baustoff]) -> Dict[str, Baustoff]:
    """
    Die Baustoffe eines Bauteils unter ihrer Kennung im Projekt -- danach
    waehlt ein Kapitel seine Werte je Material
    (:class:`~opencivil.projekt.eintraege.JeMaterial`).
    """
    ids = {b.id for b in baustoffe}
    return {kennung: b for kennung, b in aufbau.baustoffe.items() if b.id in ids}


def spannungsfaelle(eintrag, stoffe: Mapping[str, Baustoff], aufbau: Aufbau) -> None:
    """Die eingeschalteten Spannung-Dehnung-Analysen eines Bauteils, jede mit ihrer Wahl an ihm."""
    aktive = [(s, s.wahl(stoffe)) for s in eintrag.spannungsfaelle if s.aktiv]
    if aktive:
        aufbau.spannungsfaelle[eintrag.kennung] = aktive


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
                                       wahl=liste.wahl.wahl(stoffe_von(aufbau, ort.baustoffe)))
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
    """
    Ein Knickfall aus seiner Beschreibung -- jede Zahl in der Einheit ihres
    Feldes; ``mehr`` fuer die Analyse.
    """
    return klasse(name=k.name, **{f: als_groesse(k, f) for f in (
        "N_Ed", "M_Ed_1", "laenge", "knicklaenge")}, **mehr)
