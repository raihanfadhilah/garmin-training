# Existing plan (madeira25k.json) vs. the research — gap analysis

Remaining weeks are **7-17** (today is 2026-08-15, inside plan week 6). Race 2026-11-01.

| Wk | Start | Phase | Long (km) | Vertical (min) | Eccentric |
|---|---|---|---|---|---|
| 7 | Aug 16 | Build | 19 | 30 | yes |
| 8 | Aug 23 | Build DOWN | 13 | 20 | — |
| 9 | Aug 30 | Build | 21 | 30 | yes |
| 10 | Sep 06 | Build | 22 | 35 | — |
| 11 | Sep 13 | Build | 18 | 35 | yes |
| 12 | Sep 20 | Peak DOWN | 15 | 30 | — |
| 13 | Sep 27 | Peak | **28** | 40 | yes |
| 14 | Oct 04 | Peak | 20 | 35 | yes |
| 15 | Oct 11 | Taper | 15 | 20 | yes |
| 16 | Oct 18 | Taper | 11 | 20 | — |
| 17 | Oct 25 | Race | race 25 | — | — |

## The four real problems

### 1. Vertical volume is roughly an order of magnitude short
Vertical sessions peak at **40 minutes/week**. Even at a generous 600 m/h climbing rate
that is **~400 m of ascent per week** — against a race demanding **2,003 m in one day**.
The course's Mountain Index is **80 m/km**; the plan's long runs are effectively **0 m/km**.

This is the single biggest gap. Weekly vertical needs to build toward and exceed race
vertical during peak weeks, and the long session should carry most of it.

### 2. Descent volume is not programmed at all
"Vertical" sessions are labelled *climbing, concentric* in the plan — explicitly the
uphill half. **Descent is the crux of this race and it is essentially absent.** The
`eccentric` sessions (7 across the remaining block) are gym work, not descending, and
carry no descent-metre target.

The 2025 bout-count study needed **10 downhill sessions** to significantly reduce soreness.
The plan has 7 gym eccentric sessions and ~0 programmed descent metres.

### 3. The peak long run lands 5 weeks out
Week 13's 28 km falls in the week of **Sep 27 — 5 weeks before the race**, then the plan
declines (20 → 15 → 11). That is a very long, slow descent into race day and risks
detraining. Meta-analytic taper evidence favours a **2-week taper** with peak work
**14-15 days out**; the plan effectively tapers for 5 weeks.

Also note the jump from week 10 (22 km) to week 13 (28 km) is **+27%**, close to the
>30% threshold where Nielsen et al. found an injury signal — and it comes after two
reduced weeks (18, 15), which is exactly the **dip-then-rebound pattern** that preceded
injuries in the trail-runner load study (loads fell 16-24%, then rebounded 15-37% into
the injury week).

### 4. Long runs are prescribed in kilometres
Minetti's gradient cost data (a ~5.6x swing in J/kg/m between level and +45%) makes
distance an invalid load unit for this terrain. **Time on feet + vertical metres** are the
defensible units. The plan already moved partway here (commit "rebuild around time-on-feet
and descent") but the long sessions are still km.

## What the plan gets right

- **No back-to-back long runs** — correct for this athlete (2 years' consistency, an
  established 3 h long run and no bone-stress history would be prerequisites; he has none).
- **Weekly cycling 75-90 min** — good call. Aerobic volume with zero impact and zero
  eccentric cost, which is exactly what an athlete at 11% decoupling and STRAINED status
  needs.
- **Separate legs day, no running** — sensible interference management.
- **Down weeks at 8 and 12** — smooth-ish, though see the dip-rebound caveat above.
- **Strength split (push/pull/legs) maintained through the block** — consistent with the
  evidence that strength should be *maintained*, not dropped, until ~10-14 days out.

## Suggested corrections (ranked by expected value)

1. **Reprogram the long session in hours + vertical metres**, not km. Target the peak
   session at **3:30-4:00 with 1,600-1,800 m of vert**, i.e. 80-90% of race vertical.
2. **Move the peak long session to ~Oct 17-18 (14-15 days out)** and compress to a
   **2-week taper**, volume -50% then -70%, intensity and frequency held.
3. **Add explicit descent metres to every vertical session** — make them out-and-back
   repeats so ascent and descent are equal, and log descent as its own metric.
4. **Insert the weighted downhill-walk preconditioning protocol early** (see the downhill
   research doc, §2b): -25 to -30% gradient, 5 min, ~110 m descent, 10% BW pack. Cheap,
   safe, and it bought 49% strength-loss protection in the study.
5. **Deal with the STRAINED status before adding eccentric load** — the plan's week 7
   (19 km long + 30 min vertical + eccentric session) lands on an athlete whose VO2max is
   falling and whose decoupling is 11%. Consider making week 7 an unplanned down week.
6. **Add a terrain trip or two** (Posbank/Veluwezoom, Utrechtse Heuvelrug) in weeks 11-13
   and, ideally, a 2-3 day camp around weeks 13-14. Rated the highest-value flat-lander
   intervention by CTS and the only realistic way to get near race-specific descent.
