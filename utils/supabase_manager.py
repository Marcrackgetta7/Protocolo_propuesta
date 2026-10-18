import os
import sys

# Si es web, NO importamos dotenv ni supabase porque rompen el entorno WASM
_es_web = (sys.platform == "emscripten")

client = None
SUPABASE_URL = None
SUPABASE_KEY = None

if not _es_web:
    import threading
    from dotenv import load_dotenv
    load_dotenv()
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            from supabase import create_client
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print("Error inicializando Supabase:", e)
else:
    # Obtén las credenciales en Web. Lo ideal es inyectarlas o hardcodear solo la public anon key
    # Pero para no romper, simplemente usamos un placeholder si no hay forma de leer .env
    pass

def upsert_session_async(datos_locales):
    session_id = datos_locales.get("session_id")
    if not session_id: return
    
    times = datos_locales.get("times", {})
    phases = times.get("phases", {})
    answers = datos_locales.get("answers", {})
    completed_100 = len(datos_locales.get("secretos", [])) >= 9

    if _es_web:
        import asyncio
        # En web no lo implementaremos directo si no tenemos la KEY pública
        # Pero si tuviéramos la KEY, haríamos fetch()
        pass
    else:
        if not client: return
        def _run():
            def execute_safe(table_name, payload):
                try:
                    client.table(table_name).upsert(payload).execute()
                except Exception as e:
                    if "ConnectionTerminated" not in str(e):
                        print(f"Error sincronizando tabla {table_name}:", e)

            execute_safe("sessions", {"id": session_id, "total_time": times.get("total", 0.0)})
            for phase_name, time_spent in phases.items():
                execute_safe("phase_times", {"session_id": session_id, "phase_name": phase_name, "time_spent": time_spent})
            execute_safe("initial_answers", {"session_id": session_id, "q1": answers.get("q1", ""), "q2": answers.get("q2", ""), "q3": answers.get("q3", "")})
            if answers.get("final"):
                execute_safe("final_answers", {"session_id": session_id, "answer": answers.get("final", "")})
            execute_safe("completion_stats", {"session_id": session_id, "is_completed": completed_100, "time_taken": times.get("100_percent", 0.0)})
                
        import threading
        threading.Thread(target=_run, daemon=True).start()
