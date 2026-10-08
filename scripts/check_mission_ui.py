"""Optional real-browser review. Run against a locally started Streamlit server.

Developer-only prerequisite: python -m pip install playwright; uses installed Edge.
Captures actual E1/E7 screenshots and checks both jury display sizes, every tab,
the complete replay, reset and the presence of the original orbital schematic.
"""

from __future__ import annotations

import argparse
import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def require(condition, detail):
    """Keep browser validation enabled even under python -O."""
    if not condition:
        raise RuntimeError(f"Browser verification failed: {detail}")


def main():
    from playwright.sync_api import expect, sync_playwright

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8503")
    parser.add_argument("--output", type=Path, default=Path(".audit/mission-browser"))
    parser.add_argument('--profile', choices=['original', 'phase_a', 'phase_a2'], default='original')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {"profile": args.profile, "screens": [], "stages": [], "tabs": [], "browser_errors": []}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        page = browser.new_page(
            viewport={"width": 1920, "height": 1080}, reduced_motion="reduce"
        )
        page.on("pageerror", lambda error: report["browser_errors"].append(str(error)))
        page.set_default_timeout(120000)
        page.goto(args.url)
        page.locator(".mission-console").wait_for()
        page.wait_for_function(
            "document.querySelector('.spacecraft-scene')?.naturalWidth > 0"
        )

        def settle():
            # Allow the widget event to reach Streamlit before checking completion.
            # Otherwise a hidden status widget from the previous render can race
            # the next tab click and leave the test inspecting stale content.
            page.wait_for_timeout(300)
            page.locator('[data-testid="stStatusWidget"]').wait_for(state="hidden")

        if args.profile != 'original':
            from tekclipse.pipeline.profiles import PROFILE_LABELS
            page.locator('[data-testid="stExpandSidebarButton"]').click()
            page.get_by_role('combobox').nth(1).click()
            page.get_by_role('option', name=PROFILE_LABELS[args.profile], exact=True).click()
            page.get_by_text(f'Active: {PROFILE_LABELS[args.profile]}', exact=True).wait_for()
            settle()
            page.locator('[data-testid="stSidebarCollapseButton"]').click()

        def capture(name, width, height):
            page.set_viewport_size({"width": width, "height": height})
            page.wait_for_timeout(350)
            # Resizing can scroll a focused replay slider back into view. Blur it,
            # then reset the actual scroll container as well as the window.
            page.evaluate(
                """() => {document.activeElement?.blur(); window.scrollTo(0,0);
                document.querySelectorAll('*').forEach(e=>{if(e.scrollTop)e.scrollTop=0})}"""
            )
            page.wait_for_timeout(100)
            overflow = page.evaluate(
                """() => ({document:document.documentElement.scrollWidth>innerWidth,
                console:document.querySelector('.mission-console').scrollWidth>document.querySelector('.mission-console').clientWidth+1})"""
            )
            require(not any(overflow.values()), overflow)
            path = args.output / f"{name}-{width}.png"
            page.screenshot(path=str(path))
            page.locator(".mission-console").screenshot(
                path=str(args.output / f"{name}-console-{width}.png")
            )
            report["screens"].append(
                {
                    "file": str(path),
                    "width": width,
                    "height": height,
                    "overflow": overflow,
                }
            )

        settle()
        initial = "".join(page.locator(".trust-ring strong").inner_text().split())
        for width, height in [(1920, 1080), (1366, 768)]:
            capture("e1-nominal", width, height)
        page.set_viewport_size({"width": 1920, "height": 1080})
        started = time.perf_counter()
        page.get_by_role("button", name="Launch E7 attack", exact=True).click()
        page.get_by_text("REPLAY +000s", exact=False).wait_for()
        settle()
        report["e7_launch_seconds"] = time.perf_counter() - started
        for second in [20, 45, 86, 100, 120, 160, 180]:
            started = time.perf_counter()
            page.get_by_role("button", name="Next attack stage", exact=True).click()
            page.get_by_text(f"REPLAY +{second:03d}s", exact=False).wait_for()
            settle()
            report["stages"].append(
                dict(
                    second=second,
                    trust=page.locator(".trust-ring strong").inner_text(),
                    seconds=time.perf_counter() - started,
                    chain=page.locator(".attack-node b").all_text_contents(),
                )
            )
            if second == 160:
                require(
                    page.locator(".mission-console").get_attribute("data-security")
                    == "CRITICAL",
                    "E7 must reach CRITICAL",
                )
                require(
                    page.locator(".impact-preview").count() > 0,
                    "Missing mission impact",
                )
                require(
                    page.locator(".response-preview").count() > 0, "Missing response"
                )
                for width, height in [(1920, 1080), (1366, 768)]:
                    capture("e7-critical", width, height)
                page.set_viewport_size({"width": 1920, "height": 1080})
        # Every existing page still renders in the real browser.
        names = page.get_by_role("tab").all_text_contents()
        require(len(names) == 8, names)
        for name in names:
            page.get_by_role("tab", name=name, exact=True).click()
            expect(page.get_by_role('tab', name=name, exact=True)).to_have_attribute('aria-selected', 'true')
            settle()
            require(page.locator('[data-testid="stException"]').count() == 0, name)
            report["tabs"].append(name)
        page.get_by_role("tab", name="OVERVIEW", exact=True).click()
        settle()
        expect(page.get_by_role('button', name='Reset demo', exact=True)).to_be_visible()
        require(page.locator("iframe").count() >= 1, "Original orbit iframe missing")
        page.get_by_role("button", name="Reset demo", exact=True).click()
        # A hidden status widget can precede the next Streamlit rerender. Wait
        # for the requested state, then retain every original reset assertion.
        page.wait_for_function(
            "value => document.querySelector('.trust-ring strong')?.textContent.replace(/\\s/g, '') === value",
            arg=initial,
        )
        settle()
        require(
            "".join(page.locator(".trust-ring strong").inner_text().split()) == initial,
            "Trust did not reset",
        )
        require(page.locator(".attack-node").count() == 0, "Stale attack chain")
        require(page.locator(".impact-preview").count() == 0, "Stale impact")
        require(page.locator(".response-preview").count() == 0, "Stale response")
        page.get_by_role("button", name="Start nominal E1", exact=True).click()
        expect(page.locator(".mission-console")).to_have_attribute("data-security", "NORMAL", timeout=120000)
        settle()
        require(
            page.locator(".mission-console").get_attribute("data-security") == "NORMAL",
            "E1 not nominal",
        )
        report["reset"] = "E1 restored; no stale E7 chain, impact or recommendations"
        require(not report["browser_errors"], report["browser_errors"])
        browser.close()
    (args.output / "report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=True))


if __name__ == "__main__":
    main()
