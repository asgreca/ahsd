import subprocess
import json

js_extract = """
(() => {
    const results = [];
    // DuckDuckGo news results are articles or divs
    const articles = document.querySelectorAll("article, [data-testid='result'], .result");
    for (let art of articles) {
        const a = art.querySelector("a[data-testid='result-title-a']") || art.querySelector("h2 a") || art.querySelector("a");
        if (!a || !a.href || a.href.includes("duckduckgo.com")) continue;
        const title = a.innerText.trim();
        const snippetEl = art.querySelector("[data-result='snippet'], .result__snippet, div:nth-child(2)");
        const snippet = snippetEl ? snippetEl.innerText.trim() : "";
        const dateEl = art.querySelector(".result__date, time, span[class*='date']");
        const date = dateEl ? dateEl.innerText.trim() : "";
        results.push({
            url: a.href,
            title: title,
            snippet: snippet,
            date: date
        });
    }
    // If no articles found, fallback to all external content links
    if (results.length === 0) {
        const links = document.querySelectorAll("a");
        for (let a of links) {
            if (a.href && !a.href.includes("duckduckgo.com") && a.innerText.trim().length > 20) {
                results.push({
                    url: a.href,
                    title: a.innerText.trim(),
                    snippet: "",
                    date: ""
                });
            }
        }
    }
    return JSON.stringify(results);
})()
"""

applescript = f"""
tell application "Safari"
    tell current tab of window 1
        return (do JavaScript "{js_extract.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34)).replace(chr(10), ' ')}")
    end tell
end tell
"""

proc = subprocess.run(["osascript"], input=applescript, capture_output=True, text=True)
if proc.returncode != 0:
    print("Error:", proc.stderr)
else:
    raw = proc.stdout.strip()
    try:
        items = json.loads(raw)
        print(f"Sucesso! Encontrados {len(items)} artigos:")
        for idx, it in enumerate(items[:10], 1):
            print(f"[{idx}] {it.get('title')}\n    URL: {it.get('url')}\n    Data: {it.get('date')}")
    except Exception as e:
        print("Json parse error:", e, raw[:300])
