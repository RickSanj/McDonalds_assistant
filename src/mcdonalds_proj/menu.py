import yaml
import json

class Menu():
    def __init__(self) -> None:
        self.menu = get_general_menu()

def get_general_menu():
    with open('./src/data/parsed_menu.json', 'r') as file:
        data = json.load(file)
    return data

def get_clarify_menu():
    with open('./src/data/parsed_menu.json', 'r') as file:
        data = json.load(file)
    return data

def get_price_list():
    # with open('./src/data/menu_virtual_items.yaml', 'r') as f:
    #     data = yaml.full_load(f)


    # output = {
    #     'UserName': data.get('UserName'),
    #     'Password': data.get('Password'),
    #     'phone': data.get('Phone'),
    #     'Skills': ' '.join(data.get('Skills', []))
    # }
    # 👇 Load as Python dict

    with open('./src/data/menu_virtual_items.yaml', 'r') as f:
        data = yaml.safe_load(f)


    json_str = json.dumps(data, indent=2)

    print(json_str)  # OR just use `data` as a dict

def expand_sizes(item):
    """Return a dict of size-specific pricing if applicable."""
    base_price = item["price"]
    sizes = {}
    if "properties" in item:
        for prop in item["properties"]:
            if prop["name"] == "size":
                for size in prop["values"]:
                    sizes[size] = base_price
    return sizes if sizes else {"default": base_price}


def parse_yaml_menus():
    with open('./src/data/menu_virtual_items.yaml', "r") as f:
        data = yaml.safe_load(f)

    parsed_menu = {
        "combos": {},
        "drinks": {},
        "burgers": {},
        "fries": {},
        "desserts": {},
        "deals": {},
        "ingredients": {}
    }

    # Process combos
    for combo in data.get("combos", []):
        parsed_menu["combos"][combo["name"]] = {
            "price": combo["price"],
            "fries": combo["slots"].get("fries", []),
            "drinks": combo["slots"].get("drinks", []),
            "sauces": []  # Sauces not present in original YAML
        }

    # Process items
    for item in data.get("items", []):
        category = item["category"]
        name = item["name"]

        item_entry = {
            "default_ingredients": [],         # Extend if ingredients appear later
            "possible_ingredients": []
        }

        sizes = expand_sizes(item)
        if "default" in sizes:
            item_entry["price"] = sizes["default"]
        else:
            item_entry["size_price"] = sizes

        if category == "drinks":
            parsed_menu["drinks"][name] = item_entry
        elif category == "burgers":
            parsed_menu["burgers"][name] = item_entry
        elif category == "fries":
            parsed_menu["fries"][name] = item_entry
        elif category == "desserts":
            parsed_menu["desserts"][name] = item_entry

    # Process deals
    for deal in data.get("deals", []):
        parsed_menu["deals"][deal["name"]] = {
            "price": None,  # Not specified in the input
            "possible_items": deal.get("possible_items", [])
        }

    # Optional: save as JSON
    with open("parsed_menu.json", "w") as f:
        json.dump(parsed_menu, f, indent=2)

    # Optional: print for preview
    print(json.dumps(parsed_menu, indent=2))

