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
    ?pathway wdt:P2410 ?wpid .
}
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

htmloutput = open("/tmp/pathway_errors.html", "w")
htmloutput.write("<html><head></head><body><h1>Validation report</h1> <ul>")

def findPropertyError(error, error_report):
    if type(error) is dict:
        if "property" in error.keys():
            if error["property"] not in error_report.keys():
                error_report[error["property"]] = error["type"]
                htmloutput.write(error["type"] + ":")
                htmloutput.write(error["property"])
                print(error["property"] + ": " + error["type"])
            row = []
            row.append(error["property"])
            row.append(error["type"])
        elif "errors" in error.keys():
            for suberror in error["errors"]:
                findPropertyError(suberror, error_report)
    elif type(error) is list:
        for error_part in error:
            if "property" in error_part.keys():
                if error_part["property"] not in error_report.keys():
                    error_report[error_part["property"]] = error_part["type"]
                    htmloutput.write(error_part["type"] + ":")
                    htmloutput.write(error_part["property"]+"<br>")
                    print(error_part["property"] + ": " + error_part["type"])
                row = []
                row.append(error_part["property"])
                row.append(error_part["type"])
            elif "errors" in error.keys():
                for suberror in error_part["errors"]:
                    findPropertyError(suberror, error_report)
        #pprint.pprint(error)
    else:
        print(type(error))
   #elif type(error) is list

for result in results["results"]["bindings"]:
    wdid = result["pathway"]["value"].replace("http://www.wikidata.org/entity/", "")
    args = shlex.split(
        "/Users/andra/projects/shex.js/bin/validate "
        "-x https://github.com/shexSpec/schemas/raw/master/Wikidata/pathways/Wikipathways/wikipathways.shex "
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
        print("There are iseues on property:")
        pprint.pprint(output)
        error_report = dict()
        findPropertyError(output, error_report)

htmloutput.write("</ul></body>")
htmloutput.close()

print(table_data)