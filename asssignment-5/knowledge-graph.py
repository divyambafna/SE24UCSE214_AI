from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from rdflib.namespace import XSD, FOAF
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

EX = Namespace("http://example.org/kg#")

def build_movie_kg():
    g = Graph()
    g.bind("ex", EX)
    g.bind("foaf", FOAF)

    g.add((EX.Person, RDF.type, OWL.Class))
    g.add((EX.Movie, RDF.type, OWL.Class))
    g.add((EX.Genre, RDF.type, OWL.Class))
    g.add((EX.Award, RDF.type, OWL.Class))

    g.add((EX.directedBy, RDF.type, OWL.ObjectProperty))
    g.add((EX.actedIn, RDF.type, OWL.ObjectProperty))
    g.add((EX.hasGenre, RDF.type, OWL.ObjectProperty))
    g.add((EX.wonAward, RDF.type, OWL.ObjectProperty))
    g.add((EX.hasYear, RDF.type, OWL.DatatypeProperty))
    g.add((EX.hasRating, RDF.type, OWL.DatatypeProperty))

    directors = [
        (EX.Nolan, "Christopher Nolan", "British-American"),
        (EX.Spielberg, "Steven Spielberg", "American"),
        (EX.Tarantino, "Quentin Tarantino", "American"),
    ]
    for uri, name, nationality in directors:
        g.add((uri, RDF.type, EX.Person))
        g.add((uri, RDFS.label, Literal(name)))
        g.add((uri, EX.nationality, Literal(nationality)))
        g.add((uri, EX.role, Literal("Director")))

    actors = [
        (EX.DiCaprio, "Leonardo DiCaprio", "American"),
        (EX.Pitt, "Brad Pitt", "American"),
        (EX.Hanks, "Tom Hanks", "American"),
        (EX.Blanchett, "Cate Blanchett", "Australian"),
    ]
    for uri, name, nationality in actors:
        g.add((uri, RDF.type, EX.Person))
        g.add((uri, RDFS.label, Literal(name)))
        g.add((uri, EX.nationality, Literal(nationality)))
        g.add((uri, EX.role, Literal("Actor")))

    movies = [
        (EX.Inception, "Inception", 2010, 8.8, EX.Nolan),
        (EX.Interstellar, "Interstellar", 2014, 8.6, EX.Nolan),
        (EX.Schindler, "Schindler's List", 1993, 9.0, EX.Spielberg),
        (EX.Forrest, "Forrest Gump", 1994, 8.8, EX.Spielberg),
        (EX.Pulp, "Pulp Fiction", 1994, 8.9, EX.Tarantino),
        (EX.Inglourious, "Inglourious Basterds", 2009, 8.3, EX.Tarantino),
    ]
    for uri, title, year, rating, director in movies:
        g.add((uri, RDF.type, EX.Movie))
        g.add((uri, RDFS.label, Literal(title)))
        g.add((uri, EX.hasYear, Literal(year, datatype=XSD.integer)))
        g.add((uri, EX.hasRating, Literal(rating, datatype=XSD.float)))
        g.add((uri, EX.directedBy, director))

    g.add((EX.DiCaprio, EX.actedIn, EX.Inception))
    g.add((EX.DiCaprio, EX.actedIn, EX.Interstellar))
    g.add((EX.Pitt, EX.actedIn, EX.Inglourious))
    g.add((EX.Hanks, EX.actedIn, EX.Forrest))

    genres = [
        (EX.ScieFi, "Science Fiction"),
        (EX.Drama, "Drama"),
        (EX.Crime, "Crime"),
        (EX.History, "Historical"),
        (EX.Thriller, "Thriller"),
    ]
    for uri, name in genres:
        g.add((uri, RDF.type, EX.Genre))
        g.add((uri, RDFS.label, Literal(name)))

    g.add((EX.Inception, EX.hasGenre, EX.ScieFi))
    g.add((EX.Inception, EX.hasGenre, EX.Thriller))
    g.add((EX.Interstellar, EX.hasGenre, EX.ScieFi))
    g.add((EX.Interstellar, EX.hasGenre, EX.Drama))
    g.add((EX.Schindler, EX.hasGenre, EX.History))
    g.add((EX.Schindler, EX.hasGenre, EX.Drama))
    g.add((EX.Forrest, EX.hasGenre, EX.Drama))
    g.add((EX.Pulp, EX.hasGenre, EX.Crime))
    g.add((EX.Pulp, EX.hasGenre, EX.Thriller))
    g.add((EX.Inglourious, EX.hasGenre, EX.History))
    g.add((EX.Inglourious, EX.hasGenre, EX.Drama))

    awards = [
        (EX.Oscar, "Academy Award"),
        (EX.Palme, "Palme d'Or"),
        (EX.BAFTA, "BAFTA Award"),
    ]
    for uri, name in awards:
        g.add((uri, RDF.type, EX.Award))
        g.add((uri, RDFS.label, Literal(name)))

    g.add((EX.Schindler, EX.wonAward, EX.Oscar))
    g.add((EX.Forrest, EX.wonAward, EX.Oscar))
    g.add((EX.Pulp, EX.wonAward, EX.Palme))

    return g


def sparql_query_movies_by_director(g, director_name):
    query = """
    PREFIX ex: <http://example.org/kg#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?movieTitle ?year ?rating
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?movieTitle .
        ?movie ex:hasYear ?year .
        ?movie ex:hasRating ?rating .
        ?movie ex:directedBy ?director .
        ?director rdfs:label ?dirName .
        FILTER(CONTAINS(LCASE(?dirName), LCASE("%s")))
    }
    ORDER BY DESC(?rating)
    """ % director_name

    results = g.query(query)
    return [(str(r.movieTitle), int(r.year), float(r.rating)) for r in results]


def sparql_query_actor_movies(g, actor_name):
    query = """
    PREFIX ex: <http://example.org/kg#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?movieTitle ?year ?genre
    WHERE {
        ?actor rdf:type ex:Person .
        ?actor rdfs:label ?actorName .
        ?actor ex:actedIn ?movie .
        ?movie rdfs:label ?movieTitle .
        ?movie ex:hasYear ?year .
        OPTIONAL { ?movie ex:hasGenre ?genreUri . ?genreUri rdfs:label ?genre . }
        FILTER(CONTAINS(LCASE(?actorName), LCASE("%s")))
    }
    ORDER BY ?year
    """ % actor_name

    results = g.query(query)
    return [(str(r.movieTitle), int(r.year), str(r.genre) if r.genre else "N/A") for r in results]


def sparql_query_award_winners(g):
    query = """
    PREFIX ex: <http://example.org/kg#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?movieTitle ?awardName ?directorName
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?movieTitle .
        ?movie ex:wonAward ?award .
        ?award rdfs:label ?awardName .
        ?movie ex:directedBy ?director .
        ?director rdfs:label ?directorName .
    }
    ORDER BY ?movieTitle
    """
    results = g.query(query)
    return [(str(r.movieTitle), str(r.awardName), str(r.directorName)) for r in results]


def sparql_query_top_rated(g, min_rating=8.5):
    query = """
    PREFIX ex: <http://example.org/kg#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?title ?rating ?dirName
    WHERE {
        ?movie rdf:type ex:Movie .
        ?movie rdfs:label ?title .
        ?movie ex:hasRating ?rating .
        ?movie ex:directedBy ?dir .
        ?dir rdfs:label ?dirName .
        FILTER(?rating >= %s)
    }
    ORDER BY DESC(?rating)
    """ % min_rating

    results = g.query(query)
    return [(str(r.title), float(r.rating), str(r.dirName)) for r in results]


def visualize_kg(g, output_path="knowledge_graph.png"):
    G = nx.DiGraph()

    color_map = {}
    node_colors = []
    labels = {}

    for s, p, o in g:
        if isinstance(s, URIRef) and isinstance(o, URIRef):
            s_label = str(g.value(s, RDFS.label) or s.split("#")[-1])
            o_label = str(g.value(o, RDFS.label) or o.split("#")[-1])
            p_label = str(p).split("#")[-1]

            if p_label in ["directedBy", "actedIn", "hasGenre", "wonAward"]:
                G.add_edge(s_label, o_label, relation=p_label)
                labels[s_label] = s_label
                labels[o_label] = o_label

    type_colors = {}
    for node in G.nodes():
        for s, p, o in g:
            s_label = str(g.value(s, RDFS.label) or s.split("#")[-1])
            if s_label == node:
                t = str(g.value(s, RDF.type) or "").split("#")[-1]
                if t == "Movie":
                    type_colors[node] = "#4FC3F7"
                elif t == "Person":
                    role = str(g.value(s, EX.role) or "")
                    if role == "Director":
                        type_colors[node] = "#FF8A65"
                    else:
                        type_colors[node] = "#A5D6A7"
                elif t == "Genre":
                    type_colors[node] = "#CE93D8"
                elif t == "Award":
                    type_colors[node] = "#FFF176"
                else:
                    type_colors[node] = "#EEEEEE"

    for node in G.nodes():
        if node not in type_colors:
            type_colors[node] = "#EEEEEE"

    node_color_list = [type_colors.get(n, "#EEEEEE") for n in G.nodes()]
    edge_labels = {(u, v): d["relation"] for u, v, d in G.edges(data=True)}

    plt.figure(figsize=(16, 10))
    pos = nx.spring_layout(G, k=2.5, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color=node_color_list, node_size=2000, alpha=0.9)
    nx.draw_networkx_labels(G, pos, font_size=7, font_weight="bold")
    nx.draw_networkx_edges(G, pos, edge_color="#999999", arrows=True, arrowsize=20, width=1.5)
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=6, font_color="#333333")

    legend_elements = [
        plt.matplotlib.patches.Patch(facecolor="#4FC3F7", label="Movie"),
        plt.matplotlib.patches.Patch(facecolor="#FF8A65", label="Director"),
        plt.matplotlib.patches.Patch(facecolor="#A5D6A7", label="Actor"),
        plt.matplotlib.patches.Patch(facecolor="#CE93D8", label="Genre"),
        plt.matplotlib.patches.Patch(facecolor="#FFF176", label="Award"),
    ]
    plt.legend(handles=legend_elements, loc="upper left", fontsize=9)
    plt.title("Movie Knowledge Graph", fontsize=14, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"Knowledge Graph saved to: {output_path}")


def knowledge_graph_tools_overview():
    tools = {
        "RDFLib": {
            "type": "Python Library",
            "use": "Build, parse, query RDF-based KGs in Python",
            "features": ["Supports RDF, OWL, SPARQL", "Turtle/JSON-LD/N3 formats", "In-memory or file-based storage"],
            "best_for": "Lightweight KG in Python apps"
        },
        "Neo4j": {
            "type": "Graph Database",
            "use": "Property graph model with Cypher query language",
            "features": ["High-performance graph traversal", "Visual browser", "Cypher query language"],
            "best_for": "Large-scale production KG with complex queries"
        },
        "Protégé": {
            "type": "Ontology Editor",
            "use": "Design OWL ontologies visually",
            "features": ["OWL/RDF ontology authoring", "Reasoning support", "Plugin ecosystem"],
            "best_for": "Building domain ontologies"
        },
        "Apache_Jena": {
            "type": "Java Framework",
            "use": "Build semantic web and KG applications in Java",
            "features": ["SPARQL endpoint", "TDB triple store", "OWL reasoning"],
            "best_for": "Enterprise semantic web apps"
        },
        "Wikidata": {
            "type": "Public KG",
            "use": "Open structured knowledge base",
            "features": ["SPARQL endpoint", "Multilingual", "Linked open data"],
            "best_for": "General world knowledge queries"
        }
    }

    print("\n" + "="*60)
    print("  KNOWLEDGE GRAPH TOOLS OVERVIEW")
    print("="*60)
    for tool, info in tools.items():
        print(f"\nTool      : {tool}")
        print(f"Type      : {info['type']}")
        print(f"Use Case  : {info['use']}")
        print(f"Features  : {', '.join(info['features'])}")
        print(f"Best For  : {info['best_for']}")
        print("-"*40)


g = build_movie_kg()

print(f"Total triples in KG: {len(g)}")

print("\nMovies by Christopher Nolan:")
for title, year, rating in sparql_query_movies_by_director(g, "Nolan"):
    print(f"  {title} ({year}) - Rating: {rating}")

print("\nLeonardo DiCaprio's movies:")
for title, year, genre in sparql_query_actor_movies(g, "DiCaprio"):
    print(f"  {title} ({year}) - Genre: {genre}")

print("\nAward-winning movies:")
for movie, award, director in sparql_query_award_winners(g):
    print(f"  {movie} - {award} (Dir: {director})")

print("\nTop-rated movies (rating >= 8.5):")
for title, rating, director in sparql_query_top_rated(g, 8.5):
    print(f"  {title} - {rating} (Dir: {director})")

knowledge_graph_tools_overview()

visualize_kg(g, "/mnt/user-data/outputs/knowledge_graph.png")
