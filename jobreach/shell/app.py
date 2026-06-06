import traceback

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory

from jobreach.app.onboarding_service import OnboardingService
from jobreach.config.paths import migrate_legacy_data_dir
from jobreach.core.errors import JobReachError
from jobreach.logs.sent_log import SentLog
from jobreach.mail.gmail_auth import get_gmail_email, gmail_connected
from jobreach.ai.provider_registry import get_provider
from jobreach.drafts.index import list_batches
from jobreach.shell.commands import COMMANDS, ShellContext, resolve_command
from jobreach.shell.render import print_startup_banner


class JobReachShell:
    def __init__(self):
        self.ctx = ShellContext()
        self.session = PromptSession(
            history=InMemoryHistory(),
            completer=WordCompleter(sorted(set(COMMANDS.keys()) | set(["quit", "exit"]))),
        )

    def run(self) -> None:
        if migrate_legacy_data_dir():
            print(
                "Migrated local data from ./.jobreach to ~/.jobreach.\n"
            )

        onboarding = OnboardingService(self.ctx.settings_store, self.ctx.secret_store)
        if onboarding.needs_onboarding():
            onboarding.run()

        self._print_banner()

        while True:
            try:
                raw = self.session.prompt("JobReach> ")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                return

            command = resolve_command(raw)
            if not command:
                continue
            if command in {"exit", "quit"}:
                print("Goodbye.")
                return

            handler = COMMANDS.get(command)
            if not handler:
                print(f'Unknown command: {raw.strip()}. Type "help" for commands.')
                continue

            try:
                handler(self.ctx)
            except JobReachError as exc:
                print(f"Error: {exc}")
            except Exception as exc:
                if self.ctx.debug:
                    traceback.print_exception(type(exc), exc, exc.__traceback__)
                else:
                    print(f"Error: {exc}")

    def _print_banner(self) -> None:
        settings = self.ctx.settings_store.load()
        configured = bool(
            settings.default_provider
            and settings.default_model
            and self.ctx.secret_store.has_provider_key(settings.default_provider or "")
        )
        if configured and settings.default_provider:
            provider_label = get_provider(settings.default_provider).display_name
            model_label = settings.default_model or "-"
        else:
            provider_label = "Not configured"
            model_label = "-"

        if gmail_connected():
            email = get_gmail_email()
            gmail_label = f"Connected ({email})" if email else "Connected"
        else:
            gmail_label = "Not connected"

        print_startup_banner(
            provider_label=provider_label,
            model_label=model_label,
            gmail_label=gmail_label,
            draft_batches=len(list_batches()),
            sent_count=SentLog().count_sent(),
            configured=configured,
        )
