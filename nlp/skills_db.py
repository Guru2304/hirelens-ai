SKILL_CATEGORIES = {
    "Backend": [
        "Python", "Java", "C++", "C", "Flask", "Django", "FastAPI", "Node.js",
        "Express", "REST API", "GraphQL", "Microservices", "Spring Boot",
    ],
    "Frontend": [
        "HTML", "CSS", "JavaScript", "TypeScript", "React", "Angular", "Vue",
        "Next.js", "Tailwind CSS", "Bootstrap", "Figma",
    ],
    "Data Analytics": [
        "SQL", "Excel", "Power BI", "Tableau", "Pandas", "NumPy", "Matplotlib",
        "Seaborn", "Data Analysis", "Statistics", "ETL",
    ],
    "AI/ML": [
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP",
        "Computer Vision", "scikit-learn", "Keras", "spaCy", "Transformers",
        "LLM", "Generative AI", "Prompt Engineering",
    ],
    "DevOps": [
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GitHub",
        "CI/CD", "Linux", "Terraform", "Jenkins",
    ],
    "Databases": [
        "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Redis", "Oracle",
        "Elasticsearch",
    ],
}

ALL_SKILLS = sorted({skill for skills in SKILL_CATEGORIES.values() for skill in skills})

BONUS_SKILLS = {"Docker", "AWS", "Azure", "Git", "GitHub", "SQL", "Linux", "CI/CD", "REST API"}

