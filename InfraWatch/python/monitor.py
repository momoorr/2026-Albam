import subprocess
import time

# 모니터링 할 서버 정보
servers = {
    "POS 서버": "127.0.0.1",
    "DB 서버": "127.0.0.1",
    "재고 서버": "192.0.2.1"
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


while True:
    print("\n===== 무인매장 인프라 상태 =====")

    for name, ip in servers.items():

        current_status = check_server(ip)

        if current_status:
            print(f"{name} ({ip}) → 🟢 정상")
        else:
            print(f"{name} ({ip}) → 🔴 장애")

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
