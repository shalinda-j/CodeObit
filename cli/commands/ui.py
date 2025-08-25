"""
UI command to start the web-based user interface
"""

from typing import Optional


class UICommand:
    """Start the web UI server"""

    def add_parser(self, subparsers):
        """Add UI subcommand parser"""
        parser = subparsers.add_parser(
            "ui", help="Start the web-based UI for the CLI"
        )
        parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
        parser.add_argument("--port", type=int, default=8000, help="Port to bind")
        parser.add_argument(
            "--debug", action="store_true", help="Enable Flask debug mode"
        )
        return parser

    def execute(self, args, config_manager, console):
        """Execute the UI command by running the Flask app"""
        from cli.ui.app import create_app

        app = create_app()

        console.print(
            f"[green]Starting CodeObit UI at http://{args.host}:{args.port}[/green]"
        )
        app.run(host=args.host, port=args.port, debug=getattr(args, "debug", False))
