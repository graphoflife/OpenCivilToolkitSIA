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

    lesen.py       was in einer Datei stehen darf und wie es gelesen wird,
                   samt den alten Formaten
    eintraege.py   die Teile: Material, Lagen, Buegel, Lastfaelle
    platte.py      eine Platte mit ihren vier Lagen und allen Schaltern
    projekt.py     das Ganze: Zugriff, Rechnen ohne Oberflaeche, Pruefung,
                   Speichern, das Beispiel
    aufbau.py      aus der Beschreibung ein Rechenwerk

Die Abhaengigkeit laeuft in eine Richtung: lesen <- eintraege <- platte <-
aufbau <- projekt. Wer von aussen kommt, importiert aus dem Paket, nicht aus den
Modulen: ``from opencivil.projekt import Projekt``.

NORMSORTE ODER EIGENES MATERIAL:
Ein Material ist entweder eine unveraenderte Normsorte oder ein eigenes. Nur die
unveraenderte darf die Sortenbezeichnung tragen: steht 'C30/37' auf einem
Bauteil, muessen die Kennwerte auch die der Norm sein. Wer abweichen will, macht
das Material mit :meth:`Projekt.material_loesen` eigenstaendig; es bekommt dann
einen eigenen Namen wie ``C30/37_1``. So kann keine abgeaenderte Festigkeit unter
dem Deckmantel einer Normbezeichnung im Bericht landen.

EINHEITEN IN DER BESCHREIBUNG:
Alle Zahlen stehen in der Anzeige-Einheit des jeweiligen Kennwerts (mm, N/mm^2,
kNm, ...) -- also so, wie der Benutzer sie eintippt. Die Umrechnung in SI
geschieht erst beim Aufbau, ueber die :class:`Groesse`.
"""

from opencivil.projekt.lesen import (
    BEIDE_RICHTUNGEN, RISSANFORDERUNGEN, ProjektFehler, sorten,
)
from opencivil.projekt.eintraege import (
    HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, Beschreibung, GebrauchsfallEintrag,
    Gebrauchsliste, KnickEintrag, KombinationEintrag, LageEintrag,
    MaterialEintrag, PostenEintrag, QuerkraftbewehrungEintrag,
    SpannungsfallEintrag, abgeleiteter_fallname,
)
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.aufbau import Aufbau, aufbauen
from opencivil.projekt.projekt import Projekt

__all__ = [
    "Aufbau", "BEIDE_RICHTUNGEN", "Beschreibung", "GebrauchsfallEintrag",
    "Gebrauchsliste",
    "HAEUFIG_ANTEIL", "KnickEintrag", "KombinationEintrag", "LageEintrag",
    "MaterialEintrag", "PostenEintrag", "Projekt", "ProjektFehler",
    "QUASISTAENDIG_ANTEIL", "QuerkraftbewehrungEintrag", "QuerschnittEintrag",
    "RISSANFORDERUNGEN", "SpannungsfallEintrag", "abgeleiteter_fallname",
    "aufbauen", "sorten",
]
