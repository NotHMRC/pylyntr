"""Templates for creating bots."""

from .client import LyntrClient
from .dataclasses import Post, FeedType
import requests

from abc import ABC, abstractmethod
from time import sleep

SECOND = 1
MINUTE = SECOND * 60


class PostReplyBot(LyntrClient, ABC):
    """Template for creating bots that reply to comments on a post."""

    post_message: str | None = None
    check_interval: int = MINUTE * 1
    post_id: int | None = None
    seen_comments: list[int] = []

    def init(self) -> None:
        """Initialise the bot. Normally called on run()."""
        if self.post_message is None:
            raise TypeError("Subclasses of PostReplyBot must override post_message")
        if self.post_id is None:
            self.post_id = self.create_post(self.post_message).id

    def init_custom(self) -> None:
        """Function for adding custom behaviour on startup."""
        pass

    def append_comment(self, comment: Post) -> None:
        """Mark a comment as seen. Override to change where seen comments are stored."""
        self.seen_comments.append(comment.id)

    def seen_comment(self, comment: Post) -> bool:
        """Check whether a comment has already been seen. Override to change where seen comments are stored."""
        return comment.id in self.seen_comments

    def run(self) -> None:
        """Start the bot's main loop, polling for new comments."""
        self.init()
        self.init_custom()
        try:
            while True:
                try:
                    post = self.get_post(self.post_id)  # pyright: ignore[reportArgumentType]
                    for comment in self.get_comments(post):
                        if not self.seen_comment(comment):
                            self.append_comment(comment)
                            self.handle_comment(comment)
                    self.run_after_cycle(successful=True)
                except requests.RequestException as e:
                    print(f"Request failed: {e}")
                    self.run_after_cycle(successful=False)
                sleep(self.check_interval)
        except KeyboardInterrupt:
            print("Shutting down...")
            self.run_on_shutdown()
            return

    @abstractmethod
    def handle_comment(self, comment: Post) -> None:
        """Called for each new comment. Subclasses must implement this."""
        pass

    def run_after_cycle(self, successful: bool) -> None:
        """Called after each poll cycle. Override to add custom behaviour."""
        pass

    def run_on_shutdown(self) -> None:
        """Called when the bot receives a keyboard interrupt. Override for cleanup."""
        pass


class GlobalPostCommandBot(LyntrClient, ABC):
    """Template for creating bots that reply to commands in posts."""

    check_interval: int = MINUTE * 1
    seen_posts: list[int] = []
    command_list: list[str] = []

    def init(self) -> None:
        """Initialise the bot. Normally called on run()."""
        pass

    def init_custom(self) -> None:
        """Function for adding custom behaviour on startup."""
        pass

    def append_post(self, post: Post) -> None:
        """Mark a post as seen. Override to change where seen posts are stored."""
        self.seen_posts.append(post.id)

    def seen_post(self, post: Post) -> bool:
        """Check whether a post has already been seen. Override to change where seen posts are stored."""
        return post.id in self.seen_posts

    def run(self) -> None:
        """Start the bot's main loop, polling for new posts."""
        self.init()
        self.init_custom()
        try:
            while True:
                try:
                    for post in self.posts(FeedType.New):
                        if not self.seen_post(post):
                            self.append_post(post)
                            for command in self.command_list:
                                if command in post.content:
                                    self.handle_command(post, command)
                                    break
                    self.run_after_cycle(successful=True)
                except requests.RequestException as e:
                    print(f"Request failed: {e}")
                    self.run_after_cycle(successful=False)
                sleep(self.check_interval)
        except KeyboardInterrupt:
            print("Shutting down...")
            self.run_on_shutdown()
            return

    @abstractmethod
    def handle_command(self, post: Post, command: str) -> None:
        """Called for each new post with a command. Subclasses must implement this."""
        pass

    def run_after_cycle(self, successful: bool) -> None:
        """Called after each poll cycle. Override to add custom behaviour."""
        pass

    def run_on_shutdown(self) -> None:
        """Called when the bot receives a keyboard interrupt. Override for cleanup."""
        pass
