from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("Health-Service")

storage = {
    "steps": 0
}

# ── Static fallback calorie table (kcal per 100g) ────────────────────────────
# Used when Open Food Facts API is unavailable or returns no data
CALORIE_FALLBACK = {
    "chicken": 165, "chicken breast": 165, "beef": 250, "lamb": 294,
    "pork": 242, "salmon": 208, "tuna": 144, "egg": 155, "eggs": 155,
    "milk": 61, "butter": 717, "cheese": 402, "parmesan": 431,
    "cream": 345, "yogurt": 59, "paneer": 265,
    "rice": 130, "pasta": 131, "bread": 265, "flour": 364,
    "oats": 389, "noodles": 138,
    "potato": 77, "tomato": 18, "onion": 40, "garlic": 149,
    "carrot": 41, "spinach": 23, "broccoli": 34, "mushroom": 22,
    "pepper": 31, "lemon": 29, "lime": 30, "ginger": 80,
    "olive oil": 884, "oil": 884, "coconut oil": 862,
    "sugar": 387, "honey": 304, "salt": 0,
    "soy sauce": 53, "vinegar": 18, "ketchup": 112,
    "chickpeas": 164, "lentils": 116, "beans": 127,
    "almond": 579, "cashew": 553, "peanut": 567,
    "apple": 52, "banana": 89, "mango": 60, "orange": 47,
    "chocolate": 546, "cocoa": 228,
}
 
# ── Shared request headers ────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": "HealthAgentADK/1.0 (open-source educational project; contact: dev@example.com)"
}


@mcp.tool()
def get_calories(food: str) -> str:
    """
    Fetch calorie data for a raw food or ingredient.
    Primary source: Open Food Facts API.
    Fallback: built-in static calorie table.
    """
    food_name = food.lower().strip()
 
    # ── Try Open Food Facts API first ────────────────────────────────────────
    try:
        response = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            headers=HEADERS,
            params={
                "search_terms": food_name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 30,
                "fields": "product_name,generic_name,nutriments",
            },
            timeout=10,
        )
 
        if response.status_code == 200:
            products = response.json().get("products", [])
            for product in products:
                name = product.get("product_name") or product.get("generic_name") or food
                nutriments = product.get("nutriments", {})
                kcal = (
                    nutriments.get("energy-kcal_100g")
                    or nutriments.get("energy-kcal")
                    or nutriments.get("energy-kcal_value")
                )
                if kcal is not None:
                    return f"{name} contains approximately {round(kcal)} kcal per 100g."
 
    except Exception:
        pass  # Fall through to static lookup
 
    # ── Fallback: static calorie table ───────────────────────────────────────
    for key in [food_name, food_name.split()[0]]:
        if key in CALORIE_FALLBACK:
            kcal = CALORIE_FALLBACK[key]
            return f"{food.title()} contains approximately {kcal} kcal per 100g (estimated)."
 
    return (
        f"Could not find calorie data for '{food}'. "
        "Try common ingredients like chicken, rice, egg, or butter."
    )
 
 
@mcp.tool()
def manage_steps(action: str, value: int = 0) -> str:
    """Manage step count. action can be 'add', 'get', or 'reset'."""
    action = action.lower().strip()
 
    if action == "add":
        if value <= 0:
            return "Please provide a positive number of steps."
        storage["steps"] += value
        return f"Added {value} steps. Current total: {storage['steps']} steps."
 
    if action == "get":
        return f"Current step total: {storage['steps']} steps."
 
    if action == "reset":
        storage["steps"] = 0
        return "Step count reset to 0."
 
    return "Invalid action. Use 'add', 'get', or 'reset'."


if __name__ == "__main__":
    mcp.run()