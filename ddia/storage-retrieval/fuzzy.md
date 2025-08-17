I'll give you a comprehensive introduction to fuzzy search and text-based indexes with examples and practice problems.

## What is Fuzzy Search?

**Regular search** requires exact matches:

```
Database: ["apple", "banana", "orange"]
Search: "aple" → No results ❌
```

**Fuzzy search** finds similar matches:

```
Database: ["apple", "banana", "orange"]
Search: "aple" → "apple" ✅ (1 character difference)
```

## Core Text-Based Index Types

### 1. Trie (Prefix Tree)

**Structure for fast prefix matching:**

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.word = None

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.word = word

    def search_prefix(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        # Collect all words with this prefix
        results = []
        self._dfs_collect(node, results)
        return results

    def _dfs_collect(self, node, results):
        if node.is_word:
            results.append(node.word)
        for child in node.children.values():
            self._dfs_collect(child, results)

# Example usage
trie = Trie()
words = ["apple", "app", "application", "apply", "banana"]
for word in words:
    trie.insert(word)

print(trie.search_prefix("app"))
# Output: ["app", "apple", "application", "apply"]
```

**Visual representation:**

```
        root
         |
         a
         |
         p
         |
         p (word: "app")
        / \
       l   l
       |   |
       e   y (word: "apply")
       |   |
 (word: i
 "apple") c
          |
          a
          |
          t
          |
          i
          |
          o
          |
          n (word: "application")
```

### 2. Inverted Index

**Maps terms to documents containing them:**

```python
class InvertedIndex:
    def __init__(self):
        self.index = {}  # term -> set of document IDs
        self.documents = {}  # doc_id -> document text

    def add_document(self, doc_id, text):
        self.documents[doc_id] = text
        words = text.lower().split()

        for word in words:
            if word not in self.index:
                self.index[word] = set()
            self.index[word].add(doc_id)

    def search(self, query):
        query_words = query.lower().split()
        if not query_words:
            return set()

        # Find documents containing ALL query words (AND operation)
        result = self.index.get(query_words[0], set())
        for word in query_words[1:]:
            result = result.intersection(self.index.get(word, set()))

        return result

# Example
index = InvertedIndex()
index.add_document(1, "The quick brown fox jumps")
index.add_document(2, "Brown bears are quick")
index.add_document(3, "The fox is clever")

print(index.search("quick brown"))  # Output: {2}
print(index.search("fox"))          # Output: {1, 3}

# Index structure:
# {
#   "the": {1, 3},
#   "quick": {1, 2},
#   "brown": {1, 2},
#   "fox": {1, 3},
#   "jumps": {1},
#   "bears": {2},
#   "are": {2},
#   "is": {3},
#   "clever": {3}
# }
```

## Fuzzy Search Techniques

### 1. Edit Distance (Levenshtein Distance)

**Measures similarity between two strings:**

```python
def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]  # No operation needed
            else:
                dp[i][j] = 1 + min(
                    dp[i-1][j],      # Deletion
                    dp[i][j-1],      # Insertion
                    dp[i-1][j-1]     # Substitution
                )

    return dp[m][n]

# Examples
print(edit_distance("kitten", "sitting"))  # 3
print(edit_distance("apple", "aple"))      # 1
print(edit_distance("hello", "helo"))      # 1

def fuzzy_search(query, words, max_distance=2):
    results = []
    for word in words:
        if edit_distance(query, word) <= max_distance:
            results.append(word)
    return results

words = ["apple", "banana", "orange", "grape", "pineapple"]
print(fuzzy_search("aple", words))     # ["apple"]
print(fuzzy_search("ornge", words))    # ["orange"]
```

### 2. N-Grams for Fuzzy Matching

**Break words into overlapping substrings:**

```python
def generate_ngrams(text, n=2):
    text = f"#{text}#"  # Add padding
    return [text[i:i+n] for i in range(len(text) - n + 1)]

def ngram_similarity(s1, s2, n=2):
    ngrams1 = set(generate_ngrams(s1, n))
    ngrams2 = set(generate_ngrams(s2, n))

    intersection = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))

    return intersection / union if union > 0 else 0

# Examples
print(generate_ngrams("hello", 2))  # ['#h', 'he', 'el', 'll', 'lo', 'o#']
print(generate_ngrams("hello", 3))  # ['#he', 'hel', 'ell', 'llo', 'lo#']

print(ngram_similarity("hello", "helo"))    # High similarity
print(ngram_similarity("hello", "world"))   # Low similarity

class NGramIndex:
    def __init__(self, n=2):
        self.n = n
        self.ngram_to_words = {}
        self.words = set()

    def add_word(self, word):
        self.words.add(word)
        ngrams = generate_ngrams(word, self.n)
        for ngram in ngrams:
            if ngram not in self.ngram_to_words:
                self.ngram_to_words[ngram] = set()
            self.ngram_to_words[ngram].add(word)

    def fuzzy_search(self, query, threshold=0.3):
        query_ngrams = set(generate_ngrams(query, self.n))
        candidates = set()

        # Collect candidate words
        for ngram in query_ngrams:
            if ngram in self.ngram_to_words:
                candidates.update(self.ngram_to_words[ngram])

        # Score candidates
        results = []
        for word in candidates:
            similarity = ngram_similarity(query, word, self.n)
            if similarity >= threshold:
                results.append((word, similarity))

        return sorted(results, key=lambda x: x[1], reverse=True)

# Usage
index = NGramIndex(2)
for word in ["apple", "application", "banana", "orange", "grape"]:
    index.add_word(word)

print(index.fuzzy_search("aple"))  # [("apple", similarity_score)]
```

### 3. Finite State Automaton (FSA) for Fuzzy Search

**Used by Lucene for efficient fuzzy matching:**

```python
class FuzzyAutomaton:
    def __init__(self, pattern, max_edits=1):
        self.pattern = pattern
        self.max_edits = max_edits
        self.pattern_len = len(pattern)

    def matches(self, text):
        # Simplified FSA - tracks edit distance at each position
        prev_row = list(range(self.pattern_len + 1))

        for i, char in enumerate(text):
            curr_row = [i + 1]

            for j in range(self.pattern_len):
                if char == self.pattern[j]:
                    curr_row.append(prev_row[j])
                else:
                    curr_row.append(1 + min(
                        prev_row[j],      # Substitution
                        prev_row[j + 1],  # Deletion
                        curr_row[j]       # Insertion
                    ))

            prev_row = curr_row

            # Early termination if minimum edit distance > max_edits
            if min(curr_row) > self.max_edits:
                return False

        return prev_row[self.pattern_len] <= self.max_edits

# Example
automaton = FuzzyAutomaton("apple", max_edits=1)
print(automaton.matches("aple"))   # True
print(automaton.matches("banana")) # False
```

## Advanced Features

### 1. Phonetic Matching (Soundex)

**Match words that sound similar:**

```python
def soundex(word):
    word = word.upper()
    soundex_code = word[0]  # Keep first letter

    # Mapping for consonants
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }

    for char in word[1:]:
        if char in mapping:
            code = mapping[char]
            if soundex_code[-1] != code:  # Avoid consecutive duplicates
                soundex_code += code

    # Pad with zeros or truncate to 4 characters
    soundex_code = (soundex_code + '000')[:4]
    return soundex_code

# Examples
print(soundex("Smith"))    # S530
print(soundex("Smyth"))    # S530 (same sound!)
print(soundex("Johnson"))  # J525
print(soundex("Jonson"))   # J525 (same sound!)
```

### 2. Full-Text Search with Ranking

```python
import math
from collections import defaultdict

class TFIDFSearchEngine:
    def __init__(self):
        self.documents = {}
        self.term_freq = defaultdict(lambda: defaultdict(int))
        self.doc_freq = defaultdict(int)
        self.doc_count = 0

    def add_document(self, doc_id, text):
        self.documents[doc_id] = text
        words = text.lower().split()
        self.doc_count += 1

        # Calculate term frequency
        for word in words:
            self.term_freq[doc_id][word] += 1

        # Calculate document frequency
        unique_words = set(words)
        for word in unique_words:
            self.doc_freq[word] += 1

    def search(self, query):
        query_words = query.lower().split()
        scores = defaultdict(float)

        for word in query_words:
            if word in self.doc_freq:
                idf = math.log(self.doc_count / self.doc_freq[word])

                for doc_id, tf in self.term_freq.items():
                    if word in tf:
                        tfidf = tf[word] * idf
                        scores[doc_id] += tfidf

        # Sort by relevance score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Example
engine = TFIDFSearchEngine()
engine.add_document(1, "The quick brown fox jumps over lazy dog")
engine.add_document(2, "Brown bears are quick and strong")
engine.add_document(3, "The lazy cat sleeps all day")

results = engine.search("quick brown")
for doc_id, score in results:
    print(f"Doc {doc_id}: {score:.2f} - {engine.documents[doc_id]}")
```

## LeetCode-Style Practice Problems

### Beginner Level

1. **Implement Trie (Prefix Tree)** - LeetCode #208
2. **Word Search II** - LeetCode #212
3. **Edit Distance** - LeetCode #72
4. **Longest Common Subsequence** - LeetCode #1143

### Intermediate Level

5. **Design Search Autocomplete System** - LeetCode #642
6. **Word Break** - LeetCode #139
7. **Palindrome Pairs** - LeetCode #336
8. **Search Suggestions System** - LeetCode #1268

### Advanced Level

9. **Stream of Characters** - LeetCode #1032
10. **Word Squares** - LeetCode #425

### Custom Practice Problems

```python
# Problem 1: Fuzzy String Matching
def fuzzy_match_words(dictionary, query, max_distance):
    """
    Find all words in dictionary within max_distance edits of query

    Input: dictionary = ["cat", "bat", "rat", "car"], query = "ca", max_distance = 1
    Output: ["cat", "car"]
    """
    pass

# Problem 2: Auto-complete with Typos
def autocomplete_fuzzy(trie_words, prefix, max_typos):
    """
    Return autocomplete suggestions allowing for typos in prefix

    Input: words = ["apple", "application", "apply"], prefix = "apl", max_typos = 1
    Output: ["apple", "apply"]
    """
    pass

# Problem 3: Phonetic Search
def phonetic_search(words, query):
    """
    Find words that sound similar using Soundex algorithm

    Input: words = ["Smith", "Smyth", "Jones"], query = "Smith"
    Output: ["Smith", "Smyth"]
    """
    pass

# Problem 4: N-gram Based Search
def ngram_search(documents, query, n=2, threshold=0.5):
    """
    Search documents using n-gram similarity

    Input: docs = ["hello world", "help world"], query = "helo world", n=2
    Output: [("hello world", similarity_score)]
    """
    pass

# Problem 5: Multi-field Fuzzy Search
def multi_field_search(records, query_fields, fuzzy=True):
    """
    Search across multiple fields with optional fuzzy matching

    records = [
        {"name": "John Smith", "email": "john@example.com"},
        {"name": "Jane Doe", "email": "jane@test.com"}
    ]
    query = {"name": "Jon", "email": "example"}
    """
    pass
```

These problems will help you understand:

- **Trie operations** and prefix matching
- **Dynamic programming** for edit distance
- **String algorithms** for pattern matching
- **Index design** for efficient search
- **Ranking algorithms** for relevance scoring
- **Fuzzy matching** techniques

Start with the basic trie and edit distance problems, then progress to more complex search scenarios!
