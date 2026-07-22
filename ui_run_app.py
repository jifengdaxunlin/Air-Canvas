import os
from datetime import datetime
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 导入 PySide6 核心 UI 控件与图形处理模块
from PySide6.QtWidgets import (QApplication, QWidget, QInputDialog, QMessageBox, 
                             QFileDialog, QColorDialog)
from PySide6.QtGui import QImage, QPixmap, QColor
from PySide6.QtCore import QTimer

# 导入 Qt Designer 编译生成的界面类 (UI 布局)
from draw_ui_source import Ui_Form  
# 导入自定义的手势画板核心逻辑类
import draw


class AirCanvasApp(QWidget):
    """
    基于 PySide6 的隔空手势绘画与人脸识别主窗口类
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 1. 初始化界面 UI 布局
        self.ui = Ui_Form()
        self.ui.setupUi(self)  # 将 UI 布局加载到当前 QWidget 窗口中
        self.setWindowTitle("手势绘画系统")
        self.setWindowIcon(QPixmap("./icon.png"))
        
        # 2. 初始化核心状态变量与数据属性
        self.face_pass = False     # 人脸识别验证状态（True: 已通过验证；False: 未通过）
        self.air_canvas = None    # 手势画板核心对象 (AirCanvas 实例)
        self.cap = None           # OpenCV 摄像头视频捕获对象 (cv.VideoCapture)
        self.path = "./facedata"  # 人脸样本图片默认存储目录
        self.roi_gray = None      # 截取的人脸灰度区域 (Region of Interest)
        
        # 3. 初始化 Qt 刷新定时器 (控制视频帧率)
        self.timer = QTimer(self)
        
        # 4. 初始化 OpenCV Haar 级联人脸分类器与 LBPH 人脸识别器
        self.faceCascade = cv.CascadeClassifier("./haar/haarcascade_frontalface_alt2.xml")
        self.recognizer = cv.face.LBPHFaceRecognizer.create()
        
        # 5. 执行 UI 默认配置与信号槽绑定
        self.init_ui_signals()

    def init_ui_signals(self) -> None:
        """初始化 UI 控件属性，并绑定所有界面控件的信号与槽函数"""
        # 开启图像自适应缩放显示
        self.ui.label_video.setScaledContents(True)
        
        # 配置画笔粗细 SpinBox 控件的数值范围与初始值
        self.ui.font_size.setRange(1, 50)     # 允许画笔粗细范围：1px ~ 50px
        self.ui.font_size.setValue(8)        # 默认初始画笔粗细：8px
        self.ui.font_size.setSingleStep(1)   # 每次调整的步长：1px

        # 绑定画笔粗细调节信号
        self.ui.font_size.valueChanged.connect(self.on_brush_size_changed)

        # 绑定功能按钮点击事件
        self.ui.but_open_save_face.clicked.connect(self.click_open_video)      # 打开摄像头 / 录入人脸
        self.ui.but_close.clicked.connect(self.click_close)                    # 关闭摄像头与重置状态
        self.ui.but_recognizer_LBPH.clicked.connect(self.click_recognizer)    # 开始人脸识别验证
        self.ui.but_draw.clicked.connect(self.click_draw)                      # 启动隔空画板
        self.ui.but_save_pic.clicked.connect(self.click_save_pic)              # 保存当前画作
        self.ui.but_color_select.clicked.connect(self.click_color_select)      # 打开系统调色盘选择颜色
        self.ui.but_pic_select.clicked.connect(self.click_pic_select)          # 导入背景图片

        # 绑定 BGR 三原色垂直滑动条实时拖拽信号（实时切换画笔颜色）
        self.ui.verticalSlider_blue.valueChanged.connect(self.on_slider_changed)
        self.ui.verticalSlider_green.valueChanged.connect(self.on_slider_changed)
        self.ui.verticalSlider_red.valueChanged.connect(self.on_slider_changed)

        # 设置 RGB 滑块默认初始颜色（默认纯红色：R=255, G=0, B=0）
        self.ui.verticalSlider_red.setValue(255)
        self.ui.verticalSlider_green.setValue(0)
        self.ui.verticalSlider_blue.setValue(0)

    def safe_disconnect_timer(self) -> None:
        """安全断开定时器信号连接，防止重复连接不同槽函数时报 PySide6 RuntimeWarning 错误"""
        try:
            self.timer.timeout.disconnect()
        except Exception:
            pass  # 若此前未连接任何槽函数则忽略异常

    # ------------------- 1. 摄像头预览与人脸录入模块 -------------------
    def update_frame(self) -> None:
        """基础摄像头帧刷新逻辑：绘制人脸检测框并在 QLabel 上显示"""
        if self.cap is not None and self.cap.isOpened():
            res, frame = self.cap.read()
            if not res:
                return

            # 水平镜像翻转（符合人体镜像习惯）
            frame = cv.flip(frame, 1)
            
            # 获取当前界面视频 Label 的尺寸，并同步调整帧尺寸
            lbl_w = self.ui.label_video.width()
            lbl_h = self.ui.label_video.height()
            if lbl_w > 0 and lbl_h > 0:
                frame = cv.resize(frame, (lbl_w, lbl_h))

            # 转为灰度图进行人脸检测
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(gray, 1.2, 3, minSize=(100, 100))

            # 绘制绿色人脸框
            for (x, y, w, h) in faces:
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # OpenCV BGR 转为 Qt 识别的 RGB 格式
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            height, width, channel = frame_rgb.shape
            bytesPerLine = channel * width
            qImg = QImage(frame_rgb.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.ui.label_video.setPixmap(QPixmap.fromImage(qImg))

    def click_open_video(self) -> None:
        """点击【打开摄像头/录入人脸】按钮：控制摄像头开启，或暂停捕获图像并保存人脸"""
        print("打开摄像头 / 录入人脸")
        
        # 若摄像头尚未打开，则初始化摄像头并启动预览
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv.VideoCapture(0)
            self.safe_disconnect_timer()
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)  # 每 30 毫秒刷新一帧 (~33fps)
        else:
            # 若摄像头已打开，点击则代表“抓拍并保存当前人脸样本”
            if self.timer.isActive():
                self.timer.stop()
            
            res, frame = self.cap.read()
            if res:
                lbl_w = self.ui.label_video.width()
                lbl_h = self.ui.label_video.height()
                if lbl_w > 0 and lbl_h > 0:
                    frame = cv.resize(frame, (lbl_w, lbl_h))

                gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                faces = self.faceCascade.detectMultiScale(gray, 1.2, 3, minSize=(100, 100))
                
                if len(faces) > 0:
                    # 获取识别到的第一个人脸 ROI 区域
                    x, y, w, h = faces[0]
                    self.roi_gray = gray[y:y+h, x:x+w]
                    
                    # 跟据当日日期保存人脸数据
                    try:
                        save_dir = "./facedata"
                        os.makedirs(save_dir, exist_ok=True)
                
                        # 按照“年月日_时分秒”格式生成独立文件名，防止重名覆盖
                        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                        file_path = os.path.join(save_dir, filename)
                
                        success = cv.imwrite(file_path, self.roi_gray)
                        if success:
                            self.show_auto_close_msg(
                                "保存成功", 
                                f"人脸图片已自动保存至：\n{os.path.abspath(file_path)}\n\n（提示：窗口将在 1 秒后自动关闭）",
                                QMessageBox.Information,
                                1000
                            )
                        else:
                            self.show_auto_close_msg(
                                "保存失败", 
                                f"文件写入失败，请检查文件夹权限或路径：\n{file_path}",
                                QMessageBox.Critical,
                                1000
                    )
                    except Exception as e:
                        self.show_auto_close_msg("保存失败", f"文件保存异常：\n{str(e)}", QMessageBox.Critical, 1000)
                else:
                    self.show_auto_close_msg("提示", "目前没有人脸内容，请保证后面中有人脸存在！", QMessageBox.Warning, 1000)
            # 恢复画面实时更新
            self.timer.start(30)

    def click_close(self) -> None:
        """点击【关闭】按钮：停止定时器，释放摄像头硬件并清除画面，重置验证状态"""
        self.face_pass = False
        if self.timer.isActive():
            self.timer.stop()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.ui.label_video.clear()

    # ------------------- 2. 人脸识别模块 -------------------
    def update_frame_recognizer(self) -> None:
        """人脸识别刷新逻辑：对画面进行人脸比对并标注姓名/编号和置信度"""
        if self.cap is not None and self.cap.isOpened():
            res, frame = self.cap.read()
            if not res:
                return

            lbl_w = self.ui.label_video.width()
            lbl_h = self.ui.label_video.height()
            if lbl_w > 0 and lbl_h > 0:
                frame = cv.resize(frame, (lbl_w, lbl_h))

            frame = cv.flip(frame, 1)

            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(gray, 1.2, 5)

            # 遍历所有检测到的人脸
            for (x, y, w, h) in faces:
                # 利用 LBPH 模型进行人脸预测（返回 ID 和置信度/距离距离）
                face_id, conf = self.recognizer.predict(gray[y:y+h, x:x+w])
                
                # LBPH 置信度越小代表越匹配 (通常 < 80 判定为已知人脸)
                if conf < 80:
                    self.face_pass = True  # 标记权限已通过！
                    frame = self.putChineseText(frame, f"编号:{face_id},置信度:{conf:.1f}", (x, y-35), fontsize=30)
                else:
                    frame = self.putChineseText(frame, f"未知人脸,置信度:{conf:.1f}", (x, y-35), fontsize=30)
                
                # 绘制定位方框
                cv.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 0))

            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            q_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.ui.label_video.setPixmap(QPixmap.fromImage(q_img))

    def click_recognizer(self) -> None:
        """点击【人脸识别】按钮：自动读取训练集中照片并开始人脸识别过程"""
        if not self.face_pass:
            # 若包含训练数据，则进行自动在线训练
            if os.path.exists(self.path) and len(os.listdir(self.path)) > 0:
                self.faceTrain(self.path)
            else:
                self.show_auto_close_msg("警告","没有找到训练样本，请先录入人脸！",QMessageBox.Critical)
                return

        if self.cap is None or not self.cap.isOpened():
            self.cap = cv.VideoCapture(0)
            
        self.safe_disconnect_timer()
        self.timer.timeout.connect(self.update_frame_recognizer)
        self.timer.start(30)

    # ------------------- 3. 隔空手势画板与保存模块 -------------------
    def update_frame_draw(self) -> None:
        """手势画板刷新逻辑：接收 AirCanvas 渲染后的图像帧，并同步界面状态"""
        if self.cap is not None and self.cap.isOpened():
            res, frame = self.cap.read()
            if not res:
                return

            lbl_w = self.ui.label_video.width()
            lbl_h = self.ui.label_video.height()
            if lbl_w > 0 and lbl_h > 0:
                frame = cv.resize(frame, (lbl_w, lbl_h))

            frame = cv.flip(frame, 1)

            if self.air_canvas is not None:
                # 监听窗口尺寸变化，实时同步画板分辨率
                if self.air_canvas.width != lbl_w or self.air_canvas.height != lbl_h:
                    self.air_canvas.width = lbl_w
                    self.air_canvas.height = lbl_h
                    self.air_canvas.canvas = None

                # 核心方法：处理当前帧（计算手势轨迹、更新画布）
                frame = self.air_canvas.process(frame)
                
                # 手势选色时反向同步更新 Slider 和 Label 界面
                self.read_color()

                # 若使用手势调整了粗细，反向同步到 UI 的 SpinBox 控件
                if hasattr(self.air_canvas, 'draw_thickness'):
                    current_thickness = int(self.air_canvas.draw_thickness)
                    if self.ui.font_size.value() != current_thickness:
                        self.ui.font_size.blockSignals(True)  # 阻止触发二次信号回路
                        self.ui.font_size.setValue(current_thickness)
                        self.ui.font_size.blockSignals(False)

            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            q_img = QImage(frame_rgb.data, w, h, ch * w, QImage.Format_RGB888)
            self.ui.label_video.setPixmap(QPixmap.fromImage(q_img))

    def click_draw(self) -> None:
        """点击【隔空画板】按钮：校验人脸权限，成功后启动手势画板"""
        if not self.face_pass:
            self.show_auto_close_msg("权限不足", "请先通过人脸识别验证！", QMessageBox.Critical, 2000)
            return

        if self.cap is None or not self.cap.isOpened():
            self.cap = cv.VideoCapture(0)

        lbl_w = self.ui.label_video.width() or 1050
        lbl_h = self.ui.label_video.height() or 750

        # 初始化画板对象
        if self.air_canvas is None:
            self.air_canvas = draw.AirCanvas(width=lbl_w, height=lbl_h)
            # 初始化时同步 UI 颜色至画板
            self.on_slider_changed()

        self.safe_disconnect_timer()
        self.timer.timeout.connect(self.update_frame_draw)
        self.timer.start(30)

    def show_auto_close_msg(self, title: str, text: str, icon=QMessageBox.Information, timeout_ms: int = 2000):
        """辅助方法：弹出在指定毫秒数后自动关闭的提示框（提高操作交互体验）"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        
        # 借助 QTimer.singleShot 设置延迟定时关闭
        QTimer.singleShot(timeout_ms, msg_box.accept)
        msg_box.exec()

    def click_save_pic(self) -> None:
        """点击【保存画作】按钮：把当前绘画画布导出为文件"""
        if self.air_canvas is not None and self.air_canvas.canvas is not None and self.face_pass:
            try:
                save_dir = "Pic_save"
                os.makedirs(save_dir, exist_ok=True)
                
                # 按照“年月日_时分秒”格式生成独立文件名，防止重名覆盖
                filename = f"drawing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                file_path = os.path.join(save_dir, filename)
                
                success = cv.imwrite(file_path, self.air_canvas.canvas)
                if success:
                    self.show_auto_close_msg(
                        "保存成功", 
                        f"画作已自动保存至：\n{os.path.abspath(file_path)}\n\n（提示：窗口将在 2 秒后自动关闭）",
                        QMessageBox.Information,
                        2000
                    )
                else:
                    self.show_auto_close_msg(
                        "保存失败", 
                        f"文件写入失败，请检查文件夹权限或路径：\n{file_path}",
                        QMessageBox.Critical,
                        2000
                    )
            except Exception as e:
                self.show_auto_close_msg("保存失败", f"文件保存异常：\n{str(e)}", QMessageBox.Critical, 2000)
        else:
            self.show_auto_close_msg("提示", "目前没有可保存的画板内容，请先点击【打开画布】进行创作！", QMessageBox.Warning, 2000)

    # ------------------- 4. 颜色与调色盘逻辑 -------------------
    def on_slider_changed(self) -> None:
        """响应 RGB 三个垂直滑动条拖拽事件：同步更新数值文本、示例色块与画笔颜色"""
        blue = self.ui.verticalSlider_blue.value()
        green = self.ui.verticalSlider_green.value()
        red = self.ui.verticalSlider_red.value()

        # 更新 RGB 数值 Label 标签
        self.ui.label_blue_num.setNum(blue)
        self.ui.label_green_num.setNum(green)
        self.ui.label_red_num.setNum(red)

        # 通过 QSS 样式表改变颜色预览色块的背景属性
        self.ui.label_symble.setStyleSheet(f"background-color: rgb({red}, {green}, {blue});")

        # 将最新的 BGR 色值发送给 AirCanvas 画画底册
        if self.air_canvas is not None:
            self.air_canvas.change_BGR_color(blue, green, red)

    def read_color(self) -> None:
        """反向同步：当使用手势在画面中吸色/选色后，把颜色数值同步回 Qt 界面滑动条"""
        if self.air_canvas is not None:
            bgr = self.air_canvas.get_BGR_color()
            
            # 临时屏蔽滑动条信号（防止 blockSignals 导致死循环发送触发事件）
            self.ui.verticalSlider_blue.blockSignals(True)
            self.ui.verticalSlider_green.blockSignals(True)
            self.ui.verticalSlider_red.blockSignals(True)

            # 同步更新 UI 控件
            self.ui.label_blue_num.setNum(bgr[0])
            self.ui.label_green_num.setNum(bgr[1])
            self.ui.label_red_num.setNum(bgr[2])
            self.ui.verticalSlider_blue.setValue(bgr[0])
            self.ui.verticalSlider_green.setValue(bgr[1])
            self.ui.verticalSlider_red.setValue(bgr[2])
            self.ui.label_symble.setStyleSheet(f"background-color: rgb({bgr[2]}, {bgr[1]}, {bgr[0]});")

            # 解除信号屏蔽
            self.ui.verticalSlider_blue.blockSignals(False)
            self.ui.verticalSlider_green.blockSignals(False)
            self.ui.verticalSlider_red.blockSignals(False)

    def click_color_select(self) -> None:
        """点击【颜色选择】按钮：打开系统原生颜色选择对话框 (QColorDialog)"""
        current_color = QColor(
            self.ui.verticalSlider_red.value(),
            self.ui.verticalSlider_green.value(),
            self.ui.verticalSlider_blue.value()
        )
        color = QColorDialog.getColor(current_color, self, "选择画笔颜色")
        if color.isValid():
            # 将选择的新颜色更新到滑动条（自动触发 on_slider_changed）
            self.ui.verticalSlider_red.setValue(color.red())
            self.ui.verticalSlider_green.setValue(color.green())
            self.ui.verticalSlider_blue.setValue(color.blue())

    # ------------------- 5. 模型训练与文本/图像辅助 -------------------
    def getImagesAndLabels(self, data_path: str):
        """遍历指定人脸数据目录，解析人脸图像并提取对应的数字 ID 标签"""
        Sample = []
        ids = []
        filenames = [os.path.join(data_path, f) for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
        
        for filename in filenames:
            basename = os.path.basename(filename)
            name_part = basename.split(".")[0]
            # 跳过命名不规范的非数字文件名
            if not name_part.isdigit():
                continue
                
            img = cv.imread(filename)
            if img is None:
                continue
                
            gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(gray)
            face_id = int(name_part)
            
            for (x, y, w, h) in faces:
                Sample.append(gray[y:y+h, x:x+w])
                ids.append(face_id)
                
        return Sample, ids

    def faceTrain(self, data_path: str) -> None:
        """训练 LBPH 人脸识别模型，并将训练模型导出写为 xml/yml 文件"""
        images, labels = self.getImagesAndLabels(data_path)
        if len(images) == 0:
            self.show_auto_close_msg("检测失败", "未能识别到有效的人脸图片！", QMessageBox.Critical, 2000)
            return
        # 使用图像与对应数字标签训练分类器
        self.recognizer.train(images, np.array(labels))
        os.makedirs("./model", exist_ok=True)
        self.recognizer.write("./model/trainer.yml")

    def putChineseText(self, image, text, position, color=(255, 0, 255), fontsize=40):
        """借助 Pillow (PIL) 库实现 OpenCV 图像上叠加中文绘制（解决 OpenCV 原生不支持中文问题）"""
        PILImg = Image.fromarray(cv.cvtColor(image, cv.COLOR_BGR2RGB))
        draw_obj = ImageDraw.Draw(PILImg)
        
        font_path = "./STCAIYUN.TTF" if os.path.exists("./STCAIYUN.TTF") else "simhei.ttf"
        try:
            fontstyle = ImageFont.truetype(font_path, fontsize, encoding="utf-8")
        except Exception:
            fontstyle = ImageFont.load_default()
            
        draw_obj.text(position, text, fill=color, font=fontstyle)
        return cv.cvtColor(np.asarray(PILImg), cv.COLOR_RGB2BGR)

    def cv_imread(self, file_path: str):
        """兼容包含中文/特殊字符路径的 OpenCV 图片读取通用函数"""
        return cv.imdecode(np.fromfile(file_path, dtype=np.uint8), cv.IMREAD_COLOR)

    def click_pic_select(self) -> None:
        """点击【背景选择】按钮：打开文件选择框，将本地图片作为手势画板的背景图"""
        if (self.air_canvas is None) or (not self.face_pass):
            self.show_auto_close_msg("提示", "请先打开或初始化画布！", QMessageBox.Information)
            return

        pic_dir = "Pic_example"
        os.makedirs(pic_dir, exist_ok=True)

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择背景图片", pic_dir, "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            bg_img = self.cv_imread(file_path)
            if bg_img is None:
                self.show_auto_close_msg("读取失败", "无法识别该图片文件，请重试！", QMessageBox.Critical)
                return

            self.air_canvas.set_background_image(bg_img)

    def on_brush_size_changed(self, val: int) -> None:
        """响应画笔粗细数值 SpinBox 框的改变，更新 AirCanvas 画板的笔触粗细"""
        if self.air_canvas is not None:
            self.air_canvas.draw_thickness = int(val)


# ------------------- 6. 程序入口执行 -------------------
if __name__ == "__main__":
    # 创建 Qt 应用程序实例
    app = QApplication([])
    
    # 实例化并显示主界面
    main_window = AirCanvasApp()
    main_window.show()
    
    # 进入 Qt 应用程序主事件循环
    app.exec()