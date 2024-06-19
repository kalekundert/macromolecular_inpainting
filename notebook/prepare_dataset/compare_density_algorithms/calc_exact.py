import macromol_dataframe as mmdf
import numpy as np
import timerit

from utils import *
from tqdm import tqdm


cif = mmdf.read_mmcif('4w4g.cif.gz')
#cif = mmdf.read_mmcif('7y7a.cif.gz')

atoms = mmdf.make_biological_assembly(
        cif.asym_atoms,
        cif.assembly_gen,
        cif.oper_map,
        assembly_id='1',
)
kd_tree = make_kd_tree(atoms)

for _ in timerit:
    coords_A = calc_zone_centers_A(atoms, 10)

for coord_A in tqdm(coords_A):
    calc_density_atoms_nm3(atoms, kd_tree, coord_A, 15)

