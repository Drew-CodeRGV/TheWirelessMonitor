# The Signal - Intelligent Scoring System

## Philosophy

The scoring system answers one key question: **"Who is talking about what?"**

Articles that appear in multiple sources or are about widely-discussed topics get higher scores. This surfaces the truly important stories that the industry is paying attention to.

## Scoring Components (0-100 scale)

### 1. Cross-Source Coverage (0-50 points) ⭐ MOST IMPORTANT

This is the #1 indicator of importance. When multiple outlets cover the same story, it's significant.

**Scoring:**
- 5+ sources: **50 points** (Maximum - industry-wide coverage)
- 3-4 sources: **40 points** (Very important - major story)
- 2 sources: **25 points** (Important - notable coverage)
- 1 source: **5 points** (Baseline - single mention)

**How it works:**
- When RSS feeds are fetched, duplicate detection runs
- Articles with 80%+ title similarity are merged
- Each merge increments `cross_source_count`
- Higher count = higher score

**Example:**
```
"Apple announces WiFi 7 support in new iPhone"
- TechCrunch covers it: cross_source_count = 1, score = 5
- The Verge covers it: cross_source_count = 2, score = 25
- Ars Technica covers it: cross_source_count = 3, score = 40
- Engadget covers it: cross_source_count = 4, score = 40
- Wired covers it: cross_source_count = 5, score = 50
```

### 2. Topic Buzz (0-30 points) 📈

How many other articles are discussing the same topic?

**Scoring:**
- 10+ related articles: **30 points** (Hot topic)
- 5-9 related articles: **20 points** (Trending topic)
- 2-4 related articles: **10 points** (Discussed topic)
- 0-1 related articles: **0 points** (Isolated story)

**How it works:**
- Extracts key words from title (removes stop words)
- Counts articles in last 3 days with 2+ matching key words
- More matches = more buzz

**Example:**
```
"Qualcomm announces new 5G modem chip"
Key words: qualcomm, announces, 5g, modem, chip

Other articles in last 3 days:
- "Qualcomm's 5G technology leads market" (3 matches)
- "New 5G modem from MediaTek" (2 matches)
- "Chip shortage affects 5G rollout" (2 matches)
Total: 3 related articles = 10 points
```

### 3. Source Authority (0-15 points) 🏆

Quality of the source matters.

**Tier 1 - Industry Authorities (15 points):**
- Fierce Wireless
- RCR Wireless News
- Light Reading
- Mobile World Live

**Tier 2 - Major Tech Outlets (10 points):**
- TechCrunch
- The Verge
- Ars Technica
- Wired
- Engadget

**Tier 3 - General Tech (8 points):**
- IEEE Spectrum
- ZDNet
- Network World

**Tier 4 - Aggregators (5 points):**
- Google News feeds
- Other sources

### 4. Recency Boost (0-10 points) ⏰

Newer articles get a temporary boost.

**Scoring:**
- Last 6 hours: **10 points**
- Last 24 hours: **7 points**
- Last 2 days: **4 points**
- Last 3 days: **2 points**
- Older: **0 points**

This ensures breaking news surfaces quickly.

### 5. Engagement Bonus (0-10 points) 💬

Social media signals (when available).

**Scoring:**
- 100+ interactions: **10 points**
- 50-99 interactions: **7 points**
- 20-49 interactions: **4 points**
- 5-19 interactions: **2 points**
- <5 interactions: **0 points**

Interactions = likes + shares + comments

### 6. Relevance Bonus (0-10 points) 📡

How relevant to wireless/WiFi industry?

**Scoring:**
- 70%+ relevance: **10 points** (Core wireless topic)
- 50-69% relevance: **7 points** (Highly relevant)
- 30-49% relevance: **4 points** (Relevant)
- 10-29% relevance: **2 points** (Somewhat relevant)
- <10% relevance: **0 points** (Tangential)

Based on WiFi/wireless keyword density.

## Total Score Calculation

**Maximum possible: 125 points**
**Scaled to: 0-100 for display**

Formula: `final_score = min(raw_score * 0.8, 100)`

## Score Interpretation

### 🟢 High Priority (80-100)
- Multiple sources covering
- Hot topic with lots of buzz
- From authoritative sources
- Recent and engaging
- **Action:** Must read, industry-critical

### 🟠 Medium Priority (50-79)
- 2-3 sources or trending topic
- Good source quality
- Relevant and timely
- **Action:** Should read, important

### ⚫ Low Priority (0-49)
- Single source
- Limited buzz
- Lower-tier source or older
- **Action:** Optional reading

## Examples

### Example 1: Major Industry Announcement

**Article:** "Qualcomm Unveils WiFi 7 Chipset for Smartphones"

**Scoring:**
- Cross-source: 4 sources = **40 points**
- Topic buzz: 8 related articles = **20 points**
- Source: Fierce Wireless = **15 points**
- Recency: 3 hours old = **10 points**
- Engagement: 75 shares = **7 points**
- Relevance: 85% = **10 points**

**Total:** 102 points → **Scaled: 81.6** → 🟢 **82**

### Example 2: Niche Technical Update

**Article:** "New WiFi Alliance Certification Process"

**Scoring:**
- Cross-source: 1 source = **5 points**
- Topic buzz: 1 related article = **0 points**
- Source: IEEE Spectrum = **8 points**
- Recency: 36 hours old = **4 points**
- Engagement: 12 shares = **2 points**
- Relevance: 90% = **10 points**

**Total:** 29 points → **Scaled: 23.2** → ⚫ **23**

### Example 3: Trending Topic

**Article:** "5G Rollout Accelerates in Rural Areas"

**Scoring:**
- Cross-source: 3 sources = **40 points**
- Topic buzz: 12 related articles = **30 points**
- Source: TechCrunch = **10 points**
- Recency: 18 hours old = **7 points**
- Engagement: 45 shares = **4 points**
- Relevance: 75% = **10 points**

**Total:** 101 points → **Scaled: 80.8** → 🟢 **81**

## Duplicate Detection

### How It Works

1. **Exact URL Match:** Check if URL already exists
2. **Title Similarity:** 80% threshold using SequenceMatcher
3. **Substring Match:** One title contains the other
4. **Title Cleaning:** Removes prefixes, source attributions

### Cleaning Process

Before comparing:
- Convert to lowercase
- Remove prefixes: "Breaking:", "Exclusive:", "Report:", etc.
- Remove source attributions: " - TechCrunch", " | The Verge"
- Normalize whitespace

### Examples

**Detected as Duplicates:**

```
"Apple Announces WiFi 7 Support"
"Apple announces WiFi 7 support in new devices"
→ 95% similarity → DUPLICATE

"Breaking: Qualcomm Unveils 5G Chip"
"Qualcomm Unveils 5G Chip - TechCrunch"
→ After cleaning: identical → DUPLICATE

"WiFi 6E Adoption Grows"
"Report: WiFi 6E Adoption Grows in Enterprise"
→ Substring match → DUPLICATE
```

**NOT Duplicates:**

```
"Apple Announces WiFi 7"
"Samsung Announces WiFi 7"
→ 75% similarity → DIFFERENT STORIES

"5G Rollout in US"
"5G Rollout in Europe"
→ 85% similarity but different regions → DIFFERENT STORIES
```

## Recalculating Scores

### When to Recalculate

- After updating scoring algorithm
- After merging duplicates
- After fetching new articles
- Daily maintenance

### How to Recalculate

```bash
# Recalculate all scores from last 7 days
python recalculate_scores.py
```

This will:
1. Process all articles from last 7 days
2. Apply new scoring algorithm
3. Show score distribution
4. Display top 10 articles

### Automatic Recalculation

Scores are automatically calculated:
- When new articles are fetched
- When duplicates are merged
- On page load (for unscored articles)

## Tuning the System

### Increase Cross-Source Weight

In `calculate_waves_score()`:
```python
if cross_source_count >= 5:
    score += 60  # Increase from 50
elif cross_source_count >= 3:
    score += 50  # Increase from 40
```

### Adjust Duplicate Threshold

In `detect_duplicate_articles()`:
```python
if similarity >= 0.75:  # Lower from 0.80 to catch more
```

### Change Topic Buzz Window

In `calculate_waves_score()`:
```python
WHERE DATE(published_date) >= DATE('now', '-5 days')  # Change from 3 days
```

### Adjust Source Tiers

In `calculate_waves_score()`:
```python
# Add new Tier 1 sources
if any(x in feed_lower for x in ['fierce', 'rcr', 'your-source']):
    score += 15
```

## Monitoring

### Check Score Distribution

```bash
sqlite3 data/wireless_monitor.db

SELECT 
    CASE 
        WHEN waves_score >= 80 THEN 'High (80+)'
        WHEN waves_score >= 50 THEN 'Medium (50-79)'
        ELSE 'Low (<50)'
    END as category,
    COUNT(*) as count,
    ROUND(AVG(waves_score), 1) as avg_score
FROM articles
WHERE DATE(published_date) >= DATE('now', '-7 days')
GROUP BY category;
```

### Find Multi-Source Articles

```bash
SELECT title, cross_source_count, waves_score
FROM articles
WHERE cross_source_count >= 3
ORDER BY cross_source_count DESC, waves_score DESC
LIMIT 20;
```

### Check Topic Buzz

```bash
SELECT 
    SUBSTR(title, 1, 50) as title_preview,
    COUNT(*) as similar_count
FROM articles
WHERE DATE(published_date) >= DATE('now', '-3 days')
GROUP BY LOWER(SUBSTR(title, 1, 30))
HAVING similar_count >= 3
ORDER BY similar_count DESC;
```

## Best Practices

### For Accurate Scoring

1. ✅ Fetch from multiple sources regularly
2. ✅ Let duplicate detection merge articles
3. ✅ Recalculate scores after major updates
4. ✅ Monitor score distribution
5. ✅ Tune thresholds based on your needs

### For Better Duplicate Detection

1. ✅ Use consistent RSS feeds
2. ✅ Fetch frequently (every 30 min)
3. ✅ Check logs for merge activity
4. ✅ Adjust similarity threshold if needed

### For Topic Buzz

1. ✅ Maintain diverse feed sources
2. ✅ Include industry-specific feeds
3. ✅ Include general tech feeds
4. ✅ Monitor trending topics

## Troubleshooting

### All Scores Are the Same ✅ FIXED

**Problem:** Every article shows score of 60
**Cause:** Cross-source count not being incremented (duplicates not merged)
**Fix:** 
1. Run `python merge_duplicates.py` to merge existing duplicates
2. Run `python recalculate_scores.py` to apply new scores
3. Check logs for "Merging duplicate" messages

**Status:** Fixed - scores now range from 11-52 based on importance

### Scores Too Low

**Problem:** Important articles scoring <50
**Cause:** Thresholds too strict
**Fix:**
1. Lower duplicate similarity threshold (0.75 instead of 0.80)
2. Increase source authority points
3. Increase topic buzz points

### Scores Too High

**Problem:** Unimportant articles scoring >80
**Cause:** Thresholds too loose
**Fix:**
1. Raise duplicate similarity threshold (0.85 instead of 0.80)
2. Require more sources for high scores
3. Decrease recency boost

### Duplicates Not Merging

**Problem:** Same story appearing multiple times
**Cause:** Titles too different or threshold too strict
**Fix:**
1. Check title cleaning logic
2. Lower similarity threshold
3. Add more title cleaning rules
4. Check logs for similarity scores

## Conclusion

The scoring system is designed to surface what matters: stories that multiple sources are covering and topics that the industry is discussing. By focusing on cross-source coverage and topic buzz, we ensure the most important wireless industry news rises to the top.

The system is tunable and transparent - you can see exactly why each article got its score and adjust the weights to match your priorities.
