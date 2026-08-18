# Season training plan — handoff

**Date:** 2026-08-18 · **Repo:** `/Users/raihan/training` · branch `main`, clean, pushed to `origin/main` at `f232e10`

---

## TL;DR

Rebuilt the training plan from a single Madeira race plan into a three-race season (Madeira 25K → HYROX Doubles → IRONMAN 70.3 Venice), driven by research that overturned several assumptions in the original. Shipped: three plan JSONs, a published HTML reference artifact, six research documents, subscribable ICS calendars, and two `ics.py` bug fixes. All committed and on `main`.

Athlete is 25M, **160 cm / 56 kg**, VO2max 53 (down from 57 since March), FTP ~165 W. Standing instruction: **be blunt and objective, not sycophantic.** He repeatedly and correctly caught structural errors in the plan — treat his pushback as signal.

---

## Races

| Race | Date | Target | Status |
|---|---|---|---|
| Ultra X Madeira 25K | **1 Nov 2026** | **beat 5:24:37** (2025 median); expect 6:15–6:45 | entered |
| HYROX Amsterdam Doubles | 22–24 Jan 2027 | 88–95 min | **not yet entered** (~€120) |
| IRONMAN 70.3 Venice-Jesolo | 24 Apr 2027 | 6:15–7:15 | entered, €1,032 paid 17 Aug |

Madeira: 25 km, 2,003 m D+/D−, São Jorge → Machico, **11:00 start**, cut-off 11.5 h. The 2,003 m is *cumulative* — max altitude only ~500 m. A sawtooth, not one mountain.

---

## What shipped

**Plans** (`plans/*.json`, selected via the `GARMIN_PLAN` env var)
- `madeira25k.json` — weeks 1–6 untouched (history), **weeks 7–17 rewritten**
- `hyrox2027.json` — 10 weeks, 15 Nov → 23 Jan
- `venice703.json` — 12 weeks, 31 Jan → 24 Apr

**Reference artifact** — `plans/plan.html`, published at
https://claude.ai/code/artifact/5fdba2b6-7c7a-4997-b07b-c566a8115363
Republish with the Artifact tool on the same file path to keep the URL.

**Research** — `plans/research-{downhill,vertical,progression-taper,pacing,race-facts,plan-gaps}.md`, ~1,510 lines, written by subagents. Sourced and hedged. Read these before contradicting anything in the plan.

**Calendars** — `plans/{madeira25k,hyrox2027,venice703,season}.ics`. `season.ics` is 269 events, 5 Jul 2026 → 24 Apr 2027. He is subscribed on iPhone to:
`https://raw.githubusercontent.com/raihanfadhilah/garmin-training/main/plans/season.ics`

**Code** — `garmin/ics.py` (two fixes), `garmin/plan.py` (`RUN_KINDS` += brick, compromised, sim; `LONG_KINDS` += brick).

---

## Madeira: what changed and why

Three structural faults, **all identified by him**:

1. **No rest days** → now Mon and Fri
2. **Legs + push in the same session** → push moved to Wednesday
3. **Zero hard intensity** (research wants 15–20% hard, on incline) → uphill intervals from week 9

Plus, from research:
- **Vertical was an order of magnitude short** — 40 min/week (~400 m) against a 2,003 m race. Now builds to ~3,000 m/week.
- **Descent was not programmed at all.** Now: preconditioning downhill walks, walk-down stairwell sessions, hard-surface Posbank days.
- **Peak was 5 weeks out.** Moved to **Sat 17 Oct, 15 days out.**

**Locked week (7–16):**
`Sun optional ride · MON REST · Tue legs + preconditioning walk + sled · Wed easy run + strides + push · Thu vertical + pull · FRI REST · Sat LONG DAY`

Eccentric work sits **48 h apart** — Tue heavy → Thu moderate → Sat long. That spacing is the constraint the whole week is built around. Cutbacks weeks 10 and 13.

**Cut order:** (1) Sunday ride, (2) Thursday vertical. **Never** Saturday's long day or Tuesday's legs.

---

## Key research findings

Don't re-litigate without reading the files.

- **Preconditioning downhill walk** — 5 min at −28%, 5 km/h, 10% BW. One bout cuts strength loss 49%, CK 47%, soreness 66% a week later. Best evidence-to-effort ratio in the plan. Every 2–3 weeks.
- **RBE protects soreness and CK, not strength.** He reaches climb 2 with weakened quads regardless — race-day descent pacing is co-equal with training.
- **The descent decides the race.** Racing the first steep descent saves ~10 min and costs 17–46. Descent VO2 is only 79% of threshold, so breathing gives no warning. In 91% of 56 races (n=23,207), slower finishers overspent in the *first* segment.
- **10% rule falsified** (RCT n=532). **ACWR discredited** (Impellizzeri 2020) — yo-yo loading, not absolute load, preceded injury.
- **HR is unreliable in mountain ultras** — falls ~34 bpm while RPE rises 4.3 → 6.9. Pace off knee-extensor RPE.
- **Foot-strike manipulation is counterproductive** on descents. Cue is **shorten the step, 185–195 spm**.
- **Hyrox:** running is **55.8%** of doubles time (r = 0.90 with finish). Wall balls r = 0.266, lowest of any segment — don't train them. Roxzone is ~3 free minutes.
- **Venice:** swim cut-off 1:10 is absolute (0 of 19,137 finishers swam >70:00), but any stroke is legal and resting on a buoy is permitted. Water 15–17 °C; the 2027 race is 9–13 days earlier than recent editions.

---

## Nutrition

Baseline day ≈ **2,860 kcal, 142 g protein, ~233 g carbs (4.2 g/kg)**. Protein is 15% *over* target. **Carbohydrate is the gap** — Factor meals are 520 kcal / 32 g protein / **only 22 g carbs**.

Rest days adequate; training days ~240 short, long days ~790 short. Fix is two items: **porridge (~95 g carbs) + peanut butter sandwich and banana (~60 g)**, ~€1.50/day.

Targets: rest ~2,600 · training ~3,100 · long day ~3,650.
Fuelling: easy 30–40 g/h · long 60–70 g/h · **never above 90** (exogenous oxidation is 33 g/h below 70 kg vs 45 above). **Drink mix 6–8%, always.**

Gels: **Upfront Gel PRO** — 40 g, 1:0.8, €2.33 (~€5.83/100 g carbs vs €11 SIS, €19 Maurten). Packaging is unusable on the bike — **decant into a soft flask**. Train on DIY maltodextrin+fructose (~€1/100 g), race on gels.

---

## Money

Coordinated with the `finance [474255]` peer session. Amex cycle runs **17th → 16th**; salary lands 22nd–24th, same day as the debit.

| When | What | ~€ |
|---|---|---|
| Now | Madeira kit gap (1.5 L hydration, ≥15 cl beaker, 800 kcal, torch batteries) | 35–62 |
| **18–20 Sep** | **Trail shoes + poles** | 160–260 |
| after 17 Sep | Gels + bulk powder | 46 |
| ~25 Oct | Extreme-weather kit if triggered — **buy in Amsterdam** | 40–80 |
| 17 Nov | First swim card + **HR chest strap** | 154–174 |
| Dec–Apr | Swim cards 2–3, lessons, wetsuit, Italian medical | 508–888 |

September has **€67** without subscription cuts, €267 with. Pool: **Sloterparkbad, 3 × 25-visit cards, €372** — chosen on proximity (10–15 min vs 20–25 for De Mirandabad); buy spaced, not up front. **Ardennes trip (€200) unfunded**; a second Posbank day (~€30) stands instead. Hard expiry 17 Oct.

---

## Open work, ordered

1. **Trail shoes + poles, 18–20 Sep.** Nearest hard deadline. Shoes need 100+ km break-in; poles need six weeks — inexperienced pole users got *slower* in the field study.
2. **Madeira kit gap now** — €35–62, and he'd fail kit check without it. Checks are enforced (rules 13/14).
3. **Italian `certificato medico agonistico`** — ECG-based sports medical on the FITRI form, book by **Feb 2027**. No certificate, no race pack. ~€80–150, not in the entry fee.
4. **Trainmore desk questions** — is he getting the €1/workout discount (up to €18/mo)? Flex or committed contract? Pause option for Feb–Apr? Only saving that starts *this month*.
5. **Email Ultra X for the official GPX and pole policy.** All descent tactics still rest on a pixel-read of a low-res profile graphic. **No GPX exists publicly** — checked race site, 11-page pack, ITRA, UTMB, four aggregators.
6. **Hyrox entry** (~€120) — register late Sep/Oct, book the **22–24 Jan** dates (earliest maximises Venice runway).
7. **Partner needs an aerobic base.** He does sprints only. Running is 56% of doubles time and they run at the slower man's pace — biggest lever on the team result, and it isn't on Raihan's side.
8. **Car + food for Madeira** — finance carries ~€240 as an unvalidated guess. **Do not chase it** (finance's explicit instruction); it'll surface when he plans the trip. Pick up in October if not.

---

## Tooling and env

```bash
# Garmin sync + DB
uv run python -m garmin sync
sqlite3 ~/.garmin/garmin.db "SELECT day, resting_hr, hrv_last_night_avg, acwr, training_status FROM daily_metrics ORDER BY day DESC LIMIT 5;"

# Plan status against a specific block
GARMIN_PLAN=plans/hyrox2027.json uv run python -m garmin plan-status

# Regenerate calendars (then merge — see commit f232e10 for the merge script)
for p in madeira25k hyrox2027 venice703; do
  GARMIN_PLAN=plans/$p.json uv run python -m garmin calendar --out plans/$p.ics
done
```

**MCP:** `garmin` (sync, plan-status, recent-runs, analyze-run), `hevy` (routines, workouts, exercise templates).
**Peer session:** `finance [474255]` via `SendMessage` — owns the money model; this session owns training and kit.
**Browser extension** disconnected mid-session; several sites (levadas.live, Trustpilot, Upfront product pages) are JS-gated and need it.

---

## Gotchas

- **He is on `main` and asked to push directly** — skip PR ceremony for plan/calendar regenerations. `gh pr merge` is blocked by the permission classifier; don't route around it.
- **`Path.read_text()` normalises CRLF→LF.** Splitting ICS on `"\r\n"` silently yields one giant line and corrupts the file. Read with `.splitlines()`, write with `write_bytes()`.
- **ICS UIDs must be unique per session *and* per race** — was `(week, day, kind)`, which collided (Hyrox W6 has two Saturday swims). Now `{race-slug}-w{n}-s{index}-{kind}`.
- **Session labels are written for the plan file, not calendars.** `SUMMARY` is now a 48-char headline with a type glyph; the full label goes to `DESCRIPTION`.
- **Hevy's app often won't display `rep_range`** (API/app mismatch) — repeat target reps in the exercise notes.
- **His wrist HR under-reads ~37 bpm for 2–3 min at session start.** LTHR of 181 was auto-detected from that sensor, so all zones inherit the error. **Trust resting HR and power; readiness pins at 1 and is near-useless.**
- **Short-run decoupling is contaminated** by that artifact — mean +12.9% under 60 min vs +4.3% over. Long-run decoupling is trustworthy and went from **+13.3% in March to −0.8% in August**.
- **Garmin has his weight as 60 kg. He is 56.** Inflates power, calories and VO2max ~7%. Not yet fixed.
- **Subagents went idle without delivering** several times; had to prod them via `SendMessage` to hand back findings.

---

## Pointers

- Plans: `plans/{madeira25k,hyrox2027,venice703}.json`
- Artifact: `plans/plan.html` → https://claude.ai/code/artifact/5fdba2b6-7c7a-4997-b07b-c566a8115363
- Research: `plans/research-*.md`
- Calendar feed: `plans/season.ics` → `raw.githubusercontent.com/raihanfadhilah/garmin-training/main/plans/season.ics`
- Hevy routine: **"Madeira — Eccentric Day (Tue)"** `7f9f0c6b-61e3-42e1-8f75-df6484870729` (8 exercises, 30 sets)
- Custom Hevy templates: Decline Squat (heels elevated) `35060a7f-…`, Preconditioning Downhill Walk `86a2ec94-…`, Eccentric Step-Down `a732bf45-…`, Tibialis Raise `9ff4fd2f-…`
- Madeira NE trails GPX (OSM + SRTM): `~/Downloads/madeira-ne-trails-osm-srtm.gpx`

---

## Where the session left off

Tuesday 18 Aug, week 7 of 17. Morning numbers green — resting HR 52 at baseline, HRV 101 vs 95 weekly, **ACWR down 1.8 → 1.2**. He shopped at AH, ate porridge ~15:00, and was heading into the evening eccentric session.

Last exchange was practicalities of the preconditioning walk: apartment stairs (a StairMaster cannot descend, so it's useless here), a normal backpack rather than the race vest, 4.5–6 kg of water bottles, and whatever running shoes he already owns.

**Next:** Wed 19 easy run 6 km + strides + push · Thu 20 vertical 45 min stairwell + pull (Hyrox seeding: erg warm-up, farmers carry, dead hangs) · Fri 21 rest · **Sat 22 long day 1:50, 300 m vert**.
