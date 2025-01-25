import bisect
from typing import Any, List, Optional, Tuple, Union, Dict, Generic, TypeVar, cast, NewType
from .disk import DISK, Address
from .btree_node import BTreeNode, KT, VT, get_node

"""
----------------------- Starter code for your B-Tree -----------------------

Helpful Tips (You will need these):
1. Your tree should be composed of BTreeNode objects, where each node has:
    - the disk block address of its parent node
    - the disk block addresses of its children nodes (if non-leaf)
    - the data items inside (if leaf)
    - a flag indicating whether it is a leaf

------------- THE ONLY DATA STORED IN THE `BTree` OBJECT SHOULD BE THE `M` & `L` VALUES AND THE ADDRESS OF THE ROOT NODE -------------
-------------              THIS IS BECAUSE THE POINT IS TO STORE THE ENTIRE TREE ON DISK AT ALL TIMES                    -------------

2. Create helper methods:
    - get a node's parent with DISK.read(parent_address)
    - get a node's children with DISK.read(child_address)
    - write a node back to disk with DISK.write(self)
    - check the health of your tree (makes debugging a piece of cake)
        - go through the entire tree recursively and check that children point to their parents, etc.
        - now call this method after every insertion in your testing and you will find out where things are going wrong
3. Don't fall for these common bugs:
    - Forgetting to update a node's parent address when its parent splits
        - Remember that when a node splits, some of its children no longer have the same parent
    - Forgetting that the leaf and the root are edge cases
    - FORGETTING TO WRITE BACK TO THE DISK AFTER MODIFYING / CREATING A NODE
    - Forgetting to test odd / even M values
    - Forgetting to update the KEYS of a node who just gained a child
    - Forgetting to redistribute keys or children of a node who just split
    - Nesting nodes inside of each other instead of using disk addresses to reference them
        - This may seem to work but will fail our grader's stress tests
4. USE THE DEBUGGER
5. USE ASSERT STATEMENTS AS MUCH AS POSSIBLE
    - e.g. `assert node.parent != None or node == self.root` <- if this fails, something is very wrong

--------------------------- BEST OF LUCK ---------------------------
"""

# Complete both the find and insert methods to earn full credit
class BTree:
    def __init__(self, M: int, L: int):
        """
        Initialize a new BTree.
        You do not need to edit this method, nor should you.
        """
        self.root_addr: Address = DISK.new() # Remember, this is the ADDRESS of the root node
        # DO NOT RENAME THE ROOT MEMBER -- LEAVE IT AS self.root_addr
        DISK.write(self.root_addr, BTreeNode(self.root_addr, None, None, True))
        self.M = M # M will fall in the range 2 to 99999
        self.L = L # L will fall in the range 1 to 99999

    def insert(self, key: KT, value: VT) -> None:
        """
        Insert the key-value pair into your tree.
        It will probably be useful to have an internal
        _find_node() method that searches for the node
        that should be our parent (or finds the leaf
        if the key is already present).

        Overwrite old values if the key exists in the BTree.

        Make sure to write back all changes to the disk!
        """
        '''
        My basic logic here is:
        if root is none, write new key, val to the root
        else find the node in the tree where the key, val should be inserted and insert key, val into node
        then check to see if the node's too big, if it is, split it. otherwise, just write the new node to DISK
        '''
        root = DISK.read(self.root_addr)
        if root.keys == []:
            root.insert_data(key, value)
            DISK.write(self.root_addr,root)
            return
        else:
            node_to_insert = self.find(key=key,traverse=True)
            node_to_insert.insert_data(key,value)
            if len(node_to_insert.keys) > self.L:
                is_root = False if node_to_insert.my_addr != self.root_addr else True
                self.split_node(node_to_insert,is_root=is_root)
            else:
                DISK.write(node_to_insert.my_addr, node_to_insert)
        return

    def split_node(self, node: BTreeNode, is_root=False):
        '''
        My basic logic here is:
        treat root/non root's different, I am relying on passing that info as an argument
        non-root:
            -split the node into two nodes with keys <= median and one with nodes > the median
             also return the median as int (may need to change this to allow any type)
            -insert key into node's parent, and update less/greater nodes info in insert_key function
            -write new nodes to DISK
            if node's new parent has less than M keys, return
            elif node's parent is the root, split node passing is_root=True
            else: (node's new parent is too big and needs to be split again)
                split node's new parent
        root:
            -set aside root_addr
            -split root node just like above, but pass is_root arg to do function a little differently
            -assign less a new address (normal med_split just copies address of old node to less's address)
            -set less,great's new index_in_parent as 0 and 1
            -make new node to later be assigned as the root
            -insert new key (median), assign it's children_addresses, then write all changes to DISK
            -Lastly fix great's index in parents
        '''
        if not is_root:
            parent = DISK.read(node.parent_addr)
            less, median, great = self.med_split(node)
            new_less, new_parent, new_great = self.insert_key(parent, median, less, great)
            DISK.write(new_parent.my_addr, new_parent)
            DISK.write(new_less.my_addr, new_less)
            DISK.write(new_great.my_addr, new_great)
            if not node.is_leaf: # update new children's parent addrs
                for i in range(len(new_less.children_addrs)):
                    temp: BTreeNode = DISK.read(less.children_addrs[i])
                    temp.parent_addr = less.my_addr
                    DISK.write(temp.my_addr, temp)
                for i in range(len(new_great.children_addrs)):
                    temp: BTreeNode = DISK.read(great.children_addrs[i])
                    temp.parent_addr = great.my_addr
                    DISK.write(temp.my_addr, temp)
            if len(new_parent.keys) < self.M:
                return
            elif node.parent_addr == self.root_addr:
                self.split_node(new_parent,is_root=True)
            else:
                self.split_node(new_parent)
        else:
            root_addr = self.root_addr
            less, median, great = self.med_split(node,is_root=True)
            less.my_addr = DISK.new()
            less.index_in_parent, great.index_in_parent = 0, 1
            new_root = BTreeNode(
                my_addr=root_addr,
                parent_addr=None,
                index_in_parent=None,
                is_leaf=False
            )
            new_root.keys.insert(0,median)
            new_root.children_addrs = [less.my_addr, great.my_addr]
            DISK.write(root_addr,new_root)
            DISK.write(less.my_addr,less)
            DISK.write(great.my_addr,great)
            for i in range(len(less.children_addrs)):
                temp: BTreeNode = DISK.read(less.children_addrs[i])
                temp.parent_addr = less.my_addr
                DISK.write(temp.my_addr,temp)
            for i in range(len(great.children_addrs)):
                temp: BTreeNode = DISK.read(great.children_addrs[i])
                temp.parent_addr = great.my_addr
                DISK.write(temp.my_addr,temp)
            return
    '''
    inserts key into parent node (this case referred to as node)
    re-assign parent node's children addresses (less, great, then all nodes after great)
    '''
    def insert_key(self, node: BTreeNode, new_key, less: BTreeNode, great: BTreeNode):
        child_idx = less.index_in_parent
        key_idx = node.find_idx(new_key)
        node.keys.insert(key_idx,new_key)
        node.children_addrs[child_idx] = less.my_addr
        node.children_addrs.insert(child_idx+1,great.my_addr)
        for i in range(child_idx+2,len(node.children_addrs)):
            temp: BTreeNode = DISK.read(node.children_addrs[i])
            temp.index_in_parent = i
            DISK.write(temp.my_addr,temp)
        return less, node, great

    '''
    splits node into two nodes with keys <= median and > median
    '''
    def med_split(self, node: BTreeNode, is_root=False):
        leaf = node.is_leaf
        node_len = len(node.keys)
        if node_len % 2 != 0:
            med_index = int(node_len // 2)
        else:
            med_index = int(node_len / 2) - 1

        med = node.keys[med_index]

        less = BTreeNode(
            my_addr=node.my_addr,
            parent_addr=node.parent_addr if not is_root else self.root_addr,
            index_in_parent=node.index_in_parent if not is_root else 0,
            is_leaf=leaf
        )
        less.keys = [i for i in node.keys[:med_index+1]] if leaf or node_len==2 else [i for i in node.keys[:med_index]]
        if node_len == 2 and not leaf:
            empty = BTreeNode(
                my_addr=DISK.new(),
                parent_addr=less.parent_addr,
                index_in_parent=0,
                is_leaf=leaf
            )
            less.keys = []
            less.children_addrs = [node.children_addrs[0]]
            temp = DISK.read(less.children_addrs[0])
            temp.index_in_parent = 0
            DISK.write(temp.my_addr,temp)
            DISK.write(empty.my_addr,empty)

        else:
            less.children_addrs = [i for i in node.children_addrs[:med_index+1]] if not leaf else []
        less.data = [i for i in node.data[:med_index+1]] if leaf else []

        great = BTreeNode(
            my_addr=DISK.new(),
            parent_addr=node.parent_addr if not is_root else self.root_addr,
            index_in_parent=node.index_in_parent+1 if not is_root else 1,
            is_leaf=leaf
        )
        great.keys = [i for i in node.keys[med_index+1:]]
        great.children_addrs = [i for i in node.children_addrs[med_index+1:]] if not leaf else []
        if not leaf:
            for i in range(len(great.children_addrs)):
                temp = DISK.read(great.children_addrs[i])
                temp.index_in_parent = i
                DISK.write(temp.my_addr, temp)
        great.data = [i for i in node.data[med_index+1:]] if leaf else []
        return less, med, great
    def find(self, key: KT,traverse=False,levels=False) -> Optional[VT]:
        """
        Find a key and return the value associated with it.
        If it is not in the BTree, return None.

        This should be implemented with a logarithmic search
        in the node.keys array, not a linear search. Look at the
        BTreeNode.find_idx() method for an example of using
        the builtin bisect library to search for a number in 
        a sorted array in logarithmic time.
        """

        '''
        Traverse down tree until the leaf where the key should be is reached
        '''
        level = 0
        current_node = DISK.read(self.root_addr)
        if current_node.keys == []:
            return None
        else:
            while current_node.is_leaf == False:
                level += 1
                index = current_node.find_idx(key)
                current_node = DISK.read(current_node.children_addrs[index])
            if not traverse and not levels:
                if key in current_node.keys:
                    return current_node.find_data(key)
                else:
                    return None
            elif levels:
                return level
            else:
                return current_node

    def delete(self, key: KT) -> None:
        raise NotImplementedError("Karma method delete()")
    '''
    pre-order traversal of b-tree
    '''
    def pre_order_traverse(self,node_addr):
        temp: BTreeNode = DISK.read(node_addr)
        print(temp)
        if temp.is_leaf:
            return
        else:
            for child in temp.children_addrs:
                self.pre_order_traverse(child)
    '''
    To work with printing
    '''
    def __str__(self):
        self.pre_order_traverse(self.root_addr)
        return " "


