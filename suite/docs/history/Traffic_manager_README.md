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

# 📊 Keenetic Traffic Manager (VnStat Dashboard)

A lightweight, responsive HTML5 dashboard for monitoring network traffic on **Keenetic Routers** running Entware. 

It uses **vnStat** to collect data and generates a static, standalone HTML report with daily, monthly, and hourly statistics. No heavy backend (PHP/Python) required—just a simple shell script and a lightweight web server.

![alt text](https://github.com/mattheweli/Traffic_manager/raw/main/image.png.6b552a7f920526daf9fcbfa1eebe0cd3.png)

## ✨ Features

* **Responsive UI:** Clean, mobile-friendly interface inspired by modern dashboards.
* **Comprehensive Stats:** View Hourly (24h), Daily (30d), Monthly, and Yearly traffic.
* **Visual Graphs:** CSS-based bar charts embedded directly in the table (no heavy JS libraries).
* **Timezone Aware:** Automatically detects and applies the correct system Timezone to avoid offsets in hourly stats.
* **Estimates:** Provides traffic estimation for the current day and month.
* **Zero Dependencies:** The dashboard is a single HTML file + one JS data file.

## 🛠️ Prerequisites

* **Keenetic Router** with Entware installed.
* **Web Server:** `lighttpd` (recommended) or Nginx running on the router.
* **Packages:**
    * `vnstat` (specifically version 2.x, package `vnstat2`)
    * `bash`

## 🚀 Installation

### Method 1: Via Keentool (Recommended)
The easiest way to install and manage this tool is using **Keentool**, the package manager for Keenetic scripts.

1.  Run Keentool in your terminal.
2.  Select **Traffic Manager** from the menu.
3.  Keentool will handle dependency installation (`vnstat2`) and Cron setup automatically.

### Method 2: Manual Installation

1.  **Install Dependencies:**
    ```bash
    opkg update
    opkg install vnstat2 bash
    ```
    *Note: Ensure `vnstatd` service is running (`/opt/etc/init.d/S26vnstatd start`).*

2.  **Download the script:**
    ```bash
    curl -L https://raw.githubusercontent.com/YOUR_USERNAME/keenetic-vnstat/main/traffic_manager.sh -o /opt/bin/traffic_manager.sh
    ```

3.  **Make it executable:**
    ```bash
    chmod +x /opt/bin/traffic_manager.sh
    ```

## ⚙️ Usage

### Manual Run
You can run the script manually to generate the dashboard immediately:

```bash
/opt/bin/traffic_manager.sh [INTERFACE]
```

### Interface: (Optional) e.g., pppoe0, eth3. If omitted, the script auto-detects the active WAN interface.

### Output: The script generates /opt/var/www/vnstat/index.html and vnstat_data.js.

## Automation (Cron)

To keep the dashboard updated, add a job to your crontab (e.g., update every 10 minutes).

1. Edit crontab:
```bash
nano /opt/etc/crontab
```

2. Add the line:
```bash
*/10 * * * * root /opt/bin/traffic_manager.sh pppoe0 >/dev/null 2>&1
```

## 🌐 Accessing the Dashboard
Once generated, access the dashboard via your router's IP and the port configured in your web server (usually port 81 if set up via Keentool).

Example: http://192.168.1.1:81/vnstat/


## 📄 License
This project is open source. Feel free to modify and distribute.




## Alpha distribution
See ../../VERSIONS.md and ../../CHANGELOG_ALPHA.md for current versions and release policy.
