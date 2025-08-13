import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from .server import CodeAnalyzerServer

# Definiujemy stałe dla adresu i portu serwera
HOST = "0.0.0.0"  # Nasłuchuj na wszystkich interfejsach sieciowych
PORT = 8000       # Użyj portu 8000

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Prosty handler do obsługi zapytań POST."""
    
    def do_POST(self):
        try:
            # Odczytaj długość przesyłanych danych
            content_length = int(self.headers['Content-Length'])
            # Odczytaj dane POST
            post_data = self.rfile.read(content_length)
            
            # Zdekoduj dane JSON
            data = json.loads(post_data.decode('utf-8'))
            
            # Inicjalizuj analizator i przetwórz dane
            server = CodeAnalyzerServer()
            result = server.analyze_code(data.get("file"), data.get("type"))
            
            # Wyślij odpowiedź sukcesu (200 OK)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Wyślij wynik analizy jako odpowiedź
            self.wfile.write(json.dumps(result).encode('utf-8'))
            
        except Exception as e:
            # W przypadku błędu, wyślij odpowiedź błędu (500)
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_message = {"error": str(e)}
            self.wfile.write(json.dumps(error_message).encode('utf-8'))

def main():
    """Główna funkcja uruchamiająca serwer."""
    try:
        # Utwórz i uruchom serwer HTTP
        web_server = HTTPServer((HOST, PORT), SimpleHTTPRequestHandler)
        print(f"Serwer uruchomiony na http://{HOST}:{PORT}")
        web_server.serve_forever()
    except KeyboardInterrupt:
        # Obsługa przerwania (Ctrl+C)
        print("\nZamykanie serwera.")
        web_server.server_close()
    except Exception as e:
        print(f"Błąd krytyczny: {e}")

if __name__ == "__main__":
    main()
