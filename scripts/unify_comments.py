import csv
import glob
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "unified"
OUT_FILE = OUT_DIR / "comments_unified.csv"

COLUMNS = [
    # --- comentario ---
    "comment_id", "platform", "parent_comment_id", "is_reply", "depth",
    "text", "created_at", "like_count", "reply_count",
    "author_id", "author_name", "mentions", "has_attachment", "comment_url",
    # reacciones por comentario (solo Facebook)
    "react_like", "react_love", "react_care", "react_haha",
    "react_wow", "react_sad", "react_angry",
    # --- post / video ---
    "post_id", "post_url", "post_title", "post_text", "post_created_at",
    "post_type", "post_like_count", "post_comment_count", "post_share_count",
    "post_hashtags", "post_author",
]


# --------------------------------------------------------------------------
# utilidades
# --------------------------------------------------------------------------
def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_many(pattern):
    items = []
    for p in sorted(glob.glob(str(RAW / pattern))):
        items.extend(load_json(p))
    return items


def iso_utc(value):
    """Normaliza a 'YYYY-MM-DDTHH:MM:SSZ'. Acepta ISO (con/sin ms) o epoch."""
    if value in (None, ""):
        return ""
    if isinstance(value, (int, float)):
        if value > 1e11:  # milisegundos
            value /= 1000
        return datetime.fromtimestamp(value, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def join_list(values):
    return "|".join(str(v) for v in (values or []))


def row_template():
    return {c: "" for c in COLUMNS}


# --------------------------------------------------------------------------
# Facebook
# --------------------------------------------------------------------------
def facebook_rows():
    posts = {str(p["id"]): p for p in load_many("facebook/posts/*.json")}
    rows, orphans = [], 0

    for c in load_many("facebook/comments/*.json"):
        post = posts.get(str(c["postId"]))
        if post is None:
            orphans += 1

        r = row_template()
        r.update(
            comment_id=f"fb_{c['commentId']}",
            platform="facebook",
            parent_comment_id=f"fb_{c['replyToCommentId']}" if c.get("replyToCommentId") else "",
            is_reply=bool(c.get("isReply")),
            depth=c.get("threadingDepth", 0),
            text=c.get("text") or "",
            created_at=iso_utc(c.get("date") or c.get("timestamp")),
            like_count=c.get("likesCount", ""),
            reply_count=c.get("commentsCount", ""),
            author_id=c.get("profileId") or "",
            author_name=c.get("profileName") or "",
            mentions=join_list(c.get("mentions")),
            has_attachment=bool(c.get("attachmentType")),
            comment_url=c.get("commentUrl") or "",
            react_like=c.get("reactionLikeCount", ""),
            react_love=c.get("reactionLoveCount", ""),
            react_care=c.get("reactionCareCount", ""),
            react_haha=c.get("reactionHahaCount", ""),
            react_wow=c.get("reactionWowCount", ""),
            react_sad=c.get("reactionSadCount", ""),
            react_angry=c.get("reactionAngryCount", ""),
            post_id=f"fb_{c['postId']}",
            post_url=c.get("postUrl") or "",
        )
        if post:
            media = post.get("media") or []
            r.update(
                post_url=post.get("url") or r["post_url"],
                post_text=post.get("text") or "",
                post_created_at=iso_utc(post.get("createdAt")),
                post_type=media[0].get("type", "") if media else "text",
                post_like_count=post.get("reactions", ""),
                post_comment_count=post.get("comments", ""),
                post_share_count=post.get("shares", ""),
                post_author=post.get("authorName") or "",
            )
        else:
            # respaldo: titulo/descripcion que viene dentro del comentario
            r["post_text"] = c.get("postDescription") or ""
        rows.append(r)
    return rows, {"orphans": orphans}


# --------------------------------------------------------------------------
# Instagram
# --------------------------------------------------------------------------
def instagram_rows():
    posts = {str(p["id"]): p for p in load_json(RAW / "instagram/posts/posts.json")}
    rows, orphans, placeholders = [], 0, 0

    def build(c, parent_id, depth):
        post = posts.get(str(c["mediaId"]))
        r = row_template()
        r.update(
            comment_id=f"ig_{c['id']}",
            platform="instagram",
            parent_comment_id=f"ig_{parent_id}" if parent_id else "",
            is_reply=parent_id is not None,
            depth=depth,
            text=c.get("text") or "",
            created_at=iso_utc(c.get("timestamp")),
            like_count=c.get("likesCount", ""),
            reply_count=c.get("repliesCount", ""),
            author_id=c.get("ownerId") or "",
            author_name=c.get("ownerUsername") or "",
            mentions=join_list(c.get("mentions")),
            has_attachment="",  # IG no lo reporta
            comment_url=c.get("commentUrl") or "",
            post_id=f"ig_{c['mediaId']}",
            post_url=c.get("postUrl") or "",
        )
        if post:
            r.update(
                post_url=post.get("url") or r["post_url"],
                post_text=post.get("caption") or "",
                post_created_at=iso_utc(post.get("timestamp")),
                post_type=post.get("type", ""),
                post_like_count=post.get("likesCount", ""),
                post_comment_count=post.get("commentsCount", ""),
                post_hashtags=join_list(post.get("hashtags")),
                post_author=post.get("ownerUsername") or "",
            )
        return r, post is None

    for c in load_many("instagram/comments/*.json"):
        if "id" not in c:  # placeholder "No comments found on this post"
            placeholders += 1
            continue
        r, orphan = build(c, None, 0)
        orphans += orphan
        rows.append(r)
        for rep in c.get("replies") or []:
            rr, orphan = build(rep, rep.get("parentCommentId") or c["id"], rep.get("depth") or 1)
            orphans += orphan
            rows.append(rr)
    return rows, {"orphans": orphans, "placeholders_descartados": placeholders}


# --------------------------------------------------------------------------
# YouTube
# --------------------------------------------------------------------------
def youtube_rows():
    videos = {v["video_id"]: v for v in load_json(RAW / "youtube/videos/videos.json")}
    rows, orphans = [], 0

    for c in load_json(RAW / "youtube/comments/comments.json"):
        v = videos.get(c["video_id"])
        if v is None:
            orphans += 1
        r = row_template()
        r.update(
            comment_id=f"yt_{c['comment_id']}",
            platform="youtube",
            parent_comment_id=f"yt_{c['parent_comment_id']}" if c.get("parent_comment_id") else "",
            is_reply=bool(c.get("is_reply")),
            depth=1 if c.get("is_reply") else 0,
            text=c.get("text") or "",
            created_at=iso_utc(c.get("published_at")),
            like_count=c.get("like_count", ""),
            reply_count=c.get("total_reply_count", ""),
            author_name=c.get("author") or "",
            post_id=f"yt_{c['video_id']}",
            post_url=f"https://www.youtube.com/watch?v={c['video_id']}",
            post_type="video",
        )
        if v:
            r.update(
                post_title=v.get("title") or "",
                post_text=v.get("description") or "",
                post_created_at=iso_utc(v.get("published_at")),
                post_author=v.get("channel_title") or "",
            )
        rows.append(r)
    return rows, {"orphans": orphans}


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    all_rows, report = [], {}
    for name, fn in (("facebook", facebook_rows), ("instagram", instagram_rows), ("youtube", youtube_rows)):
        rows, info = fn()
        report[name] = {"filas": len(rows), **info}
        all_rows.extend(rows)

    # Validaciones basicas
    ids = Counter(r["comment_id"] for r in all_rows)
    dups = [i for i, n in ids.items() if n > 1]
    if dups:
        raise ValueError(f"comment_id duplicados: {len(dups)} (ej. {dups[:3]})")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # utf-8-sig: conserva emojis y abre bien en Excel / Power BI
    with open(OUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(all_rows)

    print(f"Archivo generado: {OUT_FILE}  ({OUT_FILE.stat().st_size / 1_048_576:.1f} MB)")
    print(f"Total de comentarios: {len(all_rows)}")
    for name, info in report.items():
        print(f"  {name:<10} {info}")


if __name__ == "__main__":
    main()
