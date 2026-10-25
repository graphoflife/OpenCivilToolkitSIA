"""
opencivil/core/protokoll.py -- Mitschrift einer Berechnung.

VERANTWORTUNG:
Eine Berechnung schreibt waehrend des Rechnens in ein Protokoll. Rechenschritt
und seine Darstellung entstehen dadurch am selben Ort und koennen nicht
auseinanderlaufen -- man kann nicht das eine rechnen und das andere aufschreiben.

Genau das braucht eine Prozedur: eine Iteration soll nicht nur ihr Resultat
liefern, sondern auch ihren Ablauf zeigen -- Startwerte, Zwischenschritte in
einer Tabelle, Abbruchkriterium. Ein Leser muss die Rechnung von Hand
nachvollziehen koennen.

Das Protokoll ist reine Datenstruktur. Ob daraus Konsolentext, ein LaTeX-
Dokument oder HTML wird, entscheidet erst der Bericht -- jede Darstellung mit
einer Tafel, die fuer jede Blockart sagt, wie sie gesetzt wird (siehe
:func:`darstellen`).

STILLES PROTOKOLL:
In heissen Schleifen (z.B. beim punktweisen Aufbau einer M-N-Interaktionslinie
mit hunderten Dehnungsebenen) will man nichts mitschreiben. Dafuer gibt es
:class:`StillesProtokoll` -- dieselbe Schnittstelle, verwirft aber alles.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Type,
    TypeVar,
)

from opencivil.core import latex as tex
from opencivil.core.einheiten import (
    EINHEITSLOS, KN, KNM, MM, MM2, N_PRO_MM2, PRO_M, PROMILLE, Einheit, Groesse,
)
from opencivil.core.wert import Wert, WertDef


# ===========================================================================
# Bloecke
# ===========================================================================


class HinweisArt(str, Enum):
    INFO = "info"
    WARNUNG = "warnung"
    ANNAHME = "annahme"

    def __str__(self) -> str:
        return self.value

    @property
    def beschriftung(self) -> str:
        return {
            HinweisArt.INFO: "Hinweis",
            HinweisArt.WARNUNG: "Warnung",
            HinweisArt.ANNAHME: "Annahme",
        }[self]


@dataclass
class Block:
    """Basis aller Protokollbausteine."""


@dataclass(frozen=True)
class Abschnitt:
    """
    Ueberschrift eines Bauteils oder Baustoffs samt seinem Namensraum.

    Beides gehoert zusammen: der Titel ist fuer den Leser, der Namensraum fuer
    die Oberflaeche, die danach filtert.
    """

    titel: str
    raum: str

    thema: str = ""
    """
    Unter welchem Thema die Formeln des Abschnitts in der Formelsammlung
    stehen, sofern die Berechnung keines mitbringt -- «Beton», «Querschnitt».
    """


@dataclass
class TitelBlock(Block):
    text: str
    ebene: int = 2

    raum: str = ""
    """
    Namensraum des Abschnitts, den dieser Titel eroeffnet -- leer, wenn er
    keinen eroeffnet.

    Die Oberflaeche grenzt die Herleitung damit auf den gewaehlten Bestandteil
    ein. Ueber den Anzeigetext ginge das auch, aber ein Vergleich ueber
    Beschriftungen ist immer eine Falle: er bricht, sobald jemand den Text
    aendert, und er bricht stumm.
    """

    @property
    def abschnitt(self) -> bool:
        return bool(self.raum)
    """
    Eroeffnet dieser Titel einen ganzen Abschnitt (ein Bauteil, ein Baustoff)?

    Die Oberflaeche braucht das, um die Herleitung auf den gewaehlten
    Bestandteil einzugrenzen. Ueber die Ebene allein liesse sich das nicht
    entscheiden -- Zwischenueberschriften stehen auf derselben.
    """


@dataclass
class TextBlock(Block):
    """Fliesstext zwischen den Formeln."""

    text: str

    erklaerung: bool = False
    """
    Ob der Text erklaert, statt ein Ergebnis zu nennen -- das 'Warum'.

    Erklaerungen stehen nicht in der Herleitung (siehe :func:`darstellen`),
    sondern in der Formelsammlung unter den Formeln ihres Themas. Die
    Herleitung zeigt Formeln, Zahlen und Stichworte.
    """

    thema: str = ""
    """Thema der Berechnung, die den Block schrieb -- vom Rechenwerk gestempelt."""


@dataclass
class GleichungBlock(Block):
    """Eine gesetzte Formel."""

    latex: str
    titel: str = ""
    referenz: str = ""
    wert_id: str = ""
    """ID des erzeugten Wertes, falls die Gleichung einen Wert liefert."""

    gruppe: str = ""
    """
    Name eines Kastens, in dem mehrere Angaben zusammenstehen sollen.

    Vier Zeilen der Form ``h = 300 mm`` untereinander sind kein Nachweis,
    sondern eine Liste. Zusammengelegt liest sie sich besser -- aber nur
    fuer die Darstellung: jede Angabe bleibt ihr eigener Block mit eigener
    ``wert_id``.

    Das ist der Punkt. Wer die vier zu *einem* Block verschmelzen wollte,
    verloere die Rueckverfolgung: wird nur ``h`` gebraucht, laeuft auch nur
    dessen Vorgabe, und im Kasten steht dann eben nur ``h``. Ein
    verschmolzener Block wuesste nichts davon und zeigte alle vier.
    """

    formelzeile: Optional[tex.Formelzeile] = None
    """Strukturierte Fassung, sofern vorhanden -- erlaubt spaeteren Umbruch."""

    ansatz: bool = False
    """
    Ob die Gleichung rein symbolisch ist -- ein Ansatz ohne Zahlen, etwa das
    Werkstoffgesetz oder die Formel, nach der gleich gerechnet wird. Die
    Formelsammlung nimmt sie so, wie sie dasteht.
    """

    thema: str = ""
    """Thema der Berechnung, die den Block schrieb -- vom Rechenwerk gestempelt."""

    name: str = field(default="", compare=False)
    """
    Name der Formel im Notizbuch -- nie Fall, Sorte, Lage oder Richtung. Leer
    heisst: ihr Titel ohne Zahlenangabe (siehe
    :func:`opencivil.bericht.formelsammlung.formelname`). Gesetzt wird er, wo
    der Titel je nach Fall wechselt oder fuer sich nichts sagt («Ansatz»).
    """

    codestelle: str = field(default="", compare=False)
    """
    Wo im Code die Gleichung geschrieben wird, als ``modul:Funktion`` -- das
    Notizbuch verlinkt damit Formel und Modul. Selbst ermittelt (siehe
    :func:`codestelle_aus`), nur die allgemeine Formel gibt sie mit.
    """


@dataclass
class TabellenBlock(Block):
    """
    Tabelle, typischerweise ein Iterationsprotokoll.

    Jede Zelle ist Text (``str``) oder :class:`latex.Mathe` -- die
    Darstellung entscheidet, wie sie beides setzt.
    """

    kopf: Sequence[tex.Zelle]
    zeilen: Sequence[Sequence[tex.Zelle]]
    titel: str = ""
    ausrichtung: Optional[str] = None

    def als_latex(self) -> str:
        return tex.tabelle(self.kopf, self.zeilen, self.ausrichtung)


@dataclass
class HinweisBlock(Block):
    text: str
    art: HinweisArt = HinweisArt.INFO


# ===========================================================================
# Protokoll
# ===========================================================================


class Protokoll:
    """
    Sammelt die Bloecke einer Berechnung in der Reihenfolge ihres Entstehens.

    Beispiel::

        p.titel("Bemessungswert der Betondruckfestigkeit")
        p.formel(f_cd, r"\\frac{@eta_fc \\cdot @f_ck}{@gamma_c}",
                 {"eta_fc": eta, "f_ck": fck, "gamma_c": gamma})
        p.hinweis("Massgebend ist der abgeminderte Wert.")
    """

    def __init__(self, titel: str = "", referenz: str = "") -> None:
        self.kopftitel = titel
        self.referenz = referenz
        self.bloecke: List[Block] = []

    # -- Aufzeichnen --------------------------------------------------------

    def _anfuegen(self, block: Block) -> Block:
        self.bloecke.append(block)
        return block

    def anfuegen(self, *bloecke: Block) -> None:
        """Fertige Bloecke uebernehmen -- etwa die Tabelle einer Zusammenfassung."""
        for block in bloecke:
            self._anfuegen(block)

    def titel(self, text: str, ebene: int = 2, raum: str = "") -> None:
        self._anfuegen(TitelBlock(text=text, ebene=ebene, raum=raum))

    def text(self, text: str) -> None:
        """Ein Ergebnis in Worten -- knapp, es steht in der Herleitung."""
        self._anfuegen(TextBlock(text=text))

    def erklaerung(self, text: str) -> None:
        """Das Warum -- steht in der Formelsammlung, nicht in der Herleitung."""
        self._anfuegen(TextBlock(text=text, erklaerung=True))

    def gleichung(self, latex: str, titel: str = "", referenz: str = "") -> None:
        """Setzt beliebiges, bereits fertiges LaTeX."""
        self._anfuegen(GleichungBlock(latex=latex, titel=titel, referenz=referenz,
                                      codestelle=_codestelle()))

    def ansatz(self, latex: str, titel: str = "", referenz: str = "", *,
               name: str = "") -> None:
        """Eine Gleichung ohne Zahlen -- sie kommt auch in die Formelsammlung."""
        self._anfuegen(GleichungBlock(latex=latex, titel=titel, referenz=referenz,
                                      ansatz=True, name=name,
                                      codestelle=_codestelle()))

    def formel(
        self,
        ergebnis: Wert,
        vorlage: str,
        eingaben: Mapping[str, Wert],
        titel: str = "",
        referenz: Optional[str] = None,
        *,
        empirisch: Optional[Mapping[str, Einheit]] = None,
        nachsatz: str = "",
        name: str = "",
        codestelle: str = "",
    ) -> None:
        """
        Der Regelfall: ``Symbol = analytische Formel = Formel mit Zahlen = Resultat``.

        Von Hand geschrieben wird nur ``vorlage`` (die analytische Form mit
        ``@name``-Platzhaltern). Die Fassung mit Zahlen und Einheiten entsteht
        automatisch aus ``eingaben``. Zwischenergebnisse, die keine Werte des
        Rechenwerks sind, legt :class:`Zwischenwerte` an.

        ``empirisch`` nennt die Eingaben einer dimensionell inhomogenen
        Normformel mit der Einheit, in der sie als blanke Zahl eingehen
        (:func:`latex.einsetzen_numerisch`). ``nachsatz`` steht hinter dem
        Resultat, etwa ein Vergleich (:func:`latex.vergleich`).

        ``name`` und ``codestelle`` sind fuer das Notizbuch (siehe
        :class:`GleichungBlock`); die Codestelle ermittelt sich selbst.
        """
        zeile = tex.Formelzeile.bauen(ergebnis, vorlage, eingaben,
                                      empirisch=empirisch, nachsatz=nachsatz)
        self._anfuegen(
            GleichungBlock(
                latex=zeile.darstellen(),
                titel=titel or ergebnis.beschreibung,
                referenz=ergebnis.referenz if referenz is None else referenz,
                wert_id=ergebnis.id,
                formelzeile=zeile,
                name=name,
                codestelle=codestelle or _codestelle(),
            )
        )

    def wert(self, ergebnis: Wert, titel: str = "", referenz: Optional[str] = None,
             gruppe: str = "", *, name: str = "", codestelle: str = "") -> None:
        """Schlichte Form ``Symbol = Wert`` -- fuer Eingaben und Vorgaben."""
        zeile = tex.Formelzeile.bauen(ergebnis)
        self._anfuegen(
            GleichungBlock(
                latex=zeile.einzeilig(),
                titel=titel or ergebnis.beschreibung,
                referenz=ergebnis.referenz if referenz is None else referenz,
                wert_id=ergebnis.id,
                gruppe=gruppe,
                formelzeile=zeile,
                name=name,
                codestelle=codestelle or _codestelle(),
            )
        )

    def tabelle(
        self,
        kopf: Sequence[tex.Zelle],
        zeilen: Iterable[Sequence[tex.Zelle]],
        titel: str = "",
        ausrichtung: Optional[str] = None,
    ) -> None:
        self._anfuegen(
            TabellenBlock(
                kopf=list(kopf),
                zeilen=[list(z) for z in zeilen],
                titel=titel,
                ausrichtung=ausrichtung,
            )
        )

    def hinweis(self, text: str) -> None:
        self._anfuegen(HinweisBlock(text=text, art=HinweisArt.INFO))

    def warnung(self, text: str) -> None:
        self._anfuegen(HinweisBlock(text=text, art=HinweisArt.WARNUNG))

    def annahme(self, text: str) -> None:
        """
        Haelt eine getroffene Annahme fest.

        Dafuer gedacht, dass empirische Normformeln ihre Einheiten-Konvention
        offenlegen (siehe ``einheiten.empirisch``).
        """
        self._anfuegen(HinweisBlock(text=text, art=HinweisArt.ANNAHME))

    def herkunft_stempeln(self, thema: str, ab: int = 0) -> None:
        """
        Das Thema auf die Bloecke ab ``ab``.

        Das Rechenwerk ruft das nach jeder Berechnung fuer das, was sie
        geschrieben hat. Die Formelsammlung ordnet danach; die Berechnung
        selbst muss nichts davon wissen. (Den Raum braucht es nicht: er
        steht am Titel des Abschnitts.)
        """
        for block in self.bloecke[ab:]:
            if isinstance(block, (GleichungBlock, TextBlock)):
                block.thema = block.thema or thema

    # -- Auswerten ----------------------------------------------------------

    @property
    def ist_leer(self) -> bool:
        return not self.bloecke

    def alle_bloecke(self) -> List[Block]:
        """
        Alle Bloecke -- als Liste.

        Als Liste und nicht als Generator: der Name verspricht eine Sammlung,
        und wer eine Sammlung zweimal durchlaeuft, erwartet zweimal dasselbe.
        Ein Generator gab beim zweiten Mal nichts zurueck, lautlos -- eine
        Pruefung, die danach «nicht gefunden» meldete, obwohl es dastand.
        Die Blockzahl ist die eines Berichts; sie in eine Liste zu legen
        kostet nichts.
        """
        return list(self.bloecke)

    def nach_abschnitten(self) -> List[Block]:
        """
        Dieselben Bloecke, aber je Abschnitt an einem Stueck.

        Gerechnet wird in Abhaengigkeitsreihenfolge, und die springt zwischen
        den Bauteilen hin und her: der Querkraftnachweis einer Platte braucht
        ihren Momentenwiderstand, kommt also erst, wenn *alle* M-N-Nachweise
        durch sind. Im Protokoll stand die Ueberschrift einer Platte darum
        zweimal, mit der anderen Platte dazwischen.

        Wer liest, erwartet alles zu einem Bauteil beieinander. Die Reihenfolge
        der Abschnitte bleibt die ihres ersten Auftretens, innerhalb eines
        Abschnitts bleibt die Rechenreihenfolge unangetastet -- verschoben wird
        also nur, was ohnehin nur der Darstellung dient.

        Eroeffnet wird ein Abschnitt von einem Titel mit Namensraum; alles
        davor (und jeder Titel ohne Namensraum) gehoert zum laufenden.
        """
        teile: Dict[str, List[Block]] = {}
        reihenfolge: List[str] = []
        raum = ""

        for block in self.bloecke:
            if isinstance(block, TitelBlock) and block.raum:
                raum = block.raum
                if raum in teile:
                    continue    # Die Ueberschrift steht schon da.
            if raum not in teile:
                teile[raum] = []
                reihenfolge.append(raum)
            teile[raum].append(block)

        return [block for r in reihenfolge for block in teile[r]]

    def gleichungen(self) -> List[GleichungBlock]:
        return [b for b in self.alle_bloecke() if isinstance(b, GleichungBlock)]

    def warnungen(self) -> List[HinweisBlock]:
        return [
            b
            for b in self.alle_bloecke()
            if isinstance(b, HinweisBlock) and b.art is HinweisArt.WARNUNG
        ]

    def __len__(self) -> int:
        return len(self.bloecke)

    def __repr__(self) -> str:
        return f"Protokoll({self.kopftitel!r}, {len(self.bloecke)} Bloecke)"


def codestelle_aus(modul: str, qualname: str) -> str:
    """
    ``modul:Klasse.methode`` -- so nennt das Notizbuch eine Stelle im Code.

    Ohne das, was nur in einer Funktion lebt (``<locals>``, ``<lambda>``):
    gemeint ist die Funktion, in der es steht. Eine Lambda auf Modulebene
    heisst schlicht wie ihr Modul.
    """
    teile = [t for t in qualname.split(".<locals>", 1)[0].split(".")
             if t and not t.startswith("<")]
    return f"{modul}:{'.'.join(teile)}" if teile else modul


def _codestelle() -> str:
    """
    Die Codestelle dessen, der gerade ins Protokoll schreibt: der erste
    Aufrufer ausserhalb dieses Moduls.

    Gefragt wird den Aufrufstapel und nicht die Berechnung, die laeuft: viele
    Formeln schreibt eine Hilfsfunktion in einem anderen Modul, und die
    Spannung-Dehnung-Analyse laeuft ganz ohne Rechenwerk. Das stille Protokoll
    fragt gar nicht -- es schreibt ja nichts.
    """
    rahmen = sys._getframe(1)
    while rahmen is not None and rahmen.f_globals.get("__name__") == __name__:
        rahmen = rahmen.f_back
    if rahmen is None:
        return ""
    code = rahmen.f_code
    return codestelle_aus(rahmen.f_globals.get("__name__", ""),
                          getattr(code, "co_qualname", code.co_name))


class StillesProtokoll(Protokoll):
    """
    Verwirft alles. Fuer Laeufe, deren Herleitung niemand liest.

    Die Schnittstelle bleibt identisch, damit derselbe Rechencode einmal
    protokollierend und einmal still laufen kann -- ohne Verzweigung im Code
    und ohne dass die beiden Pfade auseinanderlaufen koennen.

    Gebaut wird gar nichts, nicht erst gebaut und dann verworfen: eine Formel
    setzt ihre Vorlage zweimal ein und misst ihre Breite, und die
    Bewehrungssuche rechnet hundertfach, ohne je eine Zeile zu zeigen.
    """

    def _anfuegen(self, block: Block) -> Block:
        return block

    def titel(self, *_, **__) -> None:
        pass

    def text(self, *_, **__) -> None:
        pass

    def erklaerung(self, *_, **__) -> None:
        pass

    def gleichung(self, *_, **__) -> None:
        pass

    def ansatz(self, *_, **__) -> None:
        pass

    def formel(self, *_, **__) -> None:
        pass

    def wert(self, *_, **__) -> None:
        pass

    def tabelle(self, *_, **__) -> None:
        pass

    @property
    def ist_leer(self) -> bool:
        return True


# ===========================================================================
# Zwischenwerte
# ===========================================================================


class Zwischenwerte:
    """
    Benannte Zwischenwerte fuer :meth:`Protokoll.formel`.

    Eine Vorlage wird zweimal eingesetzt, mit Symbolen und mit Zahlen samt
    Einheit. Dafuer braucht jede Groesse ein Symbol, eine Einheit und eine
    Stellenzahl -- auch ein Zwischenergebnis, das kein Wert des Rechenwerks
    ist. Hier entstehen solche Werte, mit festen Gewohnheiten je Groessenart:
    Laengen in mm auf eine Stelle, Flaechen in mm² und Spannungen in N/mm²
    ganz, Kraefte in kN und Momente in kNm auf eine Stelle, Dehnungen in
    Promille auf zwei, Kruemmungen in 1/m auf fuenf; wo eine Groesse mehr verlangt (die Zugfestigkeit des
    Betons auf zwei Stellen), sagt es ``stellen``. Jede Stelle, die das von
    Hand tat, rechnete dafuer selbst um und schrieb die Einheit selbst dazu.

    Die Kennung ist ``{basis}.{name}``: eindeutig in der Mitschrift, aber nie
    im Rechenwerk angemeldet -- diese Werte zeigen eine Rechnung, sie gehen in
    keine ein.
    """

    def __init__(self, basis: str) -> None:
        self.basis = basis

    def wert(self, name: str, symbol: str, groesse: Groesse,
             stellen: int = 1, beschreibung: str = "") -> Wert:
        """Ein Zwischenwert in der Einheit, in der ``groesse`` angezeigt wird."""
        return WertDef(
            id=f"{self.basis}.{name}", symbol=symbol, einheit=groesse.anzeige,
            beschreibung=beschreibung, stellen=stellen,
        ).belegen(groesse)

    def laenge(self, name: str, symbol: str, si: float, beschreibung: str = "",
               *, stellen: int = 1) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, MM), stellen, beschreibung)

    def flaeche(self, name: str, symbol: str, si: float, beschreibung: str = "",
                *, stellen: int = 0) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, MM2), stellen, beschreibung)

    def spannung(self, name: str, symbol: str, si: float, beschreibung: str = "",
                 *, stellen: int = 0) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, N_PRO_MM2), stellen, beschreibung)

    def kraft(self, name: str, symbol: str, si: float, beschreibung: str = "",
              *, stellen: int = 1) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, KN), stellen, beschreibung)

    def moment(self, name: str, symbol: str, si: float, beschreibung: str = "",
               *, stellen: int = 1) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, KNM), stellen, beschreibung)

    def dehnung(self, name: str, symbol: str, si: float, beschreibung: str = "",
                *, stellen: int = 2) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, PROMILLE), stellen, beschreibung)

    def kruemmung(self, name: str, symbol: str, si: float, beschreibung: str = "",
                  *, stellen: int = 5) -> Wert:
        return self.wert(name, symbol, Groesse.aus_si(si, PRO_M), stellen, beschreibung)

    def zahl(self, name: str, symbol: str, zahl: float, beschreibung: str = "",
             *, stellen: int = 3) -> Wert:
        return self.wert(name, symbol, Groesse(zahl, EINHEITSLOS), stellen, beschreibung)


# ===========================================================================
# Darstellen
# ===========================================================================

T = TypeVar("T")

#: Wie eine Darstellung die Bloecke setzt: je Blockart eine Funktion, die den
#: Block bekommt. Bis 2026-10-25 bekam sie auch seine Tiefe -- die Zahl der
#: eingeschachtelten Mitschriften, in denen er stand; die schrieb da keine
#: Rechnung mehr.
Tafel = Mapping[Type[Block], Callable[[Any], T]]


def darstellen(protokoll: Protokoll, tafel: Tafel[T]) -> List[T]:
    """
    Setzt jeden Block eines Protokolls mit der Funktion seiner Art.

    Ein Durchlauf fuer alle Darstellungen. Vorher unterschied jede die
    Blockarten mit einer eigenen ``if/elif``-Kette, und die der Oberflaeche
    liess eine unbekannte Art stillschweigend weg. Jetzt wirft eine Blockart
    ohne Eintrag: eine neue fehlt nicht still in der Darstellung, die sie
    noch nicht kennt.

    Gesucht wird die genaue Art, nicht eine Oberklasse -- auch eine
    abgeleitete Blockart braucht ihren eigenen Eintrag.

    Erklaerungen (:attr:`TextBlock.erklaerung`) laesst jede Darstellung weg:
    sie stehen in der Formelsammlung. Hier, an der einen Stelle, durch die
    Oberflaeche und alle Berichte gehen.
    """
    heraus: List[T] = []
    for block in protokoll.nach_abschnitten():
        if isinstance(block, TextBlock) and block.erklaerung:
            continue
        setzen = tafel.get(type(block))
        if setzen is None:
            raise TypeError(
                f"Diese Darstellung kennt keine {type(block).__name__}.")
        heraus.append(setzen(block))
    return heraus
