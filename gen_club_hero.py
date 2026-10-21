"""
Generate the club hero image with Matan's REAL face via Kie.ai image-to-image.
Clean cool-blue single-device product hero (Market Lens vibe), landscape, NO text.
Run AFTER Kie credits are topped up:  python3 gen_club_hero.py
Key read from ~/.secrets/kie_api_key. Never in code/args.
"""
import json, os, subprocess, sys, time, urllib.error, urllib.request

UPLOAD_URL = "https://kieai.redpandaai.co/api/file-stream-upload"
GEN_URL = "https://api.kie.ai/api/v1/gpt4o-image/generate"
POLL_URL = "https://api.kie.ai/api/v1/gpt4o-image/record-info"
CREDIT_URL = "https://api.kie.ai/api/v1/chat/credit"
KEY_FILE = os.path.expanduser("~/.secrets/kie_api_key")
OUT = os.environ.get("KIE_OUT", "/Users/matanmashiah/test/landing-page/images/club-hero-v2.png")
SIZE = os.environ.get("KIE_SIZE", "3:2")

REFS = (os.environ["KIE_REFS"].split("|") if os.environ.get("KIE_REFS") else [
    # default: the studio suit + headset-mic photo (Matan looks sharpest here)
    "/Users/matanmashiah/test/brand-assets/my-photos/Screenshot 2026-06-01 at 10.54.25.png",
])

PROMPT = (
    "Using the exact face and likeness of the man in the reference photos, create a "
    "premium, photorealistic LANDSCAPE brand hero image. The same man — confident, calm "
    "and composed, faint assured smile, smart-casual dark outfit — stands to one side of "
    "the frame. Beside and slightly behind him a single sleek modern laptop floats at an "
    "elegant angle; its screen shows a clean glowing blue candlestick trading chart "
    "trending upward (purely abstract, no text). Cohesive cool-blue cinematic palette: "
    "deep midnight-navy background (#101118), soft blue rim lighting, subtle volumetric "
    "glow and a faint dot grid. Calm, institutional, high-end fintech aesthetic — "
    "restrained and elegant, NOT flashy. Generous negative space, darker toward the edges "
    "for a clean composition. Keep his face accurate to the references. "
    "Absolutely NO text, NO letters, NO Hebrew, NO numbers, NO money, NO cash, NO coins, "
    "NO logos, NO neon, NO rockets. Ultra detailed, 8k advertising photography."
)


def get_key():
    key = os.environ.get("KIE_API_KEY", "").strip()
    if not key and os.path.exists(KEY_FILE):
        key = open(KEY_FILE).read().strip()
    if not key:
        sys.exit("No API key (set ~/.secrets/kie_api_key).")
    return key


def check_credit(key):
    try:
        req = urllib.request.Request(CREDIT_URL, headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            bal = (json.loads(r.read().decode()).get("data"))
        print(f"Kie credit balance: {bal}")
        if isinstance(bal, (int, float)) and bal <= 0:
            sys.exit("STOP: Kie credits are not positive yet. Top up, then re-run.")
    except urllib.error.HTTPError as e:
        print(f"(credit check skipped: HTTP {e.code})")


def upload(path, key):
    r = subprocess.run(
        ["curl", "-s", "-X", "POST", UPLOAD_URL,
         "-H", f"Authorization: Bearer {key}",
         "-F", f"file=@{path}", "-F", "uploadPath=images/user-uploads"],
        capture_output=True, text=True, timeout=120)
    try:
        j = json.loads(r.stdout)
    except Exception:
        sys.exit(f"Upload parse error for {path}: {r.stdout[:200]} {r.stderr[:200]}")
    url = (j.get("data") or {}).get("downloadUrl")
    if not url:
        sys.exit(f"Upload failed for {path}: {json.dumps(j)[:300]}")
    print(f"  uploaded {os.path.basename(path)}")
    return url


def post_json(url, payload, key):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def get_json(url, key):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def main():
    key = get_key()
    check_credit(key)
    text_only = os.environ.get("KIE_REFS", "").lower() == "none"
    files = []
    if not text_only:
        print("Uploading reference photos...")
        files = [upload(p, key) for p in REFS if os.path.exists(p)]
        if not files:
            sys.exit("No reference photos found.")

    prompt = os.environ.get("KIE_PROMPT", PROMPT)
    print("Submitting generation...")
    payload = {"prompt": prompt, "size": SIZE}
    if files:
        payload["filesUrl"] = files
    resp = post_json(GEN_URL, payload, key)
    if resp.get("code") != 200:
        sys.exit(f"Generate rejected: {json.dumps(resp)[:300]}")
    tid = resp["data"]["taskId"]
    print(f"Task {tid}. Rendering...")

    deadline = time.time() + 360
    while time.time() < deadline:
        time.sleep(6)
        try:
            data = (get_json(f"{POLL_URL}?taskId={tid}", key).get("data") or {})
        except urllib.error.HTTPError as e:
            print(f"  poll {e.code}"); continue
        flag, status = data.get("successFlag"), data.get("status")
        print(f"  status={status} flag={flag}")
        if flag in (1, "1") or status == "SUCCESS":
            urls = (data.get("response") or {}).get("resultUrls") or []
            if not urls:
                sys.exit("Done but no URL.")
            subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", urls[0], "-o", OUT],
                           timeout=120, check=True)
            print(f"Saved -> {OUT}")
            return
        if flag in (2, 3, "2", "3") or status in ("FAILED", "GENERATE_FAILED"):
            sys.exit(f"Generation failed: {json.dumps(data)[:300]}")
    sys.exit("Timed out.")


if __name__ == "__main__":
    main()
