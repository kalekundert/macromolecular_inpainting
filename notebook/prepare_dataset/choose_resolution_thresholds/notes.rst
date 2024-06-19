****************************
Choose resolution thresholds
****************************

When picking assemblies to include in the dataset, one of the most important 
quality metrics is resolution.  My goal here is to decide how to use this 
metric.  Specifically, I want to see the distribution of resolutions for 
different types of structures, and I want to read about what modeling 
techniques are used at different resolutions.

Background
==========
- I want to distinguish between models that are primarily determined by 
  experimental data, and models that are primary determined by external 
  knowledge, e.g. homology modeling, physics-based simulations, etc.

- [Malhotra2019]_ gives the following resolution thresholds:
  
  - High resolution (<4Å): sufficient information to build atomic model 
    directly from density.

  - Intermediate resolution (4-10Å): can't build model directly from density; 
    need initial model (either existing structure, homology model, or 
    AlphaFold).

  - Low resolution (>10Å): even fitting atomic models into the map is 
    challenging.

Results
=======
Resolution:

.. figure:: resolution_cdf.svg

- The 4Å cutoff recommended by [Malhotra2019]_ includes >99% of all crystal 
  structures, and ≈75% of all EM structures.

Discussion
==========
- First, pick from structures with resolutions better than 4Å, sorted by 
  resolution.

  - This threshold identifies structures that are primarily determined by the 
    experimental data.

  - All NMR structures are excluded from this group, since they don't have 
    resolutions.

- Discard structures with >10Å resolution

  - A bit arbitrary, but discards structures that really aren't constrained at 
    an atomic level.  I think AlphaFold also used a cutoff similar to this.

  - Of course, this will leave even-worse structures that simply don't have 
    resolutions at all.  I'm not including NMR structures in this group, since 
    they're fairly high resolution, but I am thinking about homology models 
    constrained by SAXS or FRET data, or which I think there are a few in the 
    PDB.

- Second, sort by clashscore

  - This is a way to "naturally" mix in NMR structures, instead of having them 
    all come at once.  Plus, clashscore is a good metric, so I don't want it to 
    be too far down the tie-breaker list.

- Break ties by $R_\mathrm{free}$, Q-scores, and restraint numbers, then by 
  date, then by PDB id.

  - Including PDB ID at the end guarantees a deterministic ordering.

  - Choosing the order of the $R_\mathrm{free}$, Q-scores, and restraint 
    comparisons will determine my relative "preference" for each method.
    
  - I think it'd be best to have NMR first, because I think I'd prefer an NMR 
    structure over a 4Å crystal structure.

