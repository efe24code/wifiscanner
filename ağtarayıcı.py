import subprocess
import platform
import re
import socket
import struct
import time

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print("Yerel IP alınamadı:", e)
        return None

def get_network_range():
    local_ip = get_local_ip()
    if local_ip:
        network_prefix = ".".join(local_ip.split(".")[:3])
        return f"{network_prefix}.1/24"
    return None

def scan_wifi():
    system_os = platform.system()
    networks = []
    
    if system_os == "Windows":
        try:
            result = subprocess.run(["netsh", "wlan", "show", "networks", "mode=Bssid"], capture_output=True, text=True, check=True)
            output = result.stdout
            
            ssids = re.findall(r'SSID \d+ : (.+)', output)
            signals = re.findall(r'Signal : (.+)%', output)
            securities = re.findall(r'Authentication : (.+)', output)
            
            for i in range(len(ssids)):
                networks.append({
                    "SSID": ssids[i],
                    "Signal": signals[i] if i < len(signals) else "Unknown",
                    "Security": securities[i] if i < len(securities) else "Unknown"
                })
        except Exception as e:
            print("Hata oluştu:", e)
    
    elif system_os in ["Linux", "Darwin"]:
        try:
            result = subprocess.run(["nmcli", "dev", "wifi", "list"], capture_output=True, text=True, check=True)
            output = result.stdout.split("\n")[1:]  # İlk satır başlık
            
            for line in output:
                columns = line.split()
                if len(columns) < 3:
                    continue
                ssid = columns[0]
                signal = columns[-2]
                security = columns[-1]
                
                networks.append({"SSID": ssid, "Signal": signal, "Security": security})
        except Exception as e:
            print("Hata oluştu:", e)
    else:
        print("Bu işletim sistemi desteklenmiyor!")
    
    return networks

def scan_network():
    network_range = get_network_range()
    if not network_range:
        print("Ağ taraması yapılamıyor. Yerel IP alınamadı.")
        return []
    
    print(f"Ağa bağlı cihazlar taranıyor: {network_range}\n")
    try:
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True, check=True)
        devices = []
        for line in result.stdout.split("\n"):
            match = re.search(r'\((.*?)\)\s+at\s+([0-9A-Fa-f:]+)', line)
            if match:
                ip = match.group(1)
                mac = match.group(2)
                devices.append({"IP": ip, "MAC": mac})
        return devices
    except Exception as e:
        print("Hata oluştu:", e)
        return []

# Tarama yap ve sonucu göster
def main():
    print("Wi-Fi Ağları Tarama Başlatıldı...\n")
    wifi_list = scan_wifi()
    if not wifi_list:
        print("Hiçbir ağ bulunamadı!")
    else:
        print("Bulunan Ağlar:")
        print("-" * 40)
        for wifi in wifi_list:
            print(f"SSID: {wifi['SSID']}, Sinyal: {wifi['Signal']}%, Güvenlik: {wifi['Security']}")
        print("-" * 40)
    
    print("Ağa Bağlı Cihazlar Taranıyor...\n")
    devices = scan_network()
    if not devices:
        print("Bağlı cihaz bulunamadı!")
    else:
        print("Bağlı Cihazlar:")
        print("-" * 40)
        for device in devices:
            print(f"IP: {device['IP']}, MAC: {device['MAC']}")
        print("-" * 40)
    
    print("1 dakika bekleniyor...")
    time.sleep(60)
    print("Tarama tamamlandı.")
    
    input("Çıkmak için Enter'a basın...")

if __name__ == "__main__":
    main()