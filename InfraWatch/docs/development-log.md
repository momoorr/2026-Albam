## 개발 기록

### 2026-09-03

#### 1. 서버 상태 모니터링 기능 구현

무인매장 인프라 장애를 감지하기 위한 기본 모니터링 기능을 구현했다.

먼저 무인매장의 주요 인프라를 가정하여 POS 서버, DB 서버, 재고 서버를 등록했다.

```python
servers = {
    "POS 서버": "127.0.0.1",
    "DB 서버": "127.0.0.1",
    "재고 서버": "192.0.2.1"
}
```

각 서버의 IP 주소를 대상으로 Ping을 보내 서버의 네트워크 연결 상태를 확인하도록 구현했다.

#### 2. Ping을 이용한 서버 상태 확인
Python의 subprocess 모듈을 사용하여 Windows 환경에서 Ping을 실행했다.

```python
def check_server(ip):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "1000", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0
```

Ping 명령의 반환값을 이용하여 서버 상태를 판단한다.
* True → 서버 정상
* False → 서버 장애

#### 3. 여러 서버 상태 확인
등록된 서버들을 반복문으로 순회하면서 각각의 상태를 출력하도록 구현했다.

```python
for name, ip in servers.items():
    current_status = check_server(ip)
```

실행 결과:
```
POS 서버 (127.0.0.1) → 🟢 정상
DB 서버 (127.0.0.1) → 🟢 정상
재고 서버 (192.0.2.1) → 🔴 장애
```

192.0.2.1은 테스트를 위해 사용한 도달할 수 없는 IP 주소이다.

#### 4. 주기적인 상태 모니터링
while True와 time.sleep(5)를 사용하여 서버 상태를 5초마다 반복적으로 확인하도록 구현했다.

```python
while True:
    ...
    time.sleep(5)
```

이를 통해 한 번만 상태를 확인하는 것이 아니라 지속적으로 인프라 상태를 모니터링할 수 있도록 했다.

#### 5. 장애 발생 및 복구 상태 감지
서버의 이전 상태를 저장하기 위해 previous_status 딕셔너리를 사용했다.

```python
previous_status = {}
```

현재 상태와 이전 상태를 비교하여 상태가 변경되는 순간을 감지하도록 구현했다.

정상 → 장애

```python
elif previous_status[name] and not current_status:
    print(f"🚨 [장애 발생] {name}에 장애가 발생했습니다.")
```

장애 → 정상

```python
elif not previous_status[name] and current_status:
    print(f"✅ [복구 완료] {name}이 정상적으로 복구되었습니다.")
```

이를 통해 단순히 현재 상태를 보여주는 것뿐만 아니라 장애가 발생한 시점과 복구된 시점의 상태 변화를 감지할 수 있도록 했다.


#### 현재 구현 기능

현재까지 다음 기능을 구현했다.

* 서버 IP 관리
* Ping을 이용한 서버 상태 확인
* 여러 서버 모니터링
* 5초 주기 상태 확인
* 장애 발생 감지
* 장애 복구 감지


---

### 2026-09-04

#### 1. Ping을 이용한 서버 상태 확인

Python의 subprocess를 이용하여 서버의 IP 주소에 Ping을 보내
서버의 네트워크 연결 상태를 확인하도록 구현했다.

```python
def check_server(ip):
    result = subprocess.run(
        ["ping", "-n", "1", "-w", "1000", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    return result.returncode == 0
```
Ping 응답이 있으면 정상, 응답이 없으면 장애로 판단한다.

#### 2. 여러 서버 모니터링

무인매장의 주요 인프라를 가정하여 다음 서버를 구성했다.

* POS 서버
* DB 서버
* 재고 서버

각 서버의 IP 주소를 관리하고 반복적으로 상태를 확인하도록 구현했다.

#### 3. 주기적인 모니터링
while True와 time.sleep(5)를 이용하여
5초마다 서버 상태를 확인하도록 변경했다.

#### 4. 장애 발생 및 복구 감지
이전 상태를 previous_status에 저장하여
정상 → 장애 또는 장애 → 정상으로 상태가 변경되는 순간을 감지하도록 구현했다.

```python
if previous_status[name] and not current_status:
    print("장애 발생")

elif not previous_status[name] and current_status:
    print("복구 완료")
```

#### 5. 시스템 자원 모니터링
psutil 라이브러리를 이용하여 현재 시스템의

* CPU
* Memory
* Disk

사용률을 확인하도록 추가했다.

#### 6. 서비스 포트 상태 확인
Ping만으로는 서버가 살아있는지 여부만 확인할 수 있기 때문에
실제 서비스가 정상적으로 동작하는지 확인하기 위해 TCP 포트 검사를 추가했다.

```python
check_port(ip, port)
```

예를 들어 POS 서버의 경우:
* 서버 Ping 정상
* 8000번 포트 정상

이어야 POS 서비스가 정상이라고 판단할 수 있다.

#### 테스트 결과
Python HTTP 서버를 8000번 포트에서 실행한 결과:
```
POS 서버 (127.0.0.1) → 🟢 정상
포트 8000 → 정상
```

HTTP 서버를 종료하면:
```
POS 서버 (127.0.0.1) → 🟢 정상
포트 8000 → 장애
```
서버 자체는 살아있지만 서비스가 중단된 상황을 구분할 수 있음을 확인했다.

#### 7. 서비스 자동복구 기능 구현

서비스 포트 장애가 감지되었을 때 Python을 이용하여
해당 서비스를 자동으로 다시 실행하도록 구현했다.

장애 발생:
```text
🚨 [서비스 장애] POS 서버의 포트 8000에 장애가 발생했습니다.
```

자동 복구:
```text
🔧 POS 서비스 자동 복구를 시도합니다.
🔄 POS 서비스 재시작 명령을 실행했습니다.
```

복구 확인:
```text
POS 서버 → 🟢 정상
포트 8000 → 🟢 정상
```

이를 통해 서비스 장애를 감지하고 자동으로 복구하는
기본적인 장애 대응 흐름을 구현했다.

지금까지:

```text
Python
 ├─ 서버 Ping
 ├─ CPU / Memory / Disk
 ├─ 포트 확인
 ├─ 장애 감지
 └─ 자동복구
```

다음: 
```text
Python Monitor
       ↓
Docker Container
       ↓
POS 서비스
       ↓
Container 강제 종료
       ↓
Python이 장애 감지
       ↓
Docker Container 재시작
       ↓
서비스 복구
```

