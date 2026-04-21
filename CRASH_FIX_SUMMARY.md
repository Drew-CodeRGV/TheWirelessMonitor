# System Crash Fix & Scoring Improvements

## Issue Summary

The system crashed due to a duplicate route definition, and all articles were showing a score of 60 instead of varying scores based on importance.

## Problems Fixed

### 1. Duplicate Route Causing Crash ✅

**Problem:** Flask route `/api/social_media/fetch_now` was defined twice in `app/main.py`
- Line 1643: First definition
- Line 1800: Duplicate definition (removed)

**Fix:** Removed the duplicate route at line 1800

**Result:** App now starts successfully without errors

### 2. All Articles Showing Score of 60 ✅

**Problem:** Every article had the same score (60) because:
- `cross_source_count` was always 1 (no duplicates were being merged)
- Duplicate detection only ran on NEW articles, not existing ones
- Existing duplicates in database were never merged

**Fix:** 
1. Created `merge_duplicates.py` script to find and merge existing duplicates
2. Merged 36 duplicate articles
3. Updated `cross_source_count` for articles covered by multiple sources
4. Recalculated all scores using new algorithm

**Result:** Scores now range from 11.2 to 52.0, properly differentiating importance

## Score Distribution After Fix

```
Total articles: 282
Highest score: 52.0
Lowest score: 11.2
Average score: 17.7
Median score: 16.0

🟢 High (80+): 0 articles (0.0%)
🟠 Medium (50-79): 1 articles (0.4%)
⚫ Low (<50): 281 articles (99.6%)
```

## Top Articles by Score

1. **Score 52** - Starlink airplane wifi (15 sources) 🔥
2. **Score 44** - Amazon satellite internet (3 sources)
3. **Score 40** - Multiple WiFi 7 and 5G articles (2 sources each)
4. **Score 32-37** - Various tech articles (2 sources)
5. **Score 11-24** - Single source articles

## How Cross-Source Scoring Works

The scoring system now properly rewards articles covered by multiple sources:

- **15 sources** → 50 points (base) + 2 points (other factors) = 52 total
- **3 sources** → 40 points (base) + 4 points (other factors) = 44 total
- **2 sources** → 25 points (base) + 7-15 points (other factors) = 32-40 total
- **1 source** → 5 points (base) + 6-19 points (other factors) = 11-24 total

This correctly surfaces stories that multiple outlets are covering as more important.

## Scripts Created

### 1. `test_startup.py`
Tests if the app can start without errors. Run before deploying.

```bash
python test_startup.py
```

### 2. `merge_duplicates.py`
Finds and merges duplicate articles in the database.

```bash
python merge_duplicates.py
```

### 3. `recalculate_scores.py`
Recalculates Waves scores for all articles using the new algorithm.

```bash
python recalculate_scores.py
```

### 4. `find_duplicates.py`
Diagnostic tool to find potential duplicates without merging.

```bash
python find_duplicates.py
```

### 5. `check_articles.py`
Shows article counts and recent articles with their scores.

```bash
python check_articles.py
```

## Maintenance Workflow

### After Updating Scoring Logic

1. Test startup: `python test_startup.py`
2. Merge duplicates: `python merge_duplicates.py`
3. Recalculate scores: `python recalculate_scores.py`
4. Check distribution looks correct

### Regular Maintenance

The system now automatically:
- Detects duplicates when fetching new RSS articles
- Merges them and increments `cross_source_count`
- Calculates scores for new articles

For existing articles, run `merge_duplicates.py` periodically (weekly/monthly).

## Next Steps

1. ✅ System is stable and can start
2. ✅ Scoring differentiates importance correctly
3. ⏳ Deploy to production server
4. ⏳ Test with live RSS feeds
5. ⏳ Monitor score distribution over time
6. ⏳ Add social media posts (X, LinkedIn) to increase cross-source coverage

## Testing Locally

```bash
# Test startup
python test_startup.py

# Start the app
python run_local.py

# Visit http://localhost:5000
# Check that articles show varying scores
# Verify multi-source articles score higher
```

## Key Improvements

1. **Crash fixed** - Duplicate route removed
2. **Scoring works** - Articles now have varying scores (11-52)
3. **Cross-source detection** - Duplicates are properly merged
4. **Importance surfacing** - Multi-source articles score higher
5. **Diagnostic tools** - Scripts to check and fix issues

## Files Modified

- `app/main.py` - Removed duplicate route
- `recalculate_scores.py` - Updated to process all articles
- Created 5 new diagnostic/maintenance scripts

## Status

✅ **FIXED** - System is stable and scoring works correctly
