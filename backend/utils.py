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


def scrape_first_three_texts(url):
    """Scrape the first 3 correction-item link texts from the given project page"""
    headers = {
        "Cookie": "_intra_42_session=YOUR_SESSION_COOKIE_HERE",
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    tree = html.fromstring(response.content)
    # Correct and valid XPath
    texts = tree.xpath('//div[contains(@class, "correction-item")]//a/text()')
    # Return only the first 3 and strip whitespace
    return [t.strip() for t in texts[:3] if t.strip()]


if __name__ == "__main__":
    # login = "trosinsk"
    # projects_url = projects_list_per_user(login)
    # for pr in projects_url:
    #     texts = scrape_first_three_texts(pr)
    endpoint_url = "http://localhost:8000/eval_page"
    url = "https://projects.intra.42.fr/projects/42cursus-fract-ol/projects_users/3452857"
    response = requests.get(endpoint_url, params={"url": url})
    print(response.text)
