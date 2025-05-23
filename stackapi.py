import json
import os
import datetime
import time
import requests
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("STACKEXCHANGE_API_KEY")
env_site = os.getenv("STACKEXCHANGE_SITE")
env_tag = os.getenv("TAG")
env_date = os.getenv("FROM_DATE")

# Validate environment variables
if not all([api_key, env_site, env_tag, env_date]):
    raise ValueError("Missing required environment variables")

# Convert date to UNIX timestamp
try:
    date_obj = datetime.datetime.strptime(env_date, "%Y-%m-%d")
    timestamp = int(time.mktime(date_obj.timetuple()))
except ValueError:
    raise ValueError("Invalid FROM_DATE format. Use YYYY-MM-DD")

# Check if the date is in the future
current_time = int(time.time())
if timestamp > current_time:
    print("Warning: The specified date is in the future. No results will be returned.")

def fetch_questions_with_accepted(tag, date, site):
    """
    Fetch questions with accepted answers from a Stack Exchange site, including question body.
    """
    base_url = "https://api.stackexchange.com/2.3/search/advanced"
    params = {
        "order": "desc",
        "sort": "votes",
        "accepted": "true",  # Filter for questions with accepted answers
        "tagged": tag,
        "site": site,
        "filter": "withbody",  # Include question body
        "fromdate": date,
        "key": api_key,
        "page": 1,
        "pagesize": 100
    }
    all_questions = []
    while True:
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "backoff" in data:
                print(f"Received backoff: pausing for {data['backoff']} seconds")
                time.sleep(data["backoff"])
            all_questions.extend(data["items"])
            print(f"Quota remaining: {data['quota_remaining']} of {data['quota_max']}")
            if not data.get("has_more", False):
                break
            params["page"] += 1
            time.sleep(0.1)  # Respect per-second rate limit
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            if response.status_code == 400:
                print(f"Bad Request: Check parameters or filter. Response: {response.text}")
            break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break
    return all_questions

def fetch_answers_for_questions(question_ids, site):
    """
    Fetch answers for a list of question IDs, batching up to 100 IDs per request.
    """
    batch_size = 100
    all_answers = []
    for i in range(0, len(question_ids), batch_size):
        batch = question_ids[i:i+batch_size]
        ids_str = ';'.join(map(str, batch))
        base_url = f"https://api.stackexchange.com/2.3/questions/{ids_str}/answers"
        params = {
            "order": "desc",
            "sort": "votes",
            "site": site,
            "filter": "withbody",
            "key": api_key
        }
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "backoff" in data:
                print(f"Received backoff: pausing for {data['backoff']} seconds")
                time.sleep(data["backoff"])
            all_answers.extend(data["items"])
            print(f"Quota remaining: {data['quota_remaining']} of {data['quota_max']}")
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            if response.status_code == 400:
                print(f"Bad Request: Check parameters or filter. Response: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
    return all_answers

def pair_questions_with_accepted_answers(questions, all_answers):
    """
    Pair each question with its accepted answer.
    """
    question_dict = {q["question_id"]: q for q in questions}
    answer_dict = {}
    for answer in all_answers:
        qid = answer["question_id"]
        if qid not in answer_dict:
            answer_dict[qid] = []
        answer_dict[qid].append(answer)
    
    result = []
    for q in questions:
        qid = q["question_id"]
        accepted_answers = [a for a in answer_dict.get(qid, []) if a.get("is_accepted", False)]
        if len(accepted_answers) == 1:
            result.append({
                "question": q,
                "accepted_answer": accepted_answers[0]
            })
        elif len(accepted_answers) > 1:
            print(f"Warning: Question {qid} has multiple accepted answers.")
        else:
            print(f"Warning: Question {qid} has no accepted answer despite being filtered.")
    return result

def save_to_json(file_path, data):
    """
    Save the paired questions and answers to a JSON file.
    """
    with open(file_path, "w", encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def save_to_jsonl(file_path, data):
    """
    Save the paired questions and answers to a JSONL file in prompt-response format.
    """
    with open(file_path, "w", encoding='utf-8') as file:
        for item in data:
            question_title = item["question"].get("title", "")
            question_body = item["question"].get("body", "")
            prompt = f"{question_title}\n\n{question_body}".strip()
            response = item["accepted_answer"].get("body", "")
            
            jsonl_entry = {
                "prompt": prompt,
                "response": response
            }
            file.write(json.dumps(jsonl_entry, ensure_ascii=False) + "\n")

def main():
    """
    Run the Stack Exchange API fetcher.
    """
    parser = argparse.ArgumentParser(description="Fetch Stack Exchange questions and answers")
    parser.add_argument("--jsonl", action="store_true", help="Output in JSONL format instead of JSON")
    args = parser.parse_args()
    
    folder_path = "."
    tag = env_tag
    date = timestamp
    site = env_site

    # Step 1: Fetch questions with accepted answers
    questions = fetch_questions_with_accepted(tag, date, site)
    
    # Step 2: Extract question IDs
    question_ids = [q["question_id"] for q in questions]
    
    # Step 3: Fetch answers for all questions
    all_answers = fetch_answers_for_questions(question_ids, site)
    
    # Step 4: Pair questions with their accepted answers
    paired_data = pair_questions_with_accepted_answers(questions, all_answers)
    
    # Step 5: Save to appropriate format
    if args.jsonl:
        file_path = f"{folder_path}/questions_with_accepted_answers_{env_date}.jsonl"
        save_to_jsonl(file_path, paired_data)
        print(f"Questions and accepted answers saved to JSONL: {file_path}")
    else:
        file_path = f"{folder_path}/questions_with_accepted_answers_{env_date}.json"
        save_to_json(file_path, paired_data)
        print(f"Questions and accepted answers saved to JSON: {file_path}")

if __name__ == "__main__":
    main()