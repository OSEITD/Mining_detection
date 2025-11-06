# 📱 How to Install Chingola Mining Monitor as a PWA

## What is a PWA?
A Progressive Web App (PWA) is a website that can be installed on your device like a native app. It works offline, loads faster, and provides a better user experience.

---

## 💻 Desktop Installation (Chrome, Edge, Brave)

### Method 1: Install Icon
1. Open http://localhost:8510 in your browser
2. Look in the **address bar** (right side, near the star/bookmark icon)
3. You'll see a **⊕ Install** icon or **🖥️ Computer icon**
4. Click it
5. Click **"Install"** in the popup
6. The app will open in its own window!

### Method 2: Browser Menu
1. Open http://localhost:8510
2. Click the browser **Menu (⋮)** (three dots in top right)
3. Look for **"Install Chingola Mining Monitor..."** or **"Install app"**
4. Click it
5. Click **"Install"**

### ✅ Success Signs:
- App opens in a standalone window (no browser tabs/address bar)
- Desktop shortcut created
- App appears in Start Menu (Windows) or Applications (Mac)

---

## 📱 Mobile Installation - Android (Chrome, Edge)

1. Open http://192.168.1.172:8510 in Chrome or Edge
   - Use your network IP, not localhost
2. Tap the **Menu (⋮)** button (three dots in top right)
3. Look for one of these options:
   - **"Add to Home screen"**
   - **"Install app"**
   - **"Install Chingola Mining Monitor"**
4. Tap it
5. Tap **"Add"** or **"Install"** in the popup
6. The app icon appears on your home screen!

### ✅ Success Signs:
- App icon on home screen
- Opens in full screen (no browser UI)
- Works offline

---

## 📱 Mobile Installation - iOS (Safari)

1. Open http://192.168.1.172:8510 in **Safari** (must be Safari!)
   - Use your network IP, not localhost
2. Tap the **Share** button at the bottom (□↑ box with arrow)
3. Scroll down in the menu
4. Tap **"Add to Home Screen"**
5. Edit the name if you want (optional)
6. Tap **"Add"** in the top right
7. The app icon appears on your home screen!

### ✅ Success Signs:
- App icon on home screen
- Opens in full screen
- Shows splash screen

---

## 🎯 Benefits of Installing

✅ **Offline Access** - View mining data without internet  
✅ **Faster Loading** - Resources cached locally  
✅ **Full Screen** - No browser UI clutter  
✅ **Quick Access** - Desktop shortcut or home screen icon  
✅ **Native Feel** - Looks and feels like a real app  
✅ **Push Notifications** - Get mining activity alerts (future)  

---

## ⚠️ Troubleshooting

### "I don't see the install option!"

**Desktop:**
- Make sure you're using **Chrome, Edge, or Brave** (latest version)
- Firefox doesn't support PWA installation on desktop
- Look carefully in the address bar - the icon may be small
- Try Method 2 (browser menu)

**Android:**
- Use **Chrome** or **Edge** (not Firefox or other browsers)
- Make sure you're visiting the actual site, not just reading about it
- Some Android browsers don't support PWA installation

**iOS:**
- **Must use Safari** - Chrome and other browsers don't support PWA on iOS
- Make sure you're tapping the Share button at the **bottom** of Safari
- If you don't see "Add to Home Screen", scroll down in the share menu

### "It's asking for location permissions"
- Click **"Allow"** if you want to use the GPS features for reporting
- Click **"Block"** if you prefer manual entry
- You can change this later in browser settings

### "The app looks the same as the website"
- That's normal! PWAs look identical to the website
- The difference is:
  - They work offline
  - They load faster (cached)
  - They open in their own window
  - They can receive notifications

### "Can I uninstall it?"

**Desktop:**
1. Open the installed app
2. Click the menu (⋮) in the app window
3. Click "Uninstall..." or go to Settings → Apps → Find the app → Uninstall

**Android:**
1. Long-press the app icon
2. Tap "Uninstall" or drag to uninstall

**iOS:**
1. Long-press the app icon
2. Tap "Remove App" → "Delete App"

---

## 🔧 For Developers / Testing

### Verify PWA Installability

1. Open Chrome DevTools (F12)
2. Go to **Application** tab
3. Check **Manifest** - should show all icons and settings
4. Check **Service Workers** - should show active worker at `/static/service-worker.js`
5. Run **Lighthouse** audit (in DevTools) → Check "PWA" score

### Common Issues

- **Manifest not loading**: Check `/static/manifest.json` is accessible
- **Service worker not registering**: Check Console for errors
- **Icons missing**: Need at least 192x192 and 512x512 PNG icons in `/static/`
- **HTTPS required**: PWAs require HTTPS (except on localhost)

---

## 📚 Additional Resources

- **Web.dev PWA Guide**: https://web.dev/progressive-web-apps/
- **MDN PWA Documentation**: https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps
- **Google PWA Checklist**: https://web.dev/pwa-checklist/

---

## 🆘 Still Need Help?

If you're still having trouble installing the app:

1. **Check your browser version** - Update to the latest version
2. **Try a different browser** - Chrome and Edge work best
3. **Clear browser cache** - Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
4. **Restart your device** - Sometimes helps!
5. **Contact support** - Provide screenshots of what you see

---

**Made with ❤️ for Zambia | © 2025 Chingola Mining Monitor**
