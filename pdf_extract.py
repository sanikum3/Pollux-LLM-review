#from grobid import get_data
from lxml import etree

def extract(name):
    #get_data("file.pdf")
    tree = etree.parse(name)
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}

    # Заголовок статьи
    try:
        title = tree.xpath(
            "//tei:titleStmt/tei:title[@type='main']/text()",
            namespaces=ns
        )[0]
    except:
        title = "No title"
    # Аннотация
    try:
        abstract = tree.xpath(
            "//tei:profileDesc//tei:abstract//tei:p//text()",
            namespaces=ns
        )
        abstract_text = " ".join(abstract)
    except:
        abstract_text = "No abstract"

    # Основные секции
    sections = []

    for div in tree.xpath("//tei:body//tei:div", namespaces=ns):
        head = div.xpath("./tei:head/text()", namespaces=ns)
        paragraphs = div.xpath(".//tei:p//text()", namespaces=ns)

        if not paragraphs:
            continue

        sections.append({
            "title": head[0] if head else "No title",
            "text": " ".join(paragraphs)
        })

    #print(title)
    #print(abstract_text) 
    #print(sections[0])
    with open("result.txt", "w", encoding="utf-8") as out:
        out.write(title+'\n')
        out.write(abstract_text+'\n')
        for i in sections:
            out.write(i['title']+'\n')
            out.write(i['text']+'\n')
            out.write('\n') 
    return "result.txt"        
