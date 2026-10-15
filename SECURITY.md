# Security policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch.

## Reporting a vulnerability

Please **do not open a public issue** for security problems. Use GitHub's private reporting
(**Security > Report a vulnerability** on this repository) and include steps to reproduce, the affected version
and the impact. You will get an acknowledgement within a few days.

## Hardening notes for deployers

* Set `FRAUD_SHIELD_ENV=production`: it disables the simulator and demo data.
* Set `FRAUD_SHIELD_API_KEY` so that write endpoints require an `X-API-Key` header, and terminate TLS in front of the service.
* Set `FRAUD_SHIELD_RATE_LIMIT`, and restrict `FRAUD_SHIELD_CORS` to your console's origin.
* The analyst name shown in the audit log is self-reported. Put the service behind your identity provider if you
  need authenticated analyst identities.
* The service stores transaction features and decisions in SQLite; protect and back up that file accordingly.
