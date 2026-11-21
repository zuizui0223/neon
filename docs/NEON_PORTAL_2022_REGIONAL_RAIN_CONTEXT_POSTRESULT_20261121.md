# Portal 2022–23 regional rain corroboration (not a substitute for site station)

Date 2026-11-21. **Post-result exploratory environmental context**, one NEON Draft PR #23, submission HOLD. The prior on-site original hourly weather gate failed quality for 2021 (52.9%) and 2022 (61.3%); do **not** relax that gate, use regional stations as in-site imputation, or rewrite the fixed original 114-pair rodent ecology model.

Source is the SAME immutable public PortalData commit `weecology/PortalData@afd75933249ae60f3a5e9dab00b354f219e5e045`, but instrumentally independent original regional NOAA GHCN-Daily weather stations named in `Weather/README.md`:

- `Weather/Rodeo_regional_weather.csv` Git blob SHA `dcbcd3f7e414a51ff74d31b17891f8e0593506fc`, station `USC00026716`, max 30 MB.
- `Weather/Sansimon_regional_weather.csv` SHA `0f905f95d788378e3415a1482e4abfa73a2ea3b6`, station `US1AZCH0005`, max 30 MB.

No other source or station can be substituted. Both original CSV files must pass original Git blob SHA before inspecting values. Parse `year,month,day,station,prcp` with a real CSV parser because `prcp_attributes` contains quoted commas. Use only year 2021, 2022, 2023, 2024; month July, August, September, exactly 92 calendar days/year. A source date may count once per station; duplicates with conflicting values STOP that station, not selectively choose a record. Require nonnegative finite `prcp` (the publisher lists millimetres), no `NA` or empty as zero, <=1 value per day. Only if **>=90% valid daily precipitation days in each of four years** for a station may its measured daily precipitation sums be shown. Missing days remain missing; no scaling/zero fill. Preserve 2021→22, 2022→23, 2023→24 signed and absolute regional changes for EACH source-qualified station. State whether 2022→23 is largest absolute change among the three.

Source failure or quality STOP at Rodeo does NOT authorize modifying the Sansimon source criteria or vice versa. A pairwise comparison of station values is only allowed if both pass. If neither passes, both STOP; NDVI and on-site rainfall records remain as previously reported.

**Interpretation:** these regional stations are at different elevations and distances than the Portal 20ha experiments. Even a 2022→23 regional rain anomaly cannot identify resource availability at 16 plant quadrats or 49 mammal trap stations, and cannot explain the 2022-sensitive `plant_count_change × exclosure` interaction causally. The 2020–25 rodent result is already open: this is a post-result check of an external candidate driver, not a confirmatory test. No historical Portal/NEON/Finnish/Structural effects are refitted or altered.

Work: `analysis/audit_portal_2022_regional_rain_context_v1.py`, tests, GitHub source-only + contextual result workflow. Source output contains only aggregate year-level coverage and rainfall totals on qualified stations. All labels and stop reasons reported.
