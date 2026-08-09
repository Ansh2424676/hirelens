"""
scoring/skills_dictionary.py

Static, maintainable database of skills/keywords relevant to Indian IT and
software job postings. Used by scoring/keyword_extractor.py (Day 4, next
milestone) to detect which skills appear in resume text and job description
text.

This module has NO external dependencies and NO I/O — it is a pure data file.
All terms are lowercase, matching the normalization convention used by the
keyword extractor (which lowercases input text before comparison).

To add a new skill: add it to the correct category list below, in lowercase.
Avoid duplicate terms across categories.
"""

SKILLS_DB = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#",
        "sql", "r", "go", "ruby", "php", "kotlin", "swift", "scala", "bash",
    ],

    "frameworks_libraries": [
        "flask", "django", "fastapi", "spring boot", "react", "angular",
        "vue.js", "node.js", "express.js", ".net", "laravel", "next.js",
        "jquery",
    ],

    "databases": [
        "mysql", "postgresql", "mongodb", "oracle", "sql server", "sqlite",
        "redis", "cassandra", "dynamodb", "mariadb",
    ],

    "cloud_platforms": [
        "aws", "azure", "google cloud platform", "gcp", "aws ec2",
        "aws s3", "aws lambda", "azure functions", "heroku", "render",
    ],

    "devops_tools": [
        "docker", "kubernetes", "jenkins", "git", "github", "gitlab",
        "ci/cd", "terraform", "ansible", "github actions", "bitbucket",
    ],

    "data_analytics": [
        "excel", "power bi", "tableau", "pandas", "numpy", "matplotlib",
        "seaborn", "data cleaning", "data visualization", "etl",
        "sql queries", "google sheets", "statistical analysis",
        "data wrangling",
    ],

    "ai_ml": [
        "scikit-learn", "machine learning", "tensorflow", "pytorch", "nlp",
        "deep learning", "prompt engineering", "llm", "generative ai",
        "data preprocessing", "model evaluation", "claude api", "openai api",
    ],

    "web_technologies": [
        "html", "css", "html5", "css3", "bootstrap", "tailwind css",
        "rest api", "json", "xml", "api integration", "webhooks", "graphql",
    ],

    "testing": [
        "unit testing", "pytest", "selenium", "postman", "junit",
        "test automation", "manual testing", "qa",
    ],

    "soft_skills": [
        "communication", "teamwork", "problem solving",
        "stakeholder communication", "leadership", "time management",
        "adaptability", "critical thinking", "collaboration",
        "presentation skills", "analytical thinking",
    ],

    "enterprise_it": [
        "sap", "salesforce", "servicenow", "jira", "confluence", "agile",
        "scrum", "sdlc", "itil", "erp", "crm", "ms office", "sharepoint",
        "active directory",
    ],
}