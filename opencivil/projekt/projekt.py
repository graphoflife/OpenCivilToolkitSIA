"""
opencivil/projekt/projekt.py -- das Projekt als Ganzes.

VERANTWORTUNG:
Das :class:`Projekt` haelt Materialien und Platten zusammen und ist das, was
gespeichert, geoeffnet und gerechnet wird. Hier stehen der Zugriff auf die
Teile, die Methoden fuer das Rechnen ohne Oberflaeche, die Pruefungen ueber
mehrere Teile hinweg (eindeutige Namen, Anteile), Speichern und Laden -- und
das Beispiel, mit dem die Oberflaeche startet.

Gebaut wird in :mod:`opencivil.projekt.aufbau`; :meth:`Projekt.aufbauen`
reicht nur weiter.
"""

from __future__ import annotations

import difflib
import json
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Union

from opencivil.querschnitt.platte import LAGENZAHL, Richtung
from opencivil.ergebnis import Ergebnis
from opencivil.projekt.eintraege import (
    Beschreibung, MaterialEintrag, PostenEintrag,
)
from opencivil.projekt.gleichungen import GleichungsblattEintrag
from opencivil.projekt.lesen import ProjektFehler
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.aufbau import Aufbau, aufbauen


# ===========================================================================
# Projekt
# ===========================================================================


@dataclass
class Projekt(Beschreibung):
    """Die vollstaendige, speicherbare Beschreibung eines Projekts."""

    name: str = "Neues Projekt"
    materialien: List[MaterialEintrag] = field(default_factory=list)
    querschnitte: List[QuerschnittEintrag] = field(default_factory=list)
    gleichungen: List[GleichungsblattEintrag] = field(default_factory=list)
    """Blätter analytischer Gleichungen -- Zeile für Zeile, wie in Mathcad."""

    # -- Zugriff ------------------------------------------------------------

    def material(self, kennung: str) -> MaterialEintrag:
        for m in self.materialien:
            if m.kennung == kennung:
                return m
        raise ProjektFehler(f"Material '{kennung}' gibt es im Projekt nicht.")

    def querschnitt(self, kennung: str) -> QuerschnittEintrag:
        for q in self.querschnitte:
            if q.kennung == kennung:
                return q
        raise ProjektFehler(f"Querschnitt '{kennung}' gibt es im Projekt nicht.")

    def freie_kennung(self, vorsilbe: str) -> str:
        vergeben = ({m.kennung for m in self.materialien}
                    | {q.kennung for q in self.querschnitte}
                    | {b.kennung for b in self.gleichungen})
        i = 1
        while f"{vorsilbe}{i}" in vergeben:
            i += 1
        return f"{vorsilbe}{i}"

    def freier_name(self, wunsch: str, ausser: str = "") -> str:
        """Haengt bei Bedarf _1, _2, ... an, bis der Name eindeutig ist."""
        vergeben = {m.anzeigename for m in self.materialien if m.kennung != ausser}
        if wunsch not in vergeben:
            return wunsch
        i = 1
        while f"{wunsch}_{i}" in vergeben:
            i += 1
        return f"{wunsch}_{i}"

    def abgeleiteter_name(self, sorte: str, ausser: str = "") -> str:
        """
        Erster freier Name der Form ``<Sorte>_1``, ``<Sorte>_2``, ...

        Nicht ueber :meth:`freier_name` mit dem Wunsch ``C30/37_1``, denn das
        haengte bei Belegung nochmals an und ergaebe ``C30/37_1_1``.
        """
        vergeben = {m.anzeigename for m in self.materialien if m.kennung != ausser}
        i = 1
        while f"{sorte}_{i}" in vergeben:
            i += 1
        return f"{sorte}_{i}"

    def material_loesen(self, kennung: str) -> MaterialEintrag:
        """
        Macht aus einer Normsorte ein eigenstaendiges, aenderbares Material.

        Der Name wird dabei zwingend geaendert -- die Sortenbezeichnung bleibt
        der unveraenderten Norm vorbehalten.
        """
        eintrag = self.material(kennung)
        if eintrag.eigenstaendig:
            return eintrag
        eintrag.eigenstaendig = True
        eintrag.name = self.abgeleiteter_name(eintrag.sorte, ausser=kennung)
        return eintrag

    # -- Ohne Oberflaeche ---------------------------------------------------
    #
    # Die Beschreibung ist das Modell, auch in Python. Diese Methoden legen an,
    # was die Oberflaeche anlegen wuerde, und geben den Eintrag zurueck; was
    # sie nicht abdecken, setzt man am Eintrag selbst. Einen zweiten Satz
    # Klassen daneben gibt es nicht -- er muesste mit diesem gleich bleiben,
    # und genau das tut so etwas nie lange.

    def beton(self, sorte: str = "C30/37") -> MaterialEintrag:
        """Eine Betonsorte nach Norm -- Kennung ``b1``, ``b2`` ..."""
        return self._normsorte("beton", "b", sorte)

    def stahl(self, sorte: str = "B500B") -> MaterialEintrag:
        """Eine Betonstahlsorte nach Norm -- Kennung ``s1``, ``s2`` ..."""
        return self._normsorte("betonstahl", "s", sorte)

    def _normsorte(self, art: str, vorsilbe: str, sorte: str) -> MaterialEintrag:
        """
        Legt eine Normsorte an und prueft sie sofort.

        Sofort und nicht erst beim Rechnen: ein Tippfehler in der Sorte soll
        an der Zeile auffallen, in der er steht.
        """
        eintrag = MaterialEintrag(kennung=self.freie_kennung(vorsilbe), art=art,
                                  sorte=sorte, name=sorte)
        eintrag.pruefen()
        if any(m.anzeigename == sorte for m in self.materialien):
            raise ProjektFehler(
                f"'{sorte}' steht schon im Projekt. Eine Normsorte braucht es "
                f"nur einmal -- mehrere Platten verwenden dieselbe.")
        self.materialien.append(eintrag)
        return eintrag

    def platte(
        self,
        name: str,
        *,
        h: float = 300.0,
        x: Sequence[float] = (12.0, 12.0),
        y: Sequence[float] = (12.0, 12.0),
        x_zulage: Sequence[float] = (0.0, 0.0),
        y_zulage: Sequence[float] = (0.0, 0.0),
        teilung: float = 150.0,
        x_innen: bool = True,
        beton: Union[str, MaterialEintrag, None] = None,
        stahl: Union[str, MaterialEintrag, None] = None,
        **felder: Any,
    ) -> QuerschnittEintrag:
        """
        Eine Platte -- Masse in mm, Bewehrung als Durchmesser je Richtung.

        ``x`` und ``y`` sind je zwei Durchmesser, *unten* und *oben*;
        ``x_zulage`` und ``y_zulage`` ebenso, null heisst keine. Alle Posten
        liegen in derselben ``teilung``. ``x_innen`` legt die Tragrichtung
        auf die 2. und 3. Lage, wie die Vorgabe der Oberflaeche.

        ``beton`` und ``stahl`` duerfen fehlen, solange das Projekt nur je
        einen hat. Alles Weitere -- ``b``, ``rissanforderung``,
        ``duktilitaet`` ... -- geht als Stichwort an den Eintrag; ein
        unbekanntes Stichwort wird gemeldet, statt still zu verschwinden.

        Gebaut wird ueber :meth:`QuerschnittEintrag.neu`, dieselbe Vorlage wie
        in der Oberflaeche, nur ohne deren Startlast: wer rechnet, gibt seine
        Einwirkungen selbst an.
        """
        beton_kennung = self._einziges("beton", beton)
        stahl_kennung = self._einziges("betonstahl", stahl)
        eintrag = QuerschnittEintrag.neu(
            kennung=self.freie_kennung("q"), name=name,
            beton=beton_kennung, stahl=stahl_kennung)
        eintrag.h = float(h)
        eintrag.kombinationen = []
        aussen = Richtung.Y if x_innen else Richtung.X
        eintrag.richtung_lage1 = eintrag.richtung_lage4 = aussen.value

        durchmesser = {Richtung.X: (x, x_zulage), Richtung.Y: (y, y_zulage)}
        for richtung, (grund, zulage) in durchmesser.items():
            r = richtung.value
            for was, werte in ((r, grund), (f"{r}_zulage", zulage)):
                if len(werte) != 2:
                    raise ProjektFehler(
                        f"Platte '{name}': je Richtung zwei Durchmesser, unten "
                        f"und oben -- angegeben sind {len(werte)} ({was}).")
            nummern = [n for n in range(1, LAGENZAHL + 1)
                       if eintrag.richtung_von(n) is richtung]
            for nummer, d, dz in zip(nummern, grund, zulage):
                lage = eintrag.lagen[nummer - 1]
                lage.grund = PostenEintrag(durchmesser=float(d), abstand=teilung)
                lage.zulage = PostenEintrag(durchmesser=float(dz), abstand=teilung)

        bekannt = {f.name for f in fields(QuerschnittEintrag)}
        for feld, wert in felder.items():
            if feld not in bekannt:
                aehnlich = difflib.get_close_matches(feld, bekannt, n=1)
                raise ProjektFehler(
                    f"Platte '{name}': ein Feld '{feld}' gibt es nicht."
                    + (f" Gemeint ist vielleicht '{aehnlich[0]}'?" if aehnlich else ""))
            setattr(eintrag, feld, wert)

        self.querschnitte.append(eintrag)
        return eintrag

    def _einziges(self, art: str,
                  gewaehlt: Union[str, MaterialEintrag, None]) -> str:
        """Die Kennung des gewaehlten Materials -- oder des einzigen dieser Art."""
        if isinstance(gewaehlt, MaterialEintrag):
            return gewaehlt.kennung
        if gewaehlt:
            return self.material(gewaehlt).kennung
        vorhanden = [m for m in self.materialien if m.art == art]
        wort = "Beton" if art == "beton" else "Betonstahl"
        if len(vorhanden) != 1:
            raise ProjektFehler(
                f"Welcher {wort}? Im Projekt stehen {len(vorhanden)} -- bitte "
                f"mit {'beton' if art == 'beton' else 'stahl'}=... angeben"
                + ("." if vorhanden else
                   f", oder zuerst einen anlegen: "
                   f"projekt.{'beton' if art == 'beton' else 'stahl'}(...)."))
        return vorhanden[0].kennung

    def rechnen(self) -> Ergebnis:
        """
        Alles rechnen, was die Oberflaeche auch rechnet -- ohne sie.

        Dieselben Ziele in derselben Reihenfolge (:meth:`Aufbau.alle_ziele`),
        also derselbe Bericht. Ohne Zwischenspeicher: der lohnt sich erst,
        wenn man dieselbe Platte hundertmal rechnet.
        """
        aufbau = self.aufbauen()
        return Ergebnis(projekt=self, aufbau=aufbau,
                        loesung=aufbau.werk.loese(*aufbau.alle_ziele()))

    # -- Pruefung -----------------------------------------------------------

    def pruefen(self) -> None:
        """Prueft die Beschreibung, bevor daraus gerechnet wird."""
        for m in self.materialien:
            m.pruefen()

        gesehen: Dict[str, str] = {}
        for m in self.materialien:
            if m.anzeigename in gesehen:
                raise ProjektFehler(
                    f"Der Name '{m.anzeigename}' ist zweimal vergeben "
                    f"({gesehen[m.anzeigename]} und {m.kennung}). Materialnamen "
                    f"müssen eindeutig sein, sonst lässt sich im Bericht nicht "
                    f"erkennen, welches gemeint ist.")
            gesehen[m.anzeigename] = m.kennung

        for eintrag in self.querschnitte:
            eintrag.pruefen()

    # -- Aufbau -------------------------------------------------------------

    def aufbauen(self, *, schnell: bool = False) -> Aufbau:
        """
        Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

        Die Arbeit steht in :func:`opencivil.projekt.aufbau.aufbauen`, neben
        dem :class:`Aufbau`, der dabei herauskommt.
        """
        return aufbauen(self, schnell=schnell)

    # -- Speichern ----------------------------------------------------------


    @classmethod
    def aus_dict(cls, d: Mapping[str, Any]) -> "Projekt":
        return cls(
            name=str(d.get("name") or "Neues Projekt"),
            materialien=[MaterialEintrag.aus_dict(x) for x in (d.get("materialien") or [])],
            querschnitte=[QuerschnittEintrag.aus_dict(x) for x in (d.get("querschnitte") or [])],
            gleichungen=[GleichungsblattEintrag.aus_dict(x) for x in (d.get("gleichungen") or [])],
        )

    def speichern(self, pfad: str | Path) -> Path:
        ziel = Path(pfad)
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_text(
            json.dumps(self.als_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        return ziel

    @classmethod
    def laden(cls, pfad: str | Path) -> "Projekt":
        return cls.aus_dict(json.loads(Path(pfad).read_text(encoding="utf-8")))

    # -- Startpunkt ---------------------------------------------------------

    @classmethod
    def beispiel(cls) -> "Projekt":
        """
        Ein lauffähiges Beispiel, damit die Oberfläche nicht leer startet.

        Gebaut über dieselben Methoden, die man ohne Oberfläche benutzt. So
        steht die Fassade an einer Stelle vorgeführt -- und der
        Schnappschuss-Test prüft sie mit: baute sie etwas anderes als die
        Einträge von Hand, die hier vorher standen, änderte sich der Bericht.
        """
        projekt = cls(name="OCT Projekt")
        projekt.beton("C30/37")
        projekt.stahl("B500B")
        # Aussen y, innen x -- der übliche Fall: die Querrichtung läuft unten
        # und oben durch, die Tragrichtung liegt dazwischen und verliert
        # dadurch statische Höhe. Die 2. Lage trägt eine Zulage.
        platte = projekt.platte("Decke über EG", h=300,
                                x=[18, 12], x_zulage=[12, 0], y=[12, 12])
        # Die Werte sind so gewählt, dass das Beispiel grün startet.
        platte.einwirkung("Feld", M_Ed=100.0)
        platte.einwirkung("Feld mit Druck", M_Ed=100.0, N_Ed=-300.0)
        platte.einwirkung("Stütze", M_Ed=-50.0)
        return projekt
