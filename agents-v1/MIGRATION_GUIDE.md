# ✅ Migration Guide: Adding guardian/v1

## 🎯 What You're Doing

Creating `guardian/v1/` by copying `v1/` into the `guardian/` directory. This is **SAFE** and **RECOMMENDED** for better organization!

## 📁 New Structure

```
Gen-Ai-Thon/
├── guardian/
│   ├── agents/          # Old version (legacy, no ADK)
│   ├── backend/         # Backend services
│   ├── docs/            # Documentation
│   └── v1/              # NEW: Modern ADK-based agents ✨
│       ├── agents/      # Google ADK implementation
│       ├── requirements.txt
│       ├── README.md
│       └── ...
└── v1/                  # Original (can keep or remove)
    └── agents/
```

## ✅ Safe Migration Steps

### Step 1: Copy v1 to guardian/v1

```bash
# From project root
cp -r v1 guardian/v1
```

Or on Windows PowerShell:
```powershell
Copy-Item -Path v1 -Destination guardian\v1 -Recurse
```

### Step 2: Verify the Copy

```bash
# Check structure
ls guardian/v1/agents/

# Verify ADK imports still work
cd guardian/v1
python -c "from agents.registry import AgentRegistry; print('✅ ADK agents work!')"
```

### Step 3: Update Imports (If Needed)

Check if anything references `v1/agents` that needs updating:

```bash
# Search for hardcoded paths
grep -r "v1/agents" guardian/
grep -r "from v1.agents" guardian/
```

Most imports use relative paths (`from agents.registry`), so they should work fine!

### Step 4: Test Everything

```bash
cd guardian/v1
python verify_setup.py
python -m agents.run_pipeline VENDOR_001 3
```

## ⚠️ Important Considerations

### 1. **Import Paths**
- ✅ Relative imports (`from agents.registry`) will work fine
- ✅ Module imports (`from agents.registry import ...`) will work fine
- ⚠️ Hardcoded paths (`sys.path.append('v1')`) may need updating

### 2. **Python Path**
When running from `guardian/v1/`, Python will find `agents` package correctly:
```bash
cd guardian/v1
python -m agents.run_pipeline  # ✅ Works!
```

### 3. **Requirements**
The `requirements.txt` in `guardian/v1/` will be identical to `v1/requirements.txt`:
- ✅ `google-adk>=1.0.0` (mandatory)
- ✅ All other dependencies

### 4. **Documentation**
Update any documentation that references paths:
- `README.md` - Update examples if needed
- `QUICKSTART.md` - Update paths if needed

## 🎯 Benefits of This Structure

1. ✅ **Better Organization** - All Guardian AI code under `guardian/`
2. ✅ **Version Clarity** - `guardian/v1/` clearly indicates version
3. ✅ **No Breaking Changes** - All imports work the same
4. ✅ **Easy Migration** - Can update `guardian/agents` later to use ADK

## 📋 Checklist

- [ ] Copy `v1/` to `guardian/v1/`
- [ ] Verify structure: `ls guardian/v1/agents/`
- [ ] Test imports: `python -c "from agents.registry import AgentRegistry"`
- [ ] Run verification: `python verify_setup.py`
- [ ] Test pipeline: `python -m agents.run_pipeline VENDOR_001 3`
- [ ] Update any hardcoded paths in documentation
- [ ] (Optional) Keep or remove original `v1/` directory

## 🔄 What Happens to Original v1/?

You have options:

### Option A: Keep Both (Recommended Initially)
- Keep `v1/` as backup
- Use `guardian/v1/` for development
- Remove `v1/` later once confirmed working

### Option B: Remove Original v1/
```bash
# After verifying guardian/v1 works
rm -rf v1
```

### Option C: Rename for Clarity
```bash
mv v1 v1-backup  # Keep as backup
```

## ✅ Expected Result

After migration:
- ✅ `guardian/v1/agents/` contains Google ADK implementation
- ✅ All imports work correctly
- ✅ Pipeline runs successfully
- ✅ No breaking changes
- ✅ Better project organization

## 🚨 What NOT to Do

- ❌ Don't replace `guardian/agents` with `guardian/v1/agents` (they're different!)
- ❌ Don't delete `v1/` before testing `guardian/v1/`
- ❌ Don't mix old `guardian/agents` with new `guardian/v1/agents`

## 🎉 Summary

**Adding `guardian/v1` is PERFECT!** ✅

- It's just copying to a better location
- No breaking changes
- Better organization
- All ADK features preserved
- Easy to test and verify

Go ahead and create `guardian/v1/` - it's a great organizational improvement! 🚀

