import os
import sys

# 确保能正确识别到你的虚拟卡环境
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python_tests')))

from fido2.pcsc import CtapPcscDevice
from fido2.client import Fido2Client
from fido2.webauthn import PublicKeyCredentialCreationOptions, PublicKeyCredentialRequestOptions

def run_test():
    # 1. 自动寻找系统里的 PCSC 虚拟卡
    try:
        device = next(CtapPcscDevice.list_devices())
        print(f"📡 成功连接到虚拟卡: {device}")
    except StopIteration:
        print("❌ 未找到虚拟卡，请确保中继脚本正在运行！")
        return

    # 2. 初始化高层客户端（指定依赖的域名）
    client = Fido2Client(device, "https://jesse-hardware.com")
    
    # 模拟服务器下发的挑战字和用户信息
    rp = {"id": "jesse-hardware.com", "name": "Jesse's FIDO2 Lab"}
    user = {"id": b"user_id_9999", "name": "jesse_ma", "displayName": "Jesse Ma"}
    challenge = os.urandom(32)

    print("\n--- [步骤 1] 模拟 WebAuthn 注册 (MakeCredential) ---")
    try:
        # 构造创建凭据的参数
        attestation_result = client.make_credential(
            options=PublicKeyCredentialCreationOptions(
                rp=rp,
                user=user,
                challenge=challenge,
                pub_key_cred_params=[{"type": "public-key", "alg": -7}] # -7 代表 ES256 算法
            )
        )
        print("🎉 注册成功！Java Card 成功生成了密钥对。")
        
        # 提取卡片返回的凭据 ID (Credential ID)
        auth_data = attestation_result.auth_data
        credential_id = auth_data.credential_data.credential_id
        print(f"🔑 拿到凭据 ID (HEX): {credential_id.hex()}")

    except Exception as e:
        print(f"💥 注册失败！错误信息:\n{e}")
        return

    print("\n--- [步骤 2] 模拟 WebAuthn 认证 (GetAssertion) ---")
    try:
        # 构造登录请求参数，把刚才拿到的凭据 ID 传回去
        assertion_result = client.get_assertion(
            options=PublicKeyCredentialRequestOptions(
                challenge=challenge,
                rp_id="jesse-hardware.com",
                allow_credentials=[{"type": "public-key", "id": credential_id}]
            )
        )
        
        # 提取第一个断言（卡片计算出来的签名）
        assertion = assertion_result.assertions[0]
        print("🎉 认证成功！")
        print(f"✍️ 卡片吐出的硬件签名 (Signature HEX): {assertion.signature.hex()}")
        print(f"📊 计数器值 (Sign Counter): {assertion.auth_data.sign_count}")

    except Exception as e:
        print(f"💥 认证失败！错误信息:\n{e}")

if __name__ == "__main__":
    run_test()
