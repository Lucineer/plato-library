#!/usr/bin/env python3
"""PLATO Library — knowledge base room. Agents submit, query, and rate knowledge entries."""

import yaml, os
from pathlib import Path
from datetime import datetime, timezone
import fcntl

WORLD_DIR = Path(os.environ.get("WORLD_DIR", "world"))
ENTRIES_DIR = WORLD_DIR / "entries"
CATEGORIES_DIR = WORLD_DIR / "categories"
COMMANDS_DIR = WORLD_DIR / "commands"
ROOMS_DIR = WORLD_DIR / "rooms"
LOGS_DIR = WORLD_DIR / "logs"
MAX_TURNS = 20

def log(level, msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [{level}] {msg}", flush=True)

def atomic_write(path, data):
    tmp = str(path) + ".tmp"
    with open(tmp, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yaml.dump(data, f, default_flow_style=False)
        fcntl.flock(f, fcntl.LOCK_UN)
    os.replace(tmp, path)

def atomic_read(path):
    try:
        with open(path) as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            d = yaml.safe_load(f)
            fcntl.flock(f, fcntl.LOCK_UN)
            return d or {}
    except FileNotFoundError:
        return {}

def process_submit(cmd, agent):
    """Submit a knowledge entry."""
    title = cmd.get("title", "")
    content = cmd.get("content", "")
    category = cmd.get("category", "general")
    tags = cmd.get("tags", [])
    source = cmd.get("source", "")
    if not title or not content:
        return {"passed": False, "error": "Title and content required"}
    if len(content) > 10000:
        return {"passed": False, "error": "Content too long (max 10000 chars)"}

    eid = f"{category}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"
    entry = {
        "id": eid, "title": title, "content": content,
        "category": category, "tags": tags, "source": source,
        "author": agent, "rating": 0, "votes": 0,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    atomic_write(ENTRIES_DIR / f"{eid}.yaml", entry)

    # Update category index
    cat = atomic_read(CATEGORIES_DIR / f"{category}.yaml")
    cat.setdefault("entries", []).append(eid)
    cat["count"] = len(cat["entries"])
    atomic_write(CATEGORIES_DIR / f"{category}.yaml", cat)

    room = atomic_read(ROOMS_DIR / "library.yaml")
    room.setdefault("stats", {})
    room["stats"]["entries"] = room["stats"].get("entries", 0) + 1
    atomic_write(ROOMS_DIR / "library.yaml", room)

    log("INFO", f"Entry '{title}' by {agent} in {category}")
    return {"passed": True, "entry_id": eid}

def process_query(cmd, agent):
    """Query knowledge entries by category, tag, or author."""
    category = cmd.get("category")
    tags = cmd.get("tags", [])
    author = cmd.get("author")
    limit = min(cmd.get("limit", 10), 50)

    results = []
    for f in ENTRIES_DIR.glob("*.yaml"):
        e = atomic_read(f)
        if not e.get("id"):
            continue
        if category and e.get("category") != category:
            continue
        if author and e.get("author") != author:
            continue
        if tags:
            if not any(t in e.get("tags", []) for t in tags):
                continue
        results.append({"id": e["id"], "title": e["title"], "category": e.get("category"),
                        "author": e.get("author"), "rating": e.get("rating", 0)})
        if len(results) >= limit:
            break

    results.sort(key=lambda x: x.get("rating", 0), reverse=True)
    log("INFO", f"Query by {agent}: {len(results)} results")
    return {"passed": True, "results": results, "count": len(results)}

def process_rate(cmd, agent):
    """Rate a knowledge entry."""
    eid = cmd.get("entry_id")
    score = cmd.get("score")  # 1-5
    if not eid:
        return {"passed": False, "error": "Missing entry_id"}
    try:
        score = int(score)
        if not 1 <= score <= 5:
            return {"passed": False, "error": "Score must be 1-5"}
    except (ValueError, TypeError):
        return {"passed": False, "error": "Score must be integer 1-5"}

    entry = atomic_read(ENTRIES_DIR / f"{eid}.yaml")
    if not entry.get("id"):
        return {"passed": False, "error": "Entry not found"}

    old_votes = entry.get("votes", 0)
    old_rating = entry.get("rating", 0)
    new_votes = old_votes + 1
    new_rating = (old_rating * old_votes + score) / new_votes
    entry["votes"] = new_votes
    entry["rating"] = round(new_rating, 2)
    atomic_write(ENTRIES_DIR / f"{eid}.yaml", entry)

    log("INFO", f"Entry {eid} rated {score}/5 by {agent}")
    return {"passed": True, "entry_id": eid, "new_rating": entry["rating"]}

def process_turns():
    for d in [COMMANDS_DIR, ENTRIES_DIR, CATEGORIES_DIR, ROOMS_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not (ROOMS_DIR / "library.yaml").exists():
        atomic_write(ROOMS_DIR / "library.yaml", {"name": "PLATO Library", "stats": {"entries": 0}})
    commands = sorted(COMMANDS_DIR.glob("*.yaml"))
    if not commands:
        return
    log("INFO", f"Processing {len(commands)} commands")
    counts = {}
    for cp in commands:
        cmd = atomic_read(cp)
        if not cmd:
            cp.unlink(); continue
        agent = cmd.get("agent", "unknown")
        counts[agent] = counts.get(agent, 0) + 1
        if counts[agent] > MAX_TURNS:
            cp.unlink(); continue
        action = cmd.get("action")
        if action == "submit":
            r = process_submit(cmd, agent)
        elif action == "query":
            r = process_query(cmd, agent)
        elif action == "rate":
            r = process_rate(cmd, agent)
        else:
            r = {"passed": False, "error": f"Unknown: {action}"}
        atomic_write(LOGS_DIR / f"turn-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}.yaml",
                     {"agent": agent, "action": action, "result": r,
                      "timestamp": datetime.now(timezone.utc).isoformat()})
        cp.unlink()
    log("INFO", f"Turn done")

if __name__ == "__main__":
    process_turns()
