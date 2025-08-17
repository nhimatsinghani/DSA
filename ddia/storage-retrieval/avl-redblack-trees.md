I'll explain AVL and red-black trees with examples and code to show how they maintain sorted data and balance.

## Binary Search Tree Basics

Both AVL and red-black trees are **self-balancing binary search trees**. Let's start with the foundation:

**Binary Search Tree Property:**

- Left child < Parent < Right child
- This enables **sorted retrieval** via in-order traversal

```python
class TreeNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None

# Example tree with values: 2, 5, 8, 12, 15
#       8
#      / \
#     5   12
#    /     \
#   2      15

def inorder_traversal(node):
    if node:
        inorder_traversal(node.left)   # Visit left
        print(node.val)                # Visit root
        inorder_traversal(node.right)  # Visit right

# Output: 2, 5, 8, 12, 15 (sorted!)
```

## Why Balancing Matters

**Unbalanced tree (worst case):**

```
1
 \
  2
   \
    3
     \
      4  # Essentially a linked list - O(n) operations
```

**Balanced tree:**

```
    2
   / \
  1   3
       \
        4  # Height = log(n) - O(log n) operations
```

## AVL Trees

**AVL Rule:** Height difference between left and right subtrees ≤ 1

```python
class AVLNode:
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None
        self.height = 1

def get_height(node):
    return node.height if node else 0

def get_balance(node):
    return get_height(node.left) - get_height(node.right) if node else 0

def update_height(node):
    if node:
        node.height = 1 + max(get_height(node.left), get_height(node.right))
```

**AVL Rotations (4 cases):**

```python
# Right rotation (LL case)
def rotate_right(y):
    x = y.left
    T2 = x.right

    # Perform rotation
    x.right = y
    y.left = T2

    # Update heights
    update_height(y)
    update_height(x)
    return x

# Left rotation (RR case)
def rotate_left(x):
    y = x.right
    T2 = y.left

    # Perform rotation
    y.left = x
    x.right = T2

    # Update heights
    update_height(x)
    update_height(y)
    return y

def avl_insert(root, val):
    # 1. Normal BST insertion
    if not root:
        return AVLNode(val)

    if val < root.val:
        root.left = avl_insert(root.left, val)
    else:
        root.right = avl_insert(root.right, val)

    # 2. Update height
    update_height(root)

    # 3. Get balance factor
    balance = get_balance(root)

    # 4. Rebalance if needed
    # Left Left case
    if balance > 1 and val < root.left.val:
        return rotate_right(root)

    # Right Right case
    if balance < -1 and val > root.right.val:
        return rotate_left(root)

    # Left Right case
    if balance > 1 and val > root.left.val:
        root.left = rotate_left(root.left)
        return rotate_right(root)

    # Right Left case
    if balance < -1 and val < root.right.val:
        root.right = rotate_right(root.right)
        return rotate_left(root)

    return root
```

**AVL Example:**

```
Insert sequence: 10, 20, 30

Step 1: Insert 10
   10

Step 2: Insert 20
   10
    \
    20

Step 3: Insert 30 (triggers rebalancing)
   10          After left rotation:    20
    \                                 /  \
    20     →    Balance = -2         10  30
     \          (violates AVL)
     30
```

## Red-Black Trees

**Red-Black Rules:**

1. Every node is red or black
2. Root is black
3. No two red nodes are adjacent
4. Every path from root to leaf has same number of black nodes

```python
class RBNode:
    def __init__(self, val, color='RED'):
        self.val = val
        self.color = color  # 'RED' or 'BLACK'
        self.left = None
        self.right = None
        self.parent = None

def rb_insert(root, val):
    # 1. Standard BST insertion (new nodes are RED)
    new_node = RBNode(val, 'RED')

    if not root:
        new_node.color = 'BLACK'  # Root is always black
        return new_node

    # Find insertion point
    current = root
    while True:
        if val < current.val:
            if not current.left:
                current.left = new_node
                new_node.parent = current
                break
            current = current.left
        else:
            if not current.right:
                current.right = new_node
                new_node.parent = current
                break
            current = current.right

    # 2. Fix red-black violations
    return fix_rb_violations(root, new_node)

def fix_rb_violations(root, node):
    while node != root and node.parent.color == 'RED':
        parent = node.parent
        grandparent = parent.parent

        if parent == grandparent.left:  # Parent is left child
            uncle = grandparent.right

            if uncle and uncle.color == 'RED':  # Case 1: Uncle is red
                parent.color = 'BLACK'
                uncle.color = 'BLACK'
                grandparent.color = 'RED'
                node = grandparent
            else:  # Uncle is black or None
                if node == parent.right:  # Case 2: Node is right child
                    node = parent
                    root = rotate_left(root, node)
                    parent = node.parent

                # Case 3: Node is left child
                parent.color = 'BLACK'
                grandparent.color = 'RED'
                root = rotate_right(root, grandparent)
        else:  # Mirror cases for right side
            # Similar logic but mirrored
            pass

    root.color = 'BLACK'  # Root is always black
    return root
```

**Red-Black Example:**

```
Insert sequence: 10, 5, 15, 3, 7

Final tree:
      10(B)
     /     \
   5(R)    15(B)
  /   \
3(B)  7(B)

- Root is black ✓
- No adjacent red nodes ✓
- All paths have same black height (2) ✓
```

## Sorted Retrieval

Both trees maintain the BST property, so **in-order traversal gives sorted data**:

```python
def print_sorted(root):
    if root:
        print_sorted(root.left)
        print(root.val)
        print_sorted(root.right)

# For any balanced BST with values: 3, 5, 7, 10, 15
# Output: 3, 5, 7, 10, 15 (always sorted!)
```

## Key Differences

| Feature        | AVL Trees                           | Red-Black Trees                    |
| -------------- | ----------------------------------- | ---------------------------------- |
| **Balance**    | Strictly balanced (height diff ≤ 1) | Loosely balanced (red-black rules) |
| **Insertions** | More rotations needed               | Fewer rotations needed             |
| **Lookups**    | Slightly faster                     | Slightly slower                    |
| **Use Case**   | Read-heavy workloads                | Write-heavy workloads              |

**Real-world usage:**

- **AVL**: Better for databases with frequent lookups
- **Red-Black**: Used in C++ `std::map`, Java `TreeMap`, Linux kernel

Both guarantee **O(log n)** operations while maintaining sorted order through in-order traversal!
