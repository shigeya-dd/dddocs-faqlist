#!/usr/bin/env python3

import requests
import os
import base64
import re

def list_dir(gh_user, gh_repo, gh_path):
    gh_headers = {"Accept":"application/vnd.github.v3+json"}
    gh_token = os.getenv('GITHUB_TOKEN')
    if gh_token:
      gh_headers["Authorization"] = "token " + gh_token
    gh_url = "https://api.github.com/repos/{}/{}/contents/{}".format(gh_user, gh_repo, gh_path)

    try:
      response = requests.get(gh_url, headers=gh_headers)
      response.raise_for_status()
    except requests.exceptions.RequestException as e:
      if response.status_code == 403:
        print("API Error:", e)
    
    return response.status_code, response.json()

if __name__ == '__main__':
    gh_user = "DataDog"
    gh_repo = "documentation"
    gh_path = "content/en"

    r, top_dir = list_dir(gh_user, gh_repo, gh_path)
    if r == 200:
      for dir in top_dir:
        if dir['type'] == "dir":
          r, faq_dir = list_dir(gh_user, gh_repo, dir['path'] + "/faq")
          if r == 200:
            print("\n# {}\n".format(dir['name'].title().replace('_',' ')))
            for faq in faq_dir:
              if faq['name'] != "_index.md":
                r, faq_page = list_dir(gh_user, gh_repo, faq['path'])
                for line in base64.b64decode(faq_page['content']).decode().splitlines():
                  if "title: " in line:
                    print("- [{}]({}{})".format(
                      line.removeprefix("title:").strip(), # requires python 3.9+
                      "https://docs.datadoghq.com",
                      re.findall('content/en(.*)\.md', faq_page['path'])[0]))
                    break
