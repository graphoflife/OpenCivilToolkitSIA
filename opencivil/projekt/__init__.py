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

    eintraege.py   die Teile: Material, Lagen, Buegel, Lastfaelle -- und
                   die Leser fuer Zahlen, Schalter und alte Dateiformate
    platte.py      eine Platte mit ihren vier Lagen und allen Schaltern
    projekt.py     das Ganze: Zugriff, Rechnen ohne Oberflaeche, Pruefung,
                   Speichern, das Beispiel
    aufbau.py      aus der Beschreibung ein Rechenwerk

Die Abhaengigkeit laeuft in eine Richtung: eintraege <- platte <- aufbau <-
projekt. Wer von aussen kommt, importiert aus dem Paket, nicht aus den
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

from opencivil.projekt.eintraege import (
    BEIDE_RICHTUNGEN, HAEUFIG_ANTEIL, QUASISTAENDIG_ANTEIL, RISSANFORDERUNGEN,
    Beschreibung, GebrauchsfallEintrag, KnickEintrag, KombinationEintrag,
    LageEintrag, MaterialEintrag, PostenEintrag, ProjektFehler,
    QuerkraftbewehrungEintrag, SpannungsfallEintrag, abgeleiteter_fallname,
    sorten,
)
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.aufbau import Aufbau, aufbauen
from opencivil.projekt.projekt import Projekt

__all__ = [
    "Aufbau", "BEIDE_RICHTUNGEN", "Beschreibung", "GebrauchsfallEintrag",
    "HAEUFIG_ANTEIL", "KnickEintrag", "KombinationEintrag", "LageEintrag",
    "MaterialEintrag", "PostenEintrag", "Projekt", "ProjektFehler",
    "QUASISTAENDIG_ANTEIL", "QuerkraftbewehrungEintrag", "QuerschnittEintrag",
    "RISSANFORDERUNGEN", "SpannungsfallEintrag", "abgeleiteter_fallname",
    "aufbauen", "sorten",
]
