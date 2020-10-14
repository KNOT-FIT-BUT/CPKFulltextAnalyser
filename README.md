# CPKFulltextAnalyser
Software pro doplňování informací o původcích dokumentů a dalších metadat na základě analýzy plných textů dokumentů.

# Obecné informace
Software pracuje primárně se souborem naskenovaných a pomocí OCR do textu převedených obsahů a rejstříků knih. Systém nejprve propojuje tyto záznamy s bibliografickými údaji, které jsou pro příslušné knihy k dispozici. Následně jsou identifikovány textové záznamy, v nichž se vyskytují známá křestní jména a příjmení. Tento krok je motivován snahou nalézt obsahy, které odpovídají knihám, složeným z příspěvků konkrétně jmenovaných autorů (a oddělit je od obsahů knih, uvádějících pouze seznamy kapitol).
Vyhledané záznamy jsou potom upraveny tak, aby text co nejlépe odrážel původní vizuální podobu zdrojového dokumentu (jednotlivé části obsahu na samostatných řádcích, případně identifikace bloků oddělujících seznam autorů od názvu kapitoly, jejího číselného označení, čísla strany apod.). V této fázi jsou také oddělovány záznamy, odpovídající strukturou rejstříkům, od klasických (sborníkových) obsahů.
Dalším krokem zpracování je potom klasifikace jednotlivých řádků obsahů podle typů informací, které obsahuje. V některých případech je bohužel i v rámci jednoho řádku smíšeno několik typů informací, např. je bez oddělovače spojen český a cizojazyčný název příspěvku/kapitoly. Pokud je dále hranice mezi jednotlivými částmi obsahu indikována speciální formou (např. seznam autorů končí dvojtečkou), je v této fázi vyznačen předpokládaný typ obou částí a forma oddělení.
V posledním kroku jsou jednotlivé oddělené části finálně klasifikovány, pomocí předpřipravených šablon jsou namapovány jednotlivé části a na základě kontextu je rozhodnuto o přiřazení kategorií nerozlišených řádků (např. když z předchozího zpracování nebylo jasné, zda se jedná o jméno autora či název příspěvku o daném člověku). Obdobně je postupováno při rozdělení řádků uvádějících více autorů, které se mohou lišit pořadím či zkracováním křestních jmen, oddělováním jednotlivých autorů atd. Výsledné záznamy jsou potom uloženy ve strukturované formě a mohou být využity pro vyhledávání v CPK.

## Závislosti
Pro správnou funkčnost je nutné doinstalovat následující závislosti:
* numpy
* python_dateutil
* sources
* pattern
* swig

Pro instalaci je možné použít nástroj pip (pip3), například takto:

    pip install numpy

Dále je nutné mít nainstalovaný swig (http://www.swig.org). Pokud máte některou z linuxových distribucí je možné, že jej lze nainstalovat pomocí vašeho package manageru:

    sudo apt install swig

nebo

    sudo yum install swig

## Nástroj process_okcz.sh

Shellový skript process_okcz.sh slouží k analýze dat z databáze obálek knih. Skript dokáže pro daný z databáze obálek knih najít další významná jména osob (mohou mezi nimi být i další autoři). Pro svou funkci vyžaduje přítomnost souborů `okcz_toc.xml`, `export_mzk.mrc` a `export_nkp.mrc`. Tyto soubory musí být umístěny ve stejném adresáři jako skript.

* Soubor **okcz_toc.xml** je XML soubor obsahující data ze serveru obalkyknih.cz.
* Soubor **export_mzk.mrc** je soubor obsahující záznamy z knihovny MZK ve formátu MARC 21.
* Soubor **export_nkp.mrc** je soubor obsahující záznamy z knihovny NKP ve formátu MARC 21.

```
 použití: ./process_okcz.sh [ -h | -p | -m | -s FILE_NAME | -a FILE_NAME | -r | -x]

	-h Vypise tuto napovedu.
	-p Provede predzpracovani dat. Muze trvat nekolik hodin.
	-m Vypise seznam nazvu souboru razenych dle cetnosti vyskytu jmen.
	-s FILE_NAME Vypise nalezene MARC21 zaznamy pro zaznam v souboru FILE_NAME.
	-a FILE_NAME Vypise nalezena jmena z obsahu knihy pro zaznam v souboru FILE_NAME.
	-r Smaze docasne predzpracovane soubory.
	-x Hromadne zpracovani vsech zaznamu z okcz_toc.xml.
```

Při použití programu je nejprve potřeba předzpracovat všechny vstupní soubory (okcz_toc.xml, export_mzk.mrc a export_nkp.mrc). Toto předzpracování se spouští parametrem `-p` a může trvat i několik hodin.

Příklad spouštění:
```
./process_okcz.sh -p
```

Při spuštění programu s parametrem `-m` dojde k vypsání názvů souborů (dokumentů z okcz_toc.xml), které obsahují nejvíce výskytů jmen. Názvy těchto souborů mohou být následně použity v dalších režimech programu pro získání relevantních informací. Výstupem je jednoduchý textový formát o dvou sloupcích, kde je v prvním sloupci uveden příslušný název souboru a ve druhém sloupci pak počet výskytů jmen osob v souboru.

Příklad spouštění:
```
./process_okcz.sh -m
```

Příklad výstupu:
```
xx133891	1715
xx232560	1711
xx165406	1332
xx232574	1101
xx45794	987
xx23446	978
xx122127	947
xx54321	899
xx171266	889
xx50876	881
...
```

Při spuštění programu s parametrem `-s` dojde k vypsání záznamů pro danou knihu ze souborů export_mzk.mrc a export_nkp.mrc. Jako parametr FILE_NAME je potřeba zadat jméno souboru získané pomocí parametru `-m`. Mapování identifikátorů uvedených v souboru okcz_toc.xml na identifikátory v souborech export_mzk.mrc a export_nkp.mrc není 100%, proto je možné, že daný záznam vypsán nebude. Mapování probíhá podle následujících pravidel.

* `isbn` - marc pole `020` podpole `$a`, v obálkách `<ean13>`
* `cbn` - marc pole `015` podpole `$a`, v obálkách `<cnb>`
* `oclc` - marc pole `035` podpole `$a`, v obálkách `<oclc>`

Výstupem je knihovnický záznam/záznamy ve formátu MARC 21 odpovídající dané knize z databáze obálek.

Příklad spouštění:
```
./process_okcz.sh -s xx100724
```

Příklad výstupu:
```
=== ID zaznamu v souboru okcz_toc.xml ===
116399657
=== Odpovidajici ID zaznamu v souboru export_nkp.mrc ===
zpk20142603114
=== Odpovidajici zaznam v souboru export_nkp.mrc ===
zpk20142603114 LDR   L 00000nam a2200000 a 4500
zpk20142603114 001   L zpk20142603114
zpk20142603114 003   L CZ PrNK
zpk20142603114 005   L 20150409110403.0
zpk20142603114 007   L ta
zpk20142603114 008   L 150319s2013    ru ach e      000 0bruso 
zpk20142603114 020   L $$a978-5-94881-227-4$$q(brož.)
zpk20142603114 040   L $$aABA001$$bcze
zpk20142603114 043   L $$ae-ru---
zpk20142603114 045   L $$aw8x4
zpk20142603114 072 7 L $$a75$$xMalířství$$2Konspekt$$921
zpk20142603114 072 7 L $$a929$$xBiografie$$2Konspekt$$98
zpk20142603114 080   L $$a75.071.1$$2MRF
zpk20142603114 080   L $$a929$$2MRF
zpk20142603114 080   L $$a75(470+571)$$2MRF
zpk20142603114 080   L $$a75.036/.038$$2MRF
zpk20142603114 080   L $$a(470+571)$$2MRF
zpk20142603114 080   L $$a(092)$$2MRF
zpk20142603114 1001  L $$aJevreinov, Nikolaj Nikolajevič,$$d1879-1953$$7js20020805712$$4aut
zpk20142603114 24510 L $$aNesterov /$$cočerk N. N. Jevreinova
zpk20142603114 260   L $$aMoskva :$$bNovyj chronograf,$$c2013
zpk20142603114 300   L $$a82 s., xxx s. :$$bil., portréty, faksim. ;$$c18 cm
zpk20142603114 500   L $$a2000 výt.
zpk20142603114 500   L $$aNa tit. s. uvedeno původní nakl.: Peterburg : Tret'ja Straža, 1922
zpk20142603114 504   L $$aObsahuje bibliografické odkazy
zpk20142603114 60017 L $$aNesterov, Michail Vasil‘jevič,$$d1862-1942$$7jx20070528021$$2czenas
zpk20142603114 648 4 L $$a1886-1942
zpk20142603114 648 7 L $$a19.-20. století$$7ch757015$$2czenas
zpk20142603114 65007 L $$amalíři$$7ph122596$$zRusko$$y19.-20. století$$2czenas
zpk20142603114 65007 L $$aruské malířství$$7ph125341$$y19.-20. století$$2czenas
zpk20142603114 65007 L $$amoderní malířství$$7ph122940$$zRusko$$2czenas
zpk20142603114 655 7 L $$abiografie$$7fd131909$$2czenas
zpk20142603114 910   L $$aABA001
zpk20142603114 990   L $$aBK
zpk20142603114 996   L $$b1002933199$$cG 211641$$lSKLAD V REKONSTRUKCI$$rsklad$$sN$$n5$$w002603892$$u000010$$jNKC50$$tABA001.NKC01002603114.NKC50002603892000010
zpk20142603114 998   L $$ahttp://aleph.nkp.cz/F/?func=direct&doc_number=002603114&local_base=NKC
zpk20142603114 OAI   L $$aNKC01-002603114
...
```

Při spuštění programu s parametrem `-a` dojde pro danou knihu k vypsání nalezených jmen osob, která jsou doporučena k přidání do knihovnického záznamu. Jako parametr FILE_NAME je potřeba zadat jméno souboru získané pomocí parametru `-m`. Ze seznamu jmen jsou automaticky odstraněna jména, která se již v knihovnických záznamech, tedy v souborech export_mzk.mrc a export_nkp.mrc, vyskytují. Výstupem je jednoduchý textový formát o dvou sloupcích, kde je v prvním sloupci uvedeno jméno osoby a ve druhém sloupci její skóre.

Příklad spouštění:
```
./process_okcz.sh -a xx100912
```

Příklad výstupu:
```
=== Jmeno autora v souboru export_mzk.mrc ===
Pavel Hlaváček
=== Jmeno autora v souboru export_nkp.mrc ===
Pavel Hlaváček
=== Nejvyznamnejsi nalezena jmena ===
Petr Jurek	2
Jiří Zákravsky	2
Linda Piknerovd	1
David Sane	1
...
```

Při spuštění programu s parametrem `-x` dojde k hromadnemu zpracování všech záznamů z okcz_toc.xml. Jednotlivé výstupní soubory jsou ukládány do adresáře `final` a de facto obsahují pro každý záznam stejné informace, které se dají získat pomocí přepínačů `-s` a `-a`.

Příklad spouštění:
```
./process_okcz.sh -x
```

Příklad výstupu (soubor `xx100912`):
```
=== ID zaznamu v souboru okcz_toc.xml ===
116095671
=== Odpovidajici ID zaznamu v souboru export_mzk.mrc ===
nkc20152683385
=== Odpovidajici ID zaznamu v souboru export_nkp.mrc ===
nkc20152683385
=== Odpovidajici zaznam v souboru export_mzk.mrc ===
nkc20152683385 LDR   L 00000nam a2200000 a 4500
nkc20152683385 001   L nkc20152683385
nkc20152683385 003   L CZ PrNK
nkc20152683385 005   L 20160129091627.0
nkc20152683385 007   L ta
nkc20152683385 008   L 150311s2014    xr     f      001 0 cze
nkc20152683385 015   L $$acnb002683385
nkc20152683385 020   L $$a978-80-7363-678-4$$q(brož.)
nkc20152683385 035   L $$a(OCoLC)908821959
nkc20152683385 040   L $$aOLA001$$bcze
nkc20152683385 0410  L $$acze$$beng
nkc20152683385 072 7 L $$a328$$xZastupitelské orgány. Vlády. Politické systémy jednotlivých zemí$$2Konspekt$$915
nkc20152683385 080   L $$a342.5$$2MRF
nkc20152683385 080   L $$a328/329$$2MRF
nkc20152683385 080   L $$a(100=111)$$2MRF
nkc20152683385 080   L $$a(048.8:082)$$2MRF
nkc20152683385 080   L $$a(078.7)$$2MRF
nkc20152683385 1001  L $$aHlaváček, Pavel,$$d1980-$$7js20061013003$$4aut
nkc20152683385 24510 L $$aPolitické systémy anglosaských zemí /$$cPavel Hlaváček, Petr Jurek a kol.
...
=== Odpovidajici zaznam v souboru export_nkp.mrc ===
nkc20152683385 LDR   L 00000nam a2200000 a 4500
nkc20152683385 001   L nkc20152683385
nkc20152683385 003   L CZ PrNK
nkc20152683385 005   L 20160129091627.0
nkc20152683385 007   L ta
nkc20152683385 008   L 150311s2014    xr     f      001 0 cze
nkc20152683385 015   L $$acnb002683385
nkc20152683385 020   L $$a978-80-7363-678-4$$q(brož.)
nkc20152683385 035   L $$a(OCoLC)908821959
nkc20152683385 040   L $$aOLA001$$bcze
nkc20152683385 0410  L $$acze$$beng
nkc20152683385 072 7 L $$a328$$xZastupitelské orgány. Vlády. Politické systémy jednotlivých zemí$$2Konspekt$$915
nkc20152683385 080   L $$a342.5$$2MRF
nkc20152683385 080   L $$a328/329$$2MRF
nkc20152683385 080   L $$a(100=111)$$2MRF
nkc20152683385 080   L $$a(048.8:082)$$2MRF
nkc20152683385 080   L $$a(078.7)$$2MRF
nkc20152683385 1001  L $$aHlaváček, Pavel,$$d1980-$$7js20061013003$$4aut
nkc20152683385 24510 L $$aPolitické systémy anglosaských zemí /$$cPavel Hlaváček, Petr Jurek a kol.
...
=== Jmeno autora v souboru export_mzk.mrc ===
Pavel Hlaváček
=== Jmeno autora v souboru export_nkp.mrc ===
Pavel Hlaváček
=== Nejvyznamnejsi nalezena jmena ===
Petr Jurek      2
Jiří Zákravsky  2
Linda Piknerovd 1
David Sane      1
```

## add_wiki_links.sh

Spouští přiřazování URL z wikipedie k záznamům národních autorit.

Výstupem je tsv soubor se záznamy autorit, doplněnými o URL wikipedie.

Průběh:

Předpokládá se, že stažené xml soubory národních autorit, budou v adresáři records. XML soubory jsou převedeny na tsv pomocí nástroje parseXML.py.
Poté se spustí skript start.sh ve složce kb_creation, který stáhne aktuální verzi KB z wikipedie, uloženou na serveru athena3.fit.vutbr.cz a připraví soubory ke sloučení do nové KB.
Sloučení probíhá pomocí kb_compare.py. Všechny potřebné konfigurace jsou ve složce kb_creation.

Spuštění:
```
./start.sh
```

Výstupní soubory KB.tsv, entitiesWithAddedWikipediaLink.tsv, geoKB.tsv a geoEntitiesWithAddedWikipediaLink.tsv jsou umístěny ve složce kb_creation.
Soubor KB.tsv obsahuje celou KB osob z databáze národních autorit.
Soubor geoKB.tsv obsahuje KB geografických lokalit z databáze národních autorit.
KB jsou vytvořeny pomocí kb_compare.py.
Soubor entitiesWithAddedWikipediaLink.tsv a geoEntitiesWithAddedWikipediaLink.tsv obsahují pouze záznamy, kde se podařilo doplnit URL wikipedie.

Příklad obsahu z KB osob:
```
p:e25388fde8	person	Atayero Aderemi Aaron-Anthony	Aderemi Aaron-Anthony Atayero		engineer		https://en.wikipedia.org/wiki/Aderemi_Aaron-Anthony_Atayero	https://www.wikidata.org/wiki/Q52423901	http://dbpedia.org/page/AAA_Atayero		Male	1969-10-26						p:Q52423901
p:58b2aaa0bf	person	A. A. Adams	A. A. Adams	American politician	politician		https://en.wikipedia.org/wiki/A._A._Adams	https://www.wikidata.org/wiki/Q19360456	http://dbpedia.org/page/A._A._Adams	wikimedia/commons/5/52/Representative_A._A._Adams,_1971.jpg	Male	1900-08-22	Bellingham	1985-06-05				p:Q19360456
p:4cfc3a1811	person	A. A. Allen	A. A. Allen	American evangelist			https://en.wikipedia.org/wiki/A._A._Allen	https://www.wikidata.org/wiki/Q4647456	http://dbpedia.org/page/A._A._Allen		Male	1911-03-27	Sulphur Rock	1970-06-11				p:Q4647456
p:271f93f45e	person	A. A. Ames	A. A. Ames	American Civil War surgeon, mob boss and politician	military physician|politician		https://en.wikipedia.org/wiki/A._A._Ames	https://www.wikidata.org/wiki/Q4647455	http://dbpedia.org/page/A._A._Ames	wikimedia/commons/6/68/Albert_Alonzo_Ames.jpg	Male	1842-01-18	Garden Prairie	1911-11-16				p:Q4647455
p:b51d18b551	person	A. Abdul Razzak	A. Abdul Razzak		athletics competitor		https://en.wikipedia.org/wiki/A._Abdul_Razzak	https://www.wikidata.org/wiki/Q45123787	http://dbpedia.org/page/A._Abdul_Razzak		Male	1932-01-01	Baghdad					p:Q45123787
...
```

Názvy jednotlivých sloupců KB osob:
```
ID
ENTITY TYPE (vždy "person")
NAME
OTHER NAME
GENERAL NOTE
ORIGINAL_WIKINAME
IMAGE
LINK (url)
GENDER
DATE OF BIRTH
PLACE OF BIRTH
DATE OF DEATH
PLACE OF DEATH
FIELD OF ACTIVITY
NATIONALITY
RELATED PLACES
RELATED COUNTRIES
NKP ID
WIKIPEDIA ID
```

Názvy jednotlivých sloupců KB lokalit:
```
ID
ENTITY TYPE (vždy "location")
NAME
ALTERNATIVE NAME
HISTORICAL NAME
ENGLISH NAME
GENERAL NOTE
COORDINATES
LATITUDE
LONGITUDE
LINK (url)
NKP ID
WIKIPEDIA ID
```

Tvorba KB osob je rozdělena na 2 části.
Nejdříve se sloučí osoby z NKP a osoby z wikipedie, které nejsou označené jako umělci.
Výsledný soubor se jmenuje personsKB.
Následně jsou do tohoto souboru sloučeni i umělci z wikipedie.
Výsledkem je KB.tsv, která obsahuje všechny osoby, včetně umělců.
 
Potřebné konfigurace pro skript kb_compare.py, pro tvorbu KB osob:
Sloučení NKP a osob z wikipedie:
```
nkp_persons_rel.conf
personsKB_output.conf
personsKB_other_output.conf
NKP.fields
PERSONS.fields
```
Sloučení předchozího a umělců z wikipedie:
```
nkp_artists_rel.conf
KB_output.conf
KB_other_output.conf
personsKB.fields
ARTISTS.fields
```

Tvorba KB geografických lokalit probíhá v jednom kroku, sloučením KB lokalit z NKP a entit typu LOCATION z KB z wikipedie. Výsledkem je geoKB.tsv.

Konfigurace pro tvorbu KB lokalit:
```
nkp_geo_rel.conf
geoKB_output.conf
geoKB_other_output.conf
GEO.fields
LOCATIONS.fields
```

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
