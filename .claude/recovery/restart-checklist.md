# Restart Checklist

Run through this checklist after any restart:

- [ ] Git state clean (or expected in-progress changes)
- [ ] .env file present and loaded
- [ ] Dependencies installed (node_modules, venv, etc.)
- [ ] Recovery state.json readable
- [ ] Active work identified (if any)
- [ ] Queue state consistent (no items in both active and completed)
- [ ] No orphaned processes (workers, watchers)
- [ ] Integration credentials valid (if integrations enabled)
