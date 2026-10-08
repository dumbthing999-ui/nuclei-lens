# Security policy

NucleiLens 0.1.x is an experimental microscopy review tool. It has no clinical or institutional compliance certification.

## Reporting

Use GitHub private vulnerability reporting if enabled on the repository. If unavailable, open an issue requesting a private contact without including exploit details or sensitive images. Response times are best effort; no response SLA is promised.

## Browser deployment

Image analysis runs in a dedicated worker using a self-hosted Pyodide runtime. The application does not send opened image bytes to an analysis server, persist them in a database, or expose model/tool credentials. Scientific assets and bundled public examples are downloaded over HTTPS. The hosting provider still receives ordinary HTTP metadata such as IP address and asset paths. This is a data-handling design, not a regulatory guarantee.

Inputs are bounded to 10 MB, a single frame, 1,048,576 pixels, and 2,048 pixels per side. TIFF headers are checked before raster decoding; PNG/JPEG dimensions are checked before browser decoding. TIFF preserves numeric precision, while browser PNG/JPEG decoding uses 8-bit grayscale. A 90-second watchdog can terminate the worker; a user can cancel analysis.

## Optional local companion

Bind FastAPI only to `127.0.0.1`. Allowed hostnames and same-origin checks reduce browser-origin abuse; inputs and concurrent work are bounded. The companion has no authentication, TLS, process isolation, or hard CPU-job timeout. Do not expose it to a public network or reverse proxy. It is unnecessary for the hosted application.

## Verification and limits

See [security review](docs/security-review.md), the reproducible audit commands in the README, and actual audit reports in `evaluation/checks/`. A clean dependency audit does not prove absence of vulnerabilities. The project has not received an independent penetration test or parser fuzz campaign. Do not open patient-identifiable images in this research prototype.
