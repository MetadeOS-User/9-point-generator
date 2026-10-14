"""Padrão de 9 pontos - versão para celular (Kivy)."""

import math

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, platform

# Cores da interface (as mesmas da versão desktop)
FUNDO = get_color_from_hex("#111827")
COR_PONTOS = get_color_from_hex("#64748b")
COR_LINHA = get_color_from_hex("#38bdf8")
COR_SELECIONADO = get_color_from_hex("#e0f2fe")
COR_TEXTO = get_color_from_hex("#e5e7eb")
COR_SUBTITULO = get_color_from_hex("#9ca3af")
COR_BOTAO = get_color_from_hex("#1f2937")


class PadraoWidget(Widget):
    """Área de desenho com os nove pontos. Tudo é proporcional ao tamanho da tela."""

    def __init__(self, ao_mudar=None, **kwargs):
        super().__init__(**kwargs)
        self.ao_mudar = ao_mudar  # chamada sempre que a sequência muda

        self.pontos = {}
        self.espacamento = 0
        self.raio_toque = 0

        self.padrao = []
        self.desenhando = False
        self.ultima_posicao = None
        self.toque_atual = None
        self.cursor = None

        self.bind(pos=self.recalcular, size=self.recalcular)

    # ------------------------------------------------------------------ layout
    def recalcular(self, *_):
        """Reposiciona os pontos, da esquerda para a direita e de cima para baixo."""
        self.espacamento = min(self.width, self.height) * 0.36
        self.raio_toque = self.espacamento * 0.22

        centro_x = self.x + self.width / 2
        centro_y = self.y + self.height / 2

        self.pontos = {}
        numero = 0
        for linha in range(3):
            for coluna in range(3):
                self.pontos[numero] = (
                    centro_x + (coluna - 1) * self.espacamento,
                    centro_y + (1 - linha) * self.espacamento,  # y cresce para cima no Kivy
                )
                numero += 1

        self.desenhar()

    # ---------------------------------------------------------------- geometria
    def ponto_proximo(self, x, y):
        """Retorna o ponto mais próximo se o dedo estiver dentro da área de toque."""
        melhor_ponto = None
        melhor_distancia = self.raio_toque

        for numero, (px, py) in self.pontos.items():
            distancia = math.hypot(x - px, y - py)
            if distancia <= melhor_distancia:
                melhor_distancia = distancia
                melhor_ponto = numero

        return melhor_ponto

    @staticmethod
    def distancia_segmento(px, py, x1, y1, x2, y2):
        """Distância de um ponto até o segmento entre duas posições."""
        dx = x2 - x1
        dy = y2 - y1
        comprimento2 = dx * dx + dy * dy

        if comprimento2 == 0:
            return math.hypot(px - x1, py - y1), 0.0

        t = ((px - x1) * dx + (py - y1) * dy) / comprimento2
        t = max(0.0, min(1.0, t))
        mais_proximo_x = x1 + t * dx
        mais_proximo_y = y1 + t * dy
        distancia = math.hypot(px - mais_proximo_x, py - mais_proximo_y)
        return distancia, t

    def adicionar_pontos_no_segmento(self, x1, y1, x2, y2):
        """Registra os pontos atravessados, inclusive se o dedo se mover rapidamente."""
        encontrados = []

        for numero, (px, py) in self.pontos.items():
            if numero in self.padrao:
                continue

            distancia, t = self.distancia_segmento(px, py, x1, y1, x2, y2)
            if distancia <= self.raio_toque:
                encontrados.append((t, numero))

        for _, numero in sorted(encontrados):
            if numero not in self.padrao:
                self.padrao.append(numero)

    # ------------------------------------------------------------------ toques
    def on_touch_down(self, toque):
        if self.toque_atual is not None or not self.collide_point(*toque.pos):
            return super().on_touch_down(toque)

        ponto = self.ponto_proximo(*toque.pos)
        if ponto is None:
            self.desenhando = False
            return super().on_touch_down(toque)

        # Cada novo gesto começa um padrão novo.
        toque.grab(self)
        self.toque_atual = toque.uid
        self.padrao = [ponto]
        self.desenhando = True
        self.ultima_posicao = tuple(toque.pos)
        self.cursor = None
        self.notificar()
        self.desenhar()
        return True

    def on_touch_move(self, toque):
        if toque.grab_current is not self or toque.uid != self.toque_atual:
            return False
        if not self.desenhando or self.ultima_posicao is None:
            return True

        x1, y1 = self.ultima_posicao
        x2, y2 = toque.pos
        quantidade_antes = len(self.padrao)

        self.adicionar_pontos_no_segmento(x1, y1, x2, y2)

        self.ultima_posicao = (x2, y2)
        self.cursor = (x2, y2)

        if len(self.padrao) != quantidade_antes:
            self.notificar()
        self.desenhar()
        return True

    def on_touch_up(self, toque):
        if toque.grab_current is not self:
            return False

        toque.ungrab(self)
        if toque.uid == self.toque_atual:
            self.toque_atual = None
            self.desenhando = False
            self.ultima_posicao = None
            self.cursor = None
            self.desenhar()
        return True

    def limpar(self, *_):
        self.padrao = []
        self.desenhando = False
        self.ultima_posicao = None
        self.toque_atual = None
        self.cursor = None
        self.notificar()
        self.desenhar()

    def notificar(self):
        if self.ao_mudar is not None:
            self.ao_mudar(list(self.padrao))

    # ----------------------------------------------------------------- desenho
    def desenhar(self):
        self.canvas.clear()
        if not self.pontos:
            return

        espacamento = self.espacamento

        with self.canvas:
            # Linha do padrão já desenhado.
            coordenadas = [self.pontos[n] for n in self.padrao]
            if len(coordenadas) >= 2:
                achatadas = [valor for ponto in coordenadas for valor in ponto]
                Color(*COR_LINHA)
                Line(points=achatadas, width=dp(3), cap="round", joint="round")

            # Durante o gesto, mostra a linha seguindo o dedo.
            if self.desenhando and self.padrao and self.cursor is not None:
                x, y = self.pontos[self.padrao[-1]]
                Color(*COR_LINHA)
                Line(points=[x, y, *self.cursor], width=dp(2.5), cap="round")

            # Desenha os nove pontos por cima das linhas.
            for numero, (x, y) in self.pontos.items():
                if numero in self.padrao:
                    raio = espacamento * 0.12
                    Color(*COR_LINHA)
                    Ellipse(pos=(x - raio, y - raio), size=(2 * raio, 2 * raio))

                    raio = espacamento * 0.05
                    Color(*COR_SELECIONADO)
                    Ellipse(pos=(x - raio, y - raio), size=(2 * raio, 2 * raio))
                else:
                    raio = espacamento * 0.08
                    Color(*COR_PONTOS)
                    Ellipse(pos=(x - raio, y - raio), size=(2 * raio, 2 * raio))


class Padrao9PontosApp(App):
    def build(self):
        self.title = "Padrão de 9 pontos"
        Window.clearcolor = FUNDO

        no_celular = platform in ("android", "ios")
        if not no_celular:
            # Para testar no computador com um formato parecido com o de um celular.
            Window.size = (400, 780)
            Window.bind(on_keyboard=self.ao_teclar)

        # Folga extra no Android para a barra de status e a barra de navegação.
        margem_topo = dp(36) if no_celular else dp(18)
        margem_base = dp(24)

        raiz = BoxLayout(
            orientation="vertical",
            padding=[dp(16), margem_topo, dp(16), margem_base],
            spacing=dp(8),
        )

        raiz.add_widget(
            Label(
                text="Padrão de 9 pontos",
                font_size=sp(24),
                bold=True,
                color=COR_TEXTO,
                size_hint_y=None,
                height=dp(44),
            )
        )
        raiz.add_widget(
            Label(
                text="Toque em um ponto e arraste para desenhar",
                font_size=sp(14),
                color=COR_SUBTITULO,
                size_hint_y=None,
                height=dp(28),
            )
        )

        self.area = PadraoWidget(ao_mudar=self.atualizar_sequencia)
        raiz.add_widget(self.area)

        self.rotulo_sequencia = Label(
            font_size=sp(16),
            color=COR_TEXTO,
            size_hint_y=None,
            height=dp(32),
        )
        raiz.add_widget(self.rotulo_sequencia)

        botao = Button(
            text="Limpar",
            font_size=sp(16),
            color=COR_TEXTO,
            background_normal="",
            background_color=COR_BOTAO,
            size_hint_y=None,
            height=dp(52),
        )
        botao.bind(on_release=self.area.limpar)
        raiz.add_widget(botao)

        self.atualizar_sequencia([])
        return raiz

    def atualizar_sequencia(self, padrao):
        # Mostra os pontos de 1 a 9 (da esquerda para a direita, de cima para baixo).
        if padrao:
            self.rotulo_sequencia.text = "Sequência: " + " - ".join(str(n + 1) for n in padrao)
        else:
            self.rotulo_sequencia.text = "Sequência: -"

    def ao_teclar(self, _janela, tecla, *_args):
        # Esc limpa o padrão ao testar no computador (como na versão original).
        if tecla == 27:
            self.area.limpar()
            return True
        return False


if __name__ == "__main__":
    Padrao9PontosApp().run()
