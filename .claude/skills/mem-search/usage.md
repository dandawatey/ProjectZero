# Usage: mem-search

## How to Invoke
```
/mem-search <query>                    # Layer 1 — search (always start here)
/mem-search timeline <observation-id>  # Layer 2 — context window around an obs
/mem-search fetch <id1> [id2] [id3...] # Layer 3 — full content for selected IDs
```

## Examples
```
/mem-search auth bug login             # find past auth-related observations
/mem-search timeline obs_abc123        # see 5 obs before/after obs_abc123
/mem-search fetch obs_abc123 obs_def456 # fetch full content of two specific obs
```

## Expected Output

### Layer 1
```
Results for "auth bug login" (~50 tokens)
1. [obs:abc123] 2026-04-14T10:00Z  score:0.95  "Fixed auth bug in login flow..."
2. [obs:def456] 2026-04-13T08:30Z  score:0.82  "JWT expiry issue caused silent logout..."
```

### Layer 2
```
Timeline around [obs:abc123] (~200 tokens)
-5  [obs:aaa111] ...
-4  [obs:bbb222] ...
...
[0] [obs:abc123] ← target
...
+5  [obs:zzz999] ...
```

### Layer 3
```
Full content — [obs:abc123]
<full observation text>

Full content — [obs:def456]
<full observation text>
```

## Worker not running
```
claude-mem worker not running. Start with: npx claude-mem start
Or check if CLAUDE_MEM_PORT is set correctly (default: 37777)
```
