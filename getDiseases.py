import requests
import pprint
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import sys
import subprocess
import os
import stat
import shlex
import json

sparql = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
sparql .setQuery("""
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX wd: <http://www.wikidata.org/entity/>
SELECT * WHERE {
   ?item wdt:P699 ?doid .
}

""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()


for result in results["results"]["bindings"]:
    wdid = result["item"]["value"].replace("http://www.wikidata.org/entity/", "")
    query = """
     CONSTRUCT {
      wd:"""
    query += wdid
    query += """ ?p ?o .
      ?o ?qualifier ?f .
      ?o prov:wasDerivedFrom ?u .
      ?u ?a ?b .
      }
    WHERE {
     wd:"""
    query += wdid
    query += """
       ?p ?o .
      optional {?o ?qualifier ?f .}
      OPTIONAL {?o prov:wasDerivedFrom ?u .
      ?u ?a ?b .}
      }
    """
    sparql.setQuery(query)
    sparql.setReturnFormat(RDF)

    wdtriples = sparql.query().convert()
    wdtriples.serialize("test.nt", format="nt")
    os.chmod("test.nt", 776)

    args = shlex.split("/Users/andra/projects/shex.js/bin/validate -x /Users/andra/projects/ShEx/wikidata/wikidata-disease.shex test.nt")
    # print(args)
    output = None
    try:
        p = subprocess.check_output(args)
    except subprocess.CalledProcessError as grepexc:
        # pprint.pprint(grepexc.output.decode("utf-8"))
        output = json.loads(grepexc.output)


    pprint.pprint(output)
    sys.exit()



