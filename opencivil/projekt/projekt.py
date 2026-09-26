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
from opencivil.projekt.gleichungen import GleichungsblattEintrag, GleichungszeileEintrag
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
        mit Stabzahl in y, ein Knickfall; eine zweite Platte mit x aussen und
        b = 500 mm, die im Feld nicht aufgeht und deren Stahl unter Dauerlast
        fliesst, dazu Querkraft ohne Bügel -- einmal über m_Rd, einmal
        darunter, mit Einlage; eine dritte ohne x-Bewehrung; eine vierte mit
        Querkraft ohne Einlage, einer Einwirkung, die am kürzesten Abstand
        gemessen wird, und ⌀40 in y unter der x-Bewehrung -- die fliesst bei
        x = h/2 nicht. Dazu ein Blatt Gleichungen. Gebaut über die Fassade, wie
        ein Benutzer es in Python täte.
        """
        p = cls(name="Jeder Nachweis einmal")
        p.beton("C30/37")
        p.stahl("B500B")
        decke = p.platte("Decke", h=300, x=[18, 12], x_zulage=[12, 0], y=[12, 12],
                         rissanforderung="erhoeht", duktilitaet=True, sproede=True,
                         zwaengung=True, zwaengung_begrenzt=True,
                         zwaengung_biegung=True)
        decke.querkraftbewehrung.durchmesser = 8.0
        decke.querkraftbewehrung.abstand_y = None
        decke.querkraftbewehrung.anzahl_y = 5.0
        decke.einwirkung("Feld", M_Ed=150, V_Ed=80)
        decke.einwirkung("Feld mit Druck", M_Ed=120, N_Ed=-300)
        decke.einwirkung("Stütze", M_Ed=-60, V_Ed=60)
        decke.haeufig.aus_tragsicherheit = True
        decke.haeufig.lastfall("Gebrauch", M_Ed=90)
        decke.quasistaendig.aus_tragsicherheit = True
        decke.quasistaendig.lastfall("Dauerlast", M_Ed=70)
        decke.knickfall("Wand", N_Ed=-800, M_Ed_1=20, laenge=3.0)

        # Ein Streifen von 500 mm: M und N je b, V je Meter. Mit halben
        # Momenten sind es dieselben Grade wie bei 1000 mm -- nur die
        # Lagentabelle zeigt, dass x je b und y je Laufmeter gilt.
        dach = p.platte("Dach", h=200, x=[10, 10], y=[8, 8], x_innen=False,
                        einlagenhoehe=40, b=500)
        dach.einwirkung("Feld", M_Ed=40, V_Ed=40)
        dach.einwirkung("Rand", M_Ed=10, V_Ed=30)
        dach.quasistaendig.lastfall("Dauerlast", M_Ed=20)

        ohne = p.platte("Ohne x", h=250, x=[0, 0], y=[12, 12])
        ohne.einwirkung("Feld", M_Ed=30, V_Ed=20)

        konsole = p.platte("Konsole", h=250, x=[12, 12], y=[40, 10])
        konsole.einwirkung("Feld", M_Ed=40, V_Ed=50)
        konsole.einwirkung("Schräg", M_Ed=30, N_Ed=-500).art = "naechster_Punkt"

        # Ein Blatt Gleichungen: Definition, Projektwert, Auswertung mit
        # gewünschter Einheit, Text -- und eine Zeile mit Fehler.
        zeile = GleichungszeileEintrag
        p.gleichungen.append(GleichungsblattEintrag(p.freie_kennung("g"), "Vorbemessung", [
            zeile(art="text", text="Stütze 30 × 30 cm, zentrisch."),
            zeile(latex=r"a=30\mathrm{cm}"),
            zeile(art="projektwert", name=r"f_{cd}", wert_id="beton.b1.f_cd"),
            zeile(latex=r"N_{Rd}=a^{2}\cdot f_{cd}", einheit="kN"),
            zeile(latex=r"\frac{N_{Rd}}{1.5\mathrm{m}}="),
            zeile(latex=r"b=a+N_{Rd}"),
        ]))
        return p
