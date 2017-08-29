import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import sys
import subprocess
import os
import shlex
import json
import json2html


table_data = []

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql .setQuery("""
SELECT ?pathway WHERE {
    ?pathway wdt:P699 ?wpid .
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

htmloutput = open("/tmp/disease_errors.html", "w")
htmloutput.write("<html><head></head><body><h1>Validation report</h1> <ul>")

def findPropertyError(error):
    if type(error) is dict:
        if "property" in error.keys():
            htmloutput.write(error["type"] + ":")
            htmloutput.write(error["property"])
            print(error["property"] + ": " + error["type"])
            row = []
            row.append(error["property"])
            row.append(error["type"])
        elif "errors" in error.keys():
            for suberror in error["errors"]:
                findPropertyError(suberror)

for result in results["results"]["bindings"]:
    wdid = result["pathway"]["value"].replace("http://www.wikidata.org/entity/", "")
    args = shlex.split(
        "/Users/andra/projects/shex.js/bin/validate "
        "-x https://github.com/shexSpec/schemas/raw/master/Wikidata/genewiki/wikidata_disease.shex "
        "-d https://www.wikidata.org/wiki/Special:EntityData/"+wdid +" "+
        "-n wd:" +
        wdid )
    print(args)
    output = None
    try:
        p = subprocess.check_output(args)
    except subprocess.CalledProcessError as grepexc:
        #pprint.pprint(grepexc.output.decode("utf-8"))
        #pprint.pprint(grepexc.output)
        output = json.loads(grepexc.output)

    if output == None:
        table_data.append(["no issue with: " +wdid])
        htmloutput.write("<li><a href = \"http://www.wikidata.org/entity/"+wdid+"\">"+wdid+"</a><img src = \"https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Approve_icon.svg/200px-Approve_icon.svg.png\" width=20\">")
    else:
        #pprint.pprint(output)
        htmloutput.write("<li><a href = \"http://www.wikidata.org/entity/" + wdid + "\">" + wdid + "</a><img src = \"https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Emojione_26A1.svg/768px-Emojione_26A1.svg.png\" width=20\">")
        print("Issue with "+wdid)
        print("There are issues on property:")
        # pprint.pprint(output)
        findPropertyError(output)

htmloutput.write("</ul></body>")
htmloutput.close()

print(table_data)