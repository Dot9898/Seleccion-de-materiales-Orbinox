

FAMILIES = ['Metales', 'Cauchos', 'Polímeros', 'Metales (ácido con cloruros)', 'Otros']

FAMILY_TO_CURVE_NAME = {
'Metales': ['316', '317', '904L', '654 SMO', '254 SMO', '1.4565 (alloy 24)', 'Dúplex 2205', 'Hierro fundido'], 
'Metales (ácido con cloruros)': ['316 (2000 ppm de cloruros)', '904L (2000 ppm de cloruros)', '654 SMO (2000 ppm de cloruros)', '254 SMO (2000 ppm de cloruros)'], 
'Polímeros': ['ETFE', 'PTFE - PFA (teflón)', 'PVDF', 'ECTFE', 'Polipropileno', 'Viton con recubrimiento de PTFE', 'Butilo con recubrimiento de PTFE'], 
'Cauchos': ['Butilo', 'Neopreno - Goma dura (ebonita)', 'Caucho natural', 'Viton', 'Hypalon', 'EPDM'], 
'Otros': ['Vidrio', 'Punto de ebullición']}

COLOR_PALETTES = {
'Metales': ['#1A5A73', '#F04A7A', '#E65A1F', '#2FA36B', '#7A72FF', '#FFD199', '#6FD9A6', '#4A5A63'], 
'Metales (ácido con cloruros)': ['#2C8DBF', '#D43A6A', '#FF7A2A', '#1F7A5C'], 
'Polímeros': ['#33B5FF', '#FF7FA3', '#C24A1F', '#3FC27D', '#8A4DE0', '#FFA94D', '#BFEBDD'], 
'Cauchos': ['#66F0FF', '#FFB3C7', '#8C3A1A', '#6FD9A6', '#6C63FF', '#FFF0D9'], 
'Otros': ['#7A72FF', '#D0D8DC']}

MONOTONE_COLOR_PALETTES = { #unused
'Metales': ['#1A5A73', '#2C8DBF', '#33B5FF', '#66F0FF', '#7A72FF', '#8A4DE0', '#C5A6FF', '#E6C2FF'], 
'Metales (ácido con cloruros)': ['#D43A6A', '#F04A7A', '#FF7FA3', '#FFB3C7'], 
'Polímeros': ['#8C3A1A', '#C24A1F', '#E65A1F', '#FF7A2A', '#FFA94D', '#FFD199', '#FFF0D9'], 
'Cauchos': ['#1A5A4A', '#1F7A5C', '#2FA36B', '#3FC27D', '#6FD9A6', '#BFEBDD'], 
'Otros': ['#4A5A63', '#D0D8DC']}

CURVE_NAME_TO_COLOR = {
material: color
for family, materials in FAMILY_TO_CURVE_NAME.items()
for material, color in zip(materials, COLOR_PALETTES[family])}

FILE_NAME_TO_CURVE_NAME = {
'Glass': 'Vidrio', 
'ETFE': 'ETFE', 
'PVDF': 'PVDF', 
'ECTFE': 'ECTFE', 
'PTFE-PFA': 'PTFE - PFA (teflón)', 
'Butyl-rubber': 'Butilo', 
'PPL': 'Polipropileno', 
'Hard rubber - neoprene': 'Neopreno - Goma dura (ebonita)', 
'Cast iron': 'Hierro fundido', 
'Boiling point': 'Punto de ebullición', 

'Q': 'Caucho natural', 
'B-300-325': 'EPDM', 
'237': 'Hypalon', 
'226': 'Viton', 
'214-226': 'Viton con recubrimiento de PTFE', 
'214-300': 'Butilo con recubrimiento de PTFE', 

'AISI 316': '316', 
'ASTM 317L': '317', 
'904L': '904L', 
'254 SMO': '254 SMO', 
'654 SMO': '654 SMO', 
'Sandvik SAF 2205': 'Dúplex 2205', 
'4565': '1.4565 (alloy 24)', 

'AISI 316 2000': '316 (2000 ppm de cloruros)', 
'904L 2000': '904L (2000 ppm de cloruros)', 
'654 SMO 2000': '654 SMO (2000 ppm de cloruros)', 
'254 SMO 2000': '254 SMO (2000 ppm de cloruros)'}










