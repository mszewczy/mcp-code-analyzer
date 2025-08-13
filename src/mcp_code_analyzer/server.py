import ast
import json

class CodeAnalyzer(ast.NodeVisitor):
    # ... (reszta klasy CodeAnalyzer pozostaje bez zmian) ...
    def __init__(self):
        self.stats = {"functions": [], "classes": [], "imports": []}

    def visit_FunctionDef(self, node):
        # Analizuje definicje funkcji
        if isinstance(node.parent, ast.Module):  # Sprawdza, czy funkcja jest na najwyższym poziomie
            self.stats["functions"].append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "lineno": node.lineno
            })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Analizuje definicje klas i ich metod
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                methods.append({
                    "name": item.name,
                    "args": [arg.arg for arg in item.args.args],
                    "lineno": item.lineno
                })
        self.stats["classes"].append({
            "name": node.name,
            "methods": methods,
            "lineno": node.lineno
        })
        self.generic_visit(node)

    def visit_Import(self, node):
        # Analizuje importy
        for alias in node.names:
            self.stats["imports"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        # Analizuje importy typu "from ... import ..."
        for alias in node.names:
            self.stats["imports"].append(f"{node.module}.{alias.name}")
        self.generic_visit(node)
    
    def visit(self, node):
        """Dodaje rodzica do każdego węzła, aby ułatwić analizę kontekstu."""
        for child in ast.iter_child_nodes(node):
            child.parent = node
        super().visit(node)

    def analyze(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        return self.stats

class CodeAnalyzerServer:
    def __init__(self):
        pass

    # POPRAWKA: Usunięto 'async'
    def analyze_structure(self, file_content):
        analyzer = CodeAnalyzer()
        return analyzer.analyze(file_content)

    # POPRAWKA: Usunięto 'async'
    def analyze_complexity(self, file_content):
        # Placeholder for complexity analysis
        return {"error": "Complexity analysis not implemented"}

    # POPRAWKA: Usunięto 'async'
    def analyze_dependencies(self, file_content):
        # Placeholder for dependency analysis
        return {"error": "Dependency analysis not implemented"}

    # POPRAWKA: Usunięto 'async' i 'await'
    def handle_request(self, data):
        analysis_type = data.get("type")
        file_content = data.get("file")

        if analysis_type == "structure":
            return self.analyze_structure(file_content)
        elif analysis_type == "complexity":
            return self.analyze_complexity(file_content)
        elif analysis_type == "dependencies":
            return self.analyze_dependencies(file_content)
        else:
            return {"error": "Invalid analysis type"}
