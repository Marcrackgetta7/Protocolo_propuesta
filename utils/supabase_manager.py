import os
import threading
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Error inicializando Supabase:", e)

def upsert_session_async(datos_locales):
    if not client: return
    
    session_id = datos_locales.get("session_id")
    if not session_id: return
    
    times = datos_locales.get("times", {})
    phases = times.get("phases", {})
    answers = datos_locales.get("answers", {})
    
    completed_100 = len(datos_locales.get("secretos", [])) >= 9
    
    def _run():
        def execute_safe(table_name, payload):
            try:
                client.table(table_name).upsert(payload).execute()
            except Exception as e:
                # Ignorar error inofensivo de httpx/HTTP2 que ocurre frecuentemente pero los datos s llegan
                if "ConnectionTerminated" not in str(e):
                    print(f"Error sincronizando tabla {table_name}:", e)

        # 1. Sesin general
        execute_safe("sessions", {
            "id": session_id,
            "total_time": times.get("total", 0.0)
        })

        # 2. Tiempos por fase (1:N)
        for phase_name, time_spent in phases.items():
            execute_safe("phase_times", {
                "session_id": session_id,
                "phase_name": phase_name,
                "time_spent": time_spent
            })

        # 3. Respuestas iniciales
        execute_safe("initial_answers", {
            "session_id": session_id,
            "q1": answers.get("q1", ""),
            "q2": answers.get("q2", ""),
            "q3": answers.get("q3", "")
        })

        # 4. Respuesta final
        if answers.get("final"):
            execute_safe("final_answers", {
                "session_id": session_id,
                "answer": answers.get("final", "")
            })

        # 5. Completado 100%
        execute_safe("completion_stats", {
            "session_id": session_id,
            "is_completed": completed_100,
            "time_taken": times.get("100_percent", 0.0)
        })
            
    threading.Thread(target=_run, daemon=True).start()
