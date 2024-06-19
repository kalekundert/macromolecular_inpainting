from pymol import cmd
from math import pi

def select_neighbors(xyz, radius_A=5, name='neighbors'):
    radius_A = float(radius_A)

    if ' ' in xyz:
        xyz = [float(x) for x in xyz.split()]
    else:
        xyz = cmd.centerofmass(xyz)

    cmd.delete('xyz')
    cmd.pseudoatom('xyz', pos=xyz)
    cmd.show('spheres', 'xyz')
    cmd.select(name, f'all within {radius_A} of xyz')

    counts = {
        'atoms': 0,
        'weighted_atoms': 0,
    }
    cmd.iterate(
            name,
            'counts["atoms"] += 1; counts["weighted_atoms"] += q',
            space=locals(),
    )

    volume_nm3 = 4/3 * pi * (radius_A / 10)**3

    print(f"By atom:      {counts['atoms'] / volume_nm3:.2f} atoms/nm³")
    print(f"By occupancy: {counts['weighted_atoms'] / volume_nm3:.2f} atoms/nm³")

pymol.cmd.extend('select_neighbors', select_neighbors)

