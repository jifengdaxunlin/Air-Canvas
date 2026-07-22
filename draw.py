import os
from datetime import datetime
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image, ImageDraw, ImageFont

# 尝试引入 PySide6 用于弹窗提示（如果没有安装 PySide6 则降级使用命令行输出）
try:
    from PySide6.QtWidgets import QMessageBox
    from PySide6.QtCore import QTimer
    HAS_PYSIDE = True
except ImportError:
    HAS_PYSIDE = False


class AirCanvas:
    def __init__(self, width=1050, height=750):
        """初始化空中画板的核心参数、手势检测器与 UI 配置"""
        self.width = width
        self.height = height
        self.canvas = None     # 纯净绘画图层（只记录用户的笔触，初始为纯白）
        self.bg_layer = None   # 背景底稿图层（仅用于显示棋盘格及临摹底图）
        self.xp, self.yp = 0, 0 # 上一帧的指尖坐标（用于绘制连续线条）

        # ------------------ MediaPipe 手势识别初始化 ------------------
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,        # 视频流模式，开启追踪优化
            max_num_hands=1,                 # 仅识别单手
            min_detection_confidence=0.7,   # 置信度门槛
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # ------------------ 顶部 UI 菜单项配置 ------------------
        # 1. 第一层：画笔粗细设置 + 保存按钮
        self.size_items = [
            {"name": "FINE (4px)", "size": 4},
            {"name": "MID (8px)", "size": 8},
            {"name": "THICK (15px)", "size": 15},
            {"name": "MAX (25px)", "size": 25},
            {"name": "SAVE", "size": None}
        ]

        # 2. 第二层：颜色选择与功能按钮 (BGR 调色盘格式)
        self.colors = [
            {"name": "RED", "color": (0, 0, 255)},
            {"name": "ORANGE", "color": (0, 165, 255)},
            {"name": "YELLOW", "color": (0, 255, 255)},
            {"name": "GREEN", "color": (0, 255, 0)},
            {"name": "CYAN", "color": (255, 255, 0)},
            {"name": "BLUE", "color": (255, 0, 0)},
            {"name": "PURPLE", "color": (255, 0, 255)},
            {"name": "ERASER", "color": (255, 255, 255)},
            {"name": "CLEAR", "color": (200, 200, 200)}
        ]

        # 默认绘图状态
        self.draw_color = (0, 0, 255)  # 默认红色 (BGR)
        self.selected_color_idx = 0    # 当前选中的颜色索引
        self.selected_size_idx = 1     # 默认选中 MID (8px)
        
        # 初始化画笔与橡皮擦粗细
        self.brush_thickness = self.size_items[self.selected_size_idx]["size"]
        self.eraser_thickness = max(10, self.brush_thickness * 2)  # 橡皮擦粗细自动设为画笔的 2 倍

        # 保存路径记录
        self.saved_file_path = ""

        # UI 尺寸控制参数（双层顶部菜单）
        self.header_layer1_h = 60      # 第一层（字号+SAVE）高度
        self.header_layer2_h = 60      # 第二层（颜色+清屏）高度
        self.total_header_h = self.header_layer1_h + self.header_layer2_h

        # 悬停选择与交互动画控制变量
        self.hover_type = None         # 当前悬停类型: "SIZE" 或 "COLOR"
        self.hover_box_idx = -1        # 当前悬停的按钮索引
        self.hover_counter = 0         # 悬停帧数计数器
        self.HOVER_FRAMES = 10         # 悬停达到 10 帧 (~0.3秒) 触发点击动作
        self.anim_effect = None        # 水波纹动画状态

    @property
    def draw_thickness(self):
        """外部 GUI 读取画笔粗细的属性"""
        return self.brush_thickness

    @draw_thickness.setter
    def draw_thickness(self, value):
        """动态修改画笔粗细，并按比例联动更新橡皮擦粗细与 UI 高亮框"""
        self.brush_thickness = int(value)
        # 橡皮擦粗细保持 2 倍，至少 10px
        self.eraser_thickness = max(10, self.brush_thickness * 2)
        
        # 自动匹配顶部 UI 对应的字号按钮高亮
        matched = False
        for i, item in enumerate(self.size_items):
            if item["size"] == self.brush_thickness:
                self.selected_size_idx = i
                matched = True
                break
        if not matched:
            self.selected_size_idx = -1

    def set_background_image(self, bg_img):
        """设置背景临摹图片，并预计算图像处理掩膜（用于后续实时打分）"""
        if bg_img is None:
            return

        self.raw_bg_img = bg_img
        w = self.width if self.width > 0 else 1050
        h = self.height if self.height > 0 else 750

        # 1. 限制推荐绘画区域边界
        top_offset = self.total_header_h + 5
        bottom_limit = h - 80
        left_offset = 10
        right_limit = w - 10

        avail_w = max(1, right_limit - left_offset)
        avail_h = max(1, bottom_limit - top_offset)

        # 2. 将背景图等比缩放到画板可用区域内
        bg_h, bg_w = bg_img.shape[:2]
        scale = min(avail_w / bg_w, avail_h / bg_h)
        new_w = max(1, int(bg_w * scale))
        new_h = max(1, int(bg_h * scale))

        resized_bg = cv2.resize(bg_img, (new_w, new_h))

        # 3. 计算居中对齐的偏移量
        x_offset = left_offset + (avail_w - new_w) // 2
        y_offset = top_offset + (avail_h - new_h) // 2

        # 4. 叠加半透明临摹图到棋盘格背景上
        base_bg = self._get_checkerboard(w, h)
        target_roi = base_bg[y_offset : y_offset + new_h, x_offset : x_offset + new_w]
        blended = cv2.addWeighted(resized_bg, 0.5, target_roi, 0.5, 0)
        base_bg[y_offset : y_offset + new_h, x_offset : x_offset + new_w] = blended

        self.bg_layer = base_bg

        # 5. 提取前景实体掩膜与容差带（用于打分中的精准度判定）
        gray_bg = cv2.cvtColor(resized_bg, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_bg, 50, 150)
        
        # 闭运算连接边缘
        close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
        closed_mask = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, close_kernel)

        # Otsu 二值化补充
        _, otsu_mask = cv2.threshold(gray_bg, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if np.mean(otsu_mask) > 127:
            otsu_mask = cv2.bitwise_not(otsu_mask)

        target_mask = cv2.bitwise_or(closed_mask, otsu_mask)

        # 膨胀处理生成允许误差的容差区域
        tol_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
        self.bg_tolerance_mask = cv2.dilate(target_mask, tol_kernel)
        self.bg_target_pixels = np.sum(target_mask > 0)

        # 6. 提取骨架线（用于打分中的覆盖率 Recall 判定）
        dist_trans = cv2.distanceTransform(target_mask, cv2.DIST_L2, 5)
        max_val = np.max(dist_trans)
        if max_val > 0:
            self.bg_skeleton = (dist_trans >= max(2.0, max_val * 0.25)).astype(np.uint8) * 255
        else:
            self.bg_skeleton = edges

        self.bg_skeleton_pixels = np.sum(self.bg_skeleton > 0)
        self.bg_roi_rect = (x_offset, y_offset, new_w, new_h)

    def change_BGR_color(self, b, g, r):
        """切换画笔颜色 (BGR 格式)"""
        self.draw_color = (int(b), int(g), int(r))
        for i, item in enumerate(self.colors):
            if item["color"] == self.draw_color:
                self.selected_color_idx = i
                break

    def get_BGR_color(self):
        """获取当前画笔颜色"""
        return self.draw_color

    def save_to_file(self) -> str:
        """保存画作：将画布转换为透明背景 PNG (BGRA 4通道) 并保存"""
        if self.canvas is not None:
            save_dir = "Pic_save"
            os.makedirs(save_dir, exist_ok=True)
            filename = f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.saved_file_path = os.path.join(save_dir, filename)
            
            # 分离 BGR 通道并根据有无笔触提取 Alpha 透明通道
            b, g, r = cv2.split(self.canvas)
            drawing_mask = np.any(self.canvas != [255, 255, 255], axis=-1)
            alpha = np.zeros(self.canvas.shape[:2], dtype=np.uint8)
            alpha[drawing_mask] = 255  # 非白色区域设为不透明
            
            transparent_canvas = cv2.merge([b, g, r, alpha])
            # 使用 imencode 以完美支持中文文件/文件夹路径
            cv2.imencode(".png", transparent_canvas)[1].tofile(self.saved_file_path)

            # 提示保存结果
            if HAS_PYSIDE:
                msg = QMessageBox()
                msg.setWindowTitle("保存成功")
                msg.setText(f"透明背景画作已成功保存！\n\n路径：\n{os.path.abspath(self.saved_file_path)}")
                msg.setIcon(QMessageBox.Information)
                QTimer.singleShot(2000, msg.close)  # 2 秒后自动关闭
                msg.exec()
            else:
                print(f"[Save Success] 保存至: {self.saved_file_path}")

            return self.saved_file_path
        return ""

    def _get_checkerboard(self, w, h, square_size=20):
        """生成深色透明棋盘格背景（作为无背景时的底图）"""
        if hasattr(self, '_cached_checker') and self._cached_checker.shape[:2] == (h, w):
            return self._cached_checker.copy()
        color1 = (26, 26, 26)
        color2 = (68, 52, 50)
        y, x = np.indices((h, w))
        checker = ((x // square_size) + (y // square_size)) % 2
        bg = np.zeros((h, w, 3), dtype=np.uint8)
        bg[checker == 0] = color1
        bg[checker == 1] = color2
        self._cached_checker = bg
        return self._cached_checker.copy()

    def process(self, frame):
        """处理一帧摄像头图像：完成手势识别、状态切换、轨迹绘制与 UI 渲染"""
        # 确保画布与输入图像分辨率一致
        if self.canvas is None or self.canvas.shape[:2] != frame.shape[:2]:
            self.height, self.width = frame.shape[:2]
            self.canvas = np.full_like(frame, 255)  # 纯白画布

        box_size_w = max(1, self.width // len(self.size_items))
        box_color_w = max(1, self.width // len(self.colors))

        # MediaPipe RGB 转码与手势处理
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        finger_point = None
        mode = "NONE"

        # ------------------ 1. 手势逻辑判断 ------------------
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                lm_list = [(int(lm.x * self.width), int(lm.y * self.height)) for lm in hand_landmarks.landmark]

                if len(lm_list) >= 21:
                    x1, y1 = lm_list[8]  # 食指指尖坐标

                    # 判断食指和中指是否竖起（指尖 y 坐标小于指节 y 坐标）
                    index_up = lm_list[8][1] < lm_list[6][1]
                    middle_up = lm_list[12][1] < lm_list[10][1]

                    finger_point = (x1, y1)

                    # A. 选择模式 (食指 + 中指同时抬起)：用于悬停点击顶部菜单
                    if index_up and middle_up:
                        mode = "SELECT"
                        self.xp, self.yp = 0, 0  # 断开上一笔画轨迹

                        # 区域 1: 第一层【字号大小区 + SAVE保存区】
                        if y1 < self.header_layer1_h:
                            sz_idx = x1 // box_size_w
                            if 0 <= sz_idx < len(self.size_items):
                                self._update_hover("SIZE", sz_idx)
                                # 悬停时长达到设定帧数，触发点击
                                if self.hover_counter >= self.HOVER_FRAMES:
                                    item = self.size_items[sz_idx]
                                    if item["name"] == "SAVE":
                                        self._trigger_ripple(x1, y1, "SAVE")
                                        self.save_to_file()
                                    else:
                                        self.draw_thickness = item["size"]  # 设置粗细
                                        self._trigger_ripple(x1, y1, "SIZE")
                                    self.hover_counter = 0

                        # 区域 2: 第二层【颜色选择 + Eraser/Clear 功能区】
                        elif self.header_layer1_h <= y1 < self.total_header_h:
                            col_idx = x1 // box_color_w
                            if 0 <= col_idx < len(self.colors):
                                self._update_hover("COLOR", col_idx)
                                if self.hover_counter >= self.HOVER_FRAMES:
                                    chosen = self.colors[col_idx]
                                    if chosen["name"] == "CLEAR":
                                        self.canvas = np.full_like(frame, 255)  # 清屏（恢复纯白）
                                    elif chosen["name"] == "ERASER":
                                        self.change_BGR_color(255, 255, 255)     # 橡皮擦即绘制白色
                                    else:
                                        b, g, r = chosen["color"]
                                        self.change_BGR_color(b, g, r)

                                    self.selected_color_idx = col_idx
                                    self._trigger_ripple(x1, y1, chosen["name"])
                                    self.hover_counter = 0
                        else:
                            self._reset_hover()

                    # B. 绘画模式 (仅食指抬起)：在画板上进行书写或擦除
                    elif index_up and not middle_up:
                        mode = "DRAW"
                        self._reset_hover()

                        # 首次落笔，记录起始点
                        if self.xp == 0 and self.yp == 0:
                            self.xp, self.yp = x1, y1

                        # 根据颜色判断使用画笔粗细还是橡皮粗细
                        curr_th = self.eraser_thickness if self.draw_color == (255, 255, 255) else self.brush_thickness
                        # 绘制线条连接前后两点，保持流畅性
                        cv2.line(self.canvas, (self.xp, self.yp), (x1, y1), self.draw_color, curr_th)
                        self.xp, self.yp = x1, y1  # 更新当前坐标为下一笔的起始点
                    else:
                        self.xp, self.yp = 0, 0
                        self._reset_hover()

        # ------------------ 2. 图层合成 ------------------
        # 提取画板上有笔触（非白色）的像素区域
        drawing_mask = np.any(self.canvas != [255, 255, 255], axis=-1)
        if self.bg_layer is not None:
            display_frame = self.bg_layer.copy()
        else:
            display_frame = self._get_checkerboard(self.width, self.height)

        # 将绘画笔触覆盖叠加到显示图层上
        display_frame[drawing_mask] = self.canvas[drawing_mask]

        # ------------------ 3. UI 渲染与指尖光标绘制 ------------------
        self.draw_ui(display_frame)

        # 绘制交互指尖光标
        if finger_point:
            fx, fy = finger_point
            if mode == "SELECT":
                # 选择模式：绘制圆圈，并随悬停进度绘制环形进度条
                cv2.circle(display_frame, (fx, fy), 10, self.draw_color, 2)
                if self.hover_box_idx != -1 and self.hover_counter > 0:
                    angle = int((self.hover_counter / self.HOVER_FRAMES) * 360)
                    cv2.ellipse(display_frame, (fx, fy), (20, 20), 0, -90, -90 + angle, 
                                (255-self.draw_color[0], 255-self.draw_color[1], 255-self.draw_color[2]), 3)

            elif mode == "DRAW":
                # 绘画模式：随笔触/橡皮擦大小绘制实时预览圆圈
                if self.draw_color == (255, 255, 255):  # 橡皮擦预览
                    cur_size = max(8, self.eraser_thickness // 2)
                    cv2.circle(display_frame, (fx, fy), cur_size, (200, 200, 200), 2)
                else:  # 画笔预览
                    cur_size = max(4, self.brush_thickness // 2)
                    cv2.circle(display_frame, (fx, fy), cur_size, self.draw_color, -1)
                    cv2.circle(display_frame, (fx, fy), cur_size + 2, (0, 0, 0), 1)

        # 绘制触发选中的水波纹扩散动画
        if self.anim_effect:
            ax, ay = self.anim_effect["x"], self.anim_effect["y"]
            r = self.anim_effect["radius"]
            color = self.get_BGR_color()
            cv2.circle(display_frame, (ax, ay), r, (255-color[0], 255-color[1], 255-color[2]), 3)
            self.anim_effect["radius"] += 6
            if self.anim_effect["radius"] > 45:
                self.anim_effect = None

        # 绘制食指和中指的手势骨架节点
        if results.multi_hand_landmarks:
            finger_connections = [(5, 6), (6, 7), (7, 8), (9, 10), (10, 11), (11, 12)]
            finger_nodes = [5, 6, 7, 8, 9, 10, 11, 12]

            for hand_landmarks in results.multi_hand_landmarks:
                pts = [(int(lm.x * self.width), int(lm.y * self.height)) for lm in hand_landmarks.landmark]
                for p1, p2 in finger_connections:
                    cv2.line(display_frame, pts[p1], pts[p2], (0, 255, 0), 2)
                for idx in finger_nodes:
                    cv2.circle(display_frame, pts[idx], 4, (0, 0, 255), -1)

        return display_frame

    def _update_hover(self, h_type, idx):
        """更新菜单按钮悬停计数器"""
        if self.hover_type == h_type and self.hover_box_idx == idx:
            self.hover_counter += 1
        else:
            self.hover_type = h_type
            self.hover_box_idx = idx
            self.hover_counter = 1

    def _reset_hover(self):
        """重置悬停计数状态"""
        self.hover_type = None
        self.hover_box_idx = -1
        self.hover_counter = 0

    def _trigger_ripple(self, x, y, item_name):
        """在坐标 (x, y) 触发一次水波纹动画效果"""
        self.anim_effect = {
            "x": x, "y": y,
            "radius": 12,
            "color": (0, 255, 0) if item_name == "SAVE" else ((0, 255, 255) if item_name != "CLEAR" else (0, 0, 0))
        }

    def draw_ui(self, img):
        """绘制双层交互菜单与状态展示面板"""
        box_size_w = self.width // len(self.size_items)
        box_color_w = self.width // len(self.colors)

        # ---------------- 1. 绘制第一层：字号与 SAVE 按钮 ----------------
        y_top_1 = 0
        y_bottom_1 = self.header_layer1_h

        for j, sz_item in enumerate(self.size_items):
            x_start = j * box_size_w
            x_end = (j + 1) * box_size_w
            name = sz_item["name"]

            # 区分绘制普通字号项与绿色 SAVE 按钮
            if name == "SAVE":
                cv2.rectangle(img, (x_start + 2, y_top_1 + 2), (x_end - 2, y_bottom_1 - 2), (30, 140, 30), -1)
                cv2.rectangle(img, (x_start + 1, y_top_1 + 1), (x_end - 1, y_bottom_1 - 1), (0, 255, 0), 2)
            elif j == self.selected_size_idx:
                cv2.rectangle(img, (x_start + 2, y_top_1 + 2), (x_end - 2, y_bottom_1 - 2), (90, 90, 90), -1)
                cv2.rectangle(img, (x_start + 1, y_top_1 + 1), (x_end - 1, y_bottom_1 - 1), (0, 200, 255), 2)
            else:
                cv2.rectangle(img, (x_start + 2, y_top_1 + 2), (x_end - 2, y_bottom_1 - 2), (50, 50, 50), -1)
                cv2.rectangle(img, (x_start + 2, y_top_1 + 2), (x_end - 2, y_bottom_1 - 2), (100, 100, 100), 1)

            # 绘制悬停边框
            if self.hover_type == "SIZE" and j == self.hover_box_idx:
                cv2.rectangle(img, (x_start + 4, y_top_1 + 4), (x_end - 4, y_bottom_1 - 4), (255, 255, 255), 2)

            # 文字居中绘制
            font_scale = 0.42
            thickness = 2
            (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            tx = max(x_start + 2, x_start + (box_size_w - tw) // 2)
            ty = y_top_1 + (self.header_layer1_h + th) // 2
            cv2.putText(img, name, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

        # ---------------- 2. 绘制第二层：颜色与功能按钮 ----------------
        y_top_2 = self.header_layer1_h
        y_bottom_2 = self.total_header_h

        for i, col_item in enumerate(self.colors):
            x_start = i * box_color_w
            x_end = (i + 1) * box_color_w
            color = col_item["color"]
            name = col_item["name"]

            cv2.rectangle(img, (x_start + 2, y_top_2 + 2), (x_end - 2, y_bottom_2 - 2), color, -1)

            # 高亮选中项
            color = self.get_BGR_color()
            if i == self.selected_color_idx and name != "CLEAR":
                cv2.rectangle(img, (x_start + 1, y_top_2 + 1), (x_end - 1, y_bottom_2 - 1), (255-color[0],255-color[1],255-color[2]), 3)
            else:
                cv2.rectangle(img, (x_start + 2, y_top_2 + 2), (x_end - 2, y_bottom_2 - 2), (80, 80, 80), 1)

            # 绘制悬停边框
            if self.hover_type == "COLOR" and i == self.hover_box_idx:
                cv2.rectangle(img, (x_start + 4, y_top_2 + 4), (x_end - 4, y_bottom_2 - 4), (255, 255, 255), 2)

            # 文字颜色根据背景自动反色（浅色背景配黑色字）
            font_scale = 0.38
            thickness = 1
            (tw, th), _ = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            tx = max(x_start + 2, x_start + (box_color_w - tw) // 2)
            ty = y_top_2 + (self.header_layer2_h + th) // 2
            t_color = (0, 0, 0) if name in ["YELLOW", "ERASER", "CLEAR"] else (255, 255, 255)
            cv2.putText(img, name, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, t_color, thickness, cv2.LINE_AA)

        # ---------------- 3. 绘制推荐绘画区域框 ----------------
        x1, y1 = 10, self.total_header_h + 5
        x2, y2 = self.width - 10, self.height - 80

        cv2.rectangle(img, (x1, y1), (x2, y2), (180, 180, 180), 2)
        text_pos = (x1 + 10, y2 - 40)
        img[:] = self.putChineseText(img, "【推荐绘画区域】", text_pos, color=(255, 255, 0), fontsize=28)

        # ---------------- 4. 实时打分结果展示牌 ----------------
        score = self._compute_realtime_score()
        if score is not None:
            score_text = f"相似度: {score:.1f}%" if score > 0 else "相似度: 等待绘制..."
            
            badge_x, badge_y = x1 + 10, y1 + 10
            badge_w, badge_h = 240, 42
            
            # 绘制半透明黑色背景底块
            sub_roi = img[badge_y : badge_y + badge_h, badge_x : badge_x + badge_w]
            black_box = np.zeros_like(sub_roi)
            img[badge_y : badge_y + badge_h, badge_x : badge_x + badge_w] = cv2.addWeighted(sub_roi, 0.3, black_box, 0.7, 0)
            cv2.rectangle(img, (badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h), (0, 255, 255), 1)

            # 根据得分高低显示不同颜色文本
            text_color = (0, 255, 0) if score >= 70 else (255, 255, 0)
            img[:] = self.putChineseText(img, score_text, (badge_x + 10, badge_y + 6), color=text_color, fontsize=24)

    def putChineseText(self, image, text, position, color=(255, 0, 255), fontsize=40):
        """使用 PIL 库在 OpenCV 图像上叠加绘制中文文字"""
        PILImg = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        draw_obj = ImageDraw.Draw(PILImg)
    
        font_path = "./STCAIYUN.TTF" if os.path.exists("./STCAIYUN.TTF") else "simhei.ttf"
        try:
            fontstyle = ImageFont.truetype(font_path, fontsize, encoding="utf-8")
        except Exception:
            fontstyle = ImageFont.load_default()
        
        draw_obj.text(position, text, fill=color, font=fontstyle)
        return cv2.cvtColor(np.asarray(PILImg), cv2.COLOR_RGB2BGR)

    def _compute_realtime_score(self):
        """核心打分算法：通过计算 Precision、Recall、F1-Score 及乱涂惩罚因子评估临摹相似度"""
        if not hasattr(self, 'bg_tolerance_mask') or self.bg_tolerance_mask is None:
            return None

        x_offset, y_offset, new_w, new_h = self.bg_roi_rect

        # 截取用户绘画区域 ROI
        user_canvas_roi = self.canvas[y_offset : y_offset + new_h, x_offset : x_offset + new_w]
        user_mask = np.any(user_canvas_roi != [255, 255, 255], axis=-1)

        user_pixel_count = np.sum(user_mask)
        if user_pixel_count < 25:  # 笔触太少不打分
            return 0.0

        # 1. 精准度 (Precision)：用户绘制在容差带内的像素比例
        valid_user_pixels = np.sum(user_mask & (self.bg_tolerance_mask > 0))
        raw_precision = valid_user_pixels / user_pixel_count
        precision = raw_precision ** 2  # 平方放大偏离惩罚

        # 2. 覆盖率 (Recall)：底图骨架线被用户笔触（膨胀后）覆盖的比例
        stroke_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
        dilated_user = cv2.dilate(user_mask.astype(np.uint8), stroke_kernel)

        covered_skeleton = np.sum((self.bg_skeleton > 0) & (dilated_user > 0))
        recall = covered_skeleton / max(1, self.bg_skeleton_pixels)

        if precision + recall == 0:
            return 0.0

        # 3. 综合评估 F1-Score
        f1_score = 2 * (precision * recall) / (precision + recall)

        # 4. 墨水过量/乱涂惩罚：若用墨量远超目标面积，按比例扣分
        target_area = max(1, getattr(self, 'bg_target_pixels', self.bg_skeleton_pixels * 4))
        ink_ratio = user_pixel_count / target_area

        penalty_factor = 1.0
        if ink_ratio > 1.5:
            penalty_factor = max(0.1, 1.5 / ink_ratio)

        final_score = f1_score * penalty_factor * 100
        return round(min(100.0, final_score), 1)