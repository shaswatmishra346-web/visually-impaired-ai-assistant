# Share Localhost Frontend with Phone on Same Network

Guide to make your Next.js development server accessible from other devices (like phones) on your local Wi-Fi network.

## 📱 Why This Is Needed
By default, `npm run dev` (Next.js) only binds to `localhost` (127.0.0.1), which is only accessible from your own computer. To test on a friend's phone, you need to:
1. Make the server listen on your network interface (not just localhost)
2. Have your friend access it via your computer's local IP address

## 🔧 Step-by-Step Instructions

### **Step 1: Find Your Computer's Local IP Address**
**On Windows:**
1. Open Command Prompt or PowerShell
2. Run: `ipconfig`
3. Look for "IPv4 Address" under your Wi-Fi adapter (e.g., `192.168.1.100` or `10.0.0.5`)

**On Mac:**
1. Open Terminal
2. Run: `ifconfig | grep "inet "` or `ipconfig getifaddr en0`
3. Look for an address like `192.168.x.x` or `10.x.x.x` (not 127.0.0.1)

**On Linux:**
1. Open Terminal
2. Run: `hostname -I` or `ip addr show`
3. Look for an address in the 192.168.x.x or 10.x.x.x range

> 💡 **Example**: Your IP might be `192.168.1.105`

### **Step 2: Start Frontend Accessible on Network**
**Option A: Temporary (for this session only)**
In your frontend directory, run:
```bash
# Windows PowerShell/CMD:
$env:HOST="0.0.0.0"; $env:PORT="3000"; npm run dev

# Or alternatively:
set HOST=0.0.0.0 && set PORT=3000 && npm run dev
```

**Option B: Permanent (add to package.json)**
Edit `frontend/package.json`, change the "dev" script to:
```json
"scripts": {
  "dev": "next dev -H 0.0.0.0 -p 3000",
  "build": "next build",
  "start": "next start",
  "lint": "next lint"
}
```
Then run normally: `npm run dev`

**Option C: Create .env file (recommended)**
Create a file called `.env.local` in your `frontend/` directory with:
```
HOST=0.0.0.0
PORT=3000
```
Then run: `npm run dev` (Next.js will automatically use these)

### **Step 3: Check Firewall Settings (Windows)**
You may need to allow incoming connections:
1. Search for "Windows Defender Firewall"
2. Click "Allow an app through firewall"
3. Click "Change settings" → "Allow another app"
4. Browse to and add Node.js (usually `C:\Program Files\nodejs\node.exe`)
5. Or allow port 3000 specifically:
   - Go to "Advanced settings" → "Inbound Rules" → "New Rule"
   - Port → TCP → Specific port: 3000 → Allow the connection → Apply to Domain/Private/Public

### **Step 4: Have Your Friend Access It**
On your friend's phone (connected to the same Wi-Fi):
1. Open the browser (Chrome, Firefox, Safari)
2. Go to: `http://[YOUR_COMPUTER_IP]:3000`
   - Example: `http://192.168.1.105:3000`
3. They should see your frontend running!

## 📱 Alternative: Using Docker (If Preferred)
If you're using Docker Compose, it may already expose ports. Have your friend access:
```
http://[YOUR_COMPUTER_IP]:3000
```
Make sure your `docker-compose.yml` exposes the frontend port (it likely does by default).

## ⚠️ Important Notes
1. **Same Network Only**: Both devices must be on the same Wi-Fi network
2. **Development Server**: This is for testing only - not for production use
3. **Performance**: May be slower than localhost due to network overhead
4. **Hot Reloading**: Code changes should still trigger updates (may be slightly delayed)
5. **Security**: Only do this on trusted networks - avoid public Wi-Fi

## 🔍 Troubleshooting
- **"Cannot connect"** → Verify IP is correct, both devices on same Wi-Fi, firewall allows port 3000
- **Site not loading** → Try `http://[YOUR_IP]:3000` (some browsers need explicit port)
- **Connection refused** → Double-check the dev server is running and bound to 0.0.0.0
- **Slow loading** → Close bandwidth-heavy apps on your computer/network

## 📋 Quick Reference Card (Share This Part)
```
TO SHARE YOUR LOCALHOST WITH A PHONE:

1. Find your PC IP: 
   - Windows: ipconfig → look for IPv4 Address
   - Mac: ifconfig | grep "inet "
   
2. Start frontend with network access:
   - Option A (temp): set HOST=0.0.0.0 && npm run dev
   - Option B (.env.local): Create file with HOST=0.0.0.0 then npm run dev
   
3. Friend visits on phone: 
   http://[YOUR_IP]:3000
   
4. Allow port 3000 in Windows Firewall if needed
```

---
*File created for sharing localhost access. Your frontend code is in ./frontend/*