# miniChemistry 1.1.0

## New features

- Several new reaction types were added: IonGroupReaction, HalfReaction, MathReaction. Mere Reaction was renamed into MolecularReaction
- Added a Particle subclass IonGroup that represents an partially dissociated molecule (such as $HSO_4^-$)

## Improvements

- Reorganized files to add more readability and easier access to new features
- SolubilityTable was rewritten and completely moved to pandas df instead of SQLite db
- AbstractReaction class has beed added. Each reaction class must inherit from it for compatibility with methods that use Reactions
