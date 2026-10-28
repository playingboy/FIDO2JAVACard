from fido2.pcsc import CtapPcscDevice
from fido2.ctap2 import Ctap2

# 1. 自动枚举 PC/SC 读卡器中的 FIDO2 设备
devices = list(CtapPcscDevice.list_devices())
if not devices:
    print("没有找到支持 PC/SC 的 FIDO2 卡")
else:
    dev = devices[0]
    print(f"成功连接到: {dev}")
    ctap = Ctap2(dev)
    
    # 2. 发起重置
    print("🚀 正在发起硬件重置，请在提示后 10 秒内物理拔插或触摸卡片...")
    ctap.reset()
    print("✅ 重置成功！PIN 码已被清空。")
