from pymol import cmd

def select_neighbors(xyz, radius=5, name='neighbors'):
    if ' ' in xyz:
        xyz = [float(x) for x in xyz.split()]
    else:
        xyz = cmd.centerofmass(xyz)

    cmd.delete('xyz')
    cmd.pseudoatom('xyz', pos=xyz)
    cmd.show('spheres', 'xyz')
    cmd.select(name, f'all within {radius} of xyz')

    counts = {
        'atoms': 0,
        'weighted_atoms': 0,
    }
    cmd.iterate(
            name,
            'counts["atoms"] += 1; counts["weighted_atoms"] += q',
            space=locals(),
    )
    print(f"{counts['atoms']} atoms within {radius}Å")
    print(f"{counts['weighted_atoms']:.2f} occupancy-weighted atoms within {radius}Å")

pymol.cmd.extend('select_neighbors', select_neighbors)

