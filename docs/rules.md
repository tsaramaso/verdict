# Verdict — Game Rules

## 1. Purpose

Verdict is a bluffing and deduction card game. Players build hands and make public claims about their card values. The court (other players) challenges or accepts these claims. Truth and lies are scored differently. The player with the lowest cumulative score after the game ends wins.

Why lowest score? Because honest players accumulate points slowly. Liars who succeed gain points fast but risk harsh penalties.

---

## 2. Win Condition (Game)

**The game ends immediately when any player's score reaches 120 or higher.**

The player with the lowest final score wins. Standard competition ranking applies: tied scores share the same rank, next rank skips accordingly.

Example: Final scores [85, 92, 92, 110]. Rankings: 1st place = 85, 2nd place (tie) = both at 92, 4th place = 110.

---

## 3. Win Condition (Round)

Each round awards points based on outcomes. The distribution depends on whether a [Trial](#trial) occurred and how players fared.

**Outcome table:**

| Outcome | Score | Renaissance Eligible? |
|---------|-------|----------------------|
| [Perjury](#perjury) (false claim, unchallenged) | +25 AND true hand sum, stacked | No |
| [Duel](#duel) winner (lowest eligible hand sum) | +0 | No (zero never triggers) |
| [Duel](#duel) loser (higher eligible hand sum) | +50 | No |
| [Plain Agreement](#plain-agreement) (2+ eligible, no challenge) | +0 | No |
| False [Cross-Testimony](#cross-testimony) | +25 flat | No |
| [Plea](#plea) taken | +25 flat | No |
| True [Bystander](#bystander), no Perjury this round | true hand sum | Yes |
| True [Bystander](#bystander), Perjury occurred this round | player choice: true sum (eligible) OR +25 (ineligible) | Depends on choice |
| [Empty Hand](#empty-hand) (player discards last card) | +0 | N/A (everyone else scores as bystanders) |
| Last Turn, no [Testimony](#testimony) given | everyone scores as true bystander | Yes, for all |

---

## 4. Setup

**Players:** 2–5 per game.

**Deck:** One standard 52-card deck (no jokers).

**Hand size:** 4 cards per player, dealt one at a time in order.

**Turn direction:** Chosen at game start (clockwise or counterclockwise), fixed for entire game.

**Initial Glance:** After dealing, each player privately views their first two cards, then all cards return face-down. This is the only time you automatically see your own cards.

---

## 5. Card Values

| Card | Value |
|------|-------|
| A (Ace) | 1 |
| 2–10 | Face value |
| J (Jack) | 11 |
| Q (Queen) | 12 |
| K (black: ♠ ♣) | 13 |
| K (red: ♥ ♦) | 0 |

**True hand sum:** Add all four of your card values. This is your real total (known only to you until revealed).

**Eligible:** A hand with a true sum of 7 or less.

Example: A♠, 2♥, 3♣, K♥ = 1 + 2 + 3 + 0 = 6. This hand is eligible.

---

## 6. The Turn

A turn follows this sequence:

### 6.1 Draw

The active player chooses **one** of two actions:

- **Draw blind from the deck** — Take the top card, do not see it yet.
- **Take the top card from the discard pile** — See it before deciding what to do with it. (Not available on the first turn of the round; the discard pile is empty.)

If the last card in the deck is drawn, [Last Turn](#edge-cases) is flagged.

### 6.2 Action

If you drew from the deck, you have two choices:

- **Discard immediately** — Place the drawn card face-up on the discard pile. If this card has a [power](#spell-powers), you may invoke it now.
- **Swap** — Put the drawn card into one of your four hand slots, and discard the replaced card face-up. The drawn card's power never triggers on a swap.

If you took from the discard pile, you have two choices:

- **Swap** — Put the taken card into one of your four hand slots, and discard the replaced card.
- **Pass it back** — Return the card to the discard pile. This counts as a turn, but your hand doesn't change.

### 6.3 Spell Invocation (if applicable)

If you discarded immediately and the card is a 7, 8, 9, 10, J, or Q, you may invoke its [power](#spell-powers). Using a power is optional. If you decline, proceed to Quick Discard.

### 6.4 Quick Discard Window

After your card settles on the discard pile, a window opens: **any player at the table** (including you) may immediately discard a card of the **same rank** from their own hand onto the discard pile.

The rank must match exactly (suit irrelevant). Multiple players can quick-discard in any order. No card is drawn to replace a quick-discarded card.

If any player's hand reaches **zero cards**, the round ends immediately. That player scores +0. Everyone else scores as [bystanders](#bystander). No [Trial](#trial) occurs.

Example: You discard 7♠. During the quick-discard window, Player A discards 7♣, then Player C discards 7♥. Player B did not quick-discard (they don't have a 7). Three cards are now on the discard pile, and it's Player B's turn next (assuming it's not your turn again).

---

## 7. Spell Powers

Powers are only invoked when their card is **freshly drawn from the deck and immediately discarded**. Swapping or quick-discarding never triggers a power.

All powers operate on **permanent, slot-based knowledge**. Any knowledge you have about a specific card stays with that card even if it moves to a new hand via [Smuggle](#smuggle) or [Decree](#decree).

### Glance (7 or 8)

**Definition:** Privately view one of your own hand slots.

If you already know that slot's card (from initial deal or previous knowledge), this is cosmetic. If the slot is unknown, you now learn its value.

**Example:** You drew 8♦ and discarded immediately. You invoke Glance. You look at your slot 3, which is still unknown to you. It's Q♠. You now know slot 3 is Q♠ for the rest of the round.

### Spy (9 or 10)

**Definition:** Privately view one opponent's hand slot.

Only you see the value. The opponent sees the animation but not the card itself. A small eye icon marks that slot (visible to you) to indicate you've spied on it.

**Example:** You drew 9♣ and discarded immediately. You invoke Spy. You peek at Opponent B's slot 1, which is 2♦. You now know Opponent B's slot 1 is 2♦. Opponent B sees the slot was peeked but doesn't know it's a 2.

### Smuggle (Jack)

**Definition:** Blind-swap one of your cards with one of an opponent's cards by position.

Neither player sees the other's card value. The swap executes immediately. The table sees the animation but not the values.

**Two steps:** Click your slot, then click opponent's slot. After both are selected, the swap executes.

You can press Skip at any time to decline the power.

**Example:** You drew J♠ and discarded immediately. You invoke Smuggle. You select your slot 2 (which is 5♦ to you, but Smuggle doesn't let you see this). Then you select Opponent C's slot 4. The cards swap. Your slot 2 now contains whatever was at Opponent C's slot 4. Opponent C's slot 4 now contains your old 5♦. No one sees the values change.

### Decree (Queen)

**Definition:** View one opponent's slot, then optionally swap it with one of your own slots.

**Two stages:**
1. **Peek stage:** Select an opponent's slot and view its value (private to you).
2. **Swap stage:** Choose to swap it with one of your slots or decline the swap.

**Knowledge tracking on swap:**

If you swap:
- The opponent's card you receive: You now know its value (see [Knowledge Tracking](#9-knowledge)).
- Your card you give to opponent: If you already knew your card's value, an eye icon marks it at the opponent's new location (knowledge follows the card). If you didn't know your card, no icon.

If you decline the swap:
- The opponent's card stays in place. you peeked it, so you retain knowledge of it, the target player also knows retains that you have this knowledge.

You can press Skip at any time to decline the power entirely (no peek occurs).

**Example 1 (Swap, knew your card):** You drew Q♥ and discarded immediately. You invoke Decree. You peek at Opponent A's slot 3, which is K♠. You decide to swap it with your slot 1 (which you know is 5♦). Your slot 1 now has K♠. Opponent A's slot 3 now has your old 5♦. 

**Example 2 (Swap, didn't know your card):** You peek at Opponent B's slot 2, which is A♠. You decide to swap it with your slot 4 (which you never saw before). Your slot 4 now has A♠. Opponent B's slot 2 now has whatever was in your slot 4. No eye icon marks the opponent's slot 2 (because you didn't know your card).

**Example 3 (No swap):** You peek at Opponent C's slot 1, which is 7♣. You decide not to swap. Opponent C's slot 1 stays 7♣. An eye icon marks slot 1 (you peeked it, so you have knowledge).

---

## 8. The Trial

A [Trial](#trial) occurs after the [Quick Discard Window](#quick-discard-window) unless:
- No cards remain in the deck AND no [Testimony](#testimony) was given this turn (forced end, everyone scores as [bystanders](#bystander)), OR
- A player's hand reached zero during quick-discard (round ended, bystander scoring only).

The Trial has five windows. All eligible players must log an action or pass in each window.

### 8.1 Call Window (First Testimony)

**Definition:** All players see a **Testimony** button. Pressing it claims "I am [eligible](#eligible)."

A short time window stays open after the first press. Any player pressing Testimony within this window is a **first-window caller** and subject to [Perjury](#perjury) if their claim is false.

Players who don't press Testimony or press **Skip** are marked as "passed first."

If zero [Testimony](#testimony) is given:
- On the last turn of the round: everyone scores as [bystanders](#bystander), round ends.
- Otherwise: proceed to the next player's turn (no Trial).

Example: Players [A, B, C, D]. Call Window opens. Player A presses Testimony (first press, starts timer). Within the window, Players C and D also press. Players B and A (who didn't press in time) are marked as passed. First-window callers = [A, C, D].

### 8.2 Match Window (Cross-Testimony)

**Definition:** Players who didn't give [Testimony](#testimony) in the Call Window now see a **Testimony** button. Pressing it claims "I am [eligible](#eligible)" late.

Late [Testimony](#testimony) is never subject to [Perjury](#perjury).

Example: Continuing above. Players B passes the Match Window (no action). Players A, C, D see no button (they already decided). Cross-callers = [B] if B pressed.

### 8.3 Perjury Check

**Definition:** The game validates all **first-window callers only**. Any first-window caller whose true sum > 7 has committed [Perjury](#perjury).

A [perjured](#perjury) player is removed from the rest of the Trial. They score +25 + their true hand sum, stacked. No one can challenge them further.

If 2+ truly-[eligible](#eligible) callers remain (first or cross), proceed to [Duel Window](#duel-window). Otherwise, proceed to [Final Plea Window](#final-plea-window).

Example: First-window callers [A, C, D] with true sums [6, 4, 9]. A and C are truly eligible. D is not (9 > 7). D is removed, scores +25 + 9 = +34. Truly eligible = [A, C]. Since 2+ remain, go to Duel Window.

### 8.4 Duel Window

**Definition:** [Eligible](#eligible) [Testimony](#testimony)-givers (first or cross) see a **Challenge** button. Pressing it contests the [Testimony](#testimony), forcing a comparison.

Non-[Testimony](#testimony)-givers cannot act here.

If zero players press Challenge: all truly-[eligible](#eligible) [Testimony](#testimony)-givers score +0 ([Plain Agreement](#plain-agreement)).

If 1+ players press Challenge: a [Duel](#duel) occurs. The truly-[eligible](#eligible) [Testimony](#testimony)-giver with the **lowest true hand sum** scores +0. All others score +50.

Ties are allowed. Multiple players can win +0.

Example: Truly-eligible are [A (sum 6), C (sum 4)]. A presses Challenge. Duel occurs. C's sum 4 is lower, so C scores +0. A scores +50.

Example 2: Truly-eligible are [A (sum 3), C (sum 3), E (sum 7)]. C presses Challenge. Duel occurs. A and C tie at 3 (lowest), both score +0. E scores +50.

### 8.5 Final Plea Window

**Definition:** [Eligible](#eligible) bystanders (players who never gave [Testimony](#testimony), first or cross, and were not removed for [Perjury](#perjury)) see a **Take Plea** button.

**Take Plea:** Press the button to score +25 flat (can be worse than your true sum). [Renaissance](#renaissance) ineligible.

**Decline Plea (automatic):** If you do not press the button before the timer expires, it counts as declining the plea. You score your true hand sum. [Renaissance](#renaissance) eligible if no [Perjury](#perjury) occurred this round (or if [Perjury](#perjury) did occur, the choice is now informed, and you accept the risk).

The plea decision is logged as "plea taken" or "plea declined" based on whether you pressed or let timeout occur.

Example: You're a bystander with true sum 18. You press Take Plea, scoring +25. Better than your actual hand.

Example 2: You're a bystander with true sum 6. You let the timer expire (decline plea). You score +6. Better to decline in this case.

Example 3: You're a bystander with true sum 12, and [Perjury](#perjury) occurred this round. You know the game is tight. You decline plea (score +12, eligible for [Renaissance](#renaissance)). You're betting your hand is good enough.

---

## 9. Knowledge

All knowledge is **permanent and slot-based**. Once you know a card's value, you remember it for the rest of the round.

Two independent knowledge states exist: **Revealed** (you know the card's value) and **Exposed** (an opponent knows your card's value).

### Revealed

You know a card's actual value. Sources:

- **Initial Glance:** Your first two slots (dealt face-down, peeked by you, returned face-down).
- **Your own hand:** After you draw from the deck, you know that card's value.
- **Spy:** After you invoke Spy, you know that opponent's slot value.
- **Decree peek:** After you invoke Decree and peek, you know that opponent's slot value.
- **Discard pile top card:** You see it when you take it from the discard pile. If anyone quick-discards it later, you know what rank it was.

### Exposed

An opponent knows the value of one of your cards. Sources:

- **Opponent Spied on your slot:** They invoked Spy (9 or 10).
- **Opponent peeked via Decree:** They invoked Decree (Queen) and peeked your slot (regardless of swap).
- **Discard pile draw:** You took a card from the discard pile; all players see its value before you acted on it.

### Visual Indicators

**Rank badge** (visible to you): Shows rank and suit. Appears on any card whose value is [Revealed](#revealed) to you.

**Eye icon** (visible to you, your slots only): Marks a slot that is [Exposed](#exposed). Hover shows opponent color (cosmetic).

**Note:** [Revealed](#revealed) and [Exposed](#exposed) are independent. A slot can have badge only, eye icon only, both, or neither.

### Knowledge Persistence on Swap

When a [Smuggle](#smuggle) or [Decree](#decree) swap occurs, **both knowledge states follow the card to its new location**.

**Revealed** (your knowledge): If you knew a card's value, you keep that knowledge when it moves to a new slot, new hand, or opponent.

**Exposed** (opponent awareness): If an opponent knew a card's value, that knowledge follows the card. You see the eye icon track the card's new location.

Example: You Spy opponent's slot 2 (King). Your slot is now [Revealed](#revealed) as King. Later, Smuggle swaps slot 2 with your slot 1. You now know your slot 1 is King. You see the rank badge at your slot 1.

Example 2: Opponent A Spied your slot 3. Your slot 3 is now [Exposed](#exposed) (marked with eye icon). Later, Decree swaps your slot 3 with Opponent B's slot 2. Your former slot 3 card (now at Opponent B's slot 2) remains [Exposed](#exposed). The eye icon moves to Opponent B's zone, marking Opponent A's knowledge.

Example 3: You Spy opponent A's slot 4 (5). The slot is [Revealed](#revealed) to you (rank badge). Later, Smuggle swaps it to your slot 1. Your slot 1 now has the 5, is [Revealed](#revealed) to you (rank badge), and Opponent A still knows it's a 5 but can no longer see it (no eye icon in your zone—they remember it, but the game doesn't track cross-hand awareness, only same-zone exposure).

---

## 10. Renaissance

[Renaissance](#renaissance) is a comeback mechanic.

**Definition:** If your score lands **exactly** on 50 or 100 via a genuine addition, your score resets down one tier.

- Exactly 50 → reset to 25.
- Exactly 100 → reset to 50.

Only [true bystander](#bystander) scores trigger this. All penalty buckets (Perjury, Plea, False Cross-Testimony, Duel loss) explicitly block [Renaissance](#renaissance), even if the math lands on 50 or 100.

Once a score has crossed 50 or 100 in a previous round, sitting at that value with a +0 result does **not** re-trigger [Renaissance](#renaissance). Only a fresh, qualifying, upward addition that lands exactly on the threshold triggers it.

Example: Round 1, you score +25, total = 25. Round 2, you score +25, total = 50. Renaissance triggered! Score resets to 25. Round 3, you score +0, total = 25 (no reset, +0 never triggers). Round 4, you score +50, total = 75. Round 5, you score +25, total = 100. Renaissance triggered! Score resets to 50.

Example 2: Your score is 48. You score +3 (as a true bystander with sum 3), total = 51. No Renaissance (51 ≠ 50, it's past the threshold). You must land exactly on it.

---

## 11. Edge Cases

### Last Turn (Deck Exhausted)

**Definition:** When the last card in the deck is drawn, the turn plays out completely normally.

The player who drew it performs their full [Action](#action). If they discard immediately, [Spell Invocation](#spell-invocation) may occur. [Quick Discard Window](#quick-discard-window) opens. Then, if [Testimony](#testimony) was given, the full [Trial](#trial) proceeds (Call → Match → Perjury → Duel → Plea → Verdict).

After the verdict, the round ends. The game checks: any score ≥ 120? If yes, Game Over. If no, a new round begins with a fresh shuffled deck.

If no [Testimony](#testimony) is given during the last turn: everyone scores as [bystanders](#bystander), round ends, proceed to game check.

**Why:** The deck is finite. Last turn forces conclusion of the turn loop, but the Trial and scoring run normally.

### Empty Hand (Quick Discard)

**Definition:** If a player's hand reaches zero cards via [Quick Discard](#quick-discard-window), the round ends immediately.

No [Trial](#trial) occurs. The player who emptied their hand scores +0. All other players score as [bystanders](#bystander) (true hand sum, Renaissance eligible if no [Perjury](#perjury) occurred).

The game then checks: any score ≥ 120? If yes, Game Over. If no, a new round begins.

**Why:** A hand of zero has no value. There's no point running a Trial.

Example: You have 4 cards. Active player discards 7. During quick-discard window, you discard your only 7 (the fourth card in your hand). Your hand is now empty. Round ends immediately. You score +0. Everyone else scores based on their true sum as bystanders.

### No Testimony on Last Turn

**Definition:** If the last card is drawn, turns out normally, quick-discard window opens, but zero players give [Testimony](#testimony), the round ends.

Everyone scores as [true bystanders](#bystander). [Renaissance](#renaissance) applies.

Example: Last turn is drawn. Quick-discard window closes (no one quick-discarded). Call Window opens, closes (no one pressed Testimony). The round ends. Everyone reveals their true sum and scores it.

### Duel Ties (Multiple Winners)

**Definition:** In a [Duel](#duel), all players tied for the **lowest true hand sum** among [Testimony](#testimony)-givers score +0.

All others score +50.

Example: [Testimony](#testimony)-givers [A (sum 5), B (sum 5), C (sum 8)] duel. A and B tie at 5 (lowest), both score +0. C scores +50.

Example 2: [Testimony](#testimony)-givers [A (sum 1), B (sum 1), C (sum 1)] duel. All three tie at 1 (lowest), all score +0.

### False Cross-Testimony

**Definition:** A [Cross-Testimony](#cross-testimony) player who is **not** truly [eligible](#eligible) (sum > 7).

Never results in [Perjury](#perjury) (only first-window callers can perjure). Scores +25 flat, [Renaissance](#renaissance) ineligible, regardless of Challenge outcome.

Example: You give cross-testimony with true sum 10. You are false. Even if challenged, you score +25 flat.

---

## Glossary

### Bystander
A player who never gave [Testimony](#testimony) (first or cross) and was not removed for [Perjury](#perjury). Scores their true hand sum at [Final Plea Window](#final-plea-window) or receives [Renaissance](#renaissance) if sum lands exactly on 50/100.

### Challenge
A button pressed during [Duel Window](#duel-window) by a [Testimony](#testimony)-giver to contest [Testimony](#testimony), forcing a [Duel](#duel). If at least one [Challenge](#challenge) occurs, the [Duel](#duel) proceeds (lowest sum wins +0, others +50).

### Cross-Testimony
Late [Testimony](#testimony) given during [Match Window](#match-window) by a player who passed the [Call Window](#call-window). Never subject to [Perjury](#perjury), always +25 flat if false.

### Decree
A Queen power. Peek at an opponent's slot, then optionally swap it with one of your own slots (blind). If you swap with a card you knew, it becomes [Exposed](#exposed) at opponent's hand (eye icon appears). If you don't swap, opponent's peeked slot is [Exposed](#exposed) (eye icon appears).

### Duel
A Trial resolution. Triggered when at least one [Challenge](#challenge) is pressed during [Duel Window](#duel-window). Compares true hand sums of [Testimony](#testimony)-givers. Lowest sum(s) score +0. All others score +50.

### Eligible
A hand whose true sum is 7 or less. Required to avoid [Perjury](#perjury) when giving [Testimony](#testimony).

### Empty Hand
A player's hand reaches zero cards via [Quick Discard](#quick-discard-window). Round ends immediately. No [Trial](#trial). Empty-hand player scores +0.

### Glance
A 7 or 8 power. Privately view one of your own hand slots.

### Revealed
Knowledge of a card's actual value (rank and suit). Permanent for the round. Indicated by rank badges. Follows the card to its new location on swap.

### Exposed
An opponent knows the value of your card. Marked with an eye icon on your slot. Follows the card to its new location on swap (within your hand or to opponent hands). Independent of [Revealed](#revealed).

### Last Turn
The turn when the last card is drawn from the deck. Plays out completely normally, including [Trial](#trial) if [Testimony](#testimony) given. After verdict, round ends.

### Match Window
The second [Testimony](#testimony) window. Players who passed the [Call Window](#call-window) now see the **Testimony** button. Late callers cannot commit [Perjury](#perjury).

### Perjury
A false [Testimony](#testimony) given by a first-window [Testimony](#testimony)-giver that is never [Challenged](#challenge). Harshest outcome. Score: +25 + true hand sum, stacked. [Renaissance](#renaissance) ineligible.

### Plain Agreement
A [Trial](#trial) outcome: 2+ truly-[eligible](#eligible) [Testimony](#testimony)-givers gave [Testimony](#testimony), but no [Challenge](#challenge) was pressed. All score +0.

### Plea
A [Final Plea Window](#final-plea-window) button. A [bystander](#bystander) voluntarily takes +25 flat instead of their true sum by pressing the button. If the timer expires without pressing, the plea is declined automatically (score true sum). [Renaissance](#renaissance) ineligible only if plea was taken.

### Quick Discard
A window after each turn where any player may discard a card matching the rank of the discarded card. If a hand reaches zero, round ends.

### Renaissance
A comeback reset. If your score lands **exactly** on 50 or 100 via a true [bystander](#bystander) addition, score resets down one tier (50→25, 100→50).

### Smuggle
A Jack power. Blind-swap one of your cards with one of an opponent's cards by slot position. Neither player sees the values. Executes immediately once both slots are selected.

### Spy
A 9 or 10 power. Privately view one opponent's hand slot (becomes [Revealed](#revealed) to you). Opponent's slot becomes [Exposed](#exposed) (eye icon visible to you only).

### Testimony
A public claim "I am [eligible](#eligible)." Starts a [Trial](#trial) if given during [Call Window](#call-window). Can also be given late during [Match Window](#match-window). First-window [Testimony](#testimony) subject to [Perjury](#perjury) if false and unchallenged.

### Trial
The end-of-turn resolution sequence. Opens if at least one player gave [Testimony](#testimony) (unless last-turn no-[Testimony](#testimony) edge case). Sequence: Call → Match → Perjury Check → Duel → Plea → Verdict.

### True Hand Sum
The sum of your four cards' values. Known only to you until revealed at end of round. Determines eligibility, [Perjury](#perjury), and scoring.

---

**END OF RULES**