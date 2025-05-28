from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal, XSD

# Define the base namespace used in your populated ontology
BASE = Namespace("http://example.org/beer#")
DBPEDIA = Namespace("http://dbpedia.org/resource/") # Added DBPEDIA namespace for linking

# Încarcă fișierul OWL
g = Graph()
try:
    g.parse("./onto/beer_ontology_extended.owl", format="xml")
    print("Ontology loaded successfully from 'beer_ontology_extended.owl'.")
except Exception as e:
    print(f"Error loading ontology: {e}")
    print("Please ensure 'populate_owl.py' was run successfully and 'beer_ontology_extended.owl' is valid and exists.")
    exit()

# === Afișare rezultate generale (păstrate pentru context) ===
# === Explicit OWL Classes (owl:Class) ===
explicit_classes = set(s for s in g.subjects(RDF.type, OWL.Class))
# === Implicit Classes: any subject or object in rdfs:subClassOf ===
subclasses = set()
for s, p, o in g.triples((None, RDFS.subClassOf, None)):
    subclasses.add(s)
    subclasses.add(o)
# === Object Properties ===
object_properties = set(s for s in g.subjects(RDF.type, OWL.ObjectProperty))
# === Datatype Properties ===
datatype_properties = set(s for s in g.subjects(RDF.type, OWL.DatatypeProperty))

print(f"\nClase OWL explicite (owl:Class): {len(explicit_classes)}")
# for cls in explicit_classes:
#     print(f"- {cls}")

print(f"\nClase găsite în relații subClassOf: {len(subclasses)}")
# for cls in subclasses:
#     print(f"- {cls}")

print(f"\nProprietăți de obiect (owl:ObjectProperty): {len(object_properties)}")
# for prop in object_properties:
#     print(f"- {prop}")

print(f"\nProprietăți de date (owl:DatatypeProperty): {len(datatype_properties)}")
# for prop in datatype_properties:
#     print(f"- {prop}")


# === Funcție pentru a afișa detaliile unui obiect specific ===
def display_object_details(graph, object_uri, base_namespace, dbpedia_namespace): # Changed to accept URI directly
    """
    Displays all details for a specific object (instance) in the ontology.
    Details include its class, DBpedia link (if its class has one), and all its properties.
    """
    object_name = object_uri.split('#')[-1] # Extract local name for display

    print(f"\n=== Detalii pentru obiectul: {object_name} ===")

    # 1. Clasa din care face parte
    classes = list(graph.objects(object_uri, RDF.type))
    if classes:
        for cls_uri in classes:
            print(f"  Clasa directă: {cls_uri.split('#')[-1]}")
            
            # 2. Legătura DBpedia a clasei
            dbpedia_links = list(graph.objects(cls_uri, OWL.sameAs))
            for dbpedia_link in dbpedia_links:
                if str(dbpedia_link).startswith(str(dbpedia_namespace)):
                    print(f"    Legătură DBpedia (pentru clasă): {dbpedia_link}")
    else:
        print("  Clasa directă: N/A (nu s-a găsit o clasă explicită)")

    # 3. Toate proprietățile obiectului
    print("\n  Proprietăți:")
    found_properties = False
    for p, o in graph.predicate_objects(object_uri):
        found_properties = True
        prop_name = p.split('#')[-1] # Extract local name of the property
        
        # Check if it's a literal (data property) or another URI (object property)
        if isinstance(o, Literal):
            print(f"    - {prop_name}: {o.value} (Tip: {o.datatype.split('#')[-1] if o.datatype else 'Literal'})")
        elif isinstance(o, URIRef):
            print(f"    - {prop_name}: {o.split('#')[-1]} (Tip: Obiect)")
        else:
            print(f"    - {prop_name}: {o} (Tip: Necunoscut)")
    
    if not found_properties:
        print("    Nu s-au găsit proprietăți pentru acest obiect.")


# === Afișare detalii pentru primele 20 de beri ===
print("\n=== Afișare detalii pentru primele 20 de beri ===")

# Find all instances that are of type beer:Beer or its subclasses
beer_instances = set()
for s, p, o in g.triples((None, RDF.type, None)):
    # Check if the object 'o' is a subclass of BASE.Beer or BASE.Beer itself
    if (o, RDFS.subClassOf, BASE.Beer) in g or o == BASE.Beer:
        beer_instances.add(s)

if not beer_instances:
    print("Nu s-au găsit instanțe de bere în ontologie.")
else:
    # Convert to list and sort for consistent output (optional, but good for debugging)
    sorted_beer_instances = sorted(list(beer_instances))
    
    # Iterate through the first 20 beers
    count = 0
    for beer_uri in sorted_beer_instances:
        if count >= 20:
            break
        display_object_details(g, beer_uri, BASE, DBPEDIA)
        count += 1

    if len(sorted_beer_instances) > 20:
        print(f"\n... Au fost afișate detaliile pentru primele 20 de beri din {len(sorted_beer_instances)} găsite.")

