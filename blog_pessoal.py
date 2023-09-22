# Importe as bibliotecas necessárias
import sys
import sqlite3
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLineEdit, QMessageBox, QListWidget

# Crie uma classe para a aplicação do Blog
class BlogApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configure a janela principal
        self.setWindowTitle("Blog Pessoal")
        self.setGeometry(100, 100, 800, 600)

        # Crie um widget central e um layout vertical
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()

        # Crie widgets para a entrada de título, conteúdo e botões
        self.post_title = QLineEdit()
        self.post_content = QTextEdit()
        self.save_button = QPushButton("Salvar Postagem")
        self.delete_button = QPushButton("Excluir Postagem")
        self.post_list = QListWidget()

        # Adicione placeholders aos campos
        self.post_title.setPlaceholderText("Título")
        self.post_content.setPlaceholderText("Conteúdo do post")

        # Adicione os widgets ao layout vertical
        self.layout.addWidget(self.post_title)
        self.layout.addWidget(self.post_content)
        self.layout.addWidget(self.save_button)
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.post_list)

        # Configure o layout para o widget central
        self.central_widget.setLayout(self.layout)

        # Conecte os botões aos métodos correspondentes
        self.save_button.clicked.connect(self.save_post)
        self.delete_button.clicked.connect(self.delete_post)
        self.post_list.itemClicked.connect(self.load_post)

        # Inicialize o banco de dados e carregue as postagens existentes
        self.init_database()
        self.load_posts()

    # Método para inicializar o banco de dados SQLite
    def init_database(self):
        conn = sqlite3.connect('blog.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS postagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                conteudo TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    # Método para exibir uma caixa de diálogo de aviso
    def show_warning(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Aviso")
        msg_box.setText(message)
        msg_box.exec()

    # Método para salvar ou atualizar uma postagem
    def save_post(self):
        title = self.post_title.text()
        content = self.post_content.toPlainText()

        if title and content:
            conn = sqlite3.connect('blog.db')
            cursor = conn.cursor()

            # Verifica se o título já existe no banco de dados
            cursor.execute("SELECT id FROM postagens WHERE titulo=?", (title,))
            existing_post = cursor.fetchone()

            if existing_post:
                # Atualiza a postagem existente
                cursor.execute("UPDATE postagens SET conteudo=? WHERE id=?", (content, existing_post[0]))
                self.show_warning("Postagem atualizada com sucesso!")
            else:
                # Cria uma nova postagem
                cursor.execute("INSERT INTO postagens (titulo, conteudo) VALUES (?, ?)", (title, content))
                self.show_warning("Postagem salva com sucesso!")

            conn.commit()
            conn.close()

            # Limpa os campos e recarrega as postagens
            self.post_title.clear()
            self.post_content.clear()
            self.load_posts()
        else:
            self.show_warning("Título e conteúdo são obrigatórios.")

    # Método para excluir uma postagem selecionada
    def delete_post(self):
        selected_item = self.post_list.currentItem()
        if selected_item:
            post_id = selected_item.text().split(".")[0]
            conn = sqlite3.connect('blog.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM postagens WHERE id=?", (post_id,))
            conn.commit()
            conn.close()
            self.load_posts()
            self.post_title.clear()
            self.post_content.clear()
            self.show_warning("Postagem excluída com sucesso!")

    # Método para carregar todas as postagens do banco de dados
    def load_posts(self):
        self.post_list.clear()
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, titulo FROM postagens")
        posts = cursor.fetchall()
        conn.close()
        for post in posts:
            self.post_list.addItem(f"{post[0]}. {post[1]}")

    # Método para carregar uma postagem selecionada nos campos de entrada
    def load_post(self, item):
        post_id = item.text().split(".")[0]
        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()
        cursor.execute("SELECT titulo, conteudo FROM postagens WHERE id=?", (post_id,))
        post = cursor.fetchone()
        conn.close()
        if post:
            self.post_title.setText(post[0])
            self.post_content.setPlainText(post[1])

# Bloco de código principal para iniciar a aplicação
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BlogApp()
    window.show()
    sys.exit(app.exec())
