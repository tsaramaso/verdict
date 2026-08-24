# Verdict — Gameplay UI Specification

## 1. Core Concepts

### Phases

The game progresses through a sequence of **Phase** states. Only certain phases accept player input; others advance automatically.

**Player-input phases:**
- `TURN_START` — Initial Glance display (automatic, but synchronized across players)
- `DRAWING` — Active player chooses draw source
- `AWAITING_ACTION` — Active player acts on drawn card
- `AWAITING_SPELL_INVOCATION` — Active player invokes spell power (if applicable)
- `AWAITING_SPELL_SWAP_DECISION` — Active player chooses Decree swap (if applicable)
- `AWAITING_QUICK_DISCARD` — All eligible players may quick-discard
- `AWAITING_CALL_WINDOW` — All players give or pass [Testimony](#testimony)
- `AWAITING_MATCH_WINDOW` — Non-first-callers give late [Testimony](#testimony)
- `AWAITING_DUEL_WINDOW` — [Testimony](#testimony)-givers [Challenge](#challenge) or pass
- `AWAITING_FINAL_PLEA_WINDOW` — [Bystanders](#bystander) take or decline [Plea](#plea)
- `ROUND_OVER` — Automatic scoring and [Renaissance](#renaissance) check
- `GAME_OVER` — Game concluded, winner display

### Active Player

**Definition:** The player whose turn it is.

Only the active player can interact with drawing, action, and spell phases. Their slot or card zone displays a persistent highlight (glow/border) during their turn.

### Trial Windows

**Definition:** Phases from [Call Window](#awaiting_call_window) through [Final Plea Window](#awaiting_final_plea_window).

During trial windows, **all eligible players act simultaneously** (not turn-based). Eligible differs per window:
- Call Window: all players
- Match Window: players who passed Call Window
- Duel Window: [Testimony](#testimony)-givers only
- Final Plea Window: [Bystanders](#bystander) only

### Revealed & Exposed

See [Section 5](#5-revealed--exposed-rendering).

---

## 2. Phase Flow & Interactivity

### 2.1 TURN_START (Initial Glance)

**Trigger:** Start of each round (after dealing, before first turn).

**Duration:** Brief, automatic. Player views first two card slots momentarily, then returns to face-down.

**Display:**
- All players' Your Cards zones visible
- Visual reveal animation on slots 0–1 (cosmetic only, cards show briefly then face-down)
- No interaction required

**Interactable Elements:** None

**Button Zone:** All buttons disabled

**Knowledge Updated:** Each player's slots 0–1 marked [Revealed](#revealed) internally.

**Next Phase:** First active player begins `DRAWING`

---

### 2.2 DRAWING (Your Turn Begins)

**Trigger:** Your position in turn order reaches you, or previous turn ended.

**Active Player Only:** Only the active player can interact.

**Display:**
- Phase banner: "Your Turn — Choose Deck or Discard"
- Deck zone highlighted with glow/border, labeled clickable
- Discard Pile top card visible, highlighted with glow/border, labeled clickable
- Timer visible above active player's cards
- Your Cards zone has persistent glow indicating you're active

**Interactable Elements:**
- **Deck** (click to draw blind)
  - Fires action: draw from deck
  - Proceeds to `AWAITING_ACTION`

- **Discard Pile top card** (click to take face-up)
  - Only available if discard pile has cards (not first turn of round)
  - Fires action: take from discard
  - Proceeds to `AWAITING_ACTION`

**Non-Active Players:** Cannot interact. Display passive status: "Waiting for [Active Player] to draw..."

**Timeout Action:** Draw from discard (see [Section 7](#7-timeout-behavior))

**Next Phase:** `AWAITING_ACTION`

---

### 2.3 AWAITING_ACTION (Respond to Drawn Card)

**Trigger:** Card has been drawn (source: deck or discard).

**Active Player Only:** Only the active player can interact.

**Display:**
- Phase banner: "Your Drawn Card — Choose Action"
- Drawn card visible at Peek Area (face-up to you only; others see back/placeholder)
- Badge on Peek Area: "From Deck" or "From Discard"
- If power card (rank 7–Q and from deck): spell name and brief effect tooltip
- Your Cards zone highlighted with glow/border (selectable for swap)
- Discard Pile highlighted with glow/border (for discard)
- Timer visible

**If drawn from Deck, two choices:**

1. **Discard Immediate** (click Discard Pile)
   - Card placed face-up on discard pile
   - Fires action: discard_immediate
   - Routes to Rank Check (see [Section 8](#8-automatic-routing-phases))
   - If card is power (7–Q): proceeds to `AWAITING_SPELL_INVOCATION`
   - Otherwise: proceeds to `AWAITING_QUICK_DISCARD`

2. **Swap** (click one of Your Cards slots)
   - Click slot to target it (visual selection/highlight)
   - Drawn card enters that slot, replaced card discarded face-up
   - Fires action: swap, target slot_index
   - Power card never triggers on swap
   - Proceeds directly to `AWAITING_QUICK_DISCARD`

**If drawn from Discard, two choices:**

1. **Pass Back** (click Discard Pile)
   - Card returned to discard pile top
   - Fires action: pass_back
   - Your hand unchanged
   - Proceeds directly to `AWAITING_QUICK_DISCARD`

2. **Swap** (click one of Your Cards slots)
   - Same as deck swap (see above)
   - Proceeds directly to `AWAITING_QUICK_DISCARD`

**Non-Active Players:** Cannot interact. Watch and wait.

**Timeout Action:** If from deck: discard immediate. If from discard: pass back (see [Section 7](#7-timeout-behavior))

**Next Phase:** Rank Check (automatic routing) → `AWAITING_SPELL_INVOCATION` or `AWAITING_QUICK_DISCARD`

---

### 2.4 AWAITING_SPELL_INVOCATION (Invoke Power)

**Trigger:** Active player discarded immediately from deck AND card rank ∈ {7, 8, 9, 10, J, Q}.

**Active Player Only:** Only the active player can invoke.

**Display:**
- Phase banner: "SPELL INVOCATION — [Spell Name]"
- Discarded card visible at Peek Area (face-up)
- Spell description in tooltip area
- Button Zone: "SKIP" enabled (decline spell)
- Interactable zones highlighted per spell type (see below)
- Timer visible

**Spell Invocation Options:**

#### Glance (Rank 7 or 8)

**Effect:** View one of your own hand slots.

**Interactable:** Your Cards zone slots

**Interaction:** Click a slot to peek at it (brief reveal animation, card returns face-down). If already [Revealed](#revealed) to you, no new information. Fires action: invoke glance, target slot.

**Timeout Action:** Skip spell (see [Section 7](#7-timeout-behavior))

**Next Phase:** `AWAITING_QUICK_DISCARD`

#### Spy (Rank 9 or 10)

**Effect:** View one opponent's hand slot.

**Interactable:** Opponent Cards zones (all slots of one opponent selectable)

**Interaction:** Click an opponent's slot to peek (brief reveal animation to you only; opponent sees animation but not card value). Your display updates: slot marked with eye icon (you peeked it). Fires action: invoke spy, target player, target slot.

**Knowledge Updated:** Opponent's slot becomes [Revealed](#revealed) to you. Opponent's slot becomes [Exposed](#exposed) to you (eye icon appears in your view).

**Timeout Action:** Skip spell

**Next Phase:** `AWAITING_QUICK_DISCARD`

#### Smuggle (Jack)

**Effect:** Blind-swap one of your cards with one of an opponent's cards by slot position.

**Interactable:** Your Cards zone and one Opponent Cards zone (must select both)

**Interaction:** 
1. Click one of Your Cards slots (visual selection highlight)
2. Click one of an Opponent's slots (completes selection)
3. Swap executes immediately (no values shown to either player)
4. Fires action: invoke smuggle, own slot, target player, target slot

**Knowledge Tracking:** Card object (with its `known_by` set) moves to new slot. If you knew your card, opponent still doesn't know it at new location (unless they previously knew it). If opponent's card came to you, you still don't know it unless you knew it before.

**UI Update:** After swap, both players' hands rerender with updated card positions.

**Timeout Action:** Skip spell (if both slots not selected)

**Next Phase:** `AWAITING_QUICK_DISCARD`

**Special:** "SKIP" button cancels Smuggle at any time (no selection executed).

#### Decree (Queen)

**Effect:** View one opponent's slot, then optionally swap it with one of your own.

**Interactable:** Opponent Cards zones for peek, then Your Cards zone for swap decision

**Interaction:**

**Peek Stage:**
1. Click an Opponent's slot to peek (brief reveal animation to you only)
2. Slot marked with eye icon in your display
3. Fires action: invoke decree, target player, target slot (peek only)

**Swap Decision Stage:**
- Two choices now available:

  - **Swap** (click one of Your Cards slots)
    - Opponent's peeked card enters your selected slot
    - Your card enters opponent's original slot
    - Fires action: decree swap, own slot (true)
    
    **Knowledge Tracking:**
    - Card you receive: marked [Revealed](#revealed) to you (you now know its value)
    - Card you give: if you already knew your card, it becomes [Exposed](#exposed) at opponent's new slot (eye icon marks it). If you didn't know your card, no [Exposed](#exposed) marking at opponent's slot.

  - **No Swap** (click "SKIP" or timeout)
    - Cards stay in place
    - Opponent's peeked slot remains marked with eye icon (you have [Revealed](#revealed) knowledge of it)
    - Opponent knows you peeked their slot (they see eye icon on their end)
    - Fires action: decree swap, own slot (false)

**Timeout Action:** Skip spell (no peek occurs) or decline swap after peek (see [Section 7](#7-timeout-behavior))

**Next Phase:** If swap chosen: `AWAITING_QUICK_DISCARD`. If no swap or skip: `AWAITING_QUICK_DISCARD`.

**Special:** "SKIP" button cancels entire Decree (no peek executes). After peek, swap decision is separate.

---

### 2.5 AWAITING_QUICK_DISCARD (Matching Ranks)

**Trigger:** After Action phase resolves (card landed on discard pile), after spell invocation (or skip).

**All Eligible Players:** Any player may quick-discard a matching rank. Not turn-based; all simultaneous.

**Display:**
- Phase banner: "QUICK DISCARD — Match the Rank [Rank]"
- Most recent discard visible at Discard Pile
- Your Cards zone highlighted (slots with matching rank selectable)
- Opponent Cards zones visible (greyed out, non-interactive for you)
- Timer visible (optional, or can auto-advance after short duration)

**Interactable Elements:**
- **Your Cards zone**: Click any slot holding a card of matching rank
  - Card moves to discard pile
  - Slot becomes empty (marked None, no longer selectable)
  - Your hand size decreases by 1
  - Fires action: quick_discard, own slot

**All Players:** Action fires immediately when clicked; no confirmation.

**Hand Empty Check:** If your hand reaches zero cards during quick-discard, round ends immediately (see [Section 8](#8-automatic-routing-phases), Edge Case E1).

**Timeout Action:** Pass (don't quick-discard)

**Next Phase:** All players finished → Trial Call Window OR Round Over (if hand emptied or last turn with no testimony)

---

### 2.6 AWAITING_CALL_WINDOW (First Testimony Window)

**Trigger:** After quick-discard window closes (or during last turn if deck exhausted and quick-discard passed).

**All Players Simultaneous:** All players act at the same time. Not turn-based.

**Display:**
- Phase banner: "TRIAL BEGINS — First Testimony Window"
- All players see their own Button Zone
- Button Zone: "TESTIMONY" and "SKIP" both enabled
- Leaderboard visible
- Timer visible

**Interactable Elements:**
- **Button Zone: TESTIMONY**
  - Click to claim "I am [Eligible](#eligible)"
  - First player to press starts a brief window (~2 seconds)
  - All players pressing within this window are **first-window callers**
  - Fires action: testimony_given, call_window
  - Your button becomes disabled after press (greyed out)

- **Button Zone: SKIP**
  - Click to pass (do not give [Testimony](#testimony))
  - Marked as "passed first"
  - Button disabled after press

**Eligibility for Button:** All players can press (no restrictions)

**Timeout Action:** Pass (don't give testimony)

**Knowledge Updated:** First-window callers identified. Game prepares for Perjury Check.

**Special Rules:**
- If zero players give testimony:
  - If last turn: round ends immediately, all score as [Bystanders](#bystander)
  - Otherwise: trial skipped, proceed to next player's turn
- If ≥1 player gives testimony: proceed to Match Window

**Next Phase:** `AWAITING_MATCH_WINDOW`

---

### 2.7 AWAITING_MATCH_WINDOW (Late Testimony Window)

**Trigger:** After Call Window if ≥1 testimony given and players passed Call Window.

**Non-First-Callers Simultaneous:** Only players who passed Call Window can act here. All act simultaneously.

**Display:**
- Phase banner: "TRIAL CONTINUES — Late Testimony Window"
- Button Zone: "TESTIMONY" and "SKIP" both enabled
- Timer visible

**Interactable Elements:**
- **Button Zone: TESTIMONY**
  - Click to claim "I am [Eligible](#eligible)" late
  - Late testimony can never result in [Perjury](#perjury) (only first-window callers can perjure)
  - Fires action: testimony_given, match_window
  - Button disabled after press

- **Button Zone: SKIP**
  - Click to decline late testimony
  - Marked as "passed cross"
  - Button disabled after press

**Eligibility for Button:** Only players who passed Call Window see the button.

**First-Window Callers:** Their buttons remain disabled; they already decided.

**Timeout Action:** Pass (don't give testimony)

**Knowledge Updated:** Cross-window callers identified. Game proceeds to Perjury Check.

**Next Phase:** Perjury Check (automatic routing) → `AWAITING_DUEL_WINDOW` or `AWAITING_FINAL_PLEA_WINDOW`

---

### 2.8 Perjury Check (Automatic)

**Trigger:** After Match Window closes.

**Automatic Routing (No Player Input):**

Game validates all first-window callers. Any first-window caller with true hand sum > 7 has committed [Perjury](#perjury).

**Perjured players:**
- Removed from rest of trial
- Score: +25 + true hand sum (stacked), [Renaissance](#renaissance) ineligible
- Event broadcast to all players (they see who perjured)

**Survivors:** Truly-[Eligible](#eligible) [Testimony](#testimony)-givers (first or cross) remaining.

**Routing Decision:**
- If ≥2 truly-[Eligible](#eligible) survivors: proceed to `AWAITING_DUEL_WINDOW`
- Otherwise: skip Duel, proceed to `AWAITING_FINAL_PLEA_WINDOW`

**Next Phase:** `AWAITING_DUEL_WINDOW` or `AWAITING_FINAL_PLEA_WINDOW`

---

### 2.9 AWAITING_DUEL_WINDOW (Challenge Window)

**Trigger:** After Perjury Check if ≥2 truly-[Eligible](#eligible) callers remain.

**Testimony-Givers Simultaneous:** Only [Testimony](#testimony)-givers (first or cross, and not perjured) can press buttons. All act simultaneously.

**Display:**
- Phase banner: "TRIAL CONTINUES — Duel Window"
- Button Zone: "CHALLENGE" and "SKIP" both enabled
- Leaderboard visible
- Timer visible

**Interactable Elements:**
- **Button Zone: CHALLENGE**
  - Click to contest [Testimony](#testimony), forcing a [Duel](#duel)
  - Compares true hand sums of all [Testimony](#testimony)-givers
  - Fires action: challenge_given
  - Button disabled after press

- **Button Zone: SKIP**
  - Click to pass (accept [Testimony](#testimony), no challenge)
  - Marked as "passed challenge"
  - Button disabled after press

**Eligibility for Button:** Only [Testimony](#testimony)-givers (first-window or cross-window, not perjured) see buttons.

**Bystanders & Perjured Players:** Buttons disabled (greyed out).

**Timeout Action:** Pass (no challenge)

**Duel Execution (Automatic):**
- If zero challenges: all truly-[Eligible](#eligible) [Testimony](#testimony)-givers score +0 ([Plain Agreement](#plain-agreement))
- If ≥1 challenge: [Duel](#duel) occurs
  - Truly-[Eligible](#eligible) [Testimony](#testimony)-giver with **lowest true hand sum** scores +0
  - All others score +50
  - Ties: multiple players can win +0 (all tied for lowest)

**Next Phase:** `AWAITING_FINAL_PLEA_WINDOW`

---

### 2.10 AWAITING_FINAL_PLEA_WINDOW (Bystander Plea)

**Trigger:** After Duel Window (or if Duel Window skipped).

**Bystanders Simultaneous:** Only [Bystanders](#bystander) can act (players who never gave [Testimony](#testimony), first or cross, and not removed for [Perjury](#perjury)). All act simultaneously.

**Display:**
- Phase banner: "TRIAL CONCLUSION — Final Plea"
- Button Zone: "PLEA" and "SKIP" both enabled
- Leaderboard visible
- Timer visible

**Interactable Elements:**
- **Button Zone: PLEA**
  - Click to take plea: score +25 flat instead of true hand sum
  - May be better or worse than true sum (strategic decision)
  - Fires action: plea_taken
  - [Renaissance](#renaissance) ineligible if plea taken
  - Button disabled after press

- **Button Zone: SKIP**
  - Click to decline plea (score true hand sum)
  - Automatic if timeout occurs
  - [Renaissance](#renaissance) eligible if no [Perjury](#perjury) occurred this round
  - Button disabled after press

**Eligibility for Button:** Only [Bystanders](#bystander) see buttons.

**Non-Bystanders:** Buttons disabled (greyed out).

**Timeout Action:** Decline plea (automatic, score true hand sum, eligible for [Renaissance](#renaissance))

**Next Phase:** `ROUND_OVER` (automatic scoring)

---

### 2.11 ROUND_OVER (Scoring & Renaissance)

**Trigger:** After Final Plea Window or upon round end (hand empty, no testimony on last turn, etc.).

**Automatic Routing (No Player Input):**

All scores updated:
- [Perjury](#perjury) cases: +25 + true sum (stacked)
- [Duel](#duel) winners: +0
- [Duel](#duel) losers: +50
- [Bystanders](#bystander): true sum or +25 (if plea taken)
- [Plea](#plea) takers: +25 flat ([Renaissance](#renaissance) ineligible)
- False [Cross-Testimony](#cross-testimony): +25 flat ([Renaissance](#renaissance) ineligible)
- [Empty Hand](#empty-hand) player: +0

**Renaissance Check:** For each player, if score lands exactly on 50 or 100 via true [Bystander](#bystander) addition (not plea, not penalty), reset down one tier (50→25, 100→50).

**Display:**
- Round summary modal or screen showing:
  - Each player's round outcome (testimony given? challenged? score change?)
  - Current total scores
  - [Renaissance](#renaissance) triggered (if any) with visual marker
  - Next round button or "Game Over" if any player ≥120

**Timeout Action:** N/A (automatic)

**Game Check:**
- If any player score ≥120: proceed to `GAME_OVER`
- Otherwise: proceed to next round (new dealer, fresh deck, `TURN_START`)

**Next Phase:** `GAME_OVER` or new round `TURN_START`

---

### 2.12 GAME_OVER (Winner Display)

**Trigger:** After scoring, if any player score ≥120.

**Winner Determination:** Player with lowest final score wins (see [rules.md §2](rules.md#2-win-condition-game) for tiebreaker rules).

**Display:**
- Game Over modal or screen showing:
  - Final standings (rank, player name, score)
  - Winner highlighted or celebrated
  - Breakdown of round-by-round scores (optional)
  - "Return to Lobby" or "New Game" button

**Timeout Action:** N/A (automatic)

**Next Phase:** Lobby (out of scope for this doc)

---

## 3. Button Zone & Lock Rules

### Button Availability by Phase

| Phase | SKIP/PASS | TESTIMONY | CHALLENGE | PLEA |
|-------|-----------|-----------|-----------|------|
| TURN_START | ✗ | ✗ | ✗ | ✗ |
| DRAWING | ✗ | ✗ | ✗ | ✗ |
| AWAITING_ACTION | ✗ | ✗ | ✗ | ✗ |
| AWAITING_SPELL_INVOCATION | ✓ | ✗ | ✗ | ✗ |
| AWAITING_QUICK_DISCARD | ✓ | ✗ | ✗ | ✗ |
| AWAITING_CALL_WINDOW | ✓ | ✓ | ✗ | ✗ |
| AWAITING_MATCH_WINDOW | ✓* | ✓* | ✗ | ✗ |
| AWAITING_DUEL_WINDOW | ✓* | ✗ | ✓* | ✗ |
| AWAITING_FINAL_PLEA_WINDOW | ✓* | ✗ | ✗ | ✓* |
| ROUND_OVER | ✗ | ✗ | ✗ | ✗ |
| GAME_OVER | ✗ | ✗ | ✗ | ✗ |

**Legend:**
- ✓ = Button enabled for all eligible players
- ✓* = Button enabled only for eligible players in that phase (others greyed out)
- ✗ = Button disabled for all players

### Button Behavior Details

**SKIP/PASS:**
- **AWAITING_SPELL_INVOCATION:** Decline spell power (no invocation, card stays on discard)
- **AWAITING_QUICK_DISCARD:** Pass quick-discard (hand unchanged, no card discarded)
- **AWAITING_CALL_WINDOW:** Pass first-window testimony (marked as "passed first")
- **AWAITING_MATCH_WINDOW:** Pass late testimony (marked as "passed cross")
- **AWAITING_DUEL_WINDOW:** Pass challenge (accept testimony, no duel)
- **AWAITING_FINAL_PLEA_WINDOW:** Decline plea (score true sum, [Renaissance](#renaissance) eligible if no [Perjury](#perjury))

**TESTIMONY:**
- **AWAITING_CALL_WINDOW:** Claim "I am [Eligible](#eligible)" as first-window caller (subject to [Perjury](#perjury) if false and unchallenged)
- **AWAITING_MATCH_WINDOW:** Claim "I am [Eligible](#eligible)" as late caller (never subject to [Perjury](#perjury))

**CHALLENGE:**
- **AWAITING_DUEL_WINDOW:** Contest [Testimony](#testimony) of [Testimony](#testimony)-givers (force [Duel](#duel) comparison)

**PLEA:**
- **AWAITING_FINAL_PLEA_WINDOW:** Take +25 flat instead of true hand sum ([Renaissance](#renaissance) ineligible)

---

## 4. Zone Interactivity

### Your Cards Zone

**Your hand slots (4 fixed positions).**

**Interactivity by Phase:**

| Phase | Clickable | Action | Visual Feedback |
|-------|-----------|--------|---|
| TURN_START | No | — | Card back shown |
| DRAWING | No | — | — |
| AWAITING_ACTION | Yes* | Swap (if from deck) / Swap (if from discard) | Slot highlights on hover |
| AWAITING_SPELL_INVOCATION | Yes (Glance) | Peek own slot | Slot highlights on hover |
| AWAITING_SPELL_INVOCATION | Yes (Smuggle) | Select own slot for blind swap | Slot highlights on selection |
| AWAITING_SPELL_INVOCATION | Yes (Decree Swap) | Select own slot for swap decision | Slot highlights on hover |
| AWAITING_QUICK_DISCARD | Yes* | Quick-discard matching rank | Only matching rank slots selectable |
| Others | No | — | Greyed out or disabled appearance |

**Visual States:**
- **Default:** Card back with rank badge (if [Revealed](#revealed)), eye icon (if [Exposed](#exposed))
- **Hover (during clickable phase):** Subtle glow/border, cursor change
- **Selected (for Smuggle/Decree):** Pulsing border or highlight color
- **Disabled (non-clickable phase):** Greyed out appearance, no cursor change

**Opponent Knowledge Indicator:**
- Eye icon appears if any opponent knows this slot (see [Section 5](#5-revealed--exposed-rendering))
- Hover tooltip (optional): shows which opponents know this card

---

### Opponent Cards Zones

**Each opponent's 4 hand slots (displayed per opponent, rotated/positioned per player count).**

**Interactivity by Phase:**

| Phase | Clickable | Action | Who | Visual Feedback |
|-------|-----------|--------|-----|---|
| TURN_START | No | — | — | Card back shown |
| DRAWING | No | — | — | — |
| AWAITING_ACTION | No | — | — | — |
| AWAITING_SPELL_INVOCATION (Spy) | Yes | Peek opponent slot | Active player | Slot highlights on hover |
| AWAITING_SPELL_INVOCATION (Smuggle) | Yes | Select opponent slot for blind swap | Active player | Slot highlights on selection |
| AWAITING_SPELL_INVOCATION (Decree Peek) | Yes | Peek opponent slot | Active player | Slot highlights on hover |
| AWAITING_SPELL_INVOCATION (Decree Swap) | No* | — | — | Greyed out (peek already done) |
| Others | No | — | — | Greyed out or non-interactive |

**Visual States:**
- **Default:** Card back (face-down)
- **Hover (during clickable phase):** Subtle glow/border, cursor change
- **Known card (you've Spied/peeked it):** Rank badge shown (only you see it in your view)
- **Selected (for Smuggle):** Pulsing border or highlight color
- **Disabled (non-clickable):** Greyed out appearance

---

### Deck Zone

**Top card face-down, stack count displayed.**

**Interactivity by Phase:**

| Phase | Clickable | Action | Who | Outcome |
|-------|-----------|--------|-----|---------|
| DRAWING | Yes | Draw blind from deck | Active player | Card drawn, proceeds to ACTION |
| AWAITING_ACTION (as drawn source) | Yes | Discard immediate | Active player | Card to discard, routes to SPELL or QUICK_DISCARD |
| Others | No | — | — | — |

**Visual States:**
- **Default:** Card back with count label ("Deck: 35 cards")
- **Hover (DRAWING phase):** Glow/border highlight, cursor change
- **Disabled:** Greyed out appearance
- **Last card drawn:** "LAST TURN" alert fires (see [Section 6](#6-ui-helpers--displays))

---

### Discard Pile Zone

**Top card face-up (if pile has cards), stack count displayed.**

**Interactivity by Phase:**

| Phase | Clickable | Action | Who | Outcome |
|-------|-----------|--------|-----|---------|
| DRAWING | Yes (if pile ≠ empty) | Take top card face-up | Active player | Card taken, proceeds to ACTION |
| AWAITING_ACTION (from deck) | Yes | Discard immediate (target for discard) | Active player | Card discarded to pile, routes to SPELL or QUICK_DISCARD |
| AWAITING_ACTION (from discard) | Yes | Pass back (return card to pile) | Active player | Card back on pile, proceeds to QUICK_DISCARD |
| AWAITING_QUICK_DISCARD | Display only | — | All players | Reference rank for matching |
| Others | No | — | — | — |

**Visual States:**
- **Default:** Top card face-up (rank/suit visible), count label ("Discard: 8 cards")
- **Hover (clickable phase):** Glow/border highlight
- **Disabled:** Greyed out appearance

**Knowledge Display:**
- All cards in discard pile are public (all players see all ranks/suits in pile)
- You see discard pile cards as [Revealed](#revealed) if you took one from it

---

### Peek Area

**Central display zone (above or beside Deck/Discard, per layout).**

**Contents by Phase:**

| Phase | Display |
|-------|---------|
| TURN_START | Empty or faded |
| DRAWING | Empty |
| AWAITING_ACTION | Your drawn card (face-up, "From Deck" or "From Discard" badge) |
| AWAITING_SPELL_INVOCATION | Discarded card (face-up, spell name and effect) |
| Others | Empty or previous peek fades |

**Visual Style:**
- Card shown face-up with rank/suit clearly visible
- Brief animations: fade in/out on card change

---

## 5. Revealed & Exposed Rendering

See [KNOWLEDGE_ARCHITECTURE.md](KNOWLEDGE_ARCHITECTURE.md) for detailed data model. This section covers UI rendering only.

### Revealed (You Know This Card)

**Definition:** You know a card's rank and suit value.

**Visual Indicator:** **Rank Badge**
- Small display showing rank (as short symbol: A, 2–9, T, J, Q, K) and suit (as symbol: ♠ ♥ ♦ ♣)
- Example: "A♠" or "Q♥"
- Color-coded by suit (traditional colors)

**Where It Appears:**
- Your Cards zone: on any slot you've [Revealed](#revealed) via Initial Glance, own draw, Spy, Decree, or Discard Pile take
- Opponent Cards zone (your view only): on any opponent slot you've Spied or Decree-peeked
- Discard Pile: on all face-up cards (public to all)

**Styling:**
- Small badge (12–14px font), positioned corner or overlay of card back
- Semi-transparent background for readability

**Independence:** Rank badge appears regardless of [Exposed](#exposed) status. A card can have badge without eye icon (you know it, opponent doesn't) or eye icon without badge (opponent knows it, you don't).

---

### Exposed (An Opponent Knows Your Card)

**Definition:** An opponent knows your card's rank and suit value.

**Visual Indicator:** **Eye Icon**
- Small eye symbol (👁️ or stylized icon)
- Positioned on your card slot to indicate opponent awareness

**Where It Appears:**
- Your Cards zone only: slots where ≥1 opponent knows your card's value
- Opponent Cards zone (your view): never (you don't see this indicator in opponent zones; only in your own)

**Triggered By:**
- Opponent Spied on your slot
- Opponent peeked via Decree on your slot (regardless of swap decision)
- You took a card from discard pile (all opponents see it, so eye icon appears for all)
- You received a card via Decree swap from opponent who knew their card (eye icon marks your new slot)

**Hover Interaction (Optional):**
- Hover eye icon to show tooltip: "Known by: [Opponent A], [Opponent B], ..."
- Displays list of opponent names who know this card
- Cosmetic highlight or color tint (optional, subtle)

**Independence:** Eye icon appears regardless of [Revealed](#revealed) status. A slot can have eye icon without rank badge (opponent knows it, you don't) or rank badge without eye icon (you know it, opponent doesn't).

---

### No Knowledge (Unknown Slot)

**Definition:** You don't know the card, and no opponent knows it (either).

**Visual:** Card back only, no badge, no eye icon.

**Styling:** Standard card back appearance (design/pattern).

---

## 6. UI Helpers & Displays

### Phase Banner

**Location:** Top-center of play area or above Your Cards zone.

**Content:** Contextual text describing current phase and next expected action.

**Examples:**
- "Your Turn — Choose Deck or Discard"
- "Your Drawn Card — Choose Action"
- "SPELL INVOCATION — Spy"
- "QUICK DISCARD — Match 7"
- "TRIAL BEGINS — First Testimony Window"
- "Waiting for [Player] to draw..."

**Visual:**
- Large, bold text (36–48px)
- Persistent throughout phase
- Changes as phase changes

**Timer Position:** Can overlap or be adjacent to banner (e.g., "Your Turn | 00:45" in same bar).

---

### Leaderboard Panel

**Location:** Right sidebar or persistent right panel.

**Refresh Rate:** Live, updates instantly as scores change.

**Contents (per player row):**
- Player name (or nickname)
- Current score (numeric)
- Rank badge (1st, 2nd, 3rd, etc.)
- Score color-coding (optional): red if ≥100, orange if ≥75, neutral otherwise

**Sorting:** By current score (lowest to highest = 1st to last).

**Size:** 5 rows max (fits 2–5 player games).

**Appearance:**
- Compact layout, minimal padding
- Highlight current player's row during their turn (subtle glow or background tint)
- Highlight winner's row when game ends (bold or special color)

---

### Tooltips Area

**Location:** Right panel below Leaderboard or dynamically positioned.

**Content:** Context-sensitive descriptions of current phase or available actions.

**Examples:**
- "GLANCE – View one of your own slots"
- "SPY – View one opponent's slot"
- "CHALLENGE – Force a Duel comparison"
- "PLEA – Take +25 flat instead of true sum"

**Visual:**
- Regular font (14–16px)
- Updated each phase
- Brief, one-sentence descriptions

---

### Known Sum Display

**Location:** Bottom-left info section or Your Cards zone label.

**Content:** "Known Sum: [X]"

**Calculation:** Sum of card values in your hand that you have [Revealed](#revealed) knowledge of. If you know all 4 cards, this is your true hand sum. If you know only 2 cards, this is partial.

**Color Coding:**
- Green (≤7): [Eligible](#eligible) threshold met
- Red (>7): Over threshold
- Grey or neutral: Partial sum (not all cards known)

**Update Frequency:** Live, changes as you reveal cards via powers.

---

### "LAST TURN" Alert

**Trigger:** When last card is drawn from deck.

**Display:** Pulsing or highlighted banner (optional separate alert).

**Location:** Top of play area.

**Text:** "LAST TURN — After this round ends, scores are final."

**Duration:** Visible through rest of that turn (Action, Quick Discard, Trial).

---

### Timer Display

**Location:** Top-right of phase banner or adjacent.

**Format:** Countdown in remaining seconds (no need to specify exact value; determined by playtesting).

**Color Progression:**
- Green: ample time
- Yellow: warning (approaching timeout)
- Red: urgent (near timeout)

**Pulsing Animation:** Red state may pulse to emphasize urgency.

**Timeout Handling:** See [Section 7](#7-timeout-behavior).

---

### Phase-Specific Highlights

**Active player's turn zones:**
- Your Cards zone: persistent glow/border (you're active)
- Deck & Discard: glow/border during DRAWING phase

**Power card indication (AWAITING_ACTION):**
- Peek Area card displays spell name/effect if rank ∈ {7,8,9,10,J,Q}

**Quick Discard window:**
- Discard Pile rank highlighted large or colored
- Only matching rank slots in Your Cards are selectable/highlighted

**Trial windows:**
- Phase banner emphasizes "TRIAL" or "TESTIMONY"
- Button Zone buttons highlighted (TESTIMONY, CHALLENGE, PLEA per window)

---

## 7. Timeout Behavior

**Philosophy:** When timer expires, a default action fires to advance the game. Specific timeout actions per phase are listed below. Timeout values are determined by playtesting (not specified here).

### Timeout Actions by Phase

| Phase | Timeout Action | Outcome |
|-------|----------------|---------|
| DRAWING | Draw from Discard | Top discard card drawn, proceeds to ACTION |
| AWAITING_ACTION (from deck) | Discard Immediate | Card discarded to pile, routes to SPELL or QUICK_DISCARD |
| AWAITING_ACTION (from discard) | Pass Back | Card returned to pile, proceeds to QUICK_DISCARD |
| AWAITING_SPELL_INVOCATION | Skip Spell | Spell declined, proceeds to QUICK_DISCARD |
| AWAITING_QUICK_DISCARD | Skip (no quick-discard) | Player passes quick-discard, hand unchanged, proceeds to TRIAL or ROUND_OVER |
| AWAITING_CALL_WINDOW | Skip (pass testimony) | Player marked "passed first", proceeds to MATCH_WINDOW |
| AWAITING_MATCH_WINDOW | Skip (pass testimony) | Player marked "passed cross", proceeds to PERJURY_CHECK |
| AWAITING_DUEL_WINDOW | Skip (no challenge) | Player marked "passed challenge", proceeds to FINAL_PLEA_WINDOW |
| AWAITING_FINAL_PLEA_WINDOW | Decline Plea | Score true sum, [Renaissance](#renaissance) eligible (if no [Perjury](#perjury)), proceeds to ROUND_OVER |

**Effect:** Default action is logged as if player had pressed the equivalent button. Game state advances, trial progresses, scores updated accordingly.

---

## 8. Automatic Routing Phases

These phases have no player input; they execute automatically:

**Rank Check (post-ACTION):**
- Routes AWAITING_ACTION → AWAITING_SPELL_INVOCATION (if discarded card rank ∈ {7,8,9,10,J,Q}) or AWAITING_QUICK_DISCARD (otherwise)

**Perjury Check (post-MATCH_WINDOW):**
- Validates first-window [Testimony](#testimony)-givers
- Removes any with true sum > 7 (committed [Perjury](#perjury))
- Routes AWAITING_MATCH_WINDOW → AWAITING_DUEL_WINDOW (if ≥2 truly-[Eligible](#eligible) remain) or AWAITING_FINAL_PLEA_WINDOW (otherwise)

**Duel Execution (post-DUEL_WINDOW challenge):**
- Compares hand sums if ≥1 challenge given
- Assigns scores (+0 to lowest, +50 to others)
- Routes to AWAITING_FINAL_PLEA_WINDOW

**Scoring & Renaissance (post-FINAL_PLEA_WINDOW or round-end edge case):**
- Calculates all final scores
- Checks [Renaissance](#renaissance) conditions (exact 50/100 landing via true [Bystander](#bystander) score)
- Updates leaderboard
- Routes to ROUND_OVER or GAME_OVER

---

## 9. Edge Cases & Special Rules

### E1: Hand Reaches Zero During Quick Discard

**Trigger:** A player quick-discards their last card during the [Quick Discard Window](#awaiting_quick_discard).

**Outcome:** Round ends immediately.

**Scoring:**
- Player who emptied hand: +0
- All other players: true hand sum ([Bystander](#bystander) scoring, [Renaissance](#renaissance) eligible if no [Perjury](#perjury) this round)

**No Trial:** Trial does not run. Proceeds directly to ROUND_OVER.

**Display:** Event logged prominently ("Player A's hand emptied — Round Over").

**Next:** Game check → new round or GAME_OVER.

---

### E2: Nobody Gives Testimony on Last Turn

**Trigger:** Last card drawn from deck, Quick Discard window closes, Call Window opens and closes with zero [Testimony](#testimony) given.

**Outcome:** Round ends immediately.

**Scoring:** All players score as [Bystanders](#bystander) (true hand sum, [Renaissance](#renaissance) eligible if no [Perjury](#perjury) this round).

**No Trial:** Trial phases skipped. Proceeds directly to ROUND_OVER.

**Display:** Phase banner shows "No Testimony Given — Round Over".

**Next:** Game check → new round or GAME_OVER.

---

### E3: Only 1 Testimony Given

**Trigger:** Call Window + Match Window complete with only 1 [Testimony](#testimony)-giver surviving Perjury Check.

**Outcome:** Duel Window skipped.

**Scoring:**
- Testimony-giver: +0 ([Plain Agreement](#plain-agreement), no one to duel)
- All other [Bystanders](#bystander): true hand sum or plea

**No Duel:** Skips directly from Perjury Check to AWAITING_FINAL_PLEA_WINDOW.

**Display:** Phase banner updates ("Only 1 caller — Proceeding to Plea").

---

### E4: False Cross-Testimony

**Trigger:** A player gives late [Testimony](#testimony) in Match Window with true sum > 7.

**Outcome:** Never commits [Perjury](#perjury) (only first-window callers can).

**Scoring:** +25 flat, regardless of [Challenge](#challenge) outcome. [Renaissance](#renaissance) ineligible.

**Display:** Event log marks "False Cross-Testimony" outcome.

---

### E5: Duel Ties (Multiple Winners)

**Trigger:** ≥2 [Testimony](#testimony)-givers tied for lowest true hand sum during [Duel](#duel).

**Outcome:** All tied players score +0. All others score +50.

**Example:** Duel involves Players A (sum 4), B (sum 4), C (sum 8). A and B tied at 4 (lowest) → both +0. C → +50.

**Display:** Leaderboard and round summary both reflect multiple +0 winners.

---

### E6: Last Turn Deck Exhaustion

**Trigger:** Active player draws the last card from deck.

**Display:** "LAST TURN" alert fires.

**Behavior:** Turn plays out completely normally (ACTION, SPELL, QUICK_DISCARD, possibly TRIAL). After ROUND_OVER, game checks: any score ≥120? If no, new round begins with fresh shuffled deck.

**No Turn Limit:** Game continues round-by-round until someone reaches 120+.

---

### E7: Multiple Renaissance Resets (Rare)

**Trigger:** A player scores exactly 50 in one round, then exactly 100 in a later round (or any combination of exact 50/100 landings).

**Outcome:** Each exact landing triggers a reset (50→25, 100→50). Possible multiple times per game.

**Display:** Renaissance animation plays each time; round summary marks it.

---

### E8: Decree Swap with Unknown Card

**Trigger:** During Decree, you swap an opponent's peeked card with one of your cards that you didn't know.

**Outcome:**
- You receive opponent's card: marked [Revealed](#revealed) (you now know it)
- Opponent receives your card: NOT marked [Exposed](#exposed) (because you didn't know it)
- Opponent does NOT see eye icon on your card at their new location

**Knowledge Tracking:** Correct per [Knowledge Architecture](rules.md#9._Knowledge).

---

### E9: Smuggle with Discard-Pile Card

**Trigger:** You drew a card from discard (so all opponents know it). Later, you Smuggle that card to an opponent.

**Outcome:**
- Card retains [Exposed](#exposed) status (all opponents already know it)
- Opponent at new location receives [Exposed](#exposed) marking (they can see it was known)

**Knowledge Tracking:** Correct; card's `known_by` set travels with it.

---

## 10. Glossary (Quick Reference)

For full definitions, see [rules.md](rules.md#glossary).

- **[Bystander](#bystander):** Player who never gave [Testimony](#testimony) and wasn't removed for [Perjury](#perjury).
- **[Challenge](#challenge):** Button pressed during [Duel Window](#awaiting_duel_window) to force a [Duel](#duel).
- **[Cross-Testimony](#cross-testimony):** Late [Testimony](#testimony) given in [Match Window](#awaiting_match_window).
- **[Duel](#duel):** Trial resolution comparing hand sums of [Testimony](#testimony)-givers.
- **[Eligible](#eligible):** Hand with true sum ≤ 7.
- **[Empty Hand](#empty-hand):** Player's hand reaches 0 during [Quick Discard](#awaiting_quick_discard).
- **[Exposed](#exposed):** An opponent knows your card's value (eye icon).
- **[Perjury](#perjury):** False first-window [Testimony](#testimony) unchallenged; harshest penalty.
- **[Plea](#plea):** [Bystander](#bystander) button to take +25 flat instead of true sum.
- **[Plain Agreement](#plain-agreement):** ≥2 [Eligible](#eligible) [Testimony](#testimony)-givers, no [Challenge](#challenge).
- **[Quick Discard](#quick-discard):** Window after turn where any player may discard matching rank.
- **[Renaissance](#renaissance):** Comeback reset triggered when score lands exactly on 50 or 100 (true [Bystander](#bystander) only).
- **[Revealed](#revealed):** You know a card's value (rank badge).
- **[Testimony](#testimony):** Public claim "I am [Eligible](#eligible)".
- **[Trial](#trial):** End-of-turn resolution sequence (Call → Match → Perjury → Duel → Plea).

---

**END OF GAMEPLAY SPECIFICATION**