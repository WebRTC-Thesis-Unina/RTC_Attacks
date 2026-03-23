# NVD RTC/WebRTC Taxonomy Summary

- Source: official NVD 2.0 yearly feeds for 2021-2026, filtered to the publication window 2021-03-08 to 2026-03-08.
- Query terms: WebRTC, TURN, STUN, SIP, RTP, Asterisk, FreeSWITCH, Kamailio, coTURN.
- Method: local keyword query over NVD descriptions/CPE text/references, followed by relevance filtering and macro-area classification aligned with the paper taxonomy.

- Keyword-hit CVEs before relevance filtering: 886
- Filtered relevant CVEs: 415
- Filtered CVEs mapped to supported RTC-Attack Lab macro-areas: 406
- Relevant but currently unmapped CVEs: 9
- Macro-area coverage of the filtered RTC set: 97.8%
- Excluded as irrelevant/noisy matches: 471

## Macro-area distribution

| Macro-area | Dominant NVD subcategories | # CVEs | % |
| --- | --- | ---: | ---: |
| Relay / Traversal | Traversal / relay weakness (24); Relay denial of service (6); Access control bypass / internal reachability (5) | 35 | 8.4% |
| Signaling / Parser | Flooding / denial of service (70); Signaling weakness (58); Parser overflow / memory corruption (48) | 188 | 45.3% |
| Media / Transport | Media transport weakness (37); RTP flooding / denial of service (10); Media protection / downgrade weakness (5) | 52 | 12.5% |
| Web / Backend / API | Web/backend weakness (26); Cross-site scripting (9); File upload / remote code execution (6) | 44 | 10.6% |
| Client / Browser | Client/browser weakness (78); Permission reuse / device access abuse (6); Browser-side trust boundary weakness (3) | 87 | 21.0% |

The supported macro-areas capture most of the filtered RTC-related CVEs in the collection window. This supports a macro-area coverage claim, not a claim that each individual NVD CVE is directly instantiated in the testbed.
