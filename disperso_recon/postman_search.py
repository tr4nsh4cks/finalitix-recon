"""Search Postman for Disperso collections, workspaces, envs."""
import requests, json, os, time

POSTMAN_KEY = os.environ.get("POSTMAN_API_KEY", "")
BASE = "https://api.getpostman.com"
HEADERS = {"X-Api-Key": POSTMAN_KEY, "Content-Type": "application/json"}

OUT = os.path.join(os.path.dirname(__file__), "postman_results")
os.makedirs(OUT, exist_ok=True)

def api(path, params=None):
    r = requests.get(f"{BASE}{path}", headers=HEADERS, params=params, timeout=30)
    return r.status_code, r.json() if r.headers.get("content-type","").startswith("application/json") else r.text

# ============================================
print("=" * 60)
print("1. MY WORKSPACES (see if any are shared/team)")
print("=" * 60)
s, d = api("/workspaces")
if s == 200:
    workspaces = d.get("workspaces", [])
    print(f"  {len(workspaces)} workspaces")
    for ws in workspaces:
        print(f"  [{ws.get('type','')}] {ws.get('name','')} (id={ws.get('id','')})")
else:
    print(f"  {s}: {d}")

# ============================================
print("\n" + "=" * 60)
print("2. ALL COLLECTIONS")
print("=" * 60)
s, d = api("/collections")
if s == 200:
    collections = d.get("collections", [])
    print(f"  {len(collections)} collections")
    for col in collections:
        name = col.get("name", "")
        uid = col.get("uid", "")
        print(f"  {name} (uid={uid})")
else:
    print(f"  {s}: {d}")

# ============================================
print("\n" + "=" * 60)
print("3. ALL ENVIRONMENTS")
print("=" * 60)
s, d = api("/environments")
if s == 200:
    envs = d.get("environments", [])
    print(f"  {len(envs)} environments")
    for env in envs:
        print(f"  {env.get('name','')} (uid={env.get('uid','')})")
else:
    print(f"  {s}: {d}")

# ============================================
print("\n" + "=" * 60)
print("4. SEARCH POSTMAN NETWORK (public) for 'disperso'")
print("=" * 60)

# Postman API v10 global search
for query in ["disperso", "disperso.com", "disperso spei", "tuxpan payments"]:
    s, d = api("/search", params={"q": query, "limit": 10})
    if s == 200:
        results = d.get("data", [])
        print(f"\n  Search '{query}': {len(results)} results")
        for r in results:
            print(f"    [{r.get('type','')}] {r.get('name','')} by {r.get('publisherHandle','')} (id={r.get('id','')})")
    else:
        print(f"  Search '{query}': {s}")
        # Try alternate search endpoint
        s2, d2 = api(f"/search/all", params={"q": query})
        if s2 == 200:
            print(f"    alt: {json.dumps(d2)[:300]}")
    time.sleep(1)

# ============================================
print("\n" + "=" * 60)
print("5. EXPORT EACH COLLECTION (look for disperso-related)")
print("=" * 60)

if s == 200 or True:  # always run
    s, d = api("/collections")
    if s == 200:
        for col in d.get("collections", []):
            name = col.get("name", "").lower()
            uid = col.get("uid", "")
            # Check ALL collections for disperso references
            s2, d2 = api(f"/collections/{uid}")
            if s2 == 200:
                col_data = d2.get("collection", {})
                col_json = json.dumps(col_data)
                
                # Search for disperso-related strings
                hits = []
                for kw in ["disperso", "spei", "rdrrxexkm4", "SOCtEIx2s", "4fjbm9corn"]:
                    if kw.lower() in col_json.lower():
                        hits.append(kw)
                
                if hits:
                    print(f"\n  !!! MATCH: {col.get('name','')} -> keywords: {hits}")
                    # Save full collection
                    fname = f"disperso_match_{uid.replace(':','_')}.json"
                    with open(os.path.join(OUT, fname), "w") as f:
                        json.dump(col_data, f, indent=2, default=str)
                    print(f"      Saved to {fname}")
                    
                    # Extract variables and auth
                    info = col_data.get("info", {})
                    print(f"      Name: {info.get('name','')}")
                    
                    # Look for auth
                    auth = col_data.get("auth", {})
                    if auth:
                        print(f"      Auth: {json.dumps(auth)[:200]}")
                    
                    # Look for variables
                    variables = col_data.get("variable", [])
                    if variables:
                        print(f"      Variables:")
                        for v in variables:
                            print(f"        {v.get('key','')}: {v.get('value','')}")
                    
                    # Extract all URLs from items
                    def extract_urls(items, depth=0):
                        for item in items:
                            if "item" in item:
                                extract_urls(item["item"], depth+1)
                            if "request" in item:
                                r = item["request"]
                                url = r.get("url", {})
                                if isinstance(url, dict):
                                    raw = url.get("raw", "")
                                else:
                                    raw = str(url)
                                method = r.get("method", "?")
                                name = item.get("name", "")
                                print(f"        {method} {raw[:80]} [{name}]")
                    
                    items = col_data.get("item", [])
                    if items:
                        print(f"      Requests:")
                        extract_urls(items)
                else:
                    pass  # No match, skip silently
            time.sleep(0.5)

# ============================================
print("\n" + "=" * 60)
print("6. EXPORT EACH ENVIRONMENT (look for disperso)")
print("=" * 60)

s, d = api("/environments")
if s == 200:
    for env in d.get("environments", []):
        uid = env.get("uid", "")
        s2, d2 = api(f"/environments/{uid}")
        if s2 == 200:
            env_data = d2.get("environment", {})
            env_json = json.dumps(env_data)
            
            hits = []
            for kw in ["disperso", "spei", "rdrrxexkm4", "SOCtEIx2s", "4fjbm9corn"]:
                if kw.lower() in env_json.lower():
                    hits.append(kw)
            
            if hits:
                print(f"\n  !!! ENV MATCH: {env.get('name','')} -> keywords: {hits}")
                fname = f"disperso_env_{uid.replace(':','_')}.json"
                with open(os.path.join(OUT, fname), "w") as f:
                    json.dump(env_data, f, indent=2, default=str)
                print(f"      Saved to {fname}")
                
                values = env_data.get("values", [])
                for v in values:
                    print(f"        {v.get('key','')}: {v.get('value','')[:80]}")
        time.sleep(0.5)

# ============================================
print("\n" + "=" * 60)
print("7. PUBLIC POSTMAN COLLECTIONS via web scrape")
print("=" * 60)

# Try the Postman public API network search
import urllib.request
for q in ["disperso", "disperso%20spei", "disperso%20chile"]:
    try:
        rq = urllib.request.Request(
            f"https://www.postman.com/_api/ws/proxy",
            data=json.dumps({
                "service": "search",
                "method": "POST",
                "path": "/search-all",
                "body": {
                    "queryIndices": ["runtime.collection", "runtime.workspace", "adp.api"],
                    "queryText": q.replace("%20", " "),
                    "size": 10,
                    "from": 0
                }
            }).encode(),
            headers={"Content-Type": "application/json",
                     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        import ssl
        ctx = ssl._create_unverified_context()
        resp = urllib.request.urlopen(rq, timeout=15, context=ctx)
        body = json.loads(resp.read())
        data = body.get("data", [])
        print(f"\n  Public '{q}': {len(data)} results")
        for item in data[:5]:
            doc = item.get("document", {})
            print(f"    [{doc.get('entityType','')}] {doc.get('name','')} by {doc.get('publisherHandle','')} (id={doc.get('id','')})")
            if doc.get("summary"):
                print(f"      Summary: {doc['summary'][:100]}")
    except Exception as e:
        print(f"  Public '{q}': {e}")
    time.sleep(1)

print("\n" + "=" * 60)
print("POSTMAN SEARCH DONE")
print("=" * 60)
