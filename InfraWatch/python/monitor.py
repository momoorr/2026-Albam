import subprocess
import time
import psutil
import socket
import shutil


# 모니터링할 서버 목록
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

# 이전 포트 상태를 저장
previous_port_status = {}


# Ping을 이용하여 서버의 네트워크 연결 상태를 확인
def check_server(ip):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "1000", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0


# TCP 포트를 이용하여 서비스가 실행 중인지 확인
def check_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    result = sock.connect_ex((ip, port))

    sock.close()

    return result == 0

# 장애가 발생한 서비스를 자동으로 다시 실행
def auto_recover(name, port):
    if name == "POS 서버" and port == 8000:
        print("🔧 POS 서비스 자동 복구를 시도합니다.")

        subprocess.Popen(
            ["python", "-m", "http.server", "8000"]
        )

        print("🔄 POS 서비스 재시작 명령을 실행했습니다.")

# 현재 시스템의 CPU, 메모리, 디스크 사용률 확인
def get_system_status():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent

    total, used, free = shutil.disk_usage("C:\\")
    disk = (used / total) * 100

    return cpu, memory, disk


# 5초마다 인프라 상태 확인
while True:

    print("\n===== 무인매장 인프라 상태 =====")

    # 시스템 자원 상태 확인
    cpu, memory, disk = get_system_status()

    print(f"CPU     : {cpu}%")
    print(f"Memory  : {memory}%")
    print(f"Disk    : {disk}%")
    print("-------------------------------")


    # 등록된 서버들을 하나씩 확인
    for name, server in servers.items():

        ip = server["ip"]
        port = server["port"]


        # 서버 상태 확인
        current_status = check_server(ip)

        if current_status:
            print(f"{name} ({ip}) → 🟢 정상")
        else:
            print(f"{name} ({ip}) → 🔴 장애")


        # 서버 상태 변화 확인

        # 처음 확인하는 서버
        if name not in previous_status:
            previous_status[name] = current_status

        # 정상 → 장애
        elif previous_status[name] and not current_status:
            print(f"🚨 [장애 발생] {name}에 장애가 발생했습니다.")

        # 장애 → 정상
        elif not previous_status[name] and current_status:
            print(f"✅ [복구 완료] {name}이 정상적으로 복구되었습니다.")


        # 현재 서버 상태 저장
        previous_status[name] = current_status


        # 서비스 포트 상태 확인
        port_status = check_port(ip, port)

        if port_status:
            print(f"포트 {port} → 🟢 정상")
        else:
            print(f"포트 {port} → 🔴 장애")


        # 포트 상태 변화 확인

        # 처음 확인하는 포트
        if name not in previous_port_status:
            previous_port_status[name] = port_status

        # 정상 → 장애
        elif previous_port_status[name] and not port_status:
            print(
                f"🚨 [서비스 장애] "
                f"{name}의 포트 {port}에 장애가 발생했습니다."
            )

            # 자동복구 호출
            auto_recover(name, port)

        # 장애 → 정상
        elif not previous_port_status[name] and port_status:
            print(
                f"✅ [서비스 복구] "
                f"{name}의 포트 {port}가 정상적으로 복구되었습니다."
            )


        # 현재 포트 상태 저장
        previous_port_status[name] = port_status


    print("===============================")

    # 5초 대기
    time.sleep(5)
