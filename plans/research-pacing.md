# Race-Day Pacing — Research Findings

## 1. Course reality check

See `research-race-facts.md` for the verified facts. The three that drive pacing:

- **Cut-off is 11.5 hours**, not 6h15. Estimated finish 5:00-6:45. **~5 hours of margin.**
- **Point-to-point: Calhau de São Jorge (north coast, sea level) → Machico (east coast, sea
  level)**, 25 km, ~2,003 m D+ / ~2,003 m D-, **max elevation ~500 m**.
- **Only ~2 checkpoints** (~10 km apart). **No crew, no pacers, no drop bags.** Self-sufficient.

**Important caveat on the profile.** The segment shape in the brief — big early climb, then
~450 m dropped in 1.5-2 km at 25-30%, then rolling, then a second climb and sawtooth — is
**not verifiable from any public source**. The race pack publishes a route line on a map with
**no elevation profile**, and no public GPX was found. What *is* inferable: sea level to sea
level with a ~500 m ceiling and 2,003 m of gain means **at least four significant climbs** —
so "sawtooth" is structurally correct even if the specific 450 m descent is not confirmed.
**Treat the segment plan below as provisional until the GPX is obtained.**

## 2. Pacing models for vertical-heavy races

### Even pacing — associated with faster times, but the effect is modest

**Ultra-Trail du Mont-Blanc 2008-2019** ([PMC7578994](https://pmc.ncbi.nlm.nih.gov/articles/PMC7578994/)),
**n = 13,829** (12,681 men, 1,148 women), 9 years with >=18 comparable time stations. Pacing
measured as **coefficient of variation of pace between checkpoints**.

- Pace average and steadier pace **positively correlated** for men, women and combined.
- **Correlation strength: r = 0.304 (p < 0.001) for men/combined; r = 0.253 for women.**
- **No significant correlation between performance level and pacing strategy** — attributed to
  the already-elite UTMB field.

**Honest read: r ≈ 0.30 is a modest correlation in an observational dataset.** Even pacing is
*associated* with faster finishing; causation is not established, and the better runners are
plausibly steadier *because* they are better. Useful directionally, not a law.

### What actually happens in a mountain ultra — and why HR fails as a pacing tool

**Millet et al., 106 km / 5,870 m D+ French Alps, n = 15 experienced ultrarunners**
([PMC4687124](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4687124/)). Measured across 10%
segments of total duration:

| Variable | Finding |
|---|---|
| Overall pattern | **Positive pacing** — speed declines through most of the race, rises in the final 10% |
| Speed loss by gradient | **level -2.91%, downhill -2.61%, uphill -1.31%** per segment |
| **Heart rate** | Mean 132.6 ± 13.6 bpm; **declined 34.2 ± 17.2 bpm across the race** (significant 10% → 70/80/90%) |
| **General RPE** | **rose 4.3 ± 1.1 → 6.9 ± 1.4** |
| **Knee-extensor RPE** | **rose 3.8 ± 1.3 → 6.9 ± 2.2** |

**This is the single most important pacing finding for this race.** Heart rate **falls by
~34 bpm** while perceived effort **rises by ~60%**. The two decouple completely and in
opposite directions.

The authors also found HR stayed constant on sustained climbs despite varying intensity, and
concluded that HR is **not a complete pacing guide** in mountain ultras — terrain complexity
requires "multi-sensory regulation beyond cardiac response."

**Practical consequences:**
1. **GPS pace is meaningless** here — a 25-30% descent and a 25% climb produce wildly different
   paces at identical effort.
2. **HR is usable as a ceiling in the first third only.** After that it drifts *down* and will
   systematically tell him he's working easier than he is. Do not chase an HR number late.
3. **RPE is the primary instrument**, and specifically **knee-extensor RPE** — how the quads
   feel — is the variable that tracks the actual limiter. That is the number to watch.
4. Note his measured **aerobic decoupling is 11%** (target 5%), i.e. his HR-vs-output
   relationship is already unstable at much shorter durations. This makes HR *even less*
   trustworthy for him than for the study population.

### Power meters and grade-adjusted pace

Running power meters and GAP are sometimes proposed as terrain-independent pacing tools. Both
inherit the **Minetti treadmill model**, which:
- was fitted from **running only** (n=10, smooth belt) with **no walking data** — so it is
  unjustified for power hiking, which is what he'll do on every climb;
- **over-credits descent** (Strava's own engineering found the real benefit peaks near -10%
  and reverses beyond, and they re-fit against user HR data);
- ignores technical footing, eccentric damage and cumulative fatigue — the three things that
  decide this race.

**Verdict: don't pace off power or GAP.** Use RPE, with HR as an early-race ceiling only.

## 3. The early steep descent — the key tactical problem

### The mechanism

Exercise-induced muscle damage **reduces running economy during subsequent exercise above
~65% VO2max** ([Assumpção et al. 2013 review](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3575608/)).
Soreness, altered kinematics and raised metabolic rate all compound. Damage incurred early is
therefore not a local cost — it **taxes every remaining kilometre**, including the climbs.

Supporting numbers from the eccentric literature (see `research-downhill.md`):
- Knee-extensor strength loss in downhill running: **-23.5% untrained / -16.4% trained**.
- In a 156 km, 6 x 26 km / 1,000 m lap race, **knee-extensor strength fell ~41% by the finish,
  and peak power / jump height were already down 6-7% from the *early* laps.** Degradation
  starts immediately and accumulates — it is not a late-race phenomenon.
- Tissue-stress models predict **>40% higher cumulative damage at 5 m/s vs 3 m/s** on a -10%
  slope. **Speed is the dominant controllable variable.**
- At -10 degrees and steeper, knee energy absorption is *blunted* and load shifts to ankle and
  hip — so a shallower slope run fast can damage the quads more than a steeper one run slow.

### The tactical answer

**Descend the early steep section conservatively. The cost is small and the saving is large.**

- With an **11.5 h cut-off** against a 5-6.5 h estimate, time pressure is effectively zero.
  There is **no clock-based argument** for racing the first descent.
- The realistic time difference between a controlled and an aggressive descent of a 1.5-2 km
  steep section is a **few minutes**. The realistic cost of arriving at the second climb with
  quads already at -20% is **far more than a few minutes**, and it compounds over ~20 km.
- He is **downhill-naive** and this is his first mountain race. The variance on an aggressive
  steep descent includes a fall on technical volcanic rock, which is a DNF, not a slow split.

**Rule of thumb to give him: on the first descent, run at an effort where he could hold a
conversation and could stop within two strides.** If he passes people there, he is going too
fast.

## 4. Steep descent technique

Coaching consensus is fairly uniform; the evidence base under it is thinner than the
confidence with which it's stated.

| Element | Prescription | Evidence |
|---|---|---|
| **Cadence** | Short, quick, frequent steps; minimise flight time | **Contested — see below** |
| **Foot placement** | Land midfoot, **under the centre of gravity**; never reach forward | Overstriding demonstrably raises braking impulse |
| **Posture** | Slight forward lean **perpendicular to the slope**; low centre of gravity. Leaning back and heel-striking is the instinctive response and is mechanically wrong | Consensus; mechanism sound, not directly tested |
| **Arms** | Wide, away from the torso, as stabilisers | Consensus only |
| **Gaze** | Scan **3-4 m ahead**, not at the feet | Consensus only |
| **Line choice** | Pick the line early; commit | Consensus only |

### The cadence contradiction — flag this honestly

- **Standard advice:** increase cadence; higher step frequency reduces per-step peak load and
  impulse at the patellofemoral joint, tibia and Achilles across speeds and gradients.
- **But** the [2025 Frontiers review](https://www.frontiersin.org/journals/bioengineering-and-biotechnology/articles/10.3389/fbioe.2025.1690023/full)
  reports that running **within ±5% of preferred cadence** minimised both caloric cost *and*
  impulse loading; -10% below preferred was clearly worse, but large deliberate *increases*
  were not supported.
- **Foot strike:** forefoot striking reduces vertical impact force vs rearfoot, especially
  downhill — **but deliberately switching foot strike produced no improvement in neuromuscular
  fatigue.** Adaptability across patterns mattered more than any single pattern.
- **Real-race data (Giandolini):** cadence naturally *drops* across a race — 180.6 → 174.6 →
  163.8 spm — as fatigue accumulates.

**Recommendation: do not prescribe a cadence number.** Prescribe *practising varied descent
technique* so adaptability develops, and cue "quick and light, don't reach, don't brake"
qualitatively. The direction is well supported; the magnitude is oversold.

### When to stop running

On sustained 25-30% ground, especially on wet basalt or stone steps, **walking or
side-stepping is a legitimate and often faster choice** for a novice. Madeira's stone
staircases with fixed rope handrails (visible in the official race-pack photography) are
walk-down terrain for almost everyone.

## 5. Fuelling and hydration

**Energy demand.** Modelling the course as a sawtooth with the Minetti cost function at 56 kg:
climb ~1,124 kcal + descent ~220 + flat ~559 ≈ **1,900 kcal net**, ~2,200-2,400 gross over
~6 h → **~380-420 kcal/h**.

**Carbohydrate rate.**
- Single-transportable carbohydrate saturates at **~60 g/h**; glucose + fructose (SGLT1 +
  GLUT5) raises capacity to **75-90 g/h**.
- **Costa et al. 2019 (IJSNEM) ultramarathon position paper:** the 90 g/h figure "**probably
  requires scaling down for ultramarathon activities, due to the lower absolute exercise
  intensity**." **GI symptom prevalence after ultramarathon: 60-96%.**
- Higher rates (90 vs 76 g/h) produced **greater symptom severity and feeding intolerance**.
- Real-world ultrarunners average only ~**37 g/h**.

**Target: 60-80 g/h**, trained up from 40-50 g/h over the block (~7-8 rehearsal sessions),
using the exact race products. Fluid **400-800 ml/h**; sodium **~500-800 mg/h** (the sodium
evidence is weak — individualise by sweat and cramp history).

**Timing tied to the profile — this is the practical insight.** Climbing and power-hiking make
eating **easy** (low bounce, low ventilation, hands relatively free, especially with poles
stowed). Steep technical descending makes eating **nearly impossible** and raises GI upset.

**So: front-load intake on every climb. Eat on the ups, drink on the flats, take nothing on
the steep downs.** Practically — take a gel or solid at the base and again near the top of
each significant climb, and treat descents as pure work.

Note also the checkpoints are **~10 km apart** with only water and snacks, and there are no
drop bags. He must **carry essentially all his own calories** for a 5-6.5 h effort — roughly
**400-500 g of carbohydrate**. That is a meaningful pack-weight and stowage problem to solve
in training, not on race morning.

## 6. Segment-by-segment plan (provisional — profile unverified)

Efforts on a 1-10 RPE scale. **HR as a ceiling in segment 1-2 only; RPE thereafter.**

| Segment | Effort | Do | Don't |
|---|---|---|---|
| **Start → first climb** | RPE 3-4, HR ceiling ~easy-aerobic | Let the field go. Settle into a hiking rhythm immediately once gradient exceeds ~15%. Poles out | Don't run the climb because everyone else is. Don't start in the top third |
| **First big climb** | RPE 5-6, "conversational" | Power-hike, hands on quads or poles. Eat at base and near top. Target ~550-700 m/h | Don't let RPE exceed 6. If breathing breaks conversation, slow down |
| **Steep early descent (~450 m in 1.5-2 km)** | RPE 4-5 — **deliberately below what feels possible** | Short quick steps, midfoot under the hips, gaze 3-4 m ahead. Walk or side-step the steepest/wettest sections and the stone stairs | **This is the single most important don't in the race: do not race this descent.** Don't heel-brake. Don't take calories here |
| **Rolling middle** | RPE 5-6 | Run the runnable. Fuel hard — this is the easiest eating window after the climbs. Refill at the checkpoint | Don't try to "make up time" lost on the descent |
| **Second major climb** | RPE 6, rising to 6-7 late | Hike it. Expect quads to already feel compromised — that's normal and expected, not a sign of failure. Keep eating | Don't panic at the strength loss. Don't chase HR — it will read low |
| **Sawtooth section** | RPE 6-7, descents still controlled | Keep the descents conservative even now — knee-extensor RPE is the variable to monitor. Small consistent efforts | Don't surge on the short climbs. Don't let the descents become falls |
| **Final descent to Machico** | RPE 7-8 if the legs allow | This is where positive-pacing data show finishers actually speed up. Spend what's left | Don't spend it before you can see the finish |

**Realistic finish estimate: 5:00-6:45.** Cut-off 11.5 h — no time pressure whatsoever.

**Overall shape:** the UTMB data favour even pacing (r ≈ 0.30, modest), while the Millet field
data show real mountain ultras are run with **positive pacing plus a final surge**. The
reconcilable advice: **aim for even *effort*, accept that speed will decline, and hold enough
back on the early descent that a final surge is physically available.**

## 7. CORRECTIONS to sections 3-4 above

Later research overturned or sharpened several points. **Where this section conflicts with
what's above, this section wins.**

### Cadence — the standard advice is mis-cited

**Giandolini et al. 2013** (*EJAP* 113:599-609) is the paper usually invoked. In 9 rearfoot
runners, **+10% step frequency ALONE did NOT significantly reduce loading rate** (52.7 vs
56.3 BW/s, n.s.). Only the *midfoot* condition worked (-56.9%).

**The strongest damage-specific finding is about STEP LENGTH, not cadence.** Rowlands (in
Bontemps 2020): **understride -8.8% MVC loss vs preferred -15.5% vs overstride -14.7%** —
understriding roughly **halved** the strength loss. Field corroboration: shorter step length
correlated with less squat-strength loss (r = -0.37).

**Revised cue: "more steps, same speed" — 185-195 spm achieved by shortening the step, not
by driving the legs faster.** His habitual cadence is 161-178 (168 on his 17 km run) and the
plan targets 178 — **on this descent he needs to be above that.** The untrained default is
exactly wrong: cadence naturally *falls* and aerial time *rises* on descents (Vernillo 2017).
Raising step frequency 10% downhill is metabolically free (no VO2 change).

### Foot strike — do not consciously change it, and anterior is actively worse

**Giandolini 2017** (*SJMSS*), 6.5 km / 1,264 m descent: **the more anterior the foot strike,
the LARGER the drop in knee-extensor evoked torque and the larger the MVC decrement at 2 days.**
Deliberate manipulation is refuted outright — **Vernillo 2024** (*IJSPP*, 2.5 h graded run,
8 non-RFS vs 8 RFS) found **no interactions for any neuromuscular, EMG or biomechanical
variable**. The one positive finding is **variability**: high spontaneous foot-strike variability
predicted *less* fatigue in both knee extensors and plantar flexors.

**Let terrain dictate foot strike — the variability is itself protective. Manage step length
instead.**

### Descents are a frontal-plane hip problem, not only a quad problem

*IJSPT* 2025 (12 runners, -15% to +15%): **total hip drop 23.7 mm at -15% vs 7.6 mm at +15%
(d = 1.80, very large)**. This is the most neglected finding in the descent literature.
**Add hip-abductor / frontal-plane work**; the existing plan's glute-med work is framed for
IT band, not descent control.

Also: nobody runs perpendicular to the slope. Trunk sits **~12 deg behind perpendicular at -15%,
~18 deg at -28%**. Practitioner sources actively contradict each other on lean. **Prescription:
hips under you not behind you, slight lean from the ankles, don't fold at the waist, don't sit
back on a locked-out lead leg.**

### Gaze — the best-evidenced item in the whole technique section

**Matthis, Yates & Hayhoe 2018** (*Current Biology* 28:1224-33), mobile eye-tracking on natural
terrain: **temporal look-ahead is held constant at ~1.5 seconds regardless of terrain**; gaze
clusters on the **second upcoming foothold** (94-96% of time on path on rough ground).
The authors propose **visual information-gathering is the bottleneck setting maximum speed** —
you cannot run faster than you can visually plan.

**~1.5 s ahead = ~4-5 m at 3 m/s, ~3 m at 2 m/s. Fixate the second and third footfalls.
When fatigue drags the gaze down, the planning horizon is gone — slow down.**
*(Caveat: that study was walking, not running.)*

### Zig-zag — the most powerful geometric lever, and the arithmetic is clean

Traversing at angle β from the fall line reduces effective gradient by cos(β).
**At β = 60°, gradient halves: 28% → 14%** — moving him from beyond the studied range back
into the well-characterised -15% region where all the lab data lives.

**Friction matters here.** Standing on a 28% slope needs μ >= 0.28; braking hard needs
considerably more. **Wet volcanic rock and wet wooden steps sit around μ ≈ 0.3-0.5.** In the
wet he will be at or past the friction limit — zig-zagging and side-stepping stop being
stylistic choices.

### Braking forces — the numbers, and where the evidence stops

**Gottschall & Kram 2005** (*J Biomech* 38:445-52), 3 m/s, -15.8% vs level:

| Metric | Change |
|---|---|
| Normal impact force peak | **+54%** |
| Parallel braking force peak | **+73%** |
| **Parallel braking impulse** | **+108%** |
| Propulsive impulse | **-57%** |

**Almost all mechanical energy is already negative by -15.6%** — beyond that the descent is
pure energy dissipation. **No ground-reaction-force data exists beyond -15.8%**, so every
statement about -25/-30% is extrapolation. **At his gradient, speed and step length are the
only levers left.**

### The trade-off, quantified — but flag it as arithmetic, not experiment

**No published model or experiment quantifies time-cost-of-holding-back vs time-saved-later.**
This is indirect evidence plus arithmetic.

Racing the 450 m / 1.75 km descent saves: 1,900 m/h = 14:13 (**-10.0 min** vs even effort);
1,400 m/h = 19:17 (-4.9); braked 800 m/h = 33:45 (+9.6).

Cost later (sawtooth -550 m + final -600 m, 130 min combined at even effort): mild damage
(20% slowdown) **+17 min**; moderate (35%) **+30 min**; severe (55%) **+46 min**.

**Net: bombing it saves ~10 min and risks 17-46. Roughly 3:1 to 5:1 against, before fall and
DNF risk.**

Strongest evidence-anchored argument is skill-based: between-runner CV was **>30% on a
technical rocky descent vs <10% on flat** (*Front Physiol* 2019). **A first-timer from Amsterdam
sits at the bottom of that distribution — he cannot access the upside but is fully exposed to
the damage cost.** CTS telemetry has elites taking early descents at only ~126% of mean race
speed.

**And it will never feel hard:** VO2 on descents is only **79% of ventilatory threshold** vs
89% level and 100% uphill (Townshend 2010). **Breathing is a useless pacing signal here.**
That is the trap.

### Time allocation — descending discriminates more than climbing

**Bettega et al. 2026**, Dolomyths Skyrace (**22 km / ±1,750 m — the closest published course
analogue**), top 100 men: **62.5% of time uphill, 37.5% downhill.** Time lost vs the winner:
**21.6% downhill vs 18.5% uphill.**

### The single strongest pacing result

**Hoffman et al. 2025** (*PLoS ONE*, **n = 23,207**, 56 races, 6 events, 2012-2022): **in 51 of
56 races (91%), later finishers spent a disproportionately large share of total race time in
the first segment.** After the opening 20-40 km, **all finishers paced the remainder
similarly. The damage is done only at the start.**

**Over-pacing early is non-linear and unrecoverable; under-pacing early is bounded and
recoverable.**

### Even pacing is more contested than section 2 implies

| Study | Race | n | Finding |
|---|---|---|---|
| Hoffman 2014 | WSER 161 km | top-5 | CV correlated with finish time **r = .80** |
| Knechtle/Nikolaidis 2020 | UTMB | 13,829 | steadier → faster, r = 0.304 |
| **Cuk et al. 2023** | **OCC 56 km / 3,460 m** | 5,655 | **OPPOSITE — high-level runners showed *higher* variability** |
| Kerhervé 2016 | 173 km | 15 | **no correlation** |
| **2025 IJSPP, World Champs Trail Short** | closest analogue | 12 elite | **GAP declined 18.7% start→final descent even in elites**; consistency r = -.55 |

**Positive splits are universal. The elite benchmark for this duration is a ~19% grade-adjusted
slowdown. The goal is to make his smaller, not zero.**

### GAP is broken downhill — worse than section 2 states

Minetti's own Table 3: predicted/measured vertical speed **0.950 ± 0.130 uphill** (model works)
but **3.446 ± 1.324 downhill** — overpredicting descent speed ~3.4×. **Strava's empirical model
(6 million runs, 240,000 athletes): the pace-adjustment minimum is 0.88 at -9%, returning to
1.0 by -18%** — i.e. **at -18% real runners get zero net speed benefit**, where Minetti
predicted 2×.

**Stryd is validated only to 8% incline**; this course averages ~16%. Inter-device agreement is
poor (uphill ICC 0.444).

### Heart rate — sharper numbers

**Kerhervé, Millet & Solomon 2015** (*PLoS ONE* 10(12):e0145482), 106 km / 5,871 m, n=15:
**HR fell 34.2 ± 17.2 bpm** while **RPE rose 4.3 → 6.9**; mean race HR **132 ± 10**.
**Fornasiero et al. 2018**, 65 km / 4,000 m, 23 amateurs: mean intensity **77.1 ± 4.4% HRmax**,
**85.7% of time below VT1**.

**"HR is capped on steep hiking" is largely folklore** — Zimmermann 2022 found **no difference
in peak HR, VO2max or lactate between uphill walking and uphill running**. What's real: at a
self-selected hiking pace you are muscle-limited before cardiac-limited, so HR under-reads leg
fatigue.

**The 5% decoupling threshold has no peer-reviewed validation** — it originates with
Friel/TrainingPeaks and Uphill Athlete. By contrast HRV-based threshold methods (DFA-a1) *have*
been validated (ICC 0.77-0.90). What is lab-verified: dehydration costs **~3-5 bpm and 3-4% SV
per 1% body-mass loss** — for 56 kg a 2% loss is **6-10 bpm of pure drift**.

**On this course raw Pa:HR is useless. The usable analogue is VAM-per-HR compared across climbs
of similar gradient** — compare the second climb against the first; **>5% worse means he
overcooked the descent.**

### HR zones for this athlete

Observed max 181; true max likely **185-192**. For 5-7 h at 72-78% HRmax:

| Zone | Target |
|---|---|
| **Race average** | **138-150 bpm** |
| **Climb ceiling** | **155**, brief spikes to 160 |
| **Descents / rolling** | 120-140 |
| **Alarm** | >160 for more than ~2 min on a climb → **walk** |

**His 17 km run averaged 163. He cannot hold that for six hours.**

### Fuelling corrections

- **There is no 2023 ISSN ultramarathon position stand.** It is **Tiller et al. 2019**
  (*JISSN* 16:50), recommending **30-50 g/h** — conservative and out of step with ACSM.
- **Podlogar et al. 2022** (*EJAP*): 120 g/h vs 90 g/h raised exogenous oxidation +17% but
  **endogenous oxidation was unchanged**; above 90 g/h "does not provide any benefits."
- **Recommendation: 60-75 g/h at ~2:1 glucose:fructose. Hard floor 50 g/h. Do not attempt
  100-120.** For 6.5 h that's ~420-490 g.
- **Keep drink mix at 6-8%.** At >500 mOsm/kg, **42.1% of a 10% drink remained in the stomach**
  vs 0.3% of a 2% drink. **A 500 mL flask carrying 80 g CHO is 16% — a well-evidenced route to
  nausea.**
- **Sodium: Hoffman, Stuempfle & Valentino 2015** (WSER) — hyponatraemic runners took 297 and
  554 mg/h vs non-hyponatraemic 515 ± 315 (**p = 0.62, no difference**); **no difference between
  crampers (39%) and non-crampers**. Cramping, dehydration, hyponatraemia and nausea were
  "unrelated to total sodium intake." **Hew-Butler 2015 consensus: drink to thirst (Grade 1C);
  sodium supplementation NOT recommended for EAH prevention.**
  **400-650 mL/h thirst-led; 400-700 mg/h sodium as insurance and palatability. Never combine
  salt capsules with fixed-schedule drinking beyond thirst — that is the EAH recipe.**
  **Priority: carbohydrate >> fluid > sodium.**
- **GI distress (Stuempfle & Hoffman 2015, n=272): 96% had symptoms; nausea/vomiting was the
  primary DNF reason in 23.0%** and contributed to 35.6%. (The common "leading cause of DNF"
  claim is practitioner framing; 23%/36% is the defensible version.)
- **The descent-eating problem is mostly practitioner wisdom** — no study compares gastric
  emptying on ascent vs descent. **The real reason needs no physiology: on 25-30% technical
  ground you need both hands, both eyes and continuous braking.** Use **liquid calories** as the
  only descent option and **front-load a gel in the last 5-10 min before cresting each climb**.
  **Do not "catch up" after a descent** — a bolus into a jostled, hypoperfused stomach is the
  nausea trigger.
- **Caffeine at 56 kg:** ~100 mg at 3 h, ~75-100 mg at 4.5-5 h; total ~150-200 mg
  (2.7-3.6 mg/kg). **Do not scale from the 70 kg examples in popular articles.**
  ⚠️ Essentially all controlled caffeine trials are <2 h.

### Pre-race, rewritten for the 11:00 start

Carb load **8-10 g/kg/day (450-560 g) for 2 days**, low-fibre — not 10-12 g/kg; **560-672 g/day
is a large GI risk for a 56 kg first-timer, and 1-3 kg of water weight costs real work over
2,003 m of climbing.** *(That compromise is judgement, not a head-to-head trial.)*

| Time | Action |
|---|---|
| 07:00-07:30 | Wake naturally. Normal coffee (~80-100 mg, counts toward the caffeine total) |
| **08:00 (T-3 h)** | **~2 g/kg = ~110 g CHO** — white rice or bagels with jam + banana + 400 mL sports drink |
| 08:00-10:00 | Sip 300-500 mL with sodium. Transfer to São Jorge |
| 10:00 | Stop large volumes. Toilet. Kit check |
| **10:45 (T-15 min)** | **1 gel (~25 g)** + a few sips |

### Carry plan — checkpoints are WATER ONLY

Three legs of ~2h10. At 65-75 g/h for 6.5 h ≈ **420-490 g CHO**.

| Item | Amount |
|---|---|
| Gels (~25 g each) | **~13**, front pockets, tabs pre-torn |
| Drink mix | 3 flask-fills at 6-8%, pre-measured into zip bags |
| Water | **2 × 500 mL front flasks** — refill fully at both CPs |
| Mandatory 800 kcal reserve | carried, not eaten |
| **Total vest** | **~2.6 kg = 4.6% of body mass** |

**Front flasks, not a rear bladder** — he must drink one-handed on descents and see what he's
taken. **Rehearse the loaded vest.**

### Revised segment plan (6:15 target)

| # | Segment | km | D+ | D− | Time | Effort | Key point |
|---|---|---|---|---|---|---|---|
| S1 | Climb out of Calhau de São Jorge (cobbled zig-zag royal path) | 4.5 | +550 | −50 | 70 min | RPE 3-4, HR <=150, ~465 m/h | Hike from the first ramp. Let people go |
| **S2** | **THE STEEP DESCENT** | 1.75 | 0 | −450 | 26 min | **RPE 4 cardio / 8 concentration** | Cadence 185-195 via short steps. Zig-zag ~60°. Gaze on footfall N+2. Liquid only. **Every stair, never two** |
| S3 | Rolling / levada / valley | 6.0 | +350 | −300 | 75 min | RPE 4-5, HR 140-150 | Best running of the day. Feed every 20-25 min |
| S4 | Second major climb | 3.5 | +500 | −50 | 60 min | RPE 5-6, HR <=155, ~495 m/h | **Compare VAM-per-HR vs S1: >5% worse = concede 10 min now.** First caffeine |
| S5 | Sawtooth | 6.5 | +500 | −550 | 97 min | RPE 6-7, HR 145-155 | **Where the race is decided.** Hike every rise without debate |
| S6 | Final descent to Machico | 2.75 | +100 | −600 | 44 min | RPE 7 | Cadence discipline. Headtorch if past 18:00 |

### Revised time estimate — anchored on real 2025 data

| Scenario | Time | Finish clock | 2025 field position |
|---|---|---|---|
| Excellent execution, dry, descent held back | **5:45-6:15** | 16:45-17:15 | ~22-25 / 34 |
| **Central estimate** | **6:15-6:45** | **17:15-17:45** | ~25-29 / 34 |
| Wet, or quads gone on S2 | 7:15-8:15 | 18:15-19:15 — **dark** | ~32-33 / 34 |
| Cut-off | 11:30 | 22:30 | — |

**Finishing is very likely. The real risks are the descent and the dark, not the cut-off.**

## Evidence ledger

**Reasonable:**
- Even pacing associated with faster UTMB times (n = 13,829) — **but r ≈ 0.30, observational**
- HR declines ~34 bpm while RPE rises across a mountain ultra (n = 15) — small n, but the
  effect is large and mechanistically coherent
- EIMD reduces running economy above ~65% VO2max
- Speed is a stronger driver of descent damage than gradient
- Overstriding raises braking impulse

**Contested:**
- **Cadence prescription on descents** — "increase cadence" vs "stay within ±5% of preferred."
  Direction agreed, magnitude disputed
- Foot-strike modification — reduces impact force but **not** neuromuscular fatigue

**Folklore / consensus without data:**
- Arm position, gaze distance, line choice, torso angle on descents — all coaching consensus,
  none directly tested
- Specific sodium intake numbers
- **The course profile itself** — unverified; get the GPX before finalising the segment plan
