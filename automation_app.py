import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel, Frame, Label, Button, Entry, Canvas, Listbox
import configparser
import json
import time
import threading
import os
from PIL import Image, ImageTk, UnidentifiedImageError
import uuid

# We assume the pyk8055 module we built is installed system-wide
try:
    import pyk8055
except ImportError:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("Fatal Error", "The 'pyk8055' module is not installed.")
    exit()

# --- CONFIGURATION ---
APP_TITLE_KEY = 'app_title'
CONFIG_FILE = 'k8055_config.ini'
RULES_FILENAME_TPL = "rules_board_{}.json"
DIRECT_CONFIG_FILENAME_TPL = "direct_control_board_{}.ini"
ICONS_DIR = 'icons'
APP_GEOMETRY_AUTOMATION = "800x700"
APP_GEOMETRY_DIRECT = "700x650"
UI_UPDATE_INTERVAL_MS = 200
ENGINE_LOOP_DELAY_S = 0.05
HARDWARE_POLL_INTERVAL_MS = 3000

# --- MULTI-LANGUAGE SUPPORT ---
LANGUAGES = {
    'en': {
        'app_title': "K8055 Automation Studio", 'menu_config': "Configure", 'language': "Language",
        'restart_required': "Language changed. Please restart.", 'edit_layout': "Edit Output Labels & Icons",
        'direct_mode': "Direct Control", 'automation_mode': "Automation Control (PLC)",
        'select_mode_title': "Select Mode", 'select_mode_prompt': "How would you like to use this application?",
        'active_board': "Active Board:", 'scanning': "(Scanning...)", 'none_selected': "(None)",
        'config_window_title': "Edit Layout", 'output_header': "Output", 'label_header': "Label", 'icon_header': "Icon Type",
        'save': "Save", 'cancel': "Cancel", 'no_icons_found': "(no icons found)", 'icon_picker_title': "Select an Icon",
        'analog_outputs': "Analog Outputs", 'load_rules': "Load Rules File", 'save_rules': "Save Rules", 
        'start_engine': "START ENGINE", 'stop_engine': "STOP ENGINE", 'no_rules_loaded': "No rules loaded.", 
        'live_status': "Live Status", 'terminal_log': "Terminal Log", 'digital_inputs': "Digital Inputs",
        'analog_inputs': "Analog Inputs", 'counters': "Counters", 'error_no_rules': "Please load or create rules before starting the engine.",
        'error_no_board': "No valid board selected.", 'edit_rules': "Edit Rules...", 'error_loading_rules': "Error reading rules file. Please check the file or configure them again.",
        'rule_editor_title': "Rule Editor", 'add_rule': "Add...", 'edit_rule': "Edit...", 'remove_rule': "Remove", 'move_up': "Move Up", 'move_down': "Move Down",
        'rule_edit_window_title': "Edit Rule", 'rule_name': "Rule Name:", 'conditions_logic': "Conditions Logic:",
        'conditions': "Conditions (IF...)", 'actions': "Immediate Actions (THEN...)", 'delayed_actions': "Delayed Actions (THEN AFTER...)",
        'add': "Add", 'remove_selected': "Remove Selected", 'input': "Input", 'state': "State", 'operator': "Operator", 'value': "Value",
        'output': "Output", 'delay_sec': "Delay (sec):", 'confirm_remove': "Confirm Removal", 'confirm_remove_rule': "Are you sure you want to remove the selected rule?",
        'add_condition_title': "Add Condition", 'add_action_title': "Add Action", 'add_delayed_action_title': "Add Delayed Action",
        'type': "Type", 'digital_in': "Digital Input", 'analog_in': "Analog Input", 'digital_out': "Digital Output", 'analog_out': "Analog Output",
        'on': "ON", 'off': "OFF", 'action_type': "Action Type", 'set_state': "Set State", 'blink': "Blink", 'latch_on': "Latch ON",
        'interval_sec': "Interval (s):", 'duration_sec': "Duration (s):"
    },
    'pt': {
        'app_title': "Estúdio de Automação K8055", 'menu_config': "Configurar", 'language': "Idioma",
        'restart_required': "Idioma alterado. Reinicie a aplicação.", 'edit_layout': "Editar Nomes e Ícones",
        'direct_mode': "Controlo Direto", 'automation_mode': "Automação (PLC)",
        'select_mode_title': "Selecionar Modo", 'select_mode_prompt': "Como gostaria de usar esta aplicação?",
        'active_board': "Placa Ativa:", 'scanning': "(A procurar...)", 'none_selected': "(Nenhuma)",
        'config_window_title': "Editar Layout", 'output_header': "Saída", 'label_header': "Nome", 'icon_header': "Ícone",
        'save': "Guardar", 'cancel': "Cancelar", 'no_icons_found': "(nenhum ícone)", 'icon_picker_title': "Selecionar Ícone",
        'analog_outputs': "Saídas Analógicas", 'load_rules': "Carregar Regras", 'save_rules': "Guardar Regras", 
        'start_engine': "Iniciar Automação", 'stop_engine': "Parar Automação", 'no_rules_loaded': "Nenhuma regra.", 
        'live_status': "Estado Atual", 'terminal_log': "Registo", 'digital_inputs': "Entradas Digitais",
        'analog_inputs': "Entradas Analógicas", 'counters': "Contadores", 'error_no_rules': "Por favor, carregue ou crie regras antes de iniciar o motor.",
        'error_no_board': "Nenhuma placa selecionada.", 'edit_rules': "Editar Regras...", 'error_loading_rules': "Erro ao ler o ficheiro de regras. Verifique o ficheiro ou configure as regras novamente.",
        'rule_editor_title': "Editor de Regras", 'add_rule': "Adicionar...", 'edit_rule': "Editar...", 'remove_rule': "Remover", 'move_up': "Mover Cima", 'move_down': "Mover Baixo",
        'rule_edit_window_title': "Editar Regra", 'rule_name': "Nome da Regra:", 'conditions_logic': "Lógica das Condições:",
        'conditions': "Condições (SE...)", 'actions': "Ações Imediatas (ENTÃO...)", 'delayed_actions': "Ações Atrasadas (ENTÃO APÓS...)",
        'add': "Adicionar", 'remove_selected': "Remover Selecionado", 'input': "Entrada", 'state': "Estado", 'operator': "Operador", 'value': "Valor",
        'output': "Saída", 'delay_sec': "Atraso (seg):", 'confirm_remove': "Confirmar Remoção", 'confirm_remove_rule': "Tem a certeza que quer remover a regra selecionada?",
        'add_condition_title': "Adicionar Condição", 'add_action_title': "Adicionar Ação", 'add_delayed_action_title': "Adicionar Ação Atrasada",
        'type': "Tipo", 'digital_in': "Entrada Digital", 'analog_in': "Entrada Analógica", 'digital_out': "Saída Digital", 'analog_out': "Saída Analógica",
        'on': "LIGADO", 'off': "DESLIGADO", 'action_type': "Tipo de Ação", 'set_state': "Definir Estado", 'blink': "Piscar", 'latch_on': "Ligar Permanente",
        'interval_sec': "Intervalo (s):", 'duration_sec': "Duração (s):"
    },
}

class LanguageManager:
    def __init__(self, language_code='en'): self.lang_code = language_code if language_code in LANGUAGES else 'en'
    def get_string(self, key): return LANGUAGES[self.lang_code].get(key, LANGUAGES['en'].get(key, f"<{key}>"))

# =============================================================================
# (Backend Logic and GUI Application classes follow)
# ... (The rest of the script remains the same as the last "final" version) ...
# =============================================================================

class K8055Controller:
    def __init__(self, log_callback): self.log, self.boards = log_callback, {}
    def scan_for_boards(self):
        if not pyk8055: self.log("ERROR: pyk8055 module not found."); return
        self.log("Scanning for K8055 boards..."); found_mask = pyk8055.SearchDevices()
        for i in range(4):
            if (found_mask >> i) & 1 and i not in self.boards:
                try:
                    board = pyk8055.k8055(i); board.ClearAllDigital(); board.ClearAllAnalog()
                    self.boards[i] = board; self.log(f"SUCCESS: Connected to board {i}. Outputs reset.")
                except IOError as e: self.log(f"ERROR: Found board at address {i}, but could not open: {e}")
        for board_id in list(self.boards.keys()):
            if not ((found_mask >> board_id) & 1):
                self.log(f"WARNING: Board {board_id} disconnected."); del self.boards[board_id]
    def get_board(self, board_id): return self.boards.get(board_id)
    def get_connected_board_ids(self): return sorted(self.boards.keys())
    def read_all_inputs(self, board_id):
        board = self.get_board(board_id);
        if not board: return None
        try:
            values = board.ReadAllValues()
            return {"digital": values[1], "analog1": values[2], "analog2": values[3], "counter1": values[4], "counter2": values[5]}
        except Exception: return None

class AutomationEngine(threading.Thread):
    def __init__(self, controller, board_id, rules, log_callback):
        super().__init__(daemon=True); self.controller, self.board_id, self.log = controller, board_id, log_callback
        self.rules = [dict(r, **{'id': i}) for i, r in enumerate(rules)]
        self._is_running = threading.Event(); self.active_timers = {}; self.blinking_outputs = {}
        self.triggered_rules = set(); self.latched_outputs = 0
        self.last_output_state = {"digital_out": 0, "analog_out1": 0, "analog_out2": 0}
    def stop(self): self._is_running.clear()
    def run(self):
        self.log(f"INFO [Board {self.board_id}]: Automation Engine STARTED."); self._is_running.set();
        while self._is_running.is_set():
            board = self.controller.get_board(self.board_id)
            if not board: self.log("CRITICAL: Connection to board lost. Shutting down engine."); self.stop(); continue
            physical_inputs = self.controller.read_all_inputs(self.board_id); now = time.time()
            if physical_inputs is None: self.log(f"CRITICAL: Read failed for board {self.board_id}. Shutting down engine."); self.stop(); continue
            full_state = {**physical_inputs, **self.last_output_state}
            desired_digital_outputs = self.latched_outputs; desired_analog1 = self.last_output_state['analog_out1']; desired_analog2 = self.last_output_state['analog_out2']
            desired_digital_outputs = self._manage_blinkers(now, desired_digital_outputs)
            desired_digital_outputs, desired_analog1, desired_analog2 = self._manage_timers(now, desired_digital_outputs, desired_analog1, desired_analog2)
            currently_true_rules = set()
            for rule in self.rules:
                if not rule.get("enabled", True): continue
                if self._evaluate_conditions(rule, full_state):
                    currently_true_rules.add(rule['id'])
                    desired_digital_outputs, desired_analog1, desired_analog2 = self._apply_actions(rule, desired_digital_outputs, desired_analog1, desired_analog2)
                    if rule['id'] not in self.triggered_rules:
                        self.log(f"RULE TRIGGERED (Rising Edge): '{rule['name']}'"); self._fire_one_shot_actions(rule, now)
            self.triggered_rules = currently_true_rules
            board.WriteAllDigital(desired_digital_outputs)
            if desired_analog1 != self.last_output_state['analog_out1'] or desired_analog2 != self.last_output_state['analog_out2']:
                board.OutputAllAnalog(desired_analog1, desired_analog2)
            self.last_output_state = {"digital_out": desired_digital_outputs, "analog_out1": desired_analog1, "analog_out2": desired_analog2}
            time.sleep(ENGINE_LOOP_DELAY_S)
        board = self.controller.get_board(self.board_id)
        if board: board.ClearAllDigital(); board.ClearAllAnalog()
        self.log(f"INFO [Board {self.board_id}]: Automation Engine STOPPED.")
    def _manage_blinkers(self, now, current_output_state):
        for output, blinker in list(self.blinking_outputs.items()):
            if now >= blinker['end_time']: del self.blinking_outputs[output]; continue
            if now >= blinker['next_toggle']:
                blinker['current_state'] = 1 - blinker['current_state']; blinker['next_toggle'] = now + blinker['interval']
            if blinker['current_state'] == 1: current_output_state |= (1 << (output - 1))
        return current_output_state
    def _manage_timers(self, now, d_out, a1_out, a2_out):
        for timer_id, (end_time, actions) in list(self.active_timers.items()):
            if now >= end_time:
                self.log(f"TIMER FINISHED: Executing delayed actions."); d_out, a1_out, a2_out = self._apply_actions({"actions": actions}, d_out, a1_out, a2_out)
                del self.active_timers[timer_id]
        return d_out, a1_out, a2_out
    def _evaluate_conditions(self, rule, state):
        results = []
        for cond in rule.get("conditions", []):
            cond_type = cond.get("type", "")
            if cond_type == "digital_in": results.append(((state["digital"] >> (cond["port"] - 1)) & 1) == cond["state"])
            elif cond_type == "analog_in":
                val, op = state[f"analog{cond['port']}"], cond["operator"]
                if op == ">": results.append(val > cond["value"])
                elif op == "<": results.append(val < cond["value"])
                elif op == "==": results.append(val == cond["value"])
            elif cond_type == "digital_out": results.append(((state["digital_out"] >> (cond["port"] - 1)) & 1) == cond["state"])
        if not results: return False
        return any(results) if rule.get("conditions_logic", "AND").upper() == "OR" else all(results)
    def _fire_one_shot_actions(self, rule, now):
        for action in rule.get("actions", []):
            if action.get("action_type") == "blink":
                self.log(f"BLINK STARTED: Output {action['output']} for {action['duration']}s.")
                self.blinking_outputs[action['output']] = { "end_time": time.time() + action['duration'], "interval": action['interval'], "next_toggle": time.time(), "current_state": 0 }
        for d_action in rule.get("delayed_actions", []):
            timer_id = str(uuid.uuid4()); self.active_timers[timer_id] = (now + d_action['delay'], d_action['actions'])
            self.log(f"TIMER STARTED: Delay of {d_action['delay']}s.")
    def _apply_actions(self, rule_part, d_out, a1_out, a2_out):
        for action in rule_part.get("actions", []):
            action_type = action.get("type", ""); mode = action.get("action_type", "set_state")
            if action_type == "digital_out":
                bit = 1 << (action["output"] - 1)
                if mode == "set_state":
                    if action["state"] == 1: d_out |= bit
                    else: d_out &= ~bit; self.latched_outputs &= ~bit
                elif mode == "latch_on": self.latched_outputs |= bit
            elif action_type == "analog_out":
                if action["output"] == 1: a1_out = action["value"]
                else: a2_out = action["value"]
        return d_out, a1_out, a2_out

# =============================================================================
# GUI APPLICATION
# =============================================================================
class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__(); self.protocol("WM_DELETE_WINDOW", self._on_closing); self.icon_cache = {}
        self.app_config = configparser.ConfigParser(); self.app_config.read(CONFIG_FILE)
        self.lang = LanguageManager(self.app_config.get('General', 'language', fallback='en'))
        
        self.automation_engine = None; self._log_queue = []
        self.controller = K8055Controller(self.log)
        
        # --- THIS IS THE FIX ---
        self.active_board_id = tk.StringVar(self)
        self.direct_control_config = self._load_direct_control_config()
        self.rules = self._load_rules_for_board()
        self.current_digital_outputs = 0
        
        self.app_mode = self._ask_for_mode()
        if not self.app_mode: self.destroy(); return
        
        self.title(self.lang.get_string(APP_TITLE_KEY)); self.geometry(APP_GEOMETRY_DIRECT if self.app_mode == "Direct" else APP_GEOMETRY_AUTOMATION)
        
        self.active_board_id.trace_add('write', self.on_board_change)
        
        self._create_menu(); self._create_widgets()
        self.controller.scan_for_boards(); self._populate_board_selector()
        
        self.update_live_status(); self.after(HARDWARE_POLL_INTERVAL_MS, self.hardware_poll)

    def on_board_change(self, *args):
        self.current_digital_outputs = 0
        if self.automation_engine and self.automation_engine.is_alive():
            self._stop_engine(); messagebox.showinfo("Engine Stopped", "Automation engine was stopped due to board change.")
        
        if self.app_mode == "Direct":
            self.direct_control_config = self._load_direct_control_config()
            self._update_direct_control_view()
        elif self.app_mode == "Automation":
            self.rules = self._load_rules_for_board()
            if hasattr(self, 'rules_label'):
                self._update_rules_display()

    def hardware_poll(self):
        known_ids = set()
        if hasattr(self, 'board_selector') and self.board_selector.winfo_exists():
            try:
                for i in range(self.board_selector["menu"].index("end") + 1):
                    label = self.board_selector["menu"].entrycget(i, "label")
                    if label.isdigit(): known_ids.add(int(label))
            except (AttributeError, tk.TclError): pass
        current_ids = set(self.controller.get_connected_board_ids())
        if current_ids != known_ids:
            self.log("Hardware change detected. Rescanning..."); self.controller.scan_for_boards(); self._populate_board_selector()
        self.after(HARDWARE_POLL_INTERVAL_MS, self.hardware_poll)

    def _open_config_window(self): ConfigWindow(self, self.lang, self.direct_control_config, self._on_config_save)
    def _on_config_save(self, new_config):
        self.direct_control_config = new_config; board_id = self.active_board_id.get()
        if board_id.isdigit():
            path = DIRECT_CONFIG_FILENAME_TPL.format(board_id)
            config = configparser.ConfigParser(); config['DirectControl'] = {k: json.dumps(v) for k, v in new_config.items()}
            with open(path, 'w') as f: config.write(f)
            self.log(f"Direct Control config for board {board_id} saved."); self._update_direct_control_view()

    def _load_direct_control_config(self):
        board_id = self.active_board_id.get()
        if not board_id.isdigit(): return {str(i): {"label": f"Output {i}", "icon": "bulb"} for i in range(1, 9)}
        path = DIRECT_CONFIG_FILENAME_TPL.format(board_id)
        config = configparser.ConfigParser(); config.read(path)
        if config.has_section('DirectControl'): return {k: json.loads(config.get('DirectControl', k)) for k in config.options('DirectControl')}
        return {str(i): {"label": f"Output {i}", "icon": "bulb"} for i in range(1, 9)}

    def _get_icon(self, name, size):
        if (name, size) in self.icon_cache: return self.icon_cache[(name, size)]
        try:
            path = os.path.join(ICONS_DIR, name)
            with Image.open(path) as img:
                photo = ImageTk.PhotoImage(img.resize(size, Image.Resampling.LANCZOS)); self.icon_cache[(name, size)] = photo; return photo
        except Exception: self.log(f"ERROR: Could not find icon: {name}"); return None

    def _create_menu(self):
        self.menu_bar = tk.Menu(self); self.config(menu=self.menu_bar); config_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label=self.lang.get_string('menu_config'), menu=config_menu)
        if self.app_mode == "Direct": config_menu.add_command(label=self.lang.get_string('edit_layout'), command=self._open_config_window)
        lang_menu = tk.Menu(config_menu, tearoff=0); config_menu.add_cascade(label=self.lang.get_string('language'), menu=lang_menu)
        for code, name in [('en', "English"), ('pt', "Português")]: lang_menu.add_command(label=name, command=lambda c=code: self.change_language(c))

    def change_language(self, lang_code):
        config = configparser.ConfigParser(); config.read(CONFIG_FILE)
        if not config.has_section('General'): config.add_section('General')
        config.set('General', 'language', lang_code)
        with open(CONFIG_FILE, 'w') as f: config.write(f)
        messagebox.showinfo(self.lang.get_string('language'), self.lang.get_string('restart_required')); self.destroy()

    def _ask_for_mode(self):
        dialog = Toplevel(self); dialog.title(self.lang.get_string('select_mode_title')); dialog.transient(self); dialog.grab_set()
        Label(dialog, text=self.lang.get_string('select_mode_prompt'), pady=10).pack()
        mode = tk.StringVar()
        def set_mode(m): mode.set(m); dialog.destroy()
        ttk.Button(dialog, text=self.lang.get_string('direct_mode'), command=lambda: set_mode("Direct")).pack(pady=5, padx=20, fill='x')
        ttk.Button(dialog, text=self.lang.get_string('automation_mode'), command=lambda: set_mode("Automation")).pack(pady=5, padx=20, fill='x')
        self.wait_window(dialog); return mode.get()

    def _create_widgets(self):
        if self.app_mode == "Direct": self._create_direct_control_ui()
        else: self._create_automation_ui()

    def _create_direct_control_ui(self):
        for widget in self.winfo_children():
            if widget is not self.menu_bar: widget.destroy()
        main_frame = ttk.Frame(self); main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        top_bar = ttk.Frame(main_frame); top_bar.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(top_bar, text=self.lang.get_string('active_board')).pack(side=tk.LEFT, padx=(0, 5))
        self.board_selector = ttk.OptionMenu(top_bar, self.active_board_id, self.lang.get_string('scanning'))
        self.board_selector.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.grid_frame = ttk.Frame(main_frame); self.grid_frame.pack(fill=tk.BOTH, expand=True)
        self.grid_frame.rowconfigure(0, weight=2); self.grid_frame.rowconfigure(1, weight=1); self.grid_frame.columnconfigure(0, weight=3)
        for i in range(1, 4): self.grid_frame.columnconfigure(i, weight=1)
        self.digital_buttons = {}
        placements = {1: (0,0), 2: (0,1), 3: (0,2), 4: (0,3), 5: (1,0), 6: (1,1), 7: (1,2), 8: (1,3)}
        for output_id, (row, col) in placements.items():
            btn = ttk.Button(self.grid_frame, compound=tk.TOP, command=lambda ch=output_id: self._on_digital_toggle(ch))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.digital_buttons[output_id] = btn
        analog_frame = ttk.LabelFrame(main_frame, text=self.lang.get_string('analog_outputs')); analog_frame.pack(fill=tk.X, pady=10)
        self.analog_output_vars = [tk.IntVar(value=0) for _ in range(2)]
        for i in range(2):
            ttk.Label(analog_frame, text=f"A{i+1}:").pack(side=tk.LEFT, padx=(10, 5))
            scale = ttk.Scale(analog_frame, from_=0, to=255, orient=tk.HORIZONTAL, variable=self.analog_output_vars[i], command=lambda val, ch=i+1: self._on_analog_slide(ch, int(float(val))))
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.grid_frame.bind('<Configure>', self._update_direct_control_view)

    def _update_direct_control_view(self, event=None):
        if self.app_mode != "Direct" or not hasattr(self, 'grid_frame') or not self.grid_frame.winfo_exists(): return
        cell_width = self.grid_frame.winfo_width() / 4; icon_side = int(min(cell_width, self.grid_frame.winfo_height() / 2) * 0.5)
        if icon_side < 16: icon_side = 16
        new_size = (icon_side, icon_side)
        for output_id, btn in self.digital_buttons.items():
            cfg = self.direct_control_config.get(str(output_id), {"label": f"Output {output_id}", "icon": "bulb"})
            is_on = (self.current_digital_outputs >> (output_id - 1)) & 1
            icon_name = f"{cfg['icon']}_{'on' if is_on else 'off'}.png"; btn.config(text=cfg['label'], image=self._get_icon(icon_name, new_size))

    def _create_automation_ui(self):
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL); paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        top_frame = ttk.Frame(paned); paned.add(top_frame, weight=0); top_bar = ttk.Frame(top_frame); top_bar.pack(fill=tk.X)
        ttk.Label(top_bar, text=self.lang.get_string('active_board')).pack(side=tk.LEFT)
        self.board_selector = ttk.OptionMenu(top_bar, self.active_board_id, self.lang.get_string('scanning'))
        self.board_selector.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.status_frame = ttk.LabelFrame(top_frame, text=self.lang.get_string('live_status')); self.status_frame.pack(fill=tk.X, expand=True, pady=10)
        self._create_status_panel(self.status_frame)
        content_frame = ttk.Frame(paned); paned.add(content_frame, weight=1); self._create_automation_controls(content_frame)
        log_frame = ttk.LabelFrame(paned, text=self.lang.get_string('terminal_log')); paned.add(log_frame, weight=1); self._create_log_terminal(log_frame)
        self._update_rules_display()

    def _populate_board_selector(self):
        menu = self.board_selector["menu"]; menu.delete(0, "end")
        board_ids = self.controller.get_connected_board_ids()
        if board_ids:
            for board_id in board_ids: menu.add_command(label=str(board_id), command=lambda v=str(board_id): self.active_board_id.set(v))
            if not self.active_board_id.get() in [str(i) for i in board_ids]: self.active_board_id.set(str(board_ids[0]))
        else: self.active_board_id.set(self.lang.get_string('none_selected')); menu.add_command(label=self.lang.get_string('none_selected'))

    def _create_status_panel(self, parent):
        self.digital_input_vars=[tk.StringVar(value="-") for _ in range(5)]; self.analog_vars=[tk.StringVar(value="---") for _ in range(2)]; self.counter_vars=[tk.StringVar(value="---") for _ in range(2)]
        ttk.Label(parent, text=self.lang.get_string('digital_inputs')).grid(row=0, column=0, sticky="w", padx=5)
        for i in range(5): ttk.Label(parent, text=f"I{i+1}:").grid(row=0, column=i*2+1, padx=(10,2)); ttk.Label(parent, textvariable=self.digital_input_vars[i], width=3).grid(row=0, column=i*2+2)
        ttk.Label(parent, text=self.lang.get_string('analog_inputs')).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(parent, text="A1:").grid(row=1, column=1, padx=(10,2)); ttk.Label(parent, textvariable=self.analog_vars[0], width=4).grid(row=1, column=2)
        ttk.Label(parent, text="A2:").grid(row=1, column=3, padx=(10,2)); ttk.Label(parent, textvariable=self.analog_vars[1], width=4).grid(row=1, column=4)
        ttk.Label(parent, text=self.lang.get_string('counters')).grid(row=2, column=0, sticky="w", padx=5)
        ttk.Label(parent, text="C1:").grid(row=2, column=1, padx=(10,2)); ttk.Label(parent, textvariable=self.counter_vars[0], width=4).grid(row=2, column=2)
        ttk.Label(parent, text="C2:").grid(row=2, column=3, padx=(10,2)); ttk.Label(parent, textvariable=self.counter_vars[1], width=4).grid(row=2, column=4)

    def _create_automation_controls(self, parent):
        btn_frame = ttk.Frame(parent); btn_frame.pack(pady=10)
        self.load_rules_button = ttk.Button(btn_frame, text=self.lang.get_string('load_rules'), command=self._load_rules); self.load_rules_button.pack(side=tk.LEFT, padx=5)
        self.edit_rules_button = ttk.Button(btn_frame, text=self.lang.get_string('edit_rules'), command=self._open_rule_editor); self.edit_rules_button.pack(side=tk.LEFT, padx=5)
        self.start_button = ttk.Button(btn_frame, text=self.lang.get_string('start_engine'), command=self._start_engine); self.start_button.pack(side=tk.LEFT, padx=20)
        self.stop_button = ttk.Button(btn_frame, text=self.lang.get_string('stop_engine'), command=self._stop_engine, state=tk.DISABLED); self.stop_button.pack(side=tk.LEFT, padx=5)
        self.rules_label = ttk.Label(parent, text=self.lang.get_string('no_rules_loaded'), justify=tk.LEFT); self.rules_label.pack(pady=10, padx=10, fill="x")

    def _update_rules_display(self):
        if not self.rules: self.rules_label.config(text=self.lang.get_string('no_rules_loaded'))
        else: self.rules_label.config(text="Rules:\n" + "\n".join([f"- {r['name']}" for r in self.rules]))

    def _open_rule_editor(self): RuleEditorWindow(self, self.lang, self.rules, self._on_rules_saved)
    def _on_rules_saved(self, new_rules):
        self.rules = new_rules; self._update_rules_display(); self.log(f"{len(self.rules)} rules updated in memory.")
        board_id = self.active_board_id.get();
        if not board_id.isdigit(): return
        path = RULES_FILENAME_TPL.format(board_id)
        self._save_rules_to_file(path)

    def _create_log_terminal(self, parent):
        self.log_text = tk.Text(parent, height=10, state=tk.DISABLED, wrap=tk.WORD, font=("Courier", 9))
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.log_text.yview); self.log_text.config(yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        for msg in self._log_queue: self.log(msg, False); self._log_queue.clear()

    def log(self, message, process_queue=True):
        if hasattr(self, 'log_text') and self.log_text.winfo_exists():
            if process_queue and self._log_queue:
                for msg in self._log_queue: self.log(msg, False)
                self._log_queue.clear()
            self.log_text.config(state=tk.NORMAL); self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n"); self.log_text.see(tk.END); self.log_text.config(state=tk.DISABLED)
        else: self._log_queue.append(message); print(f"LOG (queued): {message}")

    def update_live_status(self):
        board_id_str = self.active_board_id.get()
        if self.app_mode == "Automation" and board_id_str.isdigit():
            inputs = self.controller.read_all_inputs(int(board_id_str))
            if inputs:
                for i in range(5): self.digital_input_vars[i].set(str((inputs["digital"] >> i) & 1))
                self.analog_vars[0].set(str(inputs["analog1"])); self.analog_vars[1].set(str(inputs["analog2"]))
                self.counter_vars[0].set(str(inputs["counter1"])); self.counter_vars[1].set(str(inputs["counter2"]))
            else:
                if self.automation_engine and self.automation_engine.is_alive(): self._stop_engine()
                for i in range(5): self.digital_input_vars[i].set("-")
                for i in range(2): self.analog_vars[i].set("---"); self.counter_vars[i].set("---")
        elif self.app_mode == "Direct":
            self._update_direct_control_view()
        self.after(UI_UPDATE_INTERVAL_MS, self.update_live_status)

    def _on_digital_toggle(self, channel):
        board_id_str = self.active_board_id.get()
        if not board_id_str or not board_id_str.isdigit(): return
        board = self.controller.get_board(int(board_id_str))
        if not board: return
        is_on = (self.current_digital_outputs >> (channel - 1)) & 1
        if is_on:
            board.ClearDigitalChannel(channel); self.current_digital_outputs &= ~(1 << (channel - 1))
            self.log(f"MANUAL [Board {board_id_str}]: Set Output {channel} OFF.")
        else:
            board.SetDigitalChannel(channel); self.current_digital_outputs |= (1 << (channel - 1))
            self.log(f"MANUAL [Board {board_id_str}]: Set Output {channel} ON.")
        self._update_direct_control_view()

    def _on_analog_slide(self, channel, value):
        board_id_str = self.active_board_id.get()
        if not board_id_str or not board_id_str.isdigit(): return
        board = self.controller.get_board(int(board_id_str))
        if not board: return
        board.OutputAnalogChannel(channel, value); self.log(f"MANUAL [Board {board_id_str}]: Set Analog Output {channel} to {value}.")

    def _load_rules_for_board(self):
        board_id = self.active_board_id.get()
        if not board_id.isdigit(): return []
        path = RULES_FILENAME_TPL.format(board_id)
        try:
            with open(path, 'r') as f: rules = json.load(f)
            if not isinstance(rules, list): raise json.JSONDecodeError("Not a list", "", 0)
            self.log(f"Loaded {len(rules)} rules for board {board_id}."); return rules
        except (FileNotFoundError, json.JSONDecodeError): return []

    def _load_rules(self):
        board_id = self.active_board_id.get()
        if not board_id.isdigit(): messagebox.showerror("Error", self.lang.get_string('error_no_board')); return
        default_path = RULES_FILENAME_TPL.format(board_id)
        fp = filedialog.askopenfilename(title="Open Rules File", filetypes=[("JSON", "*.json")], initialfile=default_path)
        if not fp: return
        try:
            with open(fp, 'r') as f: self.rules = json.load(f)
            if not isinstance(self.rules, list): raise json.JSONDecodeError("Not a list", "", 0)
            self.log(f"Loaded {len(self.rules)} rules from {fp}"); self._update_rules_display()
        except Exception as e: messagebox.showerror("Error", f"{self.lang.get_string('error_loading_rules')}\n\n{e}"); self.log(f"ERROR: {e}")

    def _save_rules_to_file(self, fp):
        try:
            with open(fp, 'w') as f: json.dump(self.rules, f, indent=4)
            self.log(f"Saved {len(self.rules)} rules to {fp}")
        except Exception as e: messagebox.showerror("Error", f"Failed to save rules.\n{e}"); self.log(f"ERROR: {e}")

    def _start_engine(self):
        if not self.rules: messagebox.showwarning("Warning", self.lang.get_string('error_no_rules')); return
        try: board_id = int(self.active_board_id.get())
        except (tk.TclError, ValueError): messagebox.showerror("Error", self.lang.get_string('error_no_board')); return
        if self.automation_engine and self.automation_engine.is_alive(): self._stop_engine()
        self.automation_engine=AutomationEngine(self.controller, board_id, self.rules, self.log); self.automation_engine.start()
        self.start_button.config(state=tk.DISABLED); self.stop_button.config(state=tk.NORMAL)
        self.board_selector.config(state=tk.DISABLED); self.edit_rules_button.config(state=tk.DISABLED); self.load_rules_button.config(state=tk.DISABLED)

    def _stop_engine(self):
        if self.automation_engine and self.automation_engine.is_alive(): self.automation_engine.stop()
        self.start_button.config(state=tk.NORMAL); self.stop_button.config(state=tk.DISABLED)
        self.board_selector.config(state=tk.NORMAL); self.edit_rules_button.config(state=tk.NORMAL); self.load_rules_button.config(state=tk.NORMAL)

    def _on_closing(self):
        if self.automation_engine and self.automation_engine.is_alive():
            self.automation_engine.stop(); self.automation_engine.join()
        for _, board in self.controller.boards.items(): board.CloseDevice()
        self.destroy()

# --- All other GUI classes (RuleEditor, ItemEditDialog, ConfigWindow) are unchanged ---
# ... (The full code for these classes is included below for completeness) ...
class RuleEditorWindow(Toplevel):
    def __init__(self, parent, lang, current_rules, save_callback):
        super().__init__(parent); self.title(lang.get_string('rule_editor_title')); self.transient(parent); self.grab_set()
        self.lang, self.rules, self.save_callback, self.parent_app = lang, [dict(r) for r in current_rules], save_callback, parent
        main_frame = Frame(self); main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.rule_listbox = Listbox(main_frame, height=10); self.rule_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True); self.populate_rule_list()
        btn_frame = Frame(main_frame); btn_frame.pack(side=tk.LEFT, padx=(10,0))
        Button(btn_frame, text=lang.get_string('add_rule'), command=self.add_rule).pack(fill=tk.X)
        Button(btn_frame, text=lang.get_string('edit_rule'), command=self.edit_rule).pack(fill=tk.X, pady=5)
        Button(btn_frame, text=lang.get_string('remove_rule'), command=self.remove_rule).pack(fill=tk.X)
        Button(btn_frame, text=lang.get_string('move_up'), command=lambda: self.move_rule(-1)).pack(fill=tk.X, pady=15)
        Button(btn_frame, text=lang.get_string('move_down'), command=lambda: self.move_rule(1)).pack(fill=tk.X)
        save_cancel_frame = Frame(self); save_cancel_frame.pack(pady=5)
        Button(save_cancel_frame, text=lang.get_string('save'), command=self.save).pack(side=tk.LEFT, padx=5)
        Button(save_cancel_frame, text=lang.get_string('cancel'), command=self.destroy).pack(side=tk.LEFT, padx=5)
    def populate_rule_list(self):
        self.rule_listbox.delete(0, tk.END)
        for rule in self.rules: self.rule_listbox.insert(tk.END, rule.get('name', 'Unnamed'))
    def add_rule(self):
        dialog = RuleEditDialog(self, self.lang); self.wait_window(dialog)
        if dialog.result_rule: self.rules.append(dialog.result_rule); self.populate_rule_list()
    def edit_rule(self):
        sel = self.rule_listbox.curselection();
        if not sel: return
        dialog = RuleEditDialog(self, self.lang, rule=self.rules[sel[0]]); self.wait_window(dialog)
        if dialog.result_rule: self.rules[sel[0]] = dialog.result_rule; self.populate_rule_list()
    def remove_rule(self):
        sel = self.rule_listbox.curselection()
        if not sel: return
        if messagebox.askyesno(self.lang.get_string('confirm_remove'), self.lang.get_string('confirm_remove_rule'), parent=self):
            self.rules.pop(sel[0]); self.populate_rule_list()
    def move_rule(self, direction):
        sel = self.rule_listbox.curselection()
        if not sel: return
        idx = sel[0]; new_idx = idx + direction
        if 0 <= new_idx < len(self.rules):
            self.rules.insert(new_idx, self.rules.pop(idx)); self.populate_rule_list(); self.rule_listbox.selection_set(new_idx)
    def save(self): self.save_callback(self.rules)

class RuleEditDialog(Toplevel):
    def __init__(self, parent, lang, rule=None):
        super().__init__(parent); self.title(lang.get_string('rule_edit_window_title')); self.transient(parent); self.grab_set()
        self.lang = lang; self.result_rule = None; self.rule_data = json.loads(json.dumps(rule)) if rule else {}
        main = ttk.Frame(self, padding="10"); main.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main, text=lang.get_string('rule_name')).grid(row=0, column=0, sticky='w'); self.name_var = tk.StringVar(value=self.rule_data.get('name', '')); ttk.Entry(main, textvariable=self.name_var, width=50).grid(row=0, column=1, columnspan=3, sticky='ew')
        ttk.Label(main, text=lang.get_string('conditions_logic')).grid(row=1, column=0, sticky='w'); self.logic_var = tk.StringVar(value=self.rule_data.get('conditions_logic', 'AND')); ttk.Combobox(main, textvariable=self.logic_var, values=['AND', 'OR'], state='readonly').grid(row=1, column=1)
        self.create_list_frame(main, lang.get_string('conditions'), 2, 'conditions').grid(row=2, column=0, columnspan=4, sticky='nsew', pady=5)
        self.create_list_frame(main, lang.get_string('actions'), 3, 'actions').grid(row=3, column=0, columnspan=4, sticky='nsew', pady=5)
        self.create_list_frame(main, lang.get_string('delayed_actions'), 4, 'delayed_actions').grid(row=4, column=0, columnspan=4, sticky='nsew', pady=5)
        Button(main, text=lang.get_string('save'), command=self.save).grid(row=5, column=2, pady=10); Button(main, text=lang.get_string('cancel'), command=self.destroy).grid(row=5, column=3, pady=10)
    def create_list_frame(self, parent, title, grid_row, data_key):
        frame = ttk.LabelFrame(parent, text=title, padding="5"); listbox = Listbox(frame, height=4); listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items = self.rule_data.get(data_key, []); listbox.items = items
        for item in items: listbox.insert(tk.END, self.item_to_string(data_key, item))
        btn_frame = ttk.Frame(frame); btn_frame.pack(side=tk.LEFT, padx=5)
        Button(btn_frame, text=self.lang.get_string('add'), command=lambda: self.add_item(data_key, listbox)).pack()
        Button(btn_frame, text=self.lang.get_string('remove_selected'), command=lambda: self.remove_item(listbox)).pack()
        setattr(self, f"{data_key}_listbox", listbox); return frame
    def add_item(self, key, listbox):
        dialog = ItemEditDialog(self, self.lang, key); self.wait_window(dialog)
        if dialog.result_item: listbox.items.append(dialog.result_item); listbox.insert(tk.END, self.item_to_string(key, dialog.result_item))
    def remove_item(self, listbox):
        sel = listbox.curselection();
        if sel: listbox.items.pop(sel[0]); listbox.delete(sel[0])
    def item_to_string(self, key, item):
        item_type_key = item.get("type", "")
        if key == 'conditions':
            port_type = self.lang.get_string(item_type_key); port_num = item['port']; op = item['operator']
            val = self.lang.get_string('on') if item.get('state') == 1 else self.lang.get_string('off') if 'state' in item else item.get('value', '')
            return f"IF {port_type} {port_num} {op} {val}"
        if key == 'actions':
            if item.get('action_type') == 'blink': return f"THEN {self.lang.get_string(item_type_key)} {item['output']} BLINK ({item['interval']}s, {item['duration']}s)"
            if item.get('action_type') == 'latch_on': return f"THEN {self.lang.get_string(item_type_key)} {item['output']} LATCH ON"
            return f"THEN {self.lang.get_string(item_type_key)} {item['output']} = {self.lang.get_string('on') if item.get('state') == 1 else self.lang.get_string('off')}"
        if key == 'delayed_actions': return f"AFTER {item.get('delay', 0)}s -> {len(item.get('actions',[]))} actions"
        return ""
    def save(self):
        self.result_rule = { 'name': self.name_var.get() or "Unnamed", 'enabled': self.rule_data.get('enabled', True), 'conditions_logic': self.logic_var.get(), 'conditions': getattr(self, 'conditions_listbox', tk.Listbox()).items, 'actions': getattr(self, 'actions_listbox', tk.Listbox()).items, 'delayed_actions': getattr(self, 'delayed_actions_listbox', tk.Listbox()).items }
        self.destroy()

class ItemEditDialog(Toplevel):
    def __init__(self, parent, lang, item_key):
        super().__init__(parent); self.transient(parent); self.grab_set(); self.lang, self.result_item, self.parent = lang, None, parent
        if item_key == 'conditions': self.setup_condition_ui()
        elif item_key == 'actions': self.setup_action_ui()
        elif item_key == 'delayed_actions': self.setup_delayed_action_ui()
    def setup_condition_ui(self):
        self.title(self.lang.get_string('add_condition_title')); f = ttk.Frame(self, padding=10); f.pack()
        ttk.Label(f, text=f"{self.lang.get_string('type')}:").grid(row=0, column=0, sticky='w'); self.type_var = tk.StringVar(value='digital_in'); self.type_var.trace_add('write', self.on_cond_type_change)
        ttk.Combobox(f, textvariable=self.type_var, values=['digital_in', 'analog_in', 'digital_out', 'analog_out'], state='readonly').grid(row=0, column=1)
        self.port_frame = ttk.Frame(f); self.port_frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.state_frame = ttk.Frame(f); self.state_frame.grid(row=2, column=0, columnspan=2, pady=5)
        Button(f, text=self.lang.get_string('add'), command=self.save_condition).grid(row=3, column=1, pady=10); self.on_cond_type_change()
    def on_cond_type_change(self, *args):
        for widget in self.port_frame.winfo_children(): widget.destroy()
        for widget in self.state_frame.winfo_children(): widget.destroy()
        cond_type = self.type_var.get()
        if 'digital' in cond_type:
            ports = list(range(1, 6)) if 'in' in cond_type else list(range(1, 9))
            ttk.Label(self.port_frame, text=f"{self.lang.get_string('input' if 'in' in cond_type else 'output')}:").grid(row=0, column=0); self.port_var = tk.IntVar(value=1); ttk.Combobox(self.port_frame, textvariable=self.port_var, values=ports, state='readonly', width=5).grid(row=0, column=1)
            ttk.Label(self.state_frame, text=f"{self.lang.get_string('state')}:").grid(row=0, column=0); self.state_var = tk.StringVar(value=self.lang.get_string('on')); ttk.Combobox(self.state_frame, textvariable=self.state_var, values=[self.lang.get_string('on'), self.lang.get_string('off')], state='readonly', width=8).grid(row=0, column=1)
        elif 'analog' in cond_type:
            ports = [1, 2]
            ttk.Label(self.port_frame, text=f"{self.lang.get_string('input' if 'in' in cond_type else 'output')}:").grid(row=0, column=0); self.port_var = tk.IntVar(value=1); ttk.Combobox(self.port_frame, textvariable=self.port_var, values=ports, state='readonly', width=5).grid(row=0, column=1)
            ttk.Label(self.state_frame, text=f"{self.lang.get_string('operator')}:").grid(row=0, column=0); self.op_var = tk.StringVar(value='>'); ttk.Combobox(self.state_frame, textvariable=self.op_var, values=['>', '<', '=='], state='readonly', width=5).grid(row=0, column=1)
            ttk.Label(self.state_frame, text=f"{self.lang.get_string('value')}:").grid(row=0, column=2); self.val_var = tk.IntVar(value=128); ttk.Entry(self.state_frame, textvariable=self.val_var, width=5).grid(row=0, column=3)
    def save_condition(self):
        cond_type = self.type_var.get()
        if 'digital' in cond_type: self.result_item = {'type': cond_type, 'port': self.port_var.get(), 'state': 1 if self.state_var.get() == self.lang.get_string('on') else 0, 'operator': '=='}
        else: self.result_item = {'type': cond_type, 'port': self.port_var.get(), 'operator': self.op_var.get(), 'value': self.val_var.get()}
        self.destroy()
    def setup_action_ui(self):
        self.title(self.lang.get_string('add_action_title')); f = ttk.Frame(self, padding=10); f.pack()
        ttk.Label(f, text=f"{self.lang.get_string('type')}:").grid(row=0, column=0, sticky='w'); self.type_var = tk.StringVar(value='digital_out'); self.type_var.trace_add('write', self.on_action_port_type_change); ttk.Combobox(f, textvariable=self.type_var, values=['digital_out', 'analog_out'], state='readonly').grid(row=0, column=1)
        self.digital_action_frame = ttk.Frame(f); self.digital_action_frame.grid(row=1, column=0, columnspan=4, pady=5)
        self.analog_action_frame = ttk.Frame(f); self.analog_action_frame.grid(row=1, column=0, columnspan=4, pady=5)
        Button(f, text=self.lang.get_string('add'), command=self.save_action).grid(row=4, column=1, columnspan=2, pady=10); self.on_action_port_type_change()
    def on_action_port_type_change(self, *args):
        is_digital = self.type_var.get() == 'digital_out'
        if is_digital:
            self.analog_action_frame.grid_remove(); self.digital_action_frame.grid()
            ttk.Label(self.digital_action_frame, text=f"{self.lang.get_string('action_type')}:").grid(row=0, column=0, sticky='w'); self.action_type_var = tk.StringVar(value='set_state'); self.action_type_var.trace_add('write', self.on_digital_action_type_change)
            ttk.Combobox(self.digital_action_frame, textvariable=self.action_type_var, values=['set_state', 'blink', 'latch_on'], state='readonly').grid(row=0, column=1, columnspan=3, sticky='w')
            self.set_state_frame = ttk.Frame(self.digital_action_frame); self.set_state_frame.grid(row=1, column=0, columnspan=4, pady=5)
            self.blink_frame = ttk.Frame(self.digital_action_frame); self.blink_frame.grid(row=2, column=0, columnspan=4, pady=5)
            self.latch_frame = ttk.Frame(self.digital_action_frame); self.latch_frame.grid(row=3, column=0, columnspan=4, pady=5)
            self.output_var = tk.IntVar(value=1) # Shared output var
            ttk.Label(self.set_state_frame, text=f"{self.lang.get_string('output')}:").grid(row=0, column=0); ttk.Combobox(self.set_state_frame, textvariable=self.output_var, values=list(range(1, 9)), state='readonly', width=5).grid(row=0, column=1)
            ttk.Label(self.set_state_frame, text=f"{self.lang.get_string('state')}:").grid(row=0, column=2); self.state_var = tk.StringVar(value=self.lang.get_string('on')); ttk.Combobox(self.set_state_frame, textvariable=self.state_var, values=[self.lang.get_string('on'), self.lang.get_string('off')], state='readonly', width=8).grid(row=0, column=3)
            ttk.Label(self.blink_frame, text=f"{self.lang.get_string('output')}:").grid(row=0, column=0); ttk.Combobox(self.blink_frame, textvariable=self.output_var, values=list(range(1, 9)), state='readonly', width=5).grid(row=0, column=1)
            ttk.Label(self.blink_frame, text=f"{self.lang.get_string('interval_sec')}:").grid(row=0, column=2); self.interval_var = tk.DoubleVar(value=0.5); ttk.Entry(self.blink_frame, textvariable=self.interval_var, width=5).grid(row=0, column=3)
            ttk.Label(self.blink_frame, text=f"{self.lang.get_string('duration_sec')}:").grid(row=0, column=4); self.duration_var = tk.DoubleVar(value=10.0); ttk.Entry(self.blink_frame, textvariable=self.duration_var, width=5).grid(row=0, column=5)
            ttk.Label(self.latch_frame, text=f"{self.lang.get_string('output')}:").grid(row=0, column=0); ttk.Combobox(self.latch_frame, textvariable=self.output_var, values=list(range(1, 9)), state='readonly', width=5).grid(row=0, column=1)
            self.on_digital_action_type_change()
        else: # Analog
            self.digital_action_frame.grid_remove(); self.analog_action_frame.grid()
            ttk.Label(self.analog_action_frame, text=f"{self.lang.get_string('output')}:").grid(row=0, column=0); self.output_var = tk.IntVar(value=1); ttk.Combobox(self.analog_action_frame, textvariable=self.output_var, values=[1,2], state='readonly', width=5).grid(row=0, column=1)
            ttk.Label(self.analog_action_frame, text=f"{self.lang.get_string('value')}:").grid(row=0, column=2); self.val_var = tk.IntVar(value=128); ttk.Entry(self.analog_action_frame, textvariable=self.val_var, width=5).grid(row=0, column=3)
    def on_digital_action_type_change(self, *args):
        action_type = self.action_type_var.get()
        is_set_state = action_type == 'set_state'; is_blink = action_type == 'blink'; is_latch = action_type == 'latch_on'
        for child in self.set_state_frame.winfo_children(): child.config(state=tk.NORMAL if is_set_state else tk.DISABLED)
        for child in self.blink_frame.winfo_children(): child.config(state=tk.NORMAL if is_blink else tk.DISABLED)
        for child in self.latch_frame.winfo_children(): child.config(state=tk.NORMAL if is_latch else tk.DISABLED)
    def save_action(self):
        action_mode = self.action_type_var.get()
        self.result_item = {'type': self.type_var.get(), 'action_type': action_mode}
        if self.type_var.get() == 'digital_out':
            self.result_item['output'] = self.output_var.get()
            if action_mode == 'set_state': self.result_item['state'] = 1 if self.state_var.get() == self.lang.get_string('on') else 0
            elif action_mode == 'blink': self.result_item.update({'interval': self.interval_var.get(), 'duration': self.duration_var.get()})
        else: self.result_item.update({'output': self.output_var.get(), 'value': self.val_var.get()})
        self.destroy()
    def setup_delayed_action_ui(self):
        self.title(self.lang.get_string('add_delayed_action_title')); f = ttk.Frame(self, padding=10); f.pack()
        ttk.Label(f, text=f"{self.lang.get_string('delay_sec')}:").grid(row=0, column=0); self.delay_var = tk.DoubleVar(value=1.0); ttk.Entry(f, textvariable=self.delay_var, width=5).grid(row=0, column=1)
        self.action_listbox = Listbox(f, height=3); self.action_listbox.grid(row=1, column=0, columnspan=2, pady=5); self.delayed_actions_list = []
        btn_frame = ttk.Frame(f); btn_frame.grid(row=2, column=0, columnspan=2)
        Button(btn_frame, text=self.lang.get_string('add'), command=self.add_sub_action).pack(side=tk.LEFT, padx=5)
        Button(btn_frame, text=self.lang.get_string('remove_selected'), command=self.remove_sub_action).pack(side=tk.LEFT, padx=5)
        Button(f, text=self.lang.get_string('save'), command=self.save_delayed_action).grid(row=3, column=0, columnspan=2, pady=10)
    def add_sub_action(self):
        dialog = ItemEditDialog(self, self.lang, 'actions'); self.wait_window(dialog)
        if dialog.result_item: self.delayed_actions_list.append(dialog.result_item); self.action_listbox.insert(tk.END, self.parent.item_to_string('actions', dialog.result_item))
    def remove_sub_action(self):
        sel = self.action_listbox.curselection();
        if sel: self.delayed_actions_list.pop(sel[0]); self.action_listbox.delete(sel[0])
    def save_delayed_action(self):
        self.result_item = {'delay': self.delay_var.get(), 'actions': self.delayed_actions_list}; self.destroy()

class ConfigWindow(Toplevel):
    def __init__(self, parent, lang, current_config, save_callback):
        super().__init__(parent); self.title(lang.get_string('config_window_title')); self.transient(parent); self.grab_set()
        self.config_vars, self.save_callback, self.lang = {}, save_callback, lang
        try: self.icon_types = sorted(list(set([f.split('_')[0] for f in os.listdir(ICONS_DIR) if '_' in f])))
        except FileNotFoundError: self.icon_types = [lang.get_string('no_icons_found')]
        main_frame = ttk.Frame(self, padding="10"); main_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(main_frame, text=lang.get_string('output_header'), font='-weight bold').grid(row=0, column=0, pady=5)
        ttk.Label(main_frame, text=lang.get_string('label_header'), font='-weight bold').grid(row=0, column=1, pady=5)
        ttk.Label(main_frame, text=lang.get_string('icon_header'), font='-weight bold').grid(row=0, column=2, pady=5)
        for i in range(1, 9):
            cfg = current_config.get(str(i), {"label": f"Output {i}", "icon": "bulb"})
            ttk.Label(main_frame, text=f"Output {i}:").grid(row=i, column=0, padx=(0, 10))
            label_var = tk.StringVar(value=cfg['label']); icon_var = tk.StringVar(value=cfg['icon'])
            ttk.Entry(main_frame, textvariable=label_var).grid(row=i, column=1, sticky="ew")
            ttk.Combobox(main_frame, textvariable=icon_var, values=self.icon_types, state="readonly").grid(row=i, column=2, padx=(5, 0))
            self.config_vars[i] = {"label": label_var, "icon": icon_var}
        main_frame.columnconfigure(1, weight=1)
        btn_frame = ttk.Frame(self); btn_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(btn_frame, text=lang.get_string('save'), command=self._save).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text=lang.get_string('cancel'), command=self.destroy).pack(side=tk.RIGHT, padx=5)
    def _save(self):
        new_config = {str(i): {"label": v["label"].get(), "icon": v["icon"].get()} for i, v in self.config_vars.items()}
        self.save_callback(new_config); self.destroy()

def create_initial_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Creating default config file: {CONFIG_FILE}")
        config = configparser.ConfigParser(); config['General'] = {'language': 'en'}
        with open(CONFIG_FILE, 'w') as f: config.write(f)

if __name__ == "__main__":
    create_initial_config()
    app = MainApplication()
    app.mainloop()
