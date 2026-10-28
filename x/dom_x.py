#!/usr/bin/env python3
"""Controlador do X (Twitter) no Safari via AppleScript / DOM.
Usa uma aba dedicada em janela própria identificada por window.name = 'mensa_x1'.
Totalmente isolado das abas de outros projetos.
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

ABA = "mensa_x_exclusivo"

AS_NAV = '''on run argv
set url_alvo to item 1 of argv
set nome to item 2 of argv
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      try
        if (do JavaScript "window.name" in t) = nome then
          set current tab of w to t
          set URL of t to url_alvo
          return "ok"
        end if
      end try
    end repeat
  end repeat
end tell
return "SEM_ABA"
end run'''

AS_JS = '''on run argv
set code to item 1 of argv
set nome to item 2 of argv
tell application "Safari"
  repeat with w in windows
    repeat with t in tabs of w
      try
        if (do JavaScript "window.name" in t) = nome then
          set current tab of w to t
          return do JavaScript code in t
        end if
      end try
    end repeat
  end repeat
end tell
return "SEM_ABA"
end run'''

AS_REC = '''on run argv
set url_alvo to item 1 of argv
set nome to item 2 of argv
tell application "Safari"
  make new document with properties {URL:url_alvo}
  delay 5
  set nw to front window
  set nt to current tab of nw
  do JavaScript "window.name = '" & nome & "'; document.title = 'Mensa_X_Janela';" in nt
  return "recreated"
end tell
end run'''

def osa(script, arg, timeout=60):
    r = subprocess.run(["osascript", "-", arg, ABA], input=script, capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "").strip()

def recrear_aba(url="https://x.com/home"):
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

def espera(segundos=3):
    time.sleep(segundos)
