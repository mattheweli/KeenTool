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

# 📂 SMB Backup Tool for Keenetic (Entware)

A robust, lightweight Bash script designed to backup your **Keenetic Router** configuration and local directories (Entware environment) to a remote **SMB/CIFS share** (NAS, Windows Share, Linux Server).

It handles compression, automatic rotation (retention policy), and logging.

## ✨ Features

* **Smart Backup:** Compresses directories into `tar.gz` archives with timestamps.
* **Retention Policy:** Automatically deletes backups older than `X` days to save storage space.
* **SMB/CIFS Support:** Connects to standard Windows/NAS shares using Entware's Samba client.
* **Logging:** Detailed operation logs for troubleshooting.
* **Keentool Ready:** Fully integrated with the [Keentool Manager](https://github.com/mattheweli/keentool).

## 🛠️ Prerequisites

You need a Keenetic router with **Entware** installed.

Required packages:
* `bash`
* `tar`
* `coreutils-date` (for accurate date calculations)
* `samba4-client` (for SMB connectivity)

**Note:** If you install via **Keentool**, these dependencies are checked and installed automatically.

## 🚀 Installation

### Method 1: Via Keentool (Recommended)
The easiest way to install and manage this tool is using **Keentool**, the package manager for Keenetic scripts.

1.  Run Keentool.
2.  Select **SMB Backup Tool** from the menu.
3.  Keentool will install the script and all required dependencies (`samba4-client`, etc.).

### Method 2: Manual Installation
1.  Connect to your router via SSH.
2.  Download the script:
    ```bash
    curl -L https://raw.githubusercontent.com/mattheweli/SMB_Backup_tool/main/smb_backup_tool.sh -o /opt/bin/smb_backup_tool.sh
    ```
3.  Make it executable:
    ```bash
    chmod +x /opt/bin/smb_backup_tool.sh
    ```
4.  Install dependencies manually:
    ```bash
    opkg update
    opkg install bash tar coreutils-date samba4-client
    ```

## ⚙️ Configuration

**Important:** You must edit the script to set your share credentials before running it.

Open the script:
```bash
nano /opt/bin/smb_backup_tool.sh
```

Edit the CONFIGURATION section at the top:
```bash
# --- CONFIGURATION ---
SMB_SERVER="//192.168.1.100/Backups"   # IP and Share Name of your NAS/PC
SMB_USER="your_username"               # SMB Username
SMB_PASS="your_password"               # SMB Password
MOUNT_POINT="/opt/mnt/backup_share"    # Local mount point (auto-created)
SOURCE_DIR="/opt/etc"                  # Directory to backup (e.g., /opt/etc or /opt/home)
RETENTION_DAYS=30                      # How many days to keep backups
LOG_FILE="/opt/var/log/smb_backup.log" # Log file location
```




## Alpha distribution
See ../../VERSIONS.md and ../../CHANGELOG_ALPHA.md for current versions and release policy.
