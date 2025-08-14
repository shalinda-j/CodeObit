"""
Autopilot command: generate → test → fix loop
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional

from rich.panel import Panel
from rich.markdown import Markdown

from cli.commands.base import BaseCommand
from cli.ai.gemini_client import GeminiClient
from cli.utils.file_manager import FileManager
from cli.utils.project_analyzer import ProjectAnalyzer


class AutopilotCommand(BaseCommand):
	"""Automated development loop that generates code, tests, and iterates fixes"""

	def add_parser(self, subparsers):
		parser = subparsers.add_parser(
			'autopilot',
			help='Automated generate → test → fix loop with optional git commits'
		)
		parser.add_argument('--goal', '-g', required=True, help='What to build (specification/goal)')
		parser.add_argument('--language', '-l', default='python', help='Target language (default: python)')
		parser.add_argument('--output', '-o', help='Output file path (default: guessed from language)')
		parser.add_argument('--apply', action='store_true', help='Write generated changes to files')
		parser.add_argument('--test', action='store_true', help='Run tests after generation')
		parser.add_argument('--max-iterations', type=int, default=2, help='Max generate→test iterations (default: 2)')
		parser.add_argument('--commit', action='store_true', help='Commit changes to git if generation succeeds')
		parser.add_argument('--branch', help='Create/switch to this git branch before committing')
		parser.add_argument('--dry-run', action='store_true', help='Do everything except writing files')
		return parser

	def execute(self, args, config_manager, console):
		console.print("[bold magenta]Autopilot:[/bold magenta] generate → test → fix")

		# Initialize helpers
		api_key = config_manager.get('api_key')
		gemini = GeminiClient(api_key)
		file_manager = FileManager()
		analyzer = ProjectAnalyzer(project_path='.')

		# Step 1: Planning
		plan_prompt = self._build_plan_prompt(args.goal, args.language)
		plan = gemini.generate_content(plan_prompt, temperature=0.3)
		console.print(Panel(Markdown(plan), title="Plan", border_style="cyan"))

		# Step 2: Iterative loop
		last_test_output: Optional[str] = None
		for iteration in range(1, max(1, args.max_iterations) + 1):
			console.print(f"[bold blue]Iteration {iteration}[/bold blue]")

			code_prompt = self._build_code_prompt(args.goal, args.language, plan, last_test_output)
			response = gemini.generate_content(code_prompt, temperature=0.2)

			language, code = self._extract_primary_code_block(response, default_language=args.language)
			if not code:
				# Fallback: use full response
				code = response

			# Determine output file
			output_path = args.output or self._default_output_for_language(language)

			# Write or preview
			if args.apply and not args.dry_run:
				file_manager.write_file(output_path, code)
				console.print(f"[green]✓ Wrote file:[/green] {output_path}")
			else:
				console.print(Panel(Markdown(f"```{language}\n{code}\n```"), title=f"Preview: {output_path}", border_style="green"))

			# Optionally run tests
			if not args.test:
				break

			test_result = analyzer.run_tests()
			if test_result.get('success'):
				console.print("[green]✓ Tests passed[/green]")
				break
			else:
				errors = "\n\n".join([e for e in test_result.get('errors', []) if e]) or "Tests failed without stderr output. Use verbose logs."
				last_test_output = errors
				md = f"""Tests failed. Will iterate.

```
{errors}
```"""
				console.print(Panel(Markdown(md), title="Test Failures", border_style="red"))

		# Step 3: Optional git commit
		if args.commit and args.apply and not args.dry_run:
			self._git_commit(console, branch=args.branch, message=f"autopilot: {args.goal[:72]}")

	def show_detailed_help(self, console):
		console.print(
			"""
[bold]Autopilot[/bold]
- --goal/-g: What to build (required)
- --language/-l: Target language (default: python)
- --output/-o: Output file path; defaults to language-based filename
- --apply: Actually write files
- --test: Run tests and iterate fixes up to --max-iterations
- --max-iterations: Iterations for generate→test (default 2)
- --commit: Git add/commit after success
- --branch: Create/switch to branch before commit
- --dry-run: Preview only; no writes
			"""
		)

	def _build_plan_prompt(self, goal: str, language: str) -> str:
		return f"""
You are a senior engineer. Create a concise, actionable plan to implement the following goal in {language}.

Goal:
{goal}

Output a short plan with:
- minimal file(s) to create or modify (prefer 1 file if possible)
- key functions/classes
- simple test approach
- success criteria
"""

	def _build_code_prompt(self, goal: str, language: str, plan: str, test_failures: Optional[str]) -> str:
		fix_tail = f"\n\nKnown test failures to fix:\n{test_failures}\n" if test_failures else ""
		return f"""
Write a single, self-contained {language} file that implements the goal below following the plan.
- Include imports and runnable code.
- Be robust and production-quality (error handling, type hints if applicable).
- Return only one fenced code block for the file content.

Goal:
{goal}

Plan:
{plan}
{fix_tail}
"""

	def _extract_primary_code_block(self, text: str, default_language: str) -> Tuple[str, str]:
		"""Extract the first code block. Returns (language, code)."""
		code_block_pattern = re.compile(r"```(\w+)?\n([\s\S]*?)```", re.MULTILINE)
		match = code_block_pattern.search(text)
		if match:
			lang = match.group(1) or default_language
			code = match.group(2).strip()
			return lang.lower(), code
		return default_language.lower(), ""

	def _default_output_for_language(self, language: str) -> str:
		lang = (language or 'text').lower()
		mapping = {
			'python': 'autopilot_output.py',
			'javascript': 'autopilot_output.js',
			'typescript': 'autopilot_output.ts',
			'java': 'AutopilotOutput.java',
			'csharp': 'AutopilotOutput.cs',
			'go': 'autopilot_output.go',
			'rust': 'autopilot_output.rs',
		}
		return mapping.get(lang, 'autopilot_output.txt')

	def _git_commit(self, console, branch: Optional[str], message: str):
		try:
			if not self._in_git_repo():
				console.print("[yellow]Skipping git commit (not a git repository)[/yellow]")
				return
			if branch:
				self._git_switch_branch(branch, console)
			subprocess.run(['git', 'add', '-A'], check=True, capture_output=True)
			subprocess.run(['git', 'commit', '-m', message], check=True, capture_output=True)
			console.print(f"[green]✓ Git committed:[/green] {message}")
		except subprocess.CalledProcessError as e:
			stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
			md = f"""Git commit failed:

```
{stderr}
```"""
			console.print(Panel(Markdown(md), title="Git Error", border_style="red"))

	def _in_git_repo(self) -> bool:
		try:
			result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], capture_output=True, check=True, text=True)
			return result.stdout.strip() == 'true'
		except Exception:
			return False

	def _git_switch_branch(self, branch: str, console) -> None:
		# Try switch -c, then checkout -b if needed
		try:
			subprocess.run(['git', 'switch', '-c', branch], check=True, capture_output=True)
			console.print(f"[green]✓ Created and switched to branch:[/green] {branch}")
		except subprocess.CalledProcessError:
			try:
				subprocess.run(['git', 'switch', branch], check=True, capture_output=True)
				console.print(f"[green]✓ Switched to branch:[/green] {branch}")
			except subprocess.CalledProcessError:
				# Fallback to checkout
				try:
					subprocess.run(['git', 'checkout', '-b', branch], check=True, capture_output=True)
					console.print(f"[green]✓ Created and switched to branch:[/green] {branch}")
				except subprocess.CalledProcessError:
					subprocess.run(['git', 'checkout', branch], check=True, capture_output=True)
					console.print(f"[green]✓ Switched to branch:[/green] {branch}")