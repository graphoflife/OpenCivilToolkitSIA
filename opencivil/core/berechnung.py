"""
opencivil/core/berechnung.py -- Berechnungen als Objekte.

VERANTWORTUNG:
Jeder Rechenschritt ist ein Objekt, das weiss, welche Werte es braucht, welche
es liefert, wie gerechnet wird und wie das Ergebnis aufzuschreiben ist.

DREI AUSPRAEGUNGEN:
* :class:`Formel`   -- ein Einzeiler: eine Ausgabe, eine analytische Formel.
* :class:`Prozedur` -- ein ganzer Ablauf: mehrere Ausgaben, Iterationen,
  Fallunterscheidungen; schreibt ihren Ablauf selbst ins Protokoll.
* :class:`Nachweis` -- ein Vergleich von Einwirkung und Widerstand mit Urteil
  und Erfuellungsgrad.

VARIANTEN -- WELCHE FORMEL GILT?
Oft haengt es von den vorhandenen Eingaben ab, welche Formel anzuwenden ist.
Dafuer duerfen mehrere Berechnungen denselben Wert liefern. Der Loeser waehlt
unter ihnen in zwei Stufen:

1. *Verfuegbarkeit* -- sind alle Pflichteingaben ueberhaupt beschaffbar?
2. *Anwendbarkeit*  -- :meth:`Berechnung.anwendbar` darf zusaetzlich von den
   tatsaechlichen Zahlenwerten abhaengen (z.B. "nur fuer f_ck <= 50 N/mm^2").

Die Begruendung der Wahl landet im Protokoll -- der Leser sieht, warum gerade
diese Formel gegriffen hat.

FEHLER WERDEN NICHT VERSCHLUCKT.
Im alten Code fing der Wertzugriff jede Ausnahme ab, warnte und lieferte einen
veralteten Wert zurueck -- eine defekte Formel ergab damit eine plausible
falsche Zahl. Hier fuehrt jeder Rechenfehler zu einem :class:`BerechnungsFehler`
mit Angabe der schuldigen Berechnung; die urspruengliche Ausnahme bleibt als
Ursache erhalten.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import (
    Any, Callable, Dict, Iterable, Iterator, Mapping, Optional, Sequence,
    Tuple, Union,
)

from opencivil.core import latex as tex
from opencivil.core.einheiten import EINHEITSLOS, EmpirischesErgebnis, Groesse
from opencivil.core.protokoll import Abschnitt, Protokoll
from opencivil.core.wert import Quelle, Wert, WertDef, grad_als_text


class BerechnungsFehler(Exception):
    """Eine Berechnung ist gescheitert. Die Ursache bleibt angehaengt."""

    def __init__(self, berechnung_id: str, meldung: str) -> None:
        self.berechnung_id = berechnung_id
        super().__init__(f"Berechnung '{berechnung_id}': {meldung}")


# ===========================================================================
# Eingaben
# ===========================================================================


@dataclass(frozen=True)
class Eingabebezug:
    """Bindet einen lokalen Formelnamen an eine globale Wert-ID."""

    name: str
    """Kurzer Name in Formel und Vorlage, z.B. ``f_ck``."""

    wert_id: str
    """Globale ID des Wertes, z.B. ``beton.C30_37.f_ck``."""

    optional: bool = False
    """Wenn True, darf der Wert fehlen; die Berechnung prueft mit ``hat()``."""


class Eingaben(Mapping[str, Wert]):
    """
    Die aufgeloesten Eingaben einer Berechnung, unter ihren lokalen Namen.

    Ist selbst eine ``Mapping``, damit sie direkt an die LaTeX-Hilfen
    weitergereicht werden kann.
    """

    def __init__(self, werte: Mapping[str, Wert]) -> None:
        self._werte: Dict[str, Wert] = dict(werte)

    # -- Mapping ------------------------------------------------------------

    def __getitem__(self, name: str) -> Wert:
        try:
            return self._werte[name]
        except KeyError:
            raise KeyError(
                f"Eingabe '{name}' wurde nicht deklariert. Vorhanden: {sorted(self._werte)}."
            ) from None

    def __iter__(self) -> Iterator[str]:
        return iter(self._werte)

    def __len__(self) -> int:
        return len(self._werte)

    # -- Bequemer Zugriff ---------------------------------------------------

    def hat(self, name: str) -> bool:
        """Prueft, ob eine optionale Eingabe vorliegt."""
        return name in self._werte

    def g(self, name: str) -> Groesse:
        """Nur die Groesse -- die Kurzform fuers Rechnen."""
        return self[name].groesse

    def groessen(self) -> Dict[str, Groesse]:
        """Alle Eingaben als ``name -> Groesse``, passend fuer ``funktion(**...)``."""
        return {name: wert.groesse for name, wert in self._werte.items()}

    def teilmenge(self, *namen: str) -> "Eingaben":
        """Auswahl einzelner Eingaben -- praktisch fuer LaTeX-Vorlagen."""
        return Eingaben({n: self._werte[n] for n in namen if n in self._werte})

    def __repr__(self) -> str:
        return f"Eingaben({', '.join(sorted(self._werte))})"


# ===========================================================================
# Berechnung
# ===========================================================================


class Berechnung(ABC):
    """
    Basisklasse aller Rechenschritte.

    Unterklassen implementieren :meth:`rechne`. Aufgerufen wird immer
    :meth:`ausfuehren`, das die Ergebnisse prueft und in :class:`Wert` verpackt.
    """

    THEMA: str = ""
    """
    Unter welchem Thema ihre Formeln in der Formelsammlung stehen -- ein
    Nachweis nennt sich selbst. Leer: das Thema ihres Abschnitts.
    """

    @property
    def thema(self) -> str:
        return self.THEMA or (self.abschnitt.thema if self.abschnitt else "")

    def __init__(
        self,
        id: str,
        *,
        ausgaben: Sequence[WertDef],
        bezuege: Sequence[Eingabebezug] = (),
        titel: str = "",
        referenz: str = "",
        prioritaet: int = 0,
        begruendung: str = "",
        abschnitt: Optional[Abschnitt] = None,
    ) -> None:
        if not ausgaben:
            raise ValueError(f"Berechnung '{id}' liefert keine Ausgaben.")
        self.id = id
        self.ausgaben: Tuple[WertDef, ...] = tuple(ausgaben)
        self.bezuege: Tuple[Eingabebezug, ...] = tuple(bezuege)
        self.abschnitt = abschnitt
        """
        Ueberschrift, unter die diese Berechnung gehoert.

        Der Loeser setzt sie, sobald die erste Berechnung eines Abschnitts an
        die Reihe kommt. Sie hier zu hinterlegen statt sie irgendwo von Hand zu
        schreiben ist der einzige verlaessliche Weg: welche Berechnung eines
        Bauteils zuerst laeuft, entscheidet die Abhaengigkeitsfolge und nicht
        die Reihenfolge im Quelltext.
        """
        self.titel = titel or (ausgaben[0].beschreibung if ausgaben else id)
        self.referenz = referenz or (ausgaben[0].referenz if ausgaben else "")
        self.prioritaet = prioritaet
        """Hoehere Prioritaet wird bei mehreren moeglichen Varianten bevorzugt."""
        self.begruendung = begruendung
        """Warum es diese Variante gibt -- erscheint im Protokoll."""

        namen = [b.name for b in self.bezuege]
        doppelt = {n for n in namen if namen.count(n) > 1}
        if doppelt:
            raise ValueError(f"Berechnung '{id}': doppelte Eingabenamen {sorted(doppelt)}.")

    # -- Deklaration --------------------------------------------------------

    @property
    def ausgabe_ids(self) -> Tuple[str, ...]:
        return tuple(a.id for a in self.ausgaben)

    @property
    def pflicht_eingaben(self) -> Tuple[str, ...]:
        """Wert-IDs, ohne die nicht gerechnet werden kann."""
        return tuple(b.wert_id for b in self.bezuege if not b.optional)

    @property
    def optionale_eingaben(self) -> Tuple[str, ...]:
        return tuple(b.wert_id for b in self.bezuege if b.optional)

    @property
    def alle_eingaben(self) -> Tuple[str, ...]:
        return tuple(b.wert_id for b in self.bezuege)

    def ausgabe_def(self, wert_id: str) -> WertDef:
        for a in self.ausgaben:
            if a.id == wert_id:
                return a
        raise KeyError(f"Berechnung '{self.id}' liefert '{wert_id}' nicht.")

    @property
    def ausgabe_quelle(self) -> Quelle:
        """
        Als was die Ergebnisse gelten sollen.

        Normalfall ist ``BERECHNET``. :class:`Vorgabe` setzt das auf ``VORGABE``,
        damit im Bericht erkennbar bleibt, dass hier nichts hergeleitet wurde.
        """
        return Quelle.BERECHNET

    # -- Variantenwahl ------------------------------------------------------

    def anwendbar(self, eingaben: Eingaben) -> Tuple[bool, str]:
        """
        Darf diese Variante mit diesen Werten verwendet werden?

        Standardmaessig ja. Ueberschreiben, wenn die Gueltigkeit vom Zahlenwert
        abhaengt, z.B.::

            def anwendbar(self, e):
                if e.g("f_ck") > Groesse(50, MPA):
                    return False, "gilt nur bis C50/60"
                return True, "f_ck liegt im Gueltigkeitsbereich"

        :return: (anwendbar, Begruendung fuers Protokoll)
        """
        return True, self.begruendung

    # -- Rechnen ------------------------------------------------------------

    @abstractmethod
    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        """
        Fuehrt die Rechnung aus und schreibt sie ins Protokoll.

        :param e: aufgeloeste Eingaben unter ihren lokalen Namen
        :param p: Mitschrift -- hier wird die Herleitung festgehalten
        :return: ``{Wert-ID: Groesse}`` fuer jede deklarierte Ausgabe
        """

    def ausfuehren(self, e: Eingaben, p: Protokoll) -> Dict[str, Wert]:
        """
        Ruft :meth:`rechne` auf und prueft dessen Ergebnis.

        Verpackt jede Groesse in einen :class:`Wert` mit der deklarierten
        Definition -- dabei wird auch die Dimension geprueft.
        """
        try:
            roh = self.rechne(e, p)
        except BerechnungsFehler:
            raise
        except Exception as exc:
            raise BerechnungsFehler(self.id, f"{type(exc).__name__}: {exc}") from exc

        if not isinstance(roh, Mapping):
            raise BerechnungsFehler(
                self.id, f"rechne() muss ein Mapping liefern, erhalten: {type(roh).__name__}."
            )

        erwartet = set(self.ausgabe_ids)
        geliefert = set(roh)
        if fehlend := erwartet - geliefert:
            raise BerechnungsFehler(self.id, f"Ausgaben fehlen: {sorted(fehlend)}.")
        if unerwartet := geliefert - erwartet:
            raise BerechnungsFehler(
                self.id, f"Nicht deklarierte Ausgaben geliefert: {sorted(unerwartet)}."
            )

        ergebnis: Dict[str, Wert] = {}
        for wert_id, groesse in roh.items():
            if not isinstance(groesse, Groesse):
                raise BerechnungsFehler(
                    self.id,
                    f"Ausgabe '{wert_id}' ist keine Groesse, sondern "
                    f"{type(groesse).__name__}. Bitte mit Einheit zurueckgeben.",
                )
            definition = self.ausgabe_def(wert_id)
            try:
                ergebnis[wert_id] = definition.belegen(
                    groesse.als(definition.einheit)
                    if groesse.dimension == definition.einheit.dimension
                    else groesse,
                    quelle=self.ausgabe_quelle,
                    herkunft=self.id,
                )
            except Exception as exc:
                raise BerechnungsFehler(self.id, f"Ausgabe '{wert_id}': {exc}") from exc
        return ergebnis

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.id!r} -> {list(self.ausgabe_ids)})"


# ===========================================================================
# Formel -- der Einzeiler
# ===========================================================================

#: Eine Rechenfunktion bekommt die Eingaben als Groessen unter ihren lokalen
#: Namen und liefert eine Groesse -- oder ein EmpirischesErgebnis, wenn die
#: Normformel dimensionell inhomogen ist.
FormelFunktion = Callable[..., Union[Groesse, EmpirischesErgebnis]]


class Formel(Berechnung):
    """
    Eine Ausgabe, eine analytische Formel.

    Die Vorlage wird nur *analytisch* geschrieben; die Fassung mit Zahlen und
    Einheiten entsteht daraus automatisch::

        Formel(
            id="beton.C30_37.f_cd",
            ausgabe=f_cd_def,
            eingaben={"eta_fc": "beton.C30_37.eta_fc",
                      "f_ck":   "beton.C30_37.f_ck",
                      "gamma_c":"beton.C30_37.gamma_c"},
            vorlage=r"\\frac{@eta_fc \\cdot @f_ck}{@gamma_c}",
            funktion=lambda eta_fc, f_ck, gamma_c: eta_fc * f_ck / gamma_c,
        )

    ergibt im Bericht::

        f_{cd} = \\frac{\\eta_{fc} \\cdot f_{ck}}{\\gamma_c}
               = \\frac{0.933 \\cdot 30\\,\\mathrm{N/mm^2}}{1.5}
               = 18.7\\,\\mathrm{N/mm^2}
    """

    def __init__(
        self,
        id: str,
        *,
        ausgabe: WertDef,
        funktion: FormelFunktion,
        vorlage: Optional[str] = None,
        eingaben: Optional[Mapping[str, str]] = None,
        optionale_eingaben: Optional[Mapping[str, str]] = None,
        titel: str = "",
        referenz: str = "",
        prioritaet: int = 0,
        begruendung: str = "",
        abschnitt: Optional[Abschnitt] = None,
        bedingung: Optional[Callable[[Eingaben], Tuple[bool, str]]] = None,
    ) -> None:
        bezuege = [Eingabebezug(name, wid) for name, wid in (eingaben or {}).items()]
        bezuege += [
            Eingabebezug(name, wid, optional=True)
            for name, wid in (optionale_eingaben or {}).items()
        ]
        super().__init__(
            id,
            ausgaben=[ausgabe],
            bezuege=bezuege,
            titel=titel,
            referenz=referenz or ausgabe.referenz,
            prioritaet=prioritaet,
            begruendung=begruendung,
            abschnitt=abschnitt,
        )
        self.ausgabe = ausgabe
        self.funktion = funktion
        self.vorlage = vorlage
        self._bedingung = bedingung

    def anwendbar(self, eingaben: Eingaben) -> Tuple[bool, str]:
        if self._bedingung is None:
            return True, self.begruendung
        return self._bedingung(eingaben)

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        roh = self.funktion(**e.groessen())

        # Eine empirische Formel verlangt ihre Eingaben als blanke Zahlen in
        # bestimmten Einheiten. So stehen sie auch in der Herleitung -- mit
        # Einheit eingesetzt stuende dort die Wurzel einer Spannung.
        empirisch = None
        if isinstance(roh, EmpirischesErgebnis):
            groesse = roh.wert
            empirisch = roh.einheiten
        elif isinstance(roh, Groesse):
            groesse = roh
        else:
            raise BerechnungsFehler(
                self.id,
                f"funktion() muss eine Groesse liefern, erhalten: {type(roh).__name__}.",
            )

        wert = self.ausgabe.belegen(groesse, Quelle.BERECHNET, herkunft=self.id)
        if self.vorlage:
            # Nur die in der Vorlage benutzten Eingaben werden eingesetzt --
            # optionale, die diesmal fehlen, stoeren so nicht.
            p.formel(wert, self.vorlage, e, titel=self.titel, referenz=self.referenz,
                     empirisch=empirisch)
        else:
            p.wert(wert, titel=self.titel, referenz=self.referenz)
        # Die Begruendung schreibt der Loeser -- er weiss als einziger, ob es
        # ueberhaupt eine Variante zu waehlen gab.
        return {self.ausgabe.id: groesse}


class Vorgabe(Berechnung):
    """
    Liefert einen festen Wert ohne Herleitung -- Normvorgabe oder Vorlagenwert.

    Erlaubt es, auch Konstanten (Teilsicherheitsbeiwerte, Tabellenwerte) als
    ordentliche Knoten im Rechengraph zu fuehren, statt sie im Code zu
    verstecken. Der Benutzer kann sie damit ueberall gleich ueberschreiben.
    """

    def __init__(
        self,
        id: str,
        *,
        ausgabe: WertDef,
        groesse: Groesse,
        quelle: Quelle = Quelle.VORGABE,
        titel: str = "",
        referenz: str = "",
        begruendung: str = "",
        abschnitt: Optional[Abschnitt] = None,
        stumm: bool = False,
        gruppe: str = "",
    ) -> None:
        super().__init__(
            id,
            ausgaben=[ausgabe],
            titel=titel,
            referenz=referenz or ausgabe.referenz,
            begruendung=begruendung,
            abschnitt=abschnitt,
        )
        self.ausgabe = ausgabe
        self.groesse = groesse
        self.quelle = quelle

        self.gruppe = gruppe
        """
        Kasten, in dem diese Vorgabe mit anderen zusammensteht.

        Nur Darstellung: die Vorgabe bleibt ein eigener Knoten mit eigenem
        Block. Damit zeigt der Kasten bei einer Rueckverfolgung von selbst nur
        die Angaben, die dafuer gebraucht wurden -- die uebrigen Vorgaben
        laufen gar nicht erst.
        """

        self.stumm = stumm
        """
        Schreibt keinen eigenen Block in die Mitschrift.

        Der Wert bleibt ein vollwertiger Knoten im Rechengraph -- er steht in
        der Werteliste und laesst sich ueberschreiben wie jeder andere. Nur
        seine eigene Zeile faellt weg, weil er anderswo schon dasteht: die
        Stabdurchmesser in der Lagentabelle, das Groesstkorn beim
        Querkraftnachweis, der ihn braucht. Vierzehn Zeilen der Form
        ``∅ = 12 mm`` untereinander sind keine Herleitung.
        """

    @property
    def ausgabe_quelle(self) -> Quelle:
        return self.quelle

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        wert = self.ausgabe.belegen(self.groesse, self.quelle, herkunft=self.id)
        if not self.stumm:
            p.wert(wert, titel=self.titel, referenz=self.referenz,
                   gruppe=self.gruppe)
        return {self.ausgabe.id: self.groesse}


# ===========================================================================
# Prozedur -- der ganze Ablauf
# ===========================================================================


class Prozedur(Berechnung):
    """
    Ein mehrstufiger Ablauf: Iterationen, Fallunterscheidungen, mehrere Ausgaben.

    Unterklassen implementieren :meth:`rechne` und schreiben dabei ihren Ablauf
    ins Protokoll -- Ansatz, Startwerte, Zwischenschritte (gerne als Tabelle),
    Abbruchkriterium, Ergebnis. Der Leser muss die Rechnung von Hand
    nachvollziehen koennen; nur das Endergebnis auszugeben genuegt nicht.

    Beispielgeruest::

        class Nulllinienlage(Prozedur):
            def rechne(self, e, p):
                p.text("Die Nulllinie wird iterativ aus dem Kraeftegleichgewicht bestimmt.")
                zeilen = []
                for schritt in range(...):
                    ...
                    zeilen.append([Mathe(str(schritt)), Mathe(x.formatiert(1)),
                                   Mathe(fehler.formatiert(2))])
                p.tabelle([Mathe("i"), Mathe("x"), Mathe(r"\\Delta F")], zeilen,
                          titel="Iterationsverlauf")
                p.formel(...)
                return {...}
    """


# ===========================================================================
# Nachweis
# ===========================================================================


def grad_def(id: str, symbol: str, beschreibung: str, referenz: str = "") -> WertDef:
    """
    Die Definition eines Erfuellungsgrads -- fuer jeden Nachweis dieselbe.

    Frueher legte jeder Nachweis seine eigene an, mit eigener Stellenzahl, und
    die Werttabelle rundete an :func:`grad_als_text` vorbei: dort stand 0.996
    als «1», neben «nicht erfuellt».
    """
    return WertDef(id=id, symbol=symbol, einheit=EINHEITSLOS,
                   beschreibung=beschreibung, referenz=referenz,
                   erfuellungsgrad=True)


def grad_formel(
    p: Protokoll, definition: WertDef, grad: float, widerstand: Wert,
    einwirkung: Wert, erfuellt: bool, *, mit_urteil: bool = False,
) -> None:
    """
    Die Zeile mit dem Erfuellungsgrad -- in jedem Nachweis dieselbe Form,
    Widerstand durch Einwirkung.

    Der Grad setzt sich selbst (:func:`grad_als_text`). Stuende im Nenner eine
    Null, bleibt es bei den Symbolen. Ohne Normverweis -- den traegt die
    Zeile, aus der Widerstand und Einwirkung kommen.
    """
    if einwirkung.formatiert() == "0":
        vorlage, eingaben = rf"\frac{{{widerstand.symbol}}}{{{einwirkung.symbol}}}", {}
    else:
        vorlage, eingaben = r"\frac{@R}{@E}", {"R": widerstand, "E": einwirkung}
    p.formel(definition.belegen(Groesse(grad, EINHEITSLOS)), vorlage, eingaben,
             titel="Erfüllungsgrad", referenz="",
             nachsatz=tex.folgerung(erfuellt) if mit_urteil else "")



@dataclass(frozen=True)
class NachweisUrteil:
    """
    Ergebnis eines Nachweises.

    ``erfuellungsgrad`` ist das Verhaeltnis Widerstand/Einwirkung: um welchen
    Faktor die Einwirkung noch wachsen duerfte. Werte ab 1 bedeuten erfuellt.

    Bewusst nur diese eine Kennzahl -- die Ausnutzung als Kehrwert waere
    dieselbe Aussage in anderer Richtung und muesste an jeder Stelle mitgepflegt
    und mitgelesen werden.
    """

    name: str
    erfuellt: bool
    erfuellungsgrad: Groesse
    begruendung: str = ""
    einwirkung: Optional[Wert] = None
    widerstand: Optional[Wert] = None

    art: str = ""
    """
    Kurzzeichen der Nachweisart -- ``M-N`` oder ``V``.

    Zusammen mit :attr:`fall` ergibt es die knappe Bezeichnung fuer die
    Zusammenfassung. Getrennt gefuehrt und nicht aus :attr:`name`
    herausgeschnitten: den langen Namen zu zerlegen hiesse, aus Anzeigetext auf
    Bedeutung zu schliessen -- genau der Fehler, der die Nachweise mehrerer
    Platten schon einmal in dieselbe Tabelle gepackt hat.
    """

    langname: str = ""
    """
    Die Nachweisart ausgeschrieben -- ``Biegung und Normalkraft (x)``.

    Steht in der Zusammenfassung in einer eigenen Spalte neben
    :attr:`fall`. Sie wird hier gefuehrt und nicht in der Schnittstelle aus
    :attr:`art` nachgeschlagen: eine Tabelle von Kuerzeln auf Klartext waere
    eine zweite Stelle, an der jeder neue Nachweis eingetragen werden muss --
    und die eine, die man vergisst.

    Die Tragrichtung gehoert hier hinein, wo eine da ist. In der Zeile steht
    sie sonst nirgends, und zwei Kombinationen gleichen Namens in x und y
    saehen in der Tabelle gleich aus.
    """

    fall: str = ""
    """
    Bezeichnung dieses einen Falls -- der eingestellte Name, wo es einen gibt.

    Bei einer Einwirkungskombination ist das ihr Name, bei einem Nachweis je
    Lage die Lage. Ohne Richtung: die steht in :attr:`langname`.
    """

    hinweis: str = ""
    """
    Was in der Zusammenfassung sichtbar dabeistehen muss.

    Fuer den Fall, dass sich gar kein Widerstand bestimmen liess -- keine
    Bewehrung auf der gezogenen Seite, eine Buegeldefinition ohne Bezug in
    dieser Richtung, eine Lage, die es nicht gibt. Dann steht in der Tabelle
    eine Null oder ein Strich, und eine Null erklaert sich nicht von selbst.

    Getrennt von :attr:`begruendung`: die traegt jedes Urteil, auch das
    erfuellte, und gehoert in den Tooltip. Dieses Feld setzt nur, wer etwas zu
    melden hat -- die Pruefung weiss es, die Schnittstelle soll es nicht aus
    einer Null erraten muessen.
    """

    ziel: str = ""
    """
    Wert-ID des Erfuellungsgrads, der dieses Urteil traegt.

    Das Ziel, mit dem sich genau dieser Nachweis samt allem, was er braucht,
    nachrechnen laesst -- das Auge in der Zusammenfassung. Gesetzt von der
    Pruefung: nur sie weiss, welcher ihrer Grade zu welchem Fall gehoert.
    """

    sammel: bool = False
    """
    Ob dieses Urteil eines von mehreren zur selben Frage ist.

    Die Nachweise, die je Bewehrungslage rechnen, faellen ein Urteil je Lage.
    Beantwortet ist die Frage aber von der schlechtesten: geht die auf, gehen
    die anderen erst recht auf. In Tabelle und Bericht steht darum nur sie --
    siehe :attr:`Loesung.gefuehrte_urteile`.

    Gerechnet und *gezaehlt* werden trotzdem alle. Die Bewehrungssuche misst
    ihren Fortschritt an der Summe der Rueckstaende; saehe sie nur das
    Minimum, stuende sie, sobald zwei Lagen gleich schlecht sind -- kein
    einzelner Schritt hebt dann das Minimum, und die Suche gaebe auf, obwohl
    der naechste Durchmesser offensichtlich hilft.
    """

    still: bool = False
    """
    Ob dieses Urteil aus einem ausgeschalteten Nachweis stammt.

    Es zaehlt dann nicht in der Zusammenfassung und nicht im Gesamturteil --
    sichtbar wird es nur als Hinweis darunter, und auch nur, wenn es nicht
    aufgeht.
    """

    raum: str = ""
    """
    Namensraum des Nachweises, der dieses Urteil gefaellt hat.

    Wird von :meth:`Nachweis.rechne` gesetzt, nicht beim Erzeugen -- so kann
    kein Nachweis ihn vergessen oder falsch angeben. Die Oberflaeche gruppiert
    danach; ohne ihn muesste sie aus dem Anzeigetext zurueckschliessen, welche
    Platte gemeint ist, und das geht schief, sobald zwei Platten dieselben
    Richtungen tragen.
    """

    @property
    def meldenswert(self) -> bool:
        """
        Ob dieses stille Urteil einen Hinweis wert ist.

        Nur was still ist und nicht aufgeht -- und nur, wenn es ueberhaupt
        einen Widerstand gibt. Ohne ihn liess sich der Nachweis gar nicht
        fuehren (etwa an einer unbewehrten Lage); das ist keine Auskunft
        ueber die Bewehrung, sondern darueber, dass es keine gibt.

        Die Regel steht hier und nicht in der Schnittstelle: Tabelle,
        Konsolenbericht und LaTeX-Dokument stellen dieselbe Frage, und drei
        Antworten darauf waeren drei Gelegenheiten, auseinanderzulaufen.
        """
        return self.still and not self.erfuellt and self.widerstand is not None

    @property
    def kurzname(self) -> str:
        """
        Die knappe Bezeichnung, z.B. ``M-N: Fall 1``.

        Fuer Meldungen und Protokolle. Die Zusammenfassung nimmt statt
        dessen :attr:`langname` und :attr:`fall` in zwei Spalten -- ein
        Kuerzel spart Platz, den man in einer Tabelle nicht braucht, und
        kostet eine Legende, die es nicht gibt.
        """
        if self.art and self.fall:
            return f"{self.art}: {self.fall}"
        return self.name

    def gradtext(self, *, latex: bool = False) -> str:
        """Der Erfuellungsgrad als Text -- siehe :func:`grad_als_text`."""
        return grad_als_text(self.erfuellungsgrad.si, self.erfuellt, latex=latex)

    def __str__(self) -> str:
        urteil = "erfüllt" if self.erfuellt else "NICHT erfüllt"
        return f"{self.name}: {urteil} (Erfüllungsgrad {self.gradtext()})"


class Nachweis(Berechnung):
    """
    Vergleicht Einwirkung und Widerstand und faellt ein Urteil.

    Unterklassen implementieren :meth:`pruefe` statt :meth:`rechne`. Die
    Urteile werden gesammelt und stehen nach dem Lauf unter :attr:`urteile`
    zur Verfuegung -- der Bericht kann daraus die Nachweistabelle bauen.
    """

    still: bool = False
    """
    Ob der Nachweis mitrechnet, ohne in die Herleitung zu kommen.

    Ausgeschaltete Nachweise verschwinden nicht, sie werden still: gerechnet
    wird weiter, in der Zusammenfassung stehen sie nicht, und wenn einer von
    ihnen nicht aufgeht, steht darunter ein Hinweis. Das ist der Unterschied
    zwischen «interessiert mich gerade nicht» und «gilt nicht» -- und nur das
    erste trifft auf einen Schalter zu, den jemand umgelegt hat.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.urteile: list[NachweisUrteil] = []
        self.stille_faelle: set = set()
        """
        Welche einzelnen Faelle still bleiben, obwohl der Nachweis laeuft.

        Ein Nachweis deckt oft mehrere Faelle ab -- vier Lagen, mehrere
        Lastfaelle --, und eingeschaltet wird jeder fuer sich. Ohne diese
        Menge haette ein einzelner Haken alle vier Lagen in die Tabelle
        gehoben; der Schalter neben den anderen dreien waere wirkungslos
        geworden, ohne es zu zeigen.

        Worauf sich die Schluessel beziehen, entscheidet der Nachweis --
        Lagennummer oder Fallname. Gefragt wird ueber :meth:`leise`, und
        gefuellt ueber :meth:`stillstellen`.
        """

    def leise(self, schluessel: Any) -> bool:
        """Ob dieser Fall nur mitrechnet: einzeln oder mit dem ganzen Nachweis."""
        return self.still or schluessel in self.stille_faelle

    @staticmethod
    def massgebend(
        urteile: Sequence[NachweisUrteil],
    ) -> List[NachweisUrteil]:
        """
        Von mehreren Teilurteilen das schlechteste -- als Liste.

        Wer eine Tabelle baut, meint dieses eine; leer bleibt leer.
        """
        if not urteile:
            return []
        return [min(urteile, key=lambda u: u.erfuellungsgrad.si)]

    def protokoll_massgebend(self, p: Protokoll,
                             urteile: Sequence[NachweisUrteil]) -> None:
        """
        Welcher Teil entscheidet, wo es mehrere gibt -- etwa zwei Lagen.

        In der Zusammenfassung steht nur der schlechteste; ohne diese Zeile
        muesste man die Zahlen der Herleitung selbst vergleichen, um zu wissen,
        welcher dort gelandet ist.
        """
        massgebend = self.massgebend(urteile)
        if len(urteile) >= 2 and massgebend:
            p.text(f"Massgebend: {massgebend[0].fall} (kleinster Erfüllungsgrad).")

    @staticmethod
    def teilurteile(
        urteile: Sequence[NachweisUrteil],
    ) -> List[NachweisUrteil]:
        """
        Dieselben Urteile, jedes als Teil derselben Frage gekennzeichnet.

        Zurueck kommt alles: gezaehlt und gerechnet wird jede Lage. Erst die
        Darstellung nimmt daraus das schlechteste -- siehe
        :attr:`NachweisUrteil.sammel`.
        """
        return [replace(u, sammel=True) for u in urteile]

    def stillstellen(self, alle: Iterable[Any], laut: Iterable[Any]) -> None:
        """
        Festlegen, welche Faelle in der Herleitung stehen und welche nur
        mitrechnen.

        Sind *alle* still, schweigt der Nachweis ganz -- sonst stuende seine
        Ueberschrift samt Ansatz ueber einer Herleitung ohne einen einzigen
        Fall darunter.

        Ein Schluessel in ``laut``, den ``alle`` nicht kennt, ist ein
        Aufbaufehler und wird gemeldet. Stillschweigend uebergangen waere er
        die unangenehmste Art von Fehler: der Nachweis verschwaende aus
        Tabelle und Herleitung, ohne dass irgendwo etwas danebenstuende --
        und gesucht wuerde er dann beim Nachweis und nicht beim Tippfehler.
        """
        alle, laut = set(alle), set(laut)
        fremd = laut - alle
        if fremd:
            raise BerechnungsFehler(
                self.id,
                f"die Fälle "
                f"{', '.join(repr(f) for f in sorted(map(str, fremd)))} "
                f"sollen laut sein, kommen aber nicht vor. Bekannt sind "
                f"{', '.join(repr(f) for f in sorted(map(str, alle)))}.")
        self.stille_faelle = alle - laut
        self.still = not (alle & laut)

    @abstractmethod
    def pruefe(self, e: Eingaben, p: Protokoll) -> Tuple[Mapping[str, Groesse], Sequence[NachweisUrteil]]:
        """
        Fuehrt den Nachweis und liefert Ausgabewerte samt Urteilen.

        :return: (``{Wert-ID: Groesse}``, Liste der Urteile)
        """

    def rechne(self, e: Eingaben, p: Protokoll) -> Mapping[str, Groesse]:
        groessen, urteile = self.pruefe(e, p)
        # Der Namensraum wird hier gestempelt und nicht von den Unterklassen
        # mitgegeben: er ist immer derselbe, naemlich der des Nachweises.
        # Still ist ein Urteil, wenn der ganze Nachweis es ist oder wenn die
        # Pruefung es einzeln so gestempelt hat -- sie kennt ihre Faelle.
        self.urteile = [replace(u, raum=self.id, still=self.still or u.still)
                        for u in urteile]
        return groessen

    # Ein `alle_erfuellt` gab es hier einmal. Es hatte keinen Aufrufer und
    # zaehlte die stillen Urteile mit -- also das Gegenteil von dem, was
    # `Loesung.alle_nachweise_erfuellt` sagt. Zwei gleichnamige Antworten auf
    # dieselbe Frage, von denen die unbenutzte die falsche war.
