import subprocess
import time
import psutil
import socket

# 모니터링 할 서버 정보
servers = {
    "POS 서버": {
        "ip": "127.0.0.1",
        "port": 8000
    },
    "DB 서버": {
        "ip": "127.0.0.1",
        "port": 3306
    },
    "재고 서버": {
        "ip": "192.0.2.1",
        "port": 8000
    }
}

# 이전 서버 상태를 저장
previous_status = {}

# 서버가 네트워크상 살아있는지 확인(ping 이용)
def check_server(ip):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "1000", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


# 특정 서비스 포트가 잘 열려있는지 확인
def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    result = sock.connect_ex((ip, port))

    sock.close()

    return result == 0


# 현재 PC의 CPU, 메모리, 디스크 사용률 확인
def get_system_status():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("C:\\").percent

    return cpu, memory, disk


while True:
    print("\n===== 무인매장 인프라 상태 =====")

    cpu, memory, disk = get_system_status()

    print(f"CPU     : {cpu}%")
    print(f"Memory  : {memory}%")
    print(f"Disk    : {disk}%")
    print("-------------------------------")

    for name, server in servers.items():

        ip = server["ip"]
        port = server["port"]
        
        current_status = check_server(ip)
        port_status = check_port(ip, port)

        if current_status:
            print(f"{name} ({ip}) → 🟢 정상")
        else:
            print(f"{name} ({ip}) → 🔴 장애")

        print(f"포트 {port} → {'정상' if port_status else '장애'}")

        # 처음 확인하는 서버
        if name not in previous_status:
            previous_status[name] = current_status

        # 정상 → 장애로 변경된 경우
        elif previous_status[name] and not current_status:
            print(f"🚨 [장애 발생] {name}에 장애가 발생했습니다.")

        # 장애 → 정상으로 변경된 경우
        elif not previous_status[name] and current_status:
            print(f"✅ [복구 완료] {name}이 정상적으로 복구되었습니다.")

        previous_status[name] = current_status

    print("===============================")

    time.sleep(5)
