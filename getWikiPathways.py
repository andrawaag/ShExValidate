import pprint
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import sys
import subprocess
import os
import shlex
import json


table_data = []

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql .setQuery("""
SELECT ?pathway WHERE {
    ?pathway wdt:P2410 ?wpid .
}
LIMIT 10
""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()


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
    else:
        pprint.pprint(output)
        row=[]
        row.append("item:")
        row.append(output["node"])
        row.append("shape:")
        row.append(output["shape"])
        row.append("type:")
        row.append(output["type"])
        table_data.append(row)

        print(output["shape"]+"was applied on "+output["node"]+" resulted in "+output["type"])

        print("There are iseues on property:")
        for error in output["errors"]:
            row = []
            row.append(error["constraint"]["predicate"])
            row.append(error["type"])
            table_data.append(row)
            print(error["constraint"]["predicate"]+ " of type: "+error["type"])


print(table_data)