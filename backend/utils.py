import requests
from lxml import html

def intra_list():
    url = "http://localhost:8000/users/filter"
    params = {
        "campus": "Heilbronn",
        "email_domain": "42heilbronn.de",
        "per_page": 1000,
        "max_pages": 1
    }
    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    return [user["login"] for user in data.get("results", [])]


def projects_list_per_user(login):
    url = f'http://localhost:8000/user/{login}'
    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    data = response.json()
    projects = data["raw"]["projects_users"]
    projects_url = []
    for project in projects:
        if project.get("validated?") and project.get("cursus_ids") == [21]:
            if "exam" not in project.get("project").get("slug"):
                url = f"https://projects.intra.42.fr/projects/{project.get('project').get('slug')}/projects_users/{project.get('id')}"
                projects_url.append(url)
    return projects_url


def create_mail(intra:str) -> str:
    email= f"{intra}@student.42heilbronn.de"
    return email