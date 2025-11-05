
#encoding: utf-8

from pathlib import Path
import csv
from unidecode import unidecode
from functools import lru_cache

ROOT_PATH = Path(__file__).resolve().parent.parent


class Material:

    all = []
    
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return(self.name)
    
    def __eq__(self, other):
        if isinstance(self, Material) and self.name == other.name:
            return(True)
        return(False)
    
    def __hash__(self):
        return(hash(self.name))

class Fluid: #arreglar conversión de pdf a excel

    all = []
    initials = set()
    families = set()

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return(self.name)
    
    def __eq__(self, other):
        if isinstance(self, Fluid) and self.name == other.name:
            return(True)
        return(False)
    
    def __hash__(self):
        return(hash(self.name))
    
    def materials_and_families_to_show(self, materials, only_inOrbinox, only_resistant):
        
        materials_to_show = []

        if only_resistant:

            max_resistance_inOrbinox = Resistance(0, 1)
            max_resistance_general = Resistance(0, 1)

            for material in materials:
                if material.is_inOrbinox and self.resistance[material] > max_resistance_inOrbinox:
                    max_resistance_inOrbinox = self.resistance[material]
                if self.resistance[material] > max_resistance_general:
                    max_resistance_general = self.resistance[material]
        
            for material in materials:

                if only_inOrbinox:
                    if material.is_inOrbinox and self.resistance[material].quality == max_resistance_inOrbinox.quality:
                        materials_to_show.append(material)
                
                else:
                    if self.resistance[material].quality == max_resistance_general.quality:
                        materials_to_show.append(material)

        else:

            for material in materials:

                if only_inOrbinox:
                    if material.is_inOrbinox and self.resistance[material].quality > 0:
                        materials_to_show.append(material)

                else:
                    if self.resistance[material].quality > 0:
                        materials_to_show.append(material)

        families_to_show = set()
        for material in materials_to_show:
            families_to_show.add(material.family)
        
        return(materials_to_show, families_to_show)

class Resistance:

    resistance_details = ({(4, 3): 'Resistente', (4, 2): 'Resistente hasta 48 C', (4, 1): 'Resistente hasta 22 C', 
                           (3, 3): 'Aceptable', (3, 2): 'Aceptable hasta 48 C', (3, 1): 'Aceptable hasta 22 C', 
                           (2, 3): 'Poco resistente', (2, 2): 'Poco resistente hasta 48 C', (2, 1): 'Poco resistente hasta 22 C',
                           (1, 3): 'No resistente', (0, 3): 'Sin datos', (0, 2): 'Sin datos', (0, 1): 'Sin datos'})
    
    def __init__(self, quality, temperature): #quality (0, 1, 2, 3, 4) = white, orange, yellow, blue, green - temperature (0, 1, 2) = always, up to 22, up to 48
        self.quality = quality
        self.temperature = temperature
        self.details = Resistance.resistance_details[(quality, temperature)]
    
    def __repr__(self):
        return(self.details)

    def __gt__(self, other):
        if not isinstance(other, Resistance):
            return(False)
        else:
            if self.quality > other.quality:
                return(True)
            elif self.quality == other.quality:
                if self.temperature > other.temperature:
                    return(True)
            return(False)


def clean_string(string):
    string = ''.join(char for char in string if char.isalnum()) #Elimina carácteres no alfanuméricos
    string = unidecode(string) #Elimina acentos
    string = string.lower()
    return(string)

def _load_data():

    with open(ROOT_PATH / 'data' / 'values.csv', mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if csv_values.line_num == 1: #Headers
                is_material_inOrbinox = line[3:]
                continue
            elif csv_values.line_num == 2:
                material_families = line[3:]
            elif csv_values.line_num == 3:
                for material_name in line:
                    if line.index(material_name) >= 3:
                        material = Material(material_name) #agregar duplex 2205, super duplex 2507
                        Material.all.append(material)
                        material.index = Material.all.index(material)
                continue
            else:
                fluid_name = line[2]
                fluid = Fluid(fluid_name)
                Fluid.all.append(fluid)
                fluid.initial = unidecode(fluid.name)[0].upper()
                Fluid.initials.add(fluid.initial)
                fluid.index = csv_values.line_num - 4
                fluid_family = line[1]
                fluid.family = 'Otros' if fluid_family == '' else fluid_family
                Fluid.families.add(fluid.family)
                fluid.temperature = {}
                for material in Material.all:
                    temperature = line[3 + material.index]
                    fluid.temperature[material] = int(temperature) if temperature != '' else 3
    
    for material in Material.all:
        material.is_inOrbinox = False if is_material_inOrbinox[material.index] == 'No' else True
        material.family = material_families[material.index]

    fluid_name_to_Fluid = {}
    for fluid in Fluid.all:
        fluid_name_to_Fluid[fluid.name] = fluid
    material_name_to_Material = {}
    for material in Material.all:
        material_name_to_Material[material.name] = material

    with open(ROOT_PATH / 'data' / 'colors.csv', mode ='r', encoding = 'utf-8') as file:
        csv_colors = csv.reader(file)
        for line in csv_colors:
            if csv_colors.line_num in [1, 2, 3]: #Headers
                continue
            fluid = Fluid.all[csv_colors.line_num - 4]
            fluid.quality = {}
            fluid.resistance = {}
            for material in Material.all:
                quality = int(line[3 + material.index])
                fluid.quality[material] = quality
                fluid.resistance[material] = Resistance(fluid.quality[material], fluid.temperature[material])

    fluids = sorted(Fluid.all, key = lambda fluid: clean_string(fluid.name)) #Los índices fluid.index y material.index quedan inutilizables
    materials = sorted(Material.all, key = lambda material: clean_string(material.name))
    fluid_families = sorted(Fluid.families, key = lambda family: clean_string(family))
    fluid_initials = sorted(Fluid.initials)

    return({'fluids': fluids, 
            'materials': materials, 
            'fluid_families': fluid_families, 
            'fluid_initials': fluid_initials, 
            'fluid_name_to_Fluid': fluid_name_to_Fluid, 
            'material_name_to_Material': material_name_to_Material})

def make_fluid_search(fluids):
    def fluid_search(searchterm):
        if type(searchterm) is not str:
            return([])
        searchterm = clean_string(searchterm)

        equal_start_search_results = []
        for fluid in fluids:
            fluid_name = clean_string(fluid.name)
            if fluid_name.startswith(searchterm):
                equal_start_search_results.append(fluid.name)
        
        other_results_searchterm_in_fluid_name = []
        for fluid in fluids:
            fluid_name = clean_string(fluid.name)
            if len(searchterm.strip()) >= 3 and searchterm in fluid_name and fluid.name not in equal_start_search_results:
                other_results_searchterm_in_fluid_name.append(fluid.name)
        
        other_results_searchterm_word_in_fluid_name = []
        for fluid in fluids:
            fluid_name = clean_string(fluid.name)
            for word in searchterm.split():
                if len(word) >= 3 and word in fluid_name and fluid.name not in equal_start_search_results + other_results_searchterm_in_fluid_name:
                    other_results_searchterm_word_in_fluid_name.append(fluid.name)


        equal_start_search_results = sorted(equal_start_search_results)
        other_results_searchterm_in_fluid_name = sorted(other_results_searchterm_in_fluid_name)
        other_results_searchterm_word_in_fluid_name = sorted(other_results_searchterm_word_in_fluid_name)
        search_results = equal_start_search_results + other_results_searchterm_in_fluid_name + other_results_searchterm_word_in_fluid_name
        return(search_results)
    return(fluid_search)

@lru_cache(maxsize = 1)
def get_data(edit_this_string_to_force_cache_clear_in_streamlit_cloud = 'v2'):
    return(_load_data())



def test():
    data = _load_data()
    fluids = data['fluids']
    initials = set()
    for fluid in fluids:
        initials.add(fluid.name[0])
    initials = sorted(initials)
    print(initials)
    #for fluid in fluids:
    #    print(fluid)

#unidecode(string)


#test()

#'fluids', 'materials', 'fluid_families', 'fluid_name_to_Fluid', 'material_name_to_Material'

















