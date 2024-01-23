import asyncio
from argparse import ArgumentParser

from .client import NAIClient


async def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    # Login command
    login_parser = subparsers.add_parser("login", help="Login to NovelAI to get your access token")
    login_parser.add_argument("username", help="NovelAI username")
    login_parser.add_argument("password", help="NovelAI password")

    args = parser.parse_args()

    if args.command == 'login':
        client = NAIClient(username=args.username, password=args.password)
        access_token = await client.get_access_token()
        print(access_token)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
