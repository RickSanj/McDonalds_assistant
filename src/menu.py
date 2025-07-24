import yaml


def get_menu():
    with open('./src/data/menu_virtual_items.yaml', 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return str(data)
