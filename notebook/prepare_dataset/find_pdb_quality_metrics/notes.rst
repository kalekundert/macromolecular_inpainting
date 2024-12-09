************************
Find PDB quality metrics
************************

2024/02/14

Now that I've decided to use the PDB instead of PDB redo, I need to figure out 
how to get quality metrics such as resolution and R-factors for each structure.  
By looking at a handful of examples, I've found that this information is 
sometimes available in the mmCIF structure itself, and sometimes available in a 
separate "validation.cif" file.  My goal here is to determine what fraction of 
the database each of these approaches cover, and to find a way to cover the 
whole database if necessary.

Brainstorming
=============
Reading an article__ on how to evaluate the quality of macromolecular 
structures, I have some ideas on how to incorporate quality metrics into my 
dataset:

__ https://www.rcsb.org/docs/general-help/assessing-the-quality-of-3d-structures

- Crystal structures:

  - Resolution and R-factors are global quality metrics.

  - Real-space correlation coefficient (RSCC or RSRCC) [Shao2022]_:
    
    - How well each residue fits its density, relative to the same residue in 
      other structures.
    - Considered the best residue-level quality metric

    - Available in the validation CIF files, which not all structures have.

  - I like the idea of integrating the RSCC metric into the dataset.  
    Basically, I could exclude views with too many low-quality atoms in them 
    from the dataset, similar to how I already treat undesirable ligands.

- NMR:

  - ``_atom_site.pdbx_PDB_model_num`` is used to distinguish models.
  - ``_pdbx_nmr_representative.conformer_id`` is used to specify a "default" 
    model.  In the one case I looked at, this model was chosen by virtue of 
    having the lowest energy in whichever force field was used to make the 
    model.
  - ``_pdbx_nmr_ensemble.*`` has some quality metrics, e.g. constraint 
    violations per residue, but none were provided for the example structure I 
    was looking at.

- EM:

  - Resolution: not sure how its calculated, but considered an important 
    overall-model quality metric.

    - ``_em_3d_reconstruction.resolution``

  - Q-score: Measure of fit between atoms and density.  Supersedes "atom 
    inclusion", which is a less sophisticated way to measuring the same thing.  
    See here__ for PBDx/mmCIF details.

    __ https://www.rcsb.org/news/feature/62de9e5235ec5bb4ddb19a43

  - 

Results
=======

Diffraction
-----------
- "Diffraction" is a catch-all term for a bunch of different structure 
  determination methods, namely X-ray crystallography, electron diffraction, 
  neutron diffraction, fiber diffraction, etc.

- There appears to be only a single X-ray crystallography 
  structure---1mcd---that doesn't specify a resolution via 
  ``_refine.ls_d_res_high``.

  - This structure also does not specify a resolution via the ``_reflns`` 
    category, nor anywhere else that I can tell.  It doesn't have a validation 
    file, and no resolution is reported on the PDB website.

  - The structure also has very poor clash/Rama/sidechain metrics and is very 
    old, so I think it's probably best left out.

  - So overall, I can count on finding the resolution of each crystal structure 
    in the above location.

- Only ≈5k structures (out of 180k) are missing $R_\mathrm{free}$, 
  $R_\mathrm{work}$, or the number of reflections.  That means that I can 
  calculate the [Wang2015]_ GGOF metric in most cases, as a possible 
  alternative to resolution.

NMR
---
- Most, but not all, structures specify a representative.

  - The ``_pdbx_nmr_representative.conformer_id`` key is more common than the 
    ``_pdbx_nmr_ensemble.representative_conformer`` key.

  - For structures that don't specify a conformer, it's probably ok to pick a 
    conformer at random.  Or to just pick the first, since I bet that most of 
    the "representative" conformers will be the first.

  - In 14024 cases:

    - 10863 cases: the representative is the first model.  
    - 2413 cases: the representative is not specified.
    - 748 cases: the representative is *not* the first model.

- Are the above keys redundant?

  - No structures specify multiple values for either the above keys, so I don't 
    need to use data frames.

  - Counts:

    - "ensemble" but not "representative": 5 (2le9)
    - "representative" but not "ensemble": 10,779 (6dze)
    - "representative" and "ensemble": 1,036 (2lrw)
    - "representative" differs from "ensemble": 94 (2lr7)
    - "representative" matches "ensemble": 942 (2lrw)

  - Here are the PDBx/mmCIF dictionary descriptions of both fields:

    - ``_pdbx_nmr_representative.conformer_id``: If a member of the ensemble 
      has been selected as a representative structure, identify it by its model 
      number.

    - ``_pdbx_nmr_ensemble.representative_conformer``: The number of the 
      conformer identified as most representative.

  - I'm suspicious that the "ensemble" key is the index of the model in the 
    ensemble, but not necessarily using PDB numbering.

  - Based on the prevalence of the two keys, and the wording of the above 
    descriptions, I think it's best to only use the "representative" key.  In 
    the few thousand cases where it's not specified, I'll just choose the first 
    model.

- NOE restraint violations are not a good indicator of quality [Fowler2020]_.

  - The reason is that most NMR structure building methods simply discard any 
    restraints that are violated, so most structures have 0 violations.

  - The number of restraints is a better metric, but still not great.

  - The above paper introduces a metric called ANSURR, which compares the 
    rigidity of the protein as observed by HSQC to that predicted by an 
    elastic-network-like model.  This seems better, but unfortunately is not 
    available for most of the PDB.
  
- Restraint counts are not available for that many structures:

  - Only 4 structures specify the average number of restraints per residue  
    directly in the mmCIF file.

  - 3839/14412 NMR structures specify this number in the validation report.

- I expect that NMR structures will not be that important in my neighbor-pair 
  dataset, because they tend to be small.  But I'd like to have them in my 
  diffusion modeling dataset.

Cryo-EM
-------
- All but 43 structures specify a resolution, via 
  ``_em_3d_reconstruction.resolution``.

- 39 structures specify two or more resolutions:

  - 7jwb: In this case, it seems like two maps were somehow used for fitting; 
    one that was 3.2Å and the other that was blurred to 6Å.  Maybe this somehow 
    helps with fitting?

  - In many cases, the maps have the same resolution, e.g. 8cvn

  - I'm not totally sure what's going on here, but my instinct is to record 
    every resolution but only use the highest one.

- Q-scores are available in the validation reports.

  - ``_pdbx_vrpt_summary_em.Q_score``

  - Available for 17434/18655 (94.4%) of EM structures.

  - There's never more than one Q-score per entry.

  - None of the Q scores are out-of-bounds (i.e. greater than 1 or less than 
    -1).  Some Q scores are negative, indicating a very poor fit.

- Resolutions are also available in the validation reports.

  - The validation report provides a number of different resolutions:
    
    - FSC calculated using different cutoffs
    - The value reported by EMDB

  - These resolutions are generally similar, but can be quite different.  I 
    found 28 cases where the EMDB and FSC 0.143 cutoff resolutions differ by 
    more than 2x.

  - My initial instinct was to include the FSC 0.143 cutoff resolution along 
    with the Q-score, since this resolution is supposed to be the most 
    comparable to crystal structure resolution.  However, there are examples in 
    the database of this resolution as low as 0.01 and as high as 1666.
    
    - FSC 0.143 cutoff resolutions ("author provided" or "calculated") are 
      available for 12012/18630 (64.5%) of EM structures with validation 
      reports.

  - All of the EMDB resolutions are in the range 1.15 to 70, which seems much 
    more reasonable.  I manually checked the 5 EM structures with EMDB 
    resolutions better than 1.3Å, and they all appear to be legitimate (i.e.  
    they all have publications with titles that emphasize the unusually high 
    resolution).

    - EMDB resolutions are available for 18602/18630 (99.8%) of EM structures 
      with validation reports.

  - I think the smart thing is to record the EMDB resolution.  The other 
    resolutions are too inconsistent to rely on.  The other alternative is to 
    not record any resolutions from the validation reports, and instead to rely 
    on the resolutions specified by the mmCIF files.  I don't know how often 
    these resolution aren't identical, but I think it's probably best to err on 
    the side of ingesting more data.  For example, Q scores are only specified 
    in validation reports, so I might have reason to prefer resolutions from 
    the same source (since I would have more confidence that the two numbers 
    "go together").
    
Miscellaneous
-------------
- 49 structures do not specify ``_refine``, ``_pdbx_nmr_representative``, or  
  ``_em_3d_reconstruction``.

- These are all either powder diffraction, solution scattering, solid-state 
  NMR, or solution NMR/theoretical model structures.

- Powder diffraction:

  - Only 21 structures total, 14 are missing ``_refine``.

  - I looked at a few of those 14 manually.  Most seem to specify ``_reflns``, 
    and most of those seem to specify a resolution.  So I could ingest the 
    reflections resolution as a fallback.

- Solid state NMR:

  - 13/174 solid-state NMR structures are missing ``_pdbx_nmr_representative``.

  - This isn't really a quality metric though, and I can use ``_exptl.method`` 
    to know which structures are NMR if I want to.

- Solution scattering (SAXS):

  - I think these are basically integrative models.  As such, they are probably 
    as low quality as I can get.  I'm happy to prioritize these after every 
    other kind of data.

Clashscore
----------
- Clashscore is a MolProbity metric.  Specifically, it is the number of 
  "all-atom steric clash overlaps ≥0.4Å per thousand atoms" [Williams2018]_.

- This metric is provided for 144421 structures.  This is 95.4% of the 151334 
  structures which have validation files, and 66.9% of the 215908 structures in 
  the PDB.

- There's never more than one clash score per entry.

- I like that this same metric can be used for all types of structure; 
  crystallography, NMR, EM, protein, nucleic acid, etc.

- I don't know why this metric is missing for some structures, or even why 
  validation reports are missing for some structures.


Discussion
==========
Here's the pseudocode I have in mind for filtering structures:

- For each structure, record each of the following:

  - Diffraction quality: ``_refine.resolution``
  - NMR quality: ``exptl.method`` contains NMR, plus 
    ``_pdbx_nmr_representative.conformer_id``
  - EM quality: ``_em_3d_reconstruction``

  - Each structure can have multiple quality rows, if multiple methods used to 
    generate structure.

- When choosing a structure for each cluster, consider:

  - Experimental method, in the following order:

    - Xtal (i.e. anything with ``_refine.*``)
    - NMR
    - EM
    - Other

  - Quality metric:

    - Xtal: resolution
    - NMR: arbitrary
    - EM: resolution
    - Other: arbitrary
