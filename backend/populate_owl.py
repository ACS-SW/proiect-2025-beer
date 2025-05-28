from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal, XSD
import pandas as pd
import re
import xml.sax.saxutils # For XML escaping

# === Încarcă ontologia existentă ===
g = Graph()
# Asigură-te că încarci ontologia manuală inițială
# sau ontologia extinsă dacă vrei să adaugi peste ce există deja
g.parse("./onto/beer_ontology_manual.owl", format="xml") # Sau beer_ontology_extended.owl dacă vrei să adaugi peste

# === Încarcă datele din CSV și selectează 50% ===
try:
    df_full = pd.read_csv("./data/BeerProject1.csv", encoding='latin1')
    print("Full CSV loaded successfully with latin1 encoding.")
except UnicodeDecodeError:
    try:
        df_full = pd.read_csv("./data/BeerProject1.csv", encoding='cp1252')
        print("Full CSV loaded successfully with cp1252 encoding.")
    except UnicodeDecodeError:
        print("Could not decode CSV with latin1 or cp1252. Trying utf-8.")
        try:
            df_full = pd.read_csv("./data/BeerProject1.csv", encoding='utf-8')
            print("Full CSV loaded successfully with utf-8 encoding.")
        except Exception as e:
            print(f"Error loading CSV with utf-8: {e}")
            print("Please check the file encoding or the path.")
            exit()
except FileNotFoundError:
    print("Error: The file 'BeerProject1.csv' was not found at './data/BeerProject1.csv'. Please check the path.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred while loading CSV: {e}")
    exit()

# Select only a subset of the DataFrame (e.g., first 1/15th)
num_rows = len(df_full)
df = df_full.head(num_rows // 15) # Use integer division
print(f"Processing {len(df)} rows (first {num_rows // 15} of total) out of {num_rows} total rows.")


# === Namespaces ===
BASE = Namespace("http://example.org/beer#")
DBPEDIA = Namespace("http://dbpedia.org/resource/")
g.bind("beer", BASE)
g.bind("owl", OWL)
g.bind("dbpedia", DBPEDIA)

# === Stiluri de bere deja cunoscute pe DBpedia (parțial) ===
dbpedia_styles = {
    "Hefeweizen": "Hefeweizen",
    "English Strong Ale": "English_strong_ale",
    "Foreign / Export Stout": "Foreign_extra_stout",
    "German Pilsener": "Pilsner",
    "India Pale Ale": "India_pale_ale",
    "Porter": "Porter",
    "Stout": "Stout",
    "Lambic": "Lambic",
    "Saison": "Saison",
    "Belgian Strong Ale": "Belgian_strong_ale",
    "Barleywine": "Barley_wine",
    "Witbier": "Witbier",
    "Imperial Stout": "Imperial_stout",
    "American Pale Ale": "American_pale_ale",
    "Scotch Ale": "Scotch_ale",
    "Gose": "Gose",
    "Berliner Weisse": "Berliner_Weisse",
    "Doppelbock": "Doppelbock",
    "Märzen": "Märzen",
    "Schwarzbier": "Schwarzbier"
}

# === Function to clean strings for XML 1.0 validity ===
def clean_xml_string(text):
    """
    Aggressively cleans a string to be safe for XML by encoding to ASCII
    and replacing problematic characters, then removing XML 1.0 invalid control chars.
    """
    if pd.isna(text):
        return ""
    text = str(text) # Ensure the input is a string

    # Aggressively convert to ASCII, replacing unencodable characters.
    # This might lose some international characters but ensures XML safety.
    text_ascii_safe = text.encode("ascii", "replace").decode("ascii")

    # Now, apply the XML 1.0 allowed character filter.
    # This regex specifically targets and removes control characters outside of tab, newline, carriage return.
    cleaned_text = re.sub(
        u'[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]',
        '',
        text_ascii_safe
    )
    
    return cleaned_text


# === Adăugare clase și instanțe ===
for index, row in df.iterrows():
    # Sanitize beer name for URI - this will be the ID
    beer_id_raw = str(row['beer_name']).strip() # Use 'beer_name' for ID, or 'beer_id' if more reliable
    # Use beer_id if it exists and is unique, otherwise a sanitized version of beer_name
    # For now, let's assume beer_name is used for ID but can be generic (e.g., Beer_7348)
    beer_name_for_uri = re.sub(r'[^a-zA-Z0-9_]', '', beer_id_raw.replace(" ", "_"))

    # Sanitize beer style for URI
    beer_style_raw = str(row['beer_style']).strip()
    beer_style = re.sub(r'[^a-zA-Z0-9_]', '', beer_style_raw.replace(" ", "_").replace("/", "").replace("-", ""))
    
    beer_uri = BASE[beer_name_for_uri] # This will be the URI, e.g., beer:Beer_7348
    style_class_uri = BASE[beer_style]

    # Creează subclasa pentru stilul de bere, dacă nu există
    g.add((style_class_uri, RDF.type, OWL.Class))
    g.add((style_class_uri, RDFS.subClassOf, BASE.Beer))

    # Leagă stilul de DBpedia dacă se regăsește
    if beer_style_raw in dbpedia_styles:
        dbpedia_uri = DBPEDIA[dbpedia_styles[beer_style_raw]]
        g.add((style_class_uri, OWL.sameAs, dbpedia_uri))

    # Adaugă instanța berii
    g.add((beer_uri, RDF.type, style_class_uri))

    # Proprietăți: ABV și review-uri
    def add_data_property(subject, prop_name, value, datatype):
        if pd.notnull(value):
            if datatype == XSD.string:
                # First, clean potentially invalid XML characters
                cleaned_value = clean_xml_string(value)
                # Then, escape XML entities (e.g., & to &amp;)
                escaped_value = xml.sax.saxutils.escape(cleaned_value)
                g.add((subject, BASE[prop_name], Literal(escaped_value, datatype=datatype)))
            else:
                g.add((subject, BASE[prop_name], Literal(value, datatype=datatype)))

    # Adăugarea proprietăților pentru bere
    add_data_property(beer_uri, "hasABV", row["beer_ABV"], XSD.float)
    add_data_property(beer_uri, "hasAppearanceScore", row["review_appearance"], XSD.float)
    add_data_property(beer_uri, "hasAromaScore", row["review_aroma"], XSD.float)
    add_data_property(beer_uri, "hasTasteScore", row["review_taste"], XSD.float)
    add_data_property(beer_uri, "hasPaletteScore", row["review_palette"], XSD.float)
    add_data_property(beer_uri, "hasOverallScore", row["review_overall"], XSD.float)
    add_data_property(beer_uri, "hasDescriptiveName", row["beer_name"], XSD.string)


# === Salvează noua ontologie ===
g.serialize(destination="./onto/beer_ontology_extended.owl", format="pretty-xml")
print("Ontologia extinsă a fost salvată în 'beer_ontology_extended.owl'")

