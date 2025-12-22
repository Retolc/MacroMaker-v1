import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import keyboard
import time
import random
import threading
import os
from PIL import Image, ImageTk
import pyautogui

class EditorMacros:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("MacroMaker")
        self.janela.geometry("900x750")
        self.janela.resizable(True, True)
        self.hotkey_iniciar = "ctrl+enter"
        self.hotkey_parar = "esc"
        self.macros = {}
        self.macro_atual = {"nome": "New Macro", "etapas": [], "repeticoes": 1, "modo_tempo": "steady", "tempo_fixo": "0.3"}
        self.executando = False
        self.thread_execucao = None
        self.aguardando_tecla = False
        self.tecla_atual = ""

        # Ações de mouse suportadas
        self.acoes_mouse = [
            "move",
            "left_click", 
            "right_click",
            "middle_click",
            "double_left_click",
            "double_right_click"
        ]
        # Hotkey para captura de mouse
        self.hotkey_captura_mouse = "ctrl+shift+c"

        self.carregar_macros()
        self.criar_interface()
        self.configurar_hotkeys()

        # Carregar configurações globais
        self.carregar_configuracoes_globais()


    def salvar_configuracoes_globais(self):
        """Salva as configurações globais em arquivo"""
        config = {
            "hotkey_iniciar": self.hotkey_iniciar,
            "hotkey_parar": self.hotkey_parar,
            "hotkey_captura_mouse": self.hotkey_captura_mouse
        }
        
        try:
            with open("config_global.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving global settings: {e}")

    def carregar_configuracoes_globais(self):
        """Carrega as configurações globais do arquivo"""
        try:
            if os.path.exists("config_global.json"):
                with open("config_global.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                self.hotkey_iniciar = config.get("hotkey_iniciar", "ctrl+enter")
                self.hotkey_parar = config.get("hotkey_parar", "esc")
                self.hotkey_captura_mouse = config.get("hotkey_captura_mouse", "ctrl+shift+c")
        except Exception as e:
            print(f"Error loading global settings: {e}")

    def configurar_hotkeys(self):
        """Configura as hotkeys globais"""
        try:
            # Remover hotkeys antigas se existirem
            keyboard.unhook_all()
            
            # Configurar novas hotkeys
            keyboard.add_hotkey(self.hotkey_iniciar, self.iniciar_execucao)
            keyboard.add_hotkey(self.hotkey_parar, self.parar_execucao)
            
            print(f"Hotkeys configured: {self.hotkey_iniciar}=Start, {self.hotkey_parar}=Stop, {self.hotkey_captura_mouse}=Mouse Capt.")
        except Exception as e:
            print(f"Warning: unable to configure hotkeys: {e}")



    def criar_dialogo_padrao(self, titulo, largura=400, altura=300):
        """Cria um diálogo padronizado centralizado"""
        dialog = tk.Toplevel(self.janela)
        dialog.title(titulo)
        dialog.geometry(f"{largura}x{altura}")
        dialog.resizable(False, False)
        dialog.transient(self.janela)
        dialog.grab_set()
        
        # Frame principal com padding
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Centralizar
        dialog.update_idletasks()
        x = (self.janela.winfo_x() + self.janela.winfo_width() // 2 - dialog.winfo_width() // 2)
        y = (self.janela.winfo_y() + self.janela.winfo_height() // 2 - dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        return dialog, main_frame


    def carregar_macros(self):
        """Carrega macros do arquivo JSON"""
        try:
            if os.path.exists("macros.json"):
                with open("macros.json", "r", encoding="utf-8") as f:
                    self.macros = json.load(f)
        except Exception as e:
            print(f"Error loading macros: {e}")
            self.macros = {}
    
    def salvar_macros(self):
        """Salva macros no arquivo JSON"""
        try:
            with open("macros.json", "w", encoding="utf-8") as f:
                json.dump(self.macros, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving macros: {e}")
    
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal com scroll
        main_frame = ttk.Frame(self.janela)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e Scrollbar para toda a interface
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_main_frame = ttk.Frame(canvas)
        
        self.scrollable_main_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_main_frame, anchor="nw", tags="frame")
        # E ADICIONE estas linhas DEPOIS:
        canvas.bind('<Configure>', lambda e: canvas.itemconfig("frame", width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        titulo = tk.Label(self.scrollable_main_frame, text="MacroMaker", 
                         font=("Arial", 16, "bold"))
        titulo.pack(pady=10)
        
        # Frame de gerenciamento de macros
        self.criar_frame_macros(self.scrollable_main_frame)
        
        # Frame de configurações
        self.criar_frame_configuracoes(self.scrollable_main_frame)
        
        # Frame de etapas
        self.criar_frame_etapas(self.scrollable_main_frame)
        
        # Frame de preview do teclado
        self.criar_frame_preview(self.scrollable_main_frame)
        
        # Frame de controles e status
        self.criar_frame_controles(self.scrollable_main_frame)
    
    def criar_frame_macros(self, parent):
        """Frame de gerenciamento de macros"""
        frame = ttk.LabelFrame(parent, text="💾 Macro Management", padding=10)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Linha 1 - Seleção de macro
        linha1 = ttk.Frame(frame)
        linha1.pack(fill=tk.X, pady=5)
        
        ttk.Label(linha1, text="Macro:").pack(side=tk.LEFT, padx=5)
        
        self.combo_macros = ttk.Combobox(linha1, values=list(self.macros.keys()), width=30)
        self.combo_macros.pack(side=tk.LEFT, padx=5)
        self.combo_macros.bind('<<ComboboxSelected>>', self.carregar_macro_selecionado)
        
        ttk.Button(linha1, text="📁 Load File", command=self.carregar_arquivo).pack(side=tk.LEFT, padx=2)
        ttk.Button(linha1, text="➕ New", command=self.novo_macro).pack(side=tk.LEFT, padx=2)
        ttk.Button(linha1, text="✏️ Edit Name", command=self.editar_nome_macro).pack(side=tk.LEFT, padx=2)
        ttk.Button(linha1, text="🗑️ Delete", command=self.excluir_macro).pack(side=tk.LEFT, padx=2)
        ttk.Button(linha1, text="💾 Save", command=self.salvar_macro_atual).pack(side=tk.LEFT, padx=2)
        
        # Linha 2 - Nome do macro
        linha2 = ttk.Frame(frame)
        linha2.pack(fill=tk.X, pady=5)
        
        ttk.Label(linha2, text="Name:").pack(side=tk.LEFT, padx=5)
        self.entry_nome = ttk.Entry(linha2, width=40)
        self.entry_nome.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_nome.insert(0, "New Macro")

    def atualizar_tempos_aleatorios(self):
        """Atualiza os tempos aleatórios na interface quando os valores mudam"""
        if self.combo_modo_tempo.get() == "random":
            self.atualizar_lista_etapas()

    def atualizar_tempos_fixos(self):
        """Atualiza os tempos fixos na interface quando o valor muda"""
        # Atualizar a lista de etapas para refletir o novo tempo fixo
        if self.combo_modo_tempo.get() == "steady":
            self.atualizar_lista_etapas()

    def atualizar_interface_repeticao(self):
        """Atualiza a interface quando o checkbox de repetição é alterado"""
        self.atualizar_lista_etapas()

    def criar_frame_configuracoes(self, parent):
        """Frame de configurações gerais"""
        frame = ttk.LabelFrame(parent, text="⚙️ General Settings", padding=10)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        linha = ttk.Frame(frame)
        linha.pack(fill=tk.X, pady=5)
        
        # Checkbox para ativar repetições por etapa
        self.var_repetir_acoes = tk.BooleanVar()
        self.check_repetir_acoes = ttk.Checkbutton(linha, text="Step repetitions", 
                                                variable=self.var_repetir_acoes,
                                                command=self.atualizar_interface_repeticao)
        self.check_repetir_acoes.pack(side=tk.LEFT, padx=5)
        
        # Repetições
        ttk.Label(linha, text="Repetitions:").pack(side=tk.LEFT, padx=5)
        self.spin_repeticoes = ttk.Spinbox(linha, from_=1, to=100, width=5, validate="key")
        self.spin_repeticoes.configure(validatecommand=(self.spin_repeticoes.register(self.validar_numero), '%P'))
        self.spin_repeticoes.set(1)
        self.spin_repeticoes.pack(side=tk.LEFT, padx=5)
        
        # Modo de tempo
        ttk.Label(linha, text="Time Mode:").pack(side=tk.LEFT, padx=5)
        self.combo_modo_tempo = ttk.Combobox(linha, values=["steady", "personalized", "random"], width=12)
        self.combo_modo_tempo.set("steady")
        self.combo_modo_tempo.pack(side=tk.LEFT, padx=5)
        self.combo_modo_tempo.bind('<<ComboboxSelected>>', self.atualizar_interface_tempo)
        
        # Frame para tempo fixo
        self.frame_tempo_fixo = ttk.Frame(frame)
        ttk.Label(self.frame_tempo_fixo, text="Fixed time:").pack(side=tk.LEFT, padx=5)
        self.entry_tempo_fixo = ttk.Entry(self.frame_tempo_fixo, width=8)
        self.entry_tempo_fixo.insert(0, "0.3")
        self.entry_tempo_fixo.bind('<KeyRelease>', lambda e: self.atualizar_tempos_fixos())
        self.entry_tempo_fixo.bind('<FocusOut>', lambda e: self.atualizar_tempos_fixos())
        self.entry_tempo_fixo.pack(side=tk.LEFT, padx=2)
        ttk.Label(self.frame_tempo_fixo, text="seconds").pack(side=tk.LEFT, padx=5)
        
        # Frame para configurações de tempo aleatório
        self.frame_tempo_aleatorio = ttk.Frame(frame)
        ttk.Label(self.frame_tempo_aleatorio, text="Between").pack(side=tk.LEFT, padx=5)
        self.entry_tempo_min = ttk.Entry(self.frame_tempo_aleatorio, width=5)
        self.entry_tempo_min.insert(0, "0.3")
        self.entry_tempo_min.pack(side=tk.LEFT, padx=2)
        self.entry_tempo_min.bind('<KeyRelease>', lambda e: self.atualizar_tempos_aleatorios())
        self.entry_tempo_min.bind('<FocusOut>', lambda e: self.atualizar_tempos_aleatorios())
        ttk.Label(self.frame_tempo_aleatorio, text="and").pack(side=tk.LEFT, padx=2)
        self.entry_tempo_max = ttk.Entry(self.frame_tempo_aleatorio, width=5)
        self.entry_tempo_max.insert(0, "2.0")
        self.entry_tempo_max.pack(side=tk.LEFT, padx=2)
        self.entry_tempo_max.bind('<KeyRelease>', lambda e: self.atualizar_tempos_aleatorios())  # ← NOVO
        self.entry_tempo_max.bind('<FocusOut>', lambda e: self.atualizar_tempos_aleatorios())   # ← NOVO
        ttk.Label(self.frame_tempo_aleatorio, text="seconds").pack(side=tk.LEFT, padx=5)
        
        # Mostrar tempo fixo por padrão
        self.frame_tempo_fixo.pack(fill=tk.X, pady=5)
    
    def criar_frame_etapas(self, parent):
        """Frame de edição de etapas"""
        frame = ttk.LabelFrame(parent, text="🎯 Macro Steps", padding=10)
        frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=10)
        
        # Cabeçalho da tabela
        cabecalho = ttk.Frame(frame)
        cabecalho.pack(fill=tk.X)
        
        ttk.Label(cabecalho, text="#", width=3).pack(side=tk.LEFT, padx=2)

        # ↓↓↓ NOVA COLUNA "TIPO" ↓↓↓
        ttk.Label(cabecalho, text="Type", width=6).pack(side=tk.LEFT, padx=2)
        ttk.Label(cabecalho, text="Action", width=22).pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        ttk.Label(cabecalho, text="Time (s)", width=10).pack(side=tk.LEFT, padx=2)

        if self.var_repetir_acoes.get():
            ttk.Label(cabecalho, text="Repeats", width=8).pack(side=tk.LEFT, padx=2)
        ttk.Label(cabecalho, text="Controls", width=15).pack(side=tk.LEFT, padx=2)
        
        # Frame scrollável para etapas
        container_etapas = ttk.Frame(frame)
        container_etapas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas_etapas = tk.Canvas(container_etapas)  # ← SEM height fixo
        scrollbar_etapas = ttk.Scrollbar(container_etapas, orient="vertical", command=self.canvas_etapas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_etapas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_etapas.configure(scrollregion=self.canvas_etapas.bbox("all"))
        )
        
        self.canvas_etapas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_etapas.configure(yscrollcommand=scrollbar_etapas.set)
        
        self.canvas_etapas.pack(side="left", fill="both", expand=True)
        scrollbar_etapas.pack(side="right", fill="y")
        
        # Botão adicionar etapa
        ttk.Button(frame, text="➕ Add Step", command=self.adicionar_etapa).pack(pady=10)
        
        self.frame_etapas = self.scrollable_frame
    
    def criar_frame_preview(self, parent):
        """Frame de preview do teclado (simplificado)"""
        frame = ttk.LabelFrame(parent, text="⌨️ Keyboard Preview", padding=10)
        frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Área simplificada do teclado
        self.label_preview = tk.Label(frame, text="PT/BR Keyboard - Layout detected\nClick on an action box and press the desired keys", 
                                     bg="lightgray", height=4, font=("Arial", 10), justify=tk.LEFT)
        self.label_preview.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(frame, text="🔄 Update Preview", command=self.atualizar_preview).pack(pady=5)
    
    def configurar_hotkeys_dialog(self):
        """Abre diálogo para configurar hotkeys"""
        dialog = tk.Toplevel(self.janela)
        dialog.title("Configure Hotkeys")
        dialog.geometry("500x300")  # Tamanho fixo adequado
        dialog.resizable(False, False)  # Não redimensionável
        dialog.transient(self.janela)
        dialog.grab_set()
        
        # Frame principal com padding
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Configure Hotkeys", 
                font=("Arial", 14, "bold")).pack(pady=(0, 20))
        
        # Frame para as hotkeys - usando grid para alinhamento perfeito
        keys_frame = ttk.Frame(main_frame)
        keys_frame.pack(fill=tk.X, pady=10)
        
        # Hotkey Iniciar
        ttk.Label(keys_frame, text="Start:", width=12).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        entry_iniciar = ttk.Entry(keys_frame, width=20)
        entry_iniciar.insert(0, self.hotkey_iniciar)
        entry_iniciar.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
        ttk.Button(keys_frame, text="Detect", width=8,
                command=lambda: self.detectar_hotkey(entry_iniciar)).grid(row=0, column=2, padx=5, pady=8)
        
        # Hotkey Parar
        ttk.Label(keys_frame, text="Stop:", width=12).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        entry_parar = ttk.Entry(keys_frame, width=20)
        entry_parar.insert(0, self.hotkey_parar)
        entry_parar.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        ttk.Button(keys_frame, text="Detect", width=8,
                command=lambda: self.detectar_hotkey(entry_parar)).grid(row=1, column=2, padx=5, pady=8)
        
        # Hotkey Mouse Capture
        ttk.Label(keys_frame, text="Mouse Capt.:", width=12).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        entry_captura = ttk.Entry(keys_frame, width=20)
        entry_captura.insert(0, self.hotkey_captura_mouse)
        entry_captura.grid(row=2, column=1, padx=5, pady=8, sticky="ew")
        ttk.Button(keys_frame, text="Detect", width=8,
                command=lambda: self.detectar_hotkey(entry_captura)).grid(row=2, column=2, padx=5, pady=8)
        
        # Configurar grid weights para responsividade
        keys_frame.columnconfigure(1, weight=1)
        
        # Frame para botões na parte inferior
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.BOTTOM, pady=(20, 0))
        
        def aplicar():
            self.hotkey_iniciar = entry_iniciar.get().lower()
            self.hotkey_parar = entry_parar.get().lower()
            self.hotkey_captura_mouse = entry_captura.get().lower()
            self.configurar_hotkeys()
            self.salvar_configuracoes_globais()
            dialog.destroy()
            messagebox.showinfo("Success", "Hotkeys updated!")
        
        ttk.Button(buttons_frame, text="Aplicar", command=aplicar).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Default", 
                command=lambda: [
                    entry_iniciar.delete(0, tk.END), entry_iniciar.insert(0, "ctrl+enter"),
                    entry_parar.delete(0, tk.END), entry_parar.insert(0, "esc"),
                    entry_captura.delete(0, tk.END), entry_captura.insert(0, "ctrl+shift+c")
                ]).pack(side=tk.LEFT, padx=5)
        
        # Centralizar diálogo
        dialog.update_idletasks()
        x = (self.janela.winfo_x() + self.janela.winfo_width() // 2 - dialog.winfo_width() // 2)
        y = (self.janela.winfo_y() + self.janela.winfo_height() // 2 - dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

    def criar_frame_controles(self, parent):
        """Frame de controles e status"""
        frame = ttk.LabelFrame(parent, text="🚀 Controls", padding=10)
        frame.pack(fill=tk.X, pady=5, padx=10)
            
        # Botões de controle
        botoes_frame = ttk.Frame(frame)
        botoes_frame.pack(fill=tk.X, pady=5)
        
        self.btn_iniciar = ttk.Button(botoes_frame, text="▶️ START", command=self.iniciar_execucao)
        self.btn_iniciar.pack(side=tk.LEFT, padx=5)
        
        self.btn_parar = ttk.Button(botoes_frame, text="⏹️ STOP", command=self.parar_execucao, state="disabled")
        self.btn_parar.pack(side=tk.LEFT, padx=5)

        ttk.Button(botoes_frame, text="⚙️ Configure Hotkeys", 
          command=self.configurar_hotkeys_dialog).pack(side=tk.LEFT, padx=5)
        
        # Status
        self.label_status = tk.Label(frame, text="Status: Ready", font=("Arial", 10), fg="blue")
        self.label_status.pack(anchor="w", pady=2)
        
        

        # Frame para o log que pode ser redimensionado
        log_container = ttk.Frame(frame)
        log_container.pack(fill=tk.X, pady=2)

        # Text log dentro do container
        self.text_log = tk.Text(log_container, height=4, font=("Arial", 9))
        self.text_log.pack(fill=tk.BOTH, expand=True)

        # Cantinho de redimensionamento no container do log
        def start_resize(event):
            log_container.start_height = self.text_log.cget("height")
            log_container.start_y = event.y_root

        def do_resize(event):
            if hasattr(log_container, 'start_height') and hasattr(log_container, 'start_y'):
                delta = event.y_root - log_container.start_y
                # Cada 10 pixels = 1 linha (ajuste a sensibilidade)
                new_height = max(2, log_container.start_height + delta // 10)
                self.text_log.config(height=new_height)

        def stop_resize(event):
            if hasattr(log_container, 'start_height'):
                delattr(log_container, 'start_height')
            if hasattr(log_container, 'start_y'):
                delattr(log_container, 'start_y')

        # Frame do cantinho (15x15 pixels no canto inferior direito)
        resize_handle = ttk.Frame(log_container, width=15, height=15)
        resize_handle.place(relx=1.0, rely=1.0, anchor="se")  # Posiciona no canto inferior direito
        resize_handle.configure(cursor="sizing")

        resize_handle.bind('<Button-1>', start_resize)
        resize_handle.bind('<B1-Motion>', do_resize)
        resize_handle.bind('<ButtonRelease-1>', stop_resize)

        # Hotkeys info
        info_hotkeys = tk.Label(frame, text=f"Hotkeys: {self.hotkey_iniciar}=Start, {self.hotkey_parar}=Stop, {self.hotkey_captura_mouse}=Mouse Capt.", 
                            font=("Arial", 8), fg="gray")
        info_hotkeys.pack(anchor="w")


        # Hotkeys info
        info_hotkeys = tk.Label(frame, 
                            text=f"Hotkeys: {self.hotkey_iniciar}=Start, {self.hotkey_parar}=Stop, {self.hotkey_captura_mouse}=Mouse Capt.", 
                            font=("Arial", 8), fg="gray")

    def detectar_hotkey(self, entry_widget):
        """Detecta uma hotkey pressionada pelo usuário"""
        dialog = tk.Toplevel(self.janela)
        dialog.title("Detect Hotkey")
        dialog.geometry("400x200")
        dialog.transient(self.janela)
        dialog.grab_set()
        
        tk.Label(dialog, text="Press the desired key combination\n\nClick X when finished", 
                font=("Arial", 10), justify=tk.CENTER).pack(pady=20)
        
        lbl_status = tk.Label(dialog, text="Waiting...", fg="blue")
        lbl_status.pack(pady=10)
        
        teclas_pressionadas = set()
        modificadores_pressionados = set()
        
        def on_key_press(e):
            tecla = e.keysym
            
            # Lista de teclas de modificador
            teclas_modificadoras = {
                'Control_L': 'ctrl', 'Control_R': 'ctrl',
                'Alt_L': 'alt', 'Alt_R': 'alt', 
                'Shift_L': 'shift', 'Shift_R': 'shift'
            }
            
            # Adicionar à lista de teclas pressionadas
            if tecla in teclas_modificadoras:
                modificador = teclas_modificadoras[tecla]
                modificadores_pressionados.add(modificador)
            else:
                teclas_pressionadas.add(tecla)
            
            # Construir a string final
            modificadores_list = list(modificadores_pressionados)
            teclas_list = list(teclas_pressionadas)
            
            if modificadores_list and teclas_list:
                hotkey = "+".join(modificadores_list + teclas_list)
            elif modificadores_list:
                hotkey = "+".join(modificadores_list)
            elif teclas_list:
                hotkey = "+".join(teclas_list)
            else:
                hotkey = ""
            
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, hotkey)
            lbl_status.config(text=f"Detected: {hotkey}")
        
        def on_key_release(e):
            tecla = e.keysym
            teclas_modificadoras = {
                'Control_L': 'ctrl', 'Control_R': 'ctrl',
                'Alt_L': 'alt', 'Alt_R': 'alt', 
                'Shift_L': 'shift', 'Shift_R': 'shift'
            }
            
            if tecla in teclas_modificadoras:
                modificador = teclas_modificadoras[tecla]
                modificadores_pressionados.discard(modificador)
            else:
                teclas_pressionadas.discard(tecla)
        
        def finalizar_deteccao():
            dialog.destroy()
        
        # Vincular eventos
        dialog.bind('<KeyPress>', on_key_press)
        dialog.bind('<KeyRelease>', on_key_release)
        
        # Botão para fechar manualmente — label padronizado
        btn_fechar = ttk.Button(dialog, text="Confirm", command=finalizar_deteccao)
        btn_fechar.pack(pady=10)
        
        dialog.focus_set()
        # Usa lambda para garantir que a função NÃO seja chamada no momento da ligação
        dialog.protocol("WM_DELETE_WINDOW", lambda: finalizar_deteccao())


    def validar_numero(self, valor):
        """Valida se o valor é um número"""
        if valor == "":
            return True
        try:
            float(valor)
            return True
        except ValueError:
            return False
    
    def atualizar_interface_tempo(self, event=None):
        """Atualiza a interface baseada no modo de tempo selecionado"""
        modo = self.combo_modo_tempo.get()
        
        # Esconder todos os frames primeiro
        self.frame_tempo_fixo.pack_forget()
        self.frame_tempo_aleatorio.pack_forget()
        
        # Mostrar o frame correto
        if modo == "steady":
            self.frame_tempo_fixo.pack(fill=tk.X, pady=5)
        elif modo == "random":
            self.frame_tempo_aleatorio.pack(fill=tk.X, pady=5)

        # Atualizar a lista de etapas para refletir a mudança
        self.atualizar_lista_etapas()


    def copiar_etapa(self, index):
        """Cria cópias de uma etapa - VERSÃO CORRIGIDA"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            dialog = tk.Toplevel(self.janela)
            dialog.title("Copy Step")
            dialog.geometry("300x200")
            dialog.resizable(False, False)
            dialog.transient(self.janela)
            dialog.grab_set()
            
            # Centralizar
            dialog.update_idletasks()
            x = (self.janela.winfo_x() + self.janela.winfo_width() // 2 - dialog.winfo_width() // 2)
            y = (self.janela.winfo_y() + self.janela.winfo_height() // 2 - dialog.winfo_height() // 2)
            dialog.geometry(f"+{x}+{y}")
            
            # **CORREÇÃO: Usar grid para layout preciso**
            
            # Label
            label = tk.Label(dialog, text="How many copies?", 
                            font=("Arial", 11))
            label.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
            
            # Input
            ttk.Label(dialog, text="Copies:").grid(row=1, column=0, padx=5, pady=10, sticky="e")
            
            entry_copias = ttk.Entry(dialog, width=10)
            entry_copias.insert(0, "1")
            entry_copias.grid(row=1, column=1, padx=5, pady=10, sticky="w")
            
            def confirmar_copias():
                try:
                    num_copias = int(entry_copias.get())
                    if num_copias > 0:
                        etapa_original = self.macro_atual["etapas"][index].copy()
                        
                        for i in range(num_copias):
                            self.macro_atual["etapas"].insert(index + 1 + i, etapa_original.copy())
                        
                        self.atualizar_lista_etapas()
                        dialog.destroy()
                except ValueError:
                    messagebox.showerror("Error", "Enter a valid number!")
            
            # Botão
            btn_confirmar = ttk.Button(dialog, text="Confirm", command=confirmar_copias)
            btn_confirmar.grid(row=2, column=0, columnspan=2, pady=15)
            
            # Configurar grid weights
            dialog.grid_rowconfigure(0, weight=1)
            dialog.grid_rowconfigure(1, weight=0)
            dialog.grid_rowconfigure(2, weight=1)
            dialog.grid_columnconfigure(0, weight=1)
            dialog.grid_columnconfigure(1, weight=1)
            
            entry_copias.focus_set()
            entry_copias.select_range(0, tk.END)
            entry_copias.bind('<Return>', lambda e: confirmar_copias())


    def adicionar_etapa(self):
        """Adiciona uma nova etapa à lista"""
        etapa = {
            "tipo": "keyboard",  # ← NOVO CAMPO
            "acao": "Click to set key", 
            "tempo": "0.3", 
            "repeticoes": 1,
            "x": 0,  # ← NOVO CAMPO (para mouse)
            "y": 0   # ← NOVO CAMPO (para mouse)
        }
        self.macro_atual["etapas"].append(etapa)
        self.atualizar_lista_etapas()
    
    def atualizar_lista_etapas(self):
        """Atualiza a lista visual de etapas"""
        # Limpar frame existente
        for widget in self.frame_etapas.winfo_children():
            widget.destroy()
        
        # Adicionar cada etapa
        for i, etapa in enumerate(self.macro_atual["etapas"]):
            self.criar_linha_etapa(i, etapa)



















    def configurar_acao_mouse(self, index):

        """Abre seletor de ação de mouse"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            # Criar diálogo de seleção
            dialog = tk.Toplevel(self.janela)
            dialog.title("Select Mouse Action")
            dialog.geometry("300x300")
            dialog.transient(self.janela)
            dialog.grab_set()
            
            tk.Label(dialog, text="Select mouse action:", 
                    font=("Arial", 11)).pack(pady=15)
            
            # Frame para ações
            frame_acoes = ttk.Frame(dialog)
            frame_acoes.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Variável para armazenar seleção
            acao_selecionada = tk.StringVar(value=self.macro_atual["etapas"][index].get("acao", "move"))
            
            # Botões para cada ação
            acoes_info = [
                ("move", "🖱️ Move", "Only moves the cursor"),
                ("left_click", "🖱️ Left Click", "Click with left button"),
                ("right_click", "🖱️ Right Click", "Click with right button"), 
                ("middle_click", "🖱️ Middle Click", "Click with middle button"),
                ("double_left_click", "🖱️ Double Left Click", "Double left click"),
                ("double_right_click", "🖱️ Double Right Click", "Double right click")
            ]
            
            for acao_id, acao_texto, acao_desc in acoes_info:
                frame_acao = ttk.Frame(frame_acoes)
                frame_acao.pack(fill=tk.X, pady=2)
                
                rb = ttk.Radiobutton(frame_acao, text=acao_texto, 
                                variable=acao_selecionada, value=acao_id)
                rb.pack(side=tk.LEFT, anchor="w")
                
                lbl_desc = ttk.Label(frame_acao, text=acao_desc, font=("Arial", 8), foreground="gray")
                lbl_desc.pack(side=tk.LEFT, padx=10)
            
            def aplicar_acao():
                self.macro_atual["etapas"][index]["acao"] = acao_selecionada.get()
                self.atualizar_lista_etapas()
                dialog.destroy()
            
            # Botões de ação — APENAS "Confirm"
            frame_botoes = ttk.Frame(dialog)
            frame_botoes.pack(pady=10)
            
            ttk.Button(frame_botoes, text="Confirm", command=aplicar_acao).pack(side=tk.LEFT, padx=5)
            
            # Evita execução acidental e permite fechar com X
            dialog.protocol("WM_DELETE_WINDOW", lambda: dialog.destroy())














    def atualizar_tipo_etapa(self, index, novo_tipo):
        """Atualiza o tipo de uma etapa de forma escalável"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            etapa = self.macro_atual["etapas"][index]
            tipo_antigo = etapa.get("tipo", "keyboard")
            
            if tipo_antigo != novo_tipo:
                etapa["tipo"] = novo_tipo
                
                # Sistema de reset por tipo (ESCALÁVEL)
                config_por_tipo = {
                    "keyboard": {
                        "acao_padrao": "Click to set key",
                        "resetar_coordenadas": True
                    },
                    "mouse": {
                        "acao_padrao": "move", 
                        "resetar_coordenadas": False
                    }
                }
                
                if novo_tipo in config_por_tipo:
                    config = config_por_tipo[novo_tipo]
                    etapa["acao"] = config["acao_padrao"]
                    
                    if config["resetar_coordenadas"]:
                        etapa["x"] = 0
                        etapa["y"] = 0
            
            self.atualizar_lista_etapas()

    def atualizar_coordenada_x(self, index, x):
        """Atualiza coordenada X de uma etapa mouse"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            try:
                self.macro_atual["etapas"][index]["x"] = int(x)
            except ValueError:
                pass

    def atualizar_coordenada_y(self, index, y):
        """Atualiza coordenada Y de uma etapa mouse"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            try:
                self.macro_atual["etapas"][index]["y"] = int(y)
            except ValueError:
                pass


    def capturar_posicao_mouse(self, index):
        """Abre modo de captura de posição do mouse"""
        # Variável para controlar se a janela ainda está aberta
        janela_aberta = True
        
        # Criar janela de captura
        captura_window = tk.Toplevel(self.janela)
        captura_window.title("Capture Mouse Position")
        captura_window.geometry("400x300")
        captura_window.transient(self.janela)
        captura_window.grab_set()
        
        # Tornar a janela semi-transparente
        captura_window.attributes('-alpha', 0.7)
        
        tk.Label(captura_window, text="Move mouse to desired position\n\nPress hotkey to capture", 
                font=("Arial", 12), justify=tk.CENTER).pack(pady=20)
        
        # Frame para informações em tempo real
        info_frame = ttk.Frame(captura_window)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Coordenadas X,Y
        coords_label = tk.Label(info_frame, text="X: 0, Y: 0", font=("Arial", 14, "bold"), fg="blue")
        coords_label.pack()
        
        # Cor do pixel
        color_label = tk.Label(info_frame, text="Color: #000000", font=("Arial", 10), fg="gray")
        color_label.pack()
        
        # Preview da cor
        color_preview = tk.Label(info_frame, text="   ", bg="#000000", relief="solid", borderwidth=1)
        color_preview.pack(pady=5)
        
        # Hotkey info
        hotkey_label = tk.Label(captura_window, 
                            text=f"Hotkey: {self.hotkey_captura_mouse}", 
                            font=("Arial", 10), fg="green")
        hotkey_label.pack(pady=5)
        
        # Variável para armazenar posição capturada
        posicao_capturada = None
        
        def atualizar_preview():
            # Verificar se a janela ainda está aberta
            if not janela_aberta:
                return
                
            try:
                # Obter posição atual do mouse
                x, y = pyautogui.position()
                
                # Atualizar labels
                coords_label.config(text=f"X: {x}, Y: {y}")
                
                # Obter cor do pixel
                try:
                    screenshot = pyautogui.screenshot().load()
                    r, g, b = screenshot[x, y]
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    color_label.config(text=f"Cor: {hex_color}")
                    color_preview.config(bg=hex_color)
                except Exception:
                    color_label.config(text="Color: N/A")
                
                # Continuar atualizando apenas se a janela estiver aberta
                if janela_aberta:
                    captura_window.after(50, atualizar_preview)
            except Exception:
                # Se ocorrer erro (janela fechada), para o loop
                pass
        
        def capturar_posicao():
            nonlocal posicao_capturada, janela_aberta
            janela_aberta = False  # Para o loop
            posicao_capturada = pyautogui.position()
            
            # Remover hotkey antes de fechar
            try:
                keyboard.remove_hotkey(capturar_posicao)
            except:
                pass
                
            captura_window.destroy()
        
        def cancelar_captura():
            nonlocal janela_aberta
            janela_aberta = False  # Para o loop
            
            # Remover hotkey antes de fechar
            try:
                keyboard.remove_hotkey(capturar_posicao)
            except:
                pass
                
            captura_window.destroy()
        
        def on_closing():
            nonlocal janela_aberta
            janela_aberta = False
            
            # Remover hotkey antes de fechar
            try:
                keyboard.remove_hotkey(capturar_posicao)
            except:
                pass
                
            captura_window.destroy()
        
        def finalizar_captura():
            if posicao_capturada:
                x, y = posicao_capturada
                self.macro_atual["etapas"][index]["x"] = x
                self.macro_atual["etapas"][index]["y"] = y
                self.atualizar_lista_etapas()
        
    # Botão cancelar (pode ser renomeado para "Confirm" se preferir)
        btn_cancelar = ttk.Button(captura_window, text="Cancel", command=cancelar_captura)
        btn_cancelar.pack(pady=10)
        
        # Configurar hotkey para captura
        try:
            keyboard.add_hotkey(self.hotkey_captura_mouse, capturar_posicao)
        except Exception as e:
            print(f"Error configuring capture hotkey: {e}")
        
        # Iniciar preview
        atualizar_preview()
        
        # Configurar destruição da janela — usar lambda para evitar execução imediata
        captura_window.protocol("WM_DELETE_WINDOW", lambda: on_closing())
        captura_window.bind('<Destroy>', lambda e: finalizar_captura())


    def criar_linha_etapa(self, index, etapa):
        """Cria uma linha na lista de etapas"""
        linha = ttk.Frame(self.scrollable_frame)
        linha.pack(fill=tk.X, pady=2)
        
        # Número
        ttk.Label(linha, text=str(index + 1), width=3).pack(side=tk.LEFT, padx=2)

        # Dropdown Tipo (Teclado/Mouse)
        combo_tipo = ttk.Combobox(linha, values=["keyboard", "mouse"], width=6, state="readonly")
        combo_tipo.set(etapa.get("tipo", "keyboard"))
        combo_tipo.pack(side=tk.LEFT, padx=2)
        combo_tipo.bind('<<ComboboxSelected>>', 
                    lambda e, i=index: self.atualizar_tipo_etapa(i, combo_tipo.get()))

        # Ação - Botão que muda conforme o tipo
        tipo_etapa = etapa.get("tipo", "keyboard")
        
        # Texto amigável para ações
        texto_acao = etapa["acao"]
        if texto_acao == "Click to set key":
            pass  # Mantém texto original
        elif tipo_etapa == "mouse":
            textos_amigaveis = {
                "move": "🖱️ Move",
                "left_click": "🖱️ Left Click", 
                "right_click": "🖱️ Right Click",
                "middle_click": "🖱️ Middle Click",
                "double_left_click": "🖱️ Double Left Click",
                "double_right_click": "🖱️ Double Right Click"
            }
            texto_acao = textos_amigaveis.get(etapa["acao"], etapa["acao"])

        # Botão de ação
        if tipo_etapa == "keyboard":
            btn_acao = ttk.Button(linha, text=texto_acao, width=22, 
                                command=lambda i=index: self.configurar_tecla(i))
        else:
            btn_acao = ttk.Button(linha, text=texto_acao, width=22, 
                                command=lambda i=index: self.configurar_acao_mouse(i))
        btn_acao.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)




        # Tempo - mostra conforme o modo
        modo_tempo = self.combo_modo_tempo.get()
        if modo_tempo == "personalized":
            entry_tempo = ttk.Entry(linha, width=8, validate="key")
            entry_tempo.configure(validatecommand=(entry_tempo.register(self.validar_numero), '%P'))
            entry_tempo.insert(0, etapa["tempo"])
            entry_tempo.pack(side=tk.LEFT, padx=2)
            entry_tempo.bind('<FocusOut>', lambda e, i=index: self.atualizar_tempo_etapa(i, entry_tempo.get()))
        else:
            # Texto informativo baseado no modo
            if modo_tempo == "steady":
                texto_tempo = self.entry_tempo_fixo.get()
            else:  # aleatório
                min_t = self.entry_tempo_min.get()
                max_t = self.entry_tempo_max.get()
                texto_tempo = f"{min_t}-{max_t}s"
            
            lbl_tempo = ttk.Label(linha, text=texto_tempo, width=8)
            lbl_tempo.pack(side=tk.LEFT, padx=2)









        # Campos X,Y (só mostra se for mouse)
        if etapa.get("tipo") == "mouse":
            frame_coords = ttk.Frame(linha)
            frame_coords.pack(side=tk.LEFT, padx=1)
            
            # Campo X
            ttk.Label(frame_coords, text="X:").pack(side=tk.LEFT)
            entry_x = ttk.Entry(frame_coords, width=4, validate="key")
            entry_x.configure(validatecommand=(entry_x.register(self.validar_numero), '%P'))
            entry_x.insert(0, str(etapa.get("x", 0)))
            entry_x.pack(side=tk.LEFT, padx=2)
            entry_x.bind('<FocusOut>', lambda e, i=index: self.atualizar_coordenada_x(i, entry_x.get()))
            
            # Campo Y  
            ttk.Label(frame_coords, text="Y:").pack(side=tk.LEFT)
            entry_y = ttk.Entry(frame_coords, width=4, validate="key")
            entry_y.configure(validatecommand=(entry_y.register(self.validar_numero), '%P'))
            entry_y.insert(0, str(etapa.get("y", 0)))
            entry_y.pack(side=tk.LEFT, padx=2)
            entry_y.bind('<FocusOut>', lambda e, i=index: self.atualizar_coordenada_y(i, entry_y.get()))
            
            # Botão Capturar
            btn_capturar = ttk.Button(frame_coords, text="📐", width=3,
                                    command=lambda i=index: self.capturar_posicao_mouse(i))
            btn_capturar.pack(side=tk.LEFT, padx=2)

        # Campo de repetições (só mostra se checkbox estiver ativo)
        if self.var_repetir_acoes.get():
            spin_repeticao = ttk.Spinbox(linha, from_=1, to=100, width=6, validate="key")
            spin_repeticao.configure(validatecommand=(spin_repeticao.register(self.validar_numero), '%P'))
            spin_repeticao.set(etapa.get("repeticoes", 1))
            spin_repeticao.pack(side=tk.LEFT, padx=2)

            # Eventos para capturar mudanças
            spin_repeticao.bind('<<ComboboxSelected>>', 
                            lambda e, i=index: self.atualizar_repeticao_etapa(i, spin_repeticao.get()))
            spin_repeticao.bind('<KeyRelease>', 
                            lambda e, i=index: self.atualizar_repeticao_etapa(i, spin_repeticao.get()))
            spin_repeticao.bind('<FocusOut>', 
                            lambda e, i=index: self.atualizar_repeticao_etapa(i, spin_repeticao.get()))
            
        # Controles
        controles_frame = ttk.Frame(linha, width=15)
        controles_frame.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(controles_frame, text="⎘", width=2,
                command=lambda i=index: self.copiar_etapa(i)).pack(side=tk.LEFT, padx=1)
        ttk.Button(controles_frame, text="▲", width=2, 
                command=lambda i=index: self.mover_etapa(i, -1)).pack(side=tk.LEFT, padx=1)
        ttk.Button(controles_frame, text="▼", width=2,
                command=lambda i=index: self.mover_etapa(i, 1)).pack(side=tk.LEFT, padx=1)
        ttk.Button(controles_frame, text="✏️", width=2,
                command=lambda i=index: self.editar_etapa(i)).pack(side=tk.LEFT, padx=1)
        ttk.Button(controles_frame, text="🗑️", width=2,
                command=lambda i=index: self.remover_etapa(i)).pack(side=tk.LEFT, padx=1)


    def atualizar_repeticao_etapa(self, index, repeticoes):
        """Atualiza as repetições de uma etapa"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            try:
                self.macro_atual["etapas"][index]["repeticoes"] = int(repeticoes)
            except ValueError:
                pass








    def configurar_tecla(self, index):
        """Configura uma tecla através de detecção de pressionamento"""
        self.aguardando_tecla = True
        self.tecla_atual = ""
        
        dialog, main_frame = self.criar_dialogo_padrao("Detect Key", 400, 200)
        
        # Conteúdo clean
        tk.Label(main_frame, text="Press desired key", 
                font=("Arial", 12)).pack(pady=15)
        
        lbl_status = tk.Label(main_frame, text="Waiting...", font=("Arial", 10), fg="blue")
        lbl_status.pack(pady=10)
        
        # Botão clean e discreto
        btn_confirmar = ttk.Button(main_frame, text="Confirm")
        btn_confirmar.pack(pady=15)
        
        teclas_pressionadas = set()
        modificadores_pressionados = set()
        
        def on_key_press(e):
            tecla = e.keysym
            
            teclas_modificadoras = {
                'Control_L': 'Ctrl', 'Control_R': 'Ctrl',
                'Alt_L': 'Alt', 'Alt_R': 'Alt', 
                'Shift_L': 'Shift', 'Shift_R': 'Shift'
            }
            
            if tecla in teclas_modificadoras:
                modificador = teclas_modificadoras[tecla]
                modificadores_pressionados.add(modificador)
            else:
                teclas_pressionadas.add(tecla)
            
            modificadores_list = list(modificadores_pressionados)
            teclas_list = list(teclas_pressionadas)
            
            if modificadores_list and teclas_list:
                tecla_completa = " + ".join(modificadores_list + teclas_list)
            elif modificadores_list:
                tecla_completa = " + ".join(modificadores_list)
            elif teclas_list:
                tecla_completa = " + ".join(teclas_list)
            else:
                tecla_completa = ""
            
            self.tecla_atual = tecla_completa
            lbl_status.config(text=f"Key: {tecla_completa}")
        
        def on_key_release(e):
            tecla = e.keysym
            teclas_modificadoras = {
                'Control_L': 'Ctrl', 'Control_R': 'Ctrl',
                'Alt_L': 'Alt', 'Alt_R': 'Alt', 
                'Shift_L': 'Shift', 'Shift_R': 'Shift'
            }
            
            if tecla in teclas_modificadoras:
                modificador = teclas_modificadoras[tecla]
                modificadores_pressionados.discard(modificador)
            else:
                teclas_pressionadas.discard(tecla)
        
        def finalizar_deteccao():
            dialog.destroy()
            self.aguardando_tecla = False
            if self.tecla_atual and 0 <= index < len(self.macro_atual["etapas"]):
                self.macro_atual["etapas"][index]["acao"] = self.tecla_atual
                self.atualizar_lista_etapas()
        
        # Configurar o botão
        btn_confirmar.config(command=finalizar_deteccao)
        
        # Vincular eventos
        dialog.bind('<KeyPress>', on_key_press)
        dialog.bind('<KeyRelease>', on_key_release)
        
        dialog.focus_set()
        # Proteção: passar lambda evita execução acidental
        dialog.protocol("WM_DELETE_WINDOW", lambda: finalizar_deteccao())


    def finalizar_deteccao_tecla(self, index):
        """Finaliza a detecção de tecla e atualiza a etapa"""
        self.aguardando_tecla = False
        if self.tecla_atual and 0 <= index < len(self.macro_atual["etapas"]):
            self.macro_atual["etapas"][index]["acao"] = self.tecla_atual
            self.atualizar_lista_etapas()
    
    def atualizar_tempo_etapa(self, index, tempo):
        """Atualiza o tempo de uma etapa"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            if self.validar_numero(tempo):
                self.macro_atual["etapas"][index]["tempo"] = tempo
            else:
                messagebox.showerror("Error", "Time must be a number!")
    
    def mover_etapa(self, index, direcao):
        """Move uma etapa para cima ou para baixo"""
        novo_index = index + direcao
        if 0 <= novo_index < len(self.macro_atual["etapas"]):
            # Trocar posições
            self.macro_atual["etapas"][index], self.macro_atual["etapas"][novo_index] = \
                self.macro_atual["etapas"][novo_index], self.macro_atual["etapas"][index]
            self.atualizar_lista_etapas()
    
    

    def editar_etapa(self, index):
        """Abre editor manual para a etapa (fallback)"""
        etapa = self.macro_atual["etapas"][index]
        
        dialog, main_frame = self.criar_dialogo_padrao("Edit Action Manually", 400, 200)
        
        tk.Label(main_frame, text="Enter action manually:", 
                font=("Arial", 11)).pack(pady=15)
        
        entry_acao = ttk.Entry(main_frame, width=30, font=("Arial", 10))
        entry_acao.insert(0, etapa["acao"])
        entry_acao.pack(pady=10)
        entry_acao.select_range(0, tk.END)
        entry_acao.focus_set()
        
        def confirmar_edicao():
            nova_acao = entry_acao.get().strip()
            if nova_acao:
                self.macro_atual["etapas"][index]["acao"] = nova_acao
                self.atualizar_lista_etapas()
                dialog.destroy()
        
        # Botões — APENAS "Confirm"
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.BOTTOM, pady=10)
        
        ttk.Button(buttons_frame, text="Confirm", command=confirmar_edicao).pack(side=tk.LEFT, padx=5)
        
        # Permitir fechar com Enter ou X
        entry_acao.bind('<Return>', lambda e: confirmar_edicao())
        dialog.protocol("WM_DELETE_WINDOW", lambda: dialog.destroy())










    def remover_etapa(self, index):
        """Remove uma etapa"""
        if 0 <= index < len(self.macro_atual["etapas"]):
            self.macro_atual["etapas"].pop(index)
            self.atualizar_lista_etapas()
    
    def atualizar_preview(self):
        """Atualiza o preview do teclado"""
        self.label_preview.config(text="PT/BR Keyboard - Layout detected ✓\nClick on an action box and press the desired keys")
    
    def carregar_arquivo(self):
        """Carrega arquivo de macro"""
        arquivo = filedialog.askopenfilename(
            title="Load Macro",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        if arquivo:
            try:
                with open(arquivo, "r", encoding="utf-8") as f:
                    macro_carregado = json.load(f)
                
                nome = macro_carregado.get("nome", "Imported Macro")
                self.macro_atual = macro_carregado
                self.entry_nome.delete(0, tk.END)
                self.entry_nome.insert(0, nome)
                self.spin_repeticoes.set(self.macro_atual.get("repeticoes", 1))
                self.combo_modo_tempo.set(self.macro_atual.get("modo_tempo", "steady"))
                self.atualizar_lista_etapas()
                self.atualizar_interface_tempo()
                
                messagebox.showinfo("Success", f"Macro '{nome}' carregado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error loading file: {e}")
    
    def carregar_macro_selecionado(self, event=None):
        """Carrega o macro selecionado no combobox"""
        nome = self.combo_macros.get()
        if nome in self.macros:
            self.macro_atual = self.macros[nome].copy()
            self.entry_nome.delete(0, tk.END)
            self.entry_nome.insert(0, nome)
            self.spin_repeticoes.set(self.macro_atual.get("repeticoes", 1))
            self.combo_modo_tempo.set(self.macro_atual.get("modo_tempo", "steady"))
            self.atualizar_lista_etapas()
            self.atualizar_interface_tempo()
            self.var_repetir_acoes.set(self.macro_atual.get("repetir_acoes", False))
            self.atualizar_interface_repeticao()

    def novo_macro(self):
        """Cria um novo macro"""
        self.macro_atual = {"nome": "New Macro", "etapas": [], "repeticoes": 1, "modo_tempo": "steady", "tempo_fixo": "0.3"}
        self.entry_nome.delete(0, tk.END)
        self.entry_nome.insert(0, "New Macro")
        self.spin_repeticoes.set(1)
        self.combo_modo_tempo.set("steady")
        self.atualizar_lista_etapas()
        self.atualizar_interface_tempo()

    def editar_nome_macro(self):
        """Permite editar o nome do macro atual"""
        dialog, main_frame = self.criar_dialogo_padrao("Edit Macro Name", 400, 200)
        
        tk.Label(main_frame, text="New name for the macro:", 
                font=("Arial", 11)).pack(pady=15)
        
        entry_nome = ttk.Entry(main_frame, width=30, font=("Arial", 10))
        entry_nome.insert(0, self.entry_nome.get())
        entry_nome.pack(pady=10)
        entry_nome.select_range(0, tk.END)
        entry_nome.focus_set()
        
        def confirmar_nome():
            novo_nome = entry_nome.get().strip()
            if novo_nome:
                self.entry_nome.delete(0, tk.END)
                self.entry_nome.insert(0, novo_nome)
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Name cannot be empty!")
        
        # Botões — APENAS "Confirm"
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(side=tk.BOTTOM, pady=10)
        
        ttk.Button(buttons_frame, text="Confirm", command=confirmar_nome).pack(side=tk.LEFT, padx=5)
        
        entry_nome.bind('<Return>', lambda e: confirmar_nome())
        dialog.protocol("WM_DELETE_WINDOW", lambda: dialog.destroy())

    
    def excluir_macro(self):
        """Exclui o macro selecionado"""
        nome = self.combo_macros.get()
        if nome in self.macros:
            if messagebox.askyesno("Confirm", f"Delete macro '{nome}'?"):
                del self.macros[nome]
                self.combo_macros['values'] = list(self.macros.keys())
                self.combo_macros.set('')
                self.salvar_macros()
                self.novo_macro()
    
    def salvar_macro_atual(self):
        """Salva o macro atual"""
        nome = self.entry_nome.get().strip()
        if not nome:
            messagebox.showerror("Error", "Enter a name for the macro!")
            return
        
        # Atualizar dados atuais
        self.macro_atual["nome"] = nome
        self.macro_atual["repeticoes"] = int(self.spin_repeticoes.get())
        self.macro_atual["modo_tempo"] = self.combo_modo_tempo.get()
        self.macro_atual["tempo_fixo"] = self.entry_tempo_fixo.get()
        self.macro_atual["repetir_acoes"] = self.var_repetir_acoes.get()

        # Salvar no dicionário
        self.macros[nome] = self.macro_atual.copy()
        
        # Atualizar combobox
        self.combo_macros['values'] = list(self.macros.keys())
        self.combo_macros.set(nome)
        
        self.salvar_macros()
        messagebox.showinfo("Success", f"Macro '{nome}' salvo com sucesso!")
    
    def iniciar_execucao(self):
        """Inicia a execução do macro"""
        if self.executando:
            return
        
        if not self.macro_atual["etapas"]:
            messagebox.showerror("Error", "Add steps before executing!")
            return
        
        self.executando = True
        self.btn_iniciar.config(state="disabled")
        self.btn_parar.config(state="normal")
        self.label_status.config(text="Status: Running...", fg="green")
        
        # Executar em thread separada
        self.thread_execucao = threading.Thread(target=self.executar_macro)
        self.thread_execucao.daemon = True
        self.thread_execucao.start()
    
    def parar_execucao(self):
        """Para a execução do macro"""
        self.executando = False
        self.btn_iniciar.config(state="normal")
        self.btn_parar.config(state="disabled")
        self.label_status.config(text="Status: Stopped", fg="red")
    
    def executar_macro(self):
        """Executa o macro (em thread separada)"""
        try:
            repeticoes = int(self.spin_repeticoes.get())
            modo_tempo = self.combo_modo_tempo.get()
            tempo_fixo = float(self.entry_tempo_fixo.get()) if modo_tempo == "steady" else 0.3
            
            for repeticao in range(repeticoes):
                if not self.executando:
                    break
                
                self.atualizar_log(f"▶️ Repetition {repeticao + 1}/{repeticoes}")
                
                for i, etapa in enumerate(self.macro_atual["etapas"]):
                    if not self.executando:
                        break
                    
                    # Atualizar status
                    tipo_etapa = etapa.get("tipo", "keyboard")
                    if tipo_etapa == "mouse":
                        self.atualizar_log(f"Step {i+1}: 🖱️ {etapa['acao']} em ({etapa.get('x', 0)},{etapa.get('y', 0)})")
                    else:
                        self.atualizar_log(f"Step {i+1}: {etapa['acao']}")

                    # Executar ação com repetições individuais
                    repeticoes_etapa = etapa.get("repeticoes", 1)
                    for rep_etapa in range(repeticoes_etapa):
                        if not self.executando:
                            break
                        self.executar_acao(etapa)  # ← Passa a etapa completa, não só a ação




                        # Pequena pausa entre repetições da mesma etapa (exceto na última)
                        if rep_etapa < repeticoes_etapa - 1:
                            time.sleep(0.1)
                        
                    # Aguardar tempo
                    tempo_espera = self.calcular_tempo_espera(etapa, modo_tempo, tempo_fixo, i)
                    time.sleep(tempo_espera)
                
                if repeticao < repeticoes - 1 and self.executando:
                    time.sleep(0.5)  # Pequena pausa entre repetições
            
            if self.executando:
                self.label_status.config(text="Status: Completed ✓", fg="darkgreen")
                self.atualizar_log("✅ Macro completed!")
        
        except Exception as e:
            self.atualizar_log(f"❌ Error: {str(e)}")
        
        finally:
            self.executando = False
            self.btn_iniciar.config(state="normal")
            self.btn_parar.config(state="disabled")
    
    def executar_acao(self, etapa):
        """Executa uma ação (keyboard ou mouse)"""
        tipo = etapa.get("tipo", "keyboard")
        acao = etapa["acao"]
        
        if tipo == "keyboard":
            self.executar_acao_teclado(acao)
        else:
            self.executar_acao_mouse(acao, etapa.get("x", 0), etapa.get("y", 0))

    def executar_acao_teclado(self, acao):
        """Executa uma ação de teclado"""
        try:
            if " + " in acao:
                # Combinação de teclas
                teclas = [t.strip() for t in acao.split(" + ")]
                for tecla in teclas:
                    keyboard.press(tecla.lower())
                time.sleep(0.1)
                for tecla in reversed(teclas):
                    keyboard.release(tecla.lower())
            else:
                # Tecla simples
                keyboard.press(acao.lower())
                time.sleep(0.1)
                keyboard.release(acao.lower())
        except Exception as e:
            print(f"Error executing keyboard action '{acao}': {e}")

    def executar_acao_mouse(self, acao, x, y):
        """Executa uma ação de mouse"""
        try:
            # Mover para a posição primeiro
            pyautogui.moveTo(x, y, duration=0.1)
            
            # Executar ação específica
            if acao == "move":
                # Apenas mover - já foi feito acima
                pass
            elif acao == "clique_esquerdo":
                pyautogui.click(button='left')
            elif acao == "clique_direito":
                pyautogui.click(button='right')
            elif acao == "clique_meio":
                pyautogui.click(button='middle')
            elif acao == "duplo_clique_esquerdo":
                pyautogui.doubleClick(button='left')
            elif acao == "duplo_clique_direito":
                pyautogui.doubleClick(button='right')
            else:
                print(f"Unknown mouse action: {acao}")
                
        except Exception as e:
            print(f"Error executing mouse action '{acao}' at ({x},{y}): {e}")

    def calcular_tempo_espera(self, etapa, modo_tempo, tempo_fixo, index_etapa):
        """Calcula o tempo de espera baseado no modo selecionado"""
        try:
            if modo_tempo == "steady":
                return tempo_fixo
            elif modo_tempo == "personalized":
                return float(etapa.get("tempo", 0.3))
            elif modo_tempo == "random":
                min_tempo = float(self.entry_tempo_min.get())
                max_tempo = float(self.entry_tempo_max.get())
                return random.uniform(min_tempo, max_tempo)
            else:
                return 0.3
        except:
            return 0.3
    
    def atualizar_log(self, mensagem):
        """Atualiza o log de execução"""
        def atualizar():
            self.text_log.insert(tk.END, mensagem + "\n")
            self.text_log.see(tk.END)
            self.janela.update()
        
        self.janela.after(0, atualizar)
    
    def executar(self):
        """Inicia a aplicação"""
        self.janela.mainloop()

# Executar a aplicação
if __name__ == "__main__":
    app = EditorMacros()
    app.executar()
