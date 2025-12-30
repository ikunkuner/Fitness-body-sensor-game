import math
import random

import cv2
import mediapipe as mp

# 初始化 MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class CircleGame:
    def __init__(self, frame_width, frame_height):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.circle_radius = 40  # 圆圈半径
        self.circle_color = (0, 255, 0)  # 绿色圆圈
        self.score = 0
        self.generate_new_circle()

    def generate_new_circle(self):
        """随机生成新的圆圈位置"""
        margin = self.circle_radius + 20  # 留出边距
        self.circle_x = random.randint(margin, self.frame_width - margin)
        self.circle_y = random.randint(margin, self.frame_height - margin)
        self.circle_color = (
            random.randint(50, 255),  # B
            random.randint(50, 255),  # G
            random.randint(50, 255)  # R
        )

    def draw_circle(self, frame):
        """在帧上绘制圆圈"""
        # 绘制实心圆圈
        cv2.circle(frame, (self.circle_x, self.circle_y),
                   self.circle_radius, self.circle_color, -1)

        # 绘制圆圈边框
        cv2.circle(frame, (self.circle_x, self.circle_y),
                   self.circle_radius, (255, 255, 255), 2)

        # 在圆圈中心绘制分数
        text = f"{self.score}"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = self.circle_x - text_size[0] // 2
        text_y = self.circle_y + text_size[1] // 2
        cv2.putText(frame, text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def check_collision(self, hand_x, hand_y):
        """检查手是否碰到圆圈"""
        if hand_x is None or hand_y is None:
            return False

        # 计算手和圆圈中心的距离
        distance = math.sqrt((hand_x - self.circle_x) ** 2 + (hand_y - self.circle_y) ** 2)

        # 如果距离小于半径，则发生碰撞
        return distance <= self.circle_radius

    def draw_score(self, frame):
        """绘制分数显示"""
        score_text = f"Score: {self.score}"
        cv2.putText(frame, score_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    def draw_instructions(self, frame):
        """绘制游戏说明"""
        instructions = [
            "Touch the circle with your hands!",
            "Press 'R' to reset score",
            "Press 'Q' to quit"
        ]

        y_pos = self.frame_height - 100
        for i, text in enumerate(instructions):
            cv2.putText(frame, text, (10, y_pos + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)


def get_hand_coordinates(landmarks, hand_type='right'):
    """获取手部坐标（左手或右手）"""
    if landmarks is None:
        return None, None

    # MediaPipe 姿态关键点索引
    if hand_type == 'right':
        # 右手腕的关键点索引
        wrist_index = mp_pose.PoseLandmark.RIGHT_WRIST.value
    else:  # left
        # 左手腕的关键点索引
        wrist_index = mp_pose.PoseLandmark.LEFT_WRIST.value

    try:
        wrist = landmarks.landmark[wrist_index]
        # 将归一化坐标转换为像素坐标
        return int(wrist.x * frame_width), int(wrist.y * frame_height)
    except:
        return None, None


def draw_hand_position(frame, hand_x, hand_y, hand_type='right'):
    """绘制手部位置指示器"""
    if hand_x is not None and hand_y is not None:
        color = (255, 0, 0) if hand_type == 'right' else (0, 0, 255)  # 蓝色右手，红色左手
        # 绘制手部位置点
        cv2.circle(frame, (hand_x, hand_y), 15, color, -1)
        cv2.circle(frame, (hand_x, hand_y), 15, (255, 255, 255), 2)

        # 绘制手部标签
        label = "Right Hand" if hand_type == 'right' else "Left Hand"
        cv2.putText(frame, label, (hand_x + 20, hand_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


def draw_collision_effect(frame, circle_x, circle_y, radius):
    """绘制碰撞特效"""
    # 绘制一个扩散的光环
    for i in range(3):
        effect_radius = radius + 10 + i * 15
        effect_color = (0, 255 - i * 50, 255 - i * 50)  # 黄色到红色的渐变
        cv2.circle(frame, (circle_x, circle_y), effect_radius,
                   effect_color, 2, lineType=cv2.LINE_AA)


# 初始化摄像头
cap = cv2.VideoCapture(0)

# 获取摄像头分辨率
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"摄像头分辨率: {frame_width} x {frame_height}")

# 初始化游戏
game = CircleGame(frame_width, frame_height)

# 创建 Pose 实例
with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        model_complexity=1
) as pose:
    # FPS 计算变量
    fps = 0
    frame_count = 0
    start_time = cv2.getTickCount()

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("无法读取摄像头画面")
            break

        # 水平翻转画面，让镜子效果更自然
        frame = cv2.flip(frame, 1)

        # 转换颜色空间
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 处理帧
        results = pose.process(frame_rgb)

        # 绘制姿态关键点
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )

            # 获取左右手坐标
            right_hand_x, right_hand_y = get_hand_coordinates(results.pose_landmarks, 'right')
            left_hand_x, left_hand_y = get_hand_coordinates(results.pose_landmarks, 'left')

            # 绘制手部位置
            draw_hand_position(frame, right_hand_x, right_hand_y, 'right')
            draw_hand_position(frame, left_hand_x, left_hand_y, 'left')

            # 检查碰撞
            collision_occurred = False

            # 检查右手碰撞
            if game.check_collision(right_hand_x, right_hand_y):
                collision_occurred = True
                if right_hand_x and right_hand_y:
                    draw_collision_effect(frame, right_hand_x, right_hand_y, 20)

            # 检查左手碰撞
            if game.check_collision(left_hand_x, left_hand_y):
                collision_occurred = True
                if left_hand_x and left_hand_y:
                    draw_collision_effect(frame, left_hand_x, left_hand_y, 20)

            # 如果发生碰撞，生成新圆圈并加分
            if collision_occurred:
                game.score += 1
                game.generate_new_circle()

                # 短暂的碰撞特效
                for _ in range(3):
                    draw_collision_effect(frame, game.circle_x, game.circle_y, game.circle_radius)

        # 绘制圆圈
        game.draw_circle(frame)

        # 绘制分数
        game.draw_score(frame)

        # 绘制游戏说明
        game.draw_instructions(frame)

        # 计算并显示FPS
        frame_count += 1
        if frame_count >= 30:
            end_time = cv2.getTickCount()
            time_diff = (end_time - start_time) / cv2.getTickFrequency()
            fps = frame_count / time_diff
            frame_count = 0
            start_time = end_time

        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 检测到人体时的提示
        if results.pose_landmarks:
            cv2.putText(frame, "Body Detected", (frame_width - 200, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No Body Detected", (frame_width - 200, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 显示画面
        cv2.imshow('Fitness Circle Game', frame)

        # 键盘控制
        key = cv2.waitKey(5) & 0xFF
        if key == ord('q'):  # 退出
            break
        elif key == ord('r'):  # 重置分数
            game.score = 0
            game.generate_new_circle()
        elif key == ord('n'):  # 手动生成新圆圈
            game.generate_new_circle()

cap.release()
cv2.destroyAllWindows()