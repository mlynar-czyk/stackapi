# What ?

This program retrieves questions and their corresponding answers from the Stack Exchange API based on a specified tag and date. The retrieved data is then saved in a JSON file.

The program utilizes environment variables to customize its behavior. The following environment variables are used:

- `STACKEXCHANGE_API_KEY`: The API key for accessing the Stack Exchange API.
- `STACKEXCHANGE_SITE`: The Stack Exchange site to query (e.g., "stackoverflow").
- `TAG`: The tag used to filter the questions.
- `FROM_DATE`: The date representing the earliest publication in the format "YYYY-MM-DD".

By setting these environment variables, you can customize the program to retrieve questions from different Stack Exchange sites, with different tags, and starting from a specific date.

The program retrieves the questions and their corresponding answers using the Stack Exchange API. It constructs API requests with the specified parameters, including the tag, site, and date. The responses are processed and the questions and answers are saved in a JSON file.

Executing this program will generate a JSON file (`questions_with_answers.json`) containing the retrieved questions and their associated answers based on the specified tag and date.