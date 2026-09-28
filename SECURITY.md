# Security and reliability

TekClipse is a public demonstration using synthetic satellite data. It is not a
flight system or a security boundary for a real spacecraft.

## Credentials and access

The application requires **no API keys, satellite credentials or external service
passwords**. Do not enter credentials into its dataset or source files.
Environment files, Streamlit secrets, private-key containers, local logs and
generated outputs are excluded from Git by default. An ignore rule does not
remove a previously committed secret or prevent a forced Git add.

The application has no built-in user authentication. Configure public or
restricted viewer access at the hosting platform. Anyone granted access can
inspect the simulated data, execute the supported scenarios and export alerts.
Shared caches must not be used for confidential/user-specific data without a
separate access-control and data-isolation design.

## Controls

- CORS and XSRF protections are enabled. Static-directory serving is disabled.
- Browser errors omit detailed tracebacks; operators retain server logs.
- There is no visitor file-upload widget, shell-command field, arbitrary URL
  fetcher or visitor-selected filesystem path.
- Dynamic alert ticker text is HTML-escaped. Dashboard JavaScript is local
  application code and only handles presentation.
- The nominal preview uses JSON, unique temporary files and atomic replacement.
  In-process read/write coordination prevents concurrent replacement collisions.
- A lock serializes uncached detector runs within each server process. Cached
  results remain available without retraining. Hosted ranges are limited to
  one/seven days; these limits reduce load but do not prevent denial of service.
- Preview fingerprints detect stale data/code; they are **not cryptographic
  authentication** against a malicious filesystem writer. Server files are trusted.

## Audit scope

The September 2026 review checks the `tekclipse-cloud` application branch,
dependency advisories and reachable local Git history. Source analysis and secret
scanning complement manual review; none can prove the absence of all defects.
The security workflow repeats regression, source, dependency and tracked-file
secret checks on pushes and pull requests to the hosting branch.

Tools used: Bandit, detect-secrets, pip-audit, targeted credential-pattern scans,
pytest and Streamlit AppTest. Dependency audit requests disclose package names
and versions to the advisory service; they do not require application credentials.

The initial dependency audit identified advisories in transitive libraries;
patched versions are pinned in `requirements.txt`. Audit findings and versions
change over time, so dependency updates still require review and regression tests.
GitHub Actions uses pinned action commit IDs, read-only repository permissions and
checkout without persisted credentials. No repository secrets are required by CI.

## Limits and reporting

No authentication, availability guarantee, penetration-test certification or
flight-system certification is claimed. Cloud memory limits, network outages,
idle suspension and cold startup can affect availability. Multiple server
processes require external coordination before relying on the local locks.

The evaluator remains experimental: its event matching, train/test alignment
and overhead interpretation are not yet validated research methodology. Do not
turn its output into cybersecurity performance claims.

For a suspected exposure, do not paste credentials into a public issue. Revoke
the credential first and use a private maintainer/security reporting channel
where available. For non-sensitive defects, provide the failing operation,
software versions and a sanitized traceback.
