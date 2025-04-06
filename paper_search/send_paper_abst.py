# arxivから論文を取得し，その要約を生成してSlackに投稿する
import json
import os

import arxiv
from dotenv import load_dotenv
import openai
import requests


def get_summary(result: arxiv.Result) -> str:
    """
    Generates a summary of the given arXiv paper using OpenAI's GPT-4o model.

    Args:
        result (arxiv.Result): The arXiv paper result object.
    Returns:
        str: The generated summary of the paper in Japanese.
    """
    system = """与えられた論文の要点を3点のみでまとめ、以下のフォーマットで日本語で出力してください。

    タイトルの日本語訳
    ・要点1
    ・要点2
    ・要点3
    """

    text = f"title: {result.title}\nbody: {result.summary}"
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {'role': 'system', 'content': system},
                {'role': 'user', 'content': text}
            ],
            temperature=0.25,
        )
    except openai.error.RateLimitError as e:
        print(f"Rate limit error: {e}")
        return ""
    except openai.error.InvalidRequestError as e:
        print(f"Invalid request error: {e}")
        return ""
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return ""

    response = response.model_dump()
    summary = response['choices'][0]['message']['content']

    title, *body = summary.split('\n')
    body = '\n'.join(body)
    return f"{title}\n{body}"


def post_paper_to_notion_database(result: arxiv.Result, summary: str, notion_token: str, database_id: str) -> bool:
    """
    Posts a paper to a Notion database.

    Args:
        result (arxiv.Result): The arXiv paper result object.
        summary (str): The summary of the paper.
        notion_token (str): The Notion API token for authentication.
        database_id (str): The ID of the Notion database.
    Returns:
        bool: True if the paper was posted successfully, False otherwise.
    """
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": result.title
                        }
                    }
                ]
            },
            "Abstract": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": summary,
                        }
                    }
                ]
            },
            "Status": {
                "status": {
                    "name": "To Read",
                    "color": "gray"
                }
            },
            "URL": {
                "url": result.entry_id
            },
        }
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            data=json.dumps(data)
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error querying Notion database: {e}")
        return False


def is_title_in_notion_database(title: str, notion_token: str, database_id: str) -> bool:
    """
    Checks if a given title exists in a Notion database.

    Args:
        title (str): The title to search for in the database.
        notion_token (str): The Notion API token for authentication.
        database_id (str): The ID of the Notion database.

    Returns:
        bool: True if the title exists in the database, False otherwise.
    """
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    payload = {
        "filter": {
            "property": "Title",
            "title": {
                "contains": title
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return len(data.get("results", [])) > 0
    except requests.exceptions.RequestException as e:
        print(f"Error querying Notion database: {e}")
        return False


def fetch_paper_from_arxiv(query: str, max_results: int=1) -> list[dict]:
    """
    Fetches articles from arXiv.
    
    Returns:
        list[dict]: A list of articles matching the search query.
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance,
        sort_order=arxiv.SortOrder.Descending
    )
    articles = list(search.results())

    if articles:
        return articles
    else:
        print(f"Error fetching data: {articles}")
        return []


def post_message_to_slack(channel, text, token) -> bool:
    """
    Sends a message to a specified Slack channel.
    
    Args:
        channel (str): The Slack channel to post the message to.
        text (str): The message text to send.
        token (str): The Slack API token for authentication.
    
    Returns:
        bool: True if the message was sent successfully, False otherwise.
    """
    url = 'https://slack.com/api/chat.postMessage'
    headers = {
        'Content-type': 'application/json',
        'Authorization': f"Bearer {token}",
    }
    payload = {
        'channel': channel,
        'text': text
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error posting message to Slack: {e}")
        return None


def main():
    load_dotenv()
    
    openai.api_key = os.getenv('OPENAI_API_KEY')
    slack_token = os.getenv('SLACK_API_TOKEN')
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')
    DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

    channel_name = '#paper'
    query = "Federated Learning"
    paper_results = fetch_paper_from_arxiv(query, 10)
    if not paper_results:
        print("No papers found.")
        return

    new_paper_result = None
    for paper in paper_results:
        if not is_title_in_notion_database(paper.title, NOTION_API_KEY, DATABASE_ID):
            new_paper_result = paper
            break
    if new_paper_result is None:
        print("All papers are already in the Notion database.")
        return

    summary = get_summary(new_paper_result)
    if not summary:
        print("Failed to generate summary.")
        return

    title_en = new_paper_result.title
    date_str = new_paper_result.published.strftime("%Y-%m-%d %H:%M:%S")
    message = f"発行日: {date_str}\nURL: {new_paper_result.entry_id}\nタイトル: {title_en}\n```{summary}```"
    post_message_to_slack(channel_name, message, slack_token)

    if post_paper_to_notion_database(new_paper_result, summary, NOTION_API_KEY, DATABASE_ID):
        print("Posted to Notion successfully.")
    else:
        print("Failed to post to Notion.")
    
    print("All done!")


if __name__ == '__main__':
    main()
