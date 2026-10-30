"""
Day 7: chat with the bot in the terminal - create a talk, then refine it step by step.

Run:
    python chat.py           # interactive: type messages, "quit" to stop
    python chat.py --demo    # a scripted conversation (create -> edit -> edit -> undo ...)

Every turn is saved to logs/session_<date>_<time>.md and .json.
"""

import argparse

from src import config
from src.conversation import ChatSession
from src.retrieval import Retriever

DEMO_MESSAGES = [
    "Make a 7-slide talk on the distillation paper for graduate students focusing on methods; "
    "include 3 speaker notes per slide and preserve key equations",
    "make #2 less technical",
    "dumb down #4",
    "shorten the script to 90 seconds",
    "history",
    "undo",
    "show #2",
]


def main():
    parser = argparse.ArgumentParser(description="Chat with the RAG chatbot")
    parser.add_argument("--demo", action="store_true", help="run a scripted demo conversation")
    args = parser.parse_args()

    print("Loading the retriever...")
    session = ChatSession(Retriever.load())
    print("Ready. " + ("Running the demo conversation." if args.demo else 'Type a message ("quit" to stop).'))

    messages = iter(DEMO_MESSAGES) if args.demo else _typed_messages()
    for message in messages:
        if args.demo:
            print(f"\n🧑 {message}")
        print(f"\n🤖 {session.handle(message)}")

    print(f"\nConversation saved -> {session.log.md_path.relative_to(config.PROJECT_ROOT)}")


def _typed_messages():
    while True:
        message = input("\n🧑 ").strip()
        if message.lower() in ("quit", "exit", "q"):
            return
        if message:
            yield message


if __name__ == "__main__":
    main()
