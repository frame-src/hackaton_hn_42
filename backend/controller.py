import requests
from lxml import html

URI=  "http://localhost:8000"


def intra_list():
    url = f"{URI}/users/filter"
    params = {
        "campus": "Heilbronn",
        "email_domain": "42heilbronn.de",
        "per_page": 1000,
        "max_pages": 1
    }
    headers = {"accept": "application/json"}

    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    students = []
    for user in data.get("results", []):
        info = {"intra": user["login"], "id": user["raw"]["id"] }
        students.append(info)
    return students

def projects_list_per_user(login):
    url = f'{URI}/user/{login}'
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


def winner_handler():
    students_array = intra_list()
    output_data = []
    for student in students_array:
        student_id = student.get("id")
        url = f'{URI}/user/{student_id}/evaluators'
        headers = {"accept": "application/json"}
        response = requests.get(url, headers=headers)
        for value in response:
            data = value
            info= {"intra": student["intra"], "data": data}
            output_data.append(info)
    print (output_data)

winner_handler()
