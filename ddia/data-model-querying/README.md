# Neo4j Cypher + GraphQL Integration Example

This example demonstrates how to build a **social network platform** using Neo4j graph database with Cypher queries and expose it through a GraphQL API.

## 🎯 Learning Objectives

By working through this example, you'll learn:

- **Graph modeling** concepts and best practices
- **Cypher query language** for Neo4j databases
- **GraphQL API** development with Python
- **Integration patterns** between Neo4j and GraphQL
- **Real-world use cases** for graph databases

## 📊 Use Case: Social Network Platform

Our social network models:

- **Users** who can follow each other
- **Posts** created by users
- **Comments** on posts
- **Skills** that users possess
- **Groups** that users can join
- **Relationships** like follows, likes, comments, etc.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GraphQL API   │    │   Python App    │    │   Neo4j Graph   │
│   (Frontend)    │◄──►│  (Backend)      │◄──►│   Database      │
│                 │    │                 │    │                 │
│ - Queries       │    │ - GraphQL       │    │ - Cypher        │
│ - Mutations     │    │ - Resolvers     │    │ - Graph Model   │
│ - Subscriptions │    │ - Neo4j Driver  │    │ - Relationships │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Neo4j Database** (Choose one option):

   ```bash
   # Option 1: Docker (Recommended)
   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

   # Option 2: Neo4j Desktop
   # Download from https://neo4j.com/download/

   # Option 3: Neo4j AuraDB (Cloud)
   # Sign up at https://neo4j.com/cloud/aura/
   ```

2. **Python 3.8+** and pip

### Installation

1. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Neo4j connection**:
   Edit the connection details in `neo4j_graphql_example.py` and `setup_database.py`:

   ```python
   NEO4J_URI = "bolt://localhost:7687"
   NEO4J_USERNAME = "neo4j"
   NEO4J_PASSWORD = "password"  # Change this!
   ```

3. **Initialize the database**:

   ```bash
   python setup_database.py
   ```

4. **Start the GraphQL API**:

   ```bash
   python neo4j_graphql_example.py
   ```

5. **Access the GraphQL Playground**:
   Open http://localhost:5000/graphql in your browser

## 📝 Graph Model

### Node Types

- **User**: Platform users with profiles
- **Post**: Content created by users
- **Comment**: User responses to posts
- **Skill**: User skills and expertise
- **Group**: Communities users can join

### Relationship Types

- **FOLLOWS**: User follows another user
- **POSTED**: User created a post
- **LIKES**: User likes a post
- **COMMENTED**: User commented on a post
- **REPLIED_TO**: Comment replies to a post
- **HAS_SKILL**: User has a skill
- **MEMBER_OF**: User is member of a group

## 🔍 Example Queries

### GraphQL Queries

#### Get User with Statistics

```graphql
{
  userWithStats(name: "Alice Johnson") {
    name
    email
    followersCount
    followingCount
    postsCount
    skills {
      name
      category
    }
  }
}
```

#### Get User's Network Feed

```graphql
{
  userFeed(userName: "Alice Johnson", limit: 5) {
    title
    content
    createdAt
    author {
      name
    }
    likeCount
    commentCount
  }
}
```

#### Find Suggested Users to Follow

```graphql
{
  suggestedUsers(userName: "Alice Johnson") {
    name
    email
  }
}
```

### GraphQL Mutations

#### Create New User

```graphql
mutation {
  createUser(name: "John Doe", email: "john@example.com") {
    user {
      name
      email
    }
  }
}
```

#### Follow Another User

```graphql
mutation {
  followUser(followerName: "Alice Johnson", followingName: "John Doe") {
    success
  }
}
```

## 🎯 Cypher Query Examples

### 1. Find All Users Someone Follows

```cypher
MATCH (user:User {name: "Alice Johnson"})-[:FOLLOWS]->(following:User)
RETURN following.name AS followingName, following.email AS email;
```

### 2. Get User's Posts with Like Counts

```cypher
MATCH (user:User {name: "Alice Johnson"})-[:POSTED]->(post:Post)
OPTIONAL MATCH (post)<-[:LIKES]-(liker:User)
RETURN post.title, post.content, post.createdAt, COUNT(liker) AS likeCount;
```

### 3. Find Users with Common Skills

```cypher
MATCH (user1:User {name: "Alice Johnson"})-[:HAS_SKILL]->(skill:Skill)<-[:HAS_SKILL]-(user2:User)
WHERE user1 <> user2
RETURN user2.name AS commonSkillUser, skill.name AS commonSkill;
```

### 4. Get User's Network Activity Feed

```cypher
MATCH (user:User {name: "Alice Johnson"})-[:FOLLOWS]->(following:User)-[:POSTED]->(post:Post)
OPTIONAL MATCH (post)<-[:LIKES]-(liker:User)
OPTIONAL MATCH (post)<-[:REPLIED_TO]-(comment:Comment)
RETURN following.name AS author, post.title, post.createdAt,
       COUNT(DISTINCT liker) AS likes, COUNT(DISTINCT comment) AS comments
ORDER BY post.createdAt DESC;
```

### 5. Find Friend Suggestions (Friends of Friends)

```cypher
MATCH (user:User {name: "Alice Johnson"})-[:FOLLOWS]->(friend:User)-[:FOLLOWS]->(suggestion:User)
WHERE user <> suggestion AND NOT (user)-[:FOLLOWS]->(suggestion)
RETURN suggestion.name AS suggestedUser, COUNT(friend) AS mutualFriends
ORDER BY mutualFriends DESC;
```

## 🏆 Key Concepts Demonstrated

### Graph Modeling Best Practices

1. **Nodes as Entities** - Users, Posts, Comments are nouns
2. **Relationships as Actions** - FOLLOWS, LIKES, POSTED are verbs
3. **Properties for Attributes** - Store data on nodes and relationships
4. **Meaningful Relationship Types** - Clear, descriptive relationship names

### Cypher Language Features

- **MATCH** - Pattern matching in graphs
- **CREATE** - Creating nodes and relationships
- **OPTIONAL MATCH** - Handling optional patterns
- **WHERE** - Filtering conditions
- **RETURN** - Specifying output
- **COUNT, COLLECT** - Aggregation functions
- **ORDER BY, LIMIT** - Result ordering and limiting

### GraphQL Integration Patterns

- **Type Definitions** - Mapping graph entities to GraphQL types
- **Resolvers** - Converting GraphQL queries to Cypher
- **Nested Queries** - Leveraging graph relationships
- **Mutations** - Modifying graph data through GraphQL

## 🔧 Advanced Features

### Performance Optimization

- **Indexes** on frequently queried properties
- **Query Planning** with EXPLAIN and PROFILE
- **Connection Pooling** in the Neo4j driver

### Security Considerations

- **Parameterized Queries** to prevent injection
- **Authentication** and authorization
- **Input Validation** in GraphQL resolvers

### Scalability Patterns

- **Read Replicas** for query scalability
- **Clustering** for high availability
- **Caching** strategies for frequently accessed data

## 📁 File Structure

```
ddia/data-model-querying/
├── README.md                    # This file
├── graph-model.txt             # Detailed graph modeling guide
├── neo4j_graphql_example.py    # Main GraphQL API implementation
├── setup_database.py           # Database initialization script
└── requirements.txt            # Python dependencies
```

## 🎓 Learning Path

1. **Start with the Graph Model** - Read `graph-model.txt` to understand the data structure
2. **Setup the Database** - Run `setup_database.py` to populate sample data
3. **Explore Cypher Queries** - Try the examples in Neo4j Browser (http://localhost:7474)
4. **Test GraphQL API** - Use the playground at http://localhost:5000/graphql
5. **Modify and Extend** - Add new node types, relationships, or API endpoints

## 🛠️ Troubleshooting

### Common Issues

1. **Neo4j Connection Failed**

   - Check if Neo4j is running on the correct port
   - Verify username/password in configuration
   - Ensure firewall allows connections

2. **GraphQL Errors**

   - Check Python dependencies are installed
   - Verify Neo4j connection from Python
   - Look at console output for detailed error messages

3. **Query Performance**
   - Use `EXPLAIN` or `PROFILE` in Neo4j Browser
   - Ensure proper indexes are created
   - Consider query optimization patterns

### Useful Commands

```bash
# Check Neo4j status
docker ps | grep neo4j

# View Neo4j logs
docker logs <neo4j-container-id>

# Test Python Neo4j connection
python -c "from neo4j import GraphDatabase; print('Connection test passed')"
```

## 🚀 Next Steps

1. **Add Real-time Features** - Implement GraphQL subscriptions
2. **Extend the Model** - Add more node types (Events, Organizations, etc.)
3. **Build a Frontend** - Create a React/Vue.js app consuming the GraphQL API
4. **Deploy to Production** - Set up Neo4j cluster and application deployment
5. **Add Analytics** - Implement graph analytics queries (centrality, community detection)

## 📚 Additional Resources

- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cypher Query Language](https://neo4j.com/docs/cypher-manual/current/)
- [GraphQL Specification](https://graphql.org/learn/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Graph Database Concepts](https://neo4j.com/docs/getting-started/current/graphdb-concepts/)

Happy graph querying! 🎉
