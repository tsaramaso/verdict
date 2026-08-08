# Verdict
### Design Reference & Rulebook — Draft v0.1

---

## 1. Glossary

The whole ruleset uses a consistent Renaissance-court theme. These terms are used precisely throughout this document — the exact word matters.

| Term | Meaning |
|---|---|
| **Eligible** | A hand whose true value sums to ≤ 7 points. |
| **Testimony** | Publicly claiming "I'm eligible" (the old "call Gabo"). Ends the current turn loop and opens the Trial. |
| **Cross-Testimony** | A player joining with their own Testimony *after* the first window has closed, during the Match Window. |
| **Challenge** | Contesting a Testimony (the old "Counter-Gabo"), escalating the situation to a Duel. |
| **Duel** | The head-to-head comparison of true hand values among everyone still eligible-and-in-play once at least one Challenge has occurred. |
| **Perjury** | A false Testimony given by a **first-window** caller that nobody managed to Challenge. The harshest outcome in the game. |
| **Perjury Check** | The moment the game validates first-window callers for Perjury; happens mid-Trial. |
| **Verdict** | The end-of-round moment when scores are finalized, Renaissances are applied, and winners are announced—the suspenseful reveal. |
| **Plea** | Voluntarily accepting a flat, capped penalty instead of your true hand score (the old "Request Penalty" / Penalty A). |
| **Renaissance** | The comeback mechanic: landing exactly on 50 or 100 points via a genuine addition resets your score down to 25 or 50. |
| **Trial** | The entire round-ending decision sequence: Call Window → Match Window → Perjury Check → Duel Window → Final Plea Window → Verdict (Scoring). |
| **Glance** | The 7/8 self-peek power. |
| **Spy** | The 9/10 opponent-peek power. |
| **Smuggle** | The Jack's blind, deliberate-position exchange power. |
| **Decree** | The Queen's peek-then-optional-swap power. |
| **Slot** | A fixed position in a player's hand layout. Knowledge in this game is tracked per-slot, not per-memory. |

---

## 2. Objective

The game is played over several rounds. The goal is the **lowest cumulative score**. When the game ends (see Section 10), the player with the minimum score takes 1st place; all ranks below follow standard competition ranking (ties share a rank, the next rank skips accordingly).

---

## 3. Setup

- **Player count: 2–5 players per game.** These are hard caps — the engine should reject game creation outside this range.
- **Deck: one standard 52-card deck, no jokers** — the four suits, ranks A through K, exactly as enumerated in Section 4's value table. No additional decks are combined regardless of player count.
- Each player is dealt 4 cards, arranged face-down in front of them in fixed **slots**.
- At the start of the round, each player privately views (Glances at) their first 2 dealt slots, then they're placed face-down again. This is a **cosmetic-only** flip — the game continues to track and display that knowledge to the player for the rest of the round regardless of the visual state. There is no "forgetting" in this game; all player knowledge is permanently and accurately tracked and displayed.
- Cards cannot be freely rearranged between slots — only specific powers (Smuggle, Decree) or normal swap-in actions change what's in a slot.
- Turn direction (clockwise/counterclockwise) is chosen once, before the game starts, and stays fixed for the whole game.

---

## 4. Card Values

| Card | Value |
|---|---|
| A | 1 |
| 2–10 | face value |
| J | 11 |
| Q | 12 |
| K (black) | 13 |
| K (red) | **0** |

The red/black King split matters strategically — see Section 5.4.

---

## 5. The Turn

Each turn follows this sequence: **Draw → Action → (Spell) → Quick-Discard Window → Trial Call Window.**

### 5.1 Draw
The active player chooses to either:
- **Draw blind** from the deck, or
- **Take the discard pile's top card** (always just the single visible top card — never digging deeper into the pile).

### 5.2 Action
**If drawn from the deck:**
- **(A) Discard immediately**, face-up. This may trigger the card's power (see Section 7) — this is the *only* way to trigger a power.
- **(B) Swap it into any of your own slots**, discarding the replaced card face-up instead. This never triggers a power (neither the newly-placed card's, since it wasn't discarded, nor the discarded card's, since it wasn't freshly drawn).

**If taken from the discard pile:**
- **(B) Swap it into any of your own slots**, discarding the replaced card, or
- **Pass it back** — put it right back on the discard pile, unchanged. This is a legal way to consume a turn without altering your hand. It never triggers a power. It still counts as a fresh discard event for the purposes of 5.4 below.

### 5.3 Spell Resolution
If the card discarded via Action A is a 7, 8, 9, 10, J, or Q, the active player may use its power now (see Section 7). Using it is always optional.

### 5.4 Quick-Discard Window
Once the discard settles (via Action A, Action B's replaced card, or a pass-back), a window opens: **any player at the table, including the active player**, may throw a card of the **same rank** (suit irrelevant) from their own hand onto the discard pile.

- The game's UI only ever allows a legal, matching card to be selected — an invalid quick-discard attempt is not possible, so there is no penalty for "guessing wrong."
- This can chain across multiple players in any order, since the required rank never changes during the window.
- A successful quick-discard shrinks that player's hand by one card. **No replacement card is drawn.**
- If any player's hand reaches **zero cards** at any point, the round ends immediately — no Trial occurs, jump straight to Scoring (see the Empty-Hand case in Section 6.7).
- Strategic note: because the red King is worth 0, whoever holds one is incentivized to quick-discard it *fast*, since the next player could otherwise take it straight off the discard pile.

### 5.5 Last-Turn Rule
If the card drawn in 5.1 was the **last card in the deck**, this turn is automatically the round's final turn. It plays out completely normally through the full Trial sequence below — the round is guaranteed to end at the conclusion of this turn regardless of outcome. See Section 6.8 for the one open question this creates.

---

## 6. The Trial

Triggered once per turn, after the Quick-Discard Window closes (assuming no hand reached zero).

### 6.1 Call Window ("Give Testimony")
Every player sees a single button: **Testimony**. Any player may press it — a public claim of "I'm eligible" — which ends the turn loop and begins the Trial resolution.

A short sub-window (exact length TBD, see Section 12) stays open after the very first press. Anyone pressing Testimony within that sub-window is a **first-window caller**, and their claim is subject to Perjury (6.3). Multiple simultaneous first-window callers is a completely valid, intended outcome — two eligible players can peacefully agree and both walk away with 0.

### 6.2 Match Window (Cross-Testimony)
Every player who has **not yet** pressed Testimony now sees a single button: **Testimony** (a late, "cross" join). A player who doesn't press it simply passes this window.

- A late Testimony press here is **never** subject to Perjury — only first-window callers can commit Perjury.
- **Plea is not offered here.** It has exactly one home in the Trial: the Final Plea Window (6.5), which comes later, after Perjury Check and any Duel have resolved — so the decision is always made with full information rather than asked repeatedly at earlier points when less was known.

### 6.3 Perjury Check
The game checks **first-window callers only**. Any first-window caller who is **not actually eligible** has committed **Perjury**:
- They receive a capped penalty (+25) **and** their true hand sum, **stacked** — the harshest single outcome in the game.
- They are immediately and fully resolved — removed from the rest of the Trial. This cannot be Challenged, and does not affect anyone else's fate.

If **two or more** truly-eligible Testimony-givers remain after the Perjury Check (combining first-window survivors and cross-testimony players), proceed to 6.4. Otherwise, skip directly to the Final Plea Window (6.5).

### 6.4 Duel Window (Challenge)
This window **only appears** if ≥2 truly-eligible Testimony-givers remain post-Perjury Check.

- **Every remaining Testimony-giver** — genuine and secretly-false cross-testimony players alike, indistinguishable in the UI — gets a **Challenge** button, on a timer.
- Everyone else has **no action in this window** — they are not Testimony-givers, so there's nothing for them to Challenge or decide here. Their one decision (Plea or not) comes right after, at the Final Plea Window (6.5).
- A secretly-false cross-testimony player may still press Challenge; it resolves as a harmless no-op ("blank send") once the Trial concludes (see 6.6).
- **Deliberate design note:** whether this window appears at all is gated on the *true* eligible count, not the publicly visible count. This can theoretically let sharp players infer that a caller was false just from the window not appearing — this is accepted as intentional, since nothing further is at stake by that point regardless.

**Resolution:**
- If **nobody** presses Challenge during this window, all remaining truly-eligible Testimony-givers simply win: **0 points each**, no Duel needed.
- If **at least one** Challenge is pressed, a **Duel** occurs among all truly-eligible Testimony-givers/Challengers: the **lowest true hand sum(s)** win (ties share the win), scoring **0**. Every other eligible Duel participant takes **+50**.

### 6.5 Final Plea Window
This is the **one and only** point in the Trial where Plea is offered. It opens once the Perjury Check has resolved (6.3) and, if applicable, the Duel Window has fully resolved (6.4) — so it always comes last, right before Scoring.

- **Who sees it:** every player who is still undetermined at this point — i.e. never gave Testimony (first or cross), and was not just removed for Perjury.
- **What they see:** two buttons, **Plea** and **Decline**. Declining means being scored as a true bystander (true hand sum).
- **Why it's placed here, not earlier:** by this point, whether any Perjury occurred is public, and any Duel outcome is public too. A player deciding Plea vs. their true hand sum is always making that call with the most complete information the round can offer, rather than committing blind earlier and having no way to reconsider.
- This window is also what implements the "true bystander, Perjury occurred this round" choice from the outcome table below (6.6) — it isn't a separate mechanic with its own event type, it's this same Plea/Decline decision, just one made with the knowledge that Perjury happened. A bystander in a Perjury-free round has exactly the same two buttons available; nothing about the window itself changes based on whether Perjury occurred.
- Every eligible player logs exactly one outcome here — Plea taken, or Plea declined — no silent absence, consistent with every other Trial window.

### 6.6 Resolving False Cross-Testimony
A cross-testimony player who turns out **not** to be truly eligible can never become Perjury (only first-window callers can). Regardless of whether they were Challenged, pressed Challenge themselves (always a no-op), or how any Duel among others resolved — they personally default to: **flat +25, no Renaissance this round.**

### 6.7 Verdict, Scoring — Full Outcome Table
Computed silently once the Trial concludes; never revealed early.

| Outcome | Score effect | Renaissance eligible? |
|---|---|---|
| **Perjury** (false, first-window, unchallenged) | +25 **and** true hand sum, stacked | No |
| **Duel winner** (lowest tied hand in a Duel) | +0 | N/A (zero addition never triggers) |
| **Duel loser** (any other eligible Duel participant) | +50 | No |
| **Plain agreement** (2+ truly eligible callers, no Challenge ever raised) | +0 | N/A (zero addition never triggers) |
| **False cross-testimony** | +25 flat | No |
| **Plea** (voluntary, taken at the Final Plea Window, 6.5) | +25 flat | No — and may "backfire" if true sum was actually < 25 |
| **True bystander, no Perjury occurred this round** (declined Plea at 6.5) | true hand sum | Yes |
| **True bystander, Perjury occurred this round** (declined Plea at 6.5, now knowing Perjury happened) | player's choice: true hand sum (Renaissance-eligible) *or* capped +25/no-Renaissance | Depends on choice — an informed gamble now that Perjury's occurrence is public, not gated by their actual hand value |
| **Empty Hand** (a player discards their last card via quick-discard) | Round ends immediately for everyone, no Trial. That player: +0. Everyone else: scored as true bystanders per the rules above (no Perjury possible in this path). | Yes, for the "everyone else" group |
| **Forced end, no Testimony given** (last turn per 5.5 completes with zero Testimony) | Round ends. Every player scored as a true bystander: true hand sum (no Perjury possible in this path). | Yes, for all players |

### 6.8 Forced Round-End on the Last Turn
If the round reaches its guaranteed final turn (5.5) and **nobody gives any Testimony at all**, the round still ends there. Since no Testimony was ever given, there is no Perjury to check and no Duel to run — **every player is scored as a true bystander**: true hand sum, normal Renaissance rules apply. This mirrors the Empty-Hand case in the table above (6.7).

---

## 7. Spell Powers

**Trigger condition, without exception:** a power only activates when its card was **freshly drawn from the deck and immediately discarded** (Action A, Section 5.2). It never triggers on a swapped-in card, a quick-discard, or a discard-pile pickup (including a pass-back).

All powers operate on **permanently tracked, slot-based knowledge** — there is no memory decay. Any physical repositioning of a card (Smuggle, Decree) is visible to the whole table as an event, even though the values involved stay hidden — so any knowledge a player already had about a specific card correctly follows it to its new slot/owner.

| Power | Cards | Effect |
|---|---|---|
| **Glance** | 7 or 8 | View one of your own slots. If you already know that slot's content, this is purely cosmetic — useful only on a currently-unknown slot (one never initially viewed, or changed by another player's swap since). |
| **Spy** | 9 or 10 | View one of an opponent's slots. Single-sided: you learn the value; the target only knows *that* the slot was peeked, never the value. This has real strategic weight — e.g., spotting a red King informs your Testimony/Challenge/Plea decisions later. |
| **Smuggle** | J | Choose one of your own slots and a target opponent's slot; the two cards swap positions. **Neither player sees either value.** The swap itself (which slots moved) is visible to the table. |
| **Decree** | Q | Choose an opponent's slot and view its value (private to you only). Then, optionally, swap it for one of your own slots (any position). If taken, the swap is table-visible in the same way as Smuggle. |

---

## 8. Quick-Discard

Covered fully in Section 5.4. Summary: any player, any time the window is open, may throw a same-rank card from their hand onto the discard pile. Never triggers a power. No penalty exists for a wrong attempt — the interface simply doesn't allow selecting a non-matching card.

---

## 9. Renaissance (Comeback)

Triggers only when a **genuine, non-zero, non-penalized** score addition lands a player's total **exactly** on 50 or 100 in a single round's tally:
- Exactly 50 → resets to **25**.
- Exactly 100 → resets to **50**.

In practice, only a **true hand-sum result** (a true bystander, or a Perjury-triggered bystander who chose true-sum) can realistically trigger this — Duel/agreement wins add 0 (never triggers), and every penalty bucket (Perjury, Plea, false cross-testimony, Duel loss) is explicitly and unconditionally blocked, regardless of what the math would otherwise show.

Once a score has crossed 50 or 100 in a previous round, it does **not** re-trigger by merely sitting at that value with a +0 result later — only a fresh, qualifying, upward addition landing exactly on the threshold triggers a reset.

---

## 10. End of Game

- At the end of **every** round, all scores are tallied.
- If **any** player's score is **≥ 120**, the game ends **immediately** — this is a hard wall with **no** Renaissance-style protection, regardless of how the score got there (even via a penalty bucket).
- **Final ranking:** lowest score = 1st place. Standard competition ranking applies at every tier — ties share a rank, and the next distinct score skips ranks accordingly (e.g., two players tied for 2nd both get "2nd," the next player is "4th").
- No special handling is given to whichever player specifically triggered the ≥120 stop — ranking is purely by final score for everyone.
