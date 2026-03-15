import requests

url = "http://localhost:8070/api/processFulltextDocument"
def get_data(file):
    with open(file, "rb") as f:
        files = {"input": f}
        data = {
            "consolidateHeader": "1",
            "consolidateCitations": "1"
        }

        r = requests.post(url, files=files, data=data)

    xml_text = r.text

    with open("result.xml", "w", encoding="utf-8") as out:
        out.write(xml_text) 

