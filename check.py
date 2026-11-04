import os, sys, re, requests

URL = "https://www.cos.com/ko-kr/women/leather-edit/product.trullo-oversized-flap-bag---leather-black.1361103001.html"
TOPIC = os.environ["NTFY_TOPIC"]
STATE = "state.txt"

IN_MARKERS = ["schema.org/instock", "장바구니에 담기", "장바구니 담기", "add to bag", "add-to-bag", "바로 구매"]
OUT_MARKERS = ["schema.org/outofstock", "schema.org/soldout", "outofstock", "품절", "재입고 알림", "coming soon", "notify me"]

def notify(title, msg):
    requests.post(f"https://ntfy.sh/{TOPIC}", data=msg.encode("utf-8"),
                  headers={"Title": title.encode("utf-8"), "Click": URL, "Priority": "high"}, timeout=20)

r = requests.get(URL, timeout=30, headers={
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Mobile Safari/604.1",
    "Accept-Language": "ko-KR,ko;q=0.9"})
html = r.text
low = html.lower()
ins = [m for m in IN_MARKERS if m.lower() in low]
outs = [m for m in OUT_MARKERS if m.lower() in low]
print("HTTP", r.status_code, "len", len(html), "in:", ins, "out:", outs)

for m in list(re.finditer(r"(?i)(stock|availab|sold.?out|sellable|inventory|buyable)", html))[:12]:
    s = max(0, m.start() - 80)
    e = min(len(html), m.end() + 80)
    print("##", html[s:e].replace("\n", " "))

if r.status_code != 200:
    sys.exit(0)

status = "in" if ins and not outs else "out"
prev = open(STATE).read().strip() if os.path.exists(STATE) else ""
if status == "in" and prev != "in":
    notify("COS 입고 확인", "트룰로 오버사이즈 플랩 백 블랙이 구매 가능해 보여요. 눌러서 확인하세요.")
open(STATE, "w").write(status)
