# Qittaでストックした記事をSlackに送信する関数を定義
import os
import random
import sys

from dotenv import load_dotenv
import requests


def fetch_qiita_stocked_articles(user_id, api_token):
    """
    Fetches the first stocked article for a Qiita user.
    
    Args:
        user_id (str): The Qiita user ID.
        api_token (str): The Qiita API token for authentication.
    
    Returns:
        list: The first article if available, otherwise an empty list.
    """
    url = f"https://qiita.com/api/v2/users/{user_id}/stocks"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        return []
    
    articles = response.json()
    if isinstance(articles, list):
        return random.sample(articles, 1)[0] if articles else []
    else:
        print(f"Error fetching data: {articles}")
        return []


def post_message_to_slack(channel, text, token):
    """
    Sends a message to a specified Slack channel.
    
    Args:
        channel (str): The Slack channel to post the message to.
        text (str): The message text to send.
        token (str): The Slack API token for authentication.
    
    Returns:
        dict: The response JSON from the Slack API.
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
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error posting message to Slack: {e}")
        return None


def main():
    load_dotenv()
    
    qiita_user_id = os.getenv('QIITA_USER_ID')
    qiita_api_token = os.getenv('QIITA_API_TOKEN')
    slack_token = os.getenv('SLACK_API_TOKEN')
    channel_name = '#qiita-stocked-article'

    if qiita_user_id and qiita_api_token:
        qiita_result = fetch_qiita_stocked_articles(qiita_user_id, qiita_api_token)
    else:
        sys.exit("Qiita user ID or API token is not set.")
    
    if qiita_result:
        message = f'今日の記事はこちら: 「{qiita_result["title"]}」\n{qiita_result["url"]}'
    else:
        message = "記事がストックされていません．"
    post_message_to_slack(channel_name, message, slack_token)


if __name__ == '__main__':
    main()
