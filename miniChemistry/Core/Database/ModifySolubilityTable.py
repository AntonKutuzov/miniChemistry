"""
Filling in the solubility table by hand would take a lot of time. Also, in the case of a mistake it would be required
to erase it and write the data again. A much more convenient and fast way is to automate this process by using common
patterns from chemistry.

The most frequently used substances which do not follow any specific pattern are given in SolubilityTable.xlsx file and
are read from there by pandas package. Some less common substances (also ions) are listed here in the code.

Since in miniChemistry solubility table also plays an important role of ions database, all possible ions are added
based on their oxidation states. In this case possible cations are bound to oxygen which always have an oxidation state
of -2 (except for rare cases that are not discussed here). In the case of anions, they are bound to hydrogen, which
always have an oxidation state of +1 (again, except for some specific cases, which are not discussed here).

IMPORTANT PATTERNS USED
- all nitrates are soluble (nitrate = anions is NO3(-))
- all sodium compounds are soluble (cation = Na(+))
- all acids are soluble except for H2SiO3 (acid = cation is H(+))
- most nonmetal oxides are gases and hence have undefined solubility* (solubility="ND")

* NOTE: Gases of course also have solubility in water, however their solubilities differ so much from solubilities of
bases, acids and salts that they are not included in solubility table. In reality, solubilities of gases are usually
obtained from solubility curves. In this module the oxides are added to add the anions, i.e. to make the table a
database. Hence, their solubility is just set to ND (no data).
"""

from miniChemistry.Core.Database.stable import SolubilityTable
import miniChemistry.Core.Database.ptable as pt
from miniChemistry.Core.Substances import Ion
from chemparse import parse_formula
import pandas as pd
from miniChemistry.Core.Tools.parser import parse_ion


# ============================================================================== CREATING IONS BASED ON OXIDATION STATES
"""
Ions based on the oxidation states of the elements can, indeed, be created only for single-element ions that consist
of the chosen element. So, the ions created for each element will be ions with all possible non-zero oxidation states of
this element. For example, since sulfur (S) is in group 6A in the periodic table, the possible oxidation states and thus
the list of possible ions are
-2, 0, 2, 4, 6
removing zero we get a list of ions
S(-2), S(2), S(4), S(6)

NOTE: remember that metals can only have positive oxidation states of the respective group.
"""
# creation of metal and nonmetal ions (with positive and negative oxidation numbers separately)
print('Creating list of metal cations...')
metals = list()

for metal in pt.METALS:
    oxidation_states = metal.oxidation_states

    for ost in oxidation_states:
        if ost != 0:
            i = Ion.from_string(metal.symbol, ost)
            metals.append(i)

print('Creating lists of nonmetal cations and anions...')
positive_nonmetals = list()
negative_nonmetals = list()

for nonmetal in pt.NONMETALS:
    # covering special cases
    if nonmetal == pt.F:    # the only possible non-zero oxidation state of fluorine is -1
        i = Ion.from_string('F', -1)
        negative_nonmetals.append(i)
        continue
    elif nonmetal == pt.O:  # even though oxygen can have different oxidation states, here we assume the only non-zero
                            # oxidation state it has is -2.
        i = Ion.from_string('O', -2)
        negative_nonmetals.append(i)
        continue

    # covering usual cases
    oxidation_states = nonmetal.oxidation_states
    for ost in oxidation_states:
        if ost > 0:
            i = Ion.from_string(nonmetal.symbol, ost)
            positive_nonmetals.append(i)
        elif ost < 0:
            i = Ion.from_string(nonmetal.symbol, ost)
            negative_nonmetals.append(i)
        else:
            # should be present for noble gases that can have only oxidation state of 0
            continue
        # print(ost, m.formula())


# ================================================================================= INITIATING SOLUBILITY TABLE DATABASE
"""
SolubilityTable's method _erase_all() required confirmation from console and returns boolean indicating whether the
database was erased or not.
"""

# initiating solubility table instance to write the data to the database
print('Initiating the database...')
st = SolubilityTable()
st.begin()
if not st._erase_all():  # the function requires console approval
    print('Program interrupted.')
    exit()

# ============================================================================ WRITING IN IONS BASED ON OXIDATION STATES
"""
To write in all the created ions, we need to find such ions of an opposite charge that will have the same pattern of
solubility with all the given ions. For example, for metals we can use nitrate ions, because ALL nitrates are soluble,
hence we don't need to write the metal ions one by one, but can use a loop with solubility="SL".

The patters used are:
for metals: all nitrates ares soluble
for nonemtal cations: all oxides are said to have no data, because they are usually not present in the solubility table
for nonmetal anions: there is a pattern of solubility for substances containing hydrogen cation, H(+), namely
                     1) many common nonmetals (in a form of anions) form soluble substances with hydrogen
                     2) some specific nonmetals form substances that react with water
                     3) the rest is given ND (no data) solubility
"""

# all nitrates are soluble, so we use nitrate anion for metal cations
print('Writing in metal cations...')
for metal_ion in metals:
    # print(metal_ion.formula(), metal_ion.charge, 'NO3', -1)
    st.write(metal_ion.formula(remove_charge=True), metal_ion.charge, 'NO3', -1, 'SL')
st.write('H', 1, 'NO3', -1, 'SL')

# all oxides are not soluble because of REACTION WITH WATER. But since usually they are not present in the solubility table
# we just set solubility = 'ND', which stands for "no data". I.e. these substances are here just for presence of ions
print('Writing in nonmetal cations...')
for nonmetal_ion in positive_nonmetals:
    # print(nonmetal_ion.formula(), nonmetal_ion.charge, 'O', -2, 'ND')
    st.write(nonmetal_ion.formula(remove_charge=True), nonmetal_ion.charge, 'O', -2, 'ND')

# all hydrogen-containing substances are either soluble (acids), react with water (very specific substances), or
# are not discovered. All three cases are covered in the code below
print('Writing in nonmetal anions...')
for nonmetal_ion in negative_nonmetals:
    if not nonmetal_ion == Ion.from_string('O', -2):  # already there
        if nonmetal_ion.elements[0] in {pt.trivials.HALOGENS, pt.S, pt.P, pt.C, pt.N}:
            # print('H', 1, nonmetal_ion.formula(), nonmetal_ion.charge, 'SL')
            st.write('H', 1, nonmetal_ion.formula(remove_charge=True), nonmetal_ion.charge, 'SL')
        elif nonmetal_ion.elements[0] in {pt.trivials.HALOGENS, pt.Si, pt.Ge}:
            # print('H', 1, nonmetal_ion.formula(), nonmetal_ion.charge, 'RW')
            st.write('H', 1, nonmetal_ion.formula(remove_charge=True), nonmetal_ion.charge, 'RW')
        else:
            # print('H', 1, nonmetal_ion.formula(), nonmetal_ion.charge, 'ND')
            st.write('H', 1, nonmetal_ion.formula(remove_charge=True), nonmetal_ion.charge, 'ND')


# ======================================================================================== WRITING IN RARELY USED ANIONS
"""
There are also some complex (containing more than one element) anions that are rarely used in school chemistry, but 
still might be useful.

In this case we use the fact that majority of acids are soluble in water, hence all the anions mentioned here (except
for SiO3(-2)) are soluble. So, we just write in their compounds with H(1) with solubility="SL", making an exception 
for SiO3(-2) anion, which makes an insoluble substance.
"""

# A list (dict) of all the anions that contain more than one atom, but still can be included in the solubility table
# (although not present in the actual table, because are quite rare)
print('Writing in anions consisting of more than one element...')
two_atom_anions = {
    'ClO': -1,
    'ClO2': -1,
    'ClO3': -1,
    'ClO4': -1,
    'BrO': -1,
    'BrO2': -1,
    'BrO3': -1,
    'BrO4': -1,
    'IO': -1,
    'IO2': -1,
    'IO3': -1,
    'IO4': -1,
    'SiO3': -2,
    'HSO3': -1,
    'HPO4': -2,
    'H2PO4': -1,
    'C2O4': -2,
    'AsO4': -3,
    'HAsO4': -2,
    'H2AsO4': -1,
    'SeO4': -2,
    'HSeO4': -1,
    'HPO3': -2,
    'P2O7': -4,
    'S2O7': -2,
}

for formula, charge in two_atom_anions.items():
    # print('Na', 1, formula, charge, 'SL')
    if formula == 'SiO3':
        st.write('H', 1, formula, charge, 'NS')
    else:
        st.write('H', 1, formula, charge, 'SL')
    # st.write('Na', 1, formula, charge, 'SL')


# ========================================================================= READING THE EXCEL FILE WITH SOLUBILITY TABLE
"""
The most common substances used in school chemistry are met in the solubility table given in the file SolubilityTable.xlsx.
Many of then do not follow any simple enough pattern to be coded, so this part just reads the excel file and writes the
substances into the solubility table database.
"""

# The actual solubility table data are read from the Excel file and written into the database
# here we need pandas (and only here)
print('Reading the solubility table excel file...')
file_name = 'SolubilityTable.xlsx'
df = pd.read_excel(file_name, sheet_name='Solubility In Water')

print('And writing the actual solubilities of the most frequently met substances...')
for index, row in df.iterrows():
    anion = row.iloc[0]  # interpreter said to use it instead of __getitem__(), i.e. instead of row[0]

    # slicing is used to avoid using anions twice. Remove it and see the result
    for cation, solubility in row[1:].items():
        # print(*row.items())  # to understand the above written code
        cation_formula, cation_charge = parse_ion(cation)
        anion_formula, anion_charge = parse_ion(anion)

        if not anion_formula == 'NO3':  # skipping nitrates, because they are already written into the table
            # print(cation_formula, cation_charge, anion_formula, anion_charge, solubility)
            if cation_formula == 'H' and len(parse_formula(anion_formula)) == 1:  # skipping halogens as well...
                continue
            st.write(cation_formula, cation_charge, anion_formula, anion_charge, solubility)

st.end()
print('Done!')
