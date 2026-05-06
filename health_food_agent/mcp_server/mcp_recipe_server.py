from mcp.server.fastmcp import FastMCP
import requests
 
mcp = FastMCP("Recipe-Service")

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

def fetch_calories_for_ingredient(ingredient: str) -> str:
    """
    Internal helper — NOT an MCP tool.
    1. Tries Open Food Facts API with proper headers.
    2. Falls back to static CALORIE_FALLBACK table.
    3. Returns 'calories unknown' only if both fail.
    """
    food_name = ingredient.lower().strip()
 
    # ── Try Open Food Facts API ───────────────────────────────────────────────
    try:
        response = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            headers=HEADERS,
            params={
                "search_terms": food_name,
                "search_simple": 1,
                "action": "process",
                "json": 1,
                "page_size": 5,
                "fields": "product_name,nutriments",
            },
            timeout=4,
        )
        if response.status_code == 200:
            for product in response.json().get("products", []):
                kcal = (
                    product.get("nutriments", {}).get("energy-kcal_100g")
                    or product.get("nutriments", {}).get("energy-kcal")
                )
                if kcal is not None:
                    return f"{round(kcal)} kcal/100g"
    except Exception:
        pass  # Fall through to static lookup
 
    # ── Fallback: static calorie table ───────────────────────────────────────
    for key in [food_name, food_name.split()[0]]:
        if key in CALORIE_FALLBACK:
            return f"~{CALORIE_FALLBACK[key]} kcal/100g (est.)"
 
    return "calories unknown"

 
@mcp.tool()
def get_recipe_with_calories(ingredient: str, cuisine: str = "") -> str:
    """
    Fetch a full recipe from TheMealDB by ingredient or dish name.
    Returns: meal name, cuisine, full ingredient list with measures,
    per-ingredient calorie estimates, and a short cooking summary.
    """
    ingredient = ingredient.lower().strip()
    meal = None
 
    # Step 1: Search by ingredient
    try:
        resp = requests.get(
            "https://www.themealdb.com/api/json/v1/1/filter.php",
            headers=HEADERS,
            params={"i": ingredient},
            timeout=10,
        ).json()
        if resp.get("meals"):
            meal_id = resp["meals"][0]["idMeal"]
            detail = requests.get(
                f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}",
                headers=HEADERS,
                timeout=10,
            ).json()
            meal = detail["meals"][0] if detail.get("meals") else None
    except Exception:
        pass
 
    # Step 2: Fallback — search by dish name
    if not meal:
        try:
            resp = requests.get(
                "https://www.themealdb.com/api/json/v1/1/search.php",
                headers=HEADERS,
                params={"s": ingredient},
                timeout=10,
            ).json()
            if resp.get("meals"):
                meal = resp["meals"][0]
        except Exception:
            pass
 
    # Step 3: Fallback — search by cuisine
    if not meal and cuisine:
        try:
            resp = requests.get(
                "https://www.themealdb.com/api/json/v1/1/filter.php",
                headers=HEADERS,
                params={"a": cuisine},
                timeout=10,
            ).json()
            if resp.get("meals"):
                meal_id = resp["meals"][0]["idMeal"]
                detail = requests.get(
                    f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}",
                    headers=HEADERS,
                    timeout=10,
                ).json()
                meal = detail["meals"][0] if detail.get("meals") else None
        except Exception:
            pass
 
    if not meal:
        return (
            f"Could not find a recipe for '{ingredient}'. "
            "Try: chicken, egg, rice, beef, pasta, salmon, tomato, or cheese."
        )
 
    # Extract recipe details
    meal_name    = meal.get("strMeal", "Unknown Meal")
    category     = meal.get("strCategory", "N/A")
    area         = meal.get("strArea", "N/A")
    instructions = meal.get("strInstructions", "")
 
    # Build ingredient list — calorie lookup per ingredient
    ingredients_lines = []
    for i in range(1, 21):
        ing     = meal.get(f"strIngredient{i}", "").strip()
        measure = meal.get(f"strMeasure{i}", "").strip()
        if not ing:
            break
        cal = fetch_calories_for_ingredient(ing)
        ingredients_lines.append(f"  • {measure} {ing} — {cal}")
 
    ingredients_block = "\n".join(ingredients_lines)
 
    # Trim instructions to a readable summary
    short_instructions = (
        instructions[:300].rsplit(".", 1)[0] + "."
        if len(instructions) > 300
        else instructions
    )
 
    return (
        f"🍽️  {meal_name}\n"
        f"Category: {category} | Cuisine: {area}\n\n"
        f"📋 Ingredients & Estimated Calories:\n"
        f"{ingredients_block}\n\n"
        f"👨‍🍳 Instructions (summary):\n{short_instructions}\n\n"
        f"ℹ️  Calorie values are per 100g of each ingredient.\n"
        f"    Values marked (est.) are from built-in estimates."
    )

if __name__ == "__main__":
    mcp.run()