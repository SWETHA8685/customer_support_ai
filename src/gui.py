import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path


# ============================================================
# PROJECT IMPORT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from agent import SupportAgent
except ImportError:
    try:
        from src.agent import SupportAgent
    except ImportError:
        SupportAgent = None


# ============================================================
# COLORS
# ============================================================

BG = "#EAEDED"
CARD = "#FFFFFF"

NAVY = "#131A22"
NAVY_LIGHT = "#232F3E"

ORANGE = "#FF9900"
ORANGE_DARK = "#E47911"
ORANGE_LIGHT = "#FFF3E0"

BLUE = "#146EB4"
BLUE_LIGHT = "#EAF4FB"

PURPLE = "#6B4EFF"
PURPLE_LIGHT = "#F1EEFF"

GREEN = "#067D62"
GREEN_LIGHT = "#E8F5F1"

RED = "#C7511F"
RED_LIGHT = "#FCEFEA"

TEXT = "#172033"
TEXT_2 = "#374151"
MUTED = "#667085"

BORDER = "#D5D9D9"
INPUT_BG = "#F7F8F8"
WHITE = "#FFFFFF"


# ============================================================
# MAIN APPLICATION
# ============================================================

class HiverSupportGUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Hiver AI Support Agent")
        self.geometry("1250x820")
        self.minsize(1000, 700)
        self.configure(bg=BG)

        self.agent = None

        self._build_styles()
        self._build_ui()

        self._show_welcome()
        self._initialize_agent()

    # ========================================================
    # INITIALIZE AGENT
    # ========================================================

    def _initialize_agent(self):

        if SupportAgent is None:

            self.status_var.set("●  Agent Import Failed")
            self.status_label.configure(
                fg="#FFB4A2"
            )

            self._set_response(
                "The GUI loaded successfully, but SupportAgent "
                "could not be imported.\n\n"
                "Please check your project structure and agent.py."
            )

            return

        try:

            self.agent = SupportAgent()

            self.status_var.set("●  Agent Ready")
            self.status_label.configure(
                fg="#7EE2B8"
            )

        except Exception as exc:

            self.status_var.set(
                "●  Agent Initialization Failed"
            )

            self.status_label.configure(
                fg="#FFB4A2"
            )

            self._set_response(
                "The interface loaded successfully, but the AI "
                "agent could not be initialized.\n\n"
                f"{type(exc).__name__}: {exc}\n\n"
                "Check the terminal for the complete traceback."
            )

    # ========================================================
    # STYLES
    # ========================================================

    def _build_styles(self):

        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Analyze.TButton",
            font=("Segoe UI", 11, "bold"),
            foreground="#111111",
            background=ORANGE,
            padding=(24, 12),
            borderwidth=0,
            relief="flat"
        )

        style.map(
            "Analyze.TButton",
            background=[
                ("active", "#FFAD1F"),
                ("pressed", ORANGE_DARK),
                ("disabled", "#E5C78C")
            ],
            foreground=[
                ("disabled", "#777777")
            ]
        )

        style.configure(
            "Clear.TButton",
            font=("Segoe UI", 10, "bold"),
            foreground=TEXT,
            background=WHITE,
            padding=(18, 10),
            borderwidth=1,
            relief="solid"
        )

        style.map(
            "Clear.TButton",
            background=[
                ("active", "#F3F4F6")
            ]
        )

    # ========================================================
    # BUILD UI
    # ========================================================

    def _build_ui(self):

        # ====================================================
        # HEADER
        # ====================================================

        header = tk.Frame(
            self,
            bg=NAVY,
            height=86
        )

        header.pack(fill="x")
        header.pack_propagate(False)

        header_left = tk.Frame(
            header,
            bg=NAVY
        )

        header_left.pack(
            side="left",
            padx=28
        )

        tk.Label(
            header_left,
            text="hiver",
            font=("Segoe UI", 25, "bold"),
            fg=WHITE,
            bg=NAVY
        ).pack(side="left")

        tk.Frame(
            header_left,
            bg=ORANGE,
            width=3,
            height=40
        ).pack(
            side="left",
            padx=15
        )

        title_box = tk.Frame(
            header_left,
            bg=NAVY
        )

        title_box.pack(side="left")

        tk.Label(
            title_box,
            text="AI Support Agent",
            font=("Segoe UI", 15, "bold"),
            fg=WHITE,
            bg=NAVY
        ).pack(anchor="w")

        tk.Label(
            title_box,
            text="AmazonHelp • Intelligent Customer Support",
            font=("Segoe UI", 8),
            fg="#AEB8C5",
            bg=NAVY
        ).pack(anchor="w")

        # ====================================================
        # STATUS
        # ====================================================

        status_box = tk.Frame(
            header,
            bg=NAVY_LIGHT,
            padx=15,
            pady=8
        )

        status_box.pack(
            side="right",
            padx=28
        )

        tk.Label(
            status_box,
            text="AI SYSTEM",
            font=("Segoe UI", 7, "bold"),
            fg="#94A3B8",
            bg=NAVY_LIGHT
        ).pack(anchor="w")

        self.status_var = tk.StringVar(
            value="●  Starting Agent..."
        )

        self.status_label = tk.Label(
            status_box,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "bold"),
            fg="#FBBF24",
            bg=NAVY_LIGHT
        )

        self.status_label.pack(anchor="w")

        # ====================================================
        # SCROLL AREA
        # ====================================================

        outer = tk.Frame(
            self,
            bg=BG
        )

        outer.pack(
            fill="both",
            expand=True
        )

        canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview
        )

        self.content = tk.Frame(
            canvas,
            bg=BG
        )

        self.content.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        def resize_content(event):

            canvas.itemconfigure(
                canvas_window,
                width=event.width
            )

        canvas.bind(
            "<Configure>",
            resize_content
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ====================================================
        # HERO
        # ====================================================

        hero = tk.Frame(
            self.content,
            bg=NAVY_LIGHT,
            height=140
        )

        hero.pack(
            fill="x",
            padx=24,
            pady=(24, 15)
        )

        hero.pack_propagate(False)

        hero_left = tk.Frame(
            hero,
            bg=NAVY_LIGHT
        )

        hero_left.pack(
            side="left",
            padx=28,
            pady=22
        )

        tk.Label(
            hero_left,
            text="AI-POWERED CUSTOMER SUPPORT",
            font=("Segoe UI", 8, "bold"),
            fg=ORANGE,
            bg=NAVY_LIGHT
        ).pack(anchor="w")

        tk.Label(
            hero_left,
            text="Analyze customer conversations intelligently",
            font=("Segoe UI", 19, "bold"),
            fg=WHITE,
            bg=NAVY_LIGHT
        ).pack(
            anchor="w",
            pady=(5, 3)
        )

        tk.Label(
            hero_left,
            text=(
                "Classify  •  Retrieve evidence  •  Decide  •  Draft response"
            ),
            font=("Segoe UI", 9),
            fg="#B8C4D2",
            bg=NAVY_LIGHT
        ).pack(anchor="w")

        tk.Label(
            hero,
            text="✦",
            font=("Segoe UI", 54),
            fg=ORANGE,
            bg=NAVY_LIGHT
        ).pack(
            side="right",
            padx=55
        )

        # ====================================================
        # CUSTOMER MESSAGE CARD
        # ====================================================

        input_card = tk.Frame(
            self.content,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        input_card.pack(
            fill="x",
            padx=24,
            pady=(0, 15)
        )

        input_header = tk.Frame(
            input_card,
            bg=CARD
        )

        input_header.pack(
            fill="x",
            padx=22,
            pady=(20, 0)
        )

        tk.Label(
            input_header,
            text="Customer Message",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(side="left")

        tk.Label(
            input_header,
            text="  AI ANALYSIS  ",
            font=("Segoe UI", 7, "bold"),
            fg=BLUE,
            bg=BLUE_LIGHT,
            padx=7,
            pady=4
        ).pack(
            side="left",
            padx=12
        )

        tk.Label(
            input_card,
            text=(
                "Enter a customer request and let the agent "
                "classify, retrieve evidence, decide, and draft a response."
            ),
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=CARD
        ).pack(
            anchor="w",
            padx=22,
            pady=(7, 11)
        )

        # ====================================================
        # MESSAGE INPUT
        # ====================================================

        self.message_text = tk.Text(
            input_card,
            height=5,
            font=("Segoe UI", 11),
            fg=TEXT,
            bg=INPUT_BG,
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1,
            wrap="word",
            padx=14,
            pady=12,
            insertbackground=TEXT
        )

        self.message_text.pack(
            fill="x",
            padx=22,
            pady=(0, 13)
        )

        # ====================================================
        # BUTTON ROW
        # ====================================================

        button_row = tk.Frame(
            input_card,
            bg=CARD
        )

        button_row.pack(
            fill="x",
            padx=22,
            pady=(0, 16)
        )

        self.analyze_button = ttk.Button(
            button_row,
            text="  🔍  Analyze Message  ",
            style="Analyze.TButton",
            command=self.analyze
        )

        self.analyze_button.pack(
            side="left"
        )

        ttk.Button(
            button_row,
            text="Clear",
            style="Clear.TButton",
            command=self.clear
        ).pack(
            side="left",
            padx=10
        )

        # ====================================================
        # QUICK EXAMPLES
        # ====================================================

        tk.Label(
            input_card,
            text="QUICK EXAMPLES",
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=CARD
        ).pack(
            anchor="w",
            padx=22,
            pady=(0, 6)
        )

        examples = [
            "My package says delivered but I haven't received it.",
            "I need a refund for my returned item.",
            "Why is my Prime membership not working?",
            "My Amazon Pay payment failed."
        ]

        example_box = tk.Frame(
            input_card,
            bg=CARD
        )

        example_box.pack(
            fill="x",
            padx=22,
            pady=(0, 20)
        )

        for example in examples:

            display_text = example

            if len(display_text) > 38:
                display_text = display_text[:38] + "..."

            tk.Button(
                example_box,
                text=display_text,
                font=("Segoe UI", 8),
                fg=BLUE,
                bg=BLUE_LIGHT,
                activeforeground=BLUE,
                activebackground="#D9ECFA",
                relief="flat",
                cursor="hand2",
                padx=10,
                pady=7,
                borderwidth=0,
                command=lambda x=example: self._set_message(x)
            ).pack(
                side="left",
                padx=(0, 7)
            )

        # ====================================================
        # RESULT CARDS
        # ====================================================

        results = tk.Frame(
            self.content,
            bg=BG
        )

        results.pack(
            fill="x",
            padx=24,
            pady=(0, 15)
        )

        results.grid_columnconfigure(
            0,
            weight=1
        )

        results.grid_columnconfigure(
            1,
            weight=1
        )

        self.intent_card = self._result_card(
            results,
            0,
            0,
            "🎯  PREDICTED INTENT",
            "Waiting for analysis",
            PURPLE
        )

        self.decision_card = self._result_card(
            results,
            0,
            1,
            "🛡  DECISION",
            "Waiting for analysis",
            ORANGE
        )

        # ====================================================
        # HISTORICAL EVIDENCE
        # ====================================================

        evidence_card = tk.Frame(
            self.content,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        evidence_card.pack(
            fill="x",
            padx=24,
            pady=(0, 15)
        )

        evidence_header = tk.Frame(
            evidence_card,
            bg=CARD
        )

        evidence_header.pack(
            fill="x",
            padx=22,
            pady=(19, 0)
        )

        tk.Label(
            evidence_header,
            text="📚  Historical Evidence",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(side="left")

        tk.Label(
            evidence_header,
            text="GROUNDING",
            font=("Segoe UI", 7, "bold"),
            fg=GREEN,
            bg=GREEN_LIGHT,
            padx=8,
            pady=4
        ).pack(
            side="left",
            padx=12
        )

        tk.Label(
            evidence_card,
            text=(
                "Closest historical customer interaction used "
                "to ground the response."
            ),
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=CARD
        ).pack(
            anchor="w",
            padx=22,
            pady=(5, 10)
        )

        self.evidence_text = self._readonly_text(
            evidence_card,
            height=9
        )

        self.evidence_text.pack(
            fill="x",
            padx=22,
            pady=(0, 20)
        )

        # ====================================================
        # SUGGESTED RESPONSE
        # ====================================================

        response_card = tk.Frame(
            self.content,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        response_card.pack(
            fill="x",
            padx=24,
            pady=(0, 25)
        )

        response_header = tk.Frame(
            response_card,
            bg=CARD
        )

        response_header.pack(
            fill="x",
            padx=22,
            pady=(19, 0)
        )

        tk.Label(
            response_header,
            text="💬  Suggested Response",
            font=("Segoe UI", 13, "bold"),
            fg=TEXT,
            bg=CARD
        ).pack(side="left")

        tk.Label(
            response_header,
            text="AI DRAFT",
            font=("Segoe UI", 7, "bold"),
            fg=ORANGE_DARK,
            bg=ORANGE_LIGHT,
            padx=8,
            pady=4
        ).pack(
            side="left",
            padx=12
        )

        tk.Label(
            response_card,
            text=(
                "Draft generated from the predicted intent "
                "and retrieved historical resolution."
            ),
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=CARD
        ).pack(
            anchor="w",
            padx=22,
            pady=(5, 10)
        )

        self.response_text = self._readonly_text(
            response_card,
            height=9
        )

        self.response_text.pack(
            fill="x",
            padx=22,
            pady=(0, 22)
        )

        # ====================================================
        # FOOTER
        # ====================================================

        footer = tk.Frame(
            self.content,
            bg=NAVY
        )

        footer.pack(
            fill="x"
        )

        tk.Label(
            footer,
            text="Hiver AI Support Agent",
            font=("Segoe UI", 9, "bold"),
            fg=WHITE,
            bg=NAVY
        ).pack(
            side="left",
            padx=25,
            pady=15
        )

        tk.Label(
            footer,
            text=(
                "Intent Classification  •  Evidence Retrieval  "
                "•  Decision Engine"
            ),
            font=("Segoe UI", 8),
            fg="#AAB5C3",
            bg=NAVY
        ).pack(
            side="right",
            padx=25
        )

    # ========================================================
    # RESULT CARD
    # ========================================================

    def _result_card(
        self,
        parent,
        row,
        col,
        heading,
        value,
        accent
    ):

        card = tk.Frame(
            parent,
            bg=CARD,
            highlightbackground=BORDER,
            highlightthickness=1,
            height=155
        )

        card.grid(
            row=row,
            column=col,
            sticky="nsew",
            padx=(
                (0, 7)
                if col == 0
                else (7, 0)
            )
        )

        card.grid_propagate(False)

        # Accent line
        tk.Frame(
            card,
            bg=accent,
            width=5
        ).pack(
            side="left",
            fill="y"
        )

        body = tk.Frame(
            card,
            bg=CARD
        )

        body.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=17
        )

        tk.Label(
            body,
            text=heading,
            font=("Segoe UI", 8, "bold"),
            fg=MUTED,
            bg=CARD
        ).pack(
            anchor="w"
        )

        value_var = tk.StringVar(
            value=value
        )

        value_label = tk.Label(
            body,
            textvariable=value_var,
            font=("Segoe UI", 18, "bold"),
            fg=accent,
            bg=CARD,
            wraplength=500,
            justify="left"
        )

        value_label.pack(
            anchor="w",
            pady=(14, 5)
        )

        detail_var = tk.StringVar(
            value="—"
        )

        tk.Label(
            body,
            textvariable=detail_var,
            font=("Segoe UI", 9),
            fg=MUTED,
            bg=CARD,
            wraplength=500,
            justify="left"
        ).pack(
            anchor="w"
        )

        return {
            "value": value_var,
            "detail": detail_var,
            "label": value_label
        }

    # ========================================================
    # READONLY TEXT
    # ========================================================

    def _readonly_text(
        self,
        parent,
        height=7
    ):

        text = tk.Text(
            parent,
            height=height,
            font=("Segoe UI", 10),
            fg=TEXT_2,
            bg=INPUT_BG,
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1,
            wrap="word",
            padx=14,
            pady=12,
            spacing1=2,
            spacing3=2
        )

        text.configure(
            state="disabled"
        )

        return text

    # ========================================================
    # SET TEXT
    # ========================================================

    def _set_text(
        self,
        widget,
        value
    ):

        widget.configure(
            state="normal"
        )

        widget.delete(
            "1.0",
            "end"
        )

        widget.insert(
            "1.0",
            str(value)
        )

        widget.configure(
            state="disabled"
        )

    # ========================================================
    # SET RESPONSE
    # ========================================================

    def _set_response(
        self,
        text
    ):

        self._set_text(
            self.response_text,
            text
        )

    # ========================================================
    # SET MESSAGE
    # ========================================================

    def _set_message(
        self,
        message
    ):

        self.message_text.delete(
            "1.0",
            "end"
        )

        self.message_text.insert(
            "1.0",
            message
        )

        self.message_text.focus_set()

    # ========================================================
    # WELCOME
    # ========================================================

    def _show_welcome(self):

        self._set_text(
            self.evidence_text,
            (
                "No analysis yet.\n\n"
                "Enter a customer message above and click "
                "\"Analyze Message\".\n\n"
                "The system will retrieve the closest historical "
                "interaction and use it as evidence."
            )
        )

        self._set_response(
            "Your AI-generated support response will appear here."
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear(self):

        self.message_text.delete(
            "1.0",
            "end"
        )

        self.intent_card["value"].set(
            "Waiting for analysis"
        )

        self.intent_card["detail"].set(
            "—"
        )

        self.decision_card["value"].set(
            "Waiting for analysis"
        )

        self.decision_card["detail"].set(
            "—"
        )

        self.intent_card["label"].configure(
            fg=PURPLE
        )

        self.decision_card["label"].configure(
            fg=ORANGE
        )

        self._set_text(
            self.evidence_text,
            "No analysis yet."
        )

        self._set_response(
            "Your AI-generated support response will appear here."
        )

        self.status_var.set(
            "●  Agent Ready"
        )

        self.status_label.configure(
            fg="#7EE2B8"
        )

        self.message_text.focus_set()

    # ========================================================
    # ANALYZE
    # ========================================================

    def analyze(self):

        message = self.message_text.get(
            "1.0",
            "end"
        ).strip()

        if not message:

            messagebox.showwarning(
                "Message Required",
                "Please enter a customer message first."
            )

            return

        if self.agent is None:

            messagebox.showerror(
                "Agent Unavailable",
                "The SupportAgent could not be loaded. "
                "Check the terminal."
            )

            return

        self.analyze_button.configure(
            state="disabled"
        )

        self.status_var.set(
            "●  Analyzing..."
        )

        self.status_label.configure(
            fg="#FBBF24"
        )

        self.update_idletasks()

        try:

            # =================================================
            # EXISTING BACKEND LOGIC
            # =================================================

            result = self.agent.handle(message)

            # =================================================
            # DISPLAY RESULT
            # =================================================

            self._display_result(
                result
            )

            self.status_var.set(
                "●  Analysis Complete"
            )

            self.status_label.configure(
                fg="#7EE2B8"
            )

        except Exception as exc:

            self.status_var.set(
                "●  Analysis Error"
            )

            self.status_label.configure(
                fg="#FFB4A2"
            )

            messagebox.showerror(
                "Analysis Error",
                f"{type(exc).__name__}: {exc}"
            )

        finally:

            self.analyze_button.configure(
                state="normal"
            )

    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    def _display_result(
        self,
        result
    ):

        if not isinstance(
            result,
            dict
        ):

            self._set_response(
                str(result)
            )

            return

        # ----------------------------------------------------
        # INTENT
        # ----------------------------------------------------

        intent = result.get(
            "intent",
            result.get(
                "predicted_intent",
                "Unknown"
            )
        )

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        decision = result.get(
            "decision",
            result.get(
                "predicted_decision",
                "Unknown"
            )
        )

        # ----------------------------------------------------
        # REASON
        # ----------------------------------------------------

        reason = result.get(
            "reason",
            "No decision reason provided."
        )

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        response = (
            result.get("response")
            or result.get("generated_response")
            or result.get("draft_response")
            or "No response was generated."
        )

        # ----------------------------------------------------
        # EVIDENCE
        # ----------------------------------------------------

        evidence = result.get(
            "evidence",
            {}
        )

        # ====================================================
        # INTENT
        # ====================================================

        self.intent_card["value"].set(
            self._pretty(intent)
        )

        self.intent_card["detail"].set(
            "Predicted from the customer conversation."
        )

        # ====================================================
        # DECISION
        # ====================================================

        self.decision_card["value"].set(
            self._pretty(decision)
        )

        self.decision_card["detail"].set(
            str(reason)
        )

        # ----------------------------------------------------
        # DECISION COLOR
        # ----------------------------------------------------

        if str(
            decision
        ).lower() == "auto_handle":

            self.decision_card["label"].configure(
                fg=GREEN
            )

        else:

            self.decision_card["label"].configure(
                fg=RED
            )

        # ====================================================
        # EVIDENCE DICTIONARY
        # ====================================================

        if isinstance(
            evidence,
            dict
        ):

            evidence_message = evidence.get(
                "customer_message",
                "No historical example available."
            )

            evidence_response = evidence.get(
                "agent_response",
                "No historical response available."
            )

            similarity = evidence.get(
                "similarity"
            )

            if similarity is not None:

                try:

                    similarity_text = (
                        f"{float(similarity):.1%}"
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    similarity_text = str(
                        similarity
                    )

            else:

                similarity_text = "N/A"

            evidence_output = (
                f"SIMILARITY: {similarity_text}\n\n"
                f"HISTORICAL CUSTOMER MESSAGE:\n"
                f"{evidence_message}\n\n"
                f"{'─' * 70}\n\n"
                f"HISTORICAL AGENT RESPONSE:\n"
                f"{evidence_response}"
            )

        # ====================================================
        # EVIDENCE LIST
        # ====================================================

        elif isinstance(
            evidence,
            list
        ):

            chunks = []

            for i, item in enumerate(
                evidence[:3],
                start=1
            ):

                if isinstance(
                    item,
                    dict
                ):

                    similarity = item.get(
                        "similarity"
                    )

                    if similarity is not None:

                        try:

                            similarity_text = (
                                f"{float(similarity):.1%}"
                            )

                        except (
                            ValueError,
                            TypeError
                        ):

                            similarity_text = str(
                                similarity
                            )

                        chunks.append(
                            f"#{i}  Similarity: "
                            f"{similarity_text}"
                        )

                    else:

                        chunks.append(
                            f"#{i}"
                        )

                    chunks.append(
                        "CUSTOMER:\n"
                        + str(
                            item.get(
                                "customer_message",
                                ""
                            )
                        )
                    )

                    chunks.append(
                        "AGENT:\n"
                        + str(
                            item.get(
                                "agent_response",
                                ""
                            )
                        )
                    )

                else:

                    chunks.append(
                        str(item)
                    )

            if chunks:

                evidence_output = (
                    "\n\n"
                    + (
                        "\n\n"
                        + ("─" * 70)
                        + "\n\n"
                    ).join(
                        chunks
                    )
                )

            else:

                evidence_output = (
                    "No evidence available."
                )

        # ====================================================
        # OTHER
        # ====================================================

        else:

            evidence_output = str(
                evidence
            )

        # ====================================================
        # UPDATE EVIDENCE
        # ====================================================

        self._set_text(
            self.evidence_text,
            evidence_output
        )

        # ====================================================
        # UPDATE RESPONSE
        # ====================================================

        self._set_response(
            str(response)
        )

    # ========================================================
    # PRETTY TEXT
    # ========================================================

    @staticmethod
    def _pretty(
        value
    ):

        text = (
            str(value)
            .replace(
                "_",
                " "
            )
            .strip()
        )

        if not text:
            return "Unknown"

        return text.title()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = HiverSupportGUI()

    app.mainloop()