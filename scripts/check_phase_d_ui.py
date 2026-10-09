"""Real Edge verification of E2/E3/E7 response enforcement and portable exports."""
import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright, expect


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8509')
    parser.add_argument('--output',type=Path,default=Path('.audit/phase-d-browser'))
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    results=dict(demos=[],screens=[],errors=[])
    expect.set_options(timeout=120000)
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True)
        page=browser.new_page(viewport=dict(width=1920,height=1080),reduced_motion='reduce')
        page.set_default_timeout(120000)
        page.on('pageerror',lambda error:results['errors'].append(str(error)))
        page.goto(args.url); page.locator('.mission-console').wait_for()

        def settle():
            page.wait_for_timeout(350)
            page.locator('[data-testid="stStatusWidget"]').wait_for(state='hidden')
            require(page.locator('[data-testid="stException"]').count()==0,'Streamlit exception')

        def select(label,value):
            print('Select '+label+': '+value,flush=True)
            marker=page.locator('[role="tabpanel"]:visible .security-render-complete')
            previous=marker.get_attribute('data-token') if marker.count() else None
            current=page.get_by_role('combobox',name=label).get_attribute('aria-label') or ''
            page.get_by_role('combobox',name=label).click()
            page.get_by_role('option',name=value,exact=True).click(); settle()
            if previous and value not in current:
                expect(marker).not_to_have_attribute('data-token',previous)

        def export(label,filename):
            with page.expect_download() as download:
                page.get_by_role('button',name=label,exact=True).click()
            path=args.output/filename
            download.value.save_as(path)
            return path

        def capture(filename,locator=None):
            settle()
            page.wait_for_function("!Array.from(document.querySelectorAll('[data-stale=\"true\"]')).some(e=>e.offsetParent!==null)")
            (locator or page).screenshot(path=str(args.output/filename))

        def open_defense():
            print('Opening defense workspace',flush=True)
            toggle=page.get_by_role('checkbox',name='Open cyber defense workspace',exact=True)
            if not toggle.is_checked():
                page.get_by_role('tabpanel',name='OVERVIEW',exact=True).get_by_text('Open cyber defense workspace',exact=True).click()
            expect(toggle).to_be_checked()
            page.locator('.defense-heading:visible').wait_for(); settle()

        def review(second):
            print('Review '+str(second),flush=True)
            field=page.get_by_role('spinbutton',name='Defense review / seconds after 12:00 UTC',exact=True)
            field.fill(str(second)); field.press('Enter'); settle()
            expect(field).to_have_value(str(second))

        def launch(scenario):
            print('Checking '+scenario,flush=True)
            page.get_by_role('tab',name='SCENARIOS E1–E7',exact=True).click(); settle()
            page.get_by_role('button',name='Run '+scenario,exact=True).click(); settle()
            expect(page.locator('.profile-ribbon')).to_contain_text(scenario)
            page.get_by_role('tab',name='OVERVIEW',exact=True).click(); settle()
            expect(page.get_by_role('checkbox',name='Open cyber defense workspace',exact=True)).not_to_be_checked()
            open_defense()

        page.locator('[data-testid="stExpandSidebarButton"]').click()
        select('Detection profile','Phase A.2 hardened (experimental)')
        page.locator('[data-testid="stSidebarCollapseButton"]').click()
        launch('E2'); review(0); select('Detector','R1')
        expect(page.locator('.defense-evidence:visible')).to_contain_text('UNKNOWN_1')
        select('Simulation policy / target','Reject unauthorized commands / command-channel')
        page.get_by_role('textbox',name='Operator reason',exact=True).fill('Jury demo: reject unauthorized command')
        page.get_by_role('textbox',name='Operator reason',exact=True).press('Enter'); settle()
        page.get_by_role('button',name='Apply simulated restriction',exact=True).click(); settle()
        expect(page.locator('.defense-response:visible')).to_contain_text('ALLOW → DENY')
        capture('e2-response.png',page.locator('.defense-response:visible'))
        audit=json.loads(export('Export response audit / JSON','e2-actions.json').read_text())
        require(audit[-1]['probe_after']['outcome']=='DENY','E2 rejection was not functional')
        page.get_by_role('button',name='Restore normal access',exact=True).click(); settle()
        expect(page.locator('.defense-response:visible')).to_contain_text('DENY → ALLOW')
        results['demos'].append(dict(scenario='E2',rejection=True,reversal=True))
        launch('E3'); review(20); select('Detector','R2')
        select('Simulation policy / target','Quarantine command station / GS_PRIMARY')
        page.get_by_role('textbox',name='Operator reason',exact=True).fill('Jury demo: contain command-rate violation')
        page.get_by_role('textbox',name='Operator reason',exact=True).press('Enter'); settle()
        page.get_by_role('button',name='Apply simulated restriction',exact=True).click(); settle()
        expect(page.locator('.defense-response:visible')).to_contain_text('ALLOW → DENY')
        review(58)
        expect(page.get_by_text('Subsequent observed records evaluated:',exact=False)).to_contain_text('denied by simulation policy: 19')
        e3=json.loads(export('Download incident report / JSON','e3-report.json').read_text())
        require(sum(r['outcome']=='DENY' for r in e3['post_response_evaluation'])==19,'E3 later commands not denied')
        page.get_by_role('button',name='Restore normal access',exact=True).click(); settle()
        expect(page.locator('.defense-response:visible')).to_contain_text('DENY → ALLOW')
        results['demos'].append(dict(scenario='E3',later_commands_denied=19,reversal=True))
        page.get_by_role('button',name='Launch E7 attack',exact=True).click(); settle()
        page.get_by_text('REPLAY +000s',exact=False).wait_for()
        open_defense()
        for second in [20,45]:
            page.get_by_role('button',name='Next attack stage',exact=True).click()
            page.get_by_text(f'REPLAY +{second:03d}s',exact=False).wait_for(); settle()
        select('Detector','NET'); select('Source identifier','203.0.113.27')
        select('Simulation policy / target','Block network source / 203.0.113.27')
        early=json.loads(export('Export security log / JSON','e7-early-log.json').read_text())
        require(all(r['timestamp']<='2026-01-01T12:00:45+00:00' for r in early),'Future finding leaked')
        page.get_by_role('textbox',name='Operator reason',exact=True).fill('Jury demo: contain unfamiliar network peer')
        page.get_by_role('textbox',name='Operator reason',exact=True).press('Enter'); settle()
        page.get_by_role('button',name='Apply simulated restriction',exact=True).click(); settle()
        expect(page.locator('.defense-response:visible')).to_contain_text('ALLOW → DENY')
        for second in [86,100,120,160,180]:
            page.get_by_role('button',name='Next attack stage',exact=True).click()
            page.get_by_text(f'REPLAY +{second:03d}s',exact=False).wait_for(); settle()
        select('Report scope','INC-001')
        incident=json.loads(export('Download incident report / JSON','e7-incident.json').read_text())
        export('Download incident report / HTML','e7-incident.html')
        require(incident['incident_id']=='INC-001','Incident report scope wrong')
        require(incident['trust']['score']==9,'Original trust changed after response')
        require(sum(r['outcome']=='DENY' for r in incident['post_response_evaluation'])==115,'E7 denylist not enforced on later flows')
        require({m['technique_id'] for m in incident['sparta']}=={'EX-0013.01'},'Supported SPARTA mapping missing')
        capture('incident-investigation.png',page.locator('.defense-evidence:visible'))
        capture('incident-card.png',page.locator('.defense-incident:visible').first)
        capture('simulated-response.png',page.locator('.defense-response:visible'))
        page.locator('.defense-heading:visible').evaluate("e=>e.scrollIntoView({block:'start'})")
        capture('security-logs.png')
        for width,height in [(1920,1080),(1366,768),(768,1024),(390,844)]:
            page.set_viewport_size(dict(width=width,height=height)); settle()
            require(not page.evaluate('document.documentElement.scrollWidth>innerWidth'),f'Overflow at {width}')
            page.evaluate("document.activeElement?.blur();document.querySelectorAll('*').forEach(e=>{if(e.scrollTop)e.scrollTop=0})")
            capture(f'overview-{width}.png')
            results['screens'].append(dict(width=width,height=height,horizontal_overflow=False))
        results['demos'].append(dict(scenario='E7',stages=7,later_flows_denied=115,report=True,trust=9,no_future_evidence=True))
        page.set_viewport_size(dict(width=1920,height=1080))
        page.get_by_role('button',name='Reset demo',exact=True).click(); settle()
        expect(page.locator('.profile-ribbon')).to_contain_text('E1')
        require(page.locator('.defense-response:visible').count()==0,'Reset retained response state')
        require(not results['errors'],results['errors'])
        browser.close()
    (args.output/'report.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    main()
