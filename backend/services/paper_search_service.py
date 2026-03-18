import requests, time, json, hashlib, os, re, xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime, timedelta

CACHE_DIR = "./search_cache"
CACHE_EXPIRY_HOURS = 24

def _cache_key(query, limit, offset):
    return hashlib.md5(f"{query.lower().strip()}|{limit}|{offset}".encode()).hexdigest()

def _cache_get(query, limit, offset):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, _cache_key(query, limit, offset) + ".json")
    if not os.path.exists(path): return None
    try:
        with open(path, "r", encoding="utf-8") as f: data = json.load(f)
        if datetime.now() - datetime.fromisoformat(data["cached_at"]) > timedelta(hours=CACHE_EXPIRY_HOURS):
            os.remove(path); return None
        print(f"[CACHE HIT] '{query}'"); return data["papers"]
    except: return None

def _cache_set(query, limit, offset, papers):
    if not papers: return
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, _cache_key(query, limit, offset) + ".json")
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"cached_at": datetime.now().isoformat(), "query": query, "papers": papers}, f, ensure_ascii=False, indent=2)
    except Exception as e: print(f"[CACHE ERROR] {e}")

def _safe_get(url, params=None, headers=None, max_retries=3, timeout=12):
    h = {"User-Agent": "ResearchAssistant/2.0 (academic use)"}
    if headers: h.update(headers)
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=h, timeout=timeout)
            if resp.status_code == 200: return resp
            elif resp.status_code == 429:
                wait = min(int(resp.headers.get("Retry-After", 5*(attempt+1))), 20)
                print(f"  [429] waiting {wait}s"); time.sleep(wait)
            elif resp.status_code == 403:
                print(f"  [403 Forbidden] skipping"); return None
            elif resp.status_code in (500,502,503,504):
                time.sleep(2**attempt)
            else:
                print(f"  [HTTP {resp.status_code}] skipping"); return None
        except requests.exceptions.Timeout: time.sleep(2**attempt)
        except requests.exceptions.ConnectionError: time.sleep(2**attempt)
        except Exception as e: print(f"  [Error] {e}"); return None
    return None

def _normalize(title): return re.sub(r'[^a-z0-9 ]', '', title.lower().strip())

def _is_dup(title, seen):
    norm = _normalize(title)
    if norm in seen: return True
    words = set(norm.split())
    for s in seen:
        sw = set(s.split())
        if words and sw and len(words & sw)/max(len(words),len(sw)) > 0.8: return True
    return False

_last_ss = 0.0

def _fetch_ss(query, limit, offset):
    global _last_ss
    gap = time.time() - _last_ss
    if gap < 3.0: time.sleep(3.0 - gap)
    print(f"[Semantic Scholar] '{query}'...")
    resp = _safe_get("https://api.semanticscholar.org/graph/v1/paper/search",
        params={"query":query,"limit":min(limit,10),"offset":offset,
                "fields":"title,authors,abstract,year,citationCount,openAccessPdf,externalIds"}, max_retries=2)
    _last_ss = time.time()
    if resp is None: return []
    try:
        papers = []
        for p in resp.json().get("data", []):
            pdf = p.get("openAccessPdf",{}).get("url") if p.get("openAccessPdf") else None
            ext = p.get("externalIds") or {}
            pub = f"https://doi.org/{ext['DOI']}" if ext.get("DOI") else (f"https://arxiv.org/abs/{ext['ArXiv']}" if ext.get("ArXiv") else None)
            if not pdf and ext.get("ArXiv"): pdf = f"https://arxiv.org/pdf/{ext['ArXiv']}"
            aus = p.get("authors") or []
            authors = ", ".join([a.get("name","") for a in aus[:5]]) + (" et al." if len(aus)>5 else "")
            abstract = (p.get("abstract") or "No abstract.")[:600]
            papers.append({"title":p.get("title","Untitled"),"authors":authors or "Unknown","abstract":abstract,
                "year":p.get("year") or 0,"citations":p.get("citationCount") or 0,"views":0,
                "pdf_link":pdf,"publisher_link":pub,"source":"Semantic Scholar"})
        print(f"  -> {len(papers)} results"); return papers
    except Exception as e: print(f"  [SS error] {e}"); return []

def _rebuild_abstract(inv):
    if not inv: return "No abstract available."
    try:
        pm = {}
        for w,ps in inv.items():
            for p in ps: pm[p] = w
        txt = " ".join(pm[i] for i in sorted(pm))
        return txt[:600] + ("..." if len(txt)>600 else "")
    except: return "No abstract available."

def _fetch_openalex(query, limit, offset):
    print(f"[OpenAlex] '{query}'...")
    resp = _safe_get("https://api.openalex.org/works",
        params={"search":query,"per-page":min(limit,25),"page":(offset//limit)+1,
                "select":"id,title,authorships,abstract_inverted_index,publication_year,cited_by_count,open_access,doi,primary_location",
                "mailto":"research@researchapp.com"}, max_retries=3)
    if resp is None: return []
    try:
        papers = []
        for w in resp.json().get("results", []):
            aus = w.get("authorships") or []
            names = [a.get("author",{}).get("display_name","") for a in aus[:5] if a.get("author")]
            authors = ", ".join(names) + (" et al." if len(aus)>5 else "")
            doi = w.get("doi")
            oa = w.get("open_access") or {}
            pdf = oa.get("oa_url") or (w.get("primary_location") or {}).get("pdf_url")
            papers.append({"title":w.get("title","Untitled"),"authors":authors or "Unknown",
                "abstract":_rebuild_abstract(w.get("abstract_inverted_index")),
                "year":w.get("publication_year") or 0,"citations":w.get("cited_by_count") or 0,"views":0,
                "pdf_link":pdf,"publisher_link":doi,"source":"OpenAlex"})
        print(f"  -> {len(papers)} results"); return papers
    except Exception as e: print(f"  [OpenAlex error] {e}"); return []

def _fetch_crossref(query, limit, offset):
    print(f"[CrossRef] '{query}'...")
    resp = _safe_get("https://api.crossref.org/works",
        params={"query":query,"rows":min(limit,20),"offset":offset,
                "select":"title,author,abstract,published,is-referenced-by-count,DOI,link,URL",
                "mailto":"research@researchapp.com"}, max_retries=3)
    if resp is None: return []
    try:
        papers = []
        for item in resp.json().get("message",{}).get("items",[]):
            titles = item.get("title") or []
            title = titles[0] if titles else "Untitled"
            aus = item.get("author") or []
            names = [f"{a.get('given','')} {a.get('family','')}".strip() for a in aus[:5]]
            authors = ", ".join(names) + (" et al." if len(aus)>5 else "")
            abstract = re.sub(r"<[^>]+>","",item.get("abstract") or "").strip() or "No abstract available."
            abstract = abstract[:600] + ("..." if len(abstract)>600 else "")
            dp = (item.get("published") or {}).get("date-parts",[[]])
            year = dp[0][0] if dp and dp[0] else 0
            doi = item.get("DOI")
            pub = f"https://doi.org/{doi}" if doi else item.get("URL")
            pdf = next((l.get("URL") for l in (item.get("link") or []) if l.get("content-type")=="application/pdf"), None)
            papers.append({"title":title,"authors":authors or "Unknown","abstract":abstract,
                "year":year,"citations":item.get("is-referenced-by-count") or 0,"views":0,
                "pdf_link":pdf,"publisher_link":pub,"source":"CrossRef"})
        print(f"  -> {len(papers)} results"); return papers
    except Exception as e: print(f"  [CrossRef error] {e}"); return []

def _fetch_arxiv(query, limit, offset):
    print(f"[arXiv] '{query}'...")
    resp = _safe_get("http://export.arxiv.org/api/query",
        params={"search_query":f"all:{query}","start":offset,"max_results":min(limit+3,25),
                "sortBy":"relevance","sortOrder":"descending"}, timeout=20, max_retries=3)
    if resp is None: return []
    try:
        ns = {"atom":"http://www.w3.org/2005/Atom"}
        root = ET.fromstring(resp.content)
        papers = []
        for entry in root.findall("atom:entry", ns):
            try:
                te = entry.find("atom:title",ns)
                title = te.text.strip().replace("\n"," ") if te is not None else "Untitled"
                aels = entry.findall("atom:author",ns)
                names = [a.find("atom:name",ns).text for a in aels[:5] if a.find("atom:name",ns) is not None]
                authors = ", ".join(names) + (" et al." if len(aels)>5 else "")
                se = entry.find("atom:summary",ns)
                abstract = (se.text.strip().replace("\n"," ") if se is not None else "No abstract.")[:600]
                pe = entry.find("atom:published",ns)
                year = int(pe.text[:4]) if pe is not None else 0
                pdf = pub = None
                for lnk in entry.findall("atom:link",ns):
                    if lnk.get("title")=="pdf": pdf = lnk.get("href")
                    elif lnk.get("rel")=="alternate": pub = lnk.get("href")
                ide = entry.find("atom:id",ns)
                if ide:
                    abs_url = ide.text.strip()
                    if not pub: pub = abs_url
                    if not pdf: pdf = f"https://arxiv.org/pdf/{abs_url.split('/abs/')[-1]}"
                papers.append({"title":title,"authors":authors or "Unknown","abstract":abstract,
                    "year":year,"citations":0,"views":0,"pdf_link":pdf,"publisher_link":pub,"source":"arXiv"})
            except: continue
        print(f"  -> {len(papers)} results"); return papers
    except Exception as e: print(f"  [arXiv error] {e}"); return []


class PaperSearchService:
    def search_papers(self, query: str, limit: int = 10, offset: int = 0) -> List[Dict]:
        cached = _cache_get(query, limit, offset)
        if cached is not None: return cached

        papers, seen = [], set()

        def add(new_papers):
            for p in new_papers:
                if not p.get("title"): continue
                if _is_dup(p["title"], seen): continue
                seen.add(_normalize(p["title"]))
                papers.append(p)
                if len(papers) >= limit: break

        sources = [
            ("Semantic Scholar", lambda: _fetch_ss(query, limit, offset)),
            ("OpenAlex",         lambda: _fetch_openalex(query, limit, offset)),
            ("CrossRef",         lambda: _fetch_crossref(query, limit, offset)),
            ("arXiv",            lambda: _fetch_arxiv(query, limit, offset)),
        ]

        for name, fn in sources:
            if len(papers) >= limit: break
            try:
                results = fn()
                if results:
                    add(results)
                    print(f"[Total after {name}] {len(papers)}/{limit}")
            except Exception as e:
                print(f"[{name} FAILED] {e} -- trying next source")

        _cache_set(query, limit, offset, papers)

        if not papers:
            print(f"[WARNING] No results for '{query}' from any source!")

        return papers[:limit]

    def clear_cache(self):
        if not os.path.exists(CACHE_DIR): return
        count = sum(1 for f in os.listdir(CACHE_DIR) if f.endswith(".json") and not os.remove(os.path.join(CACHE_DIR,f)))
        print(f"[Cache] Cleared {count} entries")

    def clear_expired_cache(self):
        if not os.path.exists(CACHE_DIR): return
        count = 0
        for f in os.listdir(CACHE_DIR):
            if not f.endswith(".json"): continue
            path = os.path.join(CACHE_DIR, f)
            try:
                with open(path) as fp: data = json.load(fp)
                if datetime.now() - datetime.fromisoformat(data["cached_at"]) > timedelta(hours=CACHE_EXPIRY_HOURS):
                    os.remove(path); count += 1
            except: os.remove(path); count += 1
        print(f"[Cache] Removed {count} expired entries")