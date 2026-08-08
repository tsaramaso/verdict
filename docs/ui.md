# Game UI Specification v2 — Figma Layout + Interactivity Rules

## CORE PRINCIPLES

### Interaction Model
**Interactivity is determined by:**
1. **Whose turn it is** (only active player can perform turn actions)
2. **Current phase** (determines what game elements are clickable)
3. **Player eligibility** (e.g., only Testimony callers can Challenge)
4. **Trial phases override turn-based rules** (all eligible players act simultaneously)

### Button Zone Philosophy
- **Right panel persistent buttons:** "SKIP / PASS", "TESTIMONY", "CHALLENGE", "PLEA"
- Only **pressable** (enabled) buttons for current state are interactive
- Other buttons are greyed/disabled
- No confirmation prompts—clicks execute immediately (veterans know the rules)

### Your Cards Zone Terminology
**"Select Card"** = a phase where Your Cards Zone is clickable for targeting/selection

---

## SECTION 1: PRE-GAME FLOWS

### 1.1 Login Screen
- UUID input field
- Join button
- "Create New Game" / "Join Lobby" links

**Next:** Home Menu

---

### 1.2 Home Menu
- "Create Game" button
- "Join Lobby" button

**Create Game Dialog:**
- Player count (2–5)
- Turn direction (clockwise)
- Start button

**Next:** Game loads into Round Start

---

## SECTION 2: BASE TABLE LAYOUT (ALL PHASES)

**Persistent Layout (always visible):**

### Left Sidebar
- **Board** label (header)
- (Reserved for future navigation, spectator list, or settings toggle)

### Center Play Area
**Top section (Opponent zones, arranged per player count):**
- Opponent 1 Cards Zone (4 slots, face-down, rotated)
- Opponent 2 Cards Zone (4 slots, face-down, rotated)
- Opponent N Cards Zones

**Middle section (Draw/Discard interaction):**
- **Deck** (center-right): Face-down stack + card count
- **Card Peek Area** (center-top): Where Glance/Spy/Decree peek animations display
- **Discard Pile** (center-left): Face-up top card + stack count

**Bottom section (Your Cards):**
- **Your Cards Zone** (4 slots, face-down, horizontal, centered)
  - Each slot shows:
    - Card back (visual placeholder)
    - Rank badge (if you know the card)
    - Memory indicator (eye icon if Spied, decree icon if peeked)
    - Hue highlight (pastel, if opponent knows this card)

### Top Section (Info & Status)
- **Phase Banner** (center): "Round X — Player Turn: [Name]" or phase-specific text
- **Timer** (above self cards): Countdown in seconds, color-coded (green → yellow → red)
- **Last Turn Alert** (if applicable): "LAST TURN" pulsing banner

### Right Panel (Persistent Info)
**Top: LeaderBoard**
- Compact standings: Player name, current score, rank
- 5 rows (max 5 players)
- Updates live

**Middle: Tooltips**
- Dynamic tooltips for current phase/actions
- Shows zone descriptions (e.g., "GLANCE – View one of your own slots")
- Contextual help text

**Bottom: Button Zone**
- "SKIP / PASS" (multi-purpose button, enabled per phase)
- "TESTIMONY" (enabled during Trial windows if eligible)
- "CHALLENGE" (enabled during Duel window if Testimony caller)
- "PLEA" (enabled during Final Plea window if eligible bystander)

### Bottom-Left Section (Game Info)
- "Score: [X]"
- "Next Renaissance: [Y]"
- "Known Sum: [Z]" (color-coded: green ≤7, red >7)
- "Standings" expandable link

---

## SECTION 3: PHASE-BY-PHASE SCREENS & INTERACTIVITY

### 3.1 Initial Glance (TURN_START)
**Trigger:** Game start or each new round  
**Duration:** ~3–5 seconds (automatic)  
**Player State:** `Phase.TURN_START`

**Display:**
- All players' Your Cards Zones visible
- Brief cosmetic flip animation on 2 slots per player (visual only, cards return face-down)
- No player input required

**Interactable Elements:** None

**Button Zone:** All buttons disabled

**Next:** TurnStart (automatic)

---

### 3.2 Drawing Phase (DRAWING)
**Trigger:** Your turn begins  
**Duration:** Timed (until you draw)  
**Player State:** `Phase.DRAWING`  
**Active Player:** Only active player can interact

**Display:**
- Active player (you): highlighted glow on Your Cards Zone border
- Deck highlighted with glow/border
- Discard Pile highlighted with glow/border
- Phase banner: "Your Turn — Choose Deck or Discard"
- Timer visible

**Interactable Elements:**
- **Deck** (click to draw blind) → fires `CARD_DRAWN` (source: deck) → proceeds to Action phase
- **Discard Pile top card** (click to take top) → fires `CARD_DRAWN` (source: discard) → proceeds to Action phase

**Button Zone:** All disabled

**Non-Active Players:** Cannot interact. Only watching.

**Next:** Action phase

---

### 3.3 Action Phase (AWAITING_ACTION)
**Trigger:** Card drawn  
**Duration:** Timed  
**Player State:** `Phase.AWAITING_ACTION`  
**Active Player:** Only active player can interact

**Display:**
- Drawn card visible at Peek Area (face-up to you only)
- "From Deck" or "From Discard" badge on drawn card
- Your Cards Zone highlighted with glow/border
- Discard Pile highlighted with glow/border

#### If drawn from Deck:
**Interactable Elements (Select Card):**
- **Discard Pile** (click to discard immediate)
  - Tooltip: **"DISCARD IMMEDIATE"**
  - If card rank ∈ {7,8,9,10,J,Q}: **"POWER: [Name] – [Effect]"** (multi-line tooltip)
  - Fires `ACTION_TAKEN` (action: discard_immediate)
  - Proceeds to Rank Check → Spell Invocation (if power present) or Quick Discard

- **Your Cards Zone** (click slot to swap)
  - Tooltip: **"SWAP one of your cards"**
  - Click slot → highlights slot
  - Fires `ACTION_TAKEN` (action: swap, target: slot_index)
  - Proceeds to Rank Check (no power trigger for swapped card)

#### If drawn from Discard:
**Interactable Elements (Select Card):**
- **Discard Pile** (click to pass back)
  - Tooltip: **"PASS BACK"**
  - Fires `ACTION_TAKEN` (action: pass_back)
  - Proceeds directly to Quick Discard

- **Your Cards Zone** (click slot to swap)
  - Tooltip: **"SWAP one of your cards"**
  - Click slot → highlights slot
  - Fires `ACTION_TAKEN` (action: swap, target: slot_index)
  - Proceeds directly to Quick Discard

**Button Zone:** 
- "SKIP / PASS" disabled (no skip during Action phase; all actions require a choice)

**Non-Active Players:** Cannot interact. Only watching.

**Next:** Rank Check → Spell Invocation or Quick Discard (routing phase, not player-facing)

---

### 3.4 Spell Invocation Phase (AWAITING_SPELL_INVOCATION)
**Trigger:** Card rank ∈ {7,8,9,10,J,Q} and discarded immediately  
**Duration:** Timed  
**Player State:** `Phase.AWAITING_SPELL_INVOCATION`  
**Active Player:** Only active player can interact

**Display:**
- Phase banner: **"SPELL INVOCATION"**
- Discarded card visible at Peek Area (face-up)
- Tooltips panel shows spell description
- Elements highlighted per spell type (see below)

#### GLANCE (7 or 8):
**Interactable Elements (Select Card):**
- **Your Cards Zone** (click slot to peek)
  - Tooltip: **"GLANCE – View one of your own slots"**
  - Click slot → peek animation (brief reveal), card returns face-down
  - Memory updated internally
  - Fires `SPELL_INVOCATION_DECISION` (invoked: glance)
  - Proceeds to Quick Discard

**Button Zone:**
- "SKIP / PASS" enabled
  - Tooltip: **"Decline Spell"**
  - Fires `SPELL_INVOCATION_DECISION` (invoked: false)
  - Proceeds to Quick Discard

#### SPY (9 or 10):
**Interactable Elements (Select Card):**
- **Opponent Cards Zones** (click slot to peek)
  - Tooltip: **"SPY – View one opponent's slot"**
  - Click slot → peek animation (reveal to you only at Peek Area), card returns face-down
  - Opponent sees the animation but not the value
  - Eye icon badge added to that slot (visible to you, indicates you've peeked)
  - Fires `SPELL_INVOCATION_DECISION` (invoked: spy)
  - Proceeds to Quick Discard

**Button Zone:**
- "SKIP / PASS" enabled
  - Tooltip: **"Decline Spell"**
  - Fires `SPELL_INVOCATION_DECISION` (invoked: false)
  - Proceeds to Quick Discard

#### SMUGGLE (J):
**Interactable Elements (Select Card, two-step):**
- **Your Cards Zone + All Opponent Cards Zones** (highlighted)
  - Tooltip: **"SMUGGLE – Click your card, then opponent's card to blind-swap"**
  - Step 1: Click Your Cards slot → slot highlights distinctly (pulsing border)
  - Step 2: Click Opponent Cards slot → confirms swap
  - Swap executes immediately (no confirmation modal)
  - Slots animate to exchange positions
  - Knowledge follows cards (if you knew a card, you still know it at new location)
  - Fires `SPELL_INVOCATION_DECISION` (invoked: smuggle), then `SPELL_SWAP_DECISION`
  - Proceeds to Quick Discard

**Button Zone:**
- "SKIP / PASS" enabled (cancels if both slots not yet selected)
  - Tooltip: **"Decline Spell"**
  - Fires `SPELL_INVOCATION_DECISION` (invoked: false)
  - Proceeds to Quick Discard

#### DECREE (Q):
**Interactable Elements (Select Card, two-stage):**

**Stage 1 – Peek:**
- **Opponent Cards Zones** (click slot to peek)
  - Tooltip: **"DECREE – Click opponent's card to view"**
  - Click slot → peek animation (reveal to you only at Peek Area), card returns face-down
  - Decree icon badge added to that slot (visible to you)

**Stage 2 – Swap Decision:**
- **Your Cards Zone** (click to swap or pass)
  - Tooltip updates: **"SWAP – Click your card to exchange"**
  - Click Your Cards slot → swap executes (no confirmation)
  - Slots animate to exchange positions
  - Fires `SPELL_REVEALED`, then `SPELL_SWAP_DECISION` (swap)
  - Proceeds to Quick Discard

**Button Zone:**
- "SKIP / PASS" enabled (declines swap, keeps cards as-is)
  - Tooltip: **"Decline Swap"**
  - Fires `SPELL_REVEALED`, then `SPELL_SWAP_DECISION` (decline)
  - Proceeds to Quick Discard

**Non-Active Players:** Cannot interact. Watching spell resolution.

**Next:** Quick Discard window (automatic)

---

### 3.5 Quick Discard Window (AWAITING_QUICK_DISCARD)
**Trigger:** Action + Spell flow complete, OR after pass-back from discard  
**Duration:** Timed (shared across all players in this window)  
**Player State:** `Phase.AWAITING_QUICK_DISCARD`  
**Active Players:** ALL players can interact simultaneously

**Display:**
- Phase banner: **"QUICK DISCARD WINDOW"**
- Discard Pile top card prominently displayed
- Discard rank clearly visible (e.g., "Rank: 7♠")
- All players' Your Cards Zones visible
- Only slots matching discard rank are **highlighted/glowing**
- Disabled state: Slots you don't know the rank of are greyed out
- Timer visible (shared for all players)

**Interactable Elements (Select Card):**
- **Your Cards Zone** (click slot with matching known rank)
  - Tooltip: **"QUICK DISCARD – Click matching card"**
  - Only enabled if rank matches AND you know the card's rank
  - Click → card slides from hand to discard pile
  - Fires `QUICK_DISCARD_PLAYED`
  - Hand count updates live
  - If hand reaches 0 → `HAND_EMPTIED` fires → Round Over (immediate, no Trial)

**Button Zone:** All disabled (only quick-discard action available)

**Non-Active Players During Turn:** Can now interact (quick discard is simultaneous)

**Next:** 
- If any hand emptied: Round Over
- Otherwise: Trial Call Window

---

### 3.6 Trial Call Window (AWAITING_CALL_WINDOW)
**Trigger:** Quick Discard window closes, hands remain, no Trial phase skipped  
**Duration:** Timed (shared across all players)  
**Player State:** `Phase.AWAITING_CALL_WINDOW`  
**Active Players:** ALL players can interact simultaneously

**Display:**
- Phase banner: **"TESTIMONY WINDOW"**
- Tooltips panel: **"Do you claim to be eligible?"**
- Your eligibility status (color-coded known sum)
- Timer visible (countdown per player, synchronized)

**Interactable Elements:** None (card zones not interactive)

**Button Zone:**
- "TESTIMONY" enabled
  - Tooltip: **"Claim Eligibility (≤7)"**
  - Fires `TESTIMONY_GIVEN` (first-window)
  - Adds you to trial.first_window_callers
  - Button becomes disabled for you (you've acted)
  - Live display: "[Player] gave Testimony" or "[Player] passed"

- "SKIP / PASS" enabled (default if timer expires)
  - Fires `TESTIMONY_WINDOW_PASSED`
  - You skipped (didn't claim)

**Non-Active Players During Turn:** Can act (all players simultaneous)

**Next:** Verdict (automatic internal check)

---

### 3.7 Verdict & Perjury Resolution (internal, non-interactive)
**Trigger:** Call Window timer expires  
**Duration:** Instant  
**Player State:** (routing only)

**Display:** (automated, no player input)
- First-window callers checked: if true_sum > 7 → Perjury committed
- Perjured players marked; scored immediately (+25 + true_sum)
- Truly eligible list computed (first-window survivors + cross callers with ≤7)
- If truly_eligible count < 2 → Duel window skipped (proceed to Final Plea)
- Otherwise → Match Window

**Automatic routing:** Proceeds to Match Window or Final Plea Window

---

### 3.8 Match Window / Cross-Testimony (AWAITING_MATCH_WINDOW)
**Trigger:** Verdict resolves with ≥2 eligible survivors  
**Duration:** Timed (shared across all players)  
**Player State:** `Phase.AWAITING_MATCH_WINDOW`  
**Active Players:** Non-first-callers only (first-callers skip this)

**Display:**
- Phase banner: **"CROSS-TESTIMONY WINDOW"**
- Tooltips panel: Shows who gave first-window testimony, perjury results
- Read-only info: first-window callers' names, perjured players (if any)
- Your eligibility status
- Timer visible

**Interactable Elements:** None (card zones not interactive)

**Button Zone:**
- "TESTIMONY" enabled (if you didn't call first)
  - Tooltip: **"Call Cross-Testimony"**
  - Fires `TESTIMONY_GIVEN` (cross-window)
  - Adds you to trial.cross_callers
  - Button becomes disabled for you
  - Live display: "[Player] gave Cross-Testimony" or "[Player] passed"

- "SKIP / PASS" enabled (default if timer expires)
  - Fires `TESTIMONY_WINDOW_PASSED`
  - You passed

- (First-window callers have all buttons disabled; they wait)

**Non-Active Players During Turn:** Can act (all players simultaneous)

**Next:** Duel Window Check → automatic routing

---

### 3.9 Duel Window (AWAITING_DUEL_WINDOW)
**Trigger:** ≥2 truly-eligible Testimony-givers exist after Match Window  
**Duration:** Timed (shared across all Testimony-givers)  
**Player State:** `Phase.AWAITING_DUEL_WINDOW`  
**Active Players:** All Testimony-givers (first or cross callers who are ≤7)

**Display:**
- Phase banner: **"DUEL WINDOW"**
- Tooltips panel: **"Do you challenge the Testimony?"**
- Read-only info: current truly-eligible callers, last perjury status
- Timer visible

**Interactable Elements:** None (card zones not interactive)

**Button Zone:**
- "CHALLENGE" enabled (if you are a Testimony-giver)
  - Tooltip: **"Challenge"**
  - Fires `CHALLENGE_GIVEN`
  - Marks you as challenger
  - Button becomes disabled for you
  - Live display: "[Player] challenged" or "[Player] passed"

- "SKIP / PASS" enabled (default if timer expires)
  - Fires `CHALLENGE_WINDOW_PASSED`
  - You didn't challenge

- (Non-Testimony-givers have all buttons disabled; they wait)

**Non-Active Players During Turn:** Can act if Testimony-givers (simultaneous)

**Resolution (automatic):**
- If 0 challenges: All truly-eligible givers score 0 (Plain Agreement)
- If ≥1 challenge: Duel occurs
  - Lowest hand sum among challengers wins 0 points
  - All others +50 points
  - Fires `DUEL_RESOLVED`

**Next:** Final Plea Window

---

### 3.10 Final Plea Window (AWAITING_FINAL_PLEA_WINDOW)
**Trigger:** Duel resolves (or skipped)  
**Duration:** Timed (shared across all players)  
**Player State:** `Phase.AWAITING_FINAL_PLEA_WINDOW`  
**Active Players:** Eligible bystanders only (non-Testimony-givers, non-Perjured)

**Display:**
- Phase banner: **"FINAL PLEA"**
- Tooltips panel: Shows perjury status, duel outcome (if applicable)
- Read-only info:
  - Your true sum
  - Plea cap: +25 vs. your true sum (numeric comparison: e.g., "25 vs 18")
  - Perjury occurred this round (yes/no)
- Timer visible

**Interactable Elements:** None (card zones not interactive)

**Button Zone:**
- "PLEA" enabled (if you are an eligible bystander)
  - Tooltip: **"Take Plea (cap +25)"**
  - Fires `PLEA_TAKEN`
  - Score += 25 (Renaissance-ineligible)
  - Button becomes disabled for you
  - Live display: "[Player] took Plea" or "[Player] declined"

- "SKIP / PASS" enabled (decline plea, take true sum)
  - Tooltip: **"Decline Plea (true sum)"**
  - Fires `PLEA_DECLINED`
  - Score += true_sum (Renaissance-eligible if no Perjury)

- (Testimony-givers and Perjured players have all buttons disabled; they wait)

**Non-Active Players During Turn:** Can act if eligible bystanders (simultaneous)

**Next:** Scoring Trial (automatic, all outcomes computed)

---

### 3.11 Round Over (ROUND_OVER)
**Trigger:** Trial concluded, scores updated  
**Duration:** Display only (no player input, auto-advance after 3–5 seconds or click)  
**Player State:** `Phase.ROUND_OVER`

**Display:**
- Phase banner: **"ROUND OVER"**
- **Round Scoring Summary (centered):**
  - Each player's outcome (Perjury / Duel win / Plain Agreement / Plea / Bystander / etc.)
  - Points gained this round
  - Updated cumulative score
  - Renaissance triggered? (highlighted in sparkle animation if yes)
- **Standings Panel (right) updates live**

**Interactable Elements:** None

**Button Zone:** All disabled

**Auto-advance:** After 3–5 seconds OR click anywhere on screen → check Game Over condition

**Next:**
- If any score ≥120: Game Over
- Otherwise: New Round (deal hands → Initial Glance)

---

### 3.12 Game Over (GAME_OVER)
**Trigger:** Any player reaches ≥120 points  
**Duration:** Final display (no timer)  
**Player State:** `Phase.GAME_OVER`

**Display:**
- Phase banner: **"GAME OVER"**
- **Final Standings (center, large):**
  - Ranked list (1st, 2nd, 3rd, etc.)
  - Each player's final score
  - 1st place highlighted (gold, sparkle effect)

**Interactable Elements:** None (display-only)

**Button Zone:** All disabled

**Buttons available:**
- "Return to Lobby"
- "Play Again" (optional, creates new game)

**Next:** Home Menu

---

## SECTION 4: KNOWLEDGE TRACKING & MEMORY INDICATORS

### 4.1 Card Rank Badge (Your Knowledge)
**When displayed:**
- Small visual badge above card slot (e.g., "7♠")
- Shows rank and suit of card you have knowledge of

**Knowledge sources:**
- You drew the card from discard pile
- You Spied on opponent's card
- You peeked opponent's card via Decree (regardless of swap outcome)
- Knowledge retained from earlier swaps (if you knew a card before swap, you still know it)

**Persistence:**
- Badge persists entire round
- On swap: badge moves with the card to new location/owner (knowledge follows card identity, not slot)
- **On hover:** See tooltip showing "Spied by: [You]" or "Decreed (no swap): [You]" or "Drawn from discard: [You]"

### 4.2 Opponent Awareness Highlight (Red Eye)
**Visual indicator:** Subtle red tint or "eye" icon on your card slot

**When displayed:**
- Applied to your card slots if opponent has knowledge of your card
- Reasons opponent knows:
  - Drew your card from discard (they took it to their hand)
  - Spied on your slot
  - Peeked your slot via Decree (swap or no swap)

**Persistence:**
- Persists entire round
- Visible to you only (helps you plan strategy)
- On swap: indicator moves with card (opponent's knowledge follows your card)

**On hover:** See tooltip showing "Known by: [Opponent names, comma-separated]"

### 4.3 Knowledge Persistence
- Knowledge is tied to **card identity**, not slot position
- When Smuggle/Decree swap occurs, knowledge moves with the card
- Example: You Spy opponent A's slot 2 (King). Smuggle swaps slot 2 with opponent B's slot 1. You now see the King badge at opponent B's zone (new slot position), still marked as Spied by you. Opponent A's slot 2 now shows the card that was at opponent B's slot 1.

### 4.4 No Icon for Decree Swap Completion
- Decree peek does **not** add a persistent icon if swap is executed
- Reason: Once swapped, the card becomes yours—no need for special marking
- If Decree swap is **declined**, card remains at opponent's slot → Decree icon persists (indicates you've seen it but didn't swap)

---

## SECTION 5: TIMER & VISUAL FEEDBACK

### 5.1 Timer Display
- **Location:** Top-right of phase banner
- **Format:** Countdown in seconds (MM:SS if ≥1 minute, otherwise SS)
- **Color progression:** Green (0–66%) → Yellow (33–66%) → Red (0–33%)
- **Pulsing animation:** Red state pulses as urgency increases

### 5.2 Auto-Actions on Timeout
- **Draw phase timeout:** No default (turn hangs until player acts or disconnects)
- **Action phase timeout:** Discard immediate (if from deck) or pass back (if from discard)
- **Spell phase timeout:** SKIP spell
- **Trial windows timeout:** Pass (skip button action)
- **Plea timeout:** Decline plea

### 5.3 Waiting Info
- Non-active players see passive info: "Waiting for [Player] to [phase]..."
- Reduced interactivity during non-active turns (Quick Discard and Trial windows exception)

---

## SECTION 6: SUMMARY TABLE — PHASE, INTERACTIVITY & FALLBACKS

| Phase | State | Active Players | Pressable Buttons | Card Zones Clickable | **Fallback (timeout)** | Next |
|---|---|---|---|---|---|---|
| Initial Glance | `TURN_START` | N/A | None | No | N/A (automatic) | TurnStart |
| Drawing | `DRAWING` | Active player | None | No | **Draw from Discard** | Action |
| Action | `AWAITING_ACTION` | Active player | None | YES (Select Card) | **If from deck: Discard Immediate** / **If from discard: Pass Back** | Rank Check → Spell or Quick Discard |
| Spell Invocation | `AWAITING_SPELL_INVOCATION` | Active player | SKIP | YES (Select Card, power-specific) | **SKIP** (decline spell) | Quick Discard |
| — Glance | (sub-phase) | Active player | SKIP | YES (Your Cards) | **SKIP** | → Quick Discard |
| — Spy | (sub-phase) | Active player | SKIP | YES (Opponent Cards) | **SKIP** | → Quick Discard |
| — Smuggle | (sub-phase) | Active player | SKIP | YES (Your + Opponent Cards) | **SKIP** (if both slots not selected) | → Quick Discard |
| — Decree (Peek) | (sub-phase) | Active player | SKIP | YES (Opponent Cards) | **SKIP** | → Decree (Swap Decision) |
| — Decree (Swap) | (sub-phase) | Active player | SKIP | YES (Your Cards) | **SKIP** (decline swap) | → Quick Discard |
| Quick Discard | `AWAITING_QUICK_DISCARD` | All players | None | YES (matching known ranks) | **SKIP** (pass quick discard) | Trial Call or Round Over |
| Trial Call | `AWAITING_CALL_WINDOW` | All players | TESTIMONY, SKIP | No | **SKIP** (pass testimony) | Verdict → Match or Final Plea |
| Match Window | `AWAITING_MATCH_WINDOW` | Non-first-callers | TESTIMONY, SKIP | No | **SKIP** (pass testimony) | Duel Check → Duel or Final Plea |
| Duel Window | `AWAITING_DUEL_WINDOW` | Testimony-givers | CHALLENGE, SKIP | No | **SKIP** (no challenge) | Final Plea |
| Final Plea | `AWAITING_FINAL_PLEA_WINDOW` | Bystanders | PLEA, SKIP | No | **SKIP** (decline plea, take true sum) | Scoring → Round Over |
| Round Over | `ROUND_OVER` | N/A | None | No | N/A (auto-advance) | Game Check → New Round or Game Over |
| Game Over | `GAME_OVER` | N/A | Menu buttons | No | N/A | Home Menu |

---

## SECTION 7: FALLBACK SCENARIOS (Timer Expiration)

**Philosophy:** When time expires, fallback actions skip toward end of turn while minimizing impact on other players.

### Fallback Behaviors by Phase

| Phase | Timeout Action | Outcome |
|---|---|---|
| **Drawing** | Draw from Discard | Immediately draws top discard card |
| **Action (from deck)** | Discard Immediate | Drawn card returned to discard pile |
| **Action (from discard)** | Pass Back | Drawn card returned to discard pile |
| **Glance** | Skip | Spell declined|
| **Spy** | Skip | Spell declined|
| **Smuggle** | Skip | Spell declined (if both slots not selected)|
| **Decree (Peek)** | Skip | Spell declined |
| **Decree (Swap Decision)** | Skip | Swap declined (card stays at opponent)|
| **Quick Discard** | Skip | Player passes quick discard, hand size unchanged |
| **Trial Call Window** | Skip | Player passes testimony, not added to first-window callers |
| **Match Window** | Skip | Player passes cross-testimony, not added to cross-window callers |
| **Duel Window** | Skip | Player doesn't challenge, marked as passed |
| **Final Plea Window** | Skip | Player declines plea, scores true sum (Renaissance-eligible if no Perjury) |

**Fallback Design Goals:**
1. **Turn completion:** Skipping accelerates turn end without hanging game
2. **Fair defaults:** Conservative choices (passing, declining) reduce impact on other players
3. **Strategy-neutral:** Vets testing can adjust strategy around known fallbacks

---

## SECTION 8: NON-INTERACTIVE PHASES (Automatic Routing)

### Initial Glance Setup (post-NewRound, pre-TurnStart)
- Internal: Automated hand reveal animation (2 slots per player, visual only)
- Knowledge updates internally (you see your cards)
- Proceeds to first player's turn

### Rank Check (post-Action)
- Internal routing: if discarded card rank is power (7–Q), go to Spell Invocation; else Quick Discard

### Verdict (post-Call-Window)
- Internal: Check first-window callers for Perjury (true_sum > 7)
- Gate Duel on ≥2 truly-eligible survivors
- Route to Match Window or Final Plea

### Duel Execution (post-Challenge-Window)
- Internal: Compare hand sums among challengers
- Determine winners (0 points) and others (+50)
- Automatic scoring

### Scoring Trial (post-Plea-Window)
- Internal: Compute all final outcomes
- Update scores
- Check Renaissance conditions
- Route to Round Over

---

## SECTION 9: RECONNECTION UI

**Scenario:** Player disconnects during an active phase

**Display:**
- Grey overlay on that player's cards zone
- Status badge: "[Player Name] Reconnecting..."
- If timer expires before reconnection: auto-default action fires

**Reconnection:**
- When player reconnects: overlay clears, status updates: "[Player Name] Reconnected"
- Game state synced to reconnected player
- Play resumes

**Connection Loss During Trial:**
- Player is locked out of button interaction (buttons disabled)
- If timeout: default action fires (e.g., pass on Testimony, decline Plea)
- Reconnection restores state view only (no replay of missed action)

---

## SECTION 10: MVP IMPLEMENTATION CHECKLIST

### Phase 1 (Core MVP):
- [x] Login / Lobby screens
- [x] Base table layout (all zones, panels)
- [x] Drawing phase
- [x] Action phase (Discard Immediate, Swap, Pass Back)
- [x] Spell Invocation phase (all 4 powers: Glance, Spy, Smuggle, Decree)
- [x] Quick Discard window
- [x] Trial windows (Call, Match, Duel, Plea)
- [x] Round Over summary
- [x] Game Over screen
- [x] Phase banner + timer
- [x] Standings panel (live-updating)
- [x] Button zone (SKIP, TESTIMONY, CHALLENGE, PLEA)
- [x] Memory indicators (rank badges, Spy/Decree icons)
- [x] Known sum color-coding (green ≤7, red >7)

### Phase 2 (Polish):
- [ ] Spell swap animations (visual flourish)
- [ ] Renaissance celebration animation
- [ ] Perjury highlighting in outcomes
- [ ] Disconnect handling + reconnection UI
- [ ] Event log (optional, scrollable history)
- [ ] Last-turn alert styling
- [ ] Mobile responsiveness (if needed)

### Phase 3 (Future):
- [ ] Spectator mode
- [ ] Game replay / history
- [ ] Advanced timer customization
- [ ] Accessibility (colorblind mode, high-contrast)

---

## SECTION 11: EDGE CASES

### E1: Hand reaches 0 during Quick Discard
- Round ends immediately, that player scores 0
- All others score as bystanders (no Trial)
- Event: `HAND_EMPTIED` fires

### E2: Nobody gives Testimony on last turn
- Round ends, all score as bystanders
- Event: `TESTIMONY_WINDOW_PASSED` (all)

### E3: Only 1 Testimony given
- Duel window skipped (need ≥2 eligible)
- Testimony-giver scores 0 (no Challenge possible)
- Others proceed to Final Plea

### E4: False cross-testimony
- Cannot commit Perjury (only first-window callers can)
- Scores +25 flat (no Renaissance eligibility)
- Excluded from Final Plea

### E5: Multiple Renaissance in one game
- Possible, one per round per player
- Example: 50 → 25 in round 1; later 75 (true sum) in round 2 → 100 total → reset to 50

### E6: Eligible player reaches exactly 50 with +0 result
- No Renaissance (only fresh upward additions trigger it)

---

## SECTION 12: DESIGN NOTES

### Colors & Highlights
- **Interactable zones:** Subtle glow/border (not overwhelming)
- **Active selection:** Pulsing or lighter border
- **Disabled state:** Greyed out (60% opacity)
- **Known sum display:** Green (#4caf50 or similar) if ≤7, Red (#f44336 or similar) if >7
- **Renaissance animation:** Sparkle effect, 2–3 second duration

### Typography
- **Phase banner:** Large, bold (36–48px)
- **Player names:** Medium (18–24px)
- **Button text:** Bold (16–18px)
- **Card badges:** Small (12–14px)
- **Tooltips:** Regular (14–16px)

### Animation Timings
- **Peek animations:** 500ms reveal, 300ms fade back
- **Card slide animations:** 400ms smooth transition
- **Renaissance sparkle:** 2–3 seconds
- **Phase transitions:** 200–300ms fade

---

**END OF SPECIFICATION v2**