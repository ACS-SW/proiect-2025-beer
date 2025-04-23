from rdflib import Graph, RDF, OWL

# Încarcă ontologia
def load_ontology(file_path):
    g = Graph()
    g.parse(file_path, format='xml')  # RDF/XML format
    return g

# Afișează statistici
def print_stats(g):
    # Clase definite
    classes = set(g.subjects(RDF.type, OWL.Class))
    print(f"Număr de clase OWL: {len(classes)}")
    for cls in classes:
        print(f" - Clasă: {cls}")

    # Indivizi (instanțe ale unor clase)
    individuals = set(s for s, p, o in g if p == RDF.type and o not in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty))
    print(f"\nNumăr de indivizi: {len(individuals)}")
    for ind in individuals:
        print(f" - Individ: {ind}")

if __name__ == "__main__":
    owl_path = "../onto/beer.owl"  # înlocuiește cu calea ta
    graph = load_ontology(owl_path)
    print_stats(graph)
