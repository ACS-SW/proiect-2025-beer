from rdflib import Graph, Namespace, RDF, RDFS, OWL

def create_ontology_structure(output_path):
    g = Graph()
    EX = Namespace("http://example.org/beer#")
    g.bind("ex", EX)

    # Definim clase
    for cls in ["Beer", "Brewery", "Review", "User"]:
        g.add((EX[cls], RDF.type, OWL.Class))

    # Proprietăți de obiect
    object_props = {
        "hasReview": ("Beer", "Review"),
        "hasReviewer": ("Review", "User"),
    }

    for prop, (domain, range_) in object_props.items():
        g.add((EX[prop], RDF.type, OWL.ObjectProperty))
        g.add((EX[prop], RDFS.domain, EX[domain]))
        g.add((EX[prop], RDFS.range, EX[range_]))

    # Proprietăți de dată
    datatype_props = [
        ("hasName", "string"),
        ("hasStyle", "string"),
        ("hasABV", "float"),
        ("hasAppearanceScore", "float"),
        ("hasAromaScore", "float"),
        ("hasTasteScore", "float"),
        ("hasOverallScore", "float"),
        ("hasPaletteScore", "float"),
        ("hasText", "string"),
        ("hasTime", "integer"),
    ]

    for prop, dtype in datatype_props:
        g.add((EX[prop], RDF.type, OWL.DatatypeProperty))
        g.add((EX[prop], RDFS.domain, OWL.Thing))  # generic
        g.add((EX[prop], RDFS.range, RDFS.Literal))

    # Salvează ontologia ca fișier OWL
    g.serialize(destination=output_path, format='xml')
    print(f"✅ Ontologie salvată: {output_path}")

if __name__ == "__main__":
    create_ontology_structure("../onto/ontology_structure.owl")
