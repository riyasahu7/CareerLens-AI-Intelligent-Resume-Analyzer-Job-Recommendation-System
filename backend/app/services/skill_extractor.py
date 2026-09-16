"""
Skill extraction service.

Approach:
  - Maintain a modular skill dictionary organised by category.
  - Tokenise and normalise resume text.
  - Match tokens/phrases against known skills using exact and alias matching.
  - Avoid false positives by requiring word-boundary matching.
  - Clearly distinguish *detected* skills (present in text) from
    *inferred* skills (which we do NOT do — inference would be speculative).

This is a deterministic rule-based approach.  It is accurate for explicitly
mentioned skills and does not invent skills that are not present.
"""

import re
import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Skill dictionary                                                     #
# ------------------------------------------------------------------ #
# Structure: category -> list of (canonical_name, [aliases])
# Aliases allow matching "js" -> "JavaScript", "ml" -> "Machine Learning", etc.
# Keep entries lowercase for matching; display names are title-cased separately.

SKILL_CATEGORIES: dict[str, list[tuple[str, list[str]]]] = {
    "Programming Languages": [
        ("Python", ["python", "py"]),
        ("JavaScript", ["javascript", "js", "es6", "es2015"]),
        ("TypeScript", ["typescript", "ts"]),
        ("Java", ["java"]),
        ("C++", ["c++", "cpp", "c plus plus"]),
        ("C#", ["c#", "csharp", "c sharp"]),
        ("C", ["\\bc\\b"]),
        ("Go", ["golang", "\\bgo\\b"]),
        ("Rust", ["rust", "\\brust\\b"]),
        ("Ruby", ["ruby", "\\bruby\\b"]),
        ("PHP", ["\\bphp\\b"]),
        ("Swift", ["\\bswift\\b"]),
        ("Kotlin", ["kotlin"]),
        ("Scala", ["scala"]),
        ("R", ["\\br programming\\b", "\\br language\\b"]),
        ("MATLAB", ["matlab"]),
        ("Shell/Bash", ["bash", "shell script", "shell scripting", "zsh", "powershell"]),
        ("SQL", ["\\bsql\\b"]),
        ("HTML", ["\\bhtml\\b", "html5"]),
        ("CSS", ["\\bcss\\b", "css3"]),
    ],
    "Web Frameworks & Libraries": [
        ("React", ["react", "reactjs", "react.js"]),
        ("Vue.js", ["vue", "vuejs", "vue.js"]),
        ("Angular", ["angular", "angularjs"]),
        ("Next.js", ["next.js", "nextjs"]),
        ("Node.js", ["node.js", "nodejs", "node"]),
        ("Express.js", ["express", "expressjs", "express.js"]),
        ("Django", ["django"]),
        ("Flask", ["flask"]),
        ("FastAPI", ["fastapi"]),
        ("Spring Boot", ["spring boot", "spring framework", "springboot"]),
        ("Laravel", ["laravel"]),
        ("Ruby on Rails", ["rails", "ruby on rails", "ror"]),
        ("Svelte", ["svelte"]),
        ("Tailwind CSS", ["tailwind", "tailwindcss"]),
        ("Bootstrap", ["bootstrap"]),
        ("GraphQL", ["graphql"]),
        ("REST API", ["rest api", "restful", "rest"]),
    ],
    "Databases": [
        ("PostgreSQL", ["postgresql", "postgres"]),
        ("MySQL", ["mysql"]),
        ("MongoDB", ["mongodb", "mongo"]),
        ("SQLite", ["sqlite"]),
        ("Redis", ["redis"]),
        ("Elasticsearch", ["elasticsearch", "elastic search"]),
        ("Cassandra", ["cassandra"]),
        ("DynamoDB", ["dynamodb", "dynamo db"]),
        ("Firebase", ["firebase"]),
        ("Oracle DB", ["oracle", "oracle db", "oracle database"]),
        ("MS SQL Server", ["sql server", "mssql", "microsoft sql"]),
    ],
    "Cloud & DevOps": [
        ("AWS", ["aws", "amazon web services"]),
        ("Azure", ["azure", "microsoft azure"]),
        ("Google Cloud", ["gcp", "google cloud", "google cloud platform"]),
        ("Docker", ["docker"]),
        ("Kubernetes", ["kubernetes", "k8s"]),
        ("CI/CD", ["ci/cd", "ci cd", "continuous integration", "continuous deployment"]),
        ("Jenkins", ["jenkins"]),
        ("GitHub Actions", ["github actions"]),
        ("Terraform", ["terraform"]),
        ("Ansible", ["ansible"]),
        ("Linux", ["linux", "ubuntu", "centos", "debian"]),
        ("Nginx", ["nginx"]),
        ("Apache", ["apache"]),
    ],
    "Data Science & ML": [
        ("Machine Learning", ["machine learning", "\\bml\\b"]),
        ("Deep Learning", ["deep learning", "\\bdl\\b"]),
        ("NumPy", ["numpy"]),
        ("Pandas", ["pandas"]),
        ("Scikit-learn", ["scikit-learn", "sklearn", "scikit learn"]),
        ("TensorFlow", ["tensorflow"]),
        ("PyTorch", ["pytorch"]),
        ("Keras", ["keras"]),
        ("Matplotlib", ["matplotlib"]),
        ("Seaborn", ["seaborn"]),
        ("Jupyter", ["jupyter", "jupyter notebook"]),
        ("NLP", ["nlp", "natural language processing"]),
        ("Computer Vision", ["computer vision", "opencv", "cv2"]),
        ("Data Analysis", ["data analysis", "data analytics"]),
        ("Data Visualization", ["data visualization", "data visualisation"]),
        ("Statistics", ["statistics", "statistical analysis"]),
        ("Power BI", ["power bi", "powerbi"]),
        ("Tableau", ["tableau"]),
        ("Apache Spark", ["spark", "apache spark", "pyspark"]),
        ("Hadoop", ["hadoop"]),
    ],
    "Cybersecurity": [
        ("Network Security", ["network security"]),
        ("Penetration Testing", ["penetration testing", "pen testing", "pentest"]),
        ("SIEM", ["siem"]),
        ("Vulnerability Assessment", ["vulnerability assessment", "vulnerability scanning"]),
        ("Incident Response", ["incident response"]),
        ("Firewalls", ["firewall", "firewalls"]),
        ("Cryptography", ["cryptography", "encryption"]),
        ("OWASP", ["owasp"]),
        ("Ethical Hacking", ["ethical hacking", "ethical hacker"]),
        ("Burp Suite", ["burp suite"]),
        ("Wireshark", ["wireshark"]),
        ("Metasploit", ["metasploit"]),
        ("CompTIA Security+", ["security+", "comptia security"]),
        ("CEH", ["ceh", "certified ethical hacker"]),
        ("CISSP", ["cissp"]),
    ],
    "Tools & Practices": [
        ("Git", ["\\bgit\\b"]),
        ("GitHub", ["github"]),
        ("GitLab", ["gitlab"]),
        ("JIRA", ["jira"]),
        ("Agile", ["agile", "scrum", "kanban", "sprint"]),
        ("Unit Testing", ["unit test", "unit testing"]),
        ("Test-Driven Development", ["tdd", "test driven development"]),
        ("Microservices", ["microservices", "micro services"]),
        ("System Design", ["system design"]),
        ("API Design", ["api design"]),
        ("Object-Oriented Programming", ["oop", "object oriented", "object-oriented"]),
        ("Data Structures", ["data structures"]),
        ("Algorithms", ["algorithms", "dsa"]),
    ],
    "Soft Skills": [
        ("Communication", ["communication"]),
        ("Teamwork", ["teamwork", "team work", "collaboration"]),
        ("Problem Solving", ["problem solving", "problem-solving"]),
        ("Leadership", ["leadership"]),
        ("Project Management", ["project management"]),
        ("Time Management", ["time management"]),
    ],
}


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

@dataclass
class SkillExtractionResult:
    skills: list[str] = field(default_factory=list)
    skills_by_category: dict[str, list[str]] = field(default_factory=dict)
    total_count: int = 0


def extract_skills(text: str) -> SkillExtractionResult:
    """
    Detect skills present in the given text.

    Returns a SkillExtractionResult with deduplicated skill names and
    a category breakdown.  All skills are *detected* (explicitly present
    in text) — nothing is inferred.
    """
    if not text or not text.strip():
        return SkillExtractionResult()

    normalised = _normalise_text(text)
    found: dict[str, str] = {}  # canonical_name -> category

    for category, skills in SKILL_CATEGORIES.items():
        for canonical, aliases in skills:
            if _matches(canonical, aliases, normalised):
                found[canonical] = category

    # Group by category
    by_cat: dict[str, list[str]] = {}
    for skill, cat in found.items():
        by_cat.setdefault(cat, []).append(skill)

    all_skills = list(found.keys())

    return SkillExtractionResult(
        skills=all_skills,
        skills_by_category=by_cat,
        total_count=len(all_skills),
    )


def get_all_known_skills() -> list[str]:
    """Return a flat list of all canonical skill names in the dictionary."""
    return [
        canonical
        for skills in SKILL_CATEGORIES.values()
        for canonical, _ in skills
    ]


# ------------------------------------------------------------------ #
# Private helpers                                                      #
# ------------------------------------------------------------------ #

def _normalise_text(text: str) -> str:
    """Lower-case the text; preserve punctuation for regex matching."""
    return text.lower()


def _matches(canonical: str, aliases: list[str], text: str) -> bool:
    """Return True if any alias (or the canonical name) appears in text."""
    candidates = [canonical.lower()] + aliases
    for pattern in candidates:
        # If the alias already contains regex meta-chars, use it as-is
        if any(c in pattern for c in r"\b()[]"):
            regex = pattern
        else:
            # Wrap in word boundaries for exact word matching
            regex = r"\b" + re.escape(pattern) + r"\b"
        try:
            if re.search(regex, text):
                return True
        except re.error:
            # Malformed regex — fall back to simple substring
            if pattern in text:
                return True
    return False
