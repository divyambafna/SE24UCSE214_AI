from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal, URIRef
from rdflib.namespace import XSD
import json
import random

TRAVEL = Namespace("http://travelplanner.org/ontology#")
PLACE = Namespace("http://travelplanner.org/place#")
FOOD = Namespace("http://travelplanner.org/food#")
WINE = Namespace("http://travelplanner.org/wine#")

def build_knowledge_base():
    g = Graph()
    g.bind("travel", TRAVEL)
    g.bind("place", PLACE)
    g.bind("food", FOOD)
    g.bind("wine", WINE)

    g.add((TRAVEL.TouristPlace, RDF.type, OWL.Class))
    g.add((TRAVEL.Food, RDF.type, OWL.Class))
    g.add((TRAVEL.Wine, RDF.type, OWL.Class))
    g.add((TRAVEL.TourPlan, RDF.type, OWL.Class))

    g.add((TRAVEL.locatedIn, RDF.type, OWL.ObjectProperty))
    g.add((TRAVEL.hasFood, RDF.type, OWL.ObjectProperty))
    g.add((TRAVEL.pairsWithWine, RDF.type, OWL.ObjectProperty))
    g.add((TRAVEL.hasCost, RDF.type, OWL.DatatypeProperty))
    g.add((TRAVEL.hasRating, RDF.type, OWL.DatatypeProperty))
    g.add((TRAVEL.hasClimate, RDF.type, OWL.DatatypeProperty))
    g.add((TRAVEL.hasDuration, RDF.type, OWL.DatatypeProperty))
    g.add((TRAVEL.hasCategory, RDF.type, OWL.DatatypeProperty))

    places = [
        (PLACE.Paris, "Paris", "France", "Cultural", 1200, 4.8, "Mild"),
        (PLACE.Rome, "Rome", "Italy", "Historical", 950, 4.7, "Mediterranean"),
        (PLACE.Bali, "Bali", "Indonesia", "Beach", 800, 4.6, "Tropical"),
        (PLACE.Kyoto, "Kyoto", "Japan", "Cultural", 1400, 4.9, "Temperate"),
        (PLACE.NewYork, "New York", "USA", "Urban", 1600, 4.5, "Continental"),
        (PLACE.Santorini, "Santorini", "Greece", "Beach", 1100, 4.8, "Mediterranean"),
        (PLACE.Machu_Picchu, "Machu Picchu", "Peru", "Adventure", 1300, 4.9, "Highland"),
        (PLACE.Safari_Kenya, "Nairobi", "Kenya", "Wildlife", 2000, 4.7, "Tropical"),
    ]

    for uri, name, country, category, cost, rating, climate in places:
        g.add((uri, RDF.type, TRAVEL.TouristPlace))
        g.add((uri, RDFS.label, Literal(name)))
        g.add((uri, TRAVEL.locatedIn, Literal(country)))
        g.add((uri, TRAVEL.hasCategory, Literal(category)))
        g.add((uri, TRAVEL.hasCost, Literal(cost, datatype=XSD.integer)))
        g.add((uri, TRAVEL.hasRating, Literal(rating, datatype=XSD.float)))
        g.add((uri, TRAVEL.hasClimate, Literal(climate)))

    foods = [
        (FOOD.Croissant, "Croissant", "French", PLACE.Paris, WINE.Champagne),
        (FOOD.Pizza, "Pizza", "Italian", PLACE.Rome, WINE.Chianti),
        (FOOD.NasiGoreng, "Nasi Goreng", "Indonesian", PLACE.Bali, WINE.Riesling),
        (FOOD.Sushi, "Sushi", "Japanese", PLACE.Kyoto, WINE.SakeSparkling),
        (FOOD.Bagel, "Bagel", "American", PLACE.NewYork, WINE.Chardonnay),
        (FOOD.Moussaka, "Moussaka", "Greek", PLACE.Santorini, WINE.Assyrtiko),
        (FOOD.Ceviche, "Ceviche", "Peruvian", PLACE.Machu_Picchu, WINE.Albario),
        (FOOD.Nyama_Choma, "Nyama Choma", "Kenyan", PLACE.Safari_Kenya, WINE.Shiraz),
    ]

    for uri, name, cuisine, place, wine in foods:
        g.add((uri, RDF.type, TRAVEL.Food))
        g.add((uri, RDFS.label, Literal(name)))
        g.add((uri, TRAVEL.hasCuisine, Literal(cuisine)))
        g.add((uri, TRAVEL.locatedIn, place))
        g.add((uri, TRAVEL.pairsWithWine, wine))

    wines = [
        (WINE.Champagne, "Champagne", "Sparkling", "France"),
        (WINE.Chianti, "Chianti", "Red", "Italy"),
        (WINE.Riesling, "Riesling", "White", "Germany"),
        (WINE.SakeSparkling, "Sake Sparkling", "Sparkling", "Japan"),
        (WINE.Chardonnay, "Chardonnay", "White", "France"),
        (WINE.Assyrtiko, "Assyrtiko", "White", "Greece"),
        (WINE.Albario, "Albariño", "White", "Spain"),
        (WINE.Shiraz, "Shiraz", "Red", "Australia"),
    ]

    for uri, name, wine_type, origin in wines:
        g.add((uri, RDF.type, TRAVEL.Wine))
        g.add((uri, RDFS.label, Literal(name)))
        g.add((uri, TRAVEL.hasWineType, Literal(wine_type)))
        g.add((uri, TRAVEL.locatedIn, Literal(origin)))

    return g


def query_places_by_category(g, category):
    results = []
    for place in g.subjects(RDF.type, TRAVEL.TouristPlace):
        cat = g.value(place, TRAVEL.hasCategory)
        if cat and str(cat).lower() == category.lower():
            name = g.value(place, RDFS.label)
            cost = g.value(place, TRAVEL.hasCost)
            rating = g.value(place, TRAVEL.hasRating)
            country = g.value(place, TRAVEL.locatedIn)
            results.append({
                "uri": place,
                "name": str(name),
                "country": str(country),
                "cost": int(cost),
                "rating": float(rating),
                "category": str(cat)
            })
    return sorted(results, key=lambda x: x["rating"], reverse=True)


def query_food_for_place(g, place_uri):
    results = []
    for food in g.subjects(TRAVEL.locatedIn, place_uri):
        if (food, RDF.type, TRAVEL.Food) in g:
            name = g.value(food, RDFS.label)
            cuisine = g.value(food, TRAVEL.hasCuisine)
            wine_uri = g.value(food, TRAVEL.pairsWithWine)
            wine_name = g.value(wine_uri, RDFS.label) if wine_uri else "None"
            results.append({
                "food": str(name),
                "cuisine": str(cuisine),
                "wine_pairing": str(wine_name)
            })
    return results


def query_places_by_budget(g, max_budget):
    results = []
    for place in g.subjects(RDF.type, TRAVEL.TouristPlace):
        cost = g.value(place, TRAVEL.hasCost)
        if cost and int(cost) <= max_budget:
            name = g.value(place, RDFS.label)
            rating = g.value(place, TRAVEL.hasRating)
            category = g.value(place, TRAVEL.hasCategory)
            country = g.value(place, TRAVEL.locatedIn)
            results.append({
                "uri": place,
                "name": str(name),
                "country": str(country),
                "cost": int(cost),
                "rating": float(rating),
                "category": str(category)
            })
    return sorted(results, key=lambda x: x["rating"], reverse=True)


def generate_tour_plan(g, preferences):
    budget = preferences.get("budget", 5000)
    category = preferences.get("category", None)
    num_days = preferences.get("days", 7)
    travelers = preferences.get("travelers", 1)

    if category:
        places = query_places_by_category(g, category)
        places = [p for p in places if p["cost"] * travelers <= budget]
    else:
        places = query_places_by_budget(g, budget // travelers)

    if not places:
        return {"error": "No places found matching your criteria."}

    selected = places[0]
    food_info = query_food_for_place(g, selected["uri"])

    daily_activities = {
        "Cultural": ["Visit local museums", "Attend cultural shows", "Explore old town", "Visit art galleries", "Attend local festivals"],
        "Beach": ["Morning beach walk", "Snorkeling/Diving", "Sunset cruise", "Beach volleyball", "Local seafood dinner"],
        "Historical": ["Ancient ruins tour", "Museum visit", "Guided heritage walk", "Archaeological site", "Historical monument visit"],
        "Adventure": ["Hiking/Trekking", "Rock climbing", "Zip-lining", "Camping", "Rappelling"],
        "Wildlife": ["Safari drive", "Bird watching", "Nature walk", "Wildlife photography", "Visit national park"],
        "Urban": ["City tour", "Shopping districts", "Street food tour", "Theatre show", "Rooftop dining"],
    }

    cat = selected["category"]
    activities = daily_activities.get(cat, ["Sightseeing", "Local tour", "Rest day", "Shopping", "Cultural experience"])

    itinerary = []
    for day in range(1, num_days + 1):
        activity = activities[(day - 1) % len(activities)]
        itinerary.append({
            "day": day,
            "activity": activity,
            "meal": food_info[0]["food"] if food_info else "Local cuisine",
            "wine": food_info[0]["wine_pairing"] if food_info else "House wine"
        })

    base_cost = selected["cost"] * travelers
    accommodation = num_days * 80 * travelers
    food_cost = num_days * 40 * travelers
    transport = 200 * travelers
    total_cost = base_cost + accommodation + food_cost + transport

    plan = {
        "destination": selected["name"],
        "country": selected["country"],
        "category": cat,
        "rating": selected["rating"],
        "travelers": travelers,
        "duration_days": num_days,
        "itinerary": itinerary,
        "cost_breakdown": {
            "flights": base_cost,
            "accommodation": accommodation,
            "food": food_cost,
            "local_transport": transport,
            "total": total_cost
        },
        "food_recommendations": food_info
    }
    return plan


def print_tour_plan(plan):
    if "error" in plan:
        print(f"Error: {plan['error']}")
        return

    print("\n" + "="*60)
    print(f"  PERSONALISED TOUR PLAN")
    print("="*60)
    print(f"Destination  : {plan['destination']}, {plan['country']}")
    print(f"Category     : {plan['category']}")
    print(f"Rating       : {plan['rating']}/5.0")
    print(f"Travelers    : {plan['travelers']}")
    print(f"Duration     : {plan['duration_days']} days")
    print("\nITINERARY:")
    print("-"*40)
    for item in plan["itinerary"]:
        print(f"  Day {item['day']}: {item['activity']}")
        print(f"           Meal: {item['meal']} | Wine: {item['wine']}")
    print("\nFOOD RECOMMENDATIONS:")
    print("-"*40)
    for f in plan["food_recommendations"]:
        print(f"  {f['food']} ({f['cuisine']}) - pairs with {f['wine_pairing']}")
    print("\nCOST BREAKDOWN (USD):")
    print("-"*40)
    cb = plan["cost_breakdown"]
    print(f"  Flights        : ${cb['flights']}")
    print(f"  Accommodation  : ${cb['accommodation']}")
    print(f"  Food           : ${cb['food']}")
    print(f"  Local Transport: ${cb['local_transport']}")
    print(f"  TOTAL          : ${cb['total']}")
    print("="*60)


g = build_knowledge_base()

print("Test 1: Beach holiday under $3000 for 2 travelers, 5 days")
plan1 = generate_tour_plan(g, {"budget": 3000, "category": "Beach", "days": 5, "travelers": 2})
print_tour_plan(plan1)

print("\nTest 2: Cultural trip under $5000 for 1 traveler, 7 days")
plan2 = generate_tour_plan(g, {"budget": 5000, "category": "Cultural", "days": 7, "travelers": 1})
print_tour_plan(plan2)

print("\nTest 3: Adventure trip under $4000 for 3 travelers, 6 days")
plan3 = generate_tour_plan(g, {"budget": 4000, "category": "Adventure", "days": 6, "travelers": 3})
print_tour_plan(plan3)
