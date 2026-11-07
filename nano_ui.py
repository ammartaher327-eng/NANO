
import asyncio
from datetime import datetime

from rich.markup import escape
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Input, Static, RichLog

from nano_engine import NanoEngine


class NanoUI(App):

    CSS = """
    Screen {
        background: #080b0a;
    }

    #main {
        margin: 1 2;
        border: round #00cc88;
        padding: 1 2;
    }

    #brand {
        color: #00ff9d;
        text-style: bold;
        text-align: center;
        height: 3;
    }

    #subtitle {
        color: #668f7c;
        text-align: center;
        height: 2;
    }

    #conversation {
        height: 1fr;
        border: round #176b4c;
        background: #0d1210;
        padding: 1;
        scrollbar-color: #00cc88;
    }

    #message {
        margin-top: 1;
        border: round #00cc88;
    }

    #status {
        color: #00cc88;
        height: 2;
        content-align: center middle;
    }
    """

    def __init__(self):
        super().__init__()
        self.engine = None
        self.busy = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Container(id="main"):
            yield Static("N A N O", id="brand")
            yield Static(
                "LOCAL INTELLIGENCE SYSTEM  /  v0.7",
                id="subtitle"
            )

            yield RichLog(
                id="conversation",
                wrap=True,
                markup=True
            )

            yield Input(
                placeholder="Initializing NANO...",
                id="message",
                disabled=True
            )

            yield Static(
                "● INITIALIZING ENGINE...",
                id="status"
            )

        yield Footer()

    def set_status(self, message):
        self.query_one("#status", Static).update(message)

    def write_message(self, sender, message):
        log = self.query_one("#conversation", RichLog)

        timestamp = datetime.now().strftime("%H:%M:%S")
        safe_message = escape(str(message))

        color = "white" if sender == "YOU" else "#00ff9d"

        log.write(
            f"[dim]{timestamp}[/dim]  "
            f"[bold {color}]{sender}[/bold {color}]"
        )

        log.write(f"  {safe_message}")
        log.write("")

    async def on_mount(self):
        self.write_message(
            "NANO",
            "Interface initialized. Loading inference engine..."
        )

        try:
            # Load the model without freezing the interface.
            self.engine = await asyncio.to_thread(NanoEngine)

            self.set_status(
                "● SYSTEM ONLINE  |  ENGINE: READY"
            )

            message_input = self.query_one("#message", Input)
            message_input.placeholder = "Enter a message..."
            message_input.disabled = False
            message_input.focus()

            self.write_message(
                "NANO",
                "Inference engine connected. I'm ready."
            )

        except Exception as error:
            self.set_status("● ENGINE INITIALIZATION FAILED")

            self.write_message(
                "SYSTEM",
                f"Engine initialization failed: {error}"
            )

    async def on_input_submitted(self, event: Input.Submitted):

        message = event.value.strip()

        if not message or self.engine is None or self.busy:
            return

        event.input.value = ""
        event.input.disabled = True

        self.busy = True

        self.write_message("YOU", message)

        self.set_status("● NANO IS THINKING...")

        try:
            # Generate without blocking the interface.
            response = await asyncio.to_thread(
                self.engine.generate_reply,
                message
            )

            self.write_message("NANO", response)

            self.set_status(
                "● SYSTEM ONLINE  |  ENGINE: READY"
            )

        except Exception as error:
            self.write_message(
                "SYSTEM",
                f"Generation failed: {error}"
            )

            self.set_status("● GENERATION ERROR")

        finally:
            self.busy = False
            event.input.disabled = False
            event.input.focus()


if __name__ == "__main__":
    NanoUI().run()
