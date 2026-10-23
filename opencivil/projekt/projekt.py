"""
opencivil/projekt/projekt.py -- das Projekt als Ganzes.

VERANTWORTUNG:
Das :class:`Projekt` haelt Materialien und Bauteile zusammen und ist das, was
gespeichert, geoeffnet und gerechnet wird. Hier stehen der Zugriff auf die
Teile, die Methoden fuer das Rechnen ohne Oberflaeche, die Pruefungen ueber
mehrere Teile hinweg (eindeutige Kennungen und Materialnamen), Speichern und
Laden -- und das Beispiel, mit dem die Oberflaeche startet.

Gebaut wird in :mod:`opencivil.projekt.aufbau`; :meth:`Projekt.aufbauen`
reicht nur weiter.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence, Union

from opencivil.querschnitt.geometrie import Linienart
from opencivil.querschnitt.platte import LAGENZAHL, Richtung
from opencivil.ergebnis import Ergebnis
from opencivil.querschnitt.gesetzwahl import Rechenart, Werkstoffsatz
from opencivil.projekt.eintraege import (
    EIGENE_VORSILBE, Beschreibung, Gebrauchswahl, KnickVerformungswahl, KnickWiderstandswahl,
    MaterialEintrag, PostenEintrag, RechenwahlEintrag,
)
from opencivil.projekt.balkensystem import BalkensystemEintrag
from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.projekt.lesen import ProjektFehler, felder_pruefen, inhalt_pruefen, lesen, ort
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.skript import VORLAGE, SkriptEintrag
from opencivil.projekt.querschnittsanalyse import (
    QuerschnittsanalyseEintrag, WerkstoffwahlEintrag,
)
from opencivil.projekt.setzung import SetzungEintrag
from opencivil.projekt.aufbau import (
    ANALYSE, BALKENSYSTEM, BAUTEILE, GRUNDBRUCH, PLATTE, SETZUNG, Aufbau, aufbauen,
)


# ===========================================================================
# Projekt
# ===========================================================================

@dataclass
class Projekt(Beschreibung):
    """Die vollstaendige, speicherbare Beschreibung eines Projekts."""

    name: str = "Neues Projekt"
    materialien: List[MaterialEintrag] = field(default_factory=list)
    querschnitte: List[QuerschnittEintrag] = field(default_factory=list)
    querschnittsanalysen: List[QuerschnittsanalyseEintrag] = field(default_factory=list)
    """Gezeichnete Querschnitte: Polygone, Bewehrung, Schubwände."""

    balkensysteme: List[BalkensystemEintrag] = field(default_factory=list)
    """Ebene Rahmen: Knoten, Stäbe, Lager, Lasten, Lastfälle."""

    grundbrueche: List[GrundbruchEintrag] = field(default_factory=list)
    """Flachfundamente mit Grundbruch und Gleiten."""

    setzungen: List[SetzungEintrag] = field(default_factory=list)
    """Flachfundamente auf geschichtetem Baugrund, mit ihrer Setzung."""

    skripte: List[SkriptEintrag] = field(default_factory=list)
    """Die Python-Skripte der App «Python» -- gespeichert, nicht gerechnet."""

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

    def querschnittsanalyse(self, kennung: str) -> QuerschnittsanalyseEintrag:
        for a in self.querschnittsanalysen:
            if a.kennung == kennung:
                return a
        raise ProjektFehler(f"Querschnittsanalyse '{kennung}' gibt es im Projekt nicht.")

    def bauteile(self) -> List[Any]:
        """Alle Bauteile in der Reihenfolge der Beschreibung -- siehe :data:`BAUTEILE`."""
        return [eintrag for art in BAUTEILE for eintrag in getattr(self, art.liste)]

    def nur(self, kennung: str) -> "Projekt":
        """
        Eine Kopie, in der von den Bauteilen nur dieses eine steht --
        die Materialien bleiben. So rechnet die Bewehrungssuche: die
        anderen Bauteile kann sie nicht beeinflussen, und ihre Urteile
        zaehlten sonst mit.
        """
        self.bauteil(kennung)
        kopie = copy.deepcopy(self)
        for art in BAUTEILE:
            setattr(kopie, art.liste,
                    [e for e in getattr(kopie, art.liste) if e.kennung == kennung])
        return kopie

    def bauteil(self, kennung: str) -> Any:
        """Ein Bauteil gleich welcher Art -- eine Platte, eine Analyse, ein System."""
        for eintrag in self.bauteile():
            if eintrag.kennung == kennung:
                return eintrag
        raise ProjektFehler(f"Ein Bauteil '{kennung}' gibt es im Projekt nicht.")

    def freie_kennung(self, vorsilbe: str) -> str:
        vergeben = ({m.kennung for m in self.materialien} | {e.kennung for e in self.bauteile()}
                    | {s.kennung for s in self.skripte})
        i = 1
        while f"{vorsilbe}{i}" in vergeben:
            i += 1
        return f"{vorsilbe}{i}"

    def verweise(self, kennung: str) -> List[Any]:
        """
        Die Bauteile, die auf diese Kennung zeigen -- als Material oder als
        Querschnitt (:meth:`materialien` und :meth:`bezuege` jedes Eintrags).
        Was hier steht, darf nicht geloescht werden; die Oberflaeche fragt hier,
        bevor sie loescht (Dienst ``verweise``), statt es in einer eigenen
        Liste nachzubauen.
        """
        return [e for e in self.bauteile()
                if kennung in e.materialien() or kennung in e.bezuege()]

    def eigener_name(self, art: str) -> str:
        """Der erste freie Name eines eigenen Materials: BE1, BE2 ... oder S1 ..."""
        vergeben = {m.anzeigename for m in self.materialien}
        i = 1
        while f"{EIGENE_VORSILBE[art]}{i}" in vergeben:
            i += 1
        return f"{EIGENE_VORSILBE[art]}{i}"

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

    def eigener_beton(self, vorlage: str = "C30/37") -> MaterialEintrag:
        """
        Ein eigener Beton, ``BE1``, ``BE2`` ... -- mit den Kennwerten der Sorte
        ``vorlage``, abzuaendern ueber ``abweichungen`` und
        ``ueberschreibungen``. Eine Normsorte selbst bleibt, wie sie ist.
        """
        return self._eigenes("beton", "b", vorlage)

    def eigener_stahl(self, vorlage: str = "B500B") -> MaterialEintrag:
        """Ein eigener Betonstahl, ``S1``, ``S2`` ... -- siehe :meth:`eigener_beton`."""
        return self._eigenes("betonstahl", "s", vorlage)

    def _eigenes(self, art: str, vorsilbe: str, vorlage: str) -> MaterialEintrag:
        eintrag = MaterialEintrag(kennung=self.freie_kennung(vorsilbe), art=art,
                                  sorte=vorlage, name=self.eigener_name(art),
                                  eigenstaendig=True)
        eintrag.sorte_pruefen()
        self.materialien.append(eintrag)
        return eintrag

    def _normsorte(self, art: str, vorsilbe: str, sorte: str) -> MaterialEintrag:
        """
        Legt eine Normsorte an und prueft sie sofort.

        Sofort und nicht erst beim Rechnen: ein Tippfehler in der Sorte soll
        an der Zeile auffallen, in der er steht.
        """
        eintrag = MaterialEintrag(kennung=self.freie_kennung(vorsilbe), art=art,
                                  sorte=sorte, name=sorte)
        eintrag.sorte_pruefen()
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
        Gelesen wird es wie aus einer Datei: ein Teil darf als Eintrag kommen
        oder als seine Felder, ``tragsicherheit_wahl={"rechenart": "parabel"}``
        aendert nur die Rechenart.

        Gebaut wird ueber :meth:`QuerschnittEintrag.neu`, dieselbe Vorlage wie
        in der Oberflaeche, nur ohne deren Startlast: wer rechnet, gibt seine
        Einwirkungen selbst an.
        """
        beton_kennung = self._einziges("beton", beton)
        stahl_kennung = self._einziges("betonstahl", stahl)
        eintrag = QuerschnittEintrag.neu(
            kennung=self.freie_kennung(PLATTE.vorsilbe), name=name,
            beton=beton_kennung, stahl=stahl_kennung)
        eintrag.h = float(h)
        eintrag.kombinationen = []
        aussen = Richtung.Y if x_innen else Richtung.X
        eintrag.richtung_lage1 = eintrag.richtung_lage4 = aussen

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

        eintrag = lesen(QuerschnittEintrag, felder, f"Platte '{name}'", eintrag)
        self.querschnitte.append(eintrag)
        return eintrag

    def analyse(
        self,
        name: str,
        *,
        beton: Union[str, MaterialEintrag, None] = None,
        stahl: Union[str, MaterialEintrag, None] = None,
        **felder: Any,
    ) -> QuerschnittsanalyseEintrag:
        """
        Eine Querschnittsanalyse -- ein Rechteck 300 × 600 mm mit drei
        Staeben unten und zwei oben, ohne Lastfall: wer rechnet, gibt seine
        Lastfaelle selbst an. In der Oberflaeche beginnt eine neue Analyse
        seit 2026-10-19 leer; hier bleibt das Rechteck, auf dem Skripte und
        Tests aufbauen.

        Gezeichnet wird danach mit dem Baukasten des Eintrags --
        ``polygon``, ``stab``, ``stablinie``, ``schubwand``, ``hilfslinie``,
        Masse in mm. Wie bei :meth:`platte` geht alles Weitere als Stichwort
        an den Eintrag.
        """
        eintrag = QuerschnittsanalyseEintrag.neu(
            kennung=self.freie_kennung(ANALYSE.vorsilbe), name=name)
        eintrag.vorlage_einsetzen("rechteck", beton=self._einziges("beton", beton),
                                  stahl=self._einziges("betonstahl", stahl), schubwaende=False)
        eintrag = lesen(QuerschnittsanalyseEintrag, felder, f"Querschnittsanalyse '{name}'",
                        eintrag)
        self.querschnittsanalysen.append(eintrag)
        return eintrag

    def balkensystem(self, name: str, **felder: Any) -> BalkensystemEintrag:
        """
        Ein leeres Balkensystem, ein ebener Rahmen. Gezeichnet wird danach
        mit dem Baukasten des Eintrags -- ``querschnitt``, ``linie``,
        ``lager_an``, ``lastfall``, ``stablast``, ``knotenlast``,
        ``kombination`` --, Koordinaten in m. Leer und nicht wie in der
        Oberflaeche mit einem Einfeldtraeger: wer in Python zeichnet, zeichnet
        sein eigenes System.
        """
        eintrag = lesen(BalkensystemEintrag, felder, f"Balkensystem '{name}'",
                        BalkensystemEintrag(kennung=self.freie_kennung(BALKENSYSTEM.vorsilbe),
                                            name=name))
        self.balkensysteme.append(eintrag)
        return eintrag

    def grundbruch(self, name: str, **felder: Any) -> GrundbruchEintrag:
        """
        Ein Grundbruchnachweis mit den Vorgaben der Oberflaeche, aber ohne
        ihre Startkombination: wer rechnet, gibt seine Einwirkungen mit
        ``kombination`` selbst an. Alles Weitere -- ``phi_k``, ``b``, ``t`` ...
        -- geht als Stichwort an den Eintrag; Winkel in Grad, Masse in m,
        Spannungen in kPa.
        """
        eintrag = lesen(GrundbruchEintrag, felder, f"Grundbruch '{name}'",
                        GrundbruchEintrag(kennung=self.freie_kennung(GRUNDBRUCH.vorsilbe),
                                          name=name))
        self.grundbrueche.append(eintrag)
        return eintrag

    def setzung(self, name: str, **felder: Any) -> SetzungEintrag:
        """
        Eine Setzungsberechnung mit den Vorgaben der Oberflaeche, aber ohne
        ihre Startschicht: wer rechnet, gibt seine Schichten mit ``schicht``
        selbst an, von der Sohle an nach unten. Alles Weitere -- ``B``,
        ``q_E``, ``steifigkeit`` ... -- geht als Stichwort an den Eintrag;
        Masse in m, Pressungen in kN/m², die zulaessige Setzung in mm.
        """
        eintrag = lesen(SetzungEintrag, felder, f"Setzung '{name}'",
                        SetzungEintrag(kennung=self.freie_kennung(SETZUNG.vorsilbe),
                                       name=name))
        self.setzungen.append(eintrag)
        return eintrag

    def skript(self, name: str, code: str = "") -> SkriptEintrag:
        """
        Ein Python-Skript für die App «Python» -- Kennung ``p1``, ``p2`` ...
        Ausgeführt wird es in der Konsole der Oberfläche, nicht hier.
        """
        eintrag = SkriptEintrag(kennung=self.freie_kennung("p"), name=name, code=code)
        self.skripte.append(eintrag)
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
        """
        Prueft die Form der Beschreibung -- vor jedem Rechnen und beim Oeffnen
        einer Datei: jedes Feld gegen das, was an ihm steht
        (:func:`~opencivil.projekt.lesen.felder_pruefen`), eine Kennung je
        Eintrag und die Sorte jedes Materials. Was in Python gebaut wurde,
        geht so durch dieselbe Tuer wie eine Datei.

        Den Inhalt -- Bereiche, die Regeln der Bauteile und Materialien, ihre
        Namen -- prueft erst das Rechnen
        (:func:`~opencivil.projekt.lesen.inhalt_pruefen`): ein abgelegtes
        Projekt mit zwei gleich benannten Materialien soll sich oeffnen und
        korrigieren lassen.
        """
        felder_pruefen(self, "Projekt")

        # Eine Kennung je Eintrag, ueber alle Arten -- an ihr haengen die
        # Werte im Rechenwerk und die Verweise. Zwei gleiche hiessen: der
        # spaetere ersetzt still den frueheren, und eine Platte rechnete mit
        # dem falschen Beton.
        vergeben: Dict[str, str] = {}
        for eintrag in [*self.materialien, *self.bauteile(), *self.skripte]:
            wer = ort(type(eintrag), {"name": getattr(eintrag, "anzeigename", eintrag.name),
                                      "kennung": eintrag.kennung})
            if eintrag.kennung in vergeben:
                raise ProjektFehler(
                    f"{vergeben[eintrag.kennung]} und {wer} haben dieselbe Kennung "
                    f"'{eintrag.kennung}'. Jeder Eintrag braucht seine eigene.")
            vergeben[eintrag.kennung] = wer

        for m in self.materialien:
            m.sorte_pruefen()

    def regeln(self, wo: str) -> None:
        """Die Namen der Materialien, vor dem Rechnen -- je Material einer."""
        gesehen: Dict[str, str] = {}
        for m in self.materialien:
            if m.anzeigename in gesehen:
                raise ProjektFehler(
                    f"Der Name '{m.anzeigename}' ist zweimal vergeben "
                    f"({gesehen[m.anzeigename]} und {m.kennung}). Materialnamen "
                    f"müssen eindeutig sein, sonst lässt sich im Bericht nicht "
                    f"erkennen, welches gemeint ist.")
            gesehen[m.anzeigename] = m.kennung

    def inhalt_pruefen(self) -> None:
        """
        Prueft den Inhalt, vor jedem Rechnen und vor jeder Suche: Bereiche
        und Regeln jedes Eintrags (:func:`~opencivil.projekt.lesen.inhalt_pruefen`).
        Die Form prueft :meth:`pruefen`.
        """
        inhalt_pruefen(self, "Projekt")

    # -- Aufbau -------------------------------------------------------------

    def aufbauen(self, *, schnell: bool = False) -> Aufbau:
        """
        Baut aus der Beschreibung ein vollstaendiges Rechenwerk.

        Die Arbeit steht in :func:`opencivil.projekt.aufbau.aufbauen`, neben
        dem :class:`Aufbau`, der dabei herauskommt.
        """
        return aufbauen(self, schnell=schnell)

    # -- Speichern ----------------------------------------------------------

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
        # Die Durchbiegung im Feld, mit E_cm gerechnet -- der
        # Vergrösserungsfaktor macht sie gut viermal grösser.
        platte.verformungsfall("Feld", w=3.5, laenge=6.0)
        # Ein gezeichneter Querschnitt: der Unterzug, 300 × 600 mm. Vier
        # Schubwände auf der Bügelachse umschliessen eine Zelle -- so trägt
        # er auch Torsion; jede Wand kreuzt ein Schenkel des Bügels.
        unterzug = projekt.analyse("Unterzug")
        stahl = unterzug.stablinien[0].stahl
        for von, bis in (([50.0, 50.0], [250.0, 50.0]), ([250.0, 50.0], [250.0, 550.0]),
                         ([250.0, 550.0], [50.0, 550.0]), ([50.0, 550.0], [50.0, 50.0])):
            unterzug.schubwand(von, bis, dicke=100.0, durchmesser=10.0, teilung=150.0,
                               schnitte=1, stahl=stahl)
        unterzug.lastfall("Feld", M_y_Ed=150.0, V_z_Ed=150.0, T_Ed=15.0)
        # Ein Rahmen: zwei Stützen von 4 m und ein Riegel von 6 m mit dem
        # Querschnitt des Unterzugs. Links eingespannt, rechts eine
        # Pendelstütze; Eigengewicht auf dem Riegel, Wind auf der linken
        # Stütze, und beides kombiniert.
        rahmen = projekt.balkensystem("Rahmen")
        stuetze = rahmen.querschnitt("Stütze 300×300", "rechteck", b=300.0, h=300.0)
        riegel = rahmen.querschnitt_aus("Unterzug", "analyse", unterzug)
        links = rahmen.linie((0, 0), (0, 4), querschnitt=stuetze, material="b1")
        balken = rahmen.linie((0, 4), (6, 4), querschnitt=riegel, material="b1")
        rahmen.linie((6, 4), (6, 0), querschnitt=stuetze, material="b1", gelenk_anfang=True)
        rahmen.lager_an((0, 0), "eingespannt")
        rahmen.lager_an((6, 0), "gelenkig")
        eigengewicht = rahmen.lastfall("Eigengewicht")
        wind = rahmen.lastfall("Wind")
        rahmen.stablast(eigengewicht, balken, wert=25.0)
        rahmen.stablast(wind, links, wert=3.0, richtung="waagrecht")
        rahmen.kombination("Tragsicherheit", (eigengewicht, 1.35), (wind, 1.5))
        # Ein Einzelfundament 2.0 × 2.5 m, 1.2 m tief, das Grundwasser tiefer
        # als der Gleitkörper -- grün, wie der Rest.
        fundament = projekt.grundbruch("Fundament Stütze", phi_k=32.0, b=2.0, L=2.5,
                                       t=1.2, t1=5.0)
        fundament.kombination("Tragsicherheit", N_Ed=1500.0, T_Ed=150.0)
        # Und seine Setzung: bis zur Sohle 1.2 m Aushub, das ist die
        # Wiederbelastung; der Rest der Pressung belastet den Boden zum
        # ersten Mal. Unter dem Kies ein weicher Silt, darunter Moräne.
        setzung = projekt.setzung("Fundament Stütze", B=2.0, L=2.5, q_W=24.0, q_E=196.0,
                                  s_zul=25.0)
        setzung.schicht("Kies, sandig", d=2.0, M_E=60.0, M_E_strich=180.0)
        setzung.schicht("Silt, tonig", d=3.0, M_E=15.0, M_E_strich=45.0)
        setzung.schicht("Moräne", d=4.0, M_E=100.0, M_E_strich=250.0)

        # Ein Skript für die App «Python», mit einem Diagramm -- ohne Download.
        projekt.skript("Skript 1", VORLAGE)
        return projekt

    @classmethod
    def jeder_nachweis(cls) -> "Projekt":
        """
        Jeder Nachweis einmal laut -- und die Fälle, die das Beispiel nie zeigt.

        Zusammen mit :meth:`beispiel` führt es jeden Nachweis einmal laut; ein
        Test wacht darüber. Aus den beiden stammen der Schnappschuss des
        Berichts und die Formelsammlung der Oberfläche -- darum steht es hier
        und nicht bei den Tests.

        Erhöhte Anforderung mit allen Schaltern und begrenzter rissaktiver
        Dicke, häufige und quasi-ständige Lastfälle abgeleitet und eigene, Bügel
        mit Stabzahl in y, ein Knickfall, die Verformung im Feld und am
        Kragarm; eine zweite Platte mit x aussen und b = 500 mm, die im Feld
        nicht aufgeht, auch nicht in der Durchbiegung, und deren Stahl unter
        Dauerlast fliesst, dazu Querkraft ohne Bügel -- einmal über m_Rd,
        einmal darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
        Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
        gemessen wird, und ⌀40 in y unter der x-Bewehrung -- die fliesst bei
        x = h/2 nicht. Gebaut über die Fassade, wie ein Benutzer es in Python
        täte.
        """
        p = cls(name="Jeder Nachweis einmal")
        p.beton("C30/37")
        p.stahl("B500B")
        decke = p.platte("Decke", h=300, x=[18, 12], x_zulage=[12, 0], y=[12, 12],
                         rissanforderung="erhoeht", duktilitaet=True, sproede=True,
                         zwaengung=True, zwaengung_begrenzt=True,
                         zwaengung_biegung=True)
        decke.querkraftbewehrung.durchmesser = 8.0
        decke.querkraftbewehrung.art_y = Linienart.ANZAHL
        decke.querkraftbewehrung.anzahl_y = 5.0
        decke.einwirkung("Feld", M_Ed=150, V_Ed=80)
        decke.einwirkung("Feld mit Druck", M_Ed=120, N_Ed=-300)
        decke.einwirkung("Stütze", M_Ed=-60, V_Ed=60)
        decke.haeufig.aus_tragsicherheit = True
        decke.haeufig.lastfall("Gebrauch", M_Ed=90)
        decke.quasistaendig.aus_tragsicherheit = True
        decke.quasistaendig.lastfall("Dauerlast", M_Ed=70)
        decke.knickfall("Wand", N_Ed=-800, M_Ed_1=20, laenge=3.0)
        # Die Verformung im Feld und am Kragarm -- einmal je gezogene Seite.
        decke.verformungsfall("Feld", w=3.0, laenge=6.0)
        decke.verformungsfall("Kragarm", w=0.8, laenge=2.5, zugseite="oben")
        # Die Kapitel der Decke rechnen mit φ = 2, wie bis 2026-10-09 die
        # Platte -- so bleiben ihre Zahlen im Bericht dieselben.
        decke.zwaengung_biegung_kriechzahl = 2.0
        decke.haeufig.wahl.kriechzahl = decke.quasistaendig.wahl.kriechzahl = 2.0
        decke.knicken_wahl_verformung.kriechzahl = 2.0
        # Zwei Linien der Spannung-Dehnung-Analyse -- sie schreiben ihre
        # Herleitung für die Formelsammlung: präzise, und mit der
        # 0.85·x-Vereinfachung und charakteristischen Werten. Eine
        # Handrechnung gibt es dort nicht mehr (2026-10-12).
        decke.spannungsfall("Biegung mit Druck", art="moment_kruemmung", N_Ed=-300,
                            kriechzahl=2.0)
        decke.spannungsfall("Zug mit Moment", art="normalkraft_dehnung", M_Ed=30,
                            kriechzahl=1.0, werkstoffsatz="charakteristisch",
                            rechenart="block")
        # Der äquivalente E-Modul, einmal über dem Moment und einmal über der
        # Normalkraft bei festem Moment -- dort zählt er ab dem Zustand ohne N.
        decke.spannungsfall("Biegesteifigkeit", art="moment_emodul",
                            werkstoffsatz="charakteristisch")
        decke.spannungsfall("Dehnsteifigkeit", art="normalkraft_emodul", M_Ed=30,
                            werkstoffsatz="charakteristisch")

        # Ein Streifen von 500 mm: M und N je b, V je Meter. Mit halben
        # Momenten sind es dieselben Grade wie bei 1000 mm -- nur die
        # Lagentabelle zeigt, dass x je b und y je Laufmeter gilt.
        dach = p.platte("Dach", h=200, x=[10, 10], y=[8, 8], x_innen=False,
                        einlagenhoehe=40, b=500)
        dach.einwirkung("Feld", M_Ed=40, V_Ed=40)
        dach.einwirkung("Rand", M_Ed=10, V_Ed=30)
        dach.quasistaendig.lastfall("Dauerlast", M_Ed=20)
        # Mit φ = 2 fliesst hier der Stahl -- der Fall soll laut bleiben.
        dach.quasistaendig.wahl.kriechzahl = 2.0
        # Die Durchbiegung geht nicht auf, mit einem eigenen φ.
        dach.verformung.kriechzahl = 1.5
        dach.verformungsfall("Feld", w=2.0, laenge=5.0)

        # Jede Rechenwahl einmal laut. Die Platte «Parabel» haelt die
        # Tragsicherheit praezise mit charakteristischen Werten -- M_Rk,
        # m_Rk in der Querkraft, sproedes Versagen --, rechnet die
        # Stahlspannungen mit 0.85·x und praezise und knickt mit eigener
        # Linie: Verformung mit charakteristischen Werten, Widerstand praezise
        # mit Bemessungswerten. Die «Decke» knickt mit der Vorgabe 0.85·x
        # gegen ihre Handrechnung, also ebenfalls mit eigener Linie.
        genau = p.platte("Parabel", h=250, x=[12, 10], y=[10, 10],
                         rissanforderung="erhoeht", sproede=True)
        genau.tragsicherheit_wahl = RechenwahlEintrag(
            kriechzahl=1.0, werkstoffsatz=Werkstoffsatz.CHARAKTERISTISCH,
            rechenart=Rechenart.PARABEL)
        genau.einwirkung("Feld", M_Ed=60, N_Ed=-200, V_Ed=50)
        genau.quasistaendig.lastfall("Dauerlast", M_Ed=30)
        genau.quasistaendig.wahl = Gebrauchswahl(kriechzahl=1.0, rechenart=Rechenart.BLOCK)
        genau.haeufig.lastfall("Gebrauch", M_Ed=45)
        genau.haeufig.wahl = Gebrauchswahl(kriechzahl=2.0, rechenart=Rechenart.PARABEL)
        genau.knickfall("Stütze", N_Ed=-600, M_Ed_1=10, laenge=3.0)
        genau.knicken_wahl_verformung = KnickVerformungswahl(
            werkstoffsatz=Werkstoffsatz.CHARAKTERISTISCH)
        genau.knicken_wahl_widerstand = KnickWiderstandswahl(rechenart=Rechenart.PARABEL)

        # Die Platte «Block» haelt die Tragsicherheit mit der 0.85·x-Vereinfachung,
        # einmal bei festem Moment -- dort zeigt die Probe die Normalkraft --,
        # rechnet die Stahlspannung von Hand und knickt gegen dieselbe Linie.
        block = p.platte("Block", h=220, x=[10, 10], y=[8, 8])
        block.tragsicherheit_wahl = RechenwahlEintrag(rechenart=Rechenart.BLOCK)
        block.einwirkung("Feld", M_Ed=25, V_Ed=30)
        block.einwirkung("Rand", M_Ed=-15, N_Ed=-100).art = "M_konstant"
        block.quasistaendig.lastfall("Dauerlast", M_Ed=12)
        block.quasistaendig.wahl = Gebrauchswahl(rechenart=Rechenart.HANDRECHNUNG)
        block.knickfall("Wand", N_Ed=-400, M_Ed_1=5, laenge=2.5)
        block.knicken_wahl_widerstand = KnickWiderstandswahl()

        ohne = p.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
        ohne.einwirkung("Feld", M_Ed=30, V_Ed=20)
        ohne.verformungsfall("Feld", w=2.0, laenge=4.0)

        konsole = p.platte("Konsole", h=250, x=[12, 12], y=[40, 10])
        konsole.einwirkung("Feld", M_Ed=40, V_Ed=50)
        konsole.einwirkung("Schräg", M_Ed=30, N_Ed=-500).art = "naechster_Punkt"

        # Zwei gezeichnete Querschnitte. Ein Kastenträger mit Aussparung,
        # Bewehrung in allen drei Arten, vier Schubwänden als Zelle, Torsion,
        # schiefer Biegung und Längszugkraft, gerechnet mit dem
        # Spannungsblock, dazu jeder Gebrauchsnachweis bei erhöhter
        # Anforderung; eine Stütze, einachsig, mit charakteristischen Werten,
        # normaler Anforderung und Knicken -- so steht jede Wahl einmal da.
        p.querschnittsanalysen.append(cls._kastentraeger(p.freie_kennung("a")))
        p.querschnittsanalysen.append(cls._stuetze(p.freie_kennung("a")))

        # Zwei Balkensysteme: eines, das alles einmal braucht, und eines, das
        # sich nicht rechnen lässt. Dazu jede Spielart des Grundbruchs.
        cls._alles_einmal(p, decke, p.querschnittsanalysen[0])
        cls._beweglich(p)
        cls._grundbrueche(p)
        cls._setzungen(p)
        return p

    @staticmethod
    def _grundbrueche(p: "Projekt") -> None:
        """
        Jede Lage des Grundwassers und beide Arten des Bodens: drainiert mit
        Kohäsion, geneigter Sohle, geneigtem Gelände, Auflast und dem
        Wasser im Gleitkörper, dazu eine Last, so schräg, dass die Klammer
        eines Lastneigungsfaktors unter null fällt; das Wasser über der Sohle
        und auf ihrer Höhe, dort ein langer Streifen; undrainiert flach und
        tief eingebunden, einmal so schräg belastet, dass es keinen
        Widerstand gibt.
        """
        hang = p.grundbruch("Hang", phi_k=33.0, c_k=6.0, b=1.6, L=4.0, t=0.8, t1=2.0,
                            alpha=5.0, beta=15.0, q_Ed=10.0, delta_faktor=0.67)
        hang.kombination("Normal", N_Ed=900.0, T_Ed=120.0)
        hang.kombination("Steil", N_Ed=150.0, T_Ed=300.0)
        p.grundbruch("Ufer", phi_k=30.0, b=1.5, L=1.5, t=1.0, t1=0.4).kombination(
            "Tragsicherheit", N_Ed=1200.0, T_Ed=100.0)
        p.grundbruch("Kai", phi_k=28.0, c_k=3.0, b=2.0, L=20.0, t=1.5, t1=1.5).kombination(
            "Tragsicherheit", N_Ed=2000.0, T_Ed=80.0)
        seeton = p.grundbruch("Seeton", phi_k=0.0, c_k=40.0, b=1.5, L=2.0, t=0.8,
                              alpha=4.0, beta=10.0)
        seeton.kombination("Normal", N_Ed=300.0, T_Ed=40.0)
        seeton.kombination("Zu schräg", N_Ed=300.0, T_Ed=200.0)
        p.grundbruch("Schacht", phi_k=0.0, c_k=60.0, b=1.2, L=1.2, t=2.0).kombination(
            "Tragsicherheit", N_Ed=900.0, T_Ed=30.0)

    @staticmethod
    def _setzungen(p: "Projekt") -> None:
        """
        Das Beispiel der Tabelle 8.4 des Kapitels -- ein Bauwerk 15 × 8 m, starr,
        auf Kiessand über Ton; der Kiessand setzt sich dort nicht, hier fast
        nicht --, das mit 20 mm nicht aufgeht; dazu ein schlaffer Damm mit
        Wiederbelastung, und eine Berechnung ohne Schicht.
        """
        bauwerk = p.setzung("Bauwerk", B=8.0, L=15.0, q_E=60.0, s_zul=20.0, dz=1.0)
        bauwerk.schicht("Kiessand", d=5.0, M_E=1000.0, M_E_strich=3000.0)
        bauwerk.schicht("Ton", d=4.0, M_E=4.0, M_E_strich=24.0)
        damm = p.setzung("Damm", B=6.0, L=40.0, steifigkeit="schlaff", q_W=20.0, q_E=80.0,
                         s_zul=120.0)
        damm.schicht("Auffüllung", d=1.5, M_E=8.0, M_E_strich=30.0)
        damm.schicht("Seeton", d=6.0, M_E=5.0, M_E_strich=25.0)
        damm.schicht("Ton", d=4.0, M_E=7.0, M_E_strich=35.0)
        p.setzung("Ohne Schicht")

    @staticmethod
    def _alles_einmal(p: "Projekt", decke: QuerschnittEintrag,
                      analyse: QuerschnittsanalyseEintrag) -> None:
        """
        Jede Vorlage, Kennwerte von Hand, Platte und Analyse als
        Querschnitt; Beton und Stahl; Gelenke und ein Knoten, dessen Drehung
        keine Steifigkeit hat; Federn am Lager, Bettung, feste Linienlager
        mit und ohne Stab; jede Lastart, auch projiziert.
        """
        s = p.balkensystem("Alles einmal")
        q = {
            "rechteck": s.querschnitt("Balken 300×500", "rechteck", b=300.0, h=500.0),
            "kreis": s.querschnitt("Rundstütze", "kreis", d=400.0),
            "kreisring": s.querschnitt("Rohr", "kreisring", D=168.3, t=10.0),
            "rechteckrohr": s.querschnitt("Hohlprofil", "rechteckrohr", b=200.0, h=300.0, t=12.5),
            "t": s.querschnitt("Plattenbalken", "t", b=1200.0, h=600.0, b_w=300.0, h_f=200.0),
            "doppel_t": s.querschnitt("Walzprofil", "doppel_t", b=300.0, h=300.0,
                                      t_f=19.0, t_w=11.0),
            "trapez": s.querschnitt("Fundamentbalken", "trapez", b_o=600.0, b_u=400.0, h=500.0),
        }
        s.querschnitt_mit_kennwerten("Von Hand", A=15000.0, I=120.0)
        s.querschnitt_aus("Deckenstreifen", "platte", decke)
        s.querschnitt_aus("Kasten", "analyse", analyse)
        gebettet = s.linie((0, 0), (8, 0), querschnitt=q["rechteck"], material="b1",
                           quer="feder", k_quer=20000.0)
        stuetze = s.linie((8, 0), (8, 3), querschnitt=q["kreis"], material="b1")
        sparren = s.linie((8, 3), (12, 5), querschnitt=q["t"], material="b1")
        s.linie((12, 5), (12, 0), querschnitt=q["kreisring"], material="s1",
                gelenk_anfang=True, gelenk_ende=True)
        stahl = s.linie((12, 0), (15, 0), querschnitt=q["doppel_t"], material="s1",
                        gelenk_anfang=True)
        aufgelegt = s.linie((15, 0), (17, 0), querschnitt=q["trapez"], material="b1",
                            quer="fest")
        s.linie((17, 0), (17, -1), stab=False, quer="fest")
        s.linie((15, 0), (15, 2), querschnitt=q["rechteckrohr"], material="s1")
        s.lager_an((0, 0), "gelenkig", z="feder", k_z=50000.0, phi="feder", k_phi=10000.0)
        s.lager_an((12, 0), "gelenkig")
        g = s.lastfall("Eigengewicht")
        w = s.lastfall("Schnee und Wind")
        s.stablast(g, gebettet, wert=5.0, wert_b=15.0)
        s.stablast(g, gebettet, art="linienmoment", wert=2.0, von=2.0, bis=6.0)
        s.stablast(g, sparren, wert=4.0)
        s.stablast(g, aufgelegt, wert=10.0)
        s.knotenlast(g, (8, 3), 5.0, art="moment")
        s.stablast(w, sparren, wert=3.0, projiziert=True)
        s.stablast(w, stuetze, art="einzellast", wert=8.0, von=1.5, richtung="quer")
        s.stablast(w, stahl, art="moment", wert=4.0, von=1.5)
        s.knotenlast(w, (8, 3), 10.0, richtung="waagrecht")
        s.kombination("Tragsicherheit", (g, 1.35), (w, 1.5))

    @staticmethod
    def _beweglich(p: "Projekt") -> None:
        """Ein Träger auf zwei Rollen: nichts hält ihn waagrecht -- eine Meldung statt einer Zahl."""
        s = p.balkensystem("Beweglich")
        traeger = s.linie((0, 0), (5, 0), querschnitt=s.querschnitt("Rechteck", "rechteck"),
                          material="b1")
        s.lager_an((0, 0), "verschieblich")
        s.lager_an((5, 0), "verschieblich")
        s.stablast(s.lastfall("Last"), traeger, wert=10.0)

    @staticmethod
    def _kastentraeger(kennung: str) -> QuerschnittsanalyseEintrag:
        a = QuerschnittsanalyseEintrag(
            kennung=kennung, name="Kastenträger",
            werkstoffwahl=[WerkstoffwahlEintrag(material="b1", betongesetz="block")],
            laengszugkraft=True, duktilitaet=True, sproede=True,
            rissanforderung="erhoeht", zwaengung=True, zwaengung_begrenzt=True,
            zwaengung_biegung=True, zwaengung_biegung_kriechzahl=1.0)
        a.polygon([[0, 0], [800, 0], [800, 600], [0, 600]], material="b1")
        a.polygon([[150, 150], [650, 150], [650, 450], [150, 450]])
        a.stablinie([50, 50], [750, 50], art="teilung", durchmesser=16, teilung=150,
                    stahl="s1")
        a.stablinie([60, 550], [740, 550], art="anzahl", durchmesser=12, anzahl=4,
                    starteisen=False, endeisen=False, stahl="s1")
        a.stablinie([40, 150], [40, 450], art="flaeche", flaeche=400, stahl="s1")
        a.stab(760, 300, durchmesser=20, stahl="s1")
        for e, f in (([75, 75], [725, 75]), ([725, 75], [725, 525]),
                     ([725, 525], [75, 525]), ([75, 525], [75, 75])):
            a.schubwand(e, f, dicke=150, durchmesser=10, teilung=150, schnitte=1, stahl="s1")
        a.lastfall("Feld", M_y_Ed=300.0, V_z_Ed=250.0, T_Ed=60.0)
        a.lastfall("Schief", N_Ed=-1500.0, M_y_Ed=250.0, M_z_Ed=150.0, V_y_Ed=100.0)
        # Spannung-Dehnung-Analysen, je Zugseite: ein Bild und eine Linie mit
        # ihrer Herleitung -- um z unter Druck, und der Modul unter Zug bei
        # negativem Moment, wo der gedrückte Rand reisst.
        a.spannungsfall("Schnitt", art="schnittgroessen", N_Ed=-500.0, M_Ed=200.0)
        a.spannungsfall("Seitlich", art="moment_kruemmung", N_Ed=-500.0, richtung="links",
                        kriechzahl=1.0)
        a.spannungsfall("Zugsteifigkeit", art="normalkraft_emodul", M_Ed=-50.0,
                        werkstoffsatz="charakteristisch", rechenart="block")
        # Die Stahlspannungen: quasi-ständig aus der Tragsicherheit und ein
        # eigener Fall, häufig ein schiefer -- die Nulllinie dreht.
        a.quasistaendig.aus_tragsicherheit = True
        a.quasistaendig.lastfall("Dauer", N_Ed=-300.0, M_y_Ed=120.0, M_z_Ed=60.0)
        a.haeufig.lastfall("Häufig schief", N_Ed=-500.0, M_y_Ed=200.0, M_z_Ed=100.0)
        return a

    @staticmethod
    def _stuetze(kennung: str) -> QuerschnittsanalyseEintrag:
        a = QuerschnittsanalyseEintrag(
            kennung=kennung, name="Stütze",
            werkstoffwahl=[WerkstoffwahlEintrag(material="b1", satz="charakteristisch"),
                           WerkstoffwahlEintrag(material="s1", satz="charakteristisch")],
            einachsig=True, zwaengung=True)
        a.polygon([[0, 0], [400, 0], [400, 400], [0, 400]], material="b1")
        for z in (50, 350):
            a.stablinie([50, z], [350, z], art="anzahl", durchmesser=20, anzahl=3, stahl="s1")
        a.lastfall("Druck", N_Ed=-2500.0, M_y_Ed=120.0)
        a.lastfall("Zug", N_Ed=400.0)
        a.spannungsfall("Randdehnungen", art="dehnungen", eps_oben=-2.0, eps_unten=5.0,
                        richtung="oben")
        a.spannungsfall("Biegesteifigkeit", art="moment_emodul", N_Ed=-800.0,
                        richtung="oben", werkstoffsatz="charakteristisch")
        # Quasi-ständig mit der Parabel: σ_s,adm ist bei normaler Anforderung f_yk.
        a.quasistaendig.wahl.rechenart = "parabel"
        a.quasistaendig.lastfall("Dauer", N_Ed=-600.0, M_y_Ed=80.0)
        # Knicken unten und seitlich, die Verformung mit Kriechen.
        a.knicken_wahl_verformung.kriechzahl = 1.5
        a.knickfall("Stütze", N_Ed=-1500.0, M_Ed_1=30.0, laenge=4.0)
        a.knickfall("Seitlich", N_Ed=-1200.0, M_Ed_1=10.0, laenge=5.0, knicklaenge=3.5,
                    richtung="links")
        return a
