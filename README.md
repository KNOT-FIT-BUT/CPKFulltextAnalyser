# CPKFulltextAnalyser
Software pro doplňování informací o původcích dokumentů a dalších metadat na základě analýzy plných textů dokumentů


## Nástroj pro tvorbu předmětových hesel `subject_heading.py`
Nástroj pro zadané vstupní soubory vygeneruje dle kategorií soubory s předmětovými hesly dané kategorie nalezenými v textu zdrojového souboru.

V prvním kroku jsou pomocí zmíněného nástroje v plném textu nalezeny všechny výskyty relevantních pojmenovaných entit, ke každé entitě je počítána četnost výskytu v daném souboru. Z těchto entit jsou pak pro jednotlivé kategorie vygenerovány soubory (`*.600` a `*.610`), kde na každém řádku je entita dané kategorie, entity jsou seřazeny od nejčetnějších po ty nejméně četné.

### Závislosti
* Nástroj [`CPKLinkedOpenDataLinker/ner_cz.py`](CPKLinkedOpenDataLinker/ner_cz.py) (a jeho závislosti)
* `Python3`
* Python3 modules: `datetime`, `regex`
* soubor `KB-HEAD.all` vygenerovaný pomocí [`CPKLinkedOpenDataLinker/start.sh`](CPKLinkedOpenDataLinker/start.sh)

### Možnosti spuštění nástroje
```
subject_heading.py [-h] -i INPUTS [INPUTS ...] [-o OUTPUT_DIR] [-n NER] [-p] [-d] [-x]
```

### Přehled parametrů spuštění nástroje:

Parametr | Popis parametru
----- | -----
`-h`, `--help` | Zobrazí nápovědu *(v angličtině)*.
`-i INPUTS [INPUTS ...]`, `--inputs INPUTS [INPUTS ...]` | Definice vstupních souboru pro vygenerování předmětových hesel *(lze nadefinovat více souborů za sebou nebo použít zástupný symbol `*`*).
`-o OUTPUT_DIR`, `--output_dir OUTPUT_DIR` | Určení výstupní složky, kam mají být soubory s předmětovými hesly generovány *(složky, které neexistují, budou vytvořeny)*.
`-n NER`, `--ner NER` | Cesta k `ner_cz.py` souboru *(výchozí: ner_cz.py)*.
`-p`, `--preserve-paging` | Vypne funkcionalitu, která se snaží v pracovních souborech ze jmen odstranit číslování stránek *(např. "Jan 5 Novák" => "Jan Novák")*.
`-d`, `--preserve-wordbreaking` | Vypne funkcionalitu, která se snaží v pracovních souborech odstranit rozdělení u jmen *(např. "Jan No- vák" => "Jan Novák")*.
`-x`, `--preserve-aliases` | Vypne funkcionalitu, která ignoruje jména aliasů entit *(tímto dramaticky vzroste počet false positive entit)*.