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

Shellový skript process_okcz.sh slouží k analýze dat z databáze obálek knih. Skript dokáže pro danou obálku najít další autory dané knihy/sborníku (pokud existují). Pro svou funkci vyžaduje přítomnost souborů `okcz_toc.xml`, `export_mzk.mrc` a `export_nkp.mrc`. Tyto soubory musí být umístěny ve stejném adresáři jako skript.

* Soubor **okcz_toc.xml** je XML soubor obsahující data ze serveru obalkyknih.cz.
* Soubor **export_mzk.mrc** je soubor obsahující záznamy z knihovny MZK ve formátu MARC 21.
* Soubor **export_nkp.mrc** je soubor obsahující záznamy z knihovny NKP ve formátu MARC 21.

```
 použití: process_okcz.sh [ -h ] [ -p ] [ -m ] [ -s FILE_NAME ] [ -a FILE_NAME]

       -h   Vypise tuto napovedu.
       -p   Provede predzpracovani dat. Muze trvat nekolik hodin.
       -m   Vypise seznam nazvu souboru razenych dle cetnosti vyskytu jmen.
       -s FILE_NAME   Vypise MARC21 zaznamy pro dany soubor.
       -a FILE_NAME   Vypise nalezena jmena z obsahu knihy.
```

Při použití programu je nejprve potřeba předzpracovat všchny vstupní soubory (okcz_toc.xml, export_mzk.mrc a export_nkp.mrc). Toto předzpracování se spouští parametrem `-p` a může trvat i několik hodin.

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
./process_okcz.sh -s xx133891
```

Příklad výstupu:
```
nkc20061662268 LDR   L 00000nam a2200000 aa4500
nkc20061662268 001   L nkc20061662268
nkc20061662268 003   L CZ PrNK
nkc20061662268 005   L 20130711142022.0
nkc20061662268 007   L ta
nkc20061662268 008   L 060630m20042006xr ac  e      001 0 cze  
nkc20061662268 015   L $$acnb001662268
nkc20061662268 020   L $$a80-7182-156-X$$q(1. díl :$$qOlomouc :$$qbrož.)
nkc20061662268 020   L $$a80-7182-206-X$$q(2. díl :$$qOlomouc :$$qbrož.)
nkc20061662268 035   L $$a(OCoLC)63295689
nkc20061662268 040   L $$aABA001$$bcze
nkc20061662268 043   L $$ae-xr---$$be-xr-ol$$2czenas
nkc20061662268 072 7 L $$a82$$xLiteratura. Literární život$$2Konspekt$$911
nkc20061662268 080   L $$a82-027.22$$2MRF
nkc20061662268 080   L $$a82:316.3$$2MRF
nkc20061662268 080   L $$a316.72/.75$$2MRF
nkc20061662268 080   L $$a(437.325)$$2MRF
nkc20061662268 080   L $$a(082)$$2MRF
nkc20061662268 24500 L $$aZ paměti literární Olomouce :$$bsborník memoárů, statí a příležitostných textů /$$ceditor Bohumír Kolář
nkc20061662268 250   L $$a1. vyd.
nkc20061662268 260   L $$aOlomouc :$$bVlastivědná společnost muzejní,$$c2004-2006
nkc20061662268 300   L $$a2 sv. (276, 446 s.) :$$bil., portréty ;$$c23 cm
nkc20061662268 500   L $$aVydáno v Nakladatelství Olomouc
nkc20061662268 504   L $$aObsahuje bibliografie, bibliografické odkazy a rejstřík
nkc20061662268 65007 L $$aliterární život$$7ph122405$$zČesko$$2czenas
nkc20061662268 65007 L $$aliteratura a společnost$$7ph122371$$zČesko$$2czenas
nkc20061662268 65007 L $$akultura a společnost$$7ph122010$$zČesko$$2czenas
nkc20061662268 65009 L $$aliterary life$$zCzechia$$2eczenas
nkc20061662268 65009 L $$aliterature and society$$zCzechia$$2eczenas
nkc20061662268 65009 L $$aculture and society$$zCzechia$$2eczenas
nkc20061662268 655 7 L $$asborníky$$7fd163935$$2czenas
nkc20061662268 655 9 L $$amiscellanea$$2eczenas
nkc20061662268 651 7 L $$aOlomouc (Česko : oblast)$$7ge128534$$2czenas
nkc20061662268 651 9 L $$aOlomouc Region (Czechia)$$2eczenas
nkc20061662268 7001  L $$aKolář, Bohumír,$$d1932-$$7jn20020618008$$4edt
nkc20061662268 9102  L $$aBOA001$$b2-1141.997$$s1-2$$tv
nkc20061662268 9289  L $$aVlastivědná společnost muzejní Olomouc
nkc20061662268 9289  L $$aNakladatelství Olomouc
nkc20061662268 990   L $$aBK
nkc20061662268 995   L $$a01
nkc20061662268 991   L $$b200608$$cNOV
nkc20061662268 9966  L $$b2610232750$$c2-1141.997$$d1. díl$$v1$$lMZK$$rSklad / do 1 hodiny$$n0$$pp.v.$$w000748629$$u000010$$a1$$eBOA001$$jMZK50$$sP
nkc20061662268 9966  L $$b2610285709$$c2-1141.997$$d2. díl$$v2$$lMZK$$rSklad / do 1 hodiny$$n0$$pp.v.$$w000748629$$u000020$$a1$$eBOA001$$jMZK50$$sP
nkc20061662268 9967  L $$b2610294111$$c2-1141.997$$d1. díl$$v1$$lVol.výběr$$rVV 1p$$n3$$pkup$$h821.162.3 KOL$$w000748629$$u000050$$a1$$eBOA001$$jMZK50$$sA
nkc20061662268 9967  L $$b2610294112$$c2-1141.997$$d1. díl$$v1$$lVol.výběr$$rVV 1p$$n4$$pkup$$h821.162.3 KOL$$w000748629$$u000060$$a1$$eBOA001$$jMZK50$$sA
nkc20061662268 9967  L $$b2610294113$$c2-1141.997$$d2. díl$$v2$$lVol.výběr$$rVV 1p$$n6$$pkup$$h821.162.3 KOL$$w000748629$$u000030$$a1$$eBOA001$$jMZK50$$sA
nkc20061662268 9967  L $$b2610294114$$c2-1141.997$$d2. díl$$v2$$lVol.výběr$$rVV 1p$$n3$$pkup$$h821.162.3 KOL$$w000748629$$u000040$$a1$$eBOA001$$jMZK50$$sA
nkc20061662268 OAI   L $$aMZK01-000748629
...
```

Při spuštění programu s parametrem `-a` dojde pro danou knihu k vypsání nalezených jmen osob, která jsou doporučena k přidání do knihovnického záznamu. Jako parametr FILE_NAME je potřeba zadat jméno souboru získané pomocí parametru `-m`. Ze seznamu jmen jsou automaticky odstraněna jména, která se již v knihovnických záznamech, tedy v souborech export_mzk.mrc a export_nkp.mrc, vyskytují. Výstupem je jednoduchý textový formát o dvou sloupcích, kde je v prvním sloupci uvedeno jméno osoby a ve druhém sloupci její skóre.

Příklad spouštění:
```
./process_okcz.sh -a xx133891
```

Příklad výstupu:
```
Bohumír Kolář	28
František Všetička	17
Eliška Blažejová	6
Bohuslav Smejkal	6
Vladimíra Cetkovská	5
Stanislav Komenda	4
Ladislav Zelina	4
František Valouch	4
Vladimír Zicháček	3
Pavel Marek	3
...
```

## start.sh

Spouští přiřazování URL z wikipedie k záznamům národních autorit.

Výstupem je tsv soubor se záznamy autorit, doplněnými o URL wikipedie.

Průběh:
Předpokládá se, že stažené xml soubory národních autorit budou v adresáři records. XML soubory jsou převedeny na tsv pomocí nástroje parseXML.py.
Poté spouští skript start.sh ve složce kb_creation, který stáhne aktuální verzi KB z wikipedie uloženou na serveru athena3.fit.vutbr.cz a připraví soubory ke sloučení do nové KB.
Sloučení probíhá pomocí kb_compare.py. Všechny potřebné konfigurace jsou ve složce kb_creation.

Spuštění:
```
./start.sh
```

Výstupní soubory KB.tsv a entitiesWithAddedWikipediaLink.tsv jsou umístěny ve složce kb_creation.
Soubor KB.tsv obsahuje celou KB vytvořenou pomocí kb_compare.py.
Soubor entitiesWithAddedWikipediaLink.tsv obsahuje pouze záznamy, kde se podařilo doplnit URL wikipedie.
Příklad obsahu:
```
p:e25388fde8	person	Atayero Aderemi Aaron-Anthony	Aderemi Aaron-Anthony Atayero		engineer		https://en.wikipedia.org/wiki/Aderemi_Aaron-Anthony_Atayero	https://www.wikidata.org/wiki/Q52423901	http://dbpedia.org/page/AAA_Atayero		Male	1969-10-26						p:Q52423901
p:58b2aaa0bf	person	A. A. Adams	A. A. Adams	American politician	politician		https://en.wikipedia.org/wiki/A._A._Adams	https://www.wikidata.org/wiki/Q19360456	http://dbpedia.org/page/A._A._Adams	wikimedia/commons/5/52/Representative_A._A._Adams,_1971.jpg	Male	1900-08-22	Bellingham	1985-06-05				p:Q19360456
p:4cfc3a1811	person	A. A. Allen	A. A. Allen	American evangelist			https://en.wikipedia.org/wiki/A._A._Allen	https://www.wikidata.org/wiki/Q4647456	http://dbpedia.org/page/A._A._Allen		Male	1911-03-27	Sulphur Rock	1970-06-11				p:Q4647456
p:271f93f45e	person	A. A. Ames	A. A. Ames	American Civil War surgeon, mob boss and politician	military physician|politician		https://en.wikipedia.org/wiki/A._A._Ames	https://www.wikidata.org/wiki/Q4647455	http://dbpedia.org/page/A._A._Ames	wikimedia/commons/6/68/Albert_Alonzo_Ames.jpg	Male	1842-01-18	Garden Prairie	1911-11-16				p:Q4647455
p:b51d18b551	person	A. Abdul Razzak	A. Abdul Razzak		athletics competitor		https://en.wikipedia.org/wiki/A._Abdul_Razzak	https://www.wikidata.org/wiki/Q45123787	http://dbpedia.org/page/A._Abdul_Razzak		Male	1932-01-01	Baghdad					p:Q45123787
...
```

Potřebné konfigurace pro skript kb_compare.py:
```
KB_output.conf
KB_other_output.conf
NKP.fields
PERSONS.fields
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
