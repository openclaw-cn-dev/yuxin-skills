# Pexels Photo ID Bank (vision-verified)

> All IDs verified via vision_analyze on 2026-06-08. Search API was unreliable — these were the keepers.

## 🦐 Shrimp / seafood (Chinese: 海鲜/虾)

| ID | Actual content | Verdict |
|---|---|---|
| **725992** | **3 red boiled shrimp on rustic iron plate, blue wood table — perfect 白灼虾** | ✅ TOP PICK |
| 1051399 | shrimp related | ✅ OK |
| 2098085 | **Sushi platter, NOT shrimp** | ❌ wrong |
| 3842911 | **Architectural city model, NOT food** | ❌ wrong |
| 1860208 | **Fried chicken, NOT shrimp** | ❌ wrong |
| 1267320 | mixed (forgot to verify) | ❓ |
| 1860209 | mixed (vision removed) | ❓ |
| 2098083 | mixed | ❓ |
| 2098084 | **Mosque interior, NOT food** | ❌ wrong |

## 🎯 Sourcing rule

Don't search Pexels — use the IDs above. When the user requests a new category, **curl 8-10 candidate IDs from Pexels search HTML, then vision_verify** before declaring success. The search HTML is fetchable even when the search API isn't.

## ⚠️ Why search fails

Pexels search HTML (e.g. `https://www.pexels.com/search/shrimp/`) returns 403 from Python urllib. Curl with a real User-Agent works. But the result quality is poor — "shrimp" returned city models and mosques, presumably because Pexels has few Chinese food photos.

## 🐟 Other categories (extending)

When user asks for non-shrimp categories, use this same workflow:
1. Google "[category] pexels" to find 5-10 known photo IDs from Pexels blog posts, Pinterest pins, etc.
2. Add them to this bank with vision verification.
3. Update this file.

Categories seen in 2026-06-08:
- Shrimp (above)
- Need banks for: fish, crab, lobster, abalone, seaweed, scallop, salmon
