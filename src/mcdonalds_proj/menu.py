import yaml
import json

SMALL_COEF = 0.75
LARGE_COEF = 1.25


class Menu():
    def __init__(self) -> None:
        self.menu = process_yaml_menus()


def process_yaml_menus():
    json_data = {
        "virtual": {},
        "combos": {},
        "drinks": {},
        "burgers": {},
        "fries": {},
        "desserts": {},
        "deals": {},
        "sauces": {},
        "ingredients": {}
    }

    # menu_virtual_items
    with open('./src/data/menu_virtual_items.yaml', 'r') as f:
        data = yaml.safe_load(f)

    if 'items' in data and isinstance(data['items'], list):
        for item in data['combos']:
            if item.get("virtual") is True:
                possible_items = item.get("possible_items", [])
                json_data["virtual"]['combos'] = possible_items
            else:
                name = item.get("name")
                price = item.get("price")
                slots = item.get("slots", {})
                fries = slots.get("fries", [])
                drinks = slots.get("drinks", [])

                json_data["combos"][name] = {
                    "size_price": {
                        "small": round(SMALL_COEF*price, 2),
                        "medium": price,
                        "large": round(LARGE_COEF*price, 2)
                    },
                    "fries": fries,
                    "drinks": drinks
                }

        for item in data['items']:
            if item.get("virtual") is True:
                name = item.get("name")
                possible_items = item.get("possible_items", [])
                json_data["virtual"][name] = possible_items
            else:
                name = item.get("name")
                category = item.get("category")
                price = item.get("price")
                properties = item.get("properties", [])

                if category in ['burgers', 'desserts']:
                    json_data[category][name] = {
                        "price": price
                    }

                elif category in ['drinks', 'fries']:
                    size_property = next(
                        (p for p in properties if p.get("name") == "size"), None)
                    sizes = size_property.get(
                        "values", []) if size_property else ['default']

                    size_price = {size: price for size in sizes}
                    for size in size_price.keys():
                        if size == "small":
                            size_price["small"] = round(SMALL_COEF *
                                                        size_price["small"], 2)
                        if size == "large":
                            size_price["large"] = round(
                                LARGE_COEF * size_price["large"], 2)

                    json_data[category][name] = {
                        "size_price": size_price
                    }
    # menu_deals
    with open('./src/data/menu_deals.yaml', 'r') as f:
        data = yaml.safe_load(f)

    if 'deals' in data and isinstance(data['deals'], list):
        for item in data['deals']:
            name = item.get("name")
            possible_items = item.get("possible_items", [])
            json_data["deals"][name] = possible_items

    # menu_upsells
    with open('./src/data/menu_upsells.yaml', 'r') as f:
        data = yaml.safe_load(f)

    if 'combos' in data and isinstance(data['combos'], list):
        for item in data['combos']:
            name = item.get("name")
            slots = item.get("slots", {})
            sauces = slots.get("sauces", [])
            possible_items = sauces.get("options", [])
            json_data["combos"][name]['sauces'] = possible_items

    if 'items' in data and isinstance(data['items'], list):
        for item in data['items']:
            name = item.get('name')
            category = item.get('category')
            if category == 'sauces':
                price = item.get("price")
                json_data["sauces"][name] = price
    # menu_ingredients
    with open('./src/data/menu_ingredients.yaml', 'r') as f:
        data = yaml.safe_load(f)

    if 'ingredients' in data and isinstance(data['ingredients'], list):
        for item in data['ingredients']:
            name = item.get("name")
            price = item.get("price")
            json_data["ingredients"][name] = price
    if 'items' in data and isinstance(data['items'], list):
        for item in data['items']:
            name = item.get('name')
            category = item.get('category')
            default_ingredients = item.get('default_ingredients', [])
            possible_ingredients = item.get('possible_ingredients', [])
            json_data[category][name]['default_ingredients'] = default_ingredients
            json_data[category][name]['possible_ingredients'] = possible_ingredients

    with open("./src/data/test.json", "w") as json_file:
        json_file.write(json.dumps(json_data, indent=4))

    return json_data
