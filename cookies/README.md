# Cookie Setup for YouTube Downloads

This folder contains cookie files used to bypass YouTube's bot detection when downloading videos.

## Why Cookies?

YouTube blocks yt-dlp downloads by detecting automated requests. Using cookies from real browser sessions makes downloads appear as legitimate user activity, achieving 95%+ success rate.

## Setup Instructions

### Step 1: Install Browser Extension

Install **"Get cookies.txt LOCALLY"** extension:
- Chrome: https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc
- Firefox: https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/

### Step 2: Export Cookies

1. **Login to YouTube** with a Google account
2. **Click the extension icon** in your browser
3. **Click "Export"** to download cookies.txt
4. **Save the file** in this folder as `cookies1.txt`

### Step 3: Add Multiple Cookies (Recommended)

For production use with 100s of concurrent downloads:

1. **Use 3-5 different Google accounts**
2. **Export cookies from each account**
3. **Save as:** `cookies1.txt`, `cookies2.txt`, `cookies3.txt`, etc.

Example:
```
cookies/
├── cookies1.txt  (account1@gmail.com)
├── cookies2.txt  (account2@gmail.com)
├── cookies3.txt  (account3@gmail.com)
├── cookies4.txt  (account4@gmail.com)
└── cookies5.txt  (account5@gmail.com)
```

## How It Works

The system automatically:
- ✅ Rotates between cookie files
- ✅ Tracks success/fail rates for each cookie
- ✅ Temporarily blocks cookies that fail too often
- ✅ Selects best available cookie for each download
- ✅ Handles 100s of concurrent downloads
- ✅ Auto-recovers from temporary blocks

## Cookie Maintenance

**Cookies expire after ~6 months.** When downloads start failing:

1. Re-export fresh cookies from your browser
2. Replace old cookie files
3. System will automatically use new cookies

## Security Notes

- ✅ Cookies are stored locally only
- ✅ Never committed to git (in .gitignore)
- ✅ Only used for YouTube downloads
- ⚠️  Don't share cookie files (they contain your login session)

## Troubleshooting

### "No cookie files found"
- Make sure cookie files are in this folder
- Files must have `.txt` extension
- Check file names: `cookies1.txt`, `cookies2.txt`, etc.

### "All cookies blocked"
- Wait 5 minutes for auto-recovery
- Or add fresh cookies from different accounts

### Downloads still failing
- Re-export fresh cookies (old ones may have expired)
- Use cookies from different Google accounts
- Make sure you're logged into YouTube when exporting

## Stats & Monitoring

Check cookie pool health:
```python
from src.tools.downloader import VideoDownloader

downloader = VideoDownloader()
stats = downloader.get_stats()
print(stats)
```

Output:
```json
{
  "total_cookies": 5,
  "available": 4,
  "blocked": 1,
  "total_downloads": 247,
  "success_rate": 0.96,
  "cookies": [...]
}
```

## Production Tips

1. **Start with 3-5 cookies** - Good balance for most use cases
2. **Monitor success rates** - Replace cookies below 80% success rate
3. **Rotate accounts** - Don't use same account for all cookies
4. **Fresh cookies** - Re-export every 3-6 months
5. **Scale up** - Add more cookies if hitting rate limits

---

**Need help?** Check the main README or open an issue.
