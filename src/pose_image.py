import cv2
import mediapipe as mp
import numpy as np

# 初始化 MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 读取图片
image_path = "../images/1.jpg"  # 替换为你的图片路径
image = cv2.imread(image_path)

# 创建 Pose 实例
with mp_pose.Pose(
        static_image_mode=True,  # 静态图片模式
        model_complexity=2,  # 模型复杂度：0-轻量，1-中等，2-高精度
        enable_segmentation=True,  # 是否进行背景分割
        min_detection_confidence=0.5  # 最小检测置信度
) as pose:
    # 转换颜色空间 BGR 转 RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 处理图片
    results = pose.process(image_rgb)

    # 绘制姿态关键点
    if results.pose_landmarks:
        # 绘制姿态骨架
        annotated_image = image.copy()
        mp_drawing.draw_landmarks(
            annotated_image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )

        # 保存或显示结果
        cv2.imwrite('../output_pose.jpg', annotated_image)
        print("姿态检测完成，结果已保存为 output_pose.jpg")

        # 打印关键点信息
        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            print(f"关键点 {idx}: x={landmark.x:.3f}, y={landmark.y:.3f}, z={landmark.z:.3f}")
    else:
        print("未检测到人体姿态")