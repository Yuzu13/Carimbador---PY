import customtkinter as ctk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import os
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import threading

USUARIOS = {
    "joao": "1234",
    "maria": "abcd"
}

PASTA_CARIMBOS = "carimbos"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🕸️ Carimbador de PDF")
        self.geometry("420x350")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")  # opções: "light", "dark", "system"
        ctk.set_default_color_theme("blue")  # opções: "blue", "green", "dark-blue"

        self.pdf_path = ""

        # Layout
        self.label_title = ctk.CTkLabel(self, text="Carimbador de PDF", font=("Segoe UI", 20, "bold"))
        self.label_title.pack(pady=10)

        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Usuário")
        self.entry_nome.pack(pady=8, fill="x", padx=60)

        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*")
        self.entry_senha.pack(pady=8, fill="x", padx=60)

        self.btn_pdf = ctk.CTkButton(self, text="Selecionar PDF", command=self.selecionar_pdf)
        self.btn_pdf.pack(pady=12)

        self.btn_carimbar = ctk.CTkButton(self, text="Carimbar PDF", command=self.iniciar_carimbamento)
        self.btn_carimbar.pack()

        self.label_status = ctk.CTkLabel(self, text="", text_color="gray")
        self.label_status.pack(pady=10)

    def selecionar_pdf(self):
        self.pdf_path = fd.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if self.pdf_path:
            self.label_status.configure(text="PDF selecionado.")

    def criar_carimbo_pdf(self, imagem_path, largura, altura, temp_file):
        c = canvas.Canvas(temp_file, pagesize=(largura, altura))
        img = Image.open(imagem_path)
        img_width, img_height = img.size
        largura_desejada = 120
        proporcao = largura_desejada / img_width
        altura_desejada = img_height * proporcao
        pos_x = largura - largura_desejada - 40
        pos_y = 40
        c.drawImage(ImageReader(img), pos_x, pos_y, width=largura_desejada, height=altura_desejada, mask='auto')
        c.save()

    def carimbar_pdf(self):
        nome = self.entry_nome.get().strip().lower()
        senha = self.entry_senha.get().strip()

        if nome not in USUARIOS:
            mb.showerror("Erro", "Usuário não encontrado.")
            return

        if senha != USUARIOS[nome]:
            mb.showerror("Erro", "Senha incorreta.")
            return

        if not self.pdf_path:
            mb.showerror("Erro", "Selecione um PDF.")
            return

        imagem_carimbo = os.path.join(PASTA_CARIMBOS, f"{nome}.png")
        if not os.path.exists(imagem_carimbo):
            mb.showerror("Erro", f"Imagem do carimbo não encontrada: {imagem_carimbo}")
            return

        try:
            with open(self.pdf_path, "rb") as pdf_file:
                leitor = PyPDF2.PdfReader(pdf_file)
                escritor = PyPDF2.PdfWriter()
                largura = float(leitor.pages[0].mediabox.width)
                altura = float(leitor.pages[0].mediabox.height)
                temp_carimbo = "temp_carimbo.pdf"
                self.criar_carimbo_pdf(imagem_carimbo, largura, altura, temp_carimbo)

                with open(temp_carimbo, "rb") as carimbo_file:
                    carimbo_pdf = PyPDF2.PdfReader(carimbo_file)
                    pagina_carimbo = carimbo_pdf.pages[0]

                    for pagina in leitor.pages:
                        pagina.merge_page(pagina_carimbo)
                        escritor.add_page(pagina)

                nome_saida = os.path.splitext(self.pdf_path)[0] + f"_{nome}_carimbado.pdf"
                with open(nome_saida, "wb") as saida:
                    escritor.write(saida)

            os.remove("temp_carimbo.pdf")
            mb.showinfo("Sucesso", f"PDF carimbado salvo como:\n{nome_saida}")
            self.label_status.configure(text="Pronto.")
        except Exception as e:
            mb.showerror("Erro", f"Erro ao carimbar:\n{e}")

    def iniciar_carimbamento(self):
        threading.Thread(target=self.carimbar_pdf, daemon=True).start()


if __name__ == "__main__":
    if not os.path.exists(PASTA_CARIMBOS):
        os.makedirs(PASTA_CARIMBOS)
    app = App()
    app.mainloop()
