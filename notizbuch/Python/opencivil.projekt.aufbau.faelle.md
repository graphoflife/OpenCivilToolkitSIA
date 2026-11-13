---
erzeugt: c309c0c1215a
art: modul
tags: [modul]
---
> [!abstract] opencivil/projekt/aufbau/faelle.py
> was Balkensystem und Decke an Faellen gleich pruefen.
> Paket [[opencivil.projekt.aufbau]] · [Quelltext](../../opencivil/projekt/aufbau/faelle.py)

## VERANTWORTUNG

Die Regeln der Lastfaelle und Kombinationen eines Bauteils, an einer
Stelle: verschiedene Namen, hoechstens ein Lastfall mit dem Eigengewicht,
je Teil eine Kennung, eine Last ohne Lastfall bleibt weg, und die Beiwerte
einer Kombination nach den Namen ihrer Lastfaelle. Was nicht stimmt, steht
in den Meldungen des Bauteils -- ein Fehler haelt das Bauteil auf, der Rest
des Projekts rechnet weiter (bis 2026-10-15 hielten gleiche Fallnamen das
ganze Projekt auf).

## Inhalt

### doppelte_kennungen

```python
def doppelte_kennungen(was: str, liste: Sequence[Any]) -> List[Meldung]
```

Je Kennung, die mehrere Teile tragen, ein Fehler: an ihr haengen Lasten
und Verweise. Bis 2026-10-16 fiel eine Last bei zwei gleichen
Lastfall-Kennungen still in beide.

### faelle_pruefen

```python
def faelle_pruefen(lastfaelle: Sequence[LastfallEintrag], kombinationen: Sequence[LastkombinationEintrag]) -> List[Meldung]
```

Die Faelle werden an ihrem Namen erkannt, zwei gleiche waeren nicht zu
unterscheiden -- auch nicht ein Lastfall und eine Kombination. Und das
Eigengewicht gehoert in einen Lastfall, nicht in zwei.

### ohne_lastfall

```python
def ohne_lastfall(kennung: str) -> Meldung
```

Der Hinweis zu einer Last, deren Lastfall es nicht gibt: sie bleibt weg, der Rest rechnet.

### beiwerte

```python
def beiwerte(kombinationen: Sequence[LastkombinationEintrag], lastfaelle: Sequence[LastfallEintrag]) -> Tuple[List[Tuple[str, Dict[str, float]]], List[Meldung]]
```

Je Kombination ihr Name und ihre Beiwerte nach dem Namen des Lastfalls.
Ein Beiwert fuer einen Lastfall, den es nicht gibt, zaehlt nicht; ein
Hinweis sagt es.


## Braucht

- [[opencivil.projekt.faelle]]
- [[opencivil.stabwerk.system]]

## Gebraucht von

- [[opencivil.projekt.aufbau.balkensystem]]
- [[opencivil.projekt.aufbau.decke]]
