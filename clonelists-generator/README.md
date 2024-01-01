# Clonelist Generator

If the table name contains the following regex pattern, assign the priority (the lower the more preferred):

```
priority_mapping = {
    r'\bBAM\b': -1,
    r'\bUltimate\b': -2,
    r'\bTerryRed\b': -3,
    r'\bSLAMT1LT\b': -4,
}
```

For Visual Pinball Set

Prioritize VPX over VP9x...