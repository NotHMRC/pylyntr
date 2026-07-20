from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


@dataclass
class PartialUser:
    id: int
    handle: str
    bio: str | None = None
    created_at: datetime | None = None
    username: str | None = None
    iq: int | None = None
    verified: bool | None = None
    admin: bool | None = None
    contributor: bool | None = None
    login_streak: int | None = None
    followers: int | None = None
    follows_user: bool | None = None
    lyntr_coins: int | None = None

    name_colour: Any | None = None  # needs research


@dataclass
class User:
    id: int
    handle: str
    bio: str | None
    created_at: datetime
    username: str
    iq: int
    verified: bool

    lynt_coins: int | None = None
    admin: bool | None = None
    contributor: bool | None = None
    login_streak: int | None = None
    followers: int | None = None
    follows_user: bool | None = None
    name_colour: str | None = None
    following: int | None = None

    @classmethod
    def from_dict(cls, user: dict):
        user_class = User(
            id=user["id"],
            username=user["username"],
            handle=user["handle"],
            bio=user["bio"],
            iq=user["iq"],
            created_at=datetime.fromisoformat(
                user["created_at"].replace("Z", "+00:00")
            ),
            verified=user["verified"],
        )
        if user.get("lynt_coins", None) is not None:
            user_class.lynt_coins = user["lynt_coins"]
        if user.get("is_admin", None) is not None:
            user_class.admin = user["is_admin"]
        if user.get("follower_count", None) is not None:
            user_class.followers = user["follower_count"]
        if user.get("following_count", None) is not None:
            user_class.following = user["following_count"]
        if user.get("contributor", None) is not None:
            user_class.contributor = user["contributor"]
        return user_class


@dataclass
class PartialPost:
    id: int
    content: str
    created_at: datetime | None = None
    reposted: bool | None = None
    has_image: bool | None = None
    views: int | None = None
    likes: int | None = None
    reposts: int | None = None
    comments: int | None = None
    liked_by_user: bool | None = None
    reposted_by_user: bool | None = None
    liked_by_followed: bool | None = None
    user: PartialUser | User | None = None
    referenced_lynts: list[Any] | None = None  # needs research

    edited_at: datetime | None = None
    gif_url: str | None = None
    gif_preview_url: str | None = None
    poll: Any | None = None  # needs research


@dataclass
class Post:
    id: int
    content: str
    created_at: datetime
    reposted: bool
    has_image: bool
    views: int
    likes: int
    reposts: int
    comments: int
    liked_by_user: bool
    reposted_by_user: bool
    liked_by_followed: bool
    user: PartialUser | User
    referenced_lynts: list[Any] = field(default_factory=list)  # needs research

    edited_at: datetime | None = None
    gif_url: str | None = None
    gif_preview_url: str | None = None
    parent: PartialPost | None = None  # needs research
    poll: Any | None = None  # needs research

    @classmethod
    def from_dict(cls, post: dict):
        post_class = Post(
            id=int(post["id"]),
            content=post["content"],
            created_at=datetime.fromisoformat(post["createdAt"].replace("Z", "+00:00")),
            reposted=post["reposted"],
            has_image=post["has_image"],
            views=int(post["views"]),
            likes=int(post["likeCount"]),
            reposts=int(post["repostCount"]),
            comments=int(post["commentCount"]),
            user=User(
                id=post["userId"],
                handle=post["handle"],
                bio=post["bio"],
                created_at=datetime.fromisoformat(
                    post["userCreatedAt"].replace("Z", "+00:00")
                ),
                username=post["username"],
                iq=post["iq"],
                verified=post["verified"],
                admin=post["isAdmin"],
                contributor=post["contributor"],
                login_streak=post["loginStreak"],
                followers=post["followerCount"],
                follows_user=post["followsViewer"],
            ),
            liked_by_user=post["likedByUser"],
            reposted_by_user=post["repostedByUser"],
            liked_by_followed=post["likedByFollowed"],
        )
        if post.get("editedAt", None):
            post_class.edited_at = datetime.fromisoformat(
                post["editedAt"].replace("Z", "+00:00")
            )
        if post.get("gif_url", None):
            post_class.gif_url = post["gif_url"]
        if post.get("gif_preview_url", None):
            post_class.gif_preview_url = post["gif_preview_url"]
        if post.get("poll", None):
            post_class.poll = post["poll"]
        if post.get("referencedLynts", None):
            post_class.referenced_lynts = post["referencedLynts"]
        return post_class


class FeedType(StrEnum):
    ForYou = "For you"
    New = "New"
    Following = "Following"
