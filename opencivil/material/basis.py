"""
opencivil/material/basis.py -- Gemeinsames Geruest fuer Baustoffe.

VERANTWORTUNG:
Ein Baustoff ist im Rechenwerk kein Sonderfall, sondern nur ein Namensraum
voller Werte und Berechnungen. Diese Datei stellt das Geruest bereit, mit dem
Beton und Betonstahl (und spaeter weitere) ihre Werte deklarieren.

WARUM VORLAGEN UND EXEMPLARE GETRENNT SIND:
Im alten Code war die Liste der Betonvariablen eine Liste veraenderlicher
Objekte auf Modulebene, die zugleich als Vorlage und als Rechenobjekt diente.
Zwei Betone im selben Projekt haetten sich gegenseitig ueberschrieben. Hier
sind Vorlagen unveraenderliche Beschreibungen; ``erzeuge()`` giesst daraus fuer
jedes Material ein eigenes Exemplar mit eigenem Namensraum.

ALLES IST UEBERSCHREIBBAR:
Jeder abgeleitete Kennwert ist eine gewoehnliche Berechnung. Wer ihn von Hand
setzen will, ruft ``werk.setze(...)`` -- die Berechnung wird dann uebersprungen,
und im Bericht steht der Wert als 'vom Benutzer überschrieben'.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Mapping, Optional, Sequence, Tuple, Union

from opencivil.core.berechnung import Berechnung, Formel, FormelFunktion, Vorgabe
from opencivil.core.einheiten import EINHEITSLOS, Einheit, Groesse
from opencivil.core.wert import Quelle, WertDef


class Baustoffart(str, Enum):
    BETON = "beton"
    BETONSTAHL = "betonstahl"

    def __str__(self) -> str:
        return self.value

    @property
    def beschriftung(self) -> str:
        return {
            Baustoffart.BETON: "Beton",
            Baustoffart.BETONSTAHL: "Betonstahl",
        }[self]


# ===========================================================================
# Vorlagen
# ===========================================================================


@dataclass(frozen=True)
class KennwertVorlage:
    """
    Beschreibung eines Baustoffkennwerts -- unabhaengig vom konkreten Material.

    Ist ``funktion`` gesetzt, wird der Kennwert gerechnet; sonst ist er eine
    Eingabe, deren Zahlenwert aus der Sortenvorlage kommt.
    """

    kurzname: str
    symbol: str
    einheit: Einheit = EINHEITSLOS
    beschreibung: str = ""
    referenz: str = ""
    stellen: int = 2

    funktion: Optional[FormelFunktion] = None
    vorlage_latex: Optional[str] = None
    eingaben: Tuple[str, ...] = ()
    """Kurznamen der Kennwerte desselben Baustoffs, die eingehen."""

    festwert: Optional[Groesse] = None
    """Normvorgabe, die nicht aus der Sortentabelle kommt (z.B. gamma_c)."""

    begruendung: str = ""

    @property
    def ist_berechnet(self) -> bool:
        return self.funktion is not None

    @property
    def ist_festwert(self) -> bool:
        return self.festwert is not None and self.funktion is None

    def definition(self, praefix: str) -> WertDef:
        return WertDef(
            id=f"{praefix}.{self.kurzname}",
            symbol=self.symbol,
            einheit=self.einheit,
            beschreibung=self.beschreibung,
            referenz=self.referenz,
            stellen=self.stellen,
        )


# ===========================================================================
# Baustoff
# ===========================================================================


@dataclass
class Baustoff:
    """
    Ein konkretes Material im Modell: eigener Namensraum, eigene Berechnungen.

    Beispiel::

        c30 = beton("C30/37")
        werk.registriere(*c30.berechnungen)
        werk.setze(c30.id_von("f_ck"), Groesse(32, MPA))   # abweichender Wert
        loesung = werk.loese(c30.id_von("f_cd"))
    """

    id: str
    """Namensraum, z.B. ``beton.C30_37``."""

    name: str
    """Anzeigename, z.B. ``C30/37``."""

    art: Baustoffart
    sorte: str = ""
    definitionen: Dict[str, WertDef] = field(default_factory=dict)
    berechnungen: List[Berechnung] = field(default_factory=list)
    eingabewerte: Dict[str, Groesse] = field(default_factory=dict)
    """Zahlenwerte aus der Sortenvorlage, nach Kurzname."""

    def id_von(self, kurzname: str) -> str:
        """Globale Wert-ID zu einem Kurznamen, z.B. ``f_cd`` -> ``beton.C30_37.f_cd``."""
        if kurzname not in self.definitionen:
            raise KeyError(
                f"Baustoff '{self.name}' kennt keinen Kennwert '{kurzname}'. "
                f"Bekannt: {sorted(self.definitionen)}."
            )
        return self.definitionen[kurzname].id

    def definition(self, kurzname: str) -> WertDef:
        return self.definitionen[self.kurzname_pruefen(kurzname)]

    def kurzname_pruefen(self, kurzname: str) -> str:
        if kurzname not in self.definitionen:
            raise KeyError(f"Baustoff '{self.name}' kennt keinen Kennwert '{kurzname}'.")
        return kurzname

    @property
    def kennwerte(self) -> Tuple[str, ...]:
        return tuple(self.definitionen)

    def ins_rechenwerk(self, werk) -> "Baustoff":
        """
        Meldet Berechnungen und Sortenwerte beim Rechenwerk an.

        Die Sortenwerte werden als :class:`Vorgabe`-Berechnungen registriert und
        nicht als gesetzte Eingaben -- so bleiben sie normale Knoten im Graphen
        und der Benutzer kann sie mit ``werk.setze(...)`` ueberschreiben.
        """
        werk.definiere(*self.definitionen.values())
        werk.registriere(*self.berechnungen)
        return self

    def __repr__(self) -> str:
        return f"Baustoff({self.name!r}, {len(self.berechnungen)} Berechnungen)"


# ===========================================================================
# Erzeugung
# ===========================================================================


def erzeuge(
    *,
    art: Baustoffart,
    name: str,
    sorte: str,
    vorlagen: Sequence[KennwertVorlage],
    werte: Mapping[str, Groesse],
    praefix: Optional[str] = None,
) -> Baustoff:
    """
    Giesst aus den Vorlagen ein Material mit eigenem Namensraum.

    :param werte: Zahlenwerte der Eingabekennwerte, nach Kurzname
                  (typischerweise aus der Sortentabelle).
    """
    namensraum = praefix or f"{art.value}.{_kennung(sorte or name)}"
    definitionen = {v.kurzname: v.definition(namensraum) for v in vorlagen}
    berechnungen: List[Berechnung] = []
    eingabewerte: Dict[str, Groesse] = {}

    for vorlage in vorlagen:
        ausgabe = definitionen[vorlage.kurzname]
        bid = f"{namensraum}.{vorlage.kurzname}"

        if vorlage.ist_berechnet:
            fehlend = [e for e in vorlage.eingaben if e not in definitionen]
            if fehlend:
                raise ValueError(
                    f"Kennwert '{vorlage.kurzname}' von '{name}' verweist auf "
                    f"unbekannte Kennwerte {fehlend}."
                )
            berechnungen.append(
                Formel(
                    id=bid,
                    ausgabe=ausgabe,
                    eingaben={e: definitionen[e].id for e in vorlage.eingaben},
                    vorlage=vorlage.vorlage_latex,
                    funktion=vorlage.funktion,
                    begruendung=vorlage.begruendung,
                )
            )
            continue

        # Ein ausdruecklich angegebener Wert schlaegt die Normvorgabe -- so
        # lassen sich auch Teilsicherheitsbeiwerte projektweise anpassen.
        groesse = werte.get(vorlage.kurzname, vorlage.festwert)
        if groesse is None:
            raise ValueError(
                f"Fuer '{name}' fehlt der Zahlenwert des Kennwerts "
                f"'{vorlage.kurzname}'."
            )
        eingabewerte[vorlage.kurzname] = groesse
        berechnungen.append(
            Vorgabe(
                id=bid,
                ausgabe=ausgabe,
                groesse=groesse,
                quelle=Quelle.VORGABE,
                begruendung=vorlage.begruendung,
            )
        )

    return Baustoff(
        id=namensraum,
        name=name,
        art=art,
        sorte=sorte,
        definitionen=definitionen,
        berechnungen=berechnungen,
        eingabewerte=eingabewerte,
    )


def _kennung(text: str) -> str:
    """Macht aus 'C30/37' die namensraumtaugliche Kennung 'C30_37'."""
    ersetzt = text.replace("/", "_").replace(" ", "_").replace(".", "_")
    return "".join(z for z in ersetzt if z.isalnum() or z == "_")
