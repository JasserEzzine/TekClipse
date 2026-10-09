"""Phase C browser checks: observed-only investigation, exports and responsive views."""
import argparse
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, expect


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8506')
    parser.add_argument('--output',type=Path,default=Path('.audit/phase-c-browser'))
    args = parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    expect.set_options(timeout=120000)
    report = dict(profiles=[],responsive=[],exports=[],errors=[])
    labels=['Original preview (default)','Phase A calibrated (experimental)','Phase A.2 hardened (experimental)']
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport=dict(width=1920,height=1080),reduced_motion='reduce')
        page.set_default_timeout(120000)
        page.on('pageerror',lambda error:report['errors'].append(str(error)))
        page.goto(args.url)
        page.locator('.observation-strip').wait_for()

        def settle():
            page.wait_for_timeout(300)
            page.locator('[data-testid="stStatusWidget"]').wait_for(state='hidden')

        for profile in labels:
            page.set_viewport_size(dict(width=1920,height=1080))
            page.locator('[data-testid="stExpandSidebarButton"]').click()
            page.locator('[data-testid="stSidebar"]').get_by_role('combobox',name='Detection profile').click()
            page.get_by_role('option',name=profile,exact=True).click()
            expect(page.locator('.profile-ribbon')).to_contain_text(profile)
            settle()
            page.locator('[data-testid="stSidebarCollapseButton"]').click()
            require(page.locator('.replay-investigation').count()==0,'Profile switch retained replay')
            require(page.locator('.subsystem-card').count()==5,'Missing subsystem cards')
            page.get_by_role('button',name='Launch E7 attack',exact=True).click()
            page.get_by_text('REPLAY +000s',exact=False).wait_for()
            settle()
            measured=[]
            for index,second in enumerate([20,45,86,100,120,160,180],1):
                start=time.perf_counter()
                page.get_by_role('button',name='Next attack stage',exact=True).click()
                page.get_by_text(f'REPLAY +{second:03d}s',exact=False).wait_for()
                settle()
                expect(page.locator('[data-stage-time]')).to_have_count(index+1)
                times=page.locator('[data-stage-time]').evaluate_all('(els)=>els.map(e=>e.dataset.stageTime)')
                require(len(times)==index+1,'Missing revealed stage')
                boundary=f'2026-01-01T12:{second//60:02d}:{second%60:02d}+00:00'
                require(all(t<=boundary for t in times),'Future stage exposed')
                require(page.locator('.stage-current').count()==1,'Current stage ambiguous')
                measured.append(dict(second=second,trust=page.get_by_role('meter').get_attribute('aria-valuenow'),seconds=time.perf_counter()-start))
            report['profiles'].append(dict(profile=profile,stages=measured))
            print(f'Checked {profile}: all seven replay advances',flush=True)
            if profile==labels[-1]:
                page.locator('.replay-investigation').screenshot(path=str(args.output/'e7-investigation.png'))
                page.locator('.subsystem-workspace').screenshot(path=str(args.output/'e7-subsystems.png'))
                page.get_by_text('Security analyst / investigate observed evidence',exact=True).click()
                page.locator('[data-testid="stRadio"]').get_by_text('Rule-based detections',exact=True).click()
                expect(page.get_by_role('radio',name='Rule-based detections',exact=True)).to_be_checked()
                settle()
                expect(page.locator('.security-render-complete')).to_have_attribute('data-family','Rule-based detections')
                expect(page.locator('.analyst-evidence')).to_contain_text('Rule-based detections')
                page.locator('.analyst-evidence').screenshot(path=str(args.output/'analyst-evidence.png'))
                with page.expect_download() as exported:
                    page.get_by_role('button',name='Export observed investigation / CSV',exact=True).click()
                target=args.output/'observed-investigation.csv'
                exported.value.save_as(target)
                import csv
                rows=list(csv.DictReader(target.open(encoding='utf-8')))
                require(bool(rows) and all(r['detector'] in {'R1','R2','R3'} for r in rows),'Export ignored family filter')
                require(all(r['observed_at']<=boundary for r in rows),'Export contains future evidence')
                report['exports'].append(dict(rows=len(rows),future_evidence=False,family_filter=True))
                for width,height in [(1920,1080),(1366,768),(768,1024),(390,844)]:
                    page.set_viewport_size(dict(width=width,height=height))
                    settle()
                    overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth')
                    require(not overflow,f'Horizontal overflow at {width}')
                    page.evaluate("document.querySelectorAll('*').forEach(e=>{if(e.scrollTop)e.scrollTop=0})")
                    page.screenshot(path=str(args.output/f'e7-{width}.png'))
                    report['responsive'].append(dict(width=width,height=height,horizontal_overflow=overflow))
            page.set_viewport_size(dict(width=1920,height=1080))
            page.get_by_role('button',name='Reset demo',exact=True).click()
            expect(page.locator('.profile-ribbon')).to_contain_text('E1')
            settle()
            require(page.locator('.stage-step').count()==0,'Reset retained investigation stages')
            require(page.locator('.attack-node').count()==0,'Reset retained attack evidence')
            require(page.locator('[data-testid="stException"]').count()==0,'Application exception')
        require(not report['errors'],report['errors'])
        browser.close()
    (args.output/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))


if __name__=='__main__':
    main()
