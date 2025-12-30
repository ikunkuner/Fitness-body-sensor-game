import cv2
import numpy as np
import mediapipe as mp

print(f"OpenCV version: {cv2.__version__}")
print(f"NumPy version: {np.__version__}")
print(f"MediaPipe version: {mp.__version__}")

# 测试基本功能
mp_pose = mp.solutions.pose
print("✓ MediaPipe Pose 模块加载成功")

# 检查 numpy 版本
if np.__version__.startswith('2.'):
    print("⚠️ 警告：使用 numpy 2.x 版本，可能出现兼容性问题")
else:
    print("✓ NumPy 版本兼容性良好")