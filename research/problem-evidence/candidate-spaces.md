# Candidate Problem Spaces: Evidence and Early Gates

**Research date:** 2026-10-07. These are discovery notes, not selected project claims.

## Accessibility data and pedestrian mobility

- **Need:** WHO estimates 1.3 billion people (16% of the global population) experience significant disability and reports transportation access as a major barrier. This establishes broad importance, not local project impact.
- **Available mechanism/data:** OpenStreetMap has tags for sidewalks, widths, surfaces, smoothness, wheelchair access, curb conditions, and tactile paving. The OSM Foundation describes attribution and possible share-alike duties; the main editing API is not meant for a read-only product. Public Overpass instances have rate/availability limits.
- **Existing approaches:** Wheelmap maps accessible places; AccessMap research has generated routes using sidewalks, curb ramps, terrain, and variable costs. A 2026 AGILE GIScience paper analyzes OSM suitability and wheelchair-specific routing in Graz.
- **Gate decision:** A basic wheelchair route finder is rejected as insufficiently differentiated. A narrower OSM data-quality/audit idea is still only a hypothesis; its novelty, local coverage, usefulness, and safe interaction with existing tagging work need evidence. Never interpret missing tags as an inaccessible feature or claim a route is safe.
- **Sources:** WHO disability fact sheet; OSM tagging and Foundation license/policy pages; 2026 AGILE GIScience paper (see [SOURCES.md](../SOURCES.md), references 16–20).

## Public transit access and equity

- **Available dataset:** Delhi OTD lists 3,464 stops, 543 routes, 16,562 trips, and 378,324 approximate stop-time records, last updated June 20, 2024.
- **Critical caveats:** The agency warns timetable stop-times are rough estimates derived from constant speed. Real-time data needs an authorized private key. Static download requires personal identity and a declared purpose; terms state the user must specify intended use, manner, time frame, and identity and the Department may refuse permission.
- **Gate decision:** Do not build a schedule/reliability predictor or download the feed without approved access. The current data age/quality also weakens a live-routing concept. No download form was submitted and no API key was requested.
- **Sources:** Delhi OTD static data, documentation, and terms; see [SOURCES.md](../SOURCES.md), references 11–13.

## Heat resilience

- **Need and official response:** IMD publishes district heat warnings and an impact-based bulletin service. Its official material reports improving day-one probability of detection for heatwave forecasts over 2016–2023; the cited numbers are IMD-reported service metrics, not independent or neighborhood-scale validation.
- **Available evidence:** IMD pages expose warnings and outlooks, but stable bulk historical data/API access was not established. Official municipal and government heat plans exist, so generic heat dashboards are not a novel response.
- **Gate decision:** Do not claim street-level risk or predictive improvement from district bulletins. A concept would need a distinct mechanism, open data rights, and a clearly scoped evaluation that does not imply clinical advice.
- **Sources:** IMD Heat Wave Guidance, Districtwise Warnings, official 2024-ish souvenir PDF, and 2019 report; see [SOURCES.md](../SOURCES.md), references 4–9.

## Research conclusions so far

1. Strong impact does not guarantee novelty; accessibility, flood risk, student support, water diagnostics, and emergency information already have relevant projects or mature tools.
2. A prospective idea must use a public dataset with clear terms and stable access, or a reproducible bounded experiment that does not pretend synthetic input proves real-world impact.
3. Prefer an underrepresented user/problem pair with a visible algorithm and evaluation path. Do not lock an idea until competitor re-crawl and the 25-concept tournament are complete.

## Microscopy count reliability (investigated; current pitch rejected)

- **Data is strong:** Broad Institute's BBBC039 v1 page documents 200 fluorescence fields, roughly 23,000 manually labeled nucleus instances, official train/validation/test metadata, and CC0. It is a tractable public benchmark, but covers a single U2OS chemical-screen experiment, not general microscopy or clinical use.
- **Problem evidence:** Microscopy segmentation evaluation is a real methodological concern. A survey/review notes the labor and consistency problems in reference annotations. This establishes a scientific-method concern, not a demonstrated end-user demand for another software product.
- **Novelty failure:** Prior work directly studies uncertainty intervals for cell counting and uncertainty-based identification of segmentations for human review. So “show uncertainty and ask a human to review” fails the novelty gate as stated. A new contribution would need a specific validated decision procedure beyond known uncertainty maps/intervals (for example, evidence that a review-budget policy controls count error on a genuinely held-out shift); that is only a hypothesis and would require focused prior-art review.
- **Current decision:** Do not build the proposed uncertainty-audit app yet. Its benchmark and demo are unusually feasible, but feasibility does not cure weak originality or absent user validation. Reconsider only if a clearly novel, defensible mechanism survives literature and gallery review.
- **Sources:** refs 21–31 in [SOURCES.md](../SOURCES.md), especially the official BBBC039 record and refs 28–30.

## Cooling-center allocation (investigated; generic pitch rejected)

- **Impact:** Published work found substantial differences in proximity to cooling centers across 81 US cities and identifies underserved populations. This supports a real planning problem, but not a claim that a new optimizer reduces heat illness.
- **Prior art/product overlap:** A 2024 co-produced Phoenix/Tucson workflow already applies public data and location-allocation to select new cooling-center locations; City-HEAT optimizes heat adaptation investments under uncertainty and includes cooling centers; WRI's 2026 Cool Cities Lab is a current open-data heat planning tool.
- **Current decision:** Reject a generic cooling-center or heat-resource optimizer. Reconsider only if a specific underserved group, city partner/data source, or operational constraint enables a genuinely different and verifiable workflow. A modeled increase in geographic coverage is not evidence of changed health outcomes.
- **Sources:** refs 32–35 in [SOURCES.md](../SOURCES.md).
