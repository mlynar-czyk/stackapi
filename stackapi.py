import requests
import json
import os
import datetime
import time
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("STACKEXCHANGE_API_KEY")
env_site = os.getenv("STACKEXCHANGE_SITE")
env_tag = os.getenv("TAG")
env_date = os.getenv("FROM_DATE")
filter = "!BLgpu)DfJ(d9Rhoza_YLz8n3TIrIvY"


# Convert the date in UNIX timestamp format

date_obj = datetime.datetime.strptime(env_date, "%Y-%m-%d")
timestamp = int(time.mktime(date_obj.timetuple()))

def fetch_questions(tag, date, site):
    base_url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": tag,
        "site": site,
        "filter": filter,
        "fromdate": date,
        "is_answered": True
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    print(response.url)
    return data["items"]


def fetch_answers(question_id, site):
    base_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": site,
        "filter": filter,
        "is_accepted": True
    }

    response = requests.get(base_url, params=params)
    data = response.json()
    print(response.url)
    return data["items"]

def save_to_json(file_path, questions_with_answers):
    with open(file_path, "w") as file:
        json.dump(questions_with_answers, file, indent=4)

def main():
    folder_path = "."  # JSON folder path
    tag = env_tag # stackexchange tag
    date = timestamp # UNIX timestamp date
    site = env_site  # Stackexchange site (for example : "stackoverflow")

    questions = fetch_questions(tag, date, site)
    questions_with_answers = []

    for question in questions:
        question_id = question["question_id"]
        answers = fetch_answers(question_id, site)
        
        question_data = {
            "question": question,
            "answers": answers
        }
        questions_with_answers.append(question_data)       

    file_path = f"{folder_path}/questions_with_answers.json"
    save_to_json(file_path, questions_with_answers)

    print(f"Questions and answers have been copied in JSON format at : {file_path}")

if __name__ == "__main__":
    main()
