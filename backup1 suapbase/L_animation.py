import random
from typing import List, Optional, Tuple
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QBrush, QLinearGradient, QRadialGradient, QFont, QPen

class Ball:
    def __init__(self, x: float, y: float, vx: float, vy: float, radius: int, number: int, parent_widget: 'LottoAnimationWidget') -> None:
        self.pos = QPointF(x, y)
        self.vel = QPointF(vx, vy)
        self.radius = radius
        self.number = number
        self.color1, self.color2 = self.get_color_for_number(number)
        self.widget = parent_widget

    def get_color_for_number(self, number: int) -> Tuple[QColor, QColor]:
        if 1 <= number <= 10: return QColor("#fbc400"), QColor("#f9a825")
        if 11 <= number <= 20: return QColor("#69c8f2"), QColor("#29b6f6")
        if 21 <= number <= 30: return QColor("#ff7272"), QColor("#f44336")
        if 31 <= number <= 40: return QColor("#aaaaaa"), QColor("#8e8e8e")
        if 41 <= number <= 45: return QColor("#b0d840"), QColor("#8bc34a")
        return QColor("#dddddd"), QColor("#aaaaaa")

    def move(self) -> None:
        bounds = self.widget.rect()
        self.pos += self.vel
        if self.pos.x() - self.radius < 0:
            self.pos.setX(self.radius)
            self.vel.setX(-self.vel.x())
        elif self.pos.x() + self.radius > bounds.width():
            self.pos.setX(bounds.width() - self.radius)
            self.vel.setX(-self.vel.x())

        if self.pos.y() - self.radius < 0:
            self.pos.setY(self.radius)
            self.vel.setY(-self.vel.y())
        elif self.pos.y() + self.radius > bounds.height():
            self.pos.setY(bounds.height() - self.radius)
            self.vel.setY(-self.vel.y())

class LottoAnimationWidget(QWidget):
    animation_finished = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.balls: List[Ball] = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.animation_duration_timer = QTimer(self)
        self.animation_duration_timer.setSingleShot(True)
        self.animation_duration_timer.timeout.connect(self.on_animation_finished)

    def init_balls(self) -> None:
        self.balls.clear()
        if self.width() == 0 or self.height() == 0:
            return
            
        for i in range(1, 46):
            radius = 25
            x = random.uniform(radius, self.width() - radius)
            y = random.uniform(radius, self.height() - radius)
            vx = random.uniform(-1.5, 1.5)
            vy = random.uniform(-1.5, 1.5)
            self.balls.append(Ball(x, y, vx, vy, radius, i, self))

    def start_animation(self) -> None:
        if not self.balls:
            self.init_balls()
        if self.balls:
            self.timer.start(16) # ~60 FPS
            self.animation_duration_timer.start(500) # Emit signal after 0.5 seconds

    def stop_animation(self) -> None:
        self.timer.stop()

    def draw_numbers(self, numbers: List[int]) -> None:
        # This method can be used to pass the numbers to be displayed/animated
        # For now, we'll just re-initialize balls if needed and start animation
        # A more sophisticated animation might use these numbers to highlight specific balls
        if not self.balls:
            self.init_balls()
        # You might want to store these numbers and use them in paintEvent
        # self.numbers_to_display = numbers 
        self.start_animation()

    def on_animation_finished(self) -> None:
        self.animation_finished.emit()

    def update_animation(self) -> None:
        for ball in self.balls:
            ball.move()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1e1e2f"))

        for ball in self.balls:
            rect = self.get_ball_rect(ball)
            
            # 3D 애니메이션 볼 그림자
            shadow_rect = rect.translated(3, 3)
            painter.setBrush(QColor(0, 0, 0, 100))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(shadow_rect)
            
            # 3D 라디얼 그라데이션
            radial_gradient = QRadialGradient(
                rect.center().x() - rect.width() * 0.2,
                rect.center().y() - rect.height() * 0.2,
                rect.width() * 0.6
            )
            radial_gradient.setColorAt(0, ball.color1.lighter(140))
            radial_gradient.setColorAt(0.4, ball.color1.lighter(110))
            radial_gradient.setColorAt(0.8, ball.color1)
            radial_gradient.setColorAt(1, ball.color2.darker(110))
            
            painter.setBrush(radial_gradient)
            painter.drawEllipse(rect)
            
            # 3D 하이라이트
            highlight_rect = rect.adjusted(
                rect.width()//4, rect.height()//4,
                -rect.width()//2, -rect.height()//2
            )
            highlight_gradient = QRadialGradient(
                highlight_rect.center().x(),
                highlight_rect.center().y(),
                highlight_rect.width()//2
            )
            highlight_gradient.setColorAt(0, QColor(255, 255, 255, 100))
            highlight_gradient.setColorAt(1, QColor(255, 255, 255, 0))
            
            painter.setBrush(highlight_gradient)
            painter.drawEllipse(highlight_rect)
            
            # 둘러리 테두리
            painter.setPen(QPen(ball.color2.darker(130), 1.5))
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(rect.adjusted(1, 1, -1, -1))

            # 3D 숫자 효과
            font = QFont("Arial", int(ball.radius * 0.7), QFont.Bold)
            painter.setFont(font)
            
            # 숫자 그림자
            painter.setPen(QColor(0, 0, 0, 180))
            shadow_text_rect = rect.translated(1, 1)
            painter.drawText(shadow_text_rect, Qt.AlignCenter, str(ball.number))
            
            # 메인 숫자
            painter.setPen(QColor("#ffffff"))
            painter.drawText(rect, Qt.AlignCenter, str(ball.number))

    def get_ball_rect(self, ball: Ball) -> QRectF:
        size = ball.radius * 2
        return QRectF(ball.pos.x() - ball.radius, ball.pos.y() - ball.radius, size, size)

    def resizeEvent(self, event):
        self.init_balls()
        super().resizeEvent(event)

    def showEvent(self, event):
        self.start_animation()
        super().showEvent(event)

    def hideEvent(self, event):
        self.stop_animation()
        super().hideEvent(event)
