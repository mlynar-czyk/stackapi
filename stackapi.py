'''Module providing JSON handling capability '''
import json
import os
import datetime
import time
import requests
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("STACKEXCHANGE_API_KEY")
env_site = os.getenv("STACKEXCHANGE_SITE")
env_tag = os.getenv("TAG")
env_date = os.getenv("FROM_DATE")
FILTER = "!BLgpu)DfJ(d9Rhoza_YLz8n3TIrIvY"


# Convert the date in UNIX timestamp format

date_obj = datetime.datetime.strptime(env_date, "%Y-%m-%d")
timestamp = int(time.mktime(date_obj.timetuple()))


def fetch_questions(tag, date, site):
    '''Fetch the questions from a given stackexchange site with a given tag'''
    base_url = "https://api.stackexchange.com/2.3/questions"
    params = {
        "order": "desc",
        "sort": "votes",
        "tagged": tag,
        "site": site,
        "filter": FILTER,
        "fromdate": date,
        "is_answered": True,
    }

    response = requests.get(base_url, params=params, timeout=10)
    data = response.json()
    print(response.url)
    return data["items"]


def fetch_answers(question_id, site):
    '''Fetch answers from given question_id from a given stackexchange site'''
    base_url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": site,
        "filter": FILTER,
        "is_accepted": True,
    }

    response = requests.get(base_url, params=params, timeout=10)
    data = response.json()
    print(response.url)
    return data["items"]


def save_to_json(file_path, questions_with_answers):
    '''Save the questions with corresponding answers in a JSON file'''
    with open(file_path, "w", encoding='utf-8') as file:
        json.dump(questions_with_answers, file, indent=4)


def main():
    '''Run the stackapi'''
    folder_path = "."  # JSON folder path
    tag = env_tag  # stackexchange tag
    date = timestamp  # UNIX timestamp date
    site = env_site  # Stackexchange site (for example : "stackoverflow")

    questions = fetch_questions(tag, date, site)
    questions_with_answers = []

    for question in questions:
        question_id = question["question_id"]
        answers = fetch_answers(question_id, site)
        time.sleep(1)

        for index, answer in enumerate(answers):
            if answer['is_accepted'] is False:
                answers.pop(index)

        question_data = {"question": question, "answers": answers}
        questions_with_answers.append(question_data)

    file_path = f"{folder_path}/questions_with_answers_{env_date}.json"
    save_to_json(file_path, questions_with_answers)

    print(f"Questions and answers have been copied in JSON format at : {file_path}")


if __name__ == "__main__":
    main()
