import xml.etree.ElementTree as ET


class LiveSplitData():
    def __init__(self, path: str):
        self.set_XML_root(path)

    def set_XML_root(self, path):
        xtree = ET.parse(path)
        self.xroot = xtree.getroot()

    def get_subcategory(self) -> str:
        category = self.xroot.find('CategoryName').text
        vars = self.xroot.find('Metadata').find('Variables')

        variables = ''
        for var in vars:
            if var.text.lower() == 'yes':
                variables += f"{var.attrib.get('name')}, "
            elif var.text.lower() == 'no':
                continue
            else:
                variables += f'{var.text}, '
            
        if variables != '':
            category = f'{category} ({variables.removesuffix(", ")})'

        return category
    
    def get_game_name(self) -> str:
        return self.xroot.find('GameName').text

    def get_split_names(self) -> list:
        return [segment.find('Name').text for segment in self.xroot.find('Segments')]