from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal
import networkx as nx
import matplotlib.pyplot as plt

# === Load the RDF Graph (Ontology) ===
g = Graph()
try:
    # Load the extended ontology which contains populated data
    g.parse("./onto/beer_ontology_extended.owl", format="xml")
    print("Ontology loaded successfully from 'beer_ontology_extended.owl'.")
except Exception as e:
    print(f"Error loading ontology: {e}")
    print("Please ensure 'populate_owl.py' was run successfully and 'beer_ontology_extended.owl' is valid and exists.")
    exit()

# === Define Namespaces ===
# Base namespace used in your populated ontology
BEER = Namespace("http://example.org/beer#")
# DBpedia namespace for external links
DBPEDIA = Namespace("http://dbpedia.org/resource/")
g.bind("beer", BEER)
g.bind("dbpedia", DBPEDIA) # Bind DBPEDIA for clearer output if needed

# === Create the NetworkX Graph for Visualization ===
G = nx.DiGraph()

# === Ontology Summary: Classes and Properties ===
# This section provides an overview of the ontology's structure.

# Find all explicit OWL Classes (subjects with rdf:type owl:Class)
explicit_classes = set(g.subjects(RDF.type, OWL.Class))
print(f"DEBUG: explicit_classes contains {len(explicit_classes)} classes after definition.") # Debug print

# Find all classes involved in rdfs:subClassOf relationships (both subjects and objects)
subclasses_in_relationships = set()
for s, p, o in g.triples((None, RDFS.subClassOf, None)):
    subclasses_in_relationships.add(s)
    subclasses_in_relationships.add(o)

# Find all Object Properties (subjects with rdf:type owl:ObjectProperty)
object_properties = set(g.subjects(RDF.type, OWL.ObjectProperty))

# Find all Datatype Properties (subjects with rdf:type owl:DatatypeProperty)
datatype_properties = set(g.subjects(RDF.type, OWL.DatatypeProperty))

# Print the summary counts (commented out for brevity in visualization focus)
# print("\n=== Ontology Summary ===")
# print(f"Total Explicit OWL Classes: {len(explicit_classes)}")
# print(f"Total Classes in SubClassOf relationships: {len(subclasses_in_relationships)}")
# print(f"Total Object Properties: {len(object_properties)}")
# print(f"Total Datatype Properties: {len(datatype_properties)}")


# === Add Classes and SubClassOf Relationships ===
# Iterate over all triples where the predicate is rdfs:subClassOf
# This captures the hierarchy of beer styles (e.g., IPA subClassOf Beer)
for s, p, o in g.triples((None, RDFS.subClassOf, None)):
    # Ensure both subject and object are part of our beer ontology namespace
    if str(s).startswith(str(BEER)) and str(o).startswith(str(BEER)):
        s_label = s.split("#")[-1] # Extract local name for subject
        o_label = o.split("#")[-1] # Extract local name for object
        G.add_edge(o_label, s_label, label="subClassOf") # Add edge from superclass to subclass

# === Add Instances (e.g., Sausa_Weizen is a Hefeweizen) ===
# Iterate over all triples where the predicate is rdf:type
# This links individual beer instances to their respective style classes
for s, p, o in g.triples((None, RDF.type, None)):
    # Check if the object (type) is within our beer ontology namespace
    if str(o).startswith(str(BEER)):
        instance_label = s.split("#")[-1] # Extract local name for the beer instance
        class_label = o.split("#")[-1]    # Extract local name for the beer style class
        G.add_edge(class_label, instance_label, label="type") # Add edge from class to instance

# === Add sameAs Relationships to DBpedia ===
# Iterate over all triples where the predicate is owl:sameAs
# This links our local ontology concepts to external DBpedia resources
for s, p, o in g.triples((None, OWL.sameAs, None)):
    # Ensure the subject is from our beer ontology and the object is a DBpedia resource
    if str(s).startswith(str(BEER)) and str(o).startswith(str(DBPEDIA)):
        s_label = s.split("#")[-1]    # Extract local name for our local concept
        o_label = o.split("/")[-1]    # Extract the last part of the DBpedia URI
        G.add_edge(s_label, o_label, label="sameAs") # Add edge from local concept to DBpedia

# === Add Data Properties (e.g., hasABV, hasTasteScore) ===
# Iterate over all datatype properties to show attributes of instances
for s, p, o in g.triples((None, None, None)):
    if isinstance(o, Literal) and str(s).startswith(str(BEER)):
        instance_label = s.split("#")[-1]
        prop_label = p.split("#")[-1] # Get property name (e.g., hasABV)
        
        # Only add properties that are relevant and not too verbose for visualization
        # You can customize which properties to show here
        if prop_label in ["hasABV", "hasOverallScore", "hasPaletteScore", "hasTasteScore", "hasAppearanceScore", "hasAromaScore"]:
            # Create a more descriptive label for the node, e.g., "ABV: 5.0"
            property_node_label = f"{prop_label.replace('has', '')}: {o.value}"
            G.add_node(property_node_label, type='property_value') # Add a node for the property value
            G.add_edge(instance_label, property_node_label, label=prop_label) # Link instance to property value


# === Draw the Graph ===
plt.figure(figsize=(15, 10)) # Adjust figure size for better readability
# Using spring_layout for a more organic, force-directed layout
pos = nx.spring_layout(G, k=0.7, iterations=50) # k regulates distance between nodes, iterations for stability

# Draw nodes
# Differentiate node colors based on their type (class, instance, dbpedia, property value)
node_colors = []
node_sizes = []
for node in G.nodes():
    # Check if the node is a class from our BEER namespace or explicitly defined as an OWL Class
    if str(node).startswith(str(BEER)) or (node in [s.split("#")[-1] for s in explicit_classes]):
        node_colors.append('lightblue') # Classes
        node_sizes.append(1500)
    # Check if the node is a DBpedia link
    elif str(node).startswith(str(DBPEDIA)) or (node in [o.split('/')[-1] for s,p,o in g.triples((None, OWL.sameAs, None))]):
        node_colors.append('lightgreen') # DBpedia links
        node_sizes.append(1200)
    # Check if the node is a property value node (created dynamically)
    elif G.nodes[node].get('type') == 'property_value':
        node_colors.append('lightcoral') # Property values
        node_sizes.append(800)
    else:
        # Default for instances (which are not explicitly classes or DBpedia links)
        node_colors.append('lightgray') # Instances
        node_sizes.append(1000)

nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes, alpha=0.9)

# Draw edges
nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=15, width=1.0, alpha=0.7, edge_color='gray')

# Draw node labels
nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold')

# Draw edge labels
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7, font_color='darkblue')

plt.title("Vizualizare Ontologie Bere Extinsă", size=16)
plt.axis('off') # Turn off the axis
plt.tight_layout() # Adjust layout to prevent labels from overlapping
plt.show() # Display the plot
