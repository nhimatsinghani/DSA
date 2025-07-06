# Graph Modeling with Neo4j Cypher and GraphQL

## Use Case: Social Network Platform

We'll model a simplified social network where users can:
- Follow other users
- Create posts
- Like posts
- Comment on posts
- Join groups
- Have skills/interests

## Graph Model Design

### Node Types:
1. **User** - Represents platform users
2. **Post** - Content created by users
3. **Comment** - User responses to posts
4. **Group** - Communities users can join
5. **Skill** - User skills/interests

### Relationship Types:
1. **FOLLOWS** - User follows another user
2. **POSTED** - User created a post
3. **LIKES** - User likes a post
4. **COMMENTED** - User commented on a post
5. **MEMBER_OF** - User is member of a group
6. **HAS_SKILL** - User has a skill
7. **REPLIED_TO** - Comment replies to another comment

## Sample Data Creation (Cypher)

```cypher
// Create Users
CREATE 
  (alice:User {id: 1, name: "Alice Johnson", email: "alice@example.com", joinDate: "2023-01-15"}),
  (bob:User {id: 2, name: "Bob Smith", email: "bob@example.com", joinDate: "2023-02-20"}),
  (charlie:User {id: 3, name: "Charlie Brown", email: "charlie@example.com", joinDate: "2023-03-10"}),
  (diana:User {id: 4, name: "Diana Prince", email: "diana@example.com", joinDate: "2023-04-05"});

// Create Skills
CREATE 
  (python:Skill {name: "Python", category: "Programming"}),
  (javascript:Skill {name: "JavaScript", category: "Programming"}),
  (graphql:Skill {name: "GraphQL", category: "API"}),
  (neo4j:Skill {name: "Neo4j", category: "Database"});

// Create Groups
CREATE 
  (devs:Group {id: 1, name: "Developers", description: "Software developers community"}),
  (graphdb:Group {id: 2, name: "Graph Database Enthusiasts", description: "Neo4j and graph database lovers"});

// Create Posts
CREATE 
  (post1:Post {id: 1, title: "Getting Started with Neo4j", content: "Neo4j is amazing for connected data...", createdAt: "2023-05-01T10:00:00Z"}),
  (post2:Post {id: 2, title: "GraphQL vs REST", content: "Let's discuss the pros and cons...", createdAt: "2023-05-02T14:30:00Z"}),
  (post3:Post {id: 3, title: "Python Tips", content: "Here are some useful Python tricks...", createdAt: "2023-05-03T09:15:00Z"});

// Create Comments
CREATE 
  (comment1:Comment {id: 1, content: "Great introduction to Neo4j!", createdAt: "2023-05-01T11:00:00Z"}),
  (comment2:Comment {id: 2, content: "Thanks for sharing!", createdAt: "2023-05-01T12:00:00Z"}),
  (comment3:Comment {id: 3, content: "I prefer GraphQL for most APIs", createdAt: "2023-05-02T15:00:00Z"});

// Create Relationships
MATCH (alice:User {name: "Alice Johnson"}), (bob:User {name: "Bob Smith"})
CREATE (alice)-[:FOLLOWS]->(bob);

MATCH (alice:User {name: "Alice Johnson"}), (charlie:User {name: "Charlie Brown"})
CREATE (alice)-[:FOLLOWS]->(charlie);

MATCH (bob:User {name: "Bob Smith"}), (diana:User {name: "Diana Prince"})
CREATE (bob)-[:FOLLOWS]->(diana);

MATCH (alice:User {name: "Alice Johnson"}), (post1:Post {id: 1})
CREATE (alice)-[:POSTED]->(post1);

MATCH (bob:User {name: "Bob Smith"}), (post2:Post {id: 2})
CREATE (bob)-[:POSTED]->(post2);

MATCH (charlie:User {name: "Charlie Brown"}), (post3:Post {id: 3})
CREATE (charlie)-[:POSTED]->(post3);

MATCH (bob:User {name: "Bob Smith"}), (post1:Post {id: 1})
CREATE (bob)-[:LIKES]->(post1);

MATCH (charlie:User {name: "Charlie Brown"}), (post1:Post {id: 1})
CREATE (charlie)-[:LIKES]->(post1);

MATCH (alice:User {name: "Alice Johnson"}), (comment1:Comment {id: 1})
CREATE (alice)-[:COMMENTED]->(comment1);

MATCH (comment1:Comment {id: 1}), (post1:Post {id: 1})
CREATE (comment1)-[:REPLIED_TO]->(post1);

MATCH (alice:User {name: "Alice Johnson"}), (python:Skill {name: "Python"})
CREATE (alice)-[:HAS_SKILL]->(python);

MATCH (alice:User {name: "Alice Johnson"}), (neo4j:Skill {name: "Neo4j"})
CREATE (alice)-[:HAS_SKILL]->(neo4j);

MATCH (bob:User {name: "Bob Smith"}), (javascript:Skill {name: "JavaScript"})
CREATE (bob)-[:HAS_SKILL]->(javascript);

MATCH (alice:User {name: "Alice Johnson"}), (devs:Group {name: "Developers"})
CREATE (alice)-[:MEMBER_OF]->(devs);

MATCH (bob:User {name: "Bob Smith"}), (devs:Group {name: "Developers"})
CREATE (bob)-[:MEMBER_OF]->(devs);
```

## Common Cypher Queries

### 1. Find all users a specific user follows
```cypher
MATCH (user:User {name: "Alice Johnson"})-[:FOLLOWS]->(following:User)
RETURN following.name AS followingName, following.email AS email;
```

### 2. Get user's posts with like counts
```cypher
MATCH (user:User {name: "Alice Johnson"})-[:POSTED]->(post:Post)
OPTIONAL MATCH (post)<-[:LIKES]-(liker:User)
RETURN post.title, post.content, post.createdAt, COUNT(liker) AS likeCount;
```

### 3. Find users with common skills
```cypher
MATCH (user1:User {name: "Alice Johnson"})-[:HAS_SKILL]->(skill:Skill)<-[:HAS_SKILL]-(user2:User)
WHERE user1 <> user2
RETURN user2.name AS commonSkillUser, skill.name AS commonSkill;
```

### 4. Get user's network activity feed
```cypher
MATCH (user:User {name: "Alice Johnson"})-[:FOLLOWS]->(following:User)-[:POSTED]->(post:Post)
OPTIONAL MATCH (post)<-[:LIKES]-(liker:User)
OPTIONAL MATCH (post)<-[:REPLIED_TO]-(comment:Comment)
RETURN following.name AS author, post.title, post.createdAt, 
       COUNT(DISTINCT liker) AS likes, COUNT(DISTINCT comment) AS comments
ORDER BY post.createdAt DESC;
```

### 5. Find suggested users to follow (friends of friends)
```cypher
MATCH (user:User {name: "Alice Johnson"})-[:FOLLOWS]->(friend:User)-[:FOLLOWS]->(suggestion:User)
WHERE user <> suggestion AND NOT (user)-[:FOLLOWS]->(suggestion)
RETURN suggestion.name AS suggestedUser, COUNT(friend) AS mutualFriends
ORDER BY mutualFriends DESC;
```

### 6. Get group members and their skills
```cypher
MATCH (group:Group {name: "Developers"})<-[:MEMBER_OF]-(member:User)
OPTIONAL MATCH (member)-[:HAS_SKILL]->(skill:Skill)
RETURN member.name AS memberName, COLLECT(skill.name) AS skills;
```

## Neo4j Indexes for Performance

```cypher
// Create indexes for frequently queried properties
CREATE INDEX user_name_index FOR (u:User) ON (u.name);
CREATE INDEX user_email_index FOR (u:User) ON (u.email);
CREATE INDEX post_created_index FOR (p:Post) ON (p.createdAt);
CREATE INDEX skill_name_index FOR (s:Skill) ON (s.name);
```

## Key Cypher Concepts

1. **MATCH** - Find patterns in the graph
2. **CREATE** - Create nodes and relationships
3. **RETURN** - Specify what to return
4. **WHERE** - Filter results
5. **OPTIONAL MATCH** - Match patterns that may not exist
6. **WITH** - Pass results to next part of query
7. **COLLECT** - Aggregate results into lists
8. **ORDER BY** - Sort results
9. **LIMIT** - Limit number of results

## Graph Modeling Best Practices

1. **Nodes** - Represent entities (nouns)
2. **Relationships** - Represent actions or associations (verbs)
3. **Properties** - Store attributes of nodes and relationships
4. **Use meaningful relationship types** - Makes queries more readable
5. **Avoid deep hierarchies** - Keep relationships at reasonable depth
6. **Index frequently queried properties** - Improves performance
7. **Use parameters** - Prevents injection attacks and improves performance
