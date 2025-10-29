import tkinter as tk
from tkinter import messagebox, ttk
import random
 
# ---------- Graph definitions ----------
SAMPLE_GRAPHS = {
    "Triangle": {
        "nodes": {"A": (200, 100), "B": (100, 250), "C": (300, 250)},
        "edges": [("A", "B"), ("B", "C"), ("C", "A")]
    },
    "Square": {
        "nodes": {"A": (150, 100), "B": (300, 100), "C": (300, 250), "D": (150, 250)},
        "edges": [("A","B"), ("B","C"), ("C","D"), ("D","A")]
    },
    "House": {
        "nodes": {"A": (150,250), "B": (300,250), "C": (300,100), "D": (150,100), "E": (225,30)},
        "edges": [("A","B"),("B","C"),("C","D"),("D","A"),("C","E"),("D","E")]
    },
    "Map-Like": {
        "nodes": {
            "A": (150,100), "B": (300,100), "C": (450,150),
            "D": (150,250), "E": (300,250), "F": (450,300)
        },
        "edges": [("A","B"),("B","C"),("A","D"),("B","E"),("C","F"),
                  ("D","E"),("E","F"),("A","E"),("B","D")]
    },
    "Star": {
        "nodes": {
            "A": (250,60), "B": (350,150), "C": (300,270),
            "D": (200,270), "E": (150,150)
        },
        "edges": [("A","B"),("A","C"),("A","D"),("A","E"),("B","C"),("C","D"),("D","E"),("E","B")]
    },
    "Hexagon": {
        "nodes": {
            "A": (200,80), "B": (300,80), "C": (350,180),
            "D": (300,280), "E": (200,280), "F": (150,180)
        },
        "edges": [("A","B"),("B","C"),("C","D"),("D","E"),("E","F"),("F","A")]
    }
}
 
# ---------- Logic functions ----------
def is_valid_coloring(edges, coloring):
    for a, b in edges:
        if coloring.get(a) == coloring.get(b) and coloring.get(a) is not None:
            return False
    return True
 
def valid_color_for_node(edges, node, color, coloring):
    for a, b in edges:
        if node in (a, b):
            neighbor = b if a == node else a
            if coloring.get(neighbor) == color:
                return False
    return True
 
def backtrack(edges, nodes, colors, coloring, idx=0):
    if idx == len(nodes):
        return coloring.copy()
    node = nodes[idx]
    for c in colors:
        if valid_color_for_node(edges, node, c, coloring):
            coloring[node] = c
            res = backtrack(edges, nodes, colors, coloring, idx+1)
            if res:
                return res
            coloring[node] = None
    return None
 
# ---------- GUI Game ----------
class GraphColoringGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Coloring Puzzle Game")
 
        # Layout
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=5)
 
        tk.Label(self.top_frame, text="Select Shape: ", font=("Arial", 12)).pack(side="left")
        self.graph_choice = ttk.Combobox(self.top_frame, values=list(SAMPLE_GRAPHS.keys()) + ["Random"], width=12)
        self.graph_choice.set("Triangle")
        self.graph_choice.pack(side="left", padx=5)
        tk.Button(self.top_frame, text="Load", command=self.load_graph).pack(side="left", padx=5)
 
        tk.Label(self.top_frame, text="Colors: ").pack(side="left")
        self.color_count = tk.Spinbox(self.top_frame, from_=2, to=5, width=5)
        self.color_count.pack(side="left", padx=5)
 
        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.pack(pady=10)
 
        self.control_frame = tk.Frame(root)
        self.control_frame.pack()
        tk.Button(self.control_frame, text="Hint", command=self.show_hint).pack(side="left", padx=5)
        tk.Button(self.control_frame, text="Solve", command=self.solve).pack(side="left", padx=5)
        tk.Button(self.control_frame, text="Reset", command=self.reset).pack(side="left", padx=5)
 
        # Colors
        self.palette = ["#f54242", "#42f554", "#4287f5", "#f5e642", "#f542dd"]
 
        self.graph_data = None
        self.coloring = {}
        self.node_radius = 25
        self.load_graph()
 
    def load_graph(self):
        """Load selected puzzle."""
        name = self.graph_choice.get()
        if name == "Random":
            name, graph = random.choice(list(SAMPLE_GRAPHS.items()))
            self.graph_choice.set(name)
        else:
            graph = SAMPLE_GRAPHS.get(name, SAMPLE_GRAPHS["Triangle"])
 
        self.graph_data = graph
        color_count = int(self.color_count.get())
        self.colors = self.palette[:color_count]
        self.nodes = list(graph["nodes"].keys())
        self.edges = graph["edges"]
        self.positions = graph["nodes"]
        self.coloring = {n: None for n in self.nodes}
        self.draw_graph()
 
    def draw_graph(self):
        """Draw nodes and edges."""
        self.canvas.delete("all")
 
        # Draw edges
        for a, b in self.edges:
            x1, y1 = self.positions[a]
            x2, y2 = self.positions[b]
            self.canvas.create_line(x1, y1, x2, y2, width=2)
 
        # Draw nodes
        for node, (x, y) in self.positions.items():
            color = self.coloring[node]
            fill = color if color else "lightgray"
            outline = "red" if not self.is_node_valid(node) else "black"
            self.canvas.create_oval(
                x - self.node_radius, y - self.node_radius,
                x + self.node_radius, y + self.node_radius,
                fill=fill, outline=outline, width=2, tags=("node", node)
            )
            self.canvas.create_text(x, y, text=node, font=("Arial", 12, "bold"))
 
        # Bind clicks
        self.canvas.tag_bind("node", "<Button-1>", self.on_click)
 
    def on_click(self, event):
        """Handle node click."""
        clicked_node = None
        for node, (x, y) in self.positions.items():
            if (x - self.node_radius <= event.x <= x + self.node_radius and
                y - self.node_radius <= event.y <= y + self.node_radius):
                clicked_node = node
                break
        if not clicked_node:
            return
 
        current = self.coloring[clicked_node]
        if current is None:
            self.coloring[clicked_node] = self.colors[0]
        else:
            idx = self.colors.index(current)
            self.coloring[clicked_node] = self.colors[(idx + 1) % len(self.colors)]
 
        self.draw_graph()
 
        if self.check_complete():
            messagebox.showinfo("Congrats!", "🎉 All nodes colored correctly!")
 
    def is_node_valid(self, node):
        """Check conflicts."""
        color = self.coloring[node]
        if not color:
            return True
        for a, b in self.edges:
            if node in (a, b):
                neighbor = b if a == node else a
                if self.coloring.get(neighbor) == color:
                    return False
        return True
 
    def check_complete(self):
        if None in self.coloring.values():
            return False
        return is_valid_coloring(self.edges, self.coloring)
 
    def show_hint(self):
        """Suggest one color."""
        solution = backtrack(self.edges, self.nodes, self.colors, self.coloring.copy())
        if not solution:
            messagebox.showwarning("Hint", "No valid solution from current state.")
            return
        for node in self.nodes:
            if self.coloring[node] is None:
                color = solution[node]
                messagebox.showinfo("Hint", f"Try coloring {node} with {color}.")
                return
        messagebox.showinfo("Hint", "All nodes already colored!")
 
    def solve(self):
        """Auto-solve puzzle."""
        solution = backtrack(self.edges, self.nodes, self.colors, self.coloring.copy())
        if not solution:
            messagebox.showerror("Solve", "No valid solution exists.")
        else:
            self.coloring = solution
            self.draw_graph()
            messagebox.showinfo("Solved", "✅ Puzzle solved!")
 
    def reset(self):
        for n in self.coloring:
            self.coloring[n] = None
        self.draw_graph()
 
 
# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = GraphColoringGame(root)
    root.mainloop()
 
