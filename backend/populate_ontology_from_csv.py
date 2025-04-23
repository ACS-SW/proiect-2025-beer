import csv
from rdflib import Graph, Namespace, Literal, RDF
from rdflib.namespace import XSD
import math


def populate_ontology(csv_path, output_path, base_ns="http://example.org/beer#", process_percentage=10):
    g = Graph()
    EX = Namespace(base_ns)
    g.bind("ex", EX)

    with open(csv_path, newline='', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        total_rows = sum(1 for _ in reader)  # Count total rows
        max_rows_to_process = math.floor(total_rows * (process_percentage / 100))
        csvfile.seek(0)  # Reset file pointer
        next(reader)  # Skip header again

        print(f"⏳ Starting to process {max_rows_to_process} rows (50% of {total_rows})...")

        for idx, row in enumerate(reader):
            if idx >= max_rows_to_process:
                break

            # Show progress every 1000 rows or 5% of total, whichever is smaller
            progress_interval = min(1000, max_rows_to_process // 20)
            if progress_interval > 0 and idx % progress_interval == 0:
                percent_complete = (idx / max_rows_to_process) * 100
                print(f"🔨 Processed {idx}/{max_rows_to_process} rows ({percent_complete:.1f}%)")

            # === Beer ===
            beer_uri = EX[f"Beer_{row['beer_beerId']}"]
            g.add((beer_uri, RDF.type, EX.Beer))
            g.add((beer_uri, EX.hasName, Literal(row['beer_name'], datatype=XSD.string)))
            g.add((beer_uri, EX.hasStyle, Literal(row['beer_style'], datatype=XSD.string)))
            if row['beer_ABV'].strip():
                g.add((beer_uri, EX.hasABV, Literal(float(row['beer_ABV']), datatype=XSD.float)))

            # === Brewery ===
            brewery_uri = EX[f"Brewery_{row['beer_brewerId']}"]
            g.add((brewery_uri, RDF.type, EX.Brewery))
            g.add((beer_uri, EX.hasBrewery, brewery_uri))

            # === Review ===
            review_uri = EX[f"Review_{idx}"]
            g.add((review_uri, RDF.type, EX.Review))
            g.add((review_uri, EX.hasAppearanceScore, Literal(float(row['review_appearance']), datatype=XSD.float)))
            g.add((review_uri, EX.hasAromaScore, Literal(float(row['review_aroma']), datatype=XSD.float)))
            g.add((review_uri, EX.hasTasteScore, Literal(float(row['review_taste']), datatype=XSD.float)))
            g.add((review_uri, EX.hasOverallScore, Literal(float(row['review_overall']), datatype=XSD.float)))
            g.add((review_uri, EX.hasPaletteScore, Literal(float(row['review_palette']), datatype=XSD.float)))
            g.add((review_uri, EX.hasText, Literal(row['review_text'], datatype=XSD.string)))
            g.add((review_uri, EX.hasTime, Literal(int(row['review_time']), datatype=XSD.integer)))

            # beer → review link
            g.add((beer_uri, EX.hasReview, review_uri))

            # === User ===
            user_uri = EX[f"User_{row['review_profileName']}"]
            g.add((user_uri, RDF.type, EX.User))
            g.add((review_uri, EX.hasReviewer, user_uri))

    # Save the result as OWL
    g.serialize(destination=output_path, format='xml')
    print(f"\n✅ Ontology populated and saved: {output_path}")
    print(f"   Processed {max_rows_to_process} rows (10% of {total_rows})")
    print(f"   Total triples created: {len(g)}")
    print(f"   Estimated triples if processed 100%: {len(g) * 5}")


if __name__ == "__main__":
    populate_ontology("../data/BeerProject.csv", "../onto/populated_beer.owl")