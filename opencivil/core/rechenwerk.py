"""
opencivil/core/rechenwerk.py -- Registrierung und Aufloesung von Berechnungen.

VERANTWORTUNG:
Das Rechenwerk kennt alle Berechnungen und alle vom Benutzer gesetzten Werte.
Es beantwortet die beiden Fragen, um die es in diesem Werkzeug geht:

**Rueckwaerts** -- "Ich will diesen Wert. Was ist dafuer noetig?"
    :meth:`Rechenwerk.loese` verfolgt das Ziel rueckwaerts durch den Graphen,
    fuehrt genau die noetigen Berechnungen aus (und nur die) und meldet jede
    Eingabe, die dafuer fehlt -- samt der Kette, ueber die sie gebraucht wird.

**Vorwaerts** -- "Was laesst sich mit dem, was ich habe, ueberhaupt rechnen?"
    :meth:`Rechenwerk.loese_alles` berechnet alles Erreichbare und listet fuer
    den Rest auf, woran es scheitert.

Ein Ziel ist ein Wert -- oder eine Berechnung unter ihrer ID. Dann laeuft
sie, auch wenn sie keine Ausgabe hat: ein Nachweis ohne Lastfall, ein
Balkensystem. Was sie findet, steht in ihrem Befund.

AUFLOESEN UND RECHNEN GESCHEHEN GEMEINSAM.
Welche Formelvariante gilt, kann von den Zahlenwerten abhaengen (siehe
``Berechnung.anwendbar``). Ein rein struktureller Plan koennte das nicht
entscheiden. Darum wird waehrend des Aufloesens gerechnet: sobald die Eingaben
einer Variante vorliegen, wird geprueft, ob sie anwendbar ist; wenn nicht,
kommt die naechste an die Reihe.

Weil rekursiv in die Tiefe gearbeitet wird, steht im Protokoll jede Groesse vor
der, die sie braucht -- die Reihenfolge des Berichts stimmt also von selbst.

EIGENSTAENDIG NUTZBAR::

    werk = Rechenwerk()
    werk.registriere(*beton_berechnungen("C30_37"))
    loesung = werk.loese("beton.C30_37.f_cd")
    print(loesung.wert("beton.C30_37.f_cd"))
    for f in loesung.fehlende:
        print(f)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Sequence, Set, Tuple, Union

from opencivil.core.berechnung import (
    Berechnung, Eingaben, NachweisUrteil,
)
from opencivil.core.einheiten import Groesse
from opencivil.core.protokoll import Protokoll, StillesProtokoll
from opencivil.core.wert import FehlendeEingabe, Quelle, Wert, WertDef


class RechenwerkFehler(Exception):
    """Aufbau- oder Bedienfehler am Rechenwerk."""


class ZyklusFehler(RechenwerkFehler):
    """Im Abhaengigkeitsgraphen wurde ein Kreis entdeckt."""


# ===========================================================================
# Loesung
# ===========================================================================


@dataclass
class Herkunft:
    """Wie ein Wert zustande kam -- die Kante im Abhaengigkeitsgraphen."""

    wert_id: str
    berechnung_id: str
    eingaben: Tuple[str, ...]


@dataclass
class NichtBerechenbar:
    """Ein Ziel liess sich nicht aufloesen, mit Begruendung."""

    ziel: str
    fehlende: List[FehlendeEingabe] = field(default_factory=list)
    verworfene_varianten: List[Tuple[str, str]] = field(default_factory=list)
    """Paare aus (Berechnungs-ID, Grund der Ablehnung)."""

    def __str__(self) -> str:
        zeilen = [f"'{self.ziel}' ist nicht berechenbar."]
        for f in self.fehlende:
            zeilen.append(f"  - {f}")
        for bid, grund in self.verworfene_varianten:
            zeilen.append(f"  - Variante '{bid}' verworfen: {grund}")
        return "\n".join(zeilen)


def _gesammelt(urteile: Sequence[NachweisUrteil]) -> List[NachweisUrteil]:
    """
    Teilurteile derselben Frage auf das schlechteste zusammenziehen.

    Gesammelt wird je Namensraum, also je Nachweis: die vier Lagen des
    Duktilitaetsnachweises sind vier Antworten auf dieselbe Frage, die drei
    Lastfaelle des M-N-Nachweises sind drei verschiedene Fragen. Welche von
    beidem es ist, sagt das Urteil selbst -- nicht diese Stelle, die von den
    Nachweisen nichts weiss.

    Die Reihenfolge bleibt die des ersten Teilurteils: eine Tabelle, in der
    Zeilen ihren Platz je nach Zahlenwert wechseln, laesst sich nicht
    vergleichen.
    """
    heraus: List[NachweisUrteil] = []
    platz: Dict[str, int] = {}
    for u in urteile:
        if not u.sammel:
            heraus.append(u)
            continue
        if u.raum not in platz:
            platz[u.raum] = len(heraus)
            heraus.append(u)
        elif u.erfuellungsgrad.si < heraus[platz[u.raum]].erfuellungsgrad.si:
            heraus[platz[u.raum]] = u
    return heraus


@dataclass
class Loesung:
    """Ergebnis eines Rechenlaufs."""

    werte: Dict[str, Wert] = field(default_factory=dict)
    protokoll: Protokoll = field(default_factory=Protokoll)
    reihenfolge: List[str] = field(default_factory=list)
    """IDs der ausgefuehrten Berechnungen, in Ausfuehrungsreihenfolge.

    Genau die Liste, die die Oberflaeche aktivieren soll, wenn der Benutzer
    einen Zielwert auswaehlt."""

    graph: Dict[str, Herkunft] = field(default_factory=dict)
    fehlende: List[FehlendeEingabe] = field(default_factory=list)
    nicht_berechenbar: Dict[str, NichtBerechenbar] = field(default_factory=dict)
    urteile: List[NachweisUrteil] = field(default_factory=list)
    befunde: Dict[str, Any] = field(default_factory=dict)
    """
    Je Berechnung, was sie ueber ihre Ausgaben hinaus festgehalten hat --
    Linien, Fallergebnisse, das Ergebnis eines Systems (siehe
    :class:`~opencivil.core.berechnung.Ausfuehrung`). Nach Berechnungs-ID.
    """

    # -- Zusammensetzen ------------------------------------------------------

    def anhaengen(self, teil: "Loesung") -> None:
        """
        Einen weiteren Lauf anhaengen, in dieser Reihenfolge -- so setzt der
        Dienst die Bauteile zusammen, jedes aus seinem eigenen Lauf oder aus
        dem Zwischenspeicher. ``teil`` bleibt dabei, wie es ist.
        """
        self.werte.update(teil.werte)
        self.protokoll.bloecke.extend(teil.protokoll.bloecke)
        self.reihenfolge.extend(r for r in teil.reihenfolge if r not in self.reihenfolge)
        self.graph.update(teil.graph)
        self.fehlende.extend(teil.fehlende)
        self.nicht_berechenbar.update(teil.nicht_berechenbar)
        self.urteile.extend(teil.urteile)
        self.befunde.update(teil.befunde)

    # -- Zugriff ------------------------------------------------------------

    def befund(self, berechnung: Union[str, Berechnung]) -> Any:
        """Der Befund einer Berechnung -- nach ihrer ID oder ihr selbst."""
        bid = berechnung if isinstance(berechnung, str) else berechnung.id
        try:
            return self.befunde[bid]
        except KeyError:
            raise KeyError(f"'{bid}' hat in diesem Lauf keinen Befund hinterlassen -- "
                           f"sie lief nicht, oder sie haelt keinen fest.") from None

    def wert(self, wert_id: str) -> Wert:
        try:
            return self.werte[wert_id]
        except KeyError:
            raise KeyError(
                f"'{wert_id}' wurde nicht berechnet. "
                f"{self.nicht_berechenbar.get(wert_id) or 'Ziel war nicht Teil des Laufs.'}"
            ) from None

    def groesse(self, wert_id: str) -> Groesse:
        return self.wert(wert_id).groesse

    def hat(self, wert_id: str) -> bool:
        return wert_id in self.werte

    @property
    def vollstaendig(self) -> bool:
        return not self.fehlende and not self.nicht_berechenbar

    @property
    def gefuehrte_urteile(self) -> List[NachweisUrteil]:
        """
        Die Urteile, die in eine Tabelle gehoeren.

        Ohne die stillen: ein stiller Nachweis ist ausgeschaltet, er rechnet
        mit, damit ein Hinweis stehen kann, wenn er nicht aufgeht -- gefuehrt
        hat ihn niemand.

        Und je Nachweis, der seine Faelle als Teile derselben Frage stempelt
        (siehe :attr:`NachweisUrteil.sammel`), nur das schlechteste. Vier
        Zeilen fuer eine Frage waren drei zuviel; beantwortet wird sie von
        der schlechtesten Lage.
        """
        return _gesammelt([u for u in self.urteile if not u.still])

    @property
    def stille_maengel(self) -> List[NachweisUrteil]:
        """Ausgeschaltete Nachweise, die nicht aufgehen -- nur als Hinweis."""
        return _gesammelt([u for u in self.urteile if u.meldenswert])

    @property
    def alle_nachweise_erfuellt(self) -> bool:
        """
        Ohne die stillen: sie sind ausgeschaltet und zaehlen nicht mit.

        Sonst staende oben rechts «nicht erfuellt» wegen eines Nachweises,
        den niemand fuehrt -- und man faende in der Tabelle nichts dazu.
        """
        return all(u.erfuellt for u in self.gefuehrte_urteile)

    def kette(self, wert_id: str) -> List[str]:
        """
        Alle Berechnungen, die zu diesem Wert gefuehrt haben, in Reihenfolge.

        Das ist die Rueckverfolgung: welche Rechenschritte waren noetig?
        """
        gesammelt: List[str] = []
        gesehen: Set[str] = set()

        def besuche(wid: str) -> None:
            herkunft = self.graph.get(wid)
            if herkunft is None or herkunft.berechnung_id in gesehen:
                return
            gesehen.add(herkunft.berechnung_id)
            for eingang in herkunft.eingaben:
                besuche(eingang)
            gesammelt.append(herkunft.berechnung_id)

        besuche(wert_id)
        return gesammelt

    def benoetigte_werte(self, wert_id: str) -> List[str]:
        """Alle Werte, die in die Berechnung dieses Wertes eingegangen sind."""
        gesammelt: List[str] = []
        gesehen: Set[str] = set()

        def besuche(wid: str) -> None:
            if wid in gesehen:
                return
            gesehen.add(wid)
            herkunft = self.graph.get(wid)
            if herkunft is not None:
                for eingang in herkunft.eingaben:
                    besuche(eingang)
            gesammelt.append(wid)

        besuche(wert_id)
        return gesammelt

    def __repr__(self) -> str:
        return (
            f"Loesung({len(self.werte)} Werte, {len(self.reihenfolge)} Berechnungen, "
            f"{len(self.fehlende)} fehlende Eingaben)"
        )


# ===========================================================================
# Rechenwerk
# ===========================================================================


class Rechenwerk:
    """
    Sammelt Berechnungen und Eingabewerte und loest Ziele auf.

    Ein Rechenwerk ist bewusst zustandsbehaftet, aber die Rechenlaeufe sind es
    nicht: :meth:`loese` liefert eine frische :class:`Loesung` und laesst das
    Rechenwerk selbst unveraendert (abgesehen vom Zwischenspeicher).
    """

    def __init__(self) -> None:
        self._berechnungen: Dict[str, Berechnung] = {}
        self._nach_ausgabe: Dict[str, List[Berechnung]] = {}
        self._definitionen: Dict[str, WertDef] = {}
        self._vorgegeben: Dict[str, Wert] = {}

    # -- Aufbau -------------------------------------------------------------

    def definiere(self, *definitionen: WertDef) -> "Rechenwerk":
        """Macht Wert-Definitionen bekannt, die keine Berechnung erzeugt."""
        for d in definitionen:
            vorhanden = self._definitionen.get(d.id)
            if vorhanden is not None and vorhanden != d:
                raise RechenwerkFehler(
                    f"Wert '{d.id}' ist bereits mit abweichender Definition bekannt."
                )
            self._definitionen[d.id] = d
        return self

    def kennt_berechnung(self, berechnung_id: str) -> bool:
        return berechnung_id in self._berechnungen

    def registriere(self, *berechnungen: Berechnung) -> "Rechenwerk":
        """
        Nimmt Berechnungen auf.

        Mehrere Berechnungen duerfen denselben Wert liefern -- das sind die
        Varianten, unter denen der Loeser spaeter waehlt. Dieselbe Berechnung
        zweimal anzumelden ist dagegen ein Aufbaufehler und wird gemeldet;
        wer nicht weiss, ob schon angemeldet wurde, fragt vorher mit
        :meth:`kennt_berechnung`.
        """
        for b in berechnungen:
            if b.id in self._berechnungen:
                raise RechenwerkFehler(f"Berechnung '{b.id}' ist bereits registriert.")
            self._berechnungen[b.id] = b
            for ausgabe in b.ausgaben:
                self.definiere(ausgabe)
                self._nach_ausgabe.setdefault(ausgabe.id, []).append(b)
                # Hoehere Prioritaet zuerst, bei Gleichstand Registrierreihenfolge.
                self._nach_ausgabe[ausgabe.id].sort(key=lambda x: -x.prioritaet)
        return self

    def setze(
        self,
        wert_id: str | WertDef,
        groesse: Groesse,
        quelle: Optional[Quelle] = None,
    ) -> "Rechenwerk":
        """
        Setzt einen Wert von Hand.

        Gibt es fuer den Wert eine Berechnung, gilt er als *ueberschrieben* und
        die Berechnung wird uebersprungen -- genau das erlaubt es, berechnete
        Materialkennwerte gezielt durch eigene zu ersetzen. Gibt es keine, ist
        es eine gewoehnliche *Eingabe*.
        """
        if isinstance(wert_id, WertDef):
            self.definiere(wert_id)
            definition = wert_id
        else:
            definition = self._definitionen.get(wert_id)
            if definition is None:
                raise RechenwerkFehler(
                    f"Wert '{wert_id}' ist unbekannt. Bitte zuerst mit definiere(...) "
                    f"bekannt machen oder eine WertDef uebergeben."
                )
        if quelle is None:
            quelle = (
                Quelle.UEBERSCHRIEBEN
                if definition.id in self._nach_ausgabe
                else Quelle.EINGABE
            )
        self._vorgegeben[definition.id] = definition.belegen(groesse, quelle)
        return self

    def loesche(self, wert_id: str) -> "Rechenwerk":
        """Nimmt eine Ueberschreibung zurueck -- der Wert wird wieder gerechnet."""
        self._vorgegeben.pop(wert_id, None)
        return self

    # -- Auskunft -----------------------------------------------------------

    @property
    def berechnungen(self) -> Tuple[Berechnung, ...]:
        return tuple(self._berechnungen.values())

    @property
    def bekannte_werte(self) -> Tuple[str, ...]:
        return tuple(sorted(self._definitionen))

    @property
    def vorgegebene_werte(self) -> Mapping[str, Wert]:
        return dict(self._vorgegeben)

    def definition(self, wert_id: str) -> Optional[WertDef]:
        return self._definitionen.get(wert_id)

    def erzeuger(self, wert_id: str) -> Tuple[Berechnung, ...]:
        """Alle Berechnungen, die diesen Wert liefern koennen (Varianten)."""
        return tuple(self._nach_ausgabe.get(wert_id, ()))

    def moegliche_ziele(self) -> Tuple[str, ...]:
        """
        Alle Werte, die ueberhaupt berechenbar waeren -- und die Berechnungen
        ohne Ausgabe, nach denen sonst kein Wert fragte.
        """
        return (tuple(sorted(self._nach_ausgabe))
                + tuple(sorted(b.id for b in self._berechnungen.values() if not b.ausgaben)))

    # -- Aufloesen ----------------------------------------------------------

    def loese(self, *ziele: str,
              bekannt: Optional[Mapping[str, Wert]] = None,
              ohne_herleitung: bool = False) -> Loesung:
        """
        Berechnet die angegebenen Ziele und alles, was dafuer noetig ist.

        Ein Ziel ist die ID eines Werts oder einer Berechnung. Eine Berechnung
        laeuft dann als Ganzes, einmal -- auch ohne Ausgabe, wie ein Nachweis
        ohne Lastfall. Eine Formel traegt die ID ihres Ergebnisses; dort ist
        der Wert gemeint, was auf dasselbe hinauslaeuft.

        Nicht mehr: Werte, die kein Ziel braucht, werden nicht angefasst.
        Laesst sich ein Ziel nicht aufloesen, bricht der Lauf nicht ab -- das
        Ziel landet in :attr:`Loesung.nicht_berechenbar`, und die fehlenden
        Eingaben werden benannt.

        ``bekannt`` sind Werte, die bereits vorliegen. Sie gelten als
        gerechnet: der Lauf holt sie nicht noch einmal und schreibt sie auch
        nicht noch einmal ins Protokoll. Damit lassen sich mehrere Laeufe
        aneinanderhaengen, ohne dass die Baustoffe in jedem davon erneut
        hergeleitet werden -- und damit laesst sich ein Bauteil auslassen,
        dessen Ergebnis von einem frueheren Lauf noch gilt.

        **Der Aufrufer haftet dafuer, dass die Werte noch gelten.** Das
        Rechenwerk prueft es nicht; es kann es nicht, denn was eine Eingabe
        wert ist, weiss nur, wer sie gesetzt hat.

        ``ohne_herleitung`` rechnet dasselbe, schreibt aber nichts mit --
        fuer Laeufe, die nur Werte und Urteile brauchen.
        """
        lauf = _Lauf(self, bekannt=bekannt, ohne_herleitung=ohne_herleitung)
        for ziel in ziele:
            lauf.ziel(ziel)
        return lauf.abschliessen()

    def loese_alles(self) -> Loesung:
        """
        Berechnet alles, was sich aus den vorhandenen Eingaben ergibt.

        Was nicht geht, wird nicht erzwungen, sondern mit Begruendung in
        :attr:`Loesung.nicht_berechenbar` vermerkt.
        """
        lauf = _Lauf(self)
        for ziel in self.moegliche_ziele():
            lauf.ziel(ziel)
        return lauf.abschliessen()

    def __repr__(self) -> str:
        return (
            f"Rechenwerk({len(self._berechnungen)} Berechnungen, "
            f"{len(self._vorgegeben)} gesetzte Werte)"
        )


# ===========================================================================
# Ein einzelner Rechenlauf
# ===========================================================================


class _Lauf:
    """
    Fuehrt einen Aufloesungsvorgang durch.

    Eigenes Objekt, damit ein Lauf seinen ganzen Zustand (Zwischenspeicher,
    Rekursionsstapel, Protokoll) fuer sich hat und mehrere Laeufe sich nicht in
    die Quere kommen.
    """

    def __init__(self, werk: Rechenwerk,
                 bekannt: Optional[Mapping[str, Wert]] = None,
                 ohne_herleitung: bool = False) -> None:
        self.werk = werk
        self.loesung = (Loesung(protokoll=StillesProtokoll()) if ohne_herleitung
                        else Loesung())
        # Mitgebrachte Werte gelten als gerechnet: aufloesen() findet sie in
        # Schritt 1 und geht darueber hinweg -- ohne Rechnung und ohne
        # Protokollblock. In die Loesung kommen sie nicht; sie haelt fest, was
        # dieser Lauf gerechnet hat, und die mitgebrachten hat der Aufrufer.
        self._bekannt: Dict[str, Wert] = dict(bekannt or {})
        self._stapel: List[str] = []
        self._gescheitert: Dict[str, NichtBerechenbar] = {}
        self._ziele: List[str] = []
        self._laufend: List[str] = []
        """Die Berechnungen, die gerade ihre Eingaben sammeln -- gegen Kreise ueber Befunde."""
        self._abschnitt = ""
        """Welche Ueberschrift zuletzt gesetzt wurde -- siehe ausfuehren()."""

    # -- Kern ---------------------------------------------------------------

    def ziel(self, ziel: str) -> None:
        """Loest ein angefordertes Ziel auf -- Wert oder Berechnung -- und merkt es sich."""
        if ziel not in self._ziele:
            self._ziele.append(ziel)
        if ziel in self.werk._berechnungen and ziel not in self.werk._nach_ausgabe:
            self.rechnen(ziel, pfad=())
        else:
            self.aufloesen(ziel, pfad=())

    def rechnen(self, berechnung_id: str, pfad: Tuple[str, ...]) -> bool:
        """
        Eine Berechnung als Ganzes, einmal je Lauf -- ob sie Ausgaben hat oder
        nicht. ``False``, wenn ihr Eingaben fehlen oder sie nicht anwendbar
        ist; der Grund steht dann unter ihrer ID.

        Brachte der Aufrufer ihre Ausgaben schon mit, lief sie in einem
        frueheren Lauf: dann gilt sie als gerechnet, wie ein mitgebrachter
        Wert.
        """
        berechnung = self.werk._berechnungen[berechnung_id]
        if berechnung_id in self.loesung.reihenfolge:
            return True
        if berechnung.ausgaben and all(a.id in self._bekannt for a in berechnung.ausgaben):
            return True
        if berechnung_id in self._gescheitert:
            return False
        if berechnung_id in self._laufend:
            kreis = " -> ".join(self._laufend[self._laufend.index(berechnung_id):]
                                + [berechnung_id])
            raise ZyklusFehler(f"Kreisbezug im Rechengraphen: {kreis}")

        self._laufend.append(berechnung_id)
        try:
            eingaben, fehlend = self._eingaben_sammeln(berechnung, pfad + (berechnung_id,))
        finally:
            self._laufend.pop()
        if fehlend:
            self._gescheitert[berechnung_id] = NichtBerechenbar(
                ziel=berechnung_id, fehlende=fehlend)
            return False
        anwendbar, grund = berechnung.anwendbar(eingaben)
        if not anwendbar:
            self._gescheitert[berechnung_id] = NichtBerechenbar(
                ziel=berechnung_id,
                verworfene_varianten=[(berechnung_id, grund or "nicht anwendbar")])
            return False
        self._ausfuehren(berechnung, eingaben, grund, echte_wahl=False)
        return True

    def aufloesen(self, ziel: str, pfad: Tuple[str, ...]) -> Optional[Wert]:
        """Liefert den Wert oder None, wenn er nicht beschaffbar ist."""
        # 1. Bereits gerechnet -- oder mitgebracht?
        if (vorhanden := self.loesung.werte.get(ziel)) is not None:
            return vorhanden
        if (mitgebracht := self._bekannt.get(ziel)) is not None:
            return mitgebracht

        # 2. Vom Benutzer gesetzt oder ueberschrieben?
        if (gesetzt := self.werk._vorgegeben.get(ziel)) is not None:
            self.loesung.werte[ziel] = gesetzt
            self.loesung.protokoll.wert(gesetzt)
            return gesetzt

        # 3. Schon einmal gescheitert? Nicht noch einmal versuchen.
        if ziel in self._gescheitert:
            return None

        # 4. Kreis im Graphen?
        if ziel in self._stapel:
            kreis = " -> ".join(self._stapel[self._stapel.index(ziel):] + [ziel])
            raise ZyklusFehler(f"Kreisbezug im Rechengraphen: {kreis}")

        varianten = self.werk._nach_ausgabe.get(ziel, [])
        if not varianten:
            self._als_fehlend_vermerken(ziel, pfad)
            return None

        self._stapel.append(ziel)
        try:
            return self._variante_waehlen(ziel, varianten, pfad)
        finally:
            self._stapel.pop()

    def _variante_waehlen(
        self, ziel: str, varianten: Sequence[Berechnung], pfad: Tuple[str, ...]
    ) -> Optional[Wert]:
        scheitern = NichtBerechenbar(ziel=ziel)

        for berechnung in varianten:
            eingaben, fehlend = self._eingaben_sammeln(berechnung, pfad + (ziel,))
            if fehlend:
                scheitern.fehlende.extend(fehlend)
                scheitern.verworfene_varianten.append(
                    (
                        berechnung.id,
                        "Eingaben fehlen: " + ", ".join(f.id for f in fehlend),
                    )
                )
                continue

            anwendbar, grund = berechnung.anwendbar(eingaben)
            if not anwendbar:
                scheitern.verworfene_varianten.append(
                    (berechnung.id, grund or "nicht anwendbar")
                )
                continue

            self._ausfuehren(berechnung, eingaben, grund, echte_wahl=len(varianten) > 1)
            if (ergebnis := self.loesung.werte.get(ziel)) is not None:
                return ergebnis
            # Sollte nicht vorkommen: ausfuehren() prueft die Ausgaben.
            scheitern.verworfene_varianten.append(
                (berechnung.id, "hat den Zielwert nicht geliefert")
            )

        # Nur vermerken, nicht sofort melden: dieses Ziel kann eine blosse
        # Sondierung auf einem Weg sein, der spaeter verworfen wird, weil eine
        # andere Variante durchkommt. Was davon wirklich fehlt, entscheidet
        # abschliessen() anhand der tatsaechlich angeforderten Ziele.
        self._gescheitert[ziel] = scheitern
        return None

    def _eingaben_sammeln(
        self, berechnung: Berechnung, pfad: Tuple[str, ...]
    ) -> Tuple[Eingaben, List[FehlendeEingabe]]:
        gesammelt: Dict[str, Wert] = {}
        fehlend: List[FehlendeEingabe] = []

        for bezug in berechnung.bezuege:
            wert = self.aufloesen(bezug.wert_id, pfad)
            if wert is not None:
                gesammelt[bezug.name] = wert
            elif not bezug.optional:
                fehlend.append(
                    FehlendeEingabe(
                        id=bezug.wert_id,
                        benoetigt_von=berechnung.id,
                        pfad=pfad,
                        definition=self.werk.definition(bezug.wert_id),
                    )
                )

        befunde: Dict[str, Any] = {}
        for bezug in berechnung.befundbezuege:
            if bezug.berechnung_id not in self.werk._berechnungen:
                raise RechenwerkFehler(
                    f"'{berechnung.id}' liest den Befund von '{bezug.berechnung_id}', "
                    f"die es im Rechenwerk nicht gibt.")
            if not self.rechnen(bezug.berechnung_id, pfad):
                # Woran sie scheitert, findet abschliessen() unter ihrer ID.
                fehlend.append(FehlendeEingabe(
                    id=bezug.berechnung_id, benoetigt_von=berechnung.id, pfad=pfad))
                continue
            if bezug.berechnung_id not in self.loesung.befunde:
                raise RechenwerkFehler(
                    f"'{berechnung.id}' liest den Befund von '{bezug.berechnung_id}', "
                    f"die in diesem Lauf keinen hinterlassen hat -- ihre Ausgaben "
                    f"waren schon bekannt, oder sie haelt keinen fest.")
            befunde[bezug.name] = self.loesung.befunde[bezug.berechnung_id]
        return Eingaben(gesammelt, befunde), fehlend

    def _ausfuehren(
        self,
        berechnung: Berechnung,
        eingaben: Eingaben,
        grund: str,
        echte_wahl: bool,
    ) -> None:
        # Ein stiller Nachweis rechnet mit, schreibt aber in einen Block, den
        # niemand liest. Er ist ausgeschaltet und soll darum nicht in der
        # Herleitung stehen -- sein Ergebnis wird trotzdem gebraucht, denn
        # unter der Zusammenfassung steht ein Hinweis, wenn er nicht aufgeht.
        still = getattr(berechnung, "still", False)
        protokoll = StillesProtokoll() if still else self.loesung.protokoll

        # Ueberschrift setzen, sobald der Abschnitt wechselt. Welche Berechnung
        # eines Bauteils zuerst laeuft, entscheidet die Abhaengigkeitsfolge --
        # deshalb traegt jede ihren Abschnitt selbst, statt dass irgendwo eine
        # Reihenfolge angenommen wird.
        # Eine stumme Berechnung schreibt nichts, also eroeffnet sie auch keinen
        # Abschnitt -- sonst stuende eine Ueberschrift ohne alles darunter.
        abschnitt = berechnung.abschnitt
        if (abschnitt is not None and abschnitt.raum != self._abschnitt
                and not still and not getattr(berechnung, "stumm", False)):
            protokoll.titel(abschnitt.titel, raum=abschnitt.raum)
            self._abschnitt = abschnitt.raum

        anfang = len(protokoll.bloecke)
        ausfuehrung = berechnung.ausfuehren(eingaben, protokoll)
        protokoll.herkunft_stempeln(berechnung.thema, ab=anfang)

        # Erst rechnen, dann begruenden. Andersherum stand der Hinweis vor der
        # eigenen Gleichung und damit unmittelbar unter der vorherigen -- er las
        # sich dann wie deren Begruendung. Genau so ist der Regelwert der
        # Gesteinskoernung unter den Teilsicherheitsbeiwert geraten.
        if grund:
            # Von einer 'gewählten Variante' nur sprechen, wo es wirklich etwas
            # zu waehlen gab -- sonst ist der Zusatz bloss Rauschen.
            protokoll.hinweis(
                f"Gewählte Variante '{berechnung.id}': {grund}" if echte_wahl else grund
            )

        eingang_ids = tuple(w.id for w in eingaben.values())
        for wert_id, wert in ausfuehrung.ausgaben.items():
            self.loesung.werte[wert_id] = wert
            self.loesung.graph[wert_id] = Herkunft(
                wert_id=wert_id,
                berechnung_id=berechnung.id,
                eingaben=eingang_ids,
            )
        self.loesung.reihenfolge.append(berechnung.id)
        self.loesung.urteile.extend(ausfuehrung.urteile)
        if ausfuehrung.befund is not None:
            self.loesung.befunde[berechnung.id] = ausfuehrung.befund

    # -- Abschluss ----------------------------------------------------------

    def _als_fehlend_vermerken(self, ziel: str, pfad: Tuple[str, ...]) -> None:
        """Ein Wert ohne jeden Erzeuger -- eine echte Eingabe, die fehlt."""
        self._gescheitert[ziel] = NichtBerechenbar(
            ziel=ziel,
            fehlende=[
                FehlendeEingabe(
                    id=ziel,
                    benoetigt_von=pfad[-1] if pfad else ziel,
                    pfad=pfad,
                    definition=self.werk.definition(ziel),
                )
            ],
        )

    def _bis_zur_wurzel(
        self, ziel: str, gesehen: Set[str]
    ) -> List[FehlendeEingabe]:
        """
        Faehrt die Fehlschlagkette hinunter bis zu den echten Eingabeluecken.

        Dem Benutzer nuetzt die Meldung "f_cd nicht berechenbar" wenig -- er
        will wissen, dass f_ck und gamma_c fehlen. Darum wird jede fehlende
        Zwischengroesse weiter aufgeloest, bis nur noch Werte uebrig sind, fuer
        die es ueberhaupt keinen Erzeuger gibt.
        """
        if ziel in gesehen:
            return []
        gesehen.add(ziel)
        scheitern = self._gescheitert.get(ziel)
        if scheitern is None:
            return []

        gesammelt: List[FehlendeEingabe] = []
        for fehlend in scheitern.fehlende:
            tiefer = self._bis_zur_wurzel(fehlend.id, gesehen)
            gesammelt.extend(tiefer if tiefer else [fehlend])
        return gesammelt

    def abschliessen(self) -> Loesung:
        gesehen_ziele: Set[str] = set()
        eindeutig: Dict[Tuple[str, str], FehlendeEingabe] = {}

        for ziel in self._ziele:
            # Ein Ziel kann anfangs scheitern und spaeter doch entstehen --
            # als Nebenausgabe einer Berechnung, die fuer ein anderes lief.
            if (ziel in self.loesung.werte or ziel in self._bekannt
                    or ziel in self.loesung.reihenfolge):
                continue
            scheitern = self._gescheitert.get(ziel)
            if scheitern is None:
                continue
            self.loesung.nicht_berechenbar[ziel] = scheitern
            for fehlend in self._bis_zur_wurzel(ziel, gesehen_ziele):
                if fehlend.id in self.loesung.werte or fehlend.id in self._bekannt:
                    continue
                eindeutig.setdefault((fehlend.id, fehlend.benoetigt_von), fehlend)

        self.loesung.fehlende = list(eindeutig.values())
        return self.loesung
