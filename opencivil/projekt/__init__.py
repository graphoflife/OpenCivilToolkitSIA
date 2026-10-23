"""
opencivil/projekt -- Serialisierbare Beschreibung eines ganzen Projekts.

VERANTWORTUNG:
Eine Oberflaeche braucht Materialien und Querschnitte als Daten: etwas, das sich
als JSON speichern, im Browser bearbeiten und wieder zu einem :class:`Rechenwerk`
zusammenbauen laesst. Genau das ist ein :class:`Projekt` -- eine reine
Beschreibung ohne Rechenlogik.

AUFTEILUNG:
Frueher eine Datei mit knapp zweitausend Zeilen und drei Aufgaben. Jetzt je
Aufgabe ein Modul::

    lesen.py       was in einer Datei stehen darf, wie es gelesen und wie
                   jedes Feld geprueft wird -- ein Leser fuer alle Eintraege
    eintraege.py   die Teile: Material, Lagen, Buegel, Lastfaelle
    platte.py      eine Platte mit ihren vier Lagen und allen Schaltern
    querschnittsanalyse.py
                   ein gezeichneter Querschnitt: Polygone, Bewehrung,
                   Schubwaende, Lastfaelle
    balkensystem.py
                   ein ebener Rahmen: Knoten, Linien als Staebe und
                   Linienlager, Lager, Lasten, Lastfaelle, Kombinationen
    grundbruch.py  ein Flachfundament: Boden, Masse, Gelaende, Grundwasser
                   und Einwirkungen fuer Grundbruch und Gleiten
    setzung.py     ein Flachfundament auf geschichtetem Baugrund: Pressungen
                   aus Wieder- und Erstbelastung, Schichten mit M_E-Werten
    netz.py        Knoten mit Kennungen, fuer beide Zeichnungen
    skript.py      ein Python-Skript der App «Python»: gespeichert, nicht
                   gerechnet
    projekt.py     das Ganze: Zugriff, Rechnen ohne Oberflaeche, Pruefung,
                   Speichern, das Beispiel
    aufbau/        aus der Beschreibung ein Rechenwerk: der Kern und je
                   Bauteilart ein Modul

Die Abhaengigkeit laeuft in eine Richtung: lesen <- eintraege <- platte <-
aufbau <- projekt. Wer von aussen kommt, importiert aus dem Paket, nicht aus den
Modulen: ``from opencivil.projekt import Projekt``.

NORMSORTE ODER EIGENES MATERIAL:
Ein Material ist entweder eine Normsorte nach SIA oder ein eigenes. Die
Normsorte traegt die Sortenbezeichnung und bleibt, wie sie ist: steht 'C30/37'
auf einem Bauteil, sind die Kennwerte die der Norm. Wer abweichen will, legt
ein eigenes Material an (:meth:`Projekt.eigener_beton`,
:meth:`Projekt.eigener_stahl`), mit einer Sorte als Vorlage; es heisst BE1,
BE2 ... oder S1 ... So kann keine abgeaenderte Festigkeit unter dem
Deckmantel einer Normbezeichnung im Bericht landen.

EINHEITEN IN DER BESCHREIBUNG:
Alle Zahlen stehen in der Anzeige-Einheit des jeweiligen Kennwerts (mm, N/mm^2,
kNm, ...) -- also so, wie der Benutzer sie eintippt. Die Umrechnung in SI
geschieht erst beim Aufbau, ueber die :class:`Groesse`.
"""

from opencivil.projekt.lesen import ProjektFehler, sorten
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Beschreibung, GebrauchsfallEintrag,
    Gebrauchsliste, Gebrauchswahl, KnickEintrag, KnickVerformungswahl, KnickWiderstandswahl,
    KombinationEintrag, LageEintrag, MaterialEintrag, ObergrenzeEintrag, PostenEintrag,
    QuerkraftbewehrungEintrag, RechenwahlEintrag, SpannungsfallEintrag, VerformungEintrag,
    VerformungsfallEintrag, abgeleiteter_fallname,
)
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.balkensystem import (
    BalkensystemEintrag, KnotenlastEintrag, LagerEintrag, LastfallEintrag,
    LastkombinationEintrag, StablastEintrag, StabquerschnittEintrag,
    StatikdiagrammEintrag, SystemknotenEintrag, SystemlinieEintrag,
)
from opencivil.projekt.querschnittsanalyse import (
    FlaecheEintrag, HilfslinieEintrag, KnotenEintrag, QAGebrauchswahl, QALastfallEintrag,
    QuerschnittsanalyseEintrag, SchubwandEintrag, StabEintrag, StablinieEintrag,
    WerkstoffwahlEintrag,
)
from opencivil.projekt.skript import SkriptEintrag
from opencivil.projekt.grundbruch import GrundbruchEintrag, GrundbruchkombinationEintrag
from opencivil.projekt.setzung import SchichtEintrag, SetzungEintrag
from opencivil.projekt.aufbau import BAUTEILE, Aufbau, Bauteil, Bauteilart, aufbauen
from opencivil.projekt.projekt import Projekt

__all__ = [
    "Aufbau", "BAUTEILE", "BalkensystemEintrag", "Bauteil",
    "Bauteilart", "Beschreibung",
    "FlaecheEintrag", "KnotenlastEintrag", "LagerEintrag", "LastfallEintrag",
    "LastkombinationEintrag", "StablastEintrag", "StabquerschnittEintrag",
    "StatikdiagrammEintrag", "SystemknotenEintrag", "SystemlinieEintrag",
    "GebrauchsfallEintrag", "HilfslinieEintrag", "KnotenEintrag",
    "QALastfallEintrag", "QuerschnittsanalyseEintrag",
    "SchubwandEintrag", "StabEintrag", "StablinieEintrag", "WerkstoffwahlEintrag",
    "Gebrauchsliste", "Gebrauchswahl", "KnickVerformungswahl", "KnickWiderstandswahl",
    "QAGebrauchswahl",
    "HAEUFIG_ANTEIL", "KnickEintrag", "KombinationEintrag", "LageEintrag",
    "MaterialEintrag", "ObergrenzeEintrag", "PostenEintrag", "Projekt", "ProjektFehler",
    "QUASISTAENDIG_ANTEIL", "QuerkraftbewehrungEintrag", "QuerschnittEintrag",
    "RechenwahlEintrag", "SkriptEintrag", "SpannungsfallEintrag",
    "VerformungEintrag", "VerformungsfallEintrag", "abgeleiteter_fallname",
    "GrundbruchEintrag", "GrundbruchkombinationEintrag",
    "SchichtEintrag", "SetzungEintrag",
    "aufbauen", "sorten",
]
