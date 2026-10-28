import os
import sys
import threading
from multiprocessing import Queue

# 将 python_tests 路径加入环境变量，确保能正常 import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python_tests')))

from ctap.ctap_test import JCardSimTestCase, TestModes

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 正在将内存 Java Card 仿真器桥接到系统 PCSC 读卡器...")
    print("=" * 60)

    # 1. 强制将测试模式修改为 PCSC
    # 这会让 VSim 启动 BackgroundSimulator，自动挂载到系统的 pcscd 虚拟读卡器上
    JCardSimTestCase.MODE = TestModes.PCSC
    
    # 如果你想把它桥接为系统的虚拟 USB HID 设备的（如果系统支持 uhid），可以尝试取消注释下面这行：
    # JCardSimTestCase.MODE = TestModes.HID

    # 2. 初始化队列
    q_in = Queue()
    q_out = Queue()
    startup_q = Queue()

    # 3. 在当前进程拉起虚拟机和监听服务
    try:
        # 这个方法内部会拉起 JVM，并调用 VSim.startBackgroundSimulator() 挂载 PCSC
        JCardSimTestCase.launch_sim(q_in, q_out, startup_q)
        
        # 等待初始化完成提示
        startup_q.get()
        print("\n🎉 虚拟卡已成功挂载！它现在正通过 vsmartcard (pcscd) 挂牌营业中。")
        print("💡 [重要提示]: 请保持此终端窗口不要关闭！")
        print("Now, 打开你的 FIDO Conformance Tool 官方测试工具，刷新 PCSC 列表，就能看到它了！")
        
        # 让主线程陷入死循环，防止程序退出
        stop_event = threading.Event()
        stop_event.wait()

    except KeyboardInterrupt:
        print("\n停止中继代理...")
