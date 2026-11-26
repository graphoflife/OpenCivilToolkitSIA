"""
opencivil/web/api.py -- Uebersetzung der Rechenergebnisse nach JSON.

VERANTWORTUNG:
Bildet :class:`Loesung`, Protokoll, Zusammenfassung und Katalogdaten auf
schlichte JSON-Strukturen ab. Zusammen mit :mod:`opencivil.web.diagrammdaten`,
das die Punktfolgen der Diagramme liefert, ist das die einzige Stelle, die
beide Welten kennt.

Wichtig: hier wird nichts gerechnet und nichts formatiert, was der Rechenkern
nicht schon bestimmt hat. Die Oberflaeche bekommt fertige LaTeX-Zeichenketten
und fertig formatierte Zahlen -- sie soll die Darstellung nicht ein zweites Mal
erfinden, sonst laufen Bericht und Bildschirm auseinander.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional, Sequence

from opencivil.bewehrungssuche import DURCHMESSER, Suchmodus
from opencivil.core.einheiten import MM
from opencivil.bericht.formelsammlung import formelname, in_sammlung
from opencivil.bericht.markdown import block_markdown
from opencivil.bericht.zusammenfassung import (
    GRAD_SPALTE, STAPEL_SPALTEN, angaben, hinweise, kennzahlen, kennzahlentabelle,
    nachweistabelle,
    stiller_hinweis, zusammenfassen,
)
from opencivil.core.kurzform import kurzform
from opencivil.core.protokoll import (
    GleichungBlock, HinweisBlock, Protokoll, TabellenBlock, Tafel, TextBlock,
    TitelBlock, darstellen,
)
from opencivil.core.rechenwerk import Loesung
from opencivil.core.wert import Wert
from opencivil.decke.modell import Aufteilung
from opencivil.material.arten import MATERIALARTEN
from opencivil.material.beton import BETONSORTEN
from opencivil.material.betonstahl import STAHLSORTEN
from opencivil.material.spannstahl import Erzeugnis
from opencivil.nachweis.biegung_normalkraft import Erfuellungsart
from opencivil.nachweis.rissanforderung import Rissanforderung
from opencivil.projekt import BAUTEILE, Aufbau
from opencivil.projekt.balkensystem import BalkensystemEintrag
from opencivil.projekt.balkensystem3d import Balkensystem3dEintrag
from opencivil.projekt.durchstanzen import DurchstanzEintrag
from opencivil.decke.schnitt import BALKENGROESSEN
from opencivil.projekt.decke import DIAGRAMMGROESSEN as DECKENGROESSEN
from opencivil.projekt.decke import VORSILBEN as DECKENVORSILBEN
from opencivil.projekt.aufbau.kern import kennwertbereich
from opencivil.projekt.lesen import eintragsklassen, feldangaben, katalogname, wahl_von
from opencivil.projekt.projekt import APPLISTEN, Projekt
from opencivil.projekt.querschnittsanalyse import SCHNITTE
from opencivil.querschnitt.bauweise import BEWEHRT
from opencivil.querschnitt.platte import BREITE_Y_MM
from opencivil.querschnitt.spannglieder import (
    NEIGUNG_ERKLAERT, VORGABE_SPANNUNG, Spannwirkung, Verbund,
)
from opencivil.querschnitt.zugseite import UM_Y, Zugseite
from opencivil.querschnitt.geometrie import VERSCHMIERT, Linienart
from opencivil.querschnitt.vorlagen import RANDABSTAND, VORLAGEN
from opencivil.querschnitt.gesetzwahl import Werkstoffsatz
from opencivil.nachweis.rechenwahl import RECHENARTEN
from opencivil.spannungsanalyse import Analyseart
from opencivil.stabwerk.rechnung import Balkensystem
from opencivil.stabwerk3d.rechnung import Balkensystem3d
from opencivil.geotechnik import fundament, setzung
from opencivil.geotechnik.setzung import Steifigkeit
from opencivil.geotechnik.verhalten import Verhalten
from opencivil.projekt.grundbruch import GrundbruchEintrag
from opencivil.projekt.setzung import SchichtEintrag, SetzungEintrag
from opencivil.durchstanzen import stelle
from opencivil.erdbeben import ersatzkraft
from opencivil.erdbeben.ersatzkraft import (
    Baugrundklasse, Bauwerksklasse, Erdbebenzone, Schwingzeit, Wandlage,
)
from opencivil.projekt.erdbeben import ErdbebenEintrag, GeschossEintrag, TragwandEintrag
from opencivil.pfahl import pfahl
from opencivil.pfahl.boden import Mantel
from opencivil.pfahl.pfahl import Abscheren, Grundlage, Kopf, Pfahlart, Spitze, Tragglied
from opencivil.projekt.pfahl import PfahlEintrag, PfahlschichtEintrag
from opencivil.web import (
    balkendaten, diagrammdaten, durchstanzdaten, systemkatalog, werkstoffkurven,
)
from opencivil.web.anzeige import zelle_dict
from opencivil.web.umschlag import endlich
from opencivil.web.zeichendaten import zeichendaten

#: Die Wertesaetze und Betongesetze mit Beschriftung -- dieselben in der
#: Querschnittsanalyse und in jeder Spannung-Dehnung-Analyse. ``kurz`` fuer
#: die Karte einer Analyse, in der die lange nicht Platz hat. Die Woerter
#: stehen beim Wertesatz selbst.
_WERKSTOFFSAETZE = [
    {"wert": s.value, "beschriftung": s.beschriftung, "kurz": s.kurz}
    for s in Werkstoffsatz
]
#: Wie die Angaben einer verschmierten Stablinie heissen: kurz im Schalter,
#: lang in seinem Titel -- je Angabe, die die Beschreibung kennt.
_VERSCHMIERUNGEN = {
    "flaeche": ("Stahlfläche", "Die Stahlfläche der ganzen Linie, von Hand"),
    "staebe": ("⌀ und Teilung", "Stäbe ⌀ im Abstand s über die Länge L, verschmiert: L/s · π⌀²/4"),
}
#: Wie die Aufteilungen einer Decke heissen: kurz im Schalter, lang in seinem
#: Titel. Die Regel dahinter steht in :mod:`opencivil.decke.aufteilung`.
#: Wie die Ergebnisbilder einer Decke heissen: kurz im Schalter, lang ueber
#: dem Bild -- je Groesse, die die Beschreibung kennt. M und V sind die eines
#: ganzen Unterzugs.
_DECKENGROESSEN = {
    "m_x": ("m_x", "Moment m_x"), "m_y": ("m_y", "Moment m_y"), "m_xy": ("m_xy", "Drillmoment m_xy"),
    "v_x": ("v_x", "Querkraft v_x"), "v_y": ("v_y", "Querkraft v_y"),
    "v_0": ("v_0", "Hauptquerkraft v_0"), "lager": ("Lager", "Lagerkräfte"),
    "M": ("M", "Moment M"), "V": ("V", "Querkraft V"),
}
_AUFTEILUNGEN = {
    Aufteilung.AUTOMATISCH: ("automatisch", "Je Stelle nach ihren Lagern: zum nahen Rand, sonst mehr "
                                            "in die kürzere Spannweite (Folie 31) – mit Bändern durch "
                                            "die Stützen und an offenen Rändern"),
    Aufteilung.FEST: ("fest", "Überall derselbe Anteil in Richtung 1 – ausser in den Zonen"),
}


def _rechenarten(arten) -> list:
    """Die Rechenarten mit Beschriftung -- und ob die Kriechzahl bei ihnen wirkt."""
    return [{"wert": a.value, "beschriftung": a.beschriftung, "kurz": a.kurz,
             "mit_kriechzahl": a.mit_kriechzahl} for a in arten]


# ===========================================================================
# Katalog
# ===========================================================================


def _vorlage(cls: type) -> Dict[str, Any]:
    """
    Wie ein frischer Eintrag dieser Klasse aussieht (:meth:`Beschreibung.frisch`)
    -- ohne Kennung, Namen und Materialien: die setzt die Oberflaeche.
    """
    return cls.frisch().als_dict()


def _neues_projekt() -> Dict[str, Any]:
    """
    Ein neues Projekt der Mappe, wie «+» oben links es anlegt: mit dem ersten
    Beton und Stahl (:meth:`Projekt.neu`) und mit den Sandboxen.
    """
    projekt = Projekt.neu()
    projekt.sandboxen_anlegen()
    return projekt.als_dict()


def klassen() -> Dict[str, type]:
    """
    Jede Klasse von Eintraegen unter dem Projekt, unter ihrem Namen ohne
    «Eintrag», klein: ``grundbruch``, ``schicht``, ``kombination`` -- so
    heissen ihre Feldangaben und ihre Vorlage im Katalog.
    """
    klassen: Dict[str, type] = {}
    for cls in eintragsklassen(Projekt):
        name = katalogname(cls)
        if name in klassen:
            raise ValueError(f"Zwei Klassen von Eintraegen hiessen im Katalog «{name}».")
        klassen[name] = cls
    return klassen


def _vorgaben() -> Dict[str, List[dict]]:
    """
    Je Klasse von Eintraegen, unter ihrem Namen im Katalog, die Gruppen der
    Vorgaben ihres Nachweises (:mod:`opencivil.core.vorgaben`) -- fuer jede
    Stellung der Wahlen, nach denen sie sich richten, mit den Werten, die die
    Beschreibung fuer diese Wahlen kennt.
    """
    return {katalogname(cls): [g.als_dict({n: wahl_von(cls, n) for n in g.nach}) for g in gruppen]
            for cls, gruppen in ((DurchstanzEintrag, stelle.VORGABEN),
                                 (GrundbruchEintrag, fundament.VORGABEN),
                                 (SetzungEintrag, setzung.VORGABEN),
                                 (SchichtEintrag, setzung.JE_SCHICHT),
                                 (PfahlEintrag, pfahl.VORGABEN),
                                 (PfahlschichtEintrag, pfahl.JE_SCHICHT),
                                 (ErdbebenEintrag, ersatzkraft.VORGABEN),
                                 (GeschossEintrag, ersatzkraft.JE_GESCHOSS),
                                 (TragwandEintrag, ersatzkraft.JE_WAND))}


def katalog() -> dict:
    """Alles, was die Oberflaeche zum Aufbau ihrer Auswahlfelder braucht."""
    return {
        "betonsorten": [
            {"sorte": sorte, "f_ck": f_ck, "f_ctm": f_ctm}
            for sorte, (f_ck, f_ctm) in BETONSORTEN.items()
        ],
        "stahlsorten": [
            {
                "sorte": sorte,
                "f_yk": s.f_yk,
                "f_yk_druck": s.f_yk_druck,
                "eps_uk": s.eps_uk,
                "eps_ud": s.eps_ud,
            }
            for sorte, s in STAHLSORTEN.items()
        ],
        # Je Materialart, in ihrer Folge: wie sie heisst, in welcher
        # Reihenfolge das Fenster «Neues Material» die Sorten anbietet,
        # womit Kennungen und Namen eigener Materialien beginnen, worauf die
        # Kennwerte stehen -- die Kennwerte selbst und, wo es sie gibt, die
        # Erzeugnisse je Sorte. Dazu, wie ein Satz die Art nennt: «Neues Holz».
        "materialarten": {
            name: {"titel": a.titel, "neu": a.neu, "eigen": a.eigen, "keinen": a.keinen,
                   "kennung": a.kennung, "eigene": a.eigene,
                   "grundlage": a.grundlage, "anlegen": list(a.anlegen),
                   "kennwerte": [_vorlage_dict(v) for v in a.vorlagen],
                   "erzeugnisse": {sorte: [_erzeugnis_dict(e, sorte) for e in liste]
                                   for sorte, liste in a.erzeugnisse.items()},
                   "erzeugnisquelle": a.erzeugnisquelle}
            for name, a in MATERIALARTEN.items()
        },
        "erfuellungsarten": [
            {"wert": a.value, "beschriftung": a.beschriftung} for a in Erfuellungsart
        ],
        # Je Klasse von Eintraegen, was der Kern ueber ihre Felder weiss --
        # Einheit, Grenzen, ob ganz -- und wie ein frischer Eintrag aussieht,
        # beides unter demselben Namen (:func:`klassen`). Die Oberflaeche
        # setzt an einer Vorlage nur Kennung, Name und Materialien. Bis
        # 2026-11-10 standen die Vorlagen von Hand da, unter eigenen Namen:
        # die Einwirkung einer Platte hiess dort «einwirkung», ihre Felder
        # «kombination».
        "felder": {name: feldangaben(cls) for name, cls in klassen().items()},
        "vorlagen": {name: _vorlage(cls) for name, cls in klassen().items()},
        # Was ein Nachweis aus seinem Eintrag liest, in den Gruppen seiner
        # Herleitung: die Karten seiner Maske, mit Zeichen, Beschriftung und
        # Hinweis (:func:`_vorgaben`). Bis 2026-11-20 schrieben die Masken
        # das ab.
        "vorgaben": _vorgaben(),
        # Was ein neuer Eintrag einer Liste des Projekts mitbringt -- je
        # Bauteilart und das Skript der App «Python». Eine neue Art hat ihre
        # Vorlage damit von selbst. Dazu ein neues Projekt der Mappe
        # (:func:`_neues_projekt`).
        "neu": {**{liste: _vorlage(klasse) for liste, (klasse, _) in APPLISTEN.items()},
                "projekte": _neues_projekt()},
        # Wie ein neuer Eintrag einer App heisst, vor seiner Nummer: «Platte 1»
        # -- und ein neues Projekt der Mappe.
        "staemme": {**{liste: klasse.STAMM for liste, (klasse, _) in APPLISTEN.items()},
                    "projekte": Projekt.STAMM},
        # Welche Felder eines neuen Eintrags das erste Material welcher Art
        # nehmen -- «+» setzt sie, wie die Sandbox im Kern
        # (:attr:`~opencivil.projekt.eintraege.Beschreibung.ERSTE_MATERIALIEN`).
        "erste_materialien": {liste: dict(klasse.ERSTE_MATERIALIEN)
                              for liste, (klasse, _) in APPLISTEN.items()},
        # Die Wahlen einer Durchstanzstelle -- je ein Schalter -- und welche
        # Felder der Nachweis mit jeder Stellung liest.
        "durchstanzen": durchstanzdaten.wahlen(),
        # Wie eine Decke die Last auf ihre zwei Richtungen aufteilt -- und
        # womit die Kennungen ihrer Teile beginnen, je Liste.
        "decke": {
            "vorsilben": dict(DECKENVORSILBEN),
            "aufteilungen": [{"wert": a.value, "beschriftung": _AUFTEILUNGEN[a][0],
                              "titel": _AUFTEILUNGEN[a][1]} for a in Aufteilung],
            # Was ein Ergebnisbild zeigt -- kurz im Schalter, lang ueber dem
            # Bild; ``unterzug``, ob es das eines Unterzugs ist.
            "diagrammgroessen": [{"wert": wert, "beschriftung": _DECKENGROESSEN[wert][0],
                                  "titel": _DECKENGROESSEN[wert][1],
                                  "unterzug": wert in BALKENGROESSEN} for wert in DECKENGROESSEN],
        },
        # Wie ein Fundament der Setzung folgt -- und wo darum gerechnet wird.
        "setzung": {
            "steifigkeiten": [{"wert": s.value, "beschriftung": s.beschriftung}
                              for s in Steifigkeit],
        },
        # Wie ein Boden trägt -- der Schalter, den Pfahl und Grundbruch teilen.
        "verhalten": [{"wert": w.value, "beschriftung": w.beschriftung, "titel": w.erklaerung}
                      for w in Verhalten],
        # Die Wahlen eines Pfahls -- je ein Schalter, das Wort auf dem Knopf,
        # die Erklärung darüber --, bei der Grundlage dazu, ob R_a,k aus einem
        # Versuch kommt. Den Grenzwert von eta_a sagt sein Feld (``vorgaben``).
        "pfahl": {
            **{name: [{"wert": w.value, "beschriftung": w.beschriftung, "titel": w.erklaerung}
                      for w in wahl]
               for name, wahl in (("arten", Pfahlart), ("spitzen", Spitze),
                                  ("abscheren", Abscheren), ("tragglieder", Tragglied),
                                  ("mantel", Mantel), ("koepfe", Kopf))},
            "grundlagen": [{"wert": g.value, "beschriftung": g.beschriftung,
                            "titel": g.erklaerung, "versuch": g.aus_versuch}
                           for g in Grundlage],
        },
        # Die Wahlen eines Gebaeudes im Erdbeben -- je ein Schalter, das Wort
        # auf dem Knopf, darueber, was es heisst und gibt --, dazu je
        # Regelmaessigkeit ihre Kriterien in eigenen Worten.
        "erdbeben": {
            "zonen": [{"wert": z.value, "beschriftung": z.value,
                       "titel": f"Zone {z.value}: a_gd = {z.a_gd:.1f} m/s²"} for z in Erdbebenzone],
            "baugrund": [{"wert": b.value, "beschriftung": b.value, "titel": b.erklaerung}
                         for b in Baugrundklasse],
            "bauwerksklassen": [{"wert": b.value, "beschriftung": b.value,
                                 "titel": f"{b.erklaerung} – γ_f = {b.gamma_f:.1f}"}
                                for b in Bauwerksklasse],
            "schwingzeiten": [{"wert": s.value, "beschriftung": s.beschriftung,
                               "titel": s.erklaerung} for s in Schwingzeit],
            "lagen": [{"wert": l.value, "beschriftung": l.beschriftung, "titel": l.erklaerung}
                      for l in Wandlage],
            "regelmaessigkeit": [r.als_dict() for r in ersatzkraft.REGELMAESSIG],
        },
        # Die Wahlmoeglichkeiten der Querschnittsanalyse, mit Beschriftung.
        "querschnittsanalyse": {
            "linienarten": [
                # «Fläche» ist im Zeichenfenster die Betonfläche -- die
                # Stahlfläche einer Linie heisst darum «verschmiert».
                {"wert": Linienart.FLAECHE.value, "beschriftung": "verschmiert"},
                {"wert": Linienart.ANZAHL.value, "beschriftung": "Anzahl"},
                {"wert": Linienart.TEILUNG.value, "beschriftung": "Teilung"},
            ],
            # Wie die Flaeche einer verschmierten Linie angegeben ist.
            "verschmierungen": [{"wert": wert, "beschriftung": _VERSCHMIERUNGEN[wert][0],
                                 "titel": _VERSCHMIERUNGEN[wert][1]} for wert in VERSCHMIERT],
            "werkstoffsaetze": _WERKSTOFFSAETZE,
            "schnitte": list(SCHNITTE),
            # Die Seiten, die ein positives Moment einer Analyse zieht -- und
            # wie dann ihre Raender heissen: der gedrueckte, der gezogene.
            "zugseiten": [{"wert": z.value, "beschriftung": z.beschriftung,
                           "pfeil": z.pfeil, "raender": list(z.raender)} for z in Zugseite],
            # Die Vorlagen mit ihren Massen -- und je eine Skizze nach
            # Vorgabe fuer das Bildchen auf ihrem Knopf. Der Achsabstand der
            # Staebe ist ein Mass aller Vorlagen.
            "vorlagen": [
                {"schluessel": v.schluessel, "name": v.name, "hat_waende": v.hat_waende,
                 "masse": [m.als_dict() for m in v.masse],
                 "skizze": v.bauen().als_dict()}
                for v in VORLAGEN
            ],
            "randabstand": RANDABSTAND.als_dict(),
            # Worin Bewehrung liegt: eine Vorlage aus anderem kommt ohne.
            "bewehrt": BEWEHRT.value,
            # Die Schalter eines Spannglieds, was seine leeren Spannungen
            # heissen und was seine Neigung -- die Regeln stehen in
            # opencivil.querschnitt.spannglieder. Je Wirkung, ob die Neigung
            # zaehlt: sonst steht an ihrem Feld, warum nicht.
            "spannglied": {
                "wirkungen": [{"wert": w.value, "beschriftung": w.beschriftung, "kurz": w.kurz,
                               "titel": w.erklaerung, "neigung": w.mit_neigung}
                              for w in Spannwirkung],
                "verbunde": [{"wert": v.value, "beschriftung": v.beschriftung, "kurz": v.kurz,
                              "titel": v.erklaerung} for v in Verbund],
                "vorgaben": dict(VORGABE_SPANNUNG),
                "neigung": dict(NEIGUNG_ERKLAERT),
            },
        },
        # Die Wahlmoeglichkeiten der Balkensysteme, eben und im Raum -- mit
        # Beschriftung und Einheit, aus der Beschreibung, die mit ihnen rechnet.
        "balkensystem": systemkatalog.katalog(BalkensystemEintrag, Balkensystem, balkendaten.EBEN),
        "balkensystem3d": systemkatalog.katalog(Balkensystem3dEintrag, Balkensystem3d,
                                                balkendaten.RAUM),
        # Die Fragen der Spannung-Dehnung-Analyse.
        "spannungsanalyse": {
            # Je Frage, welche Felder des Falls sie braucht und was ihre
            # Linie zeigt -- bis 2026-10-18 stand beides je Art in der
            # Oberflaeche (nachweise.js, spannungsbild.js).
            "arten": [{"wert": a.value, "beschriftung": a.kurz, "titel": a.beschriftung,
                       "eingaben": list(a.eingaben),
                       "groessen": diagrammdaten.liniengroessen(a)}
                      for a in Analyseart],
            # Worauf sich M und N einer Platte in y beziehen: stets auf den
            # Laufmeter, nicht auf b -- fuer den Kopf des Fensters.
            "breite_y": BREITE_Y_MM,
        },
        # Was ein Nachweis-Kapitel und eine Analyse waehlen: je Material den
        # Wertesatz, je Beton die Rechenart. Welche Arten ein Kapitel
        # anbietet, sagt sein Feld (`felder`, `wahl`); hier stehen sie alle
        # mit Namen und Bild.
        "rechenwahl": {
            "werkstoffsaetze": _WERKSTOFFSAETZE,
            "rechenarten": _rechenarten(RECHENARTEN),
        },
        # `fliessnachweis` sagt, ob diese Anforderung den Nachweis gegen
        # das Fliessen unter haeufiger Einwirkung ueberhaupt verlangt -- bei
        # normaler steht in Tabelle 17 ein Strich. Die Oberflaeche braucht
        # das, um die eingetragenen Lastfaelle nicht stillschweigend
        # wegzurechnen; die Regel selbst steht bei der Anforderung. Der
        # quasi-staendige Nachweis aus der Rissbreite laeuft immer.
        "rissanforderungen": [
            {"wert": a.value, "beschriftung": a.beschriftung,
             "fliessnachweis": a.gegen_fliessen}
            for a in Rissanforderung
        ],
        # Die lieferbaren Stabdurchmesser -- die Stufen der Durchmesserfelder
        # und die Liste, durch die die Suche geht. Eine Liste, nicht zwei.
        "durchmesser": list(DURCHMESSER),
        "suchmodi": [
            {"wert": m.value, "beschriftung": m.beschriftung}
            for m in Suchmodus
        ],
        # Die Seiten, die ein Verformungsfall ziehen kann -- mit dem Pfeil, wie
        # die Zugseite der Querschnittsanalyse.
        "verformung": {"zugseiten": [{"wert": s.value, "beschriftung": s.value,
                                      "pfeil": s.pfeil} for s in UM_Y]},
    }


def obergrenzen(projekt) -> Dict[str, str]:
    """
    Je Platte die Obergrenze der automatischen Bewehrung, fertig als Text --
    «4712 mm²/m» oder «keine». Die Oberflaeche zeigt sie neben den Eingaben,
    ohne selbst zu rechnen.
    """
    def text(grenze: float) -> str:
        return f"{grenze:.0f} mm²/m" if math.isfinite(grenze) else "keine"

    return {q.kennung: text(q.automatik_grenze.je_meter) for q in projekt.querschnitte}


def _erzeugnis_dict(erzeugnis: Erzeugnis, sorte: str) -> dict:
    """Ein Erzeugnis einer Sorte: Art, ⌀ in mm, Fläche in mm², Bezeichnung und der Modul, der gilt."""
    return {"art": erzeugnis.art.value, "beschriftung": erzeugnis.art.beschriftung,
            "durchmesser": erzeugnis.durchmesser, "flaeche": erzeugnis.flaeche,
            "bezeichnung": erzeugnis.bezeichnung(sorte), "modul": erzeugnis.modul}


def _vorlage_dict(vorlage) -> dict:
    return {
        "kurzname": vorlage.kurzname,
        "symbol": vorlage.symbol,
        "einheit": vorlage.einheit.beschriftung,
        "einheit_latex": vorlage.einheit.latex or "",
        "beschreibung": vorlage.beschreibung,
        "referenz": vorlage.referenz,
        "stellen": vorlage.stellen,
        "berechnet": vorlage.ist_berechnet,
        "aus_sorte": not vorlage.ist_berechnet and not vorlage.ist_festwert,
        # Die Grenze, wie die Felder eines Eintrags sie tragen (``felder``).
        "angabe": kennwertbereich(vorlage).angabe(),
    }


# ===========================================================================
# Werte und Protokoll
# ===========================================================================


def wert_dict(wert: Wert) -> dict:
    return {
        "id": wert.id,
        "kurzname": wert.definition.kurzname,
        "symbol": wert.symbol,
        "wert": wert.formatiert(),
        "zahl": wert.groesse.in_einheit(wert.einheit),
        # Rohzahl und Stellenzahl getrennt, damit eine Tabellenspalte feste
        # Nachkommastellen setzen kann. 'wert' streicht nachlaufende Nullen --
        # im Fliesstext richtig, in einer Zahlenkolonne nicht: dort stuende
        # sonst 205 neben 224.5.
        "stellen": wert.definition.stellen,
        "einheit": wert.einheit.beschriftung if wert.einheit.name not in ("", "-") else "",
        "einheit_latex": wert.einheit.latex or "",
        "beschreibung": wert.beschreibung,
        "referenz": wert.referenz,
        "quelle": wert.quelle.value,
        "quelle_text": wert.quelle.beschriftung,
        "herkunft": wert.herkunft or "",
        "latex": wert.zahl_latex(),
    }


def _titel_dict(block: TitelBlock) -> dict:
    return {"art": "titel", "text": block.text, "ebene": block.ebene,
            "raum": block.raum}


def _text_dict(block: TextBlock) -> dict:
    return {"art": "text", "text": block.text}


def _gleichung_dict(block: GleichungBlock) -> dict:
    eintrag = {
        "art": "gleichung",
        "latex": block.latex,
        # Fuer die Kopierknoepfe: der Block, wie er im Markdown-Bericht steht.
        "markdown": block_markdown(block),
        "titel": block.titel,
        "referenz": block.referenz,
        "wert_id": block.wert_id,
        "gruppe": block.gruppe,
    }
    # Die Seite der Formel im Notizbuch -- der Link «Formel» an der Gleichung.
    if in_sammlung(block):
        eintrag["formelseite"] = formelname(block)
    return eintrag


def _tabelle_dict(block: TabellenBlock) -> dict:
    return {
        "art": "tabelle",
        "titel": block.titel,
        "kopf": [zelle_dict(z) for z in block.kopf],
        "zeilen": [[zelle_dict(z) for z in zeile] for zeile in block.zeilen],
        "ausrichtung": block.ausrichtung,
        "latex": block.als_latex(),
        "markdown": block_markdown(block),
    }


def _hinweis_dict(block: HinweisBlock) -> dict:
    return {
        "art": "hinweis",
        "text": block.text,
        "hinweisart": block.art.value,
        "beschriftung": block.art.beschriftung,
    }


#: Je Blockart, wie die Oberflaeche sie bekommt -- jede als JSON-Objekt.
TAFEL: Tafel[dict] = {
    TitelBlock: _titel_dict,
    TextBlock: _text_dict,
    GleichungBlock: _gleichung_dict,
    TabellenBlock: _tabelle_dict,
    HinweisBlock: _hinweis_dict,
}


def protokoll_liste(protokoll: Protokoll) -> List[dict]:
    return darstellen(protokoll, TAFEL)


def kurzform_liste(protokoll: Protokoll, ziele: Sequence[str]) -> List[dict]:
    """
    Die Kurzform je Ziel (:func:`opencivil.core.kurzform.kurzform`) -- ihre
    Zeilen als Gleichungen, wie die Herleitung sie bekommt.
    """
    return [_gleichung_dict(b) for ziel in ziele for b in kurzform(protokoll, ziel)]


# ===========================================================================
# Loesung
# ===========================================================================


def loesung_dict(loesung: Loesung, aufbau: Optional[Aufbau] = None, *,
                 spannungsanalysen: Optional[dict] = None) -> dict:
    """
    Vollstaendige Abbildung eines Rechenlaufs. ``spannungsanalysen`` sind die
    Zeichendaten der Analysen, wo der Aufrufer sie schon hat -- aus dem
    Zwischenspeicher (:func:`opencivil.web.dienst.rechnen`); sonst werden sie
    hier gerechnet.
    """
    ergebnis: Dict[str, Any] = {
        "werte": {wid: wert_dict(w) for wid, w in loesung.werte.items()},
        "protokoll": protokoll_liste(loesung.protokoll),
        "reihenfolge": list(loesung.reihenfolge),
        "vollstaendig": loesung.vollstaendig,
        "fehlende": [
            {
                "id": f.id,
                "beschreibung": f.beschreibung,
                "benoetigt_von": f.benoetigt_von,
                "pfad": list(f.pfad),
                "einheit": (
                    f.definition.einheit.beschriftung
                    if f.definition and f.definition.einheit.name not in ("", "-")
                    else ""
                ),
            }
            for f in loesung.fehlende
        ],
        "nicht_berechenbar": [
            {
                "ziel": s.ziel,
                "verworfene_varianten": [
                    {"berechnung": bid, "grund": grund}
                    for bid, grund in s.verworfene_varianten
                ],
            }
            for s in loesung.nicht_berechenbar.values()
        ],
        "urteile": [
            {
                "name": u.name,
                # Namensraum des Nachweises -- danach gruppiert die Oberflaeche
                # die Zusammenfassung nach Platten.
                "raum": u.raum,
                "art": u.art,
                "fall": u.fall,
                "erfuellt": u.erfuellt,
                # Einzige Kennzahl: Widerstand/Einwirkung, ab 1 erfuellt.
                "erfuellungsgrad": u.gradtext(),
                "erfuellungsgrad_zahl": u.erfuellungsgrad.si,
                "begruendung": u.begruendung,
                "hinweis": u.hinweis,
                "einwirkung": wert_dict(u.einwirkung) if u.einwirkung else None,
                "widerstand": wert_dict(u.widerstand) if u.widerstand else None,
            }
            # Die gefuehrten: diese Liste sagt, welche Nachweise gefuehrt
            # wurden, und danach zaehlt die Anzeige oben rechts. Ein stiller
            # Nachweis stuende dort als «nicht erfuellt», waere aber in keiner
            # Tabelle zu finden. Wo er hingehoert, steht er: unter der
            # Zusammenfassung seiner Platte, als Hinweis.
            for u in loesung.gefuehrte_urteile
        ],
        "alle_nachweise_erfuellt": loesung.alle_nachweise_erfuellt,
    }
    if aufbau is not None:
        ergebnis["linien"] = diagrammdaten.linien(aufbau, loesung)
        ergebnis["werkstoffgesetze"] = werkstoffkurven.werkstoffgesetze(aufbau, loesung)
        ergebnis["querkraftkurven"] = diagrammdaten.querkraftkurven(aufbau, loesung)
        ergebnis["neigungskurven"] = diagrammdaten.neigungskurven(aufbau, loesung)
        ergebnis["spannungsanalysen"] = (
            spannungsanalysen if spannungsanalysen is not None
            else diagrammdaten.spannungsanalysen(aufbau, loesung))
        ergebnis["zusammenfassungen"] = zusammenfassungen(loesung, aufbau)
        # Je Bauteil, was seine Bilder vom Kern brauchen -- nach seiner Art
        # (zeichendaten.py). Die Verlaeufe eines Balkensystems holt eine
        # eigene Anfrage (dienst.balkensystem_verlauf).
        ergebnis["zeichendaten"] = endlich(zeichendaten(aufbau, loesung))
        ergebnis["kennzahlen"] = kennzahltabellen(aufbau, loesung)
        # Je Hinweis der Namensraum seines Eintrags: die Oberflaeche grenzt
        # ihn ein wie alles andere (kern.Warnung).
        ergebnis["warnungen"] = [w._asdict() for w in aufbau.warnungen]
        # Je Bauteil, dem fuer jeden Nachweis noch etwas fehlt, was -- die
        # Zusammenfassung sagt es an seiner Stelle (Benutzer, 2026-11-19).
        ergebnis["ohne_nachweis"] = {k: t.ohne_nachweis for k, t in aufbau.teile.items() if t.ohne_nachweis}
        ergebnis["zuordnung"] = zuordnung(aufbau)
        # Je Material und Bauteil, dem noch etwas fehlt, was -- unter seiner
        # Liste wie in der Zuordnung. Die Oberflaeche sagt es an seiner
        # Stelle, nicht nur in der Herleitung (Benutzer, 2026-11-19).
        ergebnis["unfertige"] = {liste: {} for liste in ergebnis["zuordnung"]}
        for kennung, u in aufbau.unfertige.items():
            ergebnis["unfertige"][u.liste][kennung] = {"name": u.name, "grund": u.grund}
    return ergebnis


def kennzahltabellen(aufbau: Aufbau, loesung: Loesung) -> dict:
    """
    Je Bauteil mit Kennzahlen ihre Tabelle -- dieselbe wie im Bericht
    (:func:`~opencivil.bericht.zusammenfassung.kennzahlentabelle`), mit LaTeX
    und Markdown fuer die Kopierknoepfe. Je Zeile dazu ihr Wert als Ziel des
    Auges, wie bei den Nachweisen, und ihre Erklaerung als Tooltip
    (Benutzer, 2026-11-25). Auch ohne Lastfall, darum nicht in der
    Zusammenfassung, die es nur mit Urteilen gibt. Welche Kennzahlen ein
    Bauteil hat, sagt es selbst; die meisten haben keine.
    """
    ergebnis: Dict[str, Any] = {}
    for kennung in aufbau.teile:
        zeilen = kennzahlen(aufbau, kennung, loesung)
        if not zeilen:
            continue
        tabelle = kennzahlentabelle(zeilen)
        ergebnis[kennung] = {
            **_tabelle_dict(tabelle),
            "zeilen": [{"zellen": [zelle_dict(c) for c in zellen], "ziel": wert.id,
                        "bezeichnung": k.beschriftung, "erklaerung": k.erklaerung}
                       for (k, wert), zellen in zip(zeilen, tabelle.zeilen)],
        }
    return ergebnis


def zusammenfassungen(loesung: Loesung, aufbau: Aufbau) -> dict:
    """
    Je Platte die Nachweistabelle -- Zeilen **und** ihr LaTeX.

    Was darin steht, darueber und darunter, baut
    :mod:`opencivil.bericht.zusammenfassung` -- dieselben Stuecke, die auch
    im Bericht stehen. Hier werden sie nur abgebildet; die Oberflaeche faerbt
    ein, was ``erfuellt`` sagt, und haengt die Begruendung als Tooltip an die
    Zeile.
    """
    ergebnis: Dict[str, Any] = {}
    for platte in zusammenfassen(aufbau, loesung).bauteile:
        # Ein Bauteil ohne jedes Urteil bekommt keine Tabelle -- die
        # Oberflaeche zeigt dafuer ihren eigenen Leerzustand, der Bericht
        # «Kein Nachweis geführt».
        if platte.leer:
            continue
        kopf_angaben, bewehrung = angaben(aufbau, platte.kennung, loesung)
        tabelle = nachweistabelle(platte)
        ergebnis[platte.kennung] = {
            "kopf": [zelle_dict(k) for k in tabelle.kopf],
            "zeilen": [
                {
                    "zellen": [zelle_dict(c) for c in zellen],
                    "erfuellt": z.urteil.erfuellt,
                    "begruendung": z.urteil.begruendung,
                    # Nur was die Pruefung ausdruecklich meldet -- siehe
                    # NachweisUrteil.hinweis.
                    "hinweis": z.urteil.hinweis,
                    # Womit sich genau dieser Nachweis nachrechnen laesst --
                    # und wie er dann heisst.
                    "ziel": z.urteil.ziel,
                    "bezeichnung": z.bezeichnung,
                }
                for z, zellen in zip(platte.zeilen, tabelle.zeilen)
            ],
            "grad_spalte": GRAD_SPALTE,
            "stapel_spalten": list(STAPEL_SPALTEN),
            "ausrichtung": tabelle.ausrichtung,
            "latex": tabelle.als_latex(),
            "markdown": block_markdown(tabelle),
            "hinweise": hinweise(platte),
            "angaben": _gleichung_dict(kopf_angaben),
            "bewehrung": _tabelle_dict(bewehrung) if bewehrung is not None else None,
            # Der Grad kommt fertig gesetzt: welche Stelle noetig ist, damit
            # er dem Wort «nicht erfuellt» nicht widerspricht, weiss hier
            # dieselbe Stelle wie fuer die Tabelle.
            "stille": [
                {"nachweis": z.nachweis, "fall": z.fall,
                 "grad": z.urteil.gradtext(), "begruendung": z.urteil.begruendung,
                 "text": stiller_hinweis(z)}
                for z in platte.stille
            ],
        }
    return ergebnis


def zuordnung(aufbau: Aufbau) -> dict:
    """
    Verbindet die Kennungen der Oberflaeche mit den Wert-IDs des Rechenwerks:
    die Materialien und je Bauteilart unter ihrer Liste die Bauteile -- je
    Namensraum, Name und was :data:`_ZUORDNUNG` fuer ihre Art sagt.
    """
    ergebnis: Dict[str, Any] = {
        "materialien": {
            kennung: {
                "namensraum": stoff.id,
                "name": stoff.name,
                "art": stoff.art.value,
                "kennwerte": {
                    kurzname: definition.id
                    for kurzname, definition in stoff.definitionen.items()
                },
            }
            for kennung, stoff in aufbau.baustoffe.items()
        },
        **{art.liste: {} for art in BAUTEILE},
    }
    for teil in aufbau.bauteile():
        ergebnis[teil.art.liste][teil.kennung] = {
            "namensraum": teil.objekt.id, "name": teil.objekt.name,
            **_ZUORDNUNG.get(teil.art.name, _werte)(teil)}
    return ergebnis


def _werte(teil) -> dict:
    """Wo die Werte eines Bauteils stehen, nach Kurzname."""
    return {"werte": {k: d.id for k, d in teil.objekt.definitionen.items()}}


def _plattenzuordnung(teil) -> dict:
    qs = teil.objekt
    return {
        # Der Beton gehoert zur Platte und steht darum bei ihren
        # Abmessungen, nicht nur in der Materialliste.
        "beton": qs.beton.name,
        **_werte(teil),
        "nachweise": {
            nw.richtung.value: {
                "ziele": {n: d.id for n, d in nw.d_ausnutzung.items()},
                "eckwerte": {n: d.id for n, d in nw.d_eckwerte.items()},
            }
            for nw in teil.im_feld("nachweise")
        },
        # Durchmesser, Teilung und Stabzahl als Zahlen, nicht nur als
        # Text: das Querschnittsbild soll die tatsaechliche Teilung
        # zeichnen und nicht eine erfundene Stabzahl.
        "bewehrung": [
            {
                "lage": q.lage.nummer,
                "art": q.art.value,
                "richtung": q.lage.richtung.value,
                "stahl": q.lage.stahl.name if q.lage.stahl else "",
                "menge": q.posten.menge_text(),
                "phi": q.posten.durchmesser.in_einheit(MM),
                "abstand": (q.posten.abstand.in_einheit(MM)
                            if q.posten.abstand is not None else None),
                # anzahl ist eine blanke Zahl, keine Groesse -- Staebe
                # haben keine Einheit.
                "anzahl": q.posten.anzahl,
                "a_s_id": q.as_def.id,
                "z_id": q.z_def.id,
            }
            for q in qs.posten
        ],
    }


def _systemzuordnung(teil) -> dict:
    """Je Querschnitt eines Systems, wo A und I stehen -- und je Paar aus Querschnitt und Material EA und EI."""
    system = teil.objekt
    return {
        "querschnitte": {q: dict(werte) for q, werte in system.flaechen.items()},
        "steifigkeiten": [{"querschnitt": s.querschnitt, "material": s.material, **s.werte}
                          for s in system.steifigkeiten],
        # Je Querschnitt mit E_eq, wo es steht.
        "module": dict(system.module),
    }


#: Was eine Bauteilart in der Zuordnung mehr hat als Namensraum und Name --
#: ohne Eintrag ihre Werte (:func:`_werte`). Bis 2026-10-25 stand die
#: Zuordnung je Art von Hand da, zwei Bloecke wortgleich.
_ZUORDNUNG: Dict[str, Callable[[Any], dict]] = {
    "platte": _plattenzuordnung,
    "balkensystem": _systemzuordnung,
    "balkensystem3d": _systemzuordnung,
}
