# Slice 3 — Rich Body Coordinate, Motion, and Dignity Evidence

## Outcome

Bounded Natal now assesses every ordinary body's ecliptic longitude and latitude,
equatorial right ascension and declination, the four associated provider speeds,
longitudinal motion state, possible signs, and all non-sect-dependent dignity
components. Numeric values remain conservative ranges in uncertainty evidence;
only invariant categorical sign, motion, dignity, and existing aspect facts remain
eligible for canonical promotion.

## Contract decisions

- Swiss Ephemeris' returned latitude and equatorial speed values are provider data,
  not new astronomical approximations invented by AGF.
- Every scalar/circular coordinate range uses the existing exhaustive minute grid
  and endpoint-speed safety envelope. Observed extrema are retained inside the
  wider proof range where applicable.
- Dignity evidence records true and false values for domicile (traditional and
  modern), exaltation, traditional detriment, and fall whenever sign is invariant.
  Triplicity is sect-dependent and remains out of Sprint 1.
- Missing fields, non-finite values, and provider failures are distinct evidence
  availability states. An equatorial-only failure is feature-local.
- Exact Natal output remains unchanged. Rich equatorial speeds are requested only
  by bounded evaluation.
- Bounded calculation profile advances to 1.2.0. Existing profile 1.0.0 and 1.1.0
  packages remain schema-valid.

## Gate evidence

- Synthetic fixtures cover stable coordinates, zodiac and right-ascension
  wraparound, sign crossing, station behavior, missing fields, non-finite values,
  whole-provider failure, and feature-local equatorial provider failure.
- Synthetic linear-coordinate observed extrema agree with independent exhaustive
  minute expectations, while proof envelopes conservatively contain them.
- Controlled live Linux/Python 3.11 Moshier evaluation covered all 12 ordinary
  bodies and validated 132 generalized evidence records with zero inconclusive
  coordinate/speed records.
- Calculation-only runtime for a four-hour, 241-state interval was 1.773 seconds.
  See [the compact live summary](rich-body-coordinate-live-summary.json).
- Focused Ruff and the full 225-test suite passed. Forty-two JSON files parsed, five
  changed Markdown files passed relative-link and whitespace checks, and
  `git diff --check` passed. Full command and cleanup details are in the sprint log.

## Deferred boundary

This slice does not promote numeric coordinate representatives, compute declination
relationships, transform coordinates into antiscia/harmonics, add optional bodies,
or introduce houses, angles, sect, or lots. Those remain assigned to later slices
or the second bounded-Natal sprint.
