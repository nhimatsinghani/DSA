"""
Setup script for Neo4j Social Network Database
This script creates the sample data for the social network example.

Prerequisites:
1. Neo4j database running on bolt://localhost:7687
2. Python dependencies installed: pip install -r requirements.txt

Usage:
python setup_database.py
"""

from neo4j import GraphDatabase
import sys

# Neo4j Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "password"  # Change this to your Neo4j password

def create_sample_data():
    """Creates sample data for the social network example."""
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    try:
        with driver.session() as session:
            # Clear existing data
            print("Clearing existing data...")
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create Users
            print("Creating users...")
            session.run("""
                CREATE 
                  (alice:User {id: 1, name: "Alice Johnson", email: "alice@example.com", joinDate: "2023-01-15"}),
                  (bob:User {id: 2, name: "Bob Smith", email: "bob@example.com", joinDate: "2023-02-20"}),
                  (charlie:User {id: 3, name: "Charlie Brown", email: "charlie@example.com", joinDate: "2023-03-10"}),
                  (diana:User {id: 4, name: "Diana Prince", email: "diana@example.com", joinDate: "2023-04-05"})
            """)
            
            # Create Skills
            print("Creating skills...")
            session.run("""
                CREATE 
                  (python:Skill {name: "Python", category: "Programming"}),
                  (javascript:Skill {name: "JavaScript", category: "Programming"}),
                  (graphql:Skill {name: "GraphQL", category: "API"}),
                  (neo4j:Skill {name: "Neo4j", category: "Database"}),
                  (react:Skill {name: "React", category: "Frontend"}),
                  (docker:Skill {name: "Docker", category: "DevOps"})
            """)
            
            # Create Groups
            print("Creating groups...")
            session.run("""
                CREATE 
                  (devs:Group {id: 1, name: "Developers", description: "Software developers community"}),
                  (graphdb:Group {id: 2, name: "Graph Database Enthusiasts", description: "Neo4j and graph database lovers"}),
                  (frontend:Group {id: 3, name: "Frontend Developers", description: "UI/UX and frontend technology enthusiasts"})
            """)
            
            # Create Posts
            print("Creating posts...")
            session.run("""
                CREATE 
                  (post1:Post {id: 1, title: "Getting Started with Neo4j", content: "Neo4j is amazing for connected data. Here's how to get started...", createdAt: "2023-05-01T10:00:00Z"}),
                  (post2:Post {id: 2, title: "GraphQL vs REST", content: "Let's discuss the pros and cons of GraphQL compared to REST APIs...", createdAt: "2023-05-02T14:30:00Z"}),
                  (post3:Post {id: 3, title: "Python Tips and Tricks", content: "Here are some useful Python tricks that will improve your code...", createdAt: "2023-05-03T09:15:00Z"}),
                  (post4:Post {id: 4, title: "Building React Applications", content: "Best practices for building scalable React applications...", createdAt: "2023-05-04T16:20:00Z"}),
                  (post5:Post {id: 5, title: "Docker in Production", content: "How to use Docker containers in production environments...", createdAt: "2023-05-05T11:45:00Z"})
            """)
            
            # Create Comments
            print("Creating comments...")
            session.run("""
                CREATE 
                  (comment1:Comment {id: 1, content: "Great introduction to Neo4j!", createdAt: "2023-05-01T11:00:00Z"}),
                  (comment2:Comment {id: 2, content: "Thanks for sharing this comprehensive guide!", createdAt: "2023-05-01T12:00:00Z"}),
                  (comment3:Comment {id: 3, content: "I prefer GraphQL for most of my APIs now", createdAt: "2023-05-02T15:00:00Z"}),
                  (comment4:Comment {id: 4, content: "These Python tips are really helpful!", createdAt: "2023-05-03T10:30:00Z"}),
                  (comment5:Comment {id: 5, content: "React hooks changed everything for me", createdAt: "2023-05-04T17:00:00Z"})
            """)
            
            # Create FOLLOWS relationships
            print("Creating follow relationships...")
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (bob:User {name: "Bob Smith"})
                CREATE (alice)-[:FOLLOWS]->(bob)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (charlie:User {name: "Charlie Brown"})
                CREATE (alice)-[:FOLLOWS]->(charlie)
            """)
            
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (diana:User {name: "Diana Prince"})
                CREATE (bob)-[:FOLLOWS]->(diana)
            """)
            
            session.run("""
                MATCH (charlie:User {name: "Charlie Brown"}), (alice:User {name: "Alice Johnson"})
                CREATE (charlie)-[:FOLLOWS]->(alice)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (bob:User {name: "Bob Smith"})
                CREATE (diana)-[:FOLLOWS]->(bob)
            """)
            
            # Create POSTED relationships
            print("Creating posted relationships...")
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (post1:Post {id: 1})
                CREATE (alice)-[:POSTED]->(post1)
            """)
            
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (post2:Post {id: 2})
                CREATE (bob)-[:POSTED]->(post2)
            """)
            
            session.run("""
                MATCH (charlie:User {name: "Charlie Brown"}), (post3:Post {id: 3})
                CREATE (charlie)-[:POSTED]->(post3)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (post4:Post {id: 4})
                CREATE (diana)-[:POSTED]->(post4)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (post5:Post {id: 5})
                CREATE (alice)-[:POSTED]->(post5)
            """)
            
            # Create LIKES relationships
            print("Creating like relationships...")
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (post1:Post {id: 1})
                CREATE (bob)-[:LIKES]->(post1)
            """)
            
            session.run("""
                MATCH (charlie:User {name: "Charlie Brown"}), (post1:Post {id: 1})
                CREATE (charlie)-[:LIKES]->(post1)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (post2:Post {id: 2})
                CREATE (alice)-[:LIKES]->(post2)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (post3:Post {id: 3})
                CREATE (diana)-[:LIKES]->(post3)
            """)
            
            # Create COMMENTED relationships
            print("Creating comment relationships...")
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (comment1:Comment {id: 1})
                CREATE (bob)-[:COMMENTED]->(comment1)
            """)
            
            session.run("""
                MATCH (charlie:User {name: "Charlie Brown"}), (comment2:Comment {id: 2})
                CREATE (charlie)-[:COMMENTED]->(comment2)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (comment3:Comment {id: 3})
                CREATE (diana)-[:COMMENTED]->(comment3)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (comment4:Comment {id: 4})
                CREATE (alice)-[:COMMENTED]->(comment4)
            """)
            
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (comment5:Comment {id: 5})
                CREATE (bob)-[:COMMENTED]->(comment5)
            """)
            
            # Create REPLIED_TO relationships
            print("Creating reply relationships...")
            session.run("""
                MATCH (comment1:Comment {id: 1}), (post1:Post {id: 1})
                CREATE (comment1)-[:REPLIED_TO]->(post1)
            """)
            
            session.run("""
                MATCH (comment2:Comment {id: 2}), (post1:Post {id: 1})
                CREATE (comment2)-[:REPLIED_TO]->(post1)
            """)
            
            session.run("""
                MATCH (comment3:Comment {id: 3}), (post2:Post {id: 2})
                CREATE (comment3)-[:REPLIED_TO]->(post2)
            """)
            
            session.run("""
                MATCH (comment4:Comment {id: 4}), (post3:Post {id: 3})
                CREATE (comment4)-[:REPLIED_TO]->(post3)
            """)
            
            session.run("""
                MATCH (comment5:Comment {id: 5}), (post4:Post {id: 4})
                CREATE (comment5)-[:REPLIED_TO]->(post4)
            """)
            
            # Create HAS_SKILL relationships
            print("Creating skill relationships...")
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (python:Skill {name: "Python"})
                CREATE (alice)-[:HAS_SKILL]->(python)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (neo4j:Skill {name: "Neo4j"})
                CREATE (alice)-[:HAS_SKILL]->(neo4j)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (docker:Skill {name: "Docker"})
                CREATE (alice)-[:HAS_SKILL]->(docker)
            """)
            
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (javascript:Skill {name: "JavaScript"})
                CREATE (bob)-[:HAS_SKILL]->(javascript)
            """)
            
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (graphql:Skill {name: "GraphQL"})
                CREATE (bob)-[:HAS_SKILL]->(graphql)
            """)
            
            session.run("""
                MATCH (charlie:User {name: "Charlie Brown"}), (python:Skill {name: "Python"})
                CREATE (charlie)-[:HAS_SKILL]->(python)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (react:Skill {name: "React"})
                CREATE (diana)-[:HAS_SKILL]->(react)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (javascript:Skill {name: "JavaScript"})
                CREATE (diana)-[:HAS_SKILL]->(javascript)
            """)
            
            # Create MEMBER_OF relationships
            print("Creating group membership relationships...")
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (devs:Group {name: "Developers"})
                CREATE (alice)-[:MEMBER_OF]->(devs)
            """)
            
            session.run("""
                MATCH (alice:User {name: "Alice Johnson"}), (graphdb:Group {name: "Graph Database Enthusiasts"})
                CREATE (alice)-[:MEMBER_OF]->(graphdb)
            """)
            
            session.run("""
                MATCH (bob:User {name: "Bob Smith"}), (devs:Group {name: "Developers"})
                CREATE (bob)-[:MEMBER_OF]->(devs)
            """)
            
            session.run("""
                MATCH (charlie:User {name: "Charlie Brown"}), (devs:Group {name: "Developers"})
                CREATE (charlie)-[:MEMBER_OF]->(devs)
            """)
            
            session.run("""
                MATCH (diana:User {name: "Diana Prince"}), (frontend:Group {name: "Frontend Developers"})
                CREATE (diana)-[:MEMBER_OF]->(frontend)
            """)
            
            # Create indexes
            print("Creating indexes...")
            session.run("CREATE INDEX user_name_index IF NOT EXISTS FOR (u:User) ON (u.name)")
            session.run("CREATE INDEX user_email_index IF NOT EXISTS FOR (u:User) ON (u.email)")
            session.run("CREATE INDEX post_created_index IF NOT EXISTS FOR (p:Post) ON (p.createdAt)")
            session.run("CREATE INDEX skill_name_index IF NOT EXISTS FOR (s:Skill) ON (s.name)")
            
            print("✅ Sample data created successfully!")
            print("\nSample data includes:")
            print("- 4 Users: Alice Johnson, Bob Smith, Charlie Brown, Diana Prince")
            print("- 6 Skills: Python, JavaScript, GraphQL, Neo4j, React, Docker")
            print("- 3 Groups: Developers, Graph Database Enthusiasts, Frontend Developers")
            print("- 5 Posts with various topics")
            print("- 5 Comments on posts")
            print("- Follow relationships between users")
            print("- Skill assignments to users")
            print("- Group memberships")
            print("\nYou can now run the GraphQL API with: python neo4j_graphql_example.py")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        sys.exit(1)
    finally:
        driver.close()

if __name__ == "__main__":
    print("🚀 Setting up Neo4j Social Network Database...")
    print(f"Connecting to Neo4j at {NEO4J_URI}")
    print("⚠️  This will delete all existing data in the database!")
    
    # Ask for confirmation
    response = input("Do you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Setup cancelled.")
        sys.exit(0)
    
    create_sample_data() 