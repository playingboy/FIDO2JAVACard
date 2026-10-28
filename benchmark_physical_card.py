import os
import time
from fido2.pcsc import CtapPcscDevice
from fido2.ctap2 import Ctap2
# 修复：从最新的 cose 模块引入 ES256 算法类
from fido2.cose import ES256

def run_benchmark():
    # 1. 寻找物理设备
    try:
        devices = list(CtapPcscDevice.list_devices())
        print("🔍 发现以下 PCSC 设备:")
        for idx, d in enumerate(devices):
            print(f"  [{idx}] {d}")
        device = devices[0]
        print(f"\n📡 已锁定测试目标设备: {device}\n")
    except (StopIteration, IndexError):
        print("❌ 未找到任何 PCSC 读卡器！")
        return

    # 2. 初始化底层 CTAP2 协议对象
    ctap2 = Ctap2(device)

    # 准备底层测试所需的数据
    client_data_hash = os.urandom(32)  # 模拟浏览器生成的 ClientDataHash
    rp = {"id": "perf-test.jesse.com", "name": "Performance Lab"}
    user = {"id": b"user_perf_001", "name": "jesse_bench"}

    print("==================================================")
    print("\033[96m⚡ 正在发起 [底层 MakeCredential / 注册] 性能测试...\033[0m")
    
    # 3. 测试 MakeCredential 净耗时
    start_time = time.perf_counter()
    
    # 修复：直接传入包含算法编号的字典，或者最新规范的形式
    attestation_object = ctap2.make_credential(
        client_data_hash=client_data_hash,
        rp=rp,
        user=user,
        key_params=[{"type": "public-key", "alg": ES256.ALGORITHM}], # 现代化标准写法
        options={"rk": True}
    )
    
    end_time = time.perf_counter()
    make_cred_ms = (end_time - start_time) * 1000
    print("✅ 注册成功！")
    print(f"⏱️  [MakeCredential] 硬件净耗时: \033[92m{make_cred_ms:.2f} 毫秒\033[0m")

    # 提取生成的凭据 ID 以便进行登录测试
    auth_data = attestation_object.auth_data
    credential_id = auth_data.credential_data.credential_id

    print("--------------------------------------------------")
    print("\033[96m⚡ 正在发起 [底层 GetAssertion / 登录签名] 性能测试...\033[0m")
    
    # 4. 测试 GetAssertion 净耗时
    start_time = time.perf_counter()
    
    # 直接向卡片发送原始断言签名指令
    assertions = ctap2.get_assertion(
        rp_id="perf-test.jesse.com",
        client_data_hash=client_data_hash,
        allow_list=[{"type": "public-key", "id": credential_id}]
    )
    
    end_time = time.perf_counter()
    get_assert_ms = (end_time - start_time) * 1000
    print("✅ 认证成功！")
    print(f"⏱️  [GetAssertion] 硬件净耗时: \033[92m{get_assert_ms:.2f} 毫秒\033[0m")
    print("==================================================")

if __name__ == "__main__":
    run_benchmark()
