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
