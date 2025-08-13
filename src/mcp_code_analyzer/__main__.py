import json
from flask import Flask, request, Response, stream_with_context
from queue import Queue
from threading import Thread
from .server import CodeAnalyzerServer

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Kolejka do bezpiecznej komunikacji między wątkami
# Będzie przechowywać wyniki analizy do wysłania przez SSE.
analysis_queue = Queue()

def run_analysis_in_background(file_content, analysis_type):
    """
    Funkcja wykonująca analizę w osobnym wątku, aby nie blokować serwera.
    Wynik umieszcza w kolejce.
    """
    try:
        server = CodeAnalyzerServer()
        result = server.analyze_code(file_content, analysis_type)
        analysis_queue.put({"type": "result", "data": result})
    except Exception as e:
        analysis_queue.put({"type": "error", "data": str(e)})

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Endpoint przyjmujący zlecenia analizy.
    Uruchamia analizę w tle i natychmiast zwraca odpowiedź.
    """
    try:
        data = request.get_json()
        if not data or "file" not in data or "type" not in data:
            return Response(json.dumps({"error": "Invalid request body"}), status=400, mimetype='application/json')

        # Uruchomienie analizy w osobnym wątku
        thread = Thread(target=run_analysis_in_background, args=(data["file"], data["type"]))
        thread.start()

        return Response(json.dumps({"status": "Analysis initiated"}), status=202, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')

@app.route("/stream")
def stream():
    """
    Endpoint SSE, który strumieniuje wyniki z kolejki do klienta.
    Połączenie jest utrzymywane do momentu wysłania wyniku.
    """
    def event_stream():
        try:
            # Czekaj na wiadomość w kolejce
            message = analysis_queue.get()
            # Formatuj i wyślij dane w formacie SSE
            yield f"data: {json.dumps(message)}\n\n"
        except Exception as e:
            error_message = {"type": "error", "data": f"Stream error: {e}"}
            yield f"data: {json.dumps(error_message)}\n\n"

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")

def main():
    """Główna funkcja uruchamiająca serwer."""
    # Używamy prostego serwera wbudowanego we Flask.
    # Dla środowiska produkcyjnego zalecany jest serwer WSGI, np. Gunicorn.
    app.run(host="0.0.0.0", port=8000, threaded=True)

if __name__ == "__main__":
    main()
