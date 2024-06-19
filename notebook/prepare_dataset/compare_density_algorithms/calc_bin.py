# Below is the initial code I wrote to implement this algorithm in mmt.  It's 
# not finished, but it may be a useful starting point if I ever come back to 
# this.


def calc_grid_aligned_densities_atoms_nm3(atoms, bin_size_A, bin_subdivisions):
    """
    Divide space into bins of the given size, and calculate the density (in 
    units of atoms/nm³) in each one.

    This is much faster, but slightly less accurate, than calculating densities 
    at individual points of interest.  The reason is that every atom is 
    considered exactly once.  To estimate densities at points that aren't on 
    the grid, fast linear interpolation can be used.
    """

    def bin_atoms(dx, dy, dz):

        def get_bin_expr(col, offset):
            scaled_coords = pl.col(col) / bin_size_A
            shifted_coords = scaled_coords - offset / subdivisions
            return subdivisions * shifted_coords.floor().cast(int) + offset

        return (
                atoms
                .with_columns(
                    x_bin=get_bin_expr('x', dx),
                    y_bin=get_bin_expr('y', dy),
                    z_bin=get_bin_expr('z', dz),
                )
                .group_by(['x_bin', 'y_bin', 'z_bin'])
                .agg(
                    (pl.col('occupancy').sum() / volume_nm3)
                    .alias('atoms_per_nm3')
                )
        )

    densities_atoms_nm3 = pl.concat([
        bin_atoms(dx, dy, dz)
        for dx, dy, dz in offsets
    ])

    bins = df.select('x_bin', 'y_bin', 'z_bin').to_numpy()
    min_bin = np.min(bins, axis=0)
    max_bin = np.max(bins, axis=0)

    grid_shape = max_bin - min_bin + 1
    grid_values = np.zeros(grid_shape)
    grid_values[*(bins - min_bin).T] = df['atoms_per_nm3']
    grid_points = [
        np.arange(min_bin[i], max_bin[i] + 1)
        for i in range(3)
    ]

    # mesh grid
    # density
    # overlapping bins
    #
    # on grid, not on sphere
    #
    # evaled at points on grid, and also using cubic volumes

    # calc bins and calc "point" have to go together; very coupled logic.  So 
    # output needs to be points/values.  Inputs should be size and 
    # subdivisions.
    pass


