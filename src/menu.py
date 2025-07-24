import yaml
import json


def get_general_menu():
    with open('./src/data/menu_virtual_items.yaml', 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return str(data)


def get_clarify_menu():
    with open('./src/data/menu_ingredients.yaml', 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return str(data)



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


    # return str(data)
