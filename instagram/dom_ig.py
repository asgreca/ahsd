#!/usr/bin/env python3
"""Controlador do Instagram no Safari via AppleScript / DOM.
Usa uma aba dedicada identificada por window.name = 'mensa_ig1'.
Totalmente isolado das abas do projeto BET.
"""
import json
import pathlib
import subprocess
import time

BASE = pathlib.Path(__file__).parent
DADOS = BASE / "dados"
MIDIA = BASE / "midia"
DADOS.mkdir(exist_ok=True)
MIDIA.mkdir(exist_ok=True)

ABA = "mensa_ig1"

AS_NAV = '''on run argv
set nome to item 2 of argv
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t as text) contains "instagram.com" then
        try
          if (do JavaScript "window.name" in t) = nome then
            set URL of t to item 1 of argv
            return "ok"
          end if
        end try
      end if
    end repeat
  end repeat
  tell window 1 to set nt to make new tab with properties {URL:item 1 of argv}
  delay 5
  do JavaScript "window.name='" & nome & "'" in nt
  return "nova"
end tell
end run'''

AS_JS = '''on run argv
set nome to item 2 of argv
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t as text) contains "instagram.com" then
        try
          if (do JavaScript "window.name" in t) = nome then return do JavaScript (item 1 of argv) in t
        on error e
          return "JSERR:" & e
        end try
      end if
    end repeat
  end repeat
end tell
return "SEM_ABA"
end run'''


AS_REC = '''on run argv
set nome to item 2 of argv
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      try
        if (do JavaScript "window.name" in t) = nome then close t
      end try
    end repeat
  end repeat
  tell window 1 to set nt to make new tab with properties {URL:item 1 of argv}
  delay 5
  do JavaScript "window.name='" & nome & "'" in nt
  return "recreated"
end tell
end run'''


def osa(script, arg, timeout=60):
    r = subprocess.run(["osascript", "-", arg, ABA], input=script, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "").strip()


def recrear_aba(url="https://www.instagram.com/"):
    return subprocess.run(["osascript", "-", url, ABA], input=AS_REC, capture_output=True, text=True, timeout=60).stdout.strip()


def nav(url):
    res = osa(AS_NAV, url)
    if res == "SEM_ABA":
        recrear_aba(url)
        return "ok"
    return res


def js(code):
    r = osa(AS_JS, code)
    if r == "SEM_ABA":
        recrear_aba()
        time.sleep(3)
        r = osa(AS_JS, code)
    return r


def espera(code_js, condicao_fn, timeout=25, step=1.5):
    """Executa code_js repetidamente até condicao_fn(dado_parseado) ser True ou timeout."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        res = js(code_js)
        if res and not res.startswith("SEM_ABA") and not res.startswith("JSERR:"):
            try:
                d = json.loads(res) if res.startswith("{") or res.startswith("[") else res
                if condicao_fn(d):
                    return d
            except Exception:
                pass
        time.sleep(step)
    return None


if __name__ == "__main__":
    print(f"Testando navegacao na aba {ABA}...")
    r = nav("https://www.instagram.com/mensabrasil/")
    print(f"Status nav: {r}")
    time.sleep(3)
    title = js("document.title")
    print(f"Titulo da pagina: {title}")
