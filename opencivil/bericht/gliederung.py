"""
opencivil/bericht/gliederung.py -- der ganze Bericht als Bloecke.

VERANTWORTUNG:
Legt fest, was im Bericht steht und in welcher Folge: die Herleitung, die
Formelsammlung, die Nachweise je Platte, die Werte, die fehlenden Eingaben. Als
:class:`Protokoll`, aus denselben Bloecken, aus denen schon die Herleitung
besteht. Konsole und LaTeX-Dokument setzen nur noch dieses eine Protokoll,
jede mit ihrer Tafel.

WARUM:
Vorher baute jede Darstellung ihre Abschnitte selbst, und sie liefen
auseinander: die Konsole listete die Werte nach Kennung, das Dokument nach
Bezeichnung; die Konsole stellte die Werte vor die Nachweise, das Dokument
dahinter; und beide fassten die Nachweise flach zusammen, ohne Platten und
mit anderen Spalten als der Bildschirm. Ein Bericht in einem weiteren Format
haette eine weitere Kopie gebraucht.

EIGENSTAENDIG NUTZBAR::

    from opencivil.bericht.gliederung import bericht
    from opencivil.bericht.konsole import protokoll_zeilen
    print("\\n".join(protokoll_zeilen(bericht(loesung, titel="Decke"))))
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from opencivil.bericht.formelsammlung import anfuegen as formelsammlung_anfuegen
from opencivil.bericht.formelsammlung import formelsammlung
from opencivil.bericht.zusammenfassung import (
    Zusammenfassung, bewehrungsuebersicht, hinweise, nachweistabelle,
    plattenangaben, stiller_hinweis, zusammenfassen,
)
from opencivil.core.latex import Mathe
from opencivil.core.protokoll import Protokoll, TabellenBlock
from opencivil.core.rechenwerk import Loesung

if TYPE_CHECKING:
    from opencivil.projekt import Aufbau


def bericht(
    loesung: Loesung,
    *,
    titel: str = "Berechnung",
    aufbau: Optional["Aufbau"] = None,
) -> Protokoll:
    """
    Der vollstaendige Bericht einer Loesung; ``titel`` wird sein Kopftitel.

    Mit ``aufbau`` stehen die Nachweise je Platte da, samt Angaben und
    Bewehrung -- wie auf dem Bildschirm. Ohne (ein Rechenwerk, das keine
    Platten kennt) in einer Tabelle ohne Plattenueberschrift.
    """
    p = Protokoll(titel)
    p.text(f"{len(loesung.reihenfolge)} Berechnungen ausgeführt, "
           f"{len(loesung.werte)} Werte bestimmt.")
    if not loesung.protokoll.ist_leer:
        _abschnitt(p, "Herleitung")
        p.anfuegen(*loesung.protokoll.nach_abschnitten())
    # Nur, was dieser Lauf rechnet: die ganze Formelsammlung steht in der
    # Oberflaeche, hier die Formeln und Erklaerungen zu diesem Bericht.
    themen = formelsammlung(loesung.protokoll)
    if themen:
        _abschnitt(p, "Verwendete Formeln")
        formelsammlung_anfuegen(p, themen)
    _nachweise(p, zusammenfassen(aufbau, loesung), aufbau)
    _werte(p, loesung)
    _luecken(p, loesung)
    return p


def _abschnitt(p: Protokoll, titel: str) -> None:
    """
    Ein Abschnitt des Berichts, als oberste Ueberschrift.

    Mit eigenem Namensraum: jede Darstellung ordnet die Bloecke nach
    Abschnitten (:meth:`Protokoll.nach_abschnitten`), und ein Titel ohne
    Namensraum gehoerte zum letzten Bauteil der Herleitung -- die Werte
    stuenden dann mitten in dessen Abschnitt, sobald es darin zweimal
    vorkommt.
    """
    p.titel(titel, ebene=1, raum=f"bericht.{titel.lower()}")


def _nachweise(p: Protokoll, zusammenfassung: Zusammenfassung,
               aufbau: Optional["Aufbau"]) -> None:
    """
    Je Platte dasselbe wie auf dem Bildschirm: Angaben, Bewehrung,
    Nachweistabelle, darunter Hinweise und stille Maengel.

    Eines kommt dazu. Auf dem Bildschirm ist ein nicht erfuellter Nachweis
    rot hinterlegt und traegt seine Begruendung im Tooltip -- auf Papier
    gibt es beides nicht. Darum steht jeder unter der Tabelle mit seiner
    Begruendung, sofern ihn nicht schon ein gebuendelter Hinweis erklaert.
    """
    if all(platte.leer for platte in zusammenfassung.platten) \
            and not zusammenfassung.warnungen:
        return
    _abschnitt(p, "Nachweise")
    for platte in zusammenfassung.platten:
        if platte.name:
            p.titel(platte.name)
        if platte.leer:
            p.text("Kein Nachweis geführt.")
            continue
        if aufbau is not None:
            eintrag = aufbau.querschnitte[platte.kennung]
            p.anfuegen(plattenangaben(eintrag), bewehrungsuebersicht(eintrag))
        if platte.zeilen:
            p.anfuegen(nachweistabelle(platte))
        for text in hinweise(platte):
            p.hinweis(text)
        for zeile in platte.zeilen:
            if not zeile.urteil.erfuellt and not zeile.urteil.hinweis:
                p.warnung(f"{zeile.bezeichnung}: nicht erfüllt. "
                          f"{zeile.urteil.begruendung}".rstrip())
        for zeile in platte.stille:
            p.hinweis(stiller_hinweis(zeile))

    if zusammenfassung.gefuehrt:
        p.text("Alle geführten Nachweise sind erfüllt."
               if zusammenfassung.erfuellt
               else "Mindestens ein Nachweis ist nicht erfüllt.")
    for warnung in zusammenfassung.warnungen:
        p.warnung(warnung)


def _werte(p: Protokoll, loesung: Loesung) -> None:
    zeilen = []
    for wert_id in sorted(loesung.werte):
        wert = loesung.werte[wert_id]
        if wert.definition.nur_ziel:
            continue
        einheit = (wert.einheit.beschriftung
                   if wert.einheit.name not in ("", "-") else "")
        zeilen.append([wert.beschreibung or wert_id, Mathe(wert.symbol),
                       Mathe(wert.formatiert(latex=True)), einheit,
                       wert.quelle.beschriftung])
    if not zeilen:
        return
    _abschnitt(p, "Werte")
    p.anfuegen(TabellenBlock(
        kopf=["Bezeichnung", "Symbol", "Wert", "Einheit", "Herkunft"],
        zeilen=zeilen,
        ausrichtung="Llrll",
    ))


def _luecken(p: Protokoll, loesung: Loesung) -> None:
    if loesung.vollstaendig:
        return
    _abschnitt(p, "Fehlende Eingaben")

    if loesung.fehlende:
        p.text("Damit weitergerechnet werden kann, werden gebraucht:")
        for fehlend in loesung.fehlende:
            einheit = ""
            if fehlend.definition is not None:
                e = fehlend.definition.einheit
                einheit = f" [{e.beschriftung}]" if e.name not in ("", "-") else ""
            satz = f"{fehlend.id}{einheit}: {fehlend.beschreibung}"
            if fehlend.pfad:
                satz += f" – benötigt für {' → '.join(fehlend.pfad)}"
            p.text(satz)

    nicht_erreicht = [z for z in loesung.nicht_berechenbar
                      if z not in loesung.werte]
    if nicht_erreicht:
        p.text("Nicht berechenbare Ziele:")
        for ziel in nicht_erreicht:
            varianten = loesung.nicht_berechenbar[ziel].verworfene_varianten
            p.text(ziel + "".join(f" – Variante '{bid}': {grund}"
                                  for bid, grund in varianten))
