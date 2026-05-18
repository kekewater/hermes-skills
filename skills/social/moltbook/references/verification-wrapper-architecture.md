# Moltbook Verification Wrapper Architecture

## Origins

Built May 17, 2026. Based on the excellent `moltbook-verify` PyPI library (v1.0.2) which handles ~80% of cases.
Our wrapper (`scripts/moltbook_verify_wrapper.py`) extends it with fixes for edge cases discovered during real use.

## Core Pipeline (Keke's 6-step framework)

```
Raw challenge text
  ↓ 1. Punctuation stripping (original library handles alternating caps/symbols)
  ↓ 2. Char deduplication ("thhhhreeee" → "three")
  ↓ 3. Fragment rejoining ("thi rty" → "thirty") — original library
  ↓ 4. Compound number splitting ("twentythree" → "twenty three") — OUR FIX
  ↓ 5. Number extraction (digit literals + word numbers + compound compounds)
  ↓ 6. Operation detection (keyword-based, with context awareness)
  ↓
"X.XX" answer or None
```

## Bugs Fixed vs Original Library

| # | Bug | Root Cause | Our Fix |
|---|-----|-----------|---------|
| 1 | **Hyphenated number words** | "twenty-three" → degarble strips hyphen → "twentythree" → out-of-vocabulary | Added 40+ compound variants to EXTRA_WORD_CORRECTIONS (twentythree→twenty three, etc.) |
| 2 | **Char-collapse variants** | Original degarble collapses "twentythree" → "twentythre" (removes duplicated 'e') before our fix can match it | Added compressed variants (twentythre, twentyfou, twentyeigh, etc.) |
| 3 | **"per" in unit context misclassified as division** | "meters per second" → "per" keyword matched division branch → 23/5=4.6 instead of 23+5=28 | Added `is_rate_context` regex: if "X per Y" where X is a unit (meters, cm, newtons), skip division |
| 4 | **Stop-word contamination** | "newtons", "lobster", "claw" took up token space in fragment rejoining | Added STOP_WORDS set (lobster, claw, newton, dominance, water, force, etc.) |
| 5 | **Control flow overwrite** | `if multiply: result=a*b` was a standalone `if`; then an independent `elif..else` chain would `else: result=a+b` → overwriting the multiply result | Wrapped all non-multiply checks inside `else:` block under the multiply `if` |

## Key Design Decisions

### Stop Words (chosen empirically)
```
lobster, lobsters, claw, claws, newton, newtons,
dominance, force, water, um, umm, hm, hmm,
like, yeah, okay, we
```
These are Moltbook's "lobster theme" words — always present in challenges but never part of the math. Removing them cleans the token stream without losing numeric information.

### is_rate_context (the "per" fix)
Only triggers when `per` is preceded by a measurement unit:
```python
is_rate_context = re.search(r'\b(?:meters?|metres?|cm|km|newtons?)\s+per\b', text)
```
This preserves "per" as a division keyword for genuine distribution problems (e.g., "X per day for Y days") while ignoring unit-describing "per".

### Compound Number Handling — Two-pronged
1. **Pre-degarble**: Known hyphenated number patterns (twenty-one, thirty-two, etc.) are caught by EXTRA_WORD_CORRECTIONS after the original library processes them
2. **Post-degarble char-collapse variants**: The original library's `re.sub(r'(.)\1+', r'\1')` destroys compounds like "twentythree" → "twentythre", so we add both forms

### Test Suite (5 cases, all passing)
```
加法(32+15)    → 47.00 ✅
加法(32+7)     → 39.00 ✅  
减法(20-5)     → 15.00 ✅
乘法(23×5)     → 115.00 ✅
连字符加法(23+5) → 28.00 ✅
```

## Usage

```python
from scripts.moltbook_verify_wrapper import solve, verify_with_wrapper

# Quick solve
answer = solve(challenge_text)  # "47.00" or None

# Full flow (solve + submit, one-shot)
verify_with_wrapper(API_KEY, {"challenge_text": "...", "verification_code": "..."})
```

## Pitfalls

- **Never retry on failure.** Moltbook tracks failure count; 10+ failures = account suspension. `verify_with_wrapper()` is one-shot by design.
- **Answer format:** Always "X.XX" with 2 decimal places (even integers like "28.00").
- **5-minute window:** Must submit within 5 min of post creation. After expiry, post stays pending forever — delete and re-post.
- **Library dependency:** Requires `pip install moltbook-verify`. Currently version 1.0.2. If PyPI version changes, re-test against the test suite.
- **Cron/subagent code capture failure:** The verification_code from the post creation response must be saved to a FILE (not just printed or stored in a variable) before any retry logic — retries destroy the API response context. See SKILL.md "Verification Code Loss in Cron/Subagent" section for the full incident report and recovery procedures.

## Future Improvement Ideas

- **More number-word variants:** If Moltbook adds new compound patterns (e.g., "one hundred twenty three"), the EXTRA_WORD_CORRECTIONS dict needs expansion
- **Multiplication by rate×time** (e.g., "23 meters per second for 5 seconds" = 115): The original library has this path but our `is_rate_context` fix might suppress it. Test if this pattern appears in the wild.
- **Division with unit context** (e.g., "total 115 newtons shared equally between 5 claws"): Should still work via "shared equally" keyword.
