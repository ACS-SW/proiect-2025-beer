from rdflib import Graph, Namespace, RDF, RDFS, OWL

# Încarcă graful RDF din fișier
g = Graph()
g.parse("./onto/beer_ontology_extended.owl", format="xml")

# Definește namespace-uri
BEER = Namespace("http://example.org/beer#")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
g.bind("beer", BEER)

print("\n=== Tipuri de bere (subClassOf Beer) ===")
for s, p, o in g.triples((None, RDFS.subClassOf, BEER.Beer)):
    print(f"- {s.split('#')[-1]} este un tip de Beer")

print("\n=== Instanțe de bere ===")
for s, p, o in g.triples((None, RDF.type, None)):
    if isinstance(o, Namespace) or "beer#" in str(o):
        print(f"- {s.split('#')[-1]} este de tip {o.split('#')[-1]}")

print("\n=== Linkuri externe (sameAs) ===")
for s, p, o in g.triples((None, OWL.sameAs, None)):
    print(f"- {s.split('#')[-1]} este același cu: {o}")
