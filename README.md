# pylyntr

A Python library for the [lyntr.gizmowizard.tech](https://lyntr.gizmowizard.tech) API.

## Installation

### With [uv](https://docs.astral.sh/uv) (recommended)
```bash
uv init . # if pyproject.toml doesn't already exist
uv add "pylyntr @ git+https://github.com/NotHMRC/pylyntr.git"
```

### With pip
```bash
python3 -m venv .venv # if venv doesn't already exist
source .venv/bin/activate
pip install "pylyntr @ git+https://github.com/NotHMRC/pylyntr.git"
```

Requires Python 3.10+.

## Quick Start

```python
from pylyntr import LyntrClient

client = LyntrClient(
    client_id="CLIENT_ID",
    client_secret="CLIENT_SECRET",
)

# Create a post
post = client.create_post("Hello from pylyntr!")
print(post.content)

# Get your profile
me = client.get_user()
print(f"@{me.handle} - {me.username}")

# Fetch the feed
for post in client.posts():
    print(f"@{post.user.username}: {post.content}")
```

Get a client id and secret from the [Developer API page](https://lyntr.gizmowizard.tech/developer).

## API Reference

### `LyntrClient`

```python
LyntrClient(
    client_id: str,
    client_secret: str,
    api_url: str = "https://lyntr.gizmowizard.tech/api/v1",
    max_retries: int = 3,
    retry_delay: float = 1.0,
)
```

Constructs the client and validates credentials via `test()`.

| Method | Returns | Description |
|---|---|---|
| `create_post(content)` | `Post` | Create a post |
| `get_post(id)` | `Post` | Fetch a post by ID |
| `delete_post(post)` | `None` | Delete a post you own |
| `edit_post(post, content)` | `None` | Edit a post you own |
| `get_comments(post)` | `list[Post]` | Get comments on a post |
| `reply(post, reply)` | `Post` | Reply to a post |
| `like_post(post)` | `None` | Like a post |
| `unlike_post(post)` | `None` | Unlike a post |
| `posts(feed_type)` | `list[Post]` | Get posts from a feed (default `FeedType.ForYou`) |
| `latest_post()` | `Post` | Get the most recent post from the New feed |
| `search(query)` | `list[Post]` | Search posts by query |
| `get_user(handle)` | `User` | Fetch a user by handle (defaults to self) |
| `follow_user(user)` | `None` | Follow a user |
| `unfollow_user(user)` | `None` | Unfollow a user |
| `update_profile(bio, username, name_colour)` | `None` | Update your profile bio, username, or name colour |
| `test()` | `None` | Validate credentials (called automatically on init) |

### `FeedType`

An enum used with `client.posts()`:

- `FeedType.ForYou` - algorithm
- `FeedType.New` - latest posts
- `FeedType.Following` - posts from followed users

### `Post`

A dataclass with fields: `id`, `content`, `created_at`, `reposted`, `has_image`, `views`, `likes`, `reposts`, `comments`, `liked_by_user`, `reposted_by_user`, `liked_by_followed`, `user`, `referenced_lynts`, `edited_at`, `gif_url`, `gif_preview_url`, `poll`.

### `User`

A dataclass with fields: `id`, `handle`, `bio`, `created_at`, `username`, `iq`, `verified`, `lynt_coins`, `admin`, `contributor`, `login_streak`, `followers`, `follows_user`, `name_colour`, `following`.
