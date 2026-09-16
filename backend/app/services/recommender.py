"""
Job role recommendation engine.

Approach:
  - Each role has a required-skill set and a nice-to-have-skill set.
  - Match score = (matched_required * 0.7 + matched_nice * 0.3) / max_possible * 100
  - We only recommend roles with at least one matched required skill.
  - Scores are clearly derived from skill overlap — not from any external
    hiring database.

Roles supported (initial set, easily extensible):
  Python Developer, Backend Developer, Full Stack Developer,
  Frontend Developer, Data Analyst, Machine Learning Engineer,
  Cybersecurity Analyst
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Role definitions                                                     #
# ------------------------------------------------------------------ #

ROLE_DEFINITIONS: dict[str, dict] = {
    "Python Developer": {
        "description": "Develops applications, scripts, and APIs using Python.",
        "required": [
            "Python", "REST API", "Git", "SQL",
        ],
        "nice_to_have": [
            "Django", "Flask", "FastAPI", "PostgreSQL", "Docker",
            "Unit Testing", "Object-Oriented Programming", "AWS",
        ],
    },
    "Backend Developer": {
        "description": "Designs and implements server-side logic and APIs.",
        "required": [
            "REST API", "Git", "SQL",
        ],
        "nice_to_have": [
            "Python", "Java", "Node.js", "Express.js", "Django", "Flask",
            "Docker", "PostgreSQL", "MongoDB", "Redis", "AWS",
            "Microservices", "CI/CD",
        ],
    },
    "Full Stack Developer": {
        "description": "Works across frontend and backend to build complete web applications.",
        "required": [
            "JavaScript", "HTML", "CSS", "REST API", "Git",
        ],
        "nice_to_have": [
            "React", "Vue.js", "Node.js", "Python", "TypeScript",
            "PostgreSQL", "MongoDB", "Docker", "AWS", "CI/CD",
        ],
    },
    "Frontend Developer": {
        "description": "Builds user interfaces and client-side web applications.",
        "required": [
            "JavaScript", "HTML", "CSS", "Git",
        ],
        "nice_to_have": [
            "React", "TypeScript", "Vue.js", "Angular", "Next.js",
            "Tailwind CSS", "Bootstrap", "REST API", "Unit Testing",
        ],
    },
    "Data Analyst": {
        "description": "Analyses data to extract actionable business insights.",
        "required": [
            "SQL", "Data Analysis",
        ],
        "nice_to_have": [
            "Python", "Pandas", "NumPy", "Statistics", "Tableau",
            "Power BI", "Excel", "Data Visualization", "Matplotlib",
            "Seaborn", "R",
        ],
    },
    "Machine Learning Engineer": {
        "description": "Builds and deploys machine learning models and pipelines.",
        "required": [
            "Python", "Machine Learning", "Scikit-learn",
        ],
        "nice_to_have": [
            "TensorFlow", "PyTorch", "Keras", "NumPy", "Pandas",
            "Deep Learning", "NLP", "Statistics", "SQL", "Docker",
            "AWS", "Data Analysis", "Jupyter",
        ],
    },
    "Cybersecurity Analyst": {
        "description": "Protects systems, networks, and data from security threats.",
        "required": [
            "Network Security",
        ],
        "nice_to_have": [
            "Penetration Testing", "SIEM", "Vulnerability Assessment",
            "Incident Response", "Firewalls", "Cryptography", "OWASP",
            "Ethical Hacking", "Burp Suite", "Wireshark", "Metasploit",
            "Linux", "Python",
        ],
    },
    "DevOps Engineer": {
        "description": "Automates infrastructure, deployment pipelines, and system reliability.",
        "required": [
            "Docker", "CI/CD", "Linux",
        ],
        "nice_to_have": [
            "Kubernetes", "AWS", "Azure", "Google Cloud", "Terraform",
            "Ansible", "Jenkins", "GitHub Actions", "Python",
            "Shell/Bash", "Git", "Nginx",
        ],
    },
    "Cloud Engineer": {
        "description": "Designs and manages scalable cloud infrastructure.",
        "required": [
            "AWS",
        ],
        "nice_to_have": [
            "Azure", "Google Cloud", "Docker", "Kubernetes", "Terraform",
            "CI/CD", "Linux", "Python", "Shell/Bash",
        ],
    },
}


# ------------------------------------------------------------------ #
# Public API                                                           #
# ------------------------------------------------------------------ #

@dataclass
class RoleMatch:
    role: str = ""
    description: str = ""
    match_score: float = 0.0          # 0–100, based on skill overlap
    matched_required: list[str] = field(default_factory=list)
    missing_required: list[str] = field(default_factory=list)
    matched_nice_to_have: list[str] = field(default_factory=list)
    missing_nice_to_have: list[str] = field(default_factory=list)
    scoring_note: str = (
        "Score is based on skill overlap between your detected skills "
        "and the role's typical skill requirements. It does not guarantee "
        "eligibility or hiring success."
    )


def recommend_roles(detected_skills: list[str]) -> list[RoleMatch]:
    """
    Return a sorted list of RoleMatch objects for all supported roles.
    Roles with zero required-skill matches are included but will have
    low scores so users see what skills they would need.
    """
    skill_set = {s.lower() for s in detected_skills}
    results: list[RoleMatch] = []

    for role_name, role_def in ROLE_DEFINITIONS.items():
        required = role_def["required"]
        nice = role_def["nice_to_have"]

        matched_req = [s for s in required if s.lower() in skill_set]
        missing_req = [s for s in required if s.lower() not in skill_set]
        matched_nice = [s for s in nice if s.lower() in skill_set]
        missing_nice = [s for s in nice if s.lower() not in skill_set]

        # Score formula — weighted overlap
        max_req_points = len(required) * 0.7
        max_nice_points = len(nice) * 0.3 if nice else 0
        max_possible = max_req_points + max_nice_points

        if max_possible == 0:
            score = 0.0
        else:
            earned = len(matched_req) * 0.7 + len(matched_nice) * 0.3
            score = round((earned / max_possible) * 100, 1)

        results.append(RoleMatch(
            role=role_name,
            description=role_def["description"],
            match_score=score,
            matched_required=matched_req,
            missing_required=missing_req,
            matched_nice_to_have=matched_nice,
            missing_nice_to_have=missing_nice,
        ))

    # Sort by score descending
    results.sort(key=lambda r: r.match_score, reverse=True)
    return results
