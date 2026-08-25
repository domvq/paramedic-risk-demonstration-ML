import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama

from intent_search import search


MODEL = "paramedic-ai:latest"


class ParamedicRAGApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Paramedic AI — RAG"
        )

        self.root.geometry(
            "1100x700"
        )

        self.root.configure(
            bg="#101820"
        )

        self.build_ui()

    def build_ui(self):

        header = tk.Frame(
            self.root,
            bg="#17232d"
        )

        header.pack(
            fill="x"
        )

        tk.Label(
            header,
            text="PARAMEDIC AI",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="#17232d"
        ).pack(
            side="left",
            padx=20,
            pady=15
        )

        tk.Label(
            header,
            text="RAG + Source Verification",
            font=("Segoe UI", 10),
            fg="#45d483",
            bg="#17232d"
        ).pack(
            side="right",
            padx=20
        )

        main = tk.Frame(
            self.root,
            bg="#101820"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )

        left = tk.Frame(
            main,
            bg="#101820"
        )

        left.pack(
            side="left",
            fill="both",
            expand=True
        )

        right = tk.Frame(
            main,
            bg="#17232d",
            width=320
        )

        right.pack(
            side="right",
            fill="y",
            padx=(15, 0)
        )

        right.pack_propagate(
            False
        )

        self.chat = scrolledtext.ScrolledText(
            left,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0d141a",
            fg="white",
            insertbackground="white",
            padx=15,
            pady=15
        )

        self.chat.pack(
            fill="both",
            expand=True
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI\n"
            "RAG system ready.\n\n"
        )

        tk.Label(
            right,
            text="REFERENCES",
            font=("Segoe UI", 12, "bold"),
            fg="white",
            bg="#17232d"
        ).pack(
            anchor="w",
            padx=15,
            pady=(15, 10)
        )

        self.references = scrolledtext.ScrolledText(
            right,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#0d141a",
            fg="#d8e2ea",
            padx=10,
            pady=10
        )

        self.references.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 15)
        )

        bottom = tk.Frame(
            self.root,
            bg="#101820"
        )

        bottom.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.entry = tk.Entry(
            bottom,
            font=("Segoe UI", 12),
            bg="#1b2833",
            fg="white",
            insertbackground="white"
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=10
        )

        self.entry.bind(
            "<Return>",
            self.send_message
        )

        tk.Button(
            bottom,
            text="Send",
            command=self.send_message,
            bg="#1976d2",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            padx=25,
            pady=8
        ).pack(
            side="right",
            padx=(10, 0)
        )

    def send_message(self, event=None):

        question = self.entry.get().strip()

        if not question:
            return

        self.entry.delete(
            0,
            tk.END
        )

        self.chat.insert(
            tk.END,
            f"You:\n{question}\n\n"
        )

        self.chat.insert(
            tk.END,
            "Paramedic AI:\nThinking...\n\n"
        )

        self.chat.see(
            tk.END
        )

        self.references.delete(
            "1.0",
            tk.END
        )

        thread = threading.Thread(
            target=self.process_question,
            args=(question,),
            daemon=True
        )

        thread.start()

    def process_question(self, question):

        try:

            intent, results = search(
                question
            )

            context = []

            for result in results:

                context.append(
                    f"""
SOURCE:
{result['title']}

Category:
{result['category']}

Status:
{result['status']}

Jurisdiction:
{result['jurisdiction']}

Effective date:
{result['effective_date']}

TEXT:
{result['text']}
"""
                )

            if context:

                context_text = "\n".join(
                    context
                )

            else:

                context_text = (
                    "No sufficiently "
                    "relevant references found."
                )

            prompt = f"""
You are Paramedic AI.

Intent:
{intent}

Answer the user's question using
the retrieved references below.

Rules:

- Be concise.
- Do not invent information.
- Do not assume jurisdiction.
- Clearly identify uncertainty.
- Current local protocols and medical
  direction take precedence.

Question:
{question}

Retrieved references:
{context_text}
"""

            response = ollama.chat(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content":
                            "You are a careful "
                            "EMS education "
                            "assistant."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response[
                "message"
            ][
                "content"
            ]

            self.root.after(
                0,
                self.show_result,
                answer,
                intent,
                results
            )

        except Exception as error:

            self.root.after(
                0,
                self.show_error,
                str(error)
            )

    def show_result(
        self,
        answer,
        intent,
        results
    ):

        current = self.chat.get(
            "1.0",
            tk.END
        )

        marker = (
            "Paramedic AI:\n"
            "Thinking...\n\n"
        )

        position = current.rfind(
            marker
        )

        if position != -1:

            self.chat.delete(
                f"1.0+{position}c",
                f"1.0+{position + len(marker)}c"
            )

        self.chat.insert(
            tk.END,
            f"Paramedic AI:\n"
            f"{answer}\n\n"
        )

        self.chat.see(
            tk.END
        )

        self.references.delete(
            "1.0",
            tk.END
        )

        self.references.insert(
            tk.END,
            f"Detected intent:\n"
            f"{intent}\n\n"
        )

        if not results:

            self.references.insert(
                tk.END,
                "No references found."
            )

            return

        for number, result in enumerate(
            results,
            start=1
        ):

            self.references.insert(
                tk.END,
                f"[{number}] "
                f"{result['title']}\n"
            )

            self.references.insert(
                tk.END,
                f"Category: "
                f"{result['category']}\n"
            )

            self.references.insert(
                tk.END,
                f"Status: "
                f"{result['status']}\n"
            )

            self.references.insert(
                tk.END,
                f"Jurisdiction: "
                f"{result['jurisdiction']}\n"
            )

            self.references.insert(
                tk.END,
                f"Effective: "
                f"{result['effective_date']}\n"
            )

            self.references.insert(
                tk.END,
                f"Similarity: "
                f"{result['similarity']}\n\n"
            )

    def show_error(self, error):

        self.chat.insert(
            tk.END,
            f"\nERROR:\n{error}\n\n"
        )

        self.chat.see(
            tk.END
        )


def main():

    root = tk.Tk()

    ParamedicRAGApp(
        root
    )

    root.mainloop()


if __name__ == "__main__":
    main()