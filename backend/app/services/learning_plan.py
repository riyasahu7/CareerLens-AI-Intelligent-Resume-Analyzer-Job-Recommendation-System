"""
Skill gap analysis and personalised learning plan generator.

This is fully deterministic and rule-based.  Each skill has a curated
entry covering:
  - beginner explanation
  - learning priority category
  - suggested practice tasks
  - a mini-project idea
  - estimated study effort (clearly labelled as an estimate)

We only generate plans for skills that are *missing* from the user's
resume relative to a target role — we never fabricate skills the user
already has.
"""

from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class SkillLearnItem:
    skill: str = ""
    category: str = ""
    priority: str = "medium"        # "high" | "medium" | "low"
    beginner_explanation: str = ""
    topics_to_learn: list[str] = field(default_factory=list)
    practice_task: str = ""
    mini_project: str = ""
    estimated_hours: str = ""       # clearly labelled estimate


# ------------------------------------------------------------------ #
# Learning content database                                            #
# ------------------------------------------------------------------ #

LEARNING_CONTENT: dict[str, SkillLearnItem] = {
    "Python": SkillLearnItem(
        skill="Python",
        category="Programming Languages",
        priority="high",
        beginner_explanation=(
            "Python is a versatile, readable programming language widely used in "
            "web development, data science, automation, and AI."
        ),
        topics_to_learn=[
            "Variables, data types, and control flow",
            "Functions and modules",
            "Object-Oriented Programming (OOP)",
            "File handling and I/O",
            "Exception handling",
            "Working with APIs (requests library)",
            "Virtual environments and pip",
        ],
        practice_task="Write a script that reads a CSV file, filters rows based on a condition, and writes the result to a new file.",
        mini_project="Build a command-line task manager that stores tasks in a JSON file.",
        estimated_hours="Estimate: 40–80 hours for beginner proficiency",
    ),
    "SQL": SkillLearnItem(
        skill="SQL",
        category="Databases",
        priority="high",
        beginner_explanation=(
            "SQL (Structured Query Language) is used to query and manipulate "
            "relational databases. It is required in almost every data-related role."
        ),
        topics_to_learn=[
            "SELECT, WHERE, ORDER BY, LIMIT",
            "Joins (INNER, LEFT, RIGHT, FULL)",
            "GROUP BY and aggregate functions (COUNT, SUM, AVG)",
            "Subqueries and CTEs",
            "INSERT, UPDATE, DELETE",
            "Indexes and performance basics",
            "Window functions (ROW_NUMBER, RANK, LAG)",
        ],
        practice_task="Write queries against a sample database (e.g., SQLite Chinook) to answer 10 business questions.",
        mini_project="Design a schema for a library system and write CRUD queries for books, members, and loans.",
        estimated_hours="Estimate: 20–40 hours for beginner proficiency",
    ),
    "JavaScript": SkillLearnItem(
        skill="JavaScript",
        category="Programming Languages",
        priority="high",
        beginner_explanation=(
            "JavaScript is the primary language for web browser interactivity "
            "and is also used server-side via Node.js."
        ),
        topics_to_learn=[
            "Variables (let, const), data types",
            "Functions, arrow functions, closures",
            "DOM manipulation",
            "Promises and async/await",
            "Fetch API and working with JSON",
            "ES6+ features (destructuring, spread, modules)",
            "Event handling",
        ],
        practice_task="Build a to-do list app that runs entirely in the browser using vanilla JS.",
        mini_project="Create a weather app that fetches data from a public API and displays it dynamically.",
        estimated_hours="Estimate: 40–80 hours for beginner proficiency",
    ),
    "React": SkillLearnItem(
        skill="React",
        category="Web Frameworks & Libraries",
        priority="high",
        beginner_explanation=(
            "React is a JavaScript library for building component-based user interfaces, "
            "maintained by Meta."
        ),
        topics_to_learn=[
            "JSX and component basics",
            "Props and state",
            "useState and useEffect hooks",
            "Event handling in React",
            "React Router for navigation",
            "Fetching data with useEffect + fetch/axios",
            "Context API or state management",
        ],
        practice_task="Convert a vanilla JS to-do app into a React app with components.",
        mini_project="Build a recipe search app using a public food API with search, filter, and detail pages.",
        estimated_hours="Estimate: 40–60 hours after knowing JavaScript",
    ),
    "Machine Learning": SkillLearnItem(
        skill="Machine Learning",
        category="Data Science & ML",
        priority="high",
        beginner_explanation=(
            "Machine learning enables computers to learn patterns from data and make predictions "
            "without being explicitly programmed for each case."
        ),
        topics_to_learn=[
            "Supervised vs unsupervised learning",
            "Train/test split and cross-validation",
            "Linear and logistic regression",
            "Decision trees and random forests",
            "Model evaluation (accuracy, precision, recall, F1)",
            "Feature engineering and scaling",
            "Overfitting, underfitting, and regularisation",
        ],
        practice_task="Train a classification model on the Titanic or Iris dataset and evaluate it properly.",
        mini_project="Build a house price predictor using linear regression on a public housing dataset.",
        estimated_hours="Estimate: 60–100 hours for beginner proficiency",
    ),
    "Docker": SkillLearnItem(
        skill="Docker",
        category="Cloud & DevOps",
        priority="medium",
        beginner_explanation=(
            "Docker packages applications and their dependencies into containers, "
            "making them portable and consistent across environments."
        ),
        topics_to_learn=[
            "What containers are vs virtual machines",
            "Dockerfile syntax and building images",
            "Running and managing containers",
            "Docker Compose for multi-container apps",
            "Volumes and networking",
            "Publishing images to Docker Hub",
        ],
        practice_task="Containerise a simple Flask or Node.js app with a Dockerfile.",
        mini_project="Use Docker Compose to run a web app with a database and a reverse proxy.",
        estimated_hours="Estimate: 15–25 hours for basic proficiency",
    ),
    "AWS": SkillLearnItem(
        skill="AWS",
        category="Cloud & DevOps",
        priority="medium",
        beginner_explanation=(
            "Amazon Web Services is the leading cloud platform offering compute, storage, "
            "databases, and hundreds of other services."
        ),
        topics_to_learn=[
            "Core services: EC2, S3, RDS, Lambda",
            "IAM roles and policies",
            "VPC and security groups",
            "Deploying a web app on EC2 or Elastic Beanstalk",
            "S3 for static hosting",
            "CloudWatch for monitoring",
        ],
        practice_task="Deploy a static website to S3 and set up basic CloudWatch alarms.",
        mini_project="Deploy a containerised Flask API on EC2 with an RDS PostgreSQL database.",
        estimated_hours="Estimate: 40–60 hours for AWS Cloud Practitioner level",
    ),
    "Git": SkillLearnItem(
        skill="Git",
        category="Tools & Practices",
        priority="high",
        beginner_explanation=(
            "Git is the standard version control system for tracking code changes "
            "and collaborating with other developers."
        ),
        topics_to_learn=[
            "init, add, commit, status, log",
            "Branching and merging",
            "Resolving merge conflicts",
            "Remote repositories (push, pull, fetch)",
            "Pull requests and code review workflow",
            "Rebasing and cherry-pick basics",
        ],
        practice_task="Create a GitHub repository, make commits on a feature branch, and open a pull request.",
        mini_project="Collaborate on a small open-source project or contribute to a classmate's repo using the fork-and-PR workflow.",
        estimated_hours="Estimate: 8–15 hours for everyday proficiency",
    ),
    "REST API": SkillLearnItem(
        skill="REST API",
        category="Web Frameworks & Libraries",
        priority="high",
        beginner_explanation=(
            "REST APIs are the standard way web services communicate over HTTP using "
            "resources, HTTP methods, and JSON payloads."
        ),
        topics_to_learn=[
            "HTTP methods: GET, POST, PUT, PATCH, DELETE",
            "Status codes and their meaning",
            "JSON request and response structure",
            "Authentication (API keys, JWT, OAuth basics)",
            "Building a REST API with Flask or Express",
            "API testing with Postman or curl",
        ],
        practice_task="Build a simple CRUD REST API for a resource (e.g., notes) and test it with Postman.",
        mini_project="Create a bookmarks manager API with user authentication and full CRUD operations.",
        estimated_hours="Estimate: 15–30 hours",
    ),
    "PostgreSQL": SkillLearnItem(
        skill="PostgreSQL",
        category="Databases",
        priority="medium",
        beginner_explanation=(
            "PostgreSQL is a powerful open-source relational database with strong SQL "
            "compliance and advanced features like JSONB and full-text search."
        ),
        topics_to_learn=[
            "Installation and psql CLI",
            "Creating databases, tables, and schemas",
            "Data types including JSONB",
            "Indexes and EXPLAIN ANALYZE",
            "Stored procedures and triggers",
            "Replication basics",
        ],
        practice_task="Migrate a SQLite database to PostgreSQL and verify data integrity.",
        mini_project="Design a multi-table PostgreSQL schema for an e-commerce app and write complex queries.",
        estimated_hours="Estimate: 20–35 hours after knowing basic SQL",
    ),
    "MongoDB": SkillLearnItem(
        skill="MongoDB",
        category="Databases",
        priority="medium",
        beginner_explanation=(
            "MongoDB is a NoSQL document database that stores data as flexible JSON-like "
            "documents, suitable for rapidly changing schemas."
        ),
        topics_to_learn=[
            "Documents, collections, and databases",
            "CRUD operations with the MongoDB shell",
            "Querying with filters and projections",
            "Indexes and aggregation pipelines",
            "Schema design patterns",
            "Using PyMongo or Mongoose",
        ],
        practice_task="Build a Python script that connects to MongoDB Atlas, inserts 100 documents, and runs aggregation queries.",
        mini_project="Build a blog API backed by MongoDB with posts, tags, and comments.",
        estimated_hours="Estimate: 15–25 hours",
    ),
    "Network Security": SkillLearnItem(
        skill="Network Security",
        category="Cybersecurity",
        priority="high",
        beginner_explanation=(
            "Network security involves protecting computer networks from intruders, "
            "attacks, and unauthorised access."
        ),
        topics_to_learn=[
            "OSI and TCP/IP models",
            "Common attack types (DDoS, MITM, phishing)",
            "Firewalls, IDS, and IPS",
            "VPNs and encryption protocols (TLS/SSL)",
            "Network scanning with nmap",
            "Log analysis and monitoring",
        ],
        practice_task="Set up a home lab using VirtualBox, configure a firewall, and simulate a basic port scan.",
        mini_project="Build a network traffic analyser script using Python and Scapy.",
        estimated_hours="Estimate: 40–70 hours for CompTIA Network+ level",
    ),
    "TypeScript": SkillLearnItem(
        skill="TypeScript",
        category="Programming Languages",
        priority="medium",
        beginner_explanation=(
            "TypeScript is a statically typed superset of JavaScript that compiles to JS, "
            "reducing runtime errors in large codebases."
        ),
        topics_to_learn=[
            "Basic types: string, number, boolean, array, tuple",
            "Interfaces and type aliases",
            "Generics",
            "Enums",
            "TypeScript with React",
            "tsconfig.json basics",
        ],
        practice_task="Convert a small existing JavaScript project to TypeScript and fix all type errors.",
        mini_project="Build a typed REST API client library in TypeScript.",
        estimated_hours="Estimate: 15–25 hours after knowing JavaScript",
    ),
    "Data Analysis": SkillLearnItem(
        skill="Data Analysis",
        category="Data Science & ML",
        priority="high",
        beginner_explanation=(
            "Data analysis is the process of inspecting, cleaning, and modelling data "
            "to discover useful information and support decision-making."
        ),
        topics_to_learn=[
            "Descriptive statistics (mean, median, std dev)",
            "Data cleaning and handling missing values",
            "Exploratory data analysis (EDA) techniques",
            "Pandas for data manipulation",
            "Data visualisation with Matplotlib/Seaborn",
            "Correlation and causation",
        ],
        practice_task="Perform a full EDA on a public Kaggle dataset and write a summary of findings.",
        mini_project="Analyse a year of public sales data and build a dashboard-style report with charts.",
        estimated_hours="Estimate: 30–50 hours for intermediate proficiency",
    ),
    "Kubernetes": SkillLearnItem(
        skill="Kubernetes",
        category="Cloud & DevOps",
        priority="medium",
        beginner_explanation=(
            "Kubernetes (K8s) orchestrates containerised applications, handling deployment, "
            "scaling, and self-healing across a cluster of machines."
        ),
        topics_to_learn=[
            "Pods, Deployments, and Services",
            "ConfigMaps and Secrets",
            "Persistent Volumes",
            "Ingress controllers",
            "kubectl CLI",
            "Helm charts basics",
        ],
        practice_task="Deploy a multi-container application using minikube on your local machine.",
        mini_project="Migrate a Docker Compose app to Kubernetes with proper health checks and auto-scaling.",
        estimated_hours="Estimate: 30–50 hours for CKA study level",
    ),
    "NLP": SkillLearnItem(
        skill="NLP",
        category="Data Science & ML",
        priority="medium",
        beginner_explanation=(
            "Natural Language Processing enables computers to understand, interpret, "
            "and generate human language."
        ),
        topics_to_learn=[
            "Tokenisation and text normalisation",
            "Stop word removal and stemming/lemmatisation",
            "TF-IDF and bag-of-words representations",
            "Sentiment analysis",
            "Named entity recognition (NER)",
            "Word embeddings (Word2Vec, GloVe basics)",
            "Transformers and BERT overview",
        ],
        practice_task="Build a sentiment analyser for product reviews using scikit-learn and TF-IDF.",
        mini_project="Build a simple chatbot using intent classification with an NLP pipeline.",
        estimated_hours="Estimate: 40–70 hours for intermediate NLP",
    ),
}


# Default for skills not in the database
def _default_item(skill: str) -> SkillLearnItem:
    return SkillLearnItem(
        skill=skill,
        category="General",
        priority="medium",
        beginner_explanation=(
            f"{skill} is a skill relevant to your target role. "
            "Search for beginner tutorials on official documentation or platforms "
            "like freeCodeCamp, Coursera, or YouTube."
        ),
        topics_to_learn=["Fundamentals", "Hands-on practice", "Real project"],
        practice_task=f"Complete a beginner tutorial on {skill} and build a small demo.",
        mini_project=f"Apply {skill} in a portfolio project related to your target role.",
        estimated_hours="Estimate: varies",
    )


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

def generate_learning_plan(missing_skills: list[str]) -> list[dict]:
    """
    Generate a learning plan for a list of missing skills.
    Returns a list of plain dicts (JSON-serialisable).
    """
    plan: list[dict] = []
    for skill in missing_skills:
        item = LEARNING_CONTENT.get(skill, _default_item(skill))
        plan.append({
            "skill": item.skill,
            "category": item.category,
            "priority": item.priority,
            "beginner_explanation": item.beginner_explanation,
            "topics_to_learn": item.topics_to_learn,
            "practice_task": item.practice_task,
            "mini_project": item.mini_project,
            "estimated_hours": item.estimated_hours,
        })

    # Sort: high priority first
    priority_order = {"high": 0, "medium": 1, "low": 2}
    plan.sort(key=lambda x: priority_order.get(x["priority"], 1))
    return plan
