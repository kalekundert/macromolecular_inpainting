***********************************
Find models without quality metrics
***********************************

In PDB REDO, 4oz4 has a "final" mmCIF model, but not a ``data.json`` file 
containing all the relevant quality metrics.  When I go to the PDB REDO webpage 
for this structure, I find that (i) the model model is marked as "obsolete" but 
(ii) all the quality metrics are present.

Here I want to determine two things:

- How many PDB REDO models are missing quality metadata?
- Is this metadata available elsewhere?

.. update:: 2024/02/14

  I emailed the PDB-REDO maintainers about this, and I was told that obsolete 
  strutures are those that have been removed from the PDB for one reason or 
  another, including (in some cases) data fabrication.  I was also told that 
  all structures without ``data.json`` files are obsolete, and that such 
  structures should not be used.
