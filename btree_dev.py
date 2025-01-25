from python.btree import BTree

tree = BTree(4, 3)
to_insert = {
    5: 'Jeff Garcia',
    81: 'Terell Owens',
    85: 'George Kittle',
    16: 'Joe Montana',
    80: 'Jerry Rice',
    97: 'Nick Bosa',
    23: 'CMC',
    13: 'Brock (BCB) Purdy',
    21: 'Frank Gore',
    42: 'Ronnie Lott',
    87: 'Dwight Clark',
    14: 'Ricky Persall',
    8: 'Steve Young',
    52: 'Patrick Willis',
    54: 'Fred Warner',
    31: 'Roger Craig'
}

for key, val in to_insert.items():
    # print(key, val)
    tree.insert(key=key, value=val)

print(tree)