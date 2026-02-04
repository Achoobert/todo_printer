import os
import requests

def get_assigned_issues():
GEMINI_API_KEY

    github_pat = os.getenv("GITHUB_PAT")
    if not github_pat:
        print("Error: GITHUB_PAT not found in environment variables.")
        return

    headers = {
        "Authorization": f"token {github_pat}",
        "Accept": "application/vnd.github.v3+json",
    }

    # GitHub API endpoint to list issues assigned to the authenticated user
    url = "https://api.github.com/repos/CruGlobal/gsdev_planning/issues/630"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        issue = response.json()

        if not issue:
            print("Issue not found.")
            return

        print("Assigned Issues:")
        print(f"- {issue["title"]}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching issues: {e}")

if __name__ == "__main__":
    get_assigned_issues()