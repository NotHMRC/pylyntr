import time

import requests
from enum import StrEnum
from typing import Literal

from .dataclasses import Post, User, FeedType

API_URL = "https://lyntr.gizmowizard.tech/api/v1"


class HTTPMethod(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ClientError(Exception):
    pass


class LyntrClient:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_url: str = API_URL,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Provides methods to interact with the lyntr.gizmowizard.tech API."""
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-Client-ID": client_id,
                "X-Client-Secret": client_secret,
            }
        )
        self.api_url = api_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.test()

    def test(self) -> None:
        """Test if the configured credentials work correctly."""
        try:
            self.api_request("me")
        except requests.HTTPError:
            raise ClientError("Test failed! Check credentials are correct.")

    def api_request(
        self,
        endpoint: str,
        json: dict[str, str] | None = None,
        method: HTTPMethod | Literal["auto"] = "auto",
    ) -> requests.Response:
        """Send an API request to an endpoint, with optional JSON body and method."""
        if method == "auto":
            method = HTTPMethod.POST if json else HTTPMethod.GET

        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            response = self.session.request(
                method,
                f"{self.api_url}/{endpoint}",
                json=json,
            )
            try:
                response.raise_for_status()
                return response
            except requests.HTTPError as e:
                if response.status_code == 429 and attempt < self.max_retries:
                    delay = self.retry_delay * (2**attempt)
                    time.sleep(delay)
                    last_exc = e
                    continue
                raise

        raise last_exc  # type: ignore[misc]

    def create_post(self, content: str) -> Post:
        """Create a post with the specified content."""
        return Post.from_dict(self.api_request("lynts", {"content": content}).json())

    def get_post(self, id: int) -> Post:
        """Create a Post object from an ID."""
        return Post.from_dict(self.api_request(f"lynts/{id}").json())

    def get_comments(self, post: Post) -> list[Post]:
        """Get the comments on a post."""
        response = self.api_request(f"lynts/{post.id}/comments").json()
        comments_list: list[Post] = []
        for comment in response["comments"]:
            comments_list.append(Post.from_dict(comment))
        return comments_list

    def reply(self, post: Post, reply: str) -> Post:
        """Add a comment on a post."""
        return Post.from_dict(
            self.api_request(f"lynts/{post.id}/comments", {"content": reply}).json()
        )

    def delete_post(self, post: Post) -> None:
        """Delete a post you own."""
        self.api_request(f"lynts/{post.id}", method=HTTPMethod.DELETE)

    def get_user(self, handle: str | None = None) -> User:
        """Create a User object from an ID."""
        if not handle:
            handle = User.from_dict(self.api_request("me").json()).handle
        return User.from_dict(self.api_request(f"users/{handle}").json())

    def posts(self, type: FeedType = FeedType.ForYou) -> list[Post]:
        """Get posts from the feed."""
        response = self.api_request(f"lynts?type={type}").json()
        posts_list: list[Post] = []
        for post in response["lynts"]:
            posts_list.append(Post.from_dict(post))
        return posts_list

    def like_post(self, post: Post) -> None:
        """Like a post."""
        self.api_request(f"lynts/{post.id}/like", method=HTTPMethod.POST)

    def unlike_post(self, post: Post) -> None:
        """Unlike a post."""
        self.api_request(f"lynts/{post.id}/like", method=HTTPMethod.DELETE)

    def follow_user(self, user: User) -> None:
        """Follow a user."""
        self.api_request(f"users/{user.handle}/follow", method=HTTPMethod.POST)

    def unfollow_user(self, user: User) -> None:
        """Unfollow a user."""
        self.api_request(f"users/{user.handle}/follow", method=HTTPMethod.DELETE)

    def search(self, query: str) -> list[Post]:
        """Get posts matching a query."""
        response = self.api_request(f"search?q={query}").json()
        posts_list: list[Post] = []
        for post in response["lynts"]:
            posts_list.append(Post.from_dict(post))
        return posts_list

    def update_profile(
        self,
        bio: str | None = None,
        username: str | None = None,
        name_colour: str | None = None,
    ) -> None:
        """Change the bio, username or name colour of your profile."""
        if not bio and not username and not name_colour:
            return
        if bio:
            self.api_request("me", {"bio": bio}, HTTPMethod.PATCH)
        if username:
            self.api_request("me", {"username": username}, HTTPMethod.PATCH)
        if name_colour:
            self.api_request("me", {"name_color": name_colour}, HTTPMethod.PATCH)

    def edit_post(self, post: Post, content: str) -> None:
        """Edit a post you own."""
        try:
            self.api_request(
                f"lynts/{post.id}", {"content": content}, method=HTTPMethod.PUT
            )
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 500:
                return # temporary workaround for API bug
            raise

    def latest_post(self) -> Post:
        """Get the latest post."""
        return self.posts(FeedType.New)[0]
