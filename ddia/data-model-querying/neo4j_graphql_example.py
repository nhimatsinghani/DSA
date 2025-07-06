"""
Neo4j Cypher + GraphQL Integration Example
Social Network Platform API

Requirements:
pip install neo4j graphene flask flask-graphql python-dotenv

Usage:
1. Start Neo4j database (Docker: docker run -p 7474:7474 -p 7687:7687 neo4j:latest)
2. Run this script: python neo4j_graphql_example.py
3. Visit http://localhost:5000/graphql for GraphQL playground
"""

from neo4j import GraphDatabase
import graphene
from graphene import ObjectType, String, Int, List, Field, Argument
from flask import Flask
from flask_graphql import GraphQLView
import os
from datetime import datetime

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"  # Change this to your Neo4j password

class Neo4jService:
    def __init__(self, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def close(self):
        self.driver.close()
    
    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

# Initialize Neo4j service
neo4j_service = Neo4jService(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD)

# GraphQL Schema Types
class User(ObjectType):
    id = Int()
    name = String()
    email = String()
    join_date = String()
    
class Post(ObjectType):
    id = Int()
    title = String()
    content = String()
    created_at = String()
    author = Field(User)
    like_count = Int()
    comment_count = Int()

class Comment(ObjectType):
    id = Int()
    content = String()
    created_at = String()
    author = Field(User)

class Skill(ObjectType):
    name = String()
    category = String()

class Group(ObjectType):
    id = Int()
    name = String()
    description = String()
    member_count = Int()

class UserWithStats(ObjectType):
    id = Int()
    name = String()
    email = String()
    join_date = String()
    followers_count = Int()
    following_count = Int()
    posts_count = Int()
    skills = List(Skill)

# GraphQL Queries
class Query(ObjectType):
    # Get user by name
    user = Field(User, name=Argument(String, required=True))
    
    # Get user with detailed stats
    user_with_stats = Field(UserWithStats, name=Argument(String, required=True))
    
    # Get user's posts
    user_posts = List(Post, user_name=Argument(String, required=True))
    
    # Get user's network feed
    user_feed = List(Post, user_name=Argument(String, required=True), limit=Argument(Int, default_value=10))
    
    # Get suggested users to follow
    suggested_users = List(User, user_name=Argument(String, required=True))
    
    # Get users with common skills
    users_with_common_skills = List(User, user_name=Argument(String, required=True))
    
    # Get group members
    group_members = List(User, group_name=Argument(String, required=True))
    
    # Search users by skill
    users_by_skill = List(User, skill_name=Argument(String, required=True))

    def resolve_user(self, info, name):
        query = """
        MATCH (u:User {name: $name})
        RETURN u.id as id, u.name as name, u.email as email, u.joinDate as join_date
        """
        result = neo4j_service.execute_query(query, {"name": name})
        if result:
            return User(**result[0])
        return None

    def resolve_user_with_stats(self, info, name):
        query = """
        MATCH (u:User {name: $name})
        OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower:User)
        OPTIONAL MATCH (u)-[:FOLLOWS]->(following:User)
        OPTIONAL MATCH (u)-[:POSTED]->(post:Post)
        OPTIONAL MATCH (u)-[:HAS_SKILL]->(skill:Skill)
        RETURN u.id as id, u.name as name, u.email as email, u.joinDate as join_date,
               COUNT(DISTINCT follower) as followers_count,
               COUNT(DISTINCT following) as following_count,
               COUNT(DISTINCT post) as posts_count,
               COLLECT(DISTINCT {name: skill.name, category: skill.category}) as skills
        """
        result = neo4j_service.execute_query(query, {"name": name})
        if result:
            data = result[0]
            skills = [Skill(**skill) for skill in data['skills'] if skill['name']]
            return UserWithStats(
                id=data['id'],
                name=data['name'],
                email=data['email'],
                join_date=data['join_date'],
                followers_count=data['followers_count'],
                following_count=data['following_count'],
                posts_count=data['posts_count'],
                skills=skills
            )
        return None

    def resolve_user_posts(self, info, user_name):
        query = """
        MATCH (u:User {name: $user_name})-[:POSTED]->(p:Post)
        OPTIONAL MATCH (p)<-[:LIKES]-(liker:User)
        OPTIONAL MATCH (p)<-[:REPLIED_TO]-(comment:Comment)
        RETURN p.id as id, p.title as title, p.content as content, p.createdAt as created_at,
               COUNT(DISTINCT liker) as like_count,
               COUNT(DISTINCT comment) as comment_count
        ORDER BY p.createdAt DESC
        """
        result = neo4j_service.execute_query(query, {"user_name": user_name})
        posts = []
        for record in result:
            posts.append(Post(
                id=record['id'],
                title=record['title'],
                content=record['content'],
                created_at=record['created_at'],
                like_count=record['like_count'],
                comment_count=record['comment_count']
            ))
        return posts

    def resolve_user_feed(self, info, user_name, limit):
        query = """
        MATCH (u:User {name: $user_name})-[:FOLLOWS]->(following:User)-[:POSTED]->(p:Post)
        OPTIONAL MATCH (p)<-[:LIKES]-(liker:User)
        OPTIONAL MATCH (p)<-[:REPLIED_TO]-(comment:Comment)
        RETURN following.name as author_name, p.id as id, p.title as title, 
               p.content as content, p.createdAt as created_at,
               COUNT(DISTINCT liker) as like_count,
               COUNT(DISTINCT comment) as comment_count
        ORDER BY p.createdAt DESC
        LIMIT $limit
        """
        result = neo4j_service.execute_query(query, {"user_name": user_name, "limit": limit})
        posts = []
        for record in result:
            author = User(name=record['author_name'])
            posts.append(Post(
                id=record['id'],
                title=record['title'],
                content=record['content'],
                created_at=record['created_at'],
                author=author,
                like_count=record['like_count'],
                comment_count=record['comment_count']
            ))
        return posts

    def resolve_suggested_users(self, info, user_name):
        query = """
        MATCH (u:User {name: $user_name})-[:FOLLOWS]->(friend:User)-[:FOLLOWS]->(suggestion:User)
        WHERE u <> suggestion AND NOT (u)-[:FOLLOWS]->(suggestion)
        RETURN suggestion.id as id, suggestion.name as name, 
               suggestion.email as email, suggestion.joinDate as join_date,
               COUNT(friend) as mutual_friends
        ORDER BY mutual_friends DESC
        LIMIT 5
        """
        result = neo4j_service.execute_query(query, {"user_name": user_name})
        users = []
        for record in result:
            users.append(User(
                id=record['id'],
                name=record['name'],
                email=record['email'],
                join_date=record['join_date']
            ))
        return users

    def resolve_users_with_common_skills(self, info, user_name):
        query = """
        MATCH (u:User {name: $user_name})-[:HAS_SKILL]->(skill:Skill)<-[:HAS_SKILL]-(other:User)
        WHERE u <> other
        RETURN DISTINCT other.id as id, other.name as name, 
               other.email as email, other.joinDate as join_date
        """
        result = neo4j_service.execute_query(query, {"user_name": user_name})
        users = []
        for record in result:
            users.append(User(
                id=record['id'],
                name=record['name'],
                email=record['email'],
                join_date=record['join_date']
            ))
        return users

    def resolve_group_members(self, info, group_name):
        query = """
        MATCH (g:Group {name: $group_name})<-[:MEMBER_OF]-(member:User)
        RETURN member.id as id, member.name as name, 
               member.email as email, member.joinDate as join_date
        """
        result = neo4j_service.execute_query(query, {"group_name": group_name})
        users = []
        for record in result:
            users.append(User(
                id=record['id'],
                name=record['name'],
                email=record['email'],
                join_date=record['join_date']
            ))
        return users

    def resolve_users_by_skill(self, info, skill_name):
        query = """
        MATCH (s:Skill {name: $skill_name})<-[:HAS_SKILL]-(user:User)
        RETURN user.id as id, user.name as name, 
               user.email as email, user.joinDate as join_date
        """
        result = neo4j_service.execute_query(query, {"skill_name": skill_name})
        users = []
        for record in result:
            users.append(User(
                id=record['id'],
                name=record['name'],
                email=record['email'],
                join_date=record['join_date']
            ))
        return users

# GraphQL Mutations
class CreateUser(graphene.Mutation):
    class Arguments:
        name = String(required=True)
        email = String(required=True)
    
    user = Field(User)
    
    def mutate(self, info, name, email):
        query = """
        CREATE (u:User {name: $name, email: $email, joinDate: $join_date})
        RETURN u.id as id, u.name as name, u.email as email, u.joinDate as join_date
        """
        join_date = datetime.now().strftime("%Y-%m-%d")
        result = neo4j_service.execute_query(query, {
            "name": name, 
            "email": email, 
            "join_date": join_date
        })
        if result:
            return CreateUser(user=User(**result[0]))
        return None

class FollowUser(graphene.Mutation):
    class Arguments:
        follower_name = String(required=True)
        following_name = String(required=True)
    
    success = graphene.Boolean()
    
    def mutate(self, info, follower_name, following_name):
        query = """
        MATCH (follower:User {name: $follower_name}), (following:User {name: $following_name})
        WHERE follower <> following
        CREATE (follower)-[:FOLLOWS]->(following)
        RETURN COUNT(*) as created
        """
        result = neo4j_service.execute_query(query, {
            "follower_name": follower_name,
            "following_name": following_name
        })
        return FollowUser(success=result[0]['created'] > 0 if result else False)

class Mutation(ObjectType):
    create_user = CreateUser.Field()
    follow_user = FollowUser.Field()

# Create GraphQL Schema
schema = graphene.Schema(query=Query, mutation=Mutation)

# Flask App
app = Flask(__name__)
app.debug = True

# Add GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface
    )
)

@app.route('/')
def index():
    return '''
    <h1>Neo4j + GraphQL Social Network API</h1>
    <p>Visit <a href="/graphql">/graphql</a> to access the GraphQL playground</p>
    
    <h2>Example Queries:</h2>
    <pre>
    # Get user with stats
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
    
    # Get user's posts
    {
      userPosts(userName: "Alice Johnson") {
        title
        content
        createdAt
        likeCount
        commentCount
      }
    }
    
    # Get user's network feed
    {
      userFeed(userName: "Alice Johnson", limit: 5) {
        title
        content
        createdAt
        author {
          name
        }
        likeCount
      }
    }
    
    # Get suggested users
    {
      suggestedUsers(userName: "Alice Johnson") {
        name
        email
      }
    }
    </pre>
    
    <h2>Example Mutations:</h2>
    <pre>
    # Create a new user
    mutation {
      createUser(name: "John Doe", email: "john@example.com") {
        user {
          name
          email
        }
      }
    }
    
    # Follow a user
    mutation {
      followUser(followerName: "Alice Johnson", followingName: "John Doe") {
        success
      }
    }
    </pre>
    '''

if __name__ == '__main__':
    print("Starting Neo4j + GraphQL Social Network API...")
    print("Make sure Neo4j is running on bolt://localhost:7687")
    print("Visit http://localhost:5000/graphql for GraphQL playground")
    
    try:
        app.run(debug=True, port=5000)
    finally:
        neo4j_service.close() 