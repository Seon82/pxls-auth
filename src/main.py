import os

from aiohttp import ClientSession
from dotenv import load_dotenv
from expiring_dict import ExpiringDict
from lxml import html
from sanic import Sanic
from sanic.response import text

watched_users = ExpiringDict(3600 * 5)
app = Sanic("pxls_auth")


class AuthenticationError(Exception):
    pass


def format_error(error: Exception) -> text:
    if isinstance(error, ConnectionError):
        return text("Could not connect to pxls.space, please try again later.", status=500)
    if isinstance(error, AuthenticationError):
        return text(
            "Please let the bot developer know that their cookie seems to have become invalid.",
            status=500,
        )
    else:
        return text("Internal server error, please try again.", status=500)


async def get_faction_users(session) -> list[str]:
    async with session.get(url=f"https://pxls.space/profile?action=factions") as resp:

        if resp.status == 200:
            body = await resp.text()
            tree = html.fromstring(body)
            return tree.xpath(
                f"//*/div[@data-faction-id={os.environ['FACTION_ID']}]//*/div/@data-member"
            )
        elif resp.status == 403:
            raise AuthenticationError
        else:
            raise ConnectionError


async def check_user_exists(session, username) -> bool:
    async with session.get(url=f"https://pxls.space/profile/{username}") as resp:
        if resp.status == 200:
            return True
        elif resp.status == 404:
            return False
        elif resp.status == 403:
            raise AuthenticationError
        else:
            raise ConnectionError


@app.route("/watch/<username>")
async def watch(request, username):
    try:
        if not await check_user_exists(app.ctx.http_session, username):
            return text("User does not exist.", status=404)
        if username not in await get_faction_users(app.ctx.http_session):
            watched_users[username] = None
            return text("Watching for the next 5 minutes.", status=200)
        else:
            return text("You are already in that faction. Please leave and try again.", status=403)
    except Exception as error:
        format_error(error)


@app.route("/check/<username>")
async def check(request, username):
    if not username in watched_users:
        return text(
            "This user isn't being watched. Please call /watch first.",
            status=401,
        )

    try:
        return text(str(username in await get_faction_users(app.ctx.http_session)))
    except Exception as error:
        format_error(error)


@app.before_server_start
async def create_http_client(app, _):
    app.ctx.http_session = ClientSession(cookies={"pxls-token": os.environ["COOKIE"]})


if __name__ == "__main__":
    load_dotenv()
    app.run(
        host="0.0.0.0",
        port=os.getenv("PORT", 8080),
        debug=os.getenv("DEBUG", False),
        auto_reload=os.getenv("DEBUG", False),
    )
