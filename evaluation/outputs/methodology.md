# Methodology

This dataset was built from the official NVD 2.0 yearly JSON feeds rather than the CVE API because the API restricts publication-date queries to windows of at most 120 consecutive days. Using the official feeds makes the five-year collection reproducible without changing the data source.

Relevance filtering is conservative. Keyword hits without RTC-specific contextual markers were excluded and recorded in `processed/nvd_excluded_cves.csv` with a short rationale.
Relevant CVEs that remain outside the current RTC-Attack Lab macro-areas are retained in `outputs/unmapped_relevant_cves.csv` so that any coverage claim remains auditable.
