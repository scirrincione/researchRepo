import asyncio
from twikit import Client

USERNAME = 'sofathesofster'
EMAIL = 'icesk8es9000@gmail.com'
PASSWORD = 'Cr!cket99'

# Initialize client
client = Client('en-US')

async def main():
    await client.login(
        auth_info_1=USERNAME,
        auth_info_2=EMAIL,
        password=PASSWORD,
        cookies_file='cookies.json'
    )

    tweets = await client.get_user_tweets('2609400548', 'Tweets')

    for tweet in tweets:
        print(tweet.text)

asyncio.run(main())