"""Record the MedTimeline demo — upload 2 dated reports -> timeline -> Q&A.

Prereq: server on :7864, fresh state.
Produces: demo/video/*.webm + demo/marks.json
"""
import json
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent.parent / "demo"
OUT.mkdir(exist_ok=True)
VID = OUT / "video"
VID.mkdir(exist_ok=True)
APP = "http://127.0.0.1:7864"
marks: list[dict] = []
t0 = time.time()


def mark(name: str) -> None:
    marks.append({"name": name, "t": round(time.time() - t0, 2)})
    print(f"MARK {name} @ {marks[-1]['t']}s", flush=True)


def slow(page, ms=600):
    page.wait_for_timeout(ms)


with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        record_video_dir=str(VID),
        record_video_size={"width": 1280, "height": 800},
    )
    page = ctx.new_page()
    page.on("dialog", lambda d: d.accept())

    page.goto(APP, timeout=60000)
    slow(page, 3500)
    mark("start")

    # upload BOTH reports
    page.set_input_files("#file", [
        str(OUT.parent / "data/sample_course/report_2026-03.md"),
        str(OUT.parent / "data/sample_course/report_2026-09.md"),
    ])
    slow(page, 8000)
    mark("uploaded")

    # timeline (the star!)
    page.click("nav button[data-t='timeline']")
    slow(page, 1500)
    page.click("#btnTimeline")
    slow(page, 10000)
    mark("timeline_built")
    page.evaluate("window.scrollTo(0, 300)")
    slow(page, 5000)
    page.evaluate("window.scrollTo(0, 700)")
    slow(page, 5000)
    # listen to the questions
    try:
        page.click("#btnQAudio", timeout=6000)
        mark("questions_audio")
        slow(page, 12000)
    except Exception:
        pass
    page.evaluate("window.scrollTo(0, 1100)")
    slow(page, 4000)

    # grounded Q&A
    page.click("nav button[data-t='tutor']")
    slow(page, 2000)
    page.fill("#q", "How has the ferritin changed between the two reports?")
    slow(page, 1200)
    page.click("#btnAsk")
    slow(page, 26000)
    mark("answer_played")
    try:
        page.locator("#chat .cite a").first.click(timeout=5000)
        slow(page, 4500)
    except Exception:
        pass

    # off-document refusal
    page.fill("#q", "What treatment should we start for this?")
    slow(page, 1200)
    page.click("#btnAsk")
    slow(page, 18000)
    mark("refused")

    # back to timeline for the closing view
    page.click("nav button[data-t='timeline']")
    slow(page, 3000)
    page.evaluate("window.scrollTo(0, 200)")
    slow(page, 4000)
    mark("end")

    video = page.video
    ctx.close()
    path = video.path()
    print("VIDEO:", path)
    (OUT / "marks.json").write_text(json.dumps(marks, indent=1))
    print("marks saved")
