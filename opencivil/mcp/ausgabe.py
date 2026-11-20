"""
opencivil/mcp/ausgabe.py -- was die Werkzeuge als Text zurueckgeben.

Kurz und in Markdown: eine KI liest es, und ein Mensch, der mitliest, soll
es auch koennen. Die Rechnung kommt nicht als ganze Antwort des Dienstes --
beim Beispiel rund 870 kB --, sondern je Bauteil als die Tabelle seiner
Nachweise, wie die Zusammenfassung der Seite sie zeigt, mit dem, was der
Kern dazu sagt (:func:`rechnung`).
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping

from opencivil.material.arten import MATERIALARTEN
from opencivil.mcp.sitzung import LISTEN, Sitzung, kennung_im_raum, name_von
from opencivil.projekt import Projekt
from opencivil.projekt.eintraege import MaterialEintrag
from opencivil.projekt.lesen import katalogname, ort_von


def arten() -> str:
    """Die Apps: wie ``app`` sie nennt, wie ihre Felder heissen, und die Sorten der Materialien."""
    zeilen = ["Die Apps – je mit ihrer Liste, so heisst «app» in den anderen Werkzeugen, und dem "
              "Namen ihrer Felder (felder):", ""]
    for liste, klasse in LISTEN.items():
        zeilen.append(f"- {klasse.BEZEICHNUNG}: Liste «{liste}», Felder «{katalogname(klasse)}»")
    zeilen += ["", "Materialien legt material_anlegen an, je Art mit einer ihrer Sorten:"]
    zeilen += [f"- {art} ({a.titel}): {', '.join(a.anlegen)}" for art, a in MATERIALARTEN.items()]
    return "\n".join(zeilen)


def ueberblick(sitzung: Sitzung) -> str:
    """Die Mappe in einer Zeile: ihre Datei, ihre Projekte, welches gewaehlt ist."""
    mappe = sitzung.offen()
    datei = f"Datei {sitzung.pfad}" if sitzung.pfad else "noch ohne Datei"
    stand = ", ungespeichert" if sitzung.ungespeichert else ""
    projekte = ", ".join(f"«{p.name}»" + (" (gewählt)" if i == sitzung.gewaehlt else "")
                         for i, p in enumerate(mappe.projekte))
    return f"Mappe: {datei}{stand}. {_zahl(len(mappe.projekte), 'Projekt', 'Projekte')}: {projekte}."


def eintraege(sitzung: Sitzung, listen: Iterable[str]) -> str:
    """Je App die Eintraege des gewaehlten Projekts, mit Kennung -- die Sandbox heisst so."""
    projekt = sitzung.projekt
    zeilen = [f"Projekt «{projekt.name}»:"]
    for liste in listen:
        alle = getattr(projekt, liste)
        zeilen.append(f"- {LISTEN[liste].BEZEICHNUNG} ({liste}): "
                      + (", ".join(_eintrag(e) for e in alle) if alle else "noch keine"))
    return "\n".join(zeilen)


def _eintrag(e: Any) -> str:
    if isinstance(e, MaterialEintrag):
        eigen = ", eigenes" if e.eigenstaendig else ""
        return f"{name_von(e)} ({e.kennung}, {MATERIALARTEN[e.art].titel}{eigen})"
    return f"{e.name} ({e.kennung})"


def rechnung(daten: Mapping[str, Any], projekt: Projekt, nur: str = "") -> str:
    """
    Was ``rechnen`` zurueckgibt: je Bauteil von ``projekt`` die Tabelle
    seiner Nachweise aus der Antwort ``daten`` des Dienstes, darunter seine
    Hinweise -- auch, was ihm fehlt. Mit ``nur`` dieses eine Bauteil. Ein
    Material nur, wo der Kern etwas zu ihm sagt: rechnet es nicht, sagt das
    Bauteil, das es nimmt, nur «warum, steht bei ihm».
    """
    urteile = _je_eintrag(daten["urteile"])
    hinweise = _je_eintrag(daten["warnungen"])
    unfertig = {k for je_liste in daten["unfertige"].values() for k in je_liste}
    gezeigt = ([m for m in projekt.materialien if m.kennung in hinweise]
               + [e for e in projekt.bauteile() if not nur or e.kennung == nur])
    alle = [u for e in gezeigt for u in urteile.get(e.kennung, ())]
    kopf = f"# Projekt «{projekt.name}» – {_stand(alle)}"
    teile = [kopf if nur else f"{kopf}\n\nOhne die Sandboxen gerechnet, wie der Bericht."]
    for e in gezeigt:
        teile.append(_bauteil(e, daten["zusammenfassungen"].get(e.kennung), urteile.get(e.kennung, []),
                              hinweise.get(e.kennung, []), e.kennung in unfertig))
    fehlende = [f"- {f['beschreibung']} ({f['id']})" for f in daten["fehlende"]]
    if fehlende:
        teile.append("## Es fehlen Eingaben\n\n" + "\n".join(fehlende))
    return "\n\n".join(teile)


def _bauteil(e: Any, zusammenfassung: Any, urteile: List[dict], hinweise: List[dict],
             unfertig: bool) -> str:
    stand = "rechnet nicht" if unfertig else _stand(urteile)
    teile = [f"## {ort_von(e)} ({e.kennung}) – {stand}"]
    punkte = [h["text"] for h in hinweise]
    if zusammenfassung is not None:
        teile.append(zusammenfassung["markdown"])
        punkte = [*zusammenfassung["hinweise"], *(s["text"] for s in zusammenfassung["stille"]),
                  *punkte]
    if punkte:
        teile.append("\n".join(f"- {p}" for p in punkte))
    return "\n\n".join(teile)


def _stand(urteile: List[dict]) -> str:
    """«3 Nachweise, alle erfüllt», «1 von 4 Nachweisen nicht erfüllt», «kein Nachweis»."""
    if not urteile:
        return "kein Nachweis"
    nicht = sum(not u["erfuellt"] for u in urteile)
    if not nicht:
        return f"{_zahl(len(urteile), 'Nachweis', 'Nachweise')}, " + (
            "erfüllt" if len(urteile) == 1 else "alle erfüllt")
    return f"{nicht} von {_zahl(len(urteile), 'Nachweis', 'Nachweisen')} nicht erfüllt"


def _je_eintrag(stuecke: Iterable[dict]) -> Dict[str, List[dict]]:
    """Urteile oder Hinweise nach dem Eintrag, dem ihr Namensraum gehoert (``raum``)."""
    je: Dict[str, List[dict]] = {}
    for stueck in stuecke:
        je.setdefault(kennung_im_raum(stueck["raum"]), []).append(stueck)
    return je


def _zahl(n: int, einzahl: str, mehrzahl: str) -> str:
    return f"{n} {einzahl if n == 1 else mehrzahl}"
