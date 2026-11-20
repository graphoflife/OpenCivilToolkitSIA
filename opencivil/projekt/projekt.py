"""
opencivil/projekt/projekt.py -- das Projekt als Ganzes.

VERANTWORTUNG:
Das :class:`Projekt` haelt Materialien und Bauteile zusammen und ist das, was
gespeichert, geoeffnet und gerechnet wird. Hier stehen der Zugriff auf die
Teile, die Methoden fuer das Rechnen ohne Oberflaeche, die Pruefungen ueber
mehrere Teile hinweg (eindeutige Kennungen und Materialnamen), die Sandbox
jeder App, Speichern und Laden. Das Beispiel, mit dem die Oberflaeche
startet, und das Pruefprojekt «Jeder Nachweis» baut
:mod:`opencivil.projekt.beispiele`.

Gebaut wird in :mod:`opencivil.projekt.aufbau`; :meth:`Projekt.aufbauen`
reicht nur weiter.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple, Union

from opencivil.querschnitt.platte import LAGENZAHL, Richtung
from opencivil.ergebnis import Ergebnis
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.beton import ERSTER_BETON
from opencivil.material.betonstahl import ERSTER_STAHL
from opencivil.projekt.eintraege import Beschreibung, MaterialEintrag, PostenEintrag
from opencivil.projekt.balkensystem import BalkensystemEintrag
from opencivil.projekt.balkensystem3d import Balkensystem3dEintrag
from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.projekt.pfahl import PfahlEintrag
from opencivil.projekt.lesen import (
    ProjektFehler, felder_pruefen, inhalt_pruefen, lesen, ort, ort_von,
)
from opencivil.projekt.netz import neue_kennung
from opencivil.projekt.platte import QuerschnittEintrag
from opencivil.projekt.skript import SkriptEintrag
from opencivil.projekt.querschnittsanalyse import QuerschnittsanalyseEintrag
from opencivil.projekt.setzung import SetzungEintrag
from opencivil.projekt.durchstanzen import DurchstanzEintrag
from opencivil.projekt.decke import DeckeEintrag
from opencivil.projekt.aufbau import (
    ANALYSE, BALKENSYSTEM, BALKENSYSTEM3D, BAUTEILE, DECKE, DURCHSTANZEN, GRUNDBRUCH, PFAHL,
    PLATTE, SETZUNG, Aufbau, aufbauen,
)


#: Die Listen der Apps ausser den Materialien, je mit der Klasse ihrer
#: Eintraege und der Vorsilbe ihrer Kennungen: die Bauteilarten
#: (:data:`~opencivil.projekt.aufbau.BAUTEILE`) und die Skripte der App
#: «Python». Was «+» in ihnen anlegt, steht im Katalog (``neu``); jede hat
#: eine Sandbox.
APPLISTEN: Dict[str, Tuple[type, str]] = {
    **{art.liste: (art.eintrag, art.vorsilbe) for art in BAUTEILE},
    "skripte": (SkriptEintrag, "p"),
}

#: Wie die Sandbox jeder App heisst (Benutzer, 2026-11-20).
SANDBOX = "Sandbox"


def naechster_name(stamm: str, namen: Iterable[str]) -> str:
    """
    Der Name eines neuen Eintrags: «Platte 1», «Platte 2» … -- der erste, den
    es unter ``namen`` noch nicht gibt. So nennt auch die Oberflaeche, was
    «+» anlegt (``naechsterName``, web/js/zustand.js); ein Test haelt beide
    gleich.
    """
    vergeben = set(namen)
    i = 1
    while f"{stamm} {i}" in vergeben:
        i += 1
    return f"{stamm} {i}"


def kopie_name(name: str, namen: Iterable[str]) -> str:
    """
    Der Name einer Kopie: «Decke über EG (Kopie)», dann «… (Kopie 2)» -- der
    erste, den es unter ``namen`` noch nicht gibt. Wie ⧉ in der Oberflaeche
    (``kopieName``, web/js/zustand.js); ein Test haelt beide gleich.
    """
    vergeben = set(namen)
    kandidat, i = f"{name} (Kopie)", 2
    while kandidat in vergeben:
        kandidat, i = f"{name} (Kopie {i})", i + 1
    return kandidat


# ===========================================================================
# Projekt
# ===========================================================================

@dataclass
class Projekt(Beschreibung):
    """Die vollstaendige, speicherbare Beschreibung eines Projekts."""

    STAMM = "Projekt"

    name: str = "Neues Projekt"
    materialien: List[MaterialEintrag] = field(default_factory=list)
    querschnitte: List[QuerschnittEintrag] = field(default_factory=list)
    querschnittsanalysen: List[QuerschnittsanalyseEintrag] = field(default_factory=list)
    """Gezeichnete Querschnitte: Polygone, Bewehrung, Schubwände."""

    balkensysteme: List[BalkensystemEintrag] = field(default_factory=list)
    """Ebene Rahmen: Knoten, Stäbe, Lager, Lasten, Lastfälle."""

    balkensysteme3d: List[Balkensystem3dEintrag] = field(default_factory=list)
    """Rahmen im Raum: wie die ebenen, mit x, y und z und Torsion."""

    decken: List[DeckeEintrag] = field(default_factory=list)
    """Stahlbetondecken nach der Streifenmethode: Platten, Lager, Stützen, Unterzüge."""

    durchstanzstellen: List[DurchstanzEintrag] = field(default_factory=list)
    """Stützen und Wände, an denen das Durchstanzen nachgewiesen wird."""

    grundbrueche: List[GrundbruchEintrag] = field(default_factory=list)
    """Flachfundamente mit Grundbruch und Gleiten."""

    setzungen: List[SetzungEintrag] = field(default_factory=list)
    """Flachfundamente auf geschichtetem Baugrund, mit ihrer Setzung."""

    pfaehle: List[PfahlEintrag] = field(default_factory=list)
    """Einzelpfähle: Bohr- und Mikropfähle mit äusserem und innerem Widerstand."""

    skripte: List[SkriptEintrag] = field(default_factory=list)
    """Die Python-Skripte der App «Python» -- gespeichert, nicht gerechnet."""

    sandboxen: Dict[str, str] = field(default_factory=dict)
    """
    Je Liste einer App (:data:`APPLISTEN`) die Kennung ihrer Sandbox, des
    Eintrags zum Ausprobieren -- siehe :meth:`sandbox_zuruecksetzen`. Hier
    und nicht an den Eintraegen: so steht die Regel an einer Stelle, und
    eine Kopie der Sandbox ist von selbst ein gewoehnlicher Eintrag.
    """

    vergeben: Dict[str, int] = field(default_factory=dict)
    """
    Je Vorsilbe die hoechste Nummer, die das Projekt je vergeben hat -- an
    Materialien, Bauteile, Skripte: eine Kennung kommt nie wieder
    (:func:`~opencivil.projekt.netz.neue_kennung`).
    """

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
        Eine Kopie, in der von den Bauteilen nur dieses eine steht -- mit
        denen, deren Querschnitt es nimmt (``bezuege``), auch ueber mehrere
        Stufen; die Materialien bleiben. So rechnet die Bewehrungssuche: die
        anderen Bauteile kann sie nicht beeinflussen, und ihre Urteile
        zaehlten sonst mit. Und so holt der MCP-Zugang die Herleitung eines
        Bauteils -- ein Stab, dessen Querschnitt eine Analyse ist, rechnete
        ohne sie nicht.
        """
        self.bauteil(kennung)
        alle = {e.kennung: e for e in self.bauteile()}
        behalten, offen = set(), [kennung]
        while offen:
            k = offen.pop()
            if k in alle and k not in behalten:
                behalten.add(k)
                offen.extend(alle[k].bezuege())
        kopie = copy.deepcopy(self)
        for art in BAUTEILE:
            setattr(kopie, art.liste,
                    [e for e in getattr(kopie, art.liste) if e.kennung in behalten])
        kopie.sandboxen = {liste: k for liste, k in kopie.sandboxen.items()
                           if any(e.kennung == k for e in getattr(kopie, liste))}
        return kopie

    def bauteil(self, kennung: str) -> Any:
        """Ein Bauteil gleich welcher Art -- eine Platte, eine Analyse, ein System."""
        for eintrag in self.bauteile():
            if eintrag.kennung == kennung:
                return eintrag
        raise ProjektFehler(f"Ein Bauteil '{kennung}' gibt es im Projekt nicht.")

    def freie_kennung(self, vorsilbe: str) -> str:
        """Eine Kennung, die es im Projekt nie gab -- siehe :func:`~opencivil.projekt.netz.neue_kennung`."""
        return neue_kennung(self, vorsilbe, [e.kennung for e in (*self.materialien, *self.bauteile(),
                                                                 *self.skripte)])

    def verweise(self, kennung: str) -> List[Any]:
        """
        Die Bauteile, die auf diese Kennung zeigen -- als Material oder als
        Querschnitt (:meth:`materialien` und :meth:`bezuege` jedes Eintrags).
        Was hier steht, darf nicht geloescht werden; die Oberflaeche fragt hier,
        bevor sie loescht (Dienst ``verweise``), statt es in einer eigenen
        Liste nachzubauen.

        Eine Sandbox haelt nichts fest: zeigt sie auf etwas Geloeschtes, sagt
        sie es selbst, und zurueckgesetzt nimmt sie wieder das erste Material.
        Sonst liesse sich der einzige Beton nicht loeschen, weil die Sandbox
        der Platten ihn nimmt.
        """
        return [e for e in self.bauteile() if not self.ist_sandbox(e.kennung)
                and (kennung in e.materialien() or kennung in e.bezuege())]

    def eigener_name(self, art: str) -> str:
        """Der erste freie Name eines eigenen Materials: BE1, BE2 ..., S1 ... oder ST1 ..."""
        vorsilbe = MATERIALARTEN[art].eigene
        vergeben = {m.anzeigename for m in self.materialien}
        i = 1
        while f"{vorsilbe}{i}" in vergeben:
            i += 1
        return f"{vorsilbe}{i}"

    # -- Ohne Oberflaeche ---------------------------------------------------
    #
    # Die Beschreibung ist das Modell, auch in Python. Diese Methoden legen an,
    # was die Oberflaeche anlegen wuerde, und geben den Eintrag zurueck; was
    # sie nicht abdecken, setzt man am Eintrag selbst. Einen zweiten Satz
    # Klassen daneben gibt es nicht -- er muesste mit diesem gleich bleiben,
    # und genau das tut so etwas nie lange.

    def beton(self, sorte: str = "C30/37") -> MaterialEintrag:
        """Eine Betonsorte nach Norm -- Kennung ``b1``, ``b2`` ..."""
        return self._normsorte("beton", sorte)

    def stahl(self, sorte: str = "B500B") -> MaterialEintrag:
        """Eine Betonstahlsorte nach Norm -- Kennung ``s1``, ``s2`` ..."""
        return self._normsorte("betonstahl", sorte)

    def baustahl(self, sorte: str = "S235") -> MaterialEintrag:
        """Eine Baustahlsorte nach SIA 263 -- Kennung ``st1``, ``st2`` ..."""
        return self._normsorte("baustahl", sorte)

    def eigener_beton(self, vorlage: str = "C30/37") -> MaterialEintrag:
        """
        Ein eigener Beton, ``BE1``, ``BE2`` ... -- mit den Kennwerten der Sorte
        ``vorlage``, abzuaendern ueber ``abweichungen`` und
        ``ueberschreibungen``. Eine Normsorte selbst bleibt, wie sie ist.
        """
        return self._eigenes("beton", vorlage)

    def eigener_stahl(self, vorlage: str = "B500B") -> MaterialEintrag:
        """Ein eigener Betonstahl, ``S1``, ``S2`` ... -- siehe :meth:`eigener_beton`."""
        return self._eigenes("betonstahl", vorlage)

    def eigener_baustahl(self, vorlage: str = "S235") -> MaterialEintrag:
        """Ein eigener Baustahl, ``ST1``, ``ST2`` ... -- siehe :meth:`eigener_beton`."""
        return self._eigenes("baustahl", vorlage)

    def material_anlegen(self, art: str, sorte: str, *, eigen: bool = False) -> MaterialEintrag:
        """
        «+ Material»: eine Normsorte der Art ``art`` -- mit ``eigen`` ein
        eigenes Material, die Sorte als Vorlage (:meth:`eigener_beton`). Fuer
        wer die Art als Text hat, den MCP-Zugang; :meth:`beton` und die
        anderen sagen sie im Namen.
        """
        if art not in MATERIALARTEN:
            raise ProjektFehler(f"Eine Materialart '{art}' gibt es nicht. Möglich sind: "
                                f"{', '.join(MATERIALARTEN)}.")
        return self._eigenes(art, sorte) if eigen else self._normsorte(art, sorte)

    def _eigenes(self, art: str, vorlage: str) -> MaterialEintrag:
        eintrag = MaterialEintrag(kennung=self.freie_kennung(MATERIALARTEN[art].kennung), art=art,
                                  sorte=vorlage, name=self.eigener_name(art),
                                  eigenstaendig=True)
        eintrag.sorte_pruefen()
        self.materialien.append(eintrag)
        return eintrag

    def _normsorte(self, art: str, sorte: str) -> MaterialEintrag:
        """
        Legt eine Normsorte an und prueft sie sofort.

        Sofort und nicht erst beim Rechnen: ein Tippfehler in der Sorte soll
        an der Zeile auffallen, in der er steht.
        """
        eintrag = MaterialEintrag(kennung=self.freie_kennung(MATERIALARTEN[art].kennung),
                                  art=art, sorte=sorte, name=sorte)
        eintrag.sorte_pruefen()
        if any(m.anzeigename == sorte for m in self.materialien):
            raise ProjektFehler(
                f"'{sorte}' steht schon im Projekt. Eine Normsorte braucht es "
                f"nur einmal – mehrere Platten verwenden dieselbe.")
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
                        f"je Richtung zwei Durchmesser, unten "
                        f"und oben – angegeben sind {len(werte)} ({was}).", wo=f"Platte '{name}'")
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
        ``kombination`` --, Koordinaten in m. Leer, ohne die Lastfaelle und
        Kombinationen, die die Oberflaeche mitbringt: wer in Python zeichnet,
        zeichnet sein eigenes System.
        """
        eintrag = lesen(BalkensystemEintrag, felder, f"Balkensystem '{name}'",
                        BalkensystemEintrag(kennung=self.freie_kennung(BALKENSYSTEM.vorsilbe),
                                            name=name))
        self.balkensysteme.append(eintrag)
        return eintrag

    def balkensystem3d(self, name: str, **felder: Any) -> Balkensystem3dEintrag:
        """
        Ein leeres 3D-Balkensystem, ein Rahmen im Raum -- gezeichnet wie das
        ebene (:meth:`balkensystem`), mit Punkten ``(x, y, z)`` in m.
        """
        eintrag = lesen(Balkensystem3dEintrag, felder, f"3D-Balkensystem '{name}'",
                        Balkensystem3dEintrag(kennung=self.freie_kennung(BALKENSYSTEM3D.vorsilbe),
                                              name=name))
        self.balkensysteme3d.append(eintrag)
        return eintrag

    def decke(self, name: str, **felder: Any) -> DeckeEintrag:
        """
        Eine leere Decke. Gezeichnet wird danach mit dem Baukasten des
        Eintrags -- ``platte``, ``lager`` (ein Linienlager), ``stuetze``,
        ``unterzug``, ``zone`` --, Koordinaten in m.
        """
        eintrag = lesen(DeckeEintrag, felder, f"Decke '{name}'",
                        DeckeEintrag(kennung=self.freie_kennung(DECKE.vorsilbe), name=name))
        self.decken.append(eintrag)
        return eintrag

    def durchstanzen(self, name: str, beton: str, stahl: str, **felder: Any) -> DurchstanzEintrag:
        """
        Ein Durchstanznachweis mit den Vorgaben der Oberflaeche. ``beton`` und
        ``stahl`` sind Kennungen von Materialien; alles Weitere -- ``h``,
        ``lage``, ``V_d`` ... -- geht als Stichwort an den Eintrag: Masse der
        Platte und der Stütze in mm, Spannweiten in m, Kräfte in kN.
        Aussparungen mit :meth:`~opencivil.projekt.durchstanzen.DurchstanzEintrag.aussparung`.
        """
        eintrag = lesen(DurchstanzEintrag, {"beton": beton, "stahl": stahl, **felder},
                        f"Durchstanzen '{name}'",
                        DurchstanzEintrag(kennung=self.freie_kennung(DURCHSTANZEN.vorsilbe),
                                          name=name))
        self.durchstanzstellen.append(eintrag)
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

    def pfahl(self, name: str, stahl: str, beton: str = "", **felder: Any) -> PfahlEintrag:
        """
        Ein Pfahl mit den Vorgaben der Oberflaeche, aber ohne ihre Startschicht
        und Startkombination: wer rechnet, gibt sie mit ``schicht`` und
        ``kombination`` selbst an. ``stahl`` und ``beton`` sind Kennungen von
        Materialien, der Beton nur beim Bohrpfahl. Alles Weitere -- ``art``,
        ``D``, ``grundlage`` ... -- geht als Stichwort an den Eintrag; Masse
        des Querschnitts in mm, Tiefen in m, Spannungen in kPa.
        """
        eintrag = lesen(PfahlEintrag, {"stahl": stahl, "beton": beton, **felder},
                        f"Pfahl '{name}'",
                        PfahlEintrag(kennung=self.freie_kennung(PFAHL.vorsilbe), name=name))
        self.pfaehle.append(eintrag)
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
                f"Welcher {wort}? Im Projekt stehen {len(vorhanden)} – bitte "
                f"mit {'beton' if art == 'beton' else 'stahl'}=... angeben"
                + ("." if vorhanden else
                   f", oder zuerst einen anlegen: "
                   f"projekt.{'beton' if art == 'beton' else 'stahl'}(...)."))
        return vorhanden[0].kennung

    def rechnen(self) -> Ergebnis:
        """
        Alles rechnen, was die Oberflaeche auch rechnet -- ohne sie.

        Dieselben Ziele in derselben Reihenfolge (:meth:`Aufbau.alle_ziele`),
        also derselbe Bericht -- ohne die Sandboxen, wie dort
        (:meth:`ohne_sandboxen`). Ohne Zwischenspeicher: der lohnt sich erst,
        wenn man dieselbe Platte hundertmal rechnet.
        """
        aufbau = self.ohne_sandboxen().aufbauen()
        return Ergebnis(projekt=self, aufbau=aufbau,
                        loesung=aufbau.werk.loese(*aufbau.alle_ziele()))

    # -- Eintraege der Apps -------------------------------------------------
    #
    # Was «+», ⧉ und × in einer App tun -- fuer wer ohne Oberflaeche arbeitet,
    # etwa ueber den MCP-Zugang (:mod:`opencivil.mcp`). Die Oberflaeche tut
    # dasselbe in JavaScript, ohne auf den Kern zu warten (``nachVorlage``
    # und ``kopieren`` in web/js/apps.js); Vorlage, erste Materialien und den
    # Stamm des Namens liest sie aus dem Katalog, also von hier.

    def eintrag_anlegen(self, liste: str) -> Any:
        """
        «+» einer App: ein frischer Eintrag nach der Vorlage seiner Klasse und
        mit dem ersten Material jeder Art, die er nimmt
        (:meth:`~opencivil.projekt.eintraege.Beschreibung.frisch`), unter einer
        Kennung, die es im Projekt nie gab, am Ende der Liste -- und mit dem
        Namen, den «+» gibt: «Platte 1» (:func:`naechster_name`). Fehlt ein
        Material, das er nimmt, rechnet er erst, wenn eines da ist, wie die
        Sandbox.
        """
        klasse, vorsilbe = self._app(liste)
        eintraege = getattr(self, liste)
        eintrag = klasse.frisch(self.materialien)
        eintrag.kennung = self.freie_kennung(vorsilbe)
        eintrag.name = naechster_name(klasse.STAMM, (e.name for e in eintraege))
        eintraege.append(eintrag)
        return eintrag

    def eintrag_kopieren(self, kennung: str) -> Any:
        """
        ⧉: eine Kopie gleich hinter dem Original, alles wie dort, nur Kennung
        und Name neu -- «Decke über EG (Kopie)» (:func:`kopie_name`). Die
        Kopie der Sandbox ist ein gewoehnlicher Eintrag und heisst wie ein
        neuer, «Platte 1».
        """
        liste, i = self._ort_in_app(kennung)
        klasse, vorsilbe = APPLISTEN[liste]
        eintraege = getattr(self, liste)
        namen = [e.name for e in eintraege]
        kopie = copy.deepcopy(eintraege[i])
        kopie.kennung = self.freie_kennung(vorsilbe)
        kopie.name = (naechster_name(klasse.STAMM, namen) if self.ist_sandbox(kennung)
                      else kopie_name(eintraege[i].name, namen))
        eintraege.insert(i + 1, kopie)
        return kopie

    def eintrag_loeschen(self, kennung: str) -> Any:
        """
        ×: ein Eintrag einer App oder ein Material geht -- nicht die Sandbox,
        die nur zurueckgesetzt wird, und nicht, solange ein Bauteil auf ihn
        zeigt (:meth:`verweise`); der Fehler nennt dann die Bauteile. Gibt den
        geloeschten Eintrag zurueck.
        """
        for liste in ("materialien", *APPLISTEN):
            eintraege = getattr(self, liste)
            eintrag = next((e for e in eintraege if e.kennung == kennung), None)
            if eintrag is None:
                continue
            if self.ist_sandbox(kennung):
                raise ProjektFehler("die Sandbox lässt sich nicht löschen, nur zurücksetzen.",
                                    wo=ort_von(eintrag))
            verweise = self.verweise(kennung)
            if verweise:
                raise ProjektFehler("bleibt, solange noch darauf zeigt: "
                                    + ", ".join(ort_von(v) for v in verweise) + ".",
                                    wo=ort_von(eintrag))
            eintraege.remove(eintrag)
            return eintrag
        raise ProjektFehler(f"Einen Eintrag '{kennung}' gibt es im Projekt nicht.")

    def _app(self, liste: str) -> Tuple[type, str]:
        """Klasse und Vorsilbe der App mit dieser Liste (:data:`APPLISTEN`)."""
        if liste not in APPLISTEN:
            raise ProjektFehler(f"Eine App mit der Liste '{liste}' gibt es nicht. Möglich sind: "
                                f"{', '.join(APPLISTEN)}.")
        return APPLISTEN[liste]

    def _ort_in_app(self, kennung: str) -> Tuple[str, int]:
        """In welcher Liste einer App der Eintrag steht, und an welcher Stelle."""
        for liste in APPLISTEN:
            for i, e in enumerate(getattr(self, liste)):
                if e.kennung == kennung:
                    return liste, i
        raise ProjektFehler(f"Einen Eintrag '{kennung}' gibt es in keiner App des Projekts.")

    # -- Sandbox ------------------------------------------------------------
    #
    # In jeder App ein Eintrag zum Ausprobieren (Benutzer, 2026-11-20): immer
    # da, er heisst «Sandbox», laesst sich kopieren, aber nicht loeschen, und
    # beginnt nach jedem Laden der Seite neu. Zum Projekt, wie es im Bericht
    # steht, gehoert er nicht (:meth:`ohne_sandboxen`). Er haelt kein Material
    # und kein Bauteil fest (:meth:`verweise`), und auf ihn zeigt nur eine
    # Sandbox -- sonst rechnete ein Bauteil nach dem Laden der Seite still mit
    # anderem (:func:`~opencivil.projekt.aufbau.aufbauen`).

    def ist_sandbox(self, kennung: str) -> bool:
        """Ob dieser Eintrag die Sandbox seiner App ist."""
        return kennung in self.sandboxen.values()

    def sandbox_zuruecksetzen(self, liste: str) -> Any:
        """
        Die Sandbox einer App, frisch: nach der Vorlage ihrer Klasse und mit
        dem ersten Material jeder Art, das sie nimmt, wie ein neuer Eintrag
        der Oberflaeche (:meth:`~opencivil.projekt.eintraege.Beschreibung.frisch`).
        Eine vorhandene wird an ihrem Platz ersetzt und behaelt ihre Kennung
        -- wer auf sie zeigt, zeigt weiter auf sie. Eine fehlende kommt
        zuoberst in die Liste.
        """
        if liste not in APPLISTEN:
            raise ProjektFehler(f"Eine Sandbox hat jede App ausser den Materialien – eine Liste "
                                f"'{liste}' gibt es dafür nicht. Möglich sind: "
                                f"{', '.join(APPLISTEN)}.")
        klasse, vorsilbe = APPLISTEN[liste]
        eintraege = getattr(self, liste)
        alt = self.sandboxen.get(liste, "")
        sandbox = klasse.frisch(self.materialien)
        sandbox.kennung = alt or self.freie_kennung(vorsilbe)
        sandbox.name = SANDBOX
        kennungen = [e.kennung for e in eintraege]
        if alt in kennungen:
            eintraege[kennungen.index(alt)] = sandbox
        else:
            eintraege.insert(0, sandbox)
        self.sandboxen[liste] = sandbox.kennung
        return sandbox

    def sandboxen_anlegen(self, *, frisch: bool = False) -> None:
        """
        Jede Sandbox, die fehlt -- in einem neuen Projekt, in einer Datei, die
        noch keine kennt. Mit ``frisch`` beginnt auch jede vorhandene neu: so
        startet die Seite (Benutzer, 2026-11-20).
        """
        for liste in APPLISTEN:
            if frisch or liste not in self.sandboxen:
                self.sandbox_zuruecksetzen(liste)

    def ohne_sandboxen(self) -> "Projekt":
        """Eine Kopie ohne die Sandboxen -- das Projekt, wie es im Bericht steht."""
        kopie = copy.deepcopy(self)
        for liste, kennung in self.sandboxen.items():
            setattr(kopie, liste, [e for e in getattr(kopie, liste) if e.kennung != kennung])
        kopie.sandboxen = {}
        return kopie

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

        # Je Sandbox: sie steht in ihrer Liste und heisst so. Geloescht oder
        # umbenannt wird sie nur in einer Datei von Hand -- die Oberflaeche
        # bietet beides nicht an.
        for liste, kennung in self.sandboxen.items():
            if liste not in APPLISTEN:
                raise ProjektFehler(f"eine Sandbox hat jede App ausser den Materialien – eine "
                                    f"Liste '{liste}' hat keine.", wo="Projekt")
            sandbox = next((e for e in getattr(self, liste) if e.kennung == kennung), None)
            if sandbox is None:
                raise ProjektFehler(f"die Sandbox ({APPLISTEN[liste][0].BEZEICHNUNG}) fehlt – eine "
                                    f"Sandbox lässt sich nicht löschen, nur zurücksetzen.",
                                    wo="Projekt")
            if sandbox.name != SANDBOX:
                raise ProjektFehler(f"die Sandbox heisst «{SANDBOX}», nicht «{sandbox.name}».",
                                    wo=ort_von(sandbox))

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
    def neu(cls, name: str = "Neues Projekt") -> "Projekt":
        """
        Ein neues Projekt, wie es «+» in der Oberflaeche anlegt: mit dem
        ersten Beton und dem ersten Betonstahl, den ein neues Material
        vorschlaegt (:data:`~opencivil.material.beton.ERSTER_BETON`,
        :data:`~opencivil.material.betonstahl.ERSTER_STAHL`), und ohne
        Bauteile. So rechnet die erste Platte gleich. Die Sandboxen legt die
        Oberflaeche dazu an (:meth:`sandboxen_anlegen`); wer in Python
        rechnet, braucht sie nicht.
        """
        projekt = cls(name=name)
        projekt.beton(ERSTER_BETON)
        projekt.stahl(ERSTER_STAHL)
        return projekt

    @classmethod
    def beispiel(cls) -> "Projekt":
        """Das Beispiel, mit dem die Oberflaeche startet -- gebaut in :mod:`.beispiele`."""
        from opencivil.projekt.beispiele import beispiel
        return beispiel()

    @classmethod
    def jeder_nachweis(cls) -> "Projekt":
        """Jeder Nachweis einmal laut -- gebaut in :mod:`.beispiele`."""
        from opencivil.projekt.beispiele import jeder_nachweis
        return jeder_nachweis()
