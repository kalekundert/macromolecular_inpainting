********************************
Find entities without assemblies
********************************

While parsing the subchain/chain/entities/assemblies from the PDB, I 
encountered two cases (3km0, 3tt8) where an entity was not present in any 
biological assemblies.  The 3km0 case was a clear error, and I reported it to 
the PDB.  The 3tt8 was not a clear error.  It was a structure of insulin bound 
to two copper ions, but insulin doesn't bind copper physiologically, so in some 
sense it's right that the copper ions wouldn't be in the biological assembly.

My goal is to see how common these structures are, and possibly to identify any 
more errors.

Results
=======

.. datatable:: entities_without_assemblies.csv

  Note: I generated the CSV file being displayed above after incorporating 
  fixes made to the PDB for some of the structures listed below.

Errors
------
- 7rqd:

  - Missing: entity 60; chain 1z,2z; subchain MVC,TVC: chloramphenicol 
    (ribosome inhibitor)
  - Missing: entity 61; chain 1z; subchains NVC,OVC: arginine
  - Missing: entity 62; chain 1z,2z; subchains PVC,QVC,RVC,SVC,UVC,VVC:
    '(4S)-2-METHYL-2,4-PENTANEDIOL'

  - Chloramphenicol: known ribosomal inhibitor, bound in the middle of the 
    ribosome, and mentioned in the title of the structure.  I think this should 
    be part of the biological assembly.
  - Arginine: Bound to the surface of one ribosome in the asymmetric unit, but 
    not the other.  I think this is a crystallization artifact, and makes sense 
    to exclude from the biological assembly.
  - 2-methyl-2,4-pentanediol: a common precipitant and cryoprotectant, 
    according to wikipedia.  I think this also makes sense to exclude from the 
    biological assembly.

- 7nbu:

  - Present: entity 37, subchain KA: "50S ribosomal protein L16,50S ribosomal 
    protein L31"
  - Missing: entity 38, subchain LA: "50S ribosomal protein L16"

  - I was worried that entities 37 and 38 might be two copies of the same 
    protein, since they share part of their name.  But they're definitely not.  
    They're two chains that fold together to form a single core.  No way should 
    one be present without the other.

- 8pt6:

  - Missing: chain F, entity 5, subchains F,K: cytosine monophosphate, plus a 
    Mg ion.

- 6zsb:

  - Missing: entity 87, subchain NC, chain A: Quinupristin (ribosome-inhibiting 
    antibiotic)
  - Maybe the authors left the antibiotic out of the biological assembly, 
    because it seems like their focus was just getting a structure of the 
    ribosome.  But it's there, and it affects how the ribosome functions, so I 
    think it should be part of the assembly.

- 6zsc:

  - Missing: entity 86: Quinupristin (ribosome-inhibiting antibiotic)
  - Seems the same as 6zsb, but with slightly different indexing.

- 6zsd:

  - Missing: entity 88: Quinupristin (ribosome-inhibiting antibiotic)
  - Seems the same as 6zsb, but with slightly different indexing.

- 3nqa, 3nqc:

  - Missing: entity 2, chain I, subchain C-D+G: uridine monophosphate (BMP)

- 3nqd, 3nqg:

  - Missing: entity 2, chain I, subchain C-D+H: uridine monophosphate (BMP)
  - Missing: entity 3, chain C, subchain E: glycerol
  - BMP is an inhibitor; focus of publication

- 3nqm:

  - Missing: entity 2, chain I, subchains C-D+K: uridine monophosphate (BMP)
  - Missing: entity 3, chain D, subchains E-H+J: glycerol

- 3nq6:

  - Missing: entity 2, chain I, subchain C-D+I: uridine monophosphate (UP6)
  - Missing: entity 3, chain C, subchain E+H: glycerol

- 6jn0:

  - Missing: entity 2, chain B, subchain B+E: noncanonical tripeptide
  - This peptide is the focus of the structure.

- 7oq8

  - Missing: entities 1+3-5
  - The biological assembly only includes a peptide and some nearby water.  
    It's missing the protein itself, two cofactors, and several salt ions!
    
- 3tdu:

  - Missing: entity 2, chain C+D, subchain C-D+I-J: cullin-1, a ubiquitin 
    ligase
  - Structure is supposed to be of a complex involving cullin-1, so it should 
    be present in the assembly.

- 6ml1:

  - Missing: entity 3, chain G, subchain E: 'Proteolyzed N-terminal tag of 
    Ubv.15.1a construct' (40 residue peptide, only 5 residues resolved)
  - This peptide is mentioned in the title of the structure, so I think it's 
    important.

Maybe errors
------------
- 1ts6:

  - Missing: entity 3, subchain C: water
  - Structure has 2 models, only the 2nd has water.
  - The biological assembly also doesn't have water.

- 2k9y:

  - Missing: entity 2, subchain C-D: water
  - Structure has 17 models; only the 16th has water
  - The biological assembly also doesn't have water.

- 7a4p:

  - Missing: entity 20: 'Photosystem I reaction center subunit VI --- 
    chloroplastic-like'

  - This entity is not present in the structure at all; there are no atomic 
    coordinates associated with this entity.
  - I guess this is an error, since it doesn't really make sense to define an 
    entity that's not actually in the structure.  But on the other hand, it's 
    not like the biological assembly is missing something that would otherwise 
    be there.

- 3ndb:

  - Missing: entity 4, chain D, subchain D: phosphate ion
  - Phosphate doesn't appear to be in a "binding site".
  - Associated publication doesn't mention phosphate.
  - I suspect this isn't a real biological interaction, but I'm not 100% sure.

- 7asp:

  - Missing: entity 46, subchain UA: '50S ribosomal protein L5'
  - This is a full (≈150 aa) protein that's just missing from the assembly
  - It is on the exterior of the structure, so maybe it's not always present?

- 3jxj:

  - Missing: entity 2, chains C-D, subchains C-D: phosphate ions
  - Phosphate doesn't appear to be in a "binding site".
  - Associated publication doesn't mention phosphate.
  - I suspect this isn't a real biological interaction, but I'm not 100% sure.

- 3ttb:

  - Missing: entity 3, chains E-F, subchains E-F: copper ions
  - Insulin does not bind to copper in physiological conditions, but this 
    structure was deliberately solved in the present of copper.
  - Not sure how to interpret this.

Not errors
----------
- 7xmw:

  - Missing: entity 4: selenium ion
  - The ion is really far (>170Å) any other atom.  
  - The ion itself seems like some sort of mistake.  There's no way it's 
    actually that far away from everything.  But putting that aside, it's 
    definitely not part of the biological assembly.

- 3b7a:

  - Missing: entity 3, subchains D-G, chain X: acetone (and water)
  - Acetone is clearly a solvent
  - Ethanol (a very similar molecule) is a focus of the structure, and is 
    present in the biological assembly.

- 3dge:

  - Missing: entity 5, chain N, subchain I: citrate
  - Citrate is part of the crystallization buffer.  No indication that it has 
    any biological role.

- 3m43:

  - Missing: entity 2, chain I, subchain C-E: glycerol
  - Nonspecifically-bound cryoprotectant; not biological.

Discussion
==========
I'm going to submit to errors I found to the PDB.  If they get fixed quickly, 
I'll just wait until the corrections are released, then re-run my analysis.  If 
not, I can take the time to add manual overrides.

Not really related to anything, but I wish more structure authors bothered to 
exclude clear artifacts, like glycerol, PEG, etc., from their biological 
assemblies.
