> Local major release 2026-10-13: see ../../CHANGELOG_MAJOR.md for component versions, changes and router-validation limits.

<div align="center">

### ❤️ Support the Project
If you found this project helpful, consider buying me a coffee!

<a href="https://paypal.me/MatteoRosettani">
  <img src="https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white" alt="Donate with PayPal" />
</a>

<a href="https://revolut.me/matthew_eli">
  <img src="https://img.shields.io/badge/Revolut-black?style=for-the-badge&logo=revolut&logoColor=white" alt="Donate with Revolut" />
</a>

</div>

# Keenetic PingTool ⚡

It logs Ping, Jitter, and Packet Loss to a SQLite database, visualizes the data via a responsive HTML5 dashboard using Chart.js, and automatically runs MTR diagnostics when latency spikes.

![alt text](https://github.com/mattheweli/keenetic-pingtool/raw/main/image.png.77b9f0fb50a587debc5a37fd6e24d80f.png)

## Features

- 📊 **Dashboard:** Generates a standalone `pingtool.html` file with interactive graphs (Ping, Jitter, Loss).
- 💾 **SQLite Storage:** Efficiently stores historical data with auto-rotation (default 45 days).
- 🔍 **Auto-Diagnostics:** Trigger an `MTR` trace automatically when ping exceeds a threshold or packet loss is detected.
- 🚀 **Lightweight:** Written in Bash, optimized for routers.

## Prerequisites

This script requires **Entware** installed on your Keenetic/Router.
You need to install the following packages via SSH:

```bash
opkg update
opkg install bash sqlite3-cli ping mtr
```
*Note: `traceroute` is used as a fallback if `mtr` is missing.*

---

## 🛠️ Installation

You can install the tool automatically using **Keentool** (recommended) or manually.

### Option 1: Automatic Installation (Recommended) ⚡
Use **Keentool** to install, update, and configure the Ping Monitor and its dependencies automatically.

1.  Run the following command in your SSH terminal:
    ```bash
    curl -sL https://raw.githubusercontent.com/mattheweli/keentool/main/keentool -o /opt/bin/keentool && chmod +x /opt/bin/keentool && /opt/bin/keentool
    ```
2.  Select **2. Ping Monitor** from the menu.
3.  Choose **1. Install / Update**.
    * The tool will ask if you want to enable **IPv4 Only** mode or use Dual Stack (IPv4+IPv6).
    * It will automatically configure the Crontab schedule for you.

---

### Option 2: Manual Installation 🔧

1.  **Download:** Place the `pingtool.sh` script in `/opt/bin/` (or any persistent folder).
2.  **Permissions:**
    ```bash
    chmod +x /opt/bin/pingtool.sh
    ```
3.  **Configuration:** Edit the top section of `/opt/bin/pingtool.sh` to customize:
    * `PING_TARGET`: The IP to ping (Default: 8.8.8.8).
    * `TRIGGER_LATENCY`: Threshold in ms to trigger MTR (Default: 30ms).
    * `WEB_DIR`: Where to save the HTML file (Default: `/opt/var/www`).

4.  **Automation (Cron):**
    Add a cron job to run it every minute.
    ```bash
    nano /opt/etc/crontab
    ```
    Add this line:
    ```bash
    */1 * * * * root /opt/bin/pingtool.sh > /dev/null 2>&1
    ```

---

## 🖥️ Usage

### Manual Run
You can run the script manually to test it or check the output:
```bash
/opt/bin/pingtool.sh
```

### Viewing the Dashboard
The script generates `pingtool.html` in `/opt/var/www`. If you have the Entware Web Server (nginx/lighttpd) running, you can access it via browser:
`http://YOUR_ROUTER_IP:81/ping/` (Port depends on your setup).

Alternatively, expose the folder via SMB or FTP to open the file locally.

## 🌍 Web Server Setup (Lighttpd)

To view the dashboard in your browser, ensure **Lighttpd** is configured to serve the directory where the script saves the HTML file (`/opt/var/www`).

1.  **Install Lighttpd** (if not installed):
    ```bash
    opkg install lighttpd
    ```

2.  **Configure Lighttpd:**
    Edit the configuration file:
    ```bash
    nano /opt/etc/lighttpd/lighttpd.conf
    ```
    Make sure these two lines are set correctly:
    ```bash
    # The folder where html files are saved
    server.document-root = "/opt/var/www"
    # Use port 81 (or 8081) to avoid conflict with Router Admin UI
    server.port = 81
    ```

3.  **Restart the Service:**
    ```bash
    /opt/etc/init.d/S80lighttpd restart
    ```

4.  **Access the Dashboard:**
    Open your browser and navigate to: `http://YOUR_ROUTER_IP:81/ping/`




## Alpha distribution
See ../../VERSIONS.md and ../../CHANGELOG_ALPHA.md for current versions and release policy.
