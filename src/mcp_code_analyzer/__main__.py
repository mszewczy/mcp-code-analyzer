import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from queue import Queue
from .server import CodeAnalyzerServer

# Zmienne globalne do komunikacji między wątkami
# Używamy kolejki, aby bezpiecznie przekazywać wyniki analizy
# z wątku roboczego do wątku serwera.
analysis_queue = Queue()

# Stałe konfiguracyjne serwera
HOST = "0.0.0.0"
PORT = 8000

def run_analysis_in_background(file_content, analysis_type):
    """
    Funkcja uruchamiana w osobnym wątku, aby nie blokować serwera.
    Wykonuje analizę kodu i umieszcza wynik w kolejce.
    """
    try:
        server = CodeAnalyzerServer()
        result = server.analyze_code(file_content, analysis_type)
        analysis_queue.put({"type": "result", "data": result})
    except Exception as e:
        analysis_queue.put({"type": "error", "data": str(e)})

class SSE_Handler(BaseHTTPRequestHandler):
    """
    Handler z dwoma głównymi zadaniami:
    1. Przyjmowanie zleceń analizy przez POST na /analyze.
    2. Strumieniowanie wyników przez GET na /stream (SSE).
    """

    def do_POST(self):
        # Endpoint do przyjmowania zadań
        if self.path == '/analyze':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                # Uruchomienie analizy w tle
                analysis_thread = Thread(
                    target=run_analysis_in_background,
                    args=(data.get("file"), data.get("type"))
                )
                analysis_thread.start()

                # Odpowiedź potwierdzająca przyjęcie zadania
                self.send_response(202) # 202 Accepted
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "Analysis started"}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        # Endpoint do strumieniowania wyników (SSE)
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.end_headers()

            try:
                while True:
                    # Czekaj na wynik w kolejce
                    message = analysis_queue.get()
                    
                    # Formatuj dane zgodnie ze specyfikacją SSE
                    sse_data = f"data: {json.dumps(message)}\n\n"
                    self.wfile.write(sse_data.encode('utf-8'))
                    self.wfile.flush() # Ważne: natychmiastowe wysłanie danych

                    # Zakończ pętlę po wysłaniu wyniku lub błędu
                    if message['type'] in ['result', 'error']:
                        break
            except (BrokenPipeError, ConnectionResetError):
                # Klient zamknął połączenie
                print("Klient zamknął połączenie SSE.")
            except Exception as e:
                print(f"Błąd w strumieniu SSE: {e}")
        else:
            self.send_error(404, "Not Found")

def main():
    """Główna funkcja uruchamiająca serwer."""
    try:
        server_address = (HOST, PORT)
        httpd = HTTPServer(server_address, SSE_Handler)
        print(f"Serwer SSE uruchomiony na http://{HOST}:{PORT}")
        print("Oczekiwanie na zlecenia analizy pod adresem /analyze (POST)...")
        print("Strumień wyników dostępny pod adresem /stream (GET)...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nZamykanie serwera.")
        httpd.server_close()
    except Exception as e:
        print(f"Błąd krytyczny serwera: {e}")

if __name__ == "__main__":
    main()
