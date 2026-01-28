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

# 📦 Keentool Manager

**Keentool** is an advanced CLI Package Manager designed for **Keenetic Routers** running Entware. 

It acts as an "App Store," allowing you to easily install, update, and manage powerful scripts like **Traffic Manager**, **Ping Monitor**, **Firewall Suite**, and **SMB Backup** without dealing with complex manual commands.

## ✨ Features

* **Interactive Menu:** Simple, text-based UI managed via SSH.
* **One-Click Install:** Automatically downloads scripts, sets permissions, and creates directories.
* **Dependency Resolution:** Automatically checks and installs required Entware packages (e.g., `vnstat2`, `ipset`, `lighttpd`) for each tool.
* **Smart Updates:** Checks remote versions (GitHub) against local files. Prevents overwriting if you have a newer local version (Dev Mode).
* **Cron Management:** Easily view, add, or remove automated jobs for your tools.
* **System Setup:** Auto-configures the Web Server (`lighttpd` on port 81) for dashboard visualization.

## 🧰 Included Tools

| Tool | Description |
| :--- | :--- |
| **📊 Traffic Manager** | Beautiful HTML5 dashboard for daily/monthly traffic usage (VnStat). |
| **⚡ Ping Monitor** | Real-time latency tracking with graphs for IPv4 and IPv6. |
| **🛡️ Firewall Suite** | Advanced blocklists (IP sets), GeoIP stats, and active monitoring. |
| **📂 SMB Backup** | Auto-backup your router config/files to a NAS or Windows Share. |

## 🚀 Installation (One-Line Command)

You can install Keentool with a single command. 

1.  Connect to your router via SSH.
2.  Copy and paste the following line:

```bash
opkg update && opkg install curl && curl -L https://raw.githubusercontent.com/mattheweli/keentool/main/keentool -o /opt/bin/keentool && chmod +x /opt/bin/keentool
```

(This command installs curl if missing, downloads the script to /opt/bin, and makes it executable).

## 📖 Usage
Once installed, simply type keentool in your terminal to launch the manager:

```bash
keentool
```

### First Run Recommended Steps:
1. Select option 0. Setup System Dependencies first. This ensures lighttpd (Web Server) and common tools are installed.
2. Select any tool (e.g., 1. Traffic Manager) to install it.
3. Access your dashboards at http://YOUR_ROUTER_IP:81.

## 🔄 Updating Keentool
Keentool is designed to manage other tools. To update Keentool itself, simply re-run the installation command above.

## 📄 License
This project is open source. Feel free to contribute!
