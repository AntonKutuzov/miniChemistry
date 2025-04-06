from miniChemistry.Core.Database.stable import SolubilityTable
from miniChemistry.Core.Database.ModifySolubilityTable import modify

st = SolubilityTable()
st.begin()
length = len(st.select_substance())
st.end()

if length == 0:
    modify(confirmation=False)
else:
    pass
