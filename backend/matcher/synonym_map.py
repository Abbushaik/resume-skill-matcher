"""
Synonym mapping for skill normalization.
Maps raw resume tokens → canonical skill names used in job_roles.json
"""

SYNONYM_MAP = {
    # Java ecosystem
    "spring boot": "springboot",
    "spring framework": "spring",
    "spring mvc": "spring",
    "j2ee": "java",
    "jee": "java",
    "core java": "java",
    "java se": "java",
    "java ee": "java",
    "jpa": "hibernate",

    # JavaScript ecosystem
    "js": "javascript",
    "es6": "javascript",
    "ecmascript": "javascript",
    "node": "nodejs",
    "node.js": "nodejs",
    "node js": "nodejs",
    "express": "expressjs",
    "express.js": "expressjs",
    "express js": "expressjs",
    "reactjs": "react",
    "react.js": "react",
    "react js": "react",
    "next.js": "nextjs",
    "next js": "nextjs",
    "vuejs": "vue",
    "vue.js": "vue",
    "angularjs": "angular",
    "ts": "typescript",
    "socket.io": "socketio",
    "socket io": "socketio",

    # Python ecosystem
    "python3": "python",
    "scikit learn": "scikit-learn",
    "sklearn": "scikit-learn",
    "keras": "tensorflow",
    "torch": "pytorch",

    # Database
    "mysql": "sql",
    "sqlite": "sql",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "mongo db": "mongodb",
    "oracle": "sql",
    "mssql": "sql",

    # Cloud & DevOps
    "amazon web services": "aws",
    "k8s": "kubernetes",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "github actions": "ci/cd",
    "gitlab ci": "ci/cd",

    # Tools
    "version control": "git",
    "github": "git",
    "gitlab": "git",
    "bitbucket": "git",
    "unix": "linux",
    "ubuntu": "linux",
    "bash scripting": "bash",
    "shell scripting": "bash",

    # REST API
    "restful": "rest api",
    "rest": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "api development": "rest api",

    # ML/AI
    "ml": "machine learning",
    "artificial intelligence": "machine learning",
    "ai": "machine learning",
    "natural language processing": "nlp",
    "deep learning": "deep learning",
    "dl": "deep learning",

    # Frontend
    "css3": "css",
    "html5": "html",
    "sass": "css",
    "scss": "css",
    "tailwindcss": "tailwind",
    "tailwind css": "tailwind",
    "react native": "react native",
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a raw skill string:
    1. Lowercase
    2. Strip whitespace
    3. Lookup synonym map
    Returns canonical skill name.
    """
    cleaned = skill.lower().strip()
    return SYNONYM_MAP.get(cleaned, cleaned)