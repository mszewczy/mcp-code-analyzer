import ast
import json

class CodeAnalyzer(ast.NodeVisitor):
    # ... (reszta klasy CodeAnalyzer pozostaje bez zmian) ...
    def __init__(self):
        self.stats = {"functions": [], "classes": [], "imports": []}

    def visit_FunctionDef(self, node):
        self.stats["functions"].append({
            "name": node.name,
            "args": [arg.arg for arg in node.args.args],
            "lineno": node.lineno
        })
        self.generic_visit(node)

    def visit_ClassDef(self, node):
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
        for alias in node.names:
            self.stats["imports"].append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.stats["imports"].append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def analyze(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        return self.stats

class CodeAnalyzerServer:
    def __init__(self):
        pass

    async def analyze_structure(self, file_content):
        analyzer = CodeAnalyzer()
        return analyzer.analyze(file_content)

    async def analyze_complexity(self, file_content):
        # Placeholder for complexity analysis
        return {"error": "Complexity analysis not implemented"}

    async def analyze_dependencies(self, file_content):
        # Placeholder for dependency analysis
        return {"error": "Dependency analysis not implemented"}

    async def handle_request(self, data):
        analysis_type = data.get("type")
        file_content = data.get("file")

        if analysis_type == "structure":
            # POPRAWKA: Używamy 'await' do wywołania metody asynchronicznej
            return await self.analyze_structure(file_content)
        elif analysis_type == "complexity":
            return await self.analyze_complexity(file_content)
        elif analysis_type == "dependencies":
            return await self.analyze_dependencies(file_content)
        else:
            return {"error": "Invalid analysis type"}
